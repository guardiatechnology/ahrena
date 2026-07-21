"""Regression tests for the machine-wide ahrena-mcp pipx install."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALL_PY = REPO_ROOT / "scripts" / "install.py"


@pytest.fixture()
def install_module():
    spec = importlib.util.spec_from_file_location("ahrena_install_package", INSTALL_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ahrena_install_package"] = module
    spec.loader.exec_module(module)
    return module


def _enabled_ahrena_dir(tmp_path: Path) -> Path:
    (tmp_path / ".directives").write_text(
        "mcp:\n  servers:\n    - ahrena\n",
        encoding="utf-8",
    )
    (tmp_path / "tools" / "ahrena-mcp").mkdir(parents=True)
    return tmp_path


def _completed(returncode: int = 0, stdout: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess([], returncode, stdout=stdout, stderr="")


def test_new_install_is_non_editable(
    install_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ahrena_dir = _enabled_ahrena_dir(tmp_path)
    calls: list[list[str]] = []

    monkeypatch.setattr(install_module.shutil, "which", lambda _name: "/usr/bin/pipx")

    def run(command: list[str], **_kwargs):
        calls.append(command)
        if command[1:] == ["list", "--short"]:
            return _completed(stdout="")
        return _completed()

    monkeypatch.setattr(install_module.subprocess, "run", run)

    install_module.install_mcp_package(ahrena_dir)

    expected_path = str(ahrena_dir / "tools" / "ahrena-mcp")
    assert calls[-1] == ["/usr/bin/pipx", "install", "--force", expected_path]
    assert "-e" not in calls[-1]


def test_existing_editable_install_is_migrated_without_prompt(
    install_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ahrena_dir = _enabled_ahrena_dir(tmp_path)
    calls: list[list[str]] = []

    monkeypatch.setattr(install_module.shutil, "which", lambda _name: "/usr/bin/pipx")
    monkeypatch.setattr(
        "builtins.input",
        lambda _prompt: pytest.fail("editable installs must be repaired without prompting"),
    )

    def run(command: list[str], **_kwargs):
        calls.append(command)
        if command[1:] == ["list", "--short"]:
            return _completed(stdout="ahrena-mcp 0.1.0a1\n")
        if command[1:] == [
            "runpip",
            "ahrena-mcp",
            "list",
            "--editable",
            "--format=json",
        ]:
            return _completed(
                stdout=json.dumps(
                    [
                        {
                            "name": "ahrena-mcp",
                            "version": "0.1.0a1",
                            "editable_project_location": "/deleted/project/.ahrena/tools/ahrena-mcp",
                        }
                    ]
                )
            )
        return _completed()

    monkeypatch.setattr(install_module.subprocess, "run", run)

    install_module.install_mcp_package(ahrena_dir)

    expected_path = str(ahrena_dir / "tools" / "ahrena-mcp")
    assert calls[-1] == ["/usr/bin/pipx", "install", "--force", expected_path]


def test_existing_non_editable_install_is_preserved_non_interactively(
    install_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ahrena_dir = _enabled_ahrena_dir(tmp_path)
    calls: list[list[str]] = []

    monkeypatch.setattr(install_module.shutil, "which", lambda _name: "/usr/bin/pipx")
    monkeypatch.setattr(
        install_module.sys,
        "stdin",
        SimpleNamespace(isatty=lambda: False),
    )

    def run(command: list[str], **_kwargs):
        calls.append(command)
        if command[1:] == ["list", "--short"]:
            return _completed(stdout="ahrena-mcp 0.1.0a1\n")
        if command[1:] == [
            "runpip",
            "ahrena-mcp",
            "list",
            "--editable",
            "--format=json",
        ]:
            return _completed(stdout="[]")
        return _completed()

    monkeypatch.setattr(install_module.subprocess, "run", run)

    install_module.install_mcp_package(ahrena_dir)

    assert not any("install" in command[1:] for command in calls)


def test_unreadable_install_mode_is_repaired_conservatively(
    install_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ahrena_dir = _enabled_ahrena_dir(tmp_path)
    calls: list[list[str]] = []

    monkeypatch.setattr(install_module.shutil, "which", lambda _name: "/usr/bin/pipx")

    def run(command: list[str], **_kwargs):
        calls.append(command)
        if command[1:] == ["list", "--short"]:
            return _completed(stdout="ahrena-mcp 0.1.0a1\n")
        if command[1] == "runpip":
            return _completed(returncode=1)
        return _completed()

    monkeypatch.setattr(install_module.subprocess, "run", run)

    install_module.install_mcp_package(ahrena_dir)

    assert calls[-1][1:3] == ["install", "--force"]
    assert "-e" not in calls[-1]
