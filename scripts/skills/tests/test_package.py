"""Unit tests for scripts.skills.package (packager + package validator)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from skills.package import package, validate_package  # noqa: E402


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _init_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"], check=True
    )
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "commit.gpgsign", "false"], check=True
    )
    (tmp_path / "README.md").write_text("seed", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-q", "-m", "seed"], check=True
    )
    return tmp_path


def _write_valid_skill(repo: Path, slug: str = "valid-skill") -> Path:
    skill = repo / "skills" / slug
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        f"name: {slug}\n"
        "description: A valid skill for the test suite.\n"
        "metadata:\n"
        '  version: "0.1.0"\n'
        "  language: en\n"
        "---\n\n# Title\n",
        encoding="utf-8",
    )
    (skill / "skill.config.json").write_text(json.dumps({"language": "en"}), encoding="utf-8")
    return skill


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Happy path
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_package_happy_path_produces_valid_package(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)

    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )

    assert report.ok, report.violations
    package_dir = repo / ".dist" / "valid-skill.skill"
    assert (package_dir / "SKILL.md").is_file()
    manifest = json.loads((package_dir / ".skill-manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["skill"]["name"] == "valid-skill"
    assert manifest["skill"]["version"] == "0.1.0"
    assert manifest["skill"]["language"] == "en"
    assert len(manifest["framework"]["ahrena_commit"]) >= 40
    paths = [e["path"] for e in manifest["files"]]
    assert paths == sorted(paths), "files[] must be lexicographically sorted"
    assert ".skill-manifest.json" in paths
    for entry in manifest["files"]:
        if entry["sha256"] == "self":
            continue
        actual = hashlib.sha256((package_dir / entry["path"]).read_bytes()).hexdigest()
        assert actual == entry["sha256"]


def test_dry_run_does_not_create_package(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)

    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
        dry_run=True,
    )

    assert report.ok
    assert not (repo / ".dist" / "valid-skill.skill").exists()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Source-side blocking errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_invalid_source_blocks_package(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    skill = repo / "skills" / "broken-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")
    (skill / "skill.config.json").write_text("{}", encoding="utf-8")

    report = package(
        slug="broken-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )

    assert not report.ok
    assert not (repo / ".dist" / "broken-skill.skill").exists()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Package-validation negative cases (build artifacts mutated by hand)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_orphan_file_in_package_is_caught(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)
    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )
    assert report.ok

    package_dir = repo / ".dist" / "valid-skill.skill"
    (package_dir / "orphan.txt").write_text("not in manifest", encoding="utf-8")

    violations = validate_package(package_dir)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-package-structure#no-orphans" in rules


def test_sha_mismatch_in_package_is_caught(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)
    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )
    assert report.ok

    package_dir = repo / ".dist" / "valid-skill.skill"
    skill_md = package_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text(encoding="utf-8") + "\nmutated\n", encoding="utf-8")

    violations = validate_package(package_dir)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-package-structure#files-sha256" in rules


def test_absolute_path_in_manifest_files_is_caught(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)
    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )
    assert report.ok

    package_dir = repo / ".dist" / "valid-skill.skill"
    manifest_path = package_dir / ".skill-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"].append({"path": "/etc/passwd", "sha256": "deadbeef"})
    manifest["files"].sort(key=lambda e: e["path"])
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    violations = validate_package(package_dir)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-package-structure#manifest-files-entry" in rules


def test_parent_dir_traversal_in_manifest_files_is_caught(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)
    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )
    assert report.ok

    package_dir = repo / ".dist" / "valid-skill.skill"
    manifest_path = package_dir / ".skill-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"].append({"path": "../../etc/passwd", "sha256": "deadbeef"})
    manifest["files"].sort(key=lambda e: e["path"])
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    violations = validate_package(package_dir)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-package-structure#manifest-files-entry" in rules


def test_unsafe_snapshot_path_in_reference_is_caught(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)
    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )
    assert report.ok

    package_dir = repo / ".dist" / "valid-skill.skill"
    manifest_path = package_dir / ".skill-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["references"].append(
        {
            "kind": "reference",
            "id": "evil",
            "source_commit": "a" * 40,
            "snapshot_path": "../../etc/passwd",
            "snapshot_sha256": "deadbeef",
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    violations = validate_package(package_dir)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-package-structure#manifest-references-entry" in rules


def test_empty_ahrena_commit_in_manifest_is_caught(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_valid_skill(repo)
    report = package(
        slug="valid-skill",
        repo_root=repo,
        skills_root="skills",
        skills_build=".build",
        skills_dist=".dist",
    )
    assert report.ok

    package_dir = repo / ".dist" / "valid-skill.skill"
    manifest_path = package_dir / ".skill-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["framework"]["ahrena_commit"] = ""
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    violations = validate_package(package_dir)
    rules = {v.rule for v in violations if v.severity == "error"}
    assert "lex-skill-package-structure#manifest-ahrena-commit" in rules
