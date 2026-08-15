"""Regression tests for scripts/mcp_enable.py.

Anchored on the two BLOCKERs Argos's PR #82 review surfaced (the
EOF-no-newline edge case in both _ensure_server_in_directives and
_remove_server_from_directives) plus the resolver and platform-config
cleanup paths that future contributions can regress.

mcp_enable imports preflight and install at module import time; both
scripts live in the same `scripts/` directory, so we add it to
sys.path before loading the target.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"


@pytest.fixture(scope="module")
def mcp_enable():
    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location(
        "mcp_enable_under_test", SCRIPTS_DIR / "mcp_enable.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ── _ensure_server_in_directives ─────────────────────────────────


def test_ensure_appends_to_active_block(mcp_enable):
    inp = "mcp:\n  servers:\n    - github\n"
    out = mcp_enable._ensure_server_in_directives(inp, "notion")
    assert out == "mcp:\n  servers:\n    - github\n    - notion\n"


def test_ensure_idempotent_when_already_present(mcp_enable):
    inp = "mcp:\n  servers:\n    - github\n    - notion\n"
    out = mcp_enable._ensure_server_in_directives(inp, "notion")
    assert out == inp


def test_ensure_handles_eof_without_newline_BLOCKER_1(mcp_enable):
    """Argos BLOCKER #1: when the active block's last entry sits at EOF
    without a trailing newline, the new server must still land at the end
    of the list — not in the middle."""
    inp = "mcp:\n  servers:\n    - github\n    - notion"  # no final \n
    out = mcp_enable._ensure_server_in_directives(inp, "figma")
    assert out == "mcp:\n  servers:\n    - github\n    - notion\n    - figma\n"


def test_ensure_replaces_commented_sample_block(mcp_enable):
    inp = (
        "# mcp:\n"
        "#   servers:\n"
        "#     - github\n"
        "#     - notion\n"
        "#     - figma\n"
    )
    out = mcp_enable._ensure_server_in_directives(inp, "github")
    assert out == "mcp:\n  servers:\n    - github\n"


def test_ensure_appends_block_when_no_section_exists(mcp_enable):
    inp = "language:\n  default: pt-BR\n"
    out = mcp_enable._ensure_server_in_directives(inp, "github")
    assert out.endswith("mcp:\n  servers:\n    - github\n")


# ── _remove_server_from_directives ───────────────────────────────


def test_remove_strips_present_entry(mcp_enable):
    inp = "mcp:\n  servers:\n    - github\n    - notion\n"
    out = mcp_enable._remove_server_from_directives(inp, "notion")
    assert out == "mcp:\n  servers:\n    - github\n"


def test_remove_noop_when_absent(mcp_enable):
    inp = "mcp:\n  servers:\n    - github\n"
    out = mcp_enable._remove_server_from_directives(inp, "notion")
    assert out == inp


def test_remove_handles_eof_without_newline_BLOCKER_2(mcp_enable):
    """Argos BLOCKER #2 (also gemini's suggestion): an entry sitting at
    EOF without a trailing newline must still be removable."""
    inp = "mcp:\n  servers:\n    - github\n    - notion"  # no final \n
    out = mcp_enable._remove_server_from_directives(inp, "notion")
    assert out == "mcp:\n  servers:\n    - github\n"


# ── _REQUIRES_RESOLVER ───────────────────────────────────────────


def test_requires_resolver_known_entries(mcp_enable):
    assert mcp_enable._REQUIRES_RESOLVER["bin:node"].name == "node"
    assert mcp_enable._REQUIRES_RESOLVER["bin:gh"].name == "gh"
    assert mcp_enable._REQUIRES_RESOLVER["bin:gpg"].name == "gpg"
    assert mcp_enable._REQUIRES_RESOLVER["bin:git"].name == "git"


def test_requires_resolver_unknown_entry_yields_none(mcp_enable):
    assert mcp_enable._REQUIRES_RESOLVER.get("bin:foobar") is None


# ── _remove_from_platform_config ─────────────────────────────────


def test_remove_from_platform_config_strips_entry(tmp_path, mcp_enable):
    cfg = tmp_path / ".mcp.json"
    cfg.write_text(json.dumps({
        "mcpServers": {
            "ahrena": {"command": "ahrena-mcp"},
            "github": {"type": "http", "url": "https://api.githubcopilot.com/mcp/"},
        },
    }))
    updated = mcp_enable._remove_from_platform_config(tmp_path, "github")
    assert updated == [".mcp.json"]
    after = json.loads(cfg.read_text())
    assert "github" not in after["mcpServers"]
    assert "ahrena" in after["mcpServers"]


def test_remove_from_platform_config_noop_when_server_absent(tmp_path, mcp_enable):
    cfg = tmp_path / ".mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {"ahrena": {"command": "ahrena-mcp"}}}))
    updated = mcp_enable._remove_from_platform_config(tmp_path, "github")
    assert updated == []  # nothing to remove


def test_remove_from_platform_config_handles_missing_files(tmp_path, mcp_enable):
    # Neither .mcp.json nor .cursor/mcp.json exist — must not raise
    updated = mcp_enable._remove_from_platform_config(tmp_path, "github")
    assert updated == []


def test_codex_enable_and_disable_use_native_config(tmp_path, mcp_enable):
    mcp_dir = tmp_path / ".ahrena" / "framework" / "mcp"
    mcp_dir.mkdir(parents=True)
    (mcp_dir / "notion.json").write_text(json.dumps({
        "claude-code": {"type": "http", "url": "https://mcp.notion.com/mcp"},
    }))
    directives = tmp_path / ".ahrena" / ".directives"
    directives.write_text("language:\n  default: en\n")

    assert mcp_enable.cmd_enable(
        tmp_path, "notion", "codex", non_interactive=True,
    ) == 0
    config = (tmp_path / ".codex" / "config.toml").read_text()
    assert "[mcp_servers.notion]" in config

    assert mcp_enable.cmd_disable(tmp_path, "notion", "codex") == 0
    config_path = tmp_path / ".codex" / "config.toml"
    assert not config_path.exists() or "[mcp_servers.notion]" not in config_path.read_text()
