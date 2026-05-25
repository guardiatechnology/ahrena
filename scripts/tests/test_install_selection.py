"""Unit tests for the preference-driven install selection in scripts/install.py.

Covers parse_csv_set(), resolve_selection() (profiles, overrides, ahrena pin,
unknown-name rejection), check_env_vars() (presence checks), and
render_directives() (Full vs Minimal output, sample parity).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    MCP_CATALOG,
    OPTIONAL_FEATURES,
    PROFILE_FULL,
    PROFILE_MINIMAL,
    PROFILE_STANDARD,
    Selection,
    check_env_vars,
    get_directive,
    parse_csv_set,
    parse_directives,
    render_directives,
    resolve_selection,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _make_args(**overrides: object) -> argparse.Namespace:
    """Return an argparse.Namespace with the selection flags defaulted."""
    base: dict[str, object] = {
        "profile": None,
        "with_mcp": "",
        "without_mcp": "",
        "with_hooks": "",
        "without_hooks": "",
        "with_features": "",
        "without_features": "",
        "non_interactive": True,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# parse_csv_set
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_parse_csv_set_empty_string_returns_empty() -> None:
    assert parse_csv_set("") == frozenset()


def test_parse_csv_set_none_returns_empty() -> None:
    assert parse_csv_set(None) == frozenset()


def test_parse_csv_set_strips_and_lowercases() -> None:
    assert parse_csv_set("a, B ,c") == frozenset({"a", "b", "c"})


def test_parse_csv_set_drops_blank_tokens() -> None:
    assert parse_csv_set(",a,,b,") == frozenset({"a", "b"})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# resolve_selection — profiles
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_resolve_minimal_profile_no_flags_equals_profile_minimal() -> None:
    args = _make_args(profile="minimal")
    assert resolve_selection(args, interactive=False) == PROFILE_MINIMAL


def test_resolve_standard_profile_no_flags_equals_profile_standard() -> None:
    args = _make_args(profile="standard")
    assert resolve_selection(args, interactive=False) == PROFILE_STANDARD


def test_resolve_full_profile_no_flags_equals_profile_full() -> None:
    args = _make_args(profile="full")
    assert resolve_selection(args, interactive=False) == PROFILE_FULL


def test_resolve_no_profile_no_flags_defaults_to_full() -> None:
    args = _make_args()
    assert resolve_selection(args, interactive=False) == PROFILE_FULL


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# resolve_selection — overrides
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_resolve_full_minus_notion_and_figma() -> None:
    args = _make_args(profile="full", without_mcp="notion,figma")
    result = resolve_selection(args, interactive=False)
    assert "notion" not in result.mcps
    assert "figma" not in result.mcps
    assert "ahrena" in result.mcps
    assert "github" in result.mcps
    assert "slack" in result.mcps


def test_resolve_minimal_plus_github() -> None:
    args = _make_args(profile="minimal", with_mcp="github")
    result = resolve_selection(args, interactive=False)
    assert result.mcps == frozenset({"ahrena", "github"})


def test_resolve_full_minus_pr_cost_tracking_feature() -> None:
    args = _make_args(profile="full", without_features="pr_cost_tracking")
    result = resolve_selection(args, interactive=False)
    assert "pr_cost_tracking" not in result.optional_features


def test_resolve_minimal_plus_session_tracking_feature() -> None:
    args = _make_args(profile="minimal", with_features="session_tracking")
    result = resolve_selection(args, interactive=False)
    assert result.optional_features == frozenset({"session_tracking"})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# resolve_selection — ahrena pin and validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_resolve_forces_ahrena_even_if_user_excludes_it() -> None:
    args = _make_args(profile="full", without_mcp="ahrena")
    result = resolve_selection(args, interactive=False)
    assert "ahrena" in result.mcps


def test_resolve_rejects_unknown_mcp_name(capsys: pytest.CaptureFixture[str]) -> None:
    args = _make_args(with_mcp="bogus")
    with pytest.raises(SystemExit) as excinfo:
        resolve_selection(args, interactive=False)
    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert "bogus" in captured.err


def test_resolve_rejects_unknown_hook_name() -> None:
    args = _make_args(with_hooks="not-a-hook")
    with pytest.raises(SystemExit) as excinfo:
        resolve_selection(args, interactive=False)
    assert excinfo.value.code == 2


def test_resolve_rejects_unknown_feature_name() -> None:
    args = _make_args(without_features="ghost")
    with pytest.raises(SystemExit) as excinfo:
        resolve_selection(args, interactive=False)
    assert excinfo.value.code == 2


def test_resolve_rejects_unknown_profile() -> None:
    args = _make_args(profile="exotic")
    with pytest.raises(SystemExit) as excinfo:
        resolve_selection(args, interactive=False)
    assert excinfo.value.code == 2


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# check_env_vars
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_check_env_vars_full_warns_for_mcps_with_required_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Strip any pre-existing env vars to make the test deterministic.
    for _name, (_desc, vars_) in MCP_CATALOG.items():
        for var in vars_:
            monkeypatch.delenv(var, raising=False)
    warnings = check_env_vars(PROFILE_FULL)
    joined = "\n".join(warnings)
    # github and figma declare env vars and should warn.
    assert "GITHUB_PAT" in joined
    assert "FIGMA_API_KEY" in joined
    # ahrena, notion, slack do not declare required vars in MCP_CATALOG.
    assert "ahrena" not in joined.lower() or "MCP 'ahrena'" not in joined
    for warn in warnings:
        assert warn.startswith("WARNING: MCP '")


def test_check_env_vars_clears_warning_when_var_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for _name, (_desc, vars_) in MCP_CATALOG.items():
        for var in vars_:
            monkeypatch.delenv(var, raising=False)
    before = check_env_vars(PROFILE_FULL)
    assert any("GITHUB_PAT" in w for w in before)
    monkeypatch.setenv("GITHUB_PAT", "ghp_test_value")
    after = check_env_vars(PROFILE_FULL)
    assert not any("GITHUB_PAT" in w for w in after)


def test_check_env_vars_minimal_emits_no_warnings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for _name, (_desc, vars_) in MCP_CATALOG.items():
        for var in vars_:
            monkeypatch.delenv(var, raising=False)
    # PROFILE_MINIMAL only has ahrena (no required vars).
    assert check_env_vars(PROFILE_MINIMAL) == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# render_directives — content shape
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_render_full_parses_and_lists_every_mcp() -> None:
    content = render_directives(PROFILE_FULL)
    parsed = parse_directives(content)
    servers = get_directive(parsed, "mcp", "servers")
    assert isinstance(servers, list)
    assert set(servers) == set(MCP_CATALOG.keys())


def test_render_full_has_pr_cost_tracking_enabled_true() -> None:
    content = render_directives(PROFILE_FULL)
    parsed = parse_directives(content)
    enabled = get_directive(parsed, "pr_cost_tracking", "enabled")
    # Value is stored as a string by parse_directives.
    assert enabled == "true"


def test_render_minimal_has_only_ahrena_in_mcp_servers() -> None:
    content = render_directives(PROFILE_MINIMAL)
    parsed = parse_directives(content)
    servers = get_directive(parsed, "mcp", "servers")
    assert servers == ["ahrena"]


def test_render_minimal_has_pr_cost_tracking_commented_or_disabled() -> None:
    content = render_directives(PROFILE_MINIMAL)
    parsed = parse_directives(content)
    enabled = get_directive(parsed, "pr_cost_tracking", "enabled", default=None)
    # PROFILE_MINIMAL drops pr_cost_tracking from optional_features, so the
    # section is rendered as a commented skeleton and parse returns no value.
    assert enabled is None


def test_render_minimal_has_rtk_enabled_true_when_rtk_hook_kept() -> None:
    # PROFILE_MINIMAL keeps the rtk hook by design.
    content = render_directives(PROFILE_MINIMAL)
    parsed = parse_directives(content)
    assert get_directive(parsed, "rtk", "enabled") == "true"


def test_render_selection_without_rtk_hook_emits_enabled_false() -> None:
    sel = Selection(
        mcps=frozenset({"ahrena"}),
        hooks=frozenset(),
        optional_features=frozenset(),
    )
    content = render_directives(sel)
    parsed = parse_directives(content)
    assert get_directive(parsed, "rtk", "enabled") == "false"


def test_render_full_has_notifications_provider_slack() -> None:
    content = render_directives(PROFILE_FULL)
    parsed = parse_directives(content)
    assert get_directive(parsed, "notifications", "provider") == "slack"


def test_render_includes_every_optional_feature_key_when_full() -> None:
    content = render_directives(PROFILE_FULL)
    for key in OPTIONAL_FEATURES:
        # Each feature key should appear as a top-level section header
        # somewhere in the rendered file (uncommented when selected).
        assert f"\n{key}:" in content, f"feature {key!r} missing from full render"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# render_directives ↔ framework/.directives.sample parity
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_directives_sample_matches_full_render() -> None:
    """framework/.directives.sample MUST be the literal Full-default output of
    render_directives(PROFILE_FULL). Regenerate via render_directives()."""
    repo_root = Path(__file__).resolve().parents[2]
    sample_path = repo_root / "framework" / ".directives.sample"
    assert sample_path.exists(), f"missing {sample_path}"
    on_disk = sample_path.read_text(encoding="utf-8")
    rendered = render_directives(PROFILE_FULL)
    assert on_disk == rendered, (
        "framework/.directives.sample drifted from render_directives(PROFILE_FULL). "
        "Regenerate with: python3 -c 'from scripts.install import render_directives, "
        "PROFILE_FULL; print(render_directives(PROFILE_FULL), end=\"\")' "
        "> framework/.directives.sample"
    )
