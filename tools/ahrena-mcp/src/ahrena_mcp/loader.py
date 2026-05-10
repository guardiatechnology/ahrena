"""Loader for Ahrena framework artifacts.

Walks framework/{lang}/ to build an in-memory index of all artifacts.
Indexed by (lang, name). Cache invalidated on mtime mismatch.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

PILAR_DIRS = {"lexis", "codex", "katas", "warriors", "cries"}
PILAR_PREFIX = {
    "lexis": "lex-",
    "codex": "codex-",
    "katas": "kata-",
    "warriors": "warrior-",
    "cries": "cry-",
}
PREFIX_TO_PILAR = {v: k for k, v in PILAR_PREFIX.items()}


@dataclass(frozen=True)
class Artifact:
    name: str
    pilar: str
    clade: str
    subclade: str
    lang: str
    path: Path
    mtime: float


class FrameworkLoader:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.framework_dir = self.root / "framework"
        if not self.framework_dir.is_dir():
            raise FileNotFoundError(
                f"framework/ not found under {self.root}. "
                "Run from an Ahrena repo root or pass --root."
            )
        self._cache: dict[tuple[str, str], Artifact] = {}
        self._content_cache: dict[Path, tuple[float, str]] = {}
        self._scan()

    def _scan(self) -> None:
        self._cache.clear()
        for lang_dir in sorted(self.framework_dir.iterdir()):
            if not lang_dir.is_dir() or lang_dir.name.startswith("."):
                continue
            lang = lang_dir.name
            for path in lang_dir.rglob("*.md"):
                pilar = self._pilar_from_path(path)
                if not pilar:
                    continue
                try:
                    rel = path.relative_to(lang_dir)
                except ValueError:
                    continue
                parts = rel.parts
                if len(parts) < 4:
                    continue
                clade = parts[0]
                subclade = parts[1]
                name = path.stem
                self._cache[(lang, name)] = Artifact(
                    name=name,
                    pilar=pilar,
                    clade=clade,
                    subclade=subclade,
                    lang=lang,
                    path=path,
                    mtime=path.stat().st_mtime,
                )

    def _pilar_from_path(self, path: Path) -> str | None:
        for parent in path.parents:
            if parent.name in PILAR_DIRS:
                return parent.name
        for prefix, pilar in PREFIX_TO_PILAR.items():
            if path.stem.startswith(prefix):
                return pilar
        return None

    def get(self, name: str, lang: str = "pt-BR") -> Artifact | None:
        key = (lang, name)
        artifact = self._cache.get(key)
        if artifact and (
            not artifact.path.exists()
            or artifact.path.stat().st_mtime != artifact.mtime
        ):
            self._scan()
            artifact = self._cache.get(key)
        return artifact

    def get_content(self, artifact: Artifact) -> str:
        cached = self._content_cache.get(artifact.path)
        if cached and cached[0] == artifact.mtime:
            return cached[1]
        content = artifact.path.read_text(encoding="utf-8")
        self._content_cache[artifact.path] = (artifact.mtime, content)
        return content

    def iter_artifacts(self, lang: str | None = None) -> Iterator[Artifact]:
        """Iterate over all indexed artifacts. Optionally filter by lang.

        Public iteration entrypoint — consumers MUST use this instead
        of reaching into ``_cache`` directly.
        """
        for (a_lang, _), art in self._cache.items():
            if lang and a_lang != lang:
                continue
            yield art

    def iter_pilar(
        self,
        pilar: str,
        lang: str = "pt-BR",
        clade: str | None = None,
    ) -> Iterator[Artifact]:
        for art in self.iter_artifacts(lang=lang):
            if art.pilar != pilar:
                continue
            if clade and art.clade != clade:
                continue
            yield art

    def available_languages(self) -> list[str]:
        return sorted({lang for (lang, _) in self._cache})
