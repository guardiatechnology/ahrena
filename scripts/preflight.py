"""Ahrena preflight: verify and (optionally) install host tooling.

Stdlib-only. Compatible with Python 3.8+. Used by:
  - install.py: hard tier (block on missing) + soft tier (warn + offer install)
  - mcp_enable.py: mcp tier (per-server requires; same UX as soft)

The module exposes a small, declarative API:
  - ToolSpec       : describes one tool (name, version requirement, install hints per OS)
  - check_tool()   : returns ToolReport for a single ToolSpec
  - install_tool() : runs the OS-native install command
  - run()          : checks a list of specs at a given level and reports/installs accordingly
  - HARD_TOOLS, SOFT_TOOLS, NODE: ready-made specs reused across the framework

The module deliberately does not depend on any third-party package; it is consumed
by installer scripts that ship in `.ahrena/` and run before any pip-installed code is available.
"""

from __future__ import annotations

import os
import platform as _platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


# ── Data types ───────────────────────────────────────────────────


@dataclass(frozen=True)
class ToolSpec:
    """One tool the preflight needs to verify (and optionally install)."""

    name: str
    purpose: str
    version_flag: Optional[str] = None
    min_version: Optional[Tuple[int, ...]] = None
    install_hints: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolReport:
    spec: ToolSpec
    found: bool
    version: Optional[str] = None
    path: Optional[str] = None


@dataclass(frozen=True)
class PreflightReport:
    level: str
    results: Tuple[ToolReport, ...]

    @property
    def missing(self) -> Tuple[ToolReport, ...]:
        return tuple(r for r in self.results if not r.found)

    @property
    def ok(self) -> bool:
        return all(r.found for r in self.results)


# ── OS detection ─────────────────────────────────────────────────


def detect_os() -> str:
    """Return one of: macos, linux-debian, linux-rhel, linux-other, windows, unknown."""
    sys_name = _platform.system().lower()
    if sys_name == "darwin":
        return "macos"
    if sys_name == "windows":
        return "windows"
    if sys_name == "linux":
        if _has_file("/etc/debian_version") or _has_file("/etc/lsb-release"):
            return "linux-debian"
        if _has_file("/etc/redhat-release") or _has_file("/etc/fedora-release"):
            return "linux-rhel"
        return "linux-other"
    return "unknown"


def _has_file(path: str) -> bool:
    try:
        return os.path.isfile(path)
    except OSError:
        return False


# ── Tool checking ────────────────────────────────────────────────


def check_tool(spec: ToolSpec) -> ToolReport:
    """Check whether a tool is on PATH and meets min_version (if declared)."""
    found_path = shutil.which(spec.name)
    if not found_path:
        return ToolReport(spec=spec, found=False)
    version_str = _query_version(spec)
    if spec.min_version and version_str:
        parsed = _parse_semver(version_str)
        if parsed and parsed < spec.min_version:
            # present but too old — treat as missing so soft/hard handlers offer install
            return ToolReport(spec=spec, found=False, version=version_str, path=found_path)
    return ToolReport(spec=spec, found=True, version=version_str, path=found_path)


def _query_version(spec: ToolSpec) -> Optional[str]:
    if not spec.version_flag:
        return None
    try:
        proc = subprocess.run(
            [spec.name, spec.version_flag],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    output = (proc.stdout or proc.stderr or "").strip().splitlines()
    return output[0] if output else None


def _parse_semver(s: str) -> Optional[Tuple[int, ...]]:
    """Best-effort parse of MAJOR.MINOR(.PATCH) from a free-form version string."""
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", s)
    if not m:
        return None
    return tuple(int(g) for g in m.groups() if g is not None)


# ── Tool installation ────────────────────────────────────────────


def install_tool(spec: ToolSpec, os_kind: str, *, dry_run: bool = False) -> bool:
    """Attempt to install a tool via the OS-native package manager.

    Returns True on success. On unsupported OS or install failure the agent
    is expected to communicate with the user and let them install manually.
    """
    cmd = spec.install_hints.get(os_kind)
    if not cmd:
        print(f"  No installer mapped for {spec.name!r} on {os_kind!r}.")
        print(f"  Please install {spec.name!r} manually and re-run.")
        return False
    print(f"  Installing {spec.name} via: {cmd}")
    if dry_run:
        print("  [DRY-RUN] Skipped.")
        return False
    try:
        proc = subprocess.run(cmd, shell=True, check=False, timeout=600)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"  Install failed: {exc}")
        return False
    if proc.returncode != 0:
        print(f"  Install command exited with status {proc.returncode}.")
        return False
    return True


# ── Preflight runner ─────────────────────────────────────────────


def run(
    level: str,
    specs: Iterable[ToolSpec],
    *,
    interactive: Optional[bool] = None,
    dry_run: bool = False,
) -> PreflightReport:
    """Check the given tools and act according to the level.

    - hard : missing tool → exit(1) with install hints for each.
    - soft : missing tool → print warning; if interactive, offer to install.
    - mcp  : same UX as soft; used by mcp_enable.py per-server requires.

    `interactive` defaults to autodetect (sys.stdin.isatty()). Pass False
    explicitly for CI runs.
    """
    if level not in {"hard", "soft", "mcp"}:
        raise ValueError(f"unknown preflight level: {level!r}")

    specs_t: Tuple[ToolSpec, ...] = tuple(specs)
    results = tuple(check_tool(spec) for spec in specs_t)
    report = PreflightReport(level=level, results=results)
    _print_table(report)
    if report.ok:
        return report

    if level == "hard":
        _handle_hard(report)
        return report  # unreachable; _handle_hard exits

    if interactive is None:
        interactive = sys.stdin.isatty()

    if not interactive:
        print()
        print(
            f"WARNING: {len(report.missing)} {level} tool(s) missing; "
            "non-interactive mode — skipping install offer."
        )
        _print_install_hints(report.missing)
        return report

    _handle_soft_or_mcp(report, dry_run=dry_run)
    return report


