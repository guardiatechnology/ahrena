"""Ahrena MCP server — exposes the framework as queryable tools.

Run: python -m ahrena_mcp.server [--root <path>]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print(
        "ERROR: 'mcp' not installed. From the repo root, run:\n"
        "  pip install -e tools/ahrena-mcp",
        file=sys.stderr,
    )
    raise

from ahrena_mcp.loader import FrameworkLoader
from ahrena_mcp.search import search as fw_search


def _discover_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("AHRENA_ROOT")
    if env:
        return Path(env).resolve()
    current = Path.cwd().resolve()
    for parent in [current, *current.parents]:
        if (parent / ".ahrena").is_dir():
            return parent
    raise FileNotFoundError(
        "Could not locate Ahrena root. Pass --root or set AHRENA_ROOT."
    )


def _default_lang(root: Path) -> str:
    directives = root / ".ahrena" / ".directives"
    if directives.exists():
        try:
            data = yaml.safe_load(directives.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                lang_section = data.get("language") or {}
                if isinstance(lang_section, dict):
                    val = lang_section.get("default")
                    if isinstance(val, str) and val.strip():
                        return val
        except yaml.YAMLError:
            pass
    return "pt-BR"


def build_app(root: Path) -> FastMCP:
    loader = FrameworkLoader(root)
    default_lang = _default_lang(root)
    mcp = FastMCP("ahrena")

    @mcp.tool()
    def ahrena_query_lex(name: str, lang: str = default_lang) -> str:
        """Returns the full markdown of a Lexis (e.g., 'lex-idempotency')."""
        artifact = loader.get(name, lang)
        if not artifact:
            return f"ERROR: lex '{name}' not found in lang '{lang}'."
        if artifact.pilar != "lexis":
            return f"ERROR: '{name}' is not a Lexis (it is {artifact.pilar})."
        return loader.get_content(artifact)

    @mcp.tool()
    def ahrena_get_codex(name: str, lang: str = default_lang) -> str:
        """Returns the full markdown of a Codex (e.g., 'codex-restful-apis')."""
        artifact = loader.get(name, lang)
        if not artifact:
            return f"ERROR: codex '{name}' not found in lang '{lang}'."
        if artifact.pilar != "codex":
            return f"ERROR: '{name}' is not a Codex (it is {artifact.pilar})."
        return loader.get_content(artifact)

    @mcp.tool()
    def ahrena_list_warriors(clade: str = "", lang: str = default_lang) -> list[dict]:
        """Lists warriors. Optional filter by clade (e.g., 'engineering')."""
        clade_filter = clade or None
        result = []
        for art in loader.iter_pilar("warriors", lang=lang, clade=clade_filter):
            result.append(
                {
                    "name": art.name,
                    "clade": art.clade,
                    "subclade": art.subclade,
                    "path": str(art.path.relative_to(loader.root)),
                }
            )
        return sorted(result, key=lambda x: x["name"])

    @mcp.tool()
    def ahrena_list_cries(lang: str = default_lang) -> list[dict]:
        """Lists all cries (slash commands) in the framework."""
        result = []
        for art in loader.iter_pilar("cries", lang=lang):
            result.append(
                {
                    "name": art.name,
                    "clade": art.clade,
                    "subclade": art.subclade,
                    "path": str(art.path.relative_to(loader.root)),
                }
            )
        return sorted(result, key=lambda x: x["name"])

    @mcp.tool()
    def ahrena_search(
        query: str,
        pilar: str = "",
        lang: str = default_lang,
        limit: int = 30,
    ) -> list[dict]:
        """Ranked search. pilar: 'lexis'|'codex'|'katas'|'warriors'|'cries' or empty."""
        pilar_filter = pilar or None
        hits = fw_search(loader, query, pilar=pilar_filter, lang=lang, limit=limit)
        return [
            {
                "artifact": h.artifact_name,
                "pilar": h.pilar,
                "lang": h.lang,
                "path": h.path,
                "line": h.line,
                "snippet": h.snippet,
                "score": h.score,
            }
            for h in hits
        ]

    @mcp.tool()
    def ahrena_resolve_ref(ref: str, lang: str = default_lang) -> dict:
        """Checks whether a ref exists. Returns existence + path + pilar."""
        artifact = loader.get(ref, lang)
        if artifact:
            return {
                "exists": True,
                "name": artifact.name,
                "pilar": artifact.pilar,
                "lang": artifact.lang,
                "path": str(artifact.path.relative_to(loader.root)),
            }
        for try_lang in loader.available_languages():
            if try_lang == lang:
                continue
            artifact = loader.get(ref, try_lang)
            if artifact:
                return {
                    "exists": True,
                    "name": artifact.name,
                    "pilar": artifact.pilar,
                    "lang": artifact.lang,
                    "path": str(artifact.path.relative_to(loader.root)),
                    "warning": f"not found in '{lang}', returned from '{try_lang}'",
                }
        return {"exists": False, "name": ref, "lang": lang}

    @mcp.tool()
    def ahrena_get_directives() -> dict:
        """Returns the parsed .ahrena/.directives content."""
        path = root / ".ahrena" / ".directives"
        if not path.exists():
            return {"error": ".ahrena/.directives not found"}
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return data if isinstance(data, dict) else {"error": "directives is not a mapping"}
        except yaml.YAMLError as exc:
            return {"error": f"YAML parse error: {exc}"}

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(prog="ahrena-mcp")
    parser.add_argument("--root", help="Ahrena repo root", default=None)
    args = parser.parse_args()
    root = _discover_root(args.root)
    app = build_app(root)
    app.run()


if __name__ == "__main__":
    main()
