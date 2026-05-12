#!/usr/bin/env python3
"""
Ahrena: Skill Packager.

Builds a deliverable `.skill/` package under `{paths.skills_dist}/{slug}.skill/`
from a skill project at `{paths.skills_root}/{slug}/`, and validates the result
against `lex-skill-package-structure`.

Pipeline:
    1. Resolve paths from .ahrena/.directives (or defaults).
    2. Validate the source project layout (delegates to `validate.py`).
    3. Copy the source tree into `{paths.skills_build}/{slug}/` (intermediate).
    4. Generate `.skill-manifest.json` (schema_version, skill, framework, files[], references[]).
    5. Materialize the final package at `{paths.skills_dist}/{slug}.skill/`.
    6. Validate the package against `lex-skill-package-structure`.

Usage:
    python -m scripts.skills.package <slug> [--root PATH] [--build PATH] [--dist PATH]
                                            [--dry-run] [--format text|json]

Exit codes:
    0  package built and validated
    1  validation failure (source or package)
    2  invocation error
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from skills._common import (  # type: ignore[no-redef]
        DESCRIPTION_MAX,
        DESCRIPTION_MIN,
        MANIFEST_SCHEMA_VERSION,
        RESERVED_SLUG_TOKENS,
        SEMVER_REGEX,
        SLUG_REGEX,
        Violation,
        current_head_sha,
        parse_frontmatter,
        read_directives_paths,
    )
    from skills.validate import validate as validate_project  # type: ignore[no-redef]
else:
    from ._common import (
        DESCRIPTION_MAX,
        DESCRIPTION_MIN,
        MANIFEST_SCHEMA_VERSION,
        RESERVED_SLUG_TOKENS,
        SEMVER_REGEX,
        SLUG_REGEX,
        Violation,
        current_head_sha,
        parse_frontmatter,
        read_directives_paths,
    )
    from .validate import validate as validate_project


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Result
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclasses.dataclass(frozen=True)
class PackageReport:
    slug: str
    package_path: str
    manifest_path: str
    files_count: int
    violations: list[Violation]

    def to_dict(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "package_path": self.package_path,
            "manifest_path": self.manifest_path,
            "files_count": self.files_count,
            "violations": [v.to_dict() for v in self.violations],
        }

    @property
    def ok(self) -> bool:
        return all(v.severity == "warning" for v in self.violations)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Hashing + file walk
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_files(root: Path) -> list[Path]:
    """Return every file under `root`, sorted by POSIX path, excluding dotfiles in dirs."""
    result: list[Path] = []
    for child in sorted(root.rglob("*")):
        if not child.is_file():
            continue
        rel = child.relative_to(root)
        # Skip OS noise and intermediate metadata files inside the source.
        if any(part in {"__pycache__", ".DS_Store"} for part in rel.parts):
            continue
        result.append(child)
    return sorted(result, key=lambda p: p.relative_to(root).as_posix())


def _is_unsafe_relative_path(value: object) -> bool:
    """Return True when `value` is not a safe project-relative path.

    A path is unsafe when it is absolute or contains `..` segments — both can
    escape the package root and turn the validator into a path-traversal vector
    (it would hash an attacker-controlled file outside the package).
    """
    if not isinstance(value, str) or not value:
        return True
    parts = Path(value).parts
    if Path(value).is_absolute() or ".." in parts:
        return True
    return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Manifest
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_manifest(
    package_root: Path,
    slug: str,
    version: str,
    language: str,
    framework_sha: str,
) -> dict[str, object]:
    """Build the canonical `.skill-manifest.json` payload for `package_root`."""
    files_entries: list[dict[str, str]] = [
        {"path": ".skill-manifest.json", "sha256": "self"}
    ]
    references_entries: list[dict[str, str]] = []

    for file in _iter_files(package_root):
        rel = file.relative_to(package_root).as_posix()
        if rel == ".skill-manifest.json":
            continue
        files_entries.append({"path": rel, "sha256": _sha256_of(file)})

        if rel.startswith("references/") and rel.endswith(".md"):
            ref_id = rel[len("references/"):-len(".md")]
            references_entries.append(
                {
                    "kind": "reference",
                    "id": ref_id,
                    "source_commit": framework_sha,
                    "snapshot_path": rel,
                    "snapshot_sha256": _sha256_of(file),
                }
            )

    files_entries.sort(key=lambda e: e["path"])
    references_entries.sort(key=lambda e: e["id"])

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "skill": {"name": slug, "version": version, "language": language},
        "framework": {"ahrena_commit": framework_sha},
        "references": references_entries,
        "files": files_entries,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Package validation (lex-skill-package-structure)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def validate_package(package_path: Path) -> list[Violation]:
    """Validate `package_path` (a `.skill/` directory) against lex-skill-package-structure."""
    if not package_path.is_dir():
        return [
            Violation(
                rule="lex-skill-package-structure#location",
                severity="error",
                file=str(package_path),
                message="package path does not exist or is not a directory",
            )
        ]

    slug = package_path.name.removesuffix(".skill")
    violations: list[Violation] = []

    skill_md = package_path / "SKILL.md"
    manifest_path = package_path / ".skill-manifest.json"

    if not skill_md.is_file():
        violations.append(
            Violation(
                rule="lex-skill-package-structure#frontmatter",
                severity="error",
                file=str(skill_md),
                message="SKILL.md missing in the package",
            )
        )
    else:
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm is None:
            violations.append(
                Violation(
                    rule="lex-skill-package-structure#frontmatter",
                    severity="error",
                    file=str(skill_md),
                    message="SKILL.md has no YAML frontmatter delimited by '---'",
                )
            )
        else:
            name = fm.get("name")
            if not isinstance(name, str) or not SLUG_REGEX.match(name) or any(
                tok in name for tok in RESERVED_SLUG_TOKENS
            ):
                violations.append(
                    Violation(
                        rule="lex-skill-package-structure#frontmatter-name",
                        severity="error",
                        file=str(skill_md),
                        message=f"frontmatter 'name' missing or invalid (got {name!r})",
                    )
                )
            elif name != slug:
                violations.append(
                    Violation(
                        rule="lex-skill-package-structure#name-matches-directory",
                        severity="error",
                        file=str(skill_md),
                        message=f"frontmatter name '{name}' does not match package directory '{slug}'",
                    )
                )
            description = fm.get("description")
            if not isinstance(description, str) or not (
                DESCRIPTION_MIN <= len(description) <= DESCRIPTION_MAX
            ):
                violations.append(
                    Violation(
                        rule="lex-skill-package-structure#frontmatter-description",
                        severity="error",
                        file=str(skill_md),
                        message="frontmatter 'description' missing or outside [1, 1024] chars",
                    )
                )

    if not manifest_path.is_file():
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest",
                severity="error",
                file=str(manifest_path),
                message=".skill-manifest.json missing in the package",
            )
        )
        return violations

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest",
                severity="error",
                file=str(manifest_path),
                message=f".skill-manifest.json is not valid JSON: {exc.msg} (line {exc.lineno})",
            )
        )
        return violations

    schema_version = manifest.get("schema_version")
    if schema_version != MANIFEST_SCHEMA_VERSION:
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest-schema-version",
                severity="error",
                file=str(manifest_path),
                message=f"schema_version must be {MANIFEST_SCHEMA_VERSION}, got {schema_version!r}",
            )
        )

    skill_block = manifest.get("skill") or {}
    if skill_block.get("name") != slug:
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest-name",
                severity="error",
                file=str(manifest_path),
                message=f"manifest.skill.name must equal package slug '{slug}'",
            )
        )
    if not SEMVER_REGEX.match(str(skill_block.get("version") or "")):
        violations.append(
            Violation(
                rule="lex-semantic-version",
                severity="error",
                file=str(manifest_path),
                message=f"manifest.skill.version '{skill_block.get('version')}' is not valid SemVer",
            )
        )
    if not skill_block.get("language"):
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest-language",
                severity="error",
                file=str(manifest_path),
                message="manifest.skill.language is required",
            )
        )

    framework_block = manifest.get("framework") or {}
    ahrena_commit = framework_block.get("ahrena_commit")
    if not isinstance(ahrena_commit, str) or len(ahrena_commit) < 40:
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest-ahrena-commit",
                severity="error",
                file=str(manifest_path),
                message=(
                    "manifest.framework.ahrena_commit must be a non-empty SHA "
                    "(>= 40 hex chars)"
                ),
            )
        )

    files = manifest.get("files") or []
    if not isinstance(files, list) or not files:
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest-files",
                severity="error",
                file=str(manifest_path),
                message="manifest.files must be a non-empty list",
            )
        )
        return violations

    declared_paths: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or "path" not in entry or "sha256" not in entry:
            violations.append(
                Violation(
                    rule="lex-skill-package-structure#manifest-files-entry",
                    severity="error",
                    file=str(manifest_path),
                    message=f"manifest.files entry malformed: {entry!r}",
                )
            )
            continue
        if _is_unsafe_relative_path(entry["path"]):
            violations.append(
                Violation(
                    rule="lex-skill-package-structure#manifest-files-entry",
                    severity="error",
                    file=str(manifest_path),
                    message=(
                        f"manifest.files entry has unsafe path "
                        f"(absolute or '..'-escaping): {entry['path']!r}"
                    ),
                )
            )
            continue
        declared_paths.add(entry["path"])
        target = package_path / entry["path"]
        if not target.is_file():
            violations.append(
                Violation(
                    rule="lex-skill-package-structure#files-presence",
                    severity="error",
                    file=str(target),
                    message=f"file '{entry['path']}' declared in manifest is missing",
                )
            )
            continue
        if entry["sha256"] == "self":
            if entry["path"] != ".skill-manifest.json":
                violations.append(
                    Violation(
                        rule="lex-skill-package-structure#files-sha256",
                        severity="error",
                        file=str(target),
                        message="only '.skill-manifest.json' may use sha256='self'",
                    )
                )
            continue
        actual = _sha256_of(target)
        if actual != entry["sha256"]:
            violations.append(
                Violation(
                    rule="lex-skill-package-structure#files-sha256",
                    severity="error",
                    file=str(target),
                    message=(
                        f"sha256 mismatch for '{entry['path']}': "
                        f"declared {entry['sha256']!r}, actual {actual!r}"
                    ),
                )
            )

    # Ordering check
    declared_order = [e["path"] for e in files if isinstance(e, dict) and "path" in e]
    if declared_order != sorted(declared_order):
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest-files-ordering",
                severity="error",
                file=str(manifest_path),
                message="manifest.files MUST be lexicographically sorted by 'path'",
            )
        )

    # Orphan check
    actual_files = {
        p.relative_to(package_path).as_posix() for p in _iter_files(package_path)
    }
    orphans = sorted(actual_files - declared_paths)
    for orphan in orphans:
        violations.append(
            Violation(
                rule="lex-skill-package-structure#no-orphans",
                severity="error",
                file=str(package_path / orphan),
                message=f"file '{orphan}' exists in the package but is not in manifest.files[]",
            )
        )

    references = manifest.get("references") or []
    if not isinstance(references, list):
        violations.append(
            Violation(
                rule="lex-skill-package-structure#manifest-references",
                severity="error",
                file=str(manifest_path),
                message="manifest.references must be a list (may be empty)",
            )
        )
    else:
        for ref in references:
            if not isinstance(ref, dict):
                violations.append(
                    Violation(
                        rule="lex-skill-package-structure#manifest-references-entry",
                        severity="error",
                        file=str(manifest_path),
                        message=f"reference entry malformed: {ref!r}",
                    )
                )
                continue
            for key in ("kind", "id", "source_commit", "snapshot_path", "snapshot_sha256"):
                if not ref.get(key):
                    violations.append(
                        Violation(
                            rule="lex-skill-package-structure#manifest-references-entry",
                            severity="error",
                            file=str(manifest_path),
                            message=f"reference entry missing '{key}': {ref!r}",
                        )
                    )
            if ref.get("snapshot_path"):
                if _is_unsafe_relative_path(ref["snapshot_path"]):
                    violations.append(
                        Violation(
                            rule="lex-skill-package-structure#manifest-references-entry",
                            severity="error",
                            file=str(manifest_path),
                            message=(
                                f"reference entry has unsafe snapshot_path "
                                f"(absolute or '..'-escaping): {ref['snapshot_path']!r}"
                            ),
                        )
                    )
                    continue
                snap = package_path / ref["snapshot_path"]
                if not snap.is_file():
                    violations.append(
                        Violation(
                            rule="lex-skill-package-structure#references-snapshot",
                            severity="error",
                            file=str(snap),
                            message=f"snapshot file '{ref['snapshot_path']}' missing",
                        )
                    )
                else:
                    actual = _sha256_of(snap)
                    if actual != ref.get("snapshot_sha256"):
                        violations.append(
                            Violation(
                                rule="lex-skill-package-structure#references-snapshot",
                                severity="error",
                                file=str(snap),
                                message=(
                                    f"snapshot_sha256 mismatch for '{ref['snapshot_path']}': "
                                    f"declared {ref.get('snapshot_sha256')!r}, actual {actual!r}"
                                ),
                            )
                        )

    return violations


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Build pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _copy_tree(source: Path, target: Path) -> None:
    # `rmtree` only handles real directories: on a stale file or symlink it
    # raises NotADirectoryError, and on some platforms a directory symlink
    # could be followed into the link target. `lstat` (via `is_symlink`)
    # never resolves the link, so we can branch safely.
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )


def package(
    slug: str,
    repo_root: Path,
    skills_root: str,
    skills_build: str,
    skills_dist: str,
    dry_run: bool = False,
) -> PackageReport:
    source = repo_root / skills_root / slug
    build_dir = repo_root / skills_build / slug
    package_path = repo_root / skills_dist / f"{slug}.skill"

    # 1. Source validation
    source_violations = validate_project(source)
    fatal = [v for v in source_violations if v.severity == "error"]
    if fatal:
        return PackageReport(
            slug=slug,
            package_path=str(package_path),
            manifest_path=str(package_path / ".skill-manifest.json"),
            files_count=0,
            violations=source_violations,
        )

    # 2. Frontmatter for manifest skill block
    fm = parse_frontmatter((source / "SKILL.md").read_text(encoding="utf-8")) or {}
    metadata = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    version = str(metadata.get("version") or "0.0.0") if isinstance(metadata, dict) else "0.0.0"
    language = str(metadata.get("language") or "en") if isinstance(metadata, dict) else "en"

    framework_sha = current_head_sha(repo_root) or ""
    if not framework_sha:
        return PackageReport(
            slug=slug,
            package_path=str(package_path),
            manifest_path=str(package_path / ".skill-manifest.json"),
            files_count=0,
            violations=[
                Violation(
                    rule="lex-skill-package-structure#manifest-ahrena-commit",
                    severity="error",
                    file=str(repo_root),
                    message="unable to resolve framework HEAD SHA (git unavailable?)",
                )
            ],
        )

    if dry_run:
        return PackageReport(
            slug=slug,
            package_path=str(package_path),
            manifest_path=str(package_path / ".skill-manifest.json"),
            files_count=len(_iter_files(source)),
            violations=source_violations,
        )

    # 3. Source → build
    _copy_tree(source, build_dir)

    # 4. Build → dist
    _copy_tree(build_dir, package_path)

    # 5. Manifest
    manifest = _build_manifest(package_path, slug, version, language, framework_sha)
    manifest_path = package_path / ".skill-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # 6. Package validation
    package_violations = validate_package(package_path)
    files_list = manifest.get("files")
    files_count = len(files_list) if isinstance(files_list, list) else 0

    return PackageReport(
        slug=slug,
        package_path=str(package_path),
        manifest_path=str(manifest_path),
        files_count=files_count,
        violations=source_violations + package_violations,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _format_text(report: PackageReport) -> str:
    header = "✅" if report.ok else "❌"
    lines = [
        f"{header} package: {report.package_path}",
        f"   manifest: {report.manifest_path}",
        f"   files:    {report.files_count}",
    ]
    if report.violations:
        lines.append(f"   violations: {len(report.violations)}")
        for v in report.violations:
            lines.append(f"     [{v.severity}] {v.rule}")
            lines.append(f"         file:    {v.file}")
            lines.append(f"         message: {v.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and validate a skill package")
    parser.add_argument("slug", help="Slug of the skill project (must match the directory name)")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root (default: current working directory)",
    )
    parser.add_argument("--root", help="Override paths.skills_root from .ahrena/.directives")
    parser.add_argument("--build", help="Override paths.skills_build")
    parser.add_argument("--dist", help="Override paths.skills_dist")
    parser.add_argument("--dry-run", action="store_true", help="Validate source only; do not write")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    directives = read_directives_paths(repo_root / ".ahrena" / ".directives")
    skills_root = args.root or directives["skills_root"]
    skills_build = args.build or directives["skills_build"]
    skills_dist = args.dist or directives["skills_dist"]

    report = package(
        slug=args.slug,
        repo_root=repo_root,
        skills_root=skills_root,
        skills_build=skills_build,
        skills_dist=skills_dist,
        dry_run=args.dry_run,
    )

    if args.format == "json":
        sys.stdout.write(json.dumps(report.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_text(report) + "\n")

    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
