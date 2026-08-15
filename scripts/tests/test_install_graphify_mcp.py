"""Coverage for Graphify's opt-in CLI and MCP installation contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import (  # noqa: E402
    GRAPHIFY_PACKAGE,
    PROFILE_FULL,
    _install_graphify_binary,
    get_directive,
    parse_directives,
    render_directives,
    resolve_selection,
)


def test_graphify_is_explicitly_disabled_in_full_profile() -> None:
    parsed = parse_directives(render_directives(PROFILE_FULL))
    assert "graphify" not in PROFILE_FULL.optional_features
    assert "graphify" not in PROFILE_FULL.mcps
    assert get_directive(parsed, "graphify", "enabled") == "false"


def test_graphify_cli_and_mcp_can_be_selected_together() -> None:
    args = argparse.Namespace(
        profile="minimal",
        with_mcp="graphify",
        without_mcp="",
        with_hooks="",
        without_hooks="",
        with_features="graphify",
        without_features="",
        with_setup="",
        without_setup="",
        non_interactive=True,
    )
    selected = resolve_selection(args, interactive=False)
    parsed = parse_directives(render_directives(selected))
    assert "graphify" in selected.mcps
    assert get_directive(parsed, "graphify", "enabled") == "true"


def test_binary_install_uses_mcp_extra_and_checks_exit_code() -> None:
    assert GRAPHIFY_PACKAGE == "graphifyy[mcp]"
    completed = type("Completed", (), {"returncode": 7})()
    with patch(
        "install.shutil.which",
        side_effect=lambda name: "/usr/bin/uv" if name == "uv" else None,
    ), patch("install.subprocess.run", return_value=completed) as run:
        assert _install_graphify_binary() is False
    assert run.call_args.args[0] == ["uv", "tool", "install", "graphifyy[mcp]"]


def test_graphify_mcp_manifest_is_valid() -> None:
    source = Path(__file__).resolve().parents[2] / "framework" / "mcp" / "graphify.json"
    manifest = json.loads(source.read_text(encoding="utf-8"))
    assert manifest["cursor"]["command"] == "graphify-mcp"
    assert manifest["claude-code"]["args"] == ["--graph", "graphify-out/graph.json"]
