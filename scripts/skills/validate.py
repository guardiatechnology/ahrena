#!/usr/bin/env python3
"""
Ahrena: Skill Project Validator (deterministic).

Validates a skill project under `{paths.skills_root}/{slug}/` against
`lex-skill-project-structure` and the frontmatter requirements from
`codex-skill-anthropic-agent-skills`.

Usage:
    python -m scripts.skills.validate <skill-path> [--format text|json]
    python scripts/skills/validate.py <skill-path>

Exit codes:
    0  no errors (warnings are allowed)
    1  one or more errors
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from skills._common import (  # type: ignore[no-redef]
        DESCRIPTION_MAX,
        DESCRIPTION_MIN,
        RESERVED_SLUG_TOKENS,
        SEMVER_REGEX,
        SLUG_REGEX,
        Violation,
        parse_frontmatter,
    )
else:
    from ._common import (
        DESCRIPTION_MAX,
        DESCRIPTION_MIN,
        RESERVED_SLUG_TOKENS,
        SEMVER_REGEX,
        SLUG_REGEX,
        Violation,
        parse_frontmatter,
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Constants from lex-skill-project-structure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUIRED_ROOT_FILES = ("SKILL.md", "skill.config.json")
ALLOWED_SUBDIRS = {"references", "scripts", "tools", "widgets", "assets"}


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Individual rules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _validate_slug(slug: str, skill_path: Path) -> Iterable[Violation]:
    relpath = str(skill_path)
    if not SLUG_REGEX.match(slug):
        yield Violation(
            rule="lex-skill-project-structure#slug-regex",
            severity="error",
            file=relpath,
            message=(
                f"directory name '{slug}' does not match Anthropic slug regex "
                f"^[a-z0-9](?:[a-z0-9]|-(?!-)){{0,62}}[a-z0-9]?$"
            ),
        )
    for reserved in RESERVED_SLUG_TOKENS:
        if reserved in slug:
            yield Violation(
                rule="lex-skill-project-structure#slug-reserved",
                severity="error",
                file=relpath,
                message=f"slug contains reserved token '{reserved}'",
            )


def _validate_required_files(skill_path: Path) -> Iterable[Violation]:
    for required in REQUIRED_ROOT_FILES:
        target = skill_path / required
        if not target.is_file():
            yield Violation(
                rule="lex-skill-project-structure#required-files",
                severity="error",
                file=str(target),
                message=f"required file '{required}' missing at project root",
            )


def _validate_optional_subdirs(skill_path: Path) -> Iterable[Violation]:
    for entry in sorted(skill_path.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name not in ALLOWED_SUBDIRS:
            yield Violation(
                rule="lex-skill-project-structure#optional-subdirs",
                severity="warning",
                file=str(entry),
                message=(
                    f"subdirectory '{entry.name}' is not in the allow-list "
                    f"{sorted(ALLOWED_SUBDIRS)}; declare justification in SKILL.md "
                    f"or skill.config.json"
                ),
            )


def _validate_frontmatter(skill_path: Path, slug: str) -> Iterable[Violation]:
    skill_md = skill_path / "SKILL.md"
    text = _read_text(skill_md)
    if text is None:
        return

    fm = parse_frontmatter(text)
    if fm is None:
        yield Violation(
            rule="lex-skill-project-structure#frontmatter",
            severity="error",
            file=str(skill_md),
            message="SKILL.md has no YAML frontmatter delimited by '---'",
        )
        return

    name = fm.get("name")
    if not isinstance(name, str) or not name:
        yield Violation(
            rule="lex-skill-project-structure#frontmatter-name",
            severity="error",
            file=str(skill_md),
            message="SKILL.md frontmatter is missing required field 'name'",
        )
    elif name != slug:
        yield Violation(
            rule="lex-skill-project-structure#name-matches-slug",
            severity="error",
            file=str(skill_md),
            message=f"frontmatter name '{name}' does not match directory slug '{slug}'",
        )

    description = fm.get("description")
    if not isinstance(description, str) or not description.strip():
        yield Violation(
            rule="codex-skill-anthropic-agent-skills#description",
            severity="error",
            file=str(skill_md),
            message="SKILL.md frontmatter is missing required field 'description'",
        )
    elif not (DESCRIPTION_MIN <= len(description) <= DESCRIPTION_MAX):
        yield Violation(
            rule="codex-skill-anthropic-agent-skills#description-length",
            severity="error",
            file=str(skill_md),
            message=(
                f"description length {len(description)} outside allowed range "
                f"[{DESCRIPTION_MIN}, {DESCRIPTION_MAX}]"
            ),
        )

    metadata = fm.get("metadata")
    if isinstance(metadata, dict):
        version = metadata.get("version")
        if isinstance(version, str) and version and not SEMVER_REGEX.match(version):
            yield Violation(
                rule="lex-semantic-version",
                severity="error",
                file=str(skill_md),
                message=(
                    f"metadata.version '{version}' is not valid SemVer "
                    f"(MAJOR.MINOR.PATCH per lex-semantic-version)"
                ),
            )


def _validate_skill_config(skill_path: Path) -> Iterable[Violation]:
    config = skill_path / "skill.config.json"
    text = _read_text(config)
    if text is None:
        return
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        yield Violation(
            rule="lex-skill-project-structure#required-files",
            severity="error",
            file=str(config),
            message=f"skill.config.json is not valid JSON: {exc.msg} (line {exc.lineno})",
        )


def _validate_references(skill_path: Path) -> Iterable[Violation]:
    """Verify that every relative Markdown link in SKILL.md resolves inside the project."""
    skill_md = skill_path / "SKILL.md"
    text = _read_text(skill_md)
    if text is None:
        return

    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for match in link_re.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        ref_path = (skill_md.parent / path_part).resolve()
        try:
            ref_path.relative_to(skill_path.resolve())
        except ValueError:
            yield Violation(
                rule="lex-skill-project-structure#cross-references",
                severity="error",
                file=str(skill_md),
                message=f"reference '{target}' resolves outside the skill project",
            )
            continue
        if not ref_path.exists():
            yield Violation(
                rule="lex-skill-project-structure#cross-references",
                severity="error",
                file=str(skill_md),
                message=f"reference '{target}' does not exist at {ref_path}",
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Public API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def validate(skill_path: Path) -> list[Violation]:
    """Run every project rule against `skill_path` and return all violations."""
    if not skill_path.is_dir():
        return [
            Violation(
                rule="lex-skill-project-structure#location",
                severity="error",
                file=str(skill_path),
                message="skill path does not exist or is not a directory",
            )
        ]
    slug = skill_path.name
    violations: list[Violation] = []
    violations.extend(_validate_slug(slug, skill_path))
    violations.extend(_validate_required_files(skill_path))
    violations.extend(_validate_optional_subdirs(skill_path))
    violations.extend(_validate_frontmatter(skill_path, slug))
    violations.extend(_validate_skill_config(skill_path))
    violations.extend(_validate_references(skill_path))
    return violations


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _format_text(violations: list[Violation]) -> str:
    if not violations:
        return "✅ no violations"
    lines = [f"❌ {len(violations)} violation(s):"]
    for v in violations:
        lines.append(f"  [{v.severity}] {v.rule}")
        lines.append(f"      file:    {v.file}")
        lines.append(f"      message: {v.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a skill project against lex-skill-project-structure")
    parser.add_argument("skill_path", help="Path to the skill project directory")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    skill_path = Path(args.skill_path)
    violations = validate(skill_path)

    if args.format == "json":
        sys.stdout.write(json.dumps([v.to_dict() for v in violations], indent=2) + "\n")
    else:
        sys.stdout.write(_format_text(violations) + "\n")

    return 0 if all(v.severity == "warning" for v in violations) else 1


if __name__ == "__main__":
    sys.exit(main())
