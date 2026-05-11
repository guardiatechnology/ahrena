"""Unit tests for scripts.skills.validate (deterministic skill-project validator)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from skills.validate import validate  # noqa: E402


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fixtures
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _write_valid_skill(root: Path, slug: str = "valid-skill") -> Path:
    skill = root / slug
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        f"name: {slug}\n"
        "description: A valid skill used by the test suite to lock in the happy path.\n"
        "metadata:\n"
        '  version: "0.1.0"\n'
        "  language: en\n"
        "---\n\n# Title\n\nBody.\n",
        encoding="utf-8",
    )
    (skill / "skill.config.json").write_text(json.dumps({"language": "en"}), encoding="utf-8")
    return skill


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Happy path
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_valid_skill_has_no_errors(tmp_path: Path) -> None:
    skill = _write_valid_skill(tmp_path)
    violations = validate(skill)
    errors = [v for v in violations if v.severity == "error"]
    assert errors == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Negative paths
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_missing_skill_md_is_reported(tmp_path: Path) -> None:
    skill = tmp_path / "no-skill-md"
    skill.mkdir()
    (skill / "skill.config.json").write_text("{}", encoding="utf-8")

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#required-files" in rules


def test_missing_frontmatter(tmp_path: Path) -> None:
    skill = tmp_path / "no-frontmatter"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# no frontmatter here\n", encoding="utf-8")
    (skill / "skill.config.json").write_text("{}", encoding="utf-8")

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#frontmatter" in rules


def test_name_diverges_from_slug(tmp_path: Path) -> None:
    skill = _write_valid_skill(tmp_path, slug="real-slug")
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: different-name\n"
        "description: Drift between slug and name.\n"
        "---\n",
        encoding="utf-8",
    )

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#name-matches-slug" in rules


def test_invalid_slug_regex(tmp_path: Path) -> None:
    skill = tmp_path / "Invalid_Skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: Invalid_Skill\ndescription: x.\n---\n", encoding="utf-8"
    )
    (skill / "skill.config.json").write_text("{}", encoding="utf-8")

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#slug-regex" in rules


def test_invalid_semver_in_metadata(tmp_path: Path) -> None:
    skill = _write_valid_skill(tmp_path)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: valid-skill\n"
        "description: ok.\n"
        "metadata:\n"
        "  version: not-semver\n"
        "---\n",
        encoding="utf-8",
    )

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-semantic-version" in rules


def test_orphan_reference_in_skill_md(tmp_path: Path) -> None:
    skill = _write_valid_skill(tmp_path)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: valid-skill\n"
        "description: ok.\n"
        "---\n\nSee [missing](references/does-not-exist.md).\n",
        encoding="utf-8",
    )

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#cross-references" in rules


def test_invalid_json_in_skill_config(tmp_path: Path) -> None:
    skill = _write_valid_skill(tmp_path)
    (skill / "skill.config.json").write_text("not json", encoding="utf-8")

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#required-files" in rules


def test_unknown_subdir_emits_warning(tmp_path: Path) -> None:
    skill = _write_valid_skill(tmp_path)
    (skill / "rogue").mkdir()

    violations = validate(skill)
    warnings = [v for v in violations if v.severity == "warning"]
    rules = {v.rule for v in warnings}
    assert "lex-skill-project-structure#optional-subdirs" in rules


def test_reserved_slug_token_anthropic(tmp_path: Path) -> None:
    skill = tmp_path / "anthropic-x"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: anthropic-x\ndescription: x.\n---\n", encoding="utf-8"
    )
    (skill / "skill.config.json").write_text("{}", encoding="utf-8")

    violations = validate(skill)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#slug-reserved" in rules


def test_nonexistent_skill_path_is_reported(tmp_path: Path) -> None:
    violations = validate(tmp_path / "does-not-exist")
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-project-structure#location" in rules
