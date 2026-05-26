"""Unit tests for the project setup catalog in scripts/install.py.

Covers PROJECT_SETUP_CATALOG shape, profile mapping for the new dimension,
resolve_selection() handling of --with-setup / --without-setup,
install_github_codeowners() (preserve, resolved org, fallback), and
install_gitignore_merge() (first run, idempotent re-run, client edits
inside markers). render_directives() shape for the project_setup section.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    PROFILE_FULL,
    PROFILE_MINIMAL,
    PROFILE_STANDARD,
    PROJECT_SETUP_CATALOG,
    Selection,
    install_github_codeowners,
    install_github_pr_template,
    install_gitignore_merge,
    render_directives,
    resolve_selection,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_args(**overrides: object) -> argparse.Namespace:
    """Return an argparse.Namespace with every selection flag defaulted."""
    base: dict[str, object] = {
        "profile": None,
        "with_mcp": "",
        "without_mcp": "",
        "with_hooks": "",
        "without_hooks": "",
        "with_features": "",
        "without_features": "",
        "with_setup": "",
        "without_setup": "",
        "non_interactive": True,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def _completed_process(stdout: str, returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROJECT_SETUP_CATALOG shape
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_project_setup_catalog_has_exactly_four_keys() -> None:
    assert set(PROJECT_SETUP_CATALOG.keys()) == {
        "github-issue-templates",
        "github-pr-template",
        "github-codeowners",
        "gitignore-merge",
    }


def test_project_setup_catalog_entries_are_tuples_of_desc_and_envs() -> None:
    for name, entry in PROJECT_SETUP_CATALOG.items():
        assert isinstance(entry, tuple), f"{name} entry must be a tuple"
        assert len(entry) == 2
        desc, envs = entry
        assert isinstance(desc, str) and desc, f"{name} description must be non-empty str"
        assert isinstance(envs, list), f"{name} envs must be a list"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile mapping
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_profile_full_has_all_four_setup_items() -> None:
    assert PROFILE_FULL.project_setup == frozenset(PROJECT_SETUP_CATALOG.keys())


def test_profile_standard_has_three_setup_items_without_codeowners() -> None:
    assert PROFILE_STANDARD.project_setup == frozenset({
        "github-issue-templates",
        "github-pr-template",
        "gitignore-merge",
    })
    assert "github-codeowners" not in PROFILE_STANDARD.project_setup


def test_profile_minimal_has_no_setup_items() -> None:
    assert PROFILE_MINIMAL.project_setup == frozenset()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# resolve_selection — --with-setup / --without-setup overrides
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_resolve_standard_plus_codeowners() -> None:
    args = _make_args(profile="standard", with_setup="github-codeowners")
    result = resolve_selection(args, interactive=False)
    assert "github-codeowners" in result.project_setup
    # Pre-existing standard items remain.
    assert "github-pr-template" in result.project_setup


def test_resolve_full_minus_gitignore_merge() -> None:
    args = _make_args(profile="full", without_setup="gitignore-merge")
    result = resolve_selection(args, interactive=False)
    assert "gitignore-merge" not in result.project_setup
    # The other three remain.
    assert "github-codeowners" in result.project_setup
    assert "github-pr-template" in result.project_setup
    assert "github-issue-templates" in result.project_setup


def test_resolve_minimal_plus_pr_template_only() -> None:
    args = _make_args(profile="minimal", with_setup="github-pr-template")
    result = resolve_selection(args, interactive=False)
    assert result.project_setup == frozenset({"github-pr-template"})


def test_resolve_rejects_unknown_setup_name() -> None:
    args = _make_args(with_setup="invalid-setup-item")
    with pytest.raises(SystemExit) as excinfo:
        resolve_selection(args, interactive=False)
    assert excinfo.value.code == 2


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# install_github_codeowners — preservation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_install_codeowners_preserves_existing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    existing = tmp_path / ".github" / "CODEOWNERS"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("# pre-existing\n* @custom-team\n", encoding="utf-8")
    original = existing.read_text(encoding="utf-8")

    install_github_codeowners(REPO_ROOT, tmp_path)

    assert existing.read_text(encoding="utf-8") == original
    captured = capsys.readouterr()
    assert "Preserved" in captured.out


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# install_github_codeowners — resolved org from git remote
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_install_codeowners_resolves_org_from_https_remote(tmp_path: Path) -> None:
    with patch(
        "install.subprocess.run",
        return_value=_completed_process("https://github.com/acme-org/my-repo.git\n"),
    ):
        install_github_codeowners(REPO_ROOT, tmp_path)
    written = (tmp_path / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "* @acme-org/maintainers" in written
    # The fallback comment block must not appear.
    assert "could not resolve" not in written


def test_install_codeowners_resolves_org_from_ssh_remote(tmp_path: Path) -> None:
    with patch(
        "install.subprocess.run",
        return_value=_completed_process("git@github.com:fancy-co/some-repo.git\n"),
    ):
        install_github_codeowners(REPO_ROOT, tmp_path)
    written = (tmp_path / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "* @fancy-co/maintainers" in written


def test_install_codeowners_fallback_when_no_remote(tmp_path: Path) -> None:
    with patch(
        "install.subprocess.run",
        return_value=_completed_process("", returncode=128),
    ):
        install_github_codeowners(REPO_ROOT, tmp_path)
    written = (tmp_path / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "could not resolve" in written
    # The default-team line is commented out.
    assert "# * @" in written
    # The bare uncommented form is absent.
    for line in written.splitlines():
        if line.startswith("* @"):
            pytest.fail(f"uncommented default-team line leaked: {line!r}")


def test_install_codeowners_fallback_when_remote_is_not_github(tmp_path: Path) -> None:
    with patch(
        "install.subprocess.run",
        return_value=_completed_process("https://gitlab.com/foo/bar.git\n"),
    ):
        install_github_codeowners(REPO_ROOT, tmp_path)
    written = (tmp_path / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "could not resolve" in written


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# install_github_pr_template — copy + idempotent overwrite
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_install_pr_template_copies_from_framework(tmp_path: Path) -> None:
    install_github_pr_template(REPO_ROOT, tmp_path)
    dst = tmp_path / ".github" / "pull_request_template.md"
    assert dst.exists()
    src = REPO_ROOT / "framework" / "templates" / "contributing_templates" / "pull_request_template.md"
    assert dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8")


def test_install_pr_template_overwrites_existing(tmp_path: Path) -> None:
    dst = tmp_path / ".github" / "pull_request_template.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("# stale content\n", encoding="utf-8")

    install_github_pr_template(REPO_ROOT, tmp_path)
    assert "# stale content" not in dst.read_text(encoding="utf-8")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# install_gitignore_merge — first run, idempotent, client-line preservation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_gitignore_merge_creates_file_when_absent(tmp_path: Path) -> None:
    install_gitignore_merge(REPO_ROOT, tmp_path)
    gi = tmp_path / ".gitignore"
    assert gi.exists()
    body = gi.read_text(encoding="utf-8")
    assert "# >>> AHRENA-GITIGNORE >>>" in body
    assert "# <<< AHRENA-GITIGNORE <<<" in body
    # Sample content is materialized inside the block.
    assert ".ahrena/" in body


def test_gitignore_merge_appends_block_to_existing(tmp_path: Path) -> None:
    gi = tmp_path / ".gitignore"
    gi.write_text("# project-specific\n__pycache__/\n.venv/\n", encoding="utf-8")
    install_gitignore_merge(REPO_ROOT, tmp_path)

    body = gi.read_text(encoding="utf-8")
    # Client lines preserved.
    assert "__pycache__/" in body
    assert ".venv/" in body
    # Block appended.
    assert "# >>> AHRENA-GITIGNORE >>>" in body
    assert "# <<< AHRENA-GITIGNORE <<<" in body
    # Order: client lines come before the block.
    client_idx = body.find("__pycache__/")
    block_idx = body.find("# >>> AHRENA-GITIGNORE >>>")
    assert client_idx < block_idx


def test_gitignore_merge_idempotent_no_duplicate(tmp_path: Path) -> None:
    gi = tmp_path / ".gitignore"
    gi.write_text("# client\nnode_modules/\n", encoding="utf-8")

    install_gitignore_merge(REPO_ROOT, tmp_path)
    first = gi.read_text(encoding="utf-8")
    install_gitignore_merge(REPO_ROOT, tmp_path)
    second = gi.read_text(encoding="utf-8")

    # Re-run does not duplicate the block.
    assert first == second
    assert second.count("# >>> AHRENA-GITIGNORE >>>") == 1
    assert second.count("# <<< AHRENA-GITIGNORE <<<") == 1
    # Client line preserved.
    assert "node_modules/" in second


def test_gitignore_merge_preserves_client_lines_outside_markers(tmp_path: Path) -> None:
    gi = tmp_path / ".gitignore"
    # Client edits before and after a stale Ahrena block.
    gi.write_text(
        "# client header\nfoo.log\n\n"
        "# >>> AHRENA-GITIGNORE >>>\n"
        "stale-line-from-old-version\n"
        "# <<< AHRENA-GITIGNORE <<<\n\n"
        "# client footer\nbar.tmp\n",
        encoding="utf-8",
    )

    install_gitignore_merge(REPO_ROOT, tmp_path)
    body = gi.read_text(encoding="utf-8")

    # Client lines preserved (both before and after).
    assert "# client header" in body
    assert "foo.log" in body
    assert "# client footer" in body
    assert "bar.tmp" in body
    # Stale managed content overwritten.
    assert "stale-line-from-old-version" not in body
    # Fresh block present.
    assert ".ahrena/" in body
    # Single block.
    assert body.count("# >>> AHRENA-GITIGNORE >>>") == 1


def test_gitignore_merge_overwrites_client_edits_inside_markers(tmp_path: Path) -> None:
    gi = tmp_path / ".gitignore"
    gi.write_text(
        "# >>> AHRENA-GITIGNORE >>>\n"
        ".ahrena/\n"
        "my-stray-line-from-client\n"  # client edited inside the managed block
        "# <<< AHRENA-GITIGNORE <<<\n",
        encoding="utf-8",
    )

    install_gitignore_merge(REPO_ROOT, tmp_path)
    body = gi.read_text(encoding="utf-8")

    # Stray line inside the managed block is overwritten.
    assert "my-stray-line-from-client" not in body
    # Sample content is freshly materialized.
    assert ".ahrena/" in body


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# render_directives — project_setup section shape
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_render_full_lists_every_setup_item_uncommented() -> None:
    content = render_directives(PROFILE_FULL)
    assert "project_setup:" in content
    for name in PROJECT_SETUP_CATALOG:
        # Line `  - <name>` (uncommented) appears.
        assert f"  - {name}" in content, f"setup {name!r} missing uncommented from full render"


def test_render_minimal_keeps_section_with_all_items_commented() -> None:
    content = render_directives(PROFILE_MINIMAL)
    assert "project_setup:" in content
    for name in PROJECT_SETUP_CATALOG:
        # Each item appears commented out as a placeholder.
        assert f"  # - {name}" in content, f"setup {name!r} missing commented from minimal render"
        # No uncommented form leaks through.
        for line in content.splitlines():
            assert line.strip() != f"- {name}", \
                f"setup {name!r} unexpectedly uncommented in minimal render"


def test_render_standard_uncomments_three_items_comments_codeowners() -> None:
    content = render_directives(PROFILE_STANDARD)
    assert "  - github-issue-templates" in content
    assert "  - github-pr-template" in content
    assert "  - gitignore-merge" in content
    assert "  # - github-codeowners" in content
