"""Search across Ahrena framework artifacts.

Uses ripgrep when available (fast). Falls back to a Python regex
sweep over indexed artifacts when rg is missing.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ahrena_mcp.loader import FrameworkLoader


@dataclass(frozen=True)
class Hit:
    artifact_name: str
    pilar: str
    lang: str
    path: str
    line: int
    snippet: str
    score: int


def search(
    loader: FrameworkLoader,
    query: str,
    pilar: str | None = None,
    lang: str | None = None,
    limit: int = 30,
) -> list[Hit]:
    if not query.strip():
        return []
    rg = shutil.which("rg")
    if rg:
        return _rg_search(rg, loader, query, pilar, lang, limit)
    return _py_search(loader, query, pilar, lang, limit)


def _rg_search(
    rg_path: str,
    loader: FrameworkLoader,
    query: str,
    pilar: str | None,
    lang: str | None,
    limit: int,
) -> list[Hit]:
    target = loader.framework_dir
    if lang:
        target = target / lang
        if not target.is_dir():
            return []
    cmd = [
        rg_path,
        "--no-config",
        "-i",
        "--no-heading",
        "-n",
        "--max-count",
        "5",
        "--type",
        "md",
        query,
        str(target),
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15, check=False
        )
    except subprocess.TimeoutExpired:
        return []
    if proc.returncode not in (0, 1):
        return []

    score_by_path: dict[str, int] = {}
    first_by_path: dict[str, tuple[int, str]] = {}
    for raw in proc.stdout.splitlines():
        parts = raw.split(":", 2)
        if len(parts) < 3:
            continue
        path_str, lineno_s, snippet = parts
        try:
            lineno = int(lineno_s)
        except ValueError:
            continue
        score_by_path[path_str] = score_by_path.get(path_str, 0) + 1
        first_by_path.setdefault(path_str, (lineno, snippet.strip()[:200]))

    hits: list[Hit] = []
    for path_str, score in score_by_path.items():
        path = Path(path_str)
        name = path.stem
        try:
            rel = path.relative_to(loader.framework_dir)
            art_lang = rel.parts[0] if rel.parts else ""
        except ValueError:
            art_lang = ""
        artifact = loader.get(name, art_lang) if art_lang else None
        if pilar:
            if not artifact or artifact.pilar != pilar:
                continue
        line, snippet = first_by_path[path_str]
        hits.append(
            Hit(
                artifact_name=name,
                pilar=artifact.pilar if artifact else "",
                lang=art_lang,
                path=path_str,
                line=line,
                snippet=snippet,
                score=score,
            )
        )

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]


def _py_search(
    loader: FrameworkLoader,
    query: str,
    pilar: str | None,
    lang: str | None,
    limit: int,
) -> list[Hit]:
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    hits: list[Hit] = []
    seen: set[Path] = set()
    for artifact in loader.iter_artifacts(lang=lang):
        if pilar and artifact.pilar != pilar:
            continue
        if artifact.path in seen:
            continue
        seen.add(artifact.path)
        try:
            content = loader.get_content(artifact)
        except OSError:
            continue
        score = 0
        first_line = 0
        first_snippet = ""
        for i, line in enumerate(content.splitlines(), 1):
            if pattern.search(line):
                if score == 0:
                    first_line = i
                    first_snippet = line.strip()[:200]
                score += 1
                if score >= 5:
                    break
        if score > 0:
            hits.append(
                Hit(
                    artifact_name=artifact.name,
                    pilar=artifact.pilar,
                    lang=artifact.lang,
                    path=str(artifact.path),
                    line=first_line,
                    snippet=first_snippet,
                    score=score,
                )
            )
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]
