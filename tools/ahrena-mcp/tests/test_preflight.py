"""Regression tests for scripts/preflight.py.

Covers the fixes Argos's PR #82 review surfaced (Python executable
name on Windows, install_tool shell-injection surface) and the core
helpers that future contributions may regress (parse_semver,
detect_os, check_tool, install_tool fallback).

Loaded via importlib because scripts/preflight.py is not part of an
installed package — same pattern as test_install_mcp.py.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
PREFLIGHT_PY = REPO_ROOT / "scripts" / "preflight.py"


@pytest.fixture(scope="module")
def preflight():
    spec = importlib.util.spec_from_file_location("preflight", PREFLIGHT_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["preflight"] = module
    spec.loader.exec_module(module)
    return module


# ── _python_executable_name ──────────────────────────────────────


def test_python_name_resolves_python_on_windows(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "Windows")
    assert preflight._python_executable_name() == "python"


def test_python_name_resolves_python3_on_linux(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "Linux")
    assert preflight._python_executable_name() == "python3"


def test_python_name_resolves_python3_on_darwin(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "Darwin")
    assert preflight._python_executable_name() == "python3"


# ── _parse_semver ────────────────────────────────────────────────


def test_parse_semver_extracts_three_segments(preflight):
    assert preflight._parse_semver("Python 3.12.1") == (3, 12, 1)


def test_parse_semver_extracts_two_segments(preflight):
    # GNU Make 3.81 — only major.minor
    assert preflight._parse_semver("GNU Make 3.81") == (3, 81)


def test_parse_semver_returns_none_for_unparseable(preflight):
    assert preflight._parse_semver("no version here") is None


# ── detect_os ────────────────────────────────────────────────────


def test_detect_os_macos(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "Darwin")
    assert preflight.detect_os() == "macos"


def test_detect_os_windows(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "Windows")
    assert preflight.detect_os() == "windows"


def test_detect_os_linux_debian(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "Linux")
    monkeypatch.setattr(preflight, "_has_file", lambda p: p == "/etc/debian_version")
    assert preflight.detect_os() == "linux-debian"


def test_detect_os_linux_rhel(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        preflight,
        "_has_file",
        lambda p: p == "/etc/redhat-release",
    )
    assert preflight.detect_os() == "linux-rhel"


def test_detect_os_unknown(preflight, monkeypatch):
    monkeypatch.setattr(preflight._platform, "system", lambda: "FreeBSD")
    assert preflight.detect_os() == "unknown"


# ── check_tool ───────────────────────────────────────────────────


def test_check_tool_missing_returns_not_found(preflight, monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda name: None)
    spec = preflight.ToolSpec(name="nonexistent-binary", purpose="test")
    report = preflight.check_tool(spec)
    assert report.found is False
    assert report.path is None


def test_check_tool_present_returns_path(preflight, monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda name: "/usr/bin/git")
    spec = preflight.ToolSpec(name="git", purpose="test")
    report = preflight.check_tool(spec)
    assert report.found is True
    assert report.path == "/usr/bin/git"


def test_check_tool_too_old_treated_as_missing(preflight, monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda name: "/usr/bin/python3")

    fake_proc = MagicMock(stdout="Python 3.6.0\n", stderr="")
    monkeypatch.setattr(preflight.subprocess, "run", lambda *a, **kw: fake_proc)

    spec = preflight.ToolSpec(
        name="python3", purpose="test",
        version_flag="--version", min_version=(3, 8),
    )
    report = preflight.check_tool(spec)
    assert report.found is False  # too-old → not found
    assert report.version == "Python 3.6.0"


# ── install_tool ─────────────────────────────────────────────────


def test_install_tool_no_hint_for_os_returns_false(preflight, capsys):
    spec = preflight.ToolSpec(
        name="foo", purpose="test",
        install_hints={"macos": "brew install foo"},
    )
    assert preflight.install_tool(spec, "windows", dry_run=True) is False
    out = capsys.readouterr().out
    assert "No installer mapped" in out


def test_install_tool_dry_run_does_not_invoke_subprocess(preflight, monkeypatch, capsys):
    sentinel = MagicMock()
    monkeypatch.setattr(preflight.subprocess, "run", sentinel)
    spec = preflight.ToolSpec(
        name="git", purpose="test",
        install_hints={"macos": "brew install git"},
    )
    result = preflight.install_tool(spec, "macos", dry_run=True)
    assert result is False  # dry-run reports no install performed
    sentinel.assert_not_called()


def test_install_tool_uses_shell_false(preflight, monkeypatch):
    """Argos PR #82 review: install_tool must NOT use shell=True so that
    consumers composing ToolSpecs from non-static input do not get a
    shell-injection foothold."""
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return MagicMock(returncode=0)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)
    spec = preflight.ToolSpec(
        name="git", purpose="test",
        install_hints={"linux-debian": "sudo apt-get install -y git"},
    )
    assert preflight.install_tool(spec, "linux-debian", dry_run=False) is True
    # argv must be a list (tokenized via shlex.split), not a single string
    assert isinstance(captured["argv"], list)
    assert captured["argv"] == ["sudo", "apt-get", "install", "-y", "git"]
    # shell=True must not appear in the kwargs (default is False)
    assert captured["kwargs"].get("shell") is not True
