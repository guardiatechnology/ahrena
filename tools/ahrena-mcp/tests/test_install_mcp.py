"""Regression tests for scripts/install.py install_mcp().

The `install_mcp` function in scripts/install.py is responsible for
merging MCP server configs from `framework/mcp/<name>.json` into the
target project's platform files. The Claude Code path was previously
broken (writing `mcpServers` to `.claude/settings.json`, which the
project schema rejects) — this PR fixes it to write to `.mcp.json`
at the project root + `enabledMcpjsonServers` in settings.json.

These tests exercise the merger end-to-end against a temp target,
covering the silent-breakage edge cases that motivated the fix.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALL_PY = REPO_ROOT / "scripts" / "install.py"


@pytest.fixture(scope="module")
def install_mcp():
    """Load install.py as a module and return its install_mcp callable."""
    spec = importlib.util.spec_from_file_location("ahrena_install", INSTALL_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ahrena_install"] = module
    spec.loader.exec_module(module)
    return module.install_mcp


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_writes_three_canonical_files_for_ahrena(install_mcp, tmp_path: Path) -> None:
    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": ["ahrena"]}})

    cursor_mcp = _read_json(tmp_path / ".cursor" / "mcp.json")
    project_mcp = _read_json(tmp_path / ".mcp.json")
    settings = _read_json(tmp_path / ".claude" / "settings.json")

    assert "ahrena" in cursor_mcp["mcpServers"]
    assert "ahrena" in project_mcp["mcpServers"]
    assert "ahrena" in settings["enabledMcpjsonServers"]


def test_preserves_existing_mcpservers_entry_in_project_mcp_json(
    install_mcp, tmp_path: Path
) -> None:
    """Regression: the merger MUST NOT clobber pre-existing servers."""
    (tmp_path / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "github": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-github"],
                    }
                }
            },
            indent=2,
        )
        + "\n"
    )
    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": ["ahrena"]}})

    project_mcp = _read_json(tmp_path / ".mcp.json")
    assert set(project_mcp["mcpServers"].keys()) == {"github", "ahrena"}
    # github entry untouched
    assert project_mcp["mcpServers"]["github"]["command"] == "npx"


def test_preserves_existing_permissions_in_settings_and_appends_to_enabled(
    install_mcp, tmp_path: Path
) -> None:
    """Regression: settings.json should keep its other keys intact."""
    settings_path = tmp_path / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(
        json.dumps(
            {
                "permissions": {"allow": ["Bash(git *)"]},
                "enabledMcpjsonServers": ["github"],
            },
            indent=2,
        )
        + "\n"
    )
    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": ["ahrena"]}})

    settings = _read_json(settings_path)
    assert settings["permissions"]["allow"] == ["Bash(git *)"]
    assert settings["enabledMcpjsonServers"] == ["github", "ahrena"]


def test_idempotent_on_re_run(install_mcp, tmp_path: Path) -> None:
    """Two consecutive runs MUST produce the same final state."""
    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": ["ahrena"]}})
    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": ["ahrena"]}})

    settings = _read_json(tmp_path / ".claude" / "settings.json")
    project_mcp = _read_json(tmp_path / ".mcp.json")
    cursor_mcp = _read_json(tmp_path / ".cursor" / "mcp.json")

    assert settings["enabledMcpjsonServers"] == ["ahrena"]
    assert list(project_mcp["mcpServers"].keys()) == ["ahrena"]
    assert list(cursor_mcp["mcpServers"].keys()) == ["ahrena"]


def test_does_nothing_when_mcp_servers_absent(install_mcp, tmp_path: Path) -> None:
    install_mcp(REPO_ROOT, tmp_path, {})
    install_mcp(REPO_ROOT, tmp_path, {"mcp": {}})
    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": []}})

    assert not (tmp_path / ".cursor" / "mcp.json").exists()
    assert not (tmp_path / ".mcp.json").exists()
    assert not (tmp_path / ".claude" / "settings.json").exists()


def test_preserves_enabled_true_meaning_enable_all(install_mcp, tmp_path: Path) -> None:
    """Regression: `enabledMcpjsonServers: true` (enable-all) MUST be left intact."""
    settings_path = tmp_path / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(json.dumps({"enabledMcpjsonServers": True}) + "\n")

    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": ["ahrena"]}})

    settings = _read_json(settings_path)
    assert settings["enabledMcpjsonServers"] is True


def test_warns_and_resets_when_enabled_has_unexpected_type(
    install_mcp, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Non-list, non-True types are coerced to list with a warning to stderr."""
    settings_path = tmp_path / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(json.dumps({"enabledMcpjsonServers": "ahrena"}) + "\n")

    install_mcp(REPO_ROOT, tmp_path, {"mcp": {"servers": ["ahrena"]}})

    settings = _read_json(settings_path)
    assert settings["enabledMcpjsonServers"] == ["ahrena"]
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "enabledMcpjsonServers" in captured.err