def _handle_hard(report: PreflightReport) -> None:
    print()
    print("ERROR: required tools missing — cannot continue.")
    _print_install_hints(report.missing)
    sys.exit(1)


def _handle_soft_or_mcp(report: PreflightReport, *, dry_run: bool) -> None:
    os_kind = detect_os()
    for r in report.missing:
        cmd = r.spec.install_hints.get(os_kind, "")
        if not cmd:
            print(f"  {r.spec.name}: no installer mapped for {os_kind}; skip.")
            continue
        try:
            answer = input(f"  Install {r.spec.name} via `{cmd}`? [Y/n] ").strip().lower()
        except EOFError:
            print(f"  {r.spec.name}: stdin closed; skipping install offer.")
            continue
        if answer in {"", "y", "yes"}:
            install_tool(r.spec, os_kind, dry_run=dry_run)
        else:
            print(f"  Skipped {r.spec.name}.")


# ── Output ───────────────────────────────────────────────────────


def _print_table(report: PreflightReport) -> None:
    print(f"\n--- Preflight ({report.level}) ---")
    if not report.results:
        print("  (no tools to check)")
        return
    name_w = max(len(r.spec.name) for r in report.results)
    for r in report.results:
        mark = "✓" if r.found else "✗"
        ver = f"  {r.version}" if r.version else ""
        path = f"  ({r.path})" if r.path and r.found else ""
        print(f"  [{mark}] {r.spec.name:<{name_w}}  {r.spec.purpose}{ver}{path}")


def _print_install_hints(missing: Tuple[ToolReport, ...]) -> None:
    os_kind = detect_os()
    for r in missing:
        cmd = r.spec.install_hints.get(os_kind, "(no installer mapped)")
        print(f"  - {r.spec.name}: {r.spec.purpose}")
        print(f"      install ({os_kind}): {cmd}")


# ── Tool catalog ─────────────────────────────────────────────────
# Reusable specs. Consumers compose tier lists from these.


PYTHON = ToolSpec(
    name="python3",
    purpose="Python interpreter (3.8+) — runs Ahrena scripts",
    version_flag="--version",
    min_version=(3, 8),
)

GIT = ToolSpec(
    name="git",
    purpose="Git — version control",
    version_flag="--version",
    install_hints={
        "macos": "brew install git",
        "linux-debian": "sudo apt-get install -y git",
        "linux-rhel": "sudo dnf install -y git",
        "windows": "winget install --id Git.Git -e",
    },
)

MAKE = ToolSpec(
    name="make",
    purpose="GNU make — Ahrena Makefile entrypoint",
    version_flag="--version",
    install_hints={
        "macos": "xcode-select --install",
        "linux-debian": "sudo apt-get install -y build-essential",
        "linux-rhel": "sudo dnf groupinstall -y 'Development Tools'",
        "windows": "winget install --id GnuWin32.Make -e",
    },
)

GH = ToolSpec(
    name="gh",
    purpose="GitHub CLI — Issue-Driven flow, stacked PRs, cost-stamp",
    version_flag="--version",
    install_hints={
        "macos": "brew install gh",
        "linux-debian": "sudo apt-get install -y gh",
        "linux-rhel": "sudo dnf install -y gh",
        "windows": "winget install --id GitHub.cli -e",
    },
)

GPG = ToolSpec(
    name="gpg",
    purpose="GnuPG — signed commits (lex-signed-commits)",
    version_flag="--version",
    install_hints={
        "macos": "brew install gnupg",
        "linux-debian": "sudo apt-get install -y gnupg",
        "linux-rhel": "sudo dnf install -y gnupg2",
        "windows": "winget install --id GnuPG.Gpg4win -e",
    },
)

NODE = ToolSpec(
    name="node",
    purpose="Node.js — runtime for npx-based MCP servers",
    version_flag="--version",
    min_version=(18, 0),
    install_hints={
        "macos": "brew install node",
        "linux-debian": "sudo apt-get install -y nodejs npm",
        "linux-rhel": "sudo dnf install -y nodejs npm",
        "windows": "winget install --id OpenJS.NodeJS.LTS -e",
    },
)


# Tier presets consumed by install.py.
HARD_TOOLS: Tuple[ToolSpec, ...] = (PYTHON, GIT, MAKE)
SOFT_TOOLS: Tuple[ToolSpec, ...] = (GH, GPG)


# Standalone entry point (allows `python3 preflight.py [hard|soft]` for ad-hoc checks).
def main(argv: Optional[List[str]] = None) -> None:
    args = list(argv) if argv is not None else sys.argv[1:]
    levels = args or ["hard", "soft"]
    for level in levels:
        if level == "hard":
            run("hard", HARD_TOOLS)
        elif level == "soft":
            run("soft", SOFT_TOOLS)
        else:
            print(f"unknown level: {level!r} (expected 'hard' or 'soft')")
            sys.exit(2)


if __name__ == "__main__":
    main()
