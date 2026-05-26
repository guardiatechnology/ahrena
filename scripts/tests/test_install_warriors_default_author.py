"""Unit tests for the `warriors-default-author` optional feature in scripts/install.py.

Covers the Plan P1 acceptance criteria (renamed under Plan P5):

- AC-P1-3: `warriors-default-author` appears in the install catalog (--list-catalog).
- AC-P1-4: All 3 profiles (FULL, STANDARD, MINIMAL) default to NOT selected.
- AC-P1-5: `--with-features=warriors-default-author` enables the feature;
  rendered `.directives` contains the uncommented `warriors_default_author:` block.
- AC-P1-6: install_ahrena_auth_script copies the script + sets the
  executable bit when selected; skips when not selected.
- AC-P1-9: New tests bring the suite to ~80 total without regressions.

Patterns mirrored from test_install_selection.py and
test_install_project_setup.py (same fixture conventions, same
namespace defaults).
"""

from __future__ import annotations

import argparse
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    OPTIONAL_FEATURES,
    PROFILE_FULL,
    PROFILE_MINIMAL,
    PROFILE_STANDARD,
    Selection,
    install_ahrena_auth_script,
    parse_directives,
    print_catalog,
    render_directives,
    resolve_selection,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _make_args(**overrides: object) -> argparse.Namespace:
    """Return an argparse.Namespace with the selection flags defaulted.

    Mirrors the helper in test_install_selection.py / test_install_project_setup.py
    so tests share a single shape for the resolver namespace.
    """
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Catalog membership (AC-P1-3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_warriors_default_author_in_optional_features_catalog() -> None:
    """OPTIONAL_FEATURES MUST list `warriors-default-author` with the canonical description."""
    assert "warriors-default-author" in OPTIONAL_FEATURES
    desc = OPTIONAL_FEATURES["warriors-default-author"]
    assert "GitHub App" in desc or "warriors" in desc.lower(), (
        f"warriors-default-author description should mention warriors/GitHub App; got: {desc!r}"
    )


def test_warriors_default_author_appears_in_list_catalog_output() -> None:
    """print_catalog() MUST surface `warriors-default-author` under the
    Optional features section so `--list-catalog` answers AC-P1-3."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_catalog()
    out = buf.getvalue()
    assert "warriors-default-author" in out, (
        "warriors-default-author missing from --list-catalog output"
    )
    # The catalog block is introduced by a known header — verify it
    # appears before the warriors-default-author line.
    optional_header = "Optional .directives features"
    idx_header = out.find(optional_header)
    idx_feature = out.find("warriors-default-author")
    assert idx_header != -1, f"missing '{optional_header}' header in catalog"
    assert idx_header < idx_feature, (
        "warriors-default-author should appear under the Optional features header"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile defaults — warriors-default-author MUST be opt-in (AC-P1-4)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_warriors_default_author_not_in_profile_full_default() -> None:
    assert "warriors-default-author" not in PROFILE_FULL.optional_features


def test_warriors_default_author_not_in_profile_standard_default() -> None:
    assert "warriors-default-author" not in PROFILE_STANDARD.optional_features


def test_warriors_default_author_not_in_profile_minimal_default() -> None:
    assert "warriors-default-author" not in PROFILE_MINIMAL.optional_features


def test_resolve_full_profile_does_not_select_warriors_default_author() -> None:
    """`--profile full` with no overrides MUST resolve to a selection that
    omits warriors-default-author (defensive cross-check of AC-P1-4 via the resolver)."""
    args = _make_args(profile="full")
    sel = resolve_selection(args, interactive=False)
    assert "warriors-default-author" not in sel.optional_features


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Opt-in via --with-features=warriors-default-author (AC-P1-5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_with_features_warriors_default_author_enables_selection() -> None:
    args = _make_args(profile="minimal", with_features="warriors-default-author")
    sel = resolve_selection(args, interactive=False)
    assert "warriors-default-author" in sel.optional_features


def test_without_features_warriors_default_author_removes_when_explicitly_added() -> None:
    """--without-features must win over --with-features for the same name
    (mirrors the precedence checks in test_install_selection.py)."""
    args = _make_args(
        profile="full",
        with_features="warriors-default-author",
        without_features="warriors-default-author",
    )
    sel = resolve_selection(args, interactive=False)
    assert "warriors-default-author" not in sel.optional_features


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# render_directives — warriors_default_author section shape
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_render_directives_emits_commented_warriors_default_author_when_not_selected() -> None:
    """PROFILE_FULL leaves warriors-default-author OFF by design — the
    rendered `.directives` MUST therefore contain the commented
    `# warriors_default_author:` skeleton so the schema stays documented."""
    content = render_directives(PROFILE_FULL)
    assert "# warriors_default_author:" in content
    # The active form MUST NOT appear when not selected.
    assert "\nwarriors_default_author:" not in content
    # The schema MUST mention the master switch with default false.
    assert "enabled: false" in content


def test_render_directives_emits_uncommented_warriors_default_author_when_selected() -> None:
    """When the selection includes warriors-default-author the rendered
    file MUST emit the section uncommented with enabled=true so
    parse_directives sees a live block."""
    sel = Selection(
        mcps=PROFILE_FULL.mcps,
        hooks=PROFILE_FULL.hooks,
        optional_features=PROFILE_FULL.optional_features | {"warriors-default-author"},
        project_setup=PROFILE_FULL.project_setup,
    )
    content = render_directives(sel)
    assert "\nwarriors_default_author:" in content
    parsed = parse_directives(content)
    assert parsed.get("warriors_default_author", {}).get("enabled") == "true"
    assert parsed.get("warriors_default_author", {}).get("identity") == "ahrena-bot"
    assert parsed.get("warriors_default_author", {}).get("commit_mode") == "api"
    assert parsed.get("warriors_default_author", {}).get("commit_co_author") == "human"
    # apply_to MUST be a non-empty list mirroring the Plan schema.
    apply_to = parsed.get("warriors_default_author", {}).get("apply_to")
    assert isinstance(apply_to, list)
    assert "athena" in apply_to
    assert "apollo" in apply_to
    assert "hephaestus" in apply_to


def test_render_directives_warriors_default_author_header_present_in_both_modes() -> None:
    """The section header comment ('# ─── Warriors Default Author ───')
    MUST always appear so projects can find the block whether it is
    active or not."""
    for sel in (
        PROFILE_FULL,
        Selection(optional_features=frozenset({"warriors-default-author"})),
    ):
        content = render_directives(sel)
        assert "Warriors Default Author" in content, (
            f"missing 'Warriors Default Author' header in render for selection={sel!r}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# install_ahrena_auth_script (AC-P1-6)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _make_source_with_auth_script(source_root: Path) -> Path:
    """Fixture helper: materialize a fake source repo carrying the
    ahrena-auth.sh script the installer expects to copy."""
    scripts_dir = source_root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    src = scripts_dir / "ahrena-auth.sh"
    src.write_text(
        "#!/usr/bin/env bash\n# fake ahrena-auth.sh used by the test fixture\n",
        encoding="utf-8",
    )
    return src


def test_install_ahrena_auth_script_copies_when_feature_selected(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    _make_source_with_auth_script(source)

    sel = Selection(optional_features=frozenset({"warriors-default-author"}))
    install_ahrena_auth_script(source, target, sel)

    dst = target / "scripts" / "ahrena-auth.sh"
    assert dst.exists(), "ahrena-auth.sh was not copied to the target"
    # Content parity with source (basic sanity).
    assert "ahrena-auth.sh" in dst.read_text(encoding="utf-8")


def test_install_ahrena_auth_script_skips_when_feature_not_selected(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    _make_source_with_auth_script(source)

    sel = Selection(optional_features=frozenset())  # warriors-default-author NOT selected
    install_ahrena_auth_script(source, target, sel)

    dst = target / "scripts" / "ahrena-auth.sh"
    assert not dst.exists(), (
        "ahrena-auth.sh MUST NOT be copied when warriors-default-author is not selected"
    )


def test_install_ahrena_auth_script_sets_executable_bit(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    _make_source_with_auth_script(source)

    sel = Selection(optional_features=frozenset({"warriors-default-author"}))
    install_ahrena_auth_script(source, target, sel)

    dst = target / "scripts" / "ahrena-auth.sh"
    mode = dst.stat().st_mode & 0o777
    # 0o755 is the canonical executable mode used elsewhere in install.py
    # (mirrors install_github_pr_template / pr-cost-attribution hook).
    assert mode == 0o755, f"expected mode 0o755, got {oct(mode)}"


def test_install_ahrena_auth_script_warns_when_source_missing(
    tmp_path: Path,
    capsys: object,
) -> None:
    """When the source script is missing the installer MUST warn (not
    raise) so the install run as a whole keeps going."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    # Intentionally NOT creating scripts/ahrena-auth.sh at the source.

    sel = Selection(optional_features=frozenset({"warriors-default-author"}))
    install_ahrena_auth_script(source, target, sel)

    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "ahrena-auth.sh not found" in captured.err
    dst = target / "scripts" / "ahrena-auth.sh"
    assert not dst.exists(), "script should not be created when source is missing"
