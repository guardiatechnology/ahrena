"""Ahrena `mcp_enable`: activate or deactivate MCP servers per project.

Reads server declarations from `framework/mcp/<name>.json` (or the
project override at `.ahrena/mcp/<name>.json`), resolves their
`requires` array for the chosen platform, runs preflight at the `mcp`
tier to install any missing local dependency (e.g. Node for npx-tier
servers), updates `.ahrena/.directives` and re-runs the merger from
`install.install_mcp()` so platform configs (`.mcp.json`, `.cursor/mcp.json`)
stay in sync.

Sub-commands:
  list                                  — show known servers and their state
  enable SERVER --platform PLATFORM    — activate a server
  disable SERVER --platform PLATFORM   — deactivate a server

Stdlib-only. Reuses scripts/preflight.py and scripts/install.py at runtime.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Colocated modules: when installed in .ahrena/, preflight.py and install.py
# live next to this file. We insert the directory into sys.path so a plain
# `import preflight` / `import install` resolves correctly.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight  # type: ignore[import-not-found]
import install  # type: ignore[import-not-found]


# Map `requires` entries (`bin:<tool>`) to the preflight ToolSpec catalog.
_REQUIRES_RESOLVER: Dict[str, preflight.ToolSpec] = {
    "bin:node": preflight.NODE,
    "bin:git": preflight.GIT,
    "bin:gh": preflight.GH,
    "bin:gpg": preflight.GPG,
}


# ── Paths ────────────────────────────────────────────────────────


def _framework_mcp_dir(target_dir: Path) -> Path:
    return target_dir / ".ahrena" / "framework" / "mcp"


def _project_mcp_dir(target_dir: Path) -> Path:
    return target_dir / ".ahrena" / "mcp"


def _directives_path(target_dir: Path) -> Path:
    return target_dir / ".ahrena" / ".directives"


# ── Loading ──────────────────────────────────────────────────────


def _load_server(target_dir: Path, server: str) -> Optional[dict]:
    """Project override (`.ahrena/mcp/<name>.json`) wins over framework default."""
    override = _project_mcp_dir(target_dir) / f"{server}.json"
    framework = _framework_mcp_dir(target_dir) / f"{server}.json"
    for p in (override, framework):
        if p.is_file():
            return json.loads(p.read_text())
    return None


def _list_known_servers(target_dir: Path) -> List[str]:
    seen: set[str] = set()
    for d in (_project_mcp_dir(target_dir), _framework_mcp_dir(target_dir)):
        if d.is_dir():
            for p in d.glob("*.json"):
                seen.add(p.stem)
    return sorted(seen)


# ── .directives text manipulation ────────────────────────────────


def _read_directives(target_dir: Path) -> str:
    p = _directives_path(target_dir)
    return p.read_text() if p.is_file() else ""


def _write_directives(target_dir: Path, text: str) -> None:
    _directives_path(target_dir).write_text(text)


_ACTIVE_BLOCK_RE = re.compile(
    # `(?:\n|$)` (instead of strictly `\n`) tolerates a final entry that sits
    # at end-of-file without a trailing newline — which happens after a manual
    # edit. Without it, the body capture stops at the previous entry and the
    # new server gets inserted in the middle of the existing list.
    r"^(mcp:\s*\n\s*servers:\s*\n)((?:\s*-\s*\S+\s*(?:\n|$))*)",
    re.MULTILINE,
)

_COMMENTED_BLOCK_RE = re.compile(
    r"^# mcp:\s*\n# {2,}servers:\s*\n(?:# {4,}-\s*\S+\s*\n)+",
    re.MULTILINE,
)


def _ensure_server_in_directives(text: str, server: str) -> str:
    """Idempotent: make sure mcp.servers contains `server`.
    Three cases: (1) active block exists, (2) sample-commented block exists,
    (3) no block at all."""
    m = _ACTIVE_BLOCK_RE.search(text)
    if m:
        header, body = m.group(1), m.group(2)
        if re.search(rf"^\s*-\s+{re.escape(server)}\s*$", body, re.MULTILINE):
            return text
        indent_m = re.match(r"(\s*)-", body)
        indent = indent_m.group(1) if indent_m else "    "
        # Normalize body to end with `\n` so the new entry sits on its own line
        # even when the captured block's last entry was at EOF without one.
        normalized = body if body.endswith("\n") else body + "\n"
        new_body = normalized + f"{indent}- {server}\n"
        return text[: m.start()] + header + new_body + text[m.end():]

    block = f"mcp:\n  servers:\n    - {server}\n"
    m2 = _COMMENTED_BLOCK_RE.search(text)
    if m2:
        return text[: m2.start()] + block + text[m2.end():]

    sep = "" if text.endswith("\n") else "\n"
    return text + sep + "\n" + block


def _remove_server_from_directives(text: str, server: str) -> str:
    # Match the entry whether it ends with a newline or sits at end-of-file
    # without one (the latter happens when the file was edited manually).
    pattern = re.compile(rf"^(\s*)-\s+{re.escape(server)}\s*(?:\n|$)", re.MULTILINE)
    return pattern.sub("", text)


# ── Platform config cleanup (disable) ────────────────────────────


def _remove_from_platform_config(target_dir: Path, server: str) -> List[str]:
    """Drop the server entry from .mcp.json and .cursor/mcp.json. Returns
    the labels of files that were updated."""
    updated: List[str] = []
    candidates = (
        (target_dir / ".mcp.json", ".mcp.json"),
        (target_dir / ".cursor" / "mcp.json", ".cursor/mcp.json"),
    )
    for path, label in candidates:
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        servers = data.get("mcpServers")
        if isinstance(servers, dict) and server in servers:
            del servers[server]
            path.write_text(json.dumps(data, indent=2) + "\n")
            updated.append(label)
    return updated


# ── Commands ─────────────────────────────────────────────────────


def cmd_enable(
    target_dir: Path,
    server: str,
    platform: str,
    *,
    non_interactive: bool,
) -> int:
    raw = _load_server(target_dir, server)
    if raw is None:
        print(f"  ERROR: no MCP config for server '{server}' in framework/mcp/ or .ahrena/mcp/")
        return 2
    block = raw.get(platform)
    if not isinstance(block, dict):
        print(f"  ERROR: '{server}' has no '{platform}' block (server JSON missing platform key)")
        return 2

    # Resolve `requires` → preflight specs
    requires = block.get("requires", []) or []
    specs: List[preflight.ToolSpec] = []
    unresolved: List[str] = []
    for entry in requires:
        spec = _REQUIRES_RESOLVER.get(entry)
        if spec:
            specs.append(spec)
        else:
            unresolved.append(entry)
    # Unrecognised `requires` entries mean the framework cannot guarantee a
    # working environment for the server — silent ignore would surface as
    # confusing runtime errors. Default to fatal under --non-interactive
    # (CI must never proceed past unknown deps), and prompt the human in
    # interactive sessions so a known-safe entry can still be skipped.
    if unresolved:
        msg = f"unrecognised requires entries for '{server}': {unresolved}"
        remediation = (
            f"  Either remove them from the server JSON, override the config at\n"
            f"  .ahrena/mcp/{server}.json, or extend _REQUIRES_RESOLVER in mcp_enable.py\n"
            f"  to handle the new dependency type."
        )
        if non_interactive:
            print(f"  ERROR: {msg}")
            print(remediation)
            return 3
        print(f"  WARNING: {msg}")
        print(remediation)
        try:
            answer = input("  Proceed anyway? [y/N] ").strip().lower()
        except EOFError:
            answer = "n"
        if answer not in {"y", "yes"}:
            print(f"  Activation of '{server}' cancelled.")
            return 3

    if specs:
        interactive = False if non_interactive else None
        report = preflight.run("mcp", specs, interactive=interactive)
        if not report.ok:
            print(f"  ERROR: dependencies missing — cannot activate '{server}'.")
            return 3

    # Update .ahrena/.directives idempotently
    text = _read_directives(target_dir)
    new_text = _ensure_server_in_directives(text, server)
    if new_text != text:
        _write_directives(target_dir, new_text)
        print(f"  Added '{server}' to mcp.servers in .ahrena/.directives")
    else:
        print(f"  '{server}' already in mcp.servers")

    # Re-run the install.py merger so platform configs reflect the new state
    directives = install.parse_directives(new_text)
    ahrena_dir = target_dir / ".ahrena"
    install.install_mcp(ahrena_dir, target_dir, directives, dry_run=False)
    return 0


def cmd_disable(target_dir: Path, server: str, platform: str) -> int:
    # NOTE: `platform` is accepted for symmetry with `enable` but is not
    # required to disable — we strip the entry from both .mcp.json and
    # .cursor/mcp.json whenever they exist.
    text = _read_directives(target_dir)
    new_text = _remove_server_from_directives(text, server)
    if new_text != text:
        _write_directives(target_dir, new_text)
        print(f"  Removed '{server}' from mcp.servers in .ahrena/.directives")
    else:
        print(f"  '{server}' was not in mcp.servers (nothing to do)")

    cleaned = _remove_from_platform_config(target_dir, server)
    for label in cleaned:
        print(f"  Removed '{server}' from {label}")
    return 0


def cmd_list(target_dir: Path) -> int:
    text = _read_directives(target_dir)
    directives = install.parse_directives(text)
    enabled = install.get_directive(directives, "mcp", "servers", default=[]) or []
    enabled_set: set[str] = set(enabled) if isinstance(enabled, list) else set()
    known = _list_known_servers(target_dir)

    print()
    header = f"  {'Server':<14} {'State':<10} {'Transport':<12} {'Requires'}"
    print(header)
    print(f"  {'-' * 14} {'-' * 10} {'-' * 12} {'-' * 8}")
    for name in known:
        state = "enabled" if name in enabled_set else "available"
        raw = _load_server(target_dir, name) or {}
        # Summarise the transport from whichever platform block exists first.
        block = raw.get("cursor") or raw.get("claude-code") or {}
        if "url" in block:
            transport = "http"
        elif "command" in block:
            transport = str(block.get("command"))
        else:
            transport = "?"
        requires = block.get("requires") or []
        req_str = ", ".join(requires) if requires else "none"
        print(f"  {name:<14} {state:<10} {transport:<12} {req_str}")
    return 0


# ── CLI ─────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mcp_enable.py",
        description="Activate or deactivate MCP servers per project.",
    )
    p.add_argument("--target", default=".", help="project root (default: cwd)")
    p.add_argument(
        "--platform",
        choices=["cursor", "claude-code"],
        help="target platform (required for enable/disable)",
    )
    p.add_argument(
        "--non-interactive",
        action="store_true",
        help="never prompt; missing dependencies block activation",
    )

    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list known MCP servers and their state")
    enable = sub.add_parser("enable", help="activate a server for the chosen platform")
    enable.add_argument("server", help="server name (e.g. github, notion, figma)")
    disable = sub.add_parser("disable", help="deactivate a server")
    disable.add_argument("server", help="server name")
    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    target_dir = Path(args.target).resolve()

    if args.command == "list":
        sys.exit(cmd_list(target_dir))

    if not args.platform:
        print("  ERROR: --platform is required for enable/disable")
        sys.exit(2)

    if args.command == "enable":
        sys.exit(
            cmd_enable(
                target_dir, args.server, args.platform,
                non_interactive=args.non_interactive,
            )
        )

    if args.command == "disable":
        sys.exit(cmd_disable(target_dir, args.server, args.platform))


if __name__ == "__main__":
    main()
