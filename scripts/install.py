#!/usr/bin/env python3
"""
Ahrena: AI-First Capability Framework — Installer

Downloads the Ahrena framework from GitHub and installs it locally.
Optionally generates platform-specific files (e.g., Cursor IDE).

Bootstrap (nothing exists locally):
  macOS/Linux:
    curl -sSL https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py | python3 - --platform cursor
  Windows (PowerShell):
    irm https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; del install.py

After first install:
  make -f .ahrena/Makefile install-cursor
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEFAULT_REPO = "https://github.com/guardiatechnology/ahrena"
DEFAULT_VERSION = "main"
MIN_PYTHON = (3, 8)

# WHY: SemVer tags ship as `vX.Y.Z`; the .version manifest stores `X.Y.Z`
# (no `v`) so consumers can use the value directly in version comparisons.
# Non-tag refs (branches, commit-ish) are written verbatim.
_SEMVER_TAG_RE = re.compile(r"^v(\d+\.\d+\.\d+(?:[-+].*)?)$")


def resolve_install_version(args: argparse.Namespace) -> str:
    """Resolve the version string written into `.ahrena/.version` at install time.

    Resolution order:
      1. `--source PATH` or `--local`  -> read `git describe --tags --abbrev=0`
         from the source repo (strip `v` prefix) so a local install reflects the
         tip of the source tree, not the literal `main` from DEFAULT_VERSION.
      2. `--self` install               -> same git describe path against the
         repo containing this script.
      3. Remote install                  -> use `args.version` verbatim,
         stripping the `v` prefix only when the value matches a SemVer tag.
         Branch names (`main`, `release/*`) and commit-ish refs are preserved
         as-is so the manifest reflects the exact ref consumed.

    Returns the version string. Returns empty string when no value can be
    resolved (caller decides how to react: skip the write, log a warning, ...).
    """
    if args.source is not None:
        repo_path = Path(args.source).resolve()
        return _git_describe_or_blank(repo_path)
    if getattr(args, "self_source", False):
        repo_path = Path(__file__).resolve().parent.parent
        return _git_describe_or_blank(repo_path)
    if args.local:
        return _git_describe_or_blank(Path(".").resolve())
    raw = (args.version or "").strip()
    if not raw:
        return ""
    match = _SEMVER_TAG_RE.match(raw)
    if match:
        return match.group(1)
    return raw


def _git_describe_or_blank(repo_path: Path) -> str:
    """Return `git describe --tags --abbrev=0` (no `v` prefix) or blank on failure."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    raw = result.stdout.strip()
    if not raw:
        return ""
    match = _SEMVER_TAG_RE.match(raw)
    return match.group(1) if match else raw


def write_version_file(ahrena_dir: Path, version: str, dry_run: bool = False) -> None:
    """Persist `.ahrena/.version` with a single-line SemVer string + final newline.

    No-op when `version` is blank — the kata-ahrena-version fallback chain handles
    the absent-file case gracefully.
    """
    if not version:
        return
    target = ahrena_dir / ".version"
    if dry_run:
        print(f"  [DRY-RUN] Would write {target} containing '{version}'")
        return
    ahrena_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(f"{version}\n", encoding="utf-8")
    print(f"  Wrote {target} ({version})")

# Pilar names (prefixes) for detection and clean; transposition comes from platforms.yaml.
PILAR_NAMES: tuple[str, ...] = ("lex", "codex", "kata", "warrior", "cry")

PILAR_FOLDER_NAME: dict[str, str] = {
    "lex": "lexis",
    "codex": "codex",
    "kata": "katas",
    "warrior": "warriors",
    "cry": "cries",
}

PILAR_GENERATES_AGENT: set[str] = {"warrior"}

SECTIONS_TO_REMOVE: dict[str, set[str]] = {
    "lex": {
        "purpose", "scope", "consequences of violation",
        "propósito", "abrangência", "consequências de violação",
    },
    "codex": {
        "overview", "context", "glossary", "update flow", "folder structure",
        "visão geral", "contexto", "glossário",
    },
    "kata": {
        "objective", "when to use", "inputs",
        "objetivo", "quando usar",
    },
    "warrior": {
        "mission", "consultation", "example interaction",
        "missão", "consulta", "exemplo de interação",
    },
    "cry": {
        "description", "translation order", "invocation examples",
        "cry vs kata",
        "descrição", "exemplo de invocação", "diferença de kata",
    },
}

ALWAYS_REMOVE: set[str] = {"references", "referências"}

SAMPLE_DESCRIPTIONS: dict[str, str] = {
    "lex": (
        "Template de Lexis (lei inquebável). Use como referência para "
        "criar novas regras absolutas que governam segurança, qualidade e processo."
    ),
    "codex": (
        "Template de Codex (manual de referência). Use como referência para "
        "criar novas bases de conhecimento que orientam decisões da IA."
    ),
    "kata": (
        "Template de Kata (skill repetível). Use como referência para "
        "criar novos procedimentos padronizados que agentes de IA executam de forma recorrente."
    ),
    "warrior": (
        "Template de Warrior (agente especializado). Use como referência para "
        "criar novos agentes de IA com identidade, escopo e responsabilidades definidos."
    ),
    "cry": (
        "Template de Cry (comando recorrente). Use como referência para "
        "criar novos atalhos de produtividade invocáveis via /comando no chat."
    ),
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Directives parser
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_directives(content: str) -> dict:
    """Parse the simple YAML-like .directives format (stdlib only, no PyYAML).

    Each stack frame is (container, indent, parent_dict, key_in_parent). The
    last two fields let us retroactively swap a placeholder empty dict for a
    list when we discover ``- item`` lines under a key whose value was bare
    (e.g. ``mcp:\\n  servers:\\n    - ahrena``).
    """
    result: dict = {}
    stack: list[tuple[object, int, dict | None, str | None]] = [
        (result, -1, None, None),
    ]

    for raw in content.splitlines():
        stripped = raw.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(stripped)

        # Pop frames whose indent is at or beyond the current line's.
        while len(stack) > 1 and stack[-1][1] >= indent:
            stack.pop()

        if stripped.startswith("- "):
            value = stripped[2:].strip().strip('"').strip("'")
            container, cur_indent, parent_dict, key_in_parent = stack[-1]
            if (
                isinstance(container, dict)
                and not container
                and parent_dict is not None
                and key_in_parent is not None
            ):
                # Placeholder empty dict was actually a list.
                parent_dict[key_in_parent] = []
                stack[-1] = (parent_dict[key_in_parent], cur_indent, parent_dict, key_in_parent)
                container = parent_dict[key_in_parent]
            if isinstance(container, list):
                container.append(value)
            continue

        if ":" not in stripped:
            continue

        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")

        parent_obj, _, _, _ = stack[-1]
        if not isinstance(parent_obj, dict):
            continue  # malformed (list scope); skip silently

        if val:
            parent_obj[key] = val
        else:
            parent_obj[key] = {}
            stack.append((parent_obj[key], indent, parent_obj, key))

    return result


def get_directive(directives: dict, *keys: str, default: object = None) -> object:
    """Retrieve a nested value from parsed directives."""
    current: object = directives
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def _parse_platforms_yaml(content: str) -> dict:
    """Parse platforms.yaml. Uses pyyaml when available; falls back to stdlib parser.

    The custom parser supports a narrow YAML subset (see `codex-platforms` §"YAML
    subset"). If pyyaml is installed, it is preferred for correctness.
    """
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(content)
        return data if isinstance(data, dict) else {}
    except ImportError:
        pass  # fall through to stdlib parser

    result: dict = {}
    stack: list[tuple[dict, str | None, int]] = [(result, None, -1)]

    for line in content.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)

        # Find key and value (value may be quoted string with colons)
        if ":" not in stripped:
            continue
        first_colon = stripped.index(":")
        key = stripped[:first_colon].strip().rstrip(":")
        rest = stripped[first_colon + 1 :].strip()

        # Pop stack until we are at the right indent
        while len(stack) > 1 and stack[-1][2] >= indent:
            stack.pop()

        parent, _, _ = stack[-1]

        if rest:
            # Value on same line
            if rest.startswith('"') and rest.endswith('"') and len(rest) >= 2:
                val = rest[1:-1].replace('\\"', '"')
            elif rest.startswith("'") and rest.endswith("'") and len(rest) >= 2:
                val = rest[1:-1].replace("\\'", "'")
            elif rest.lower() == "true":
                val = True
            elif rest.lower() == "false":
                val = False
            else:
                val = rest
            parent[key] = val
        else:
            # Nested block
            child: dict = {}
            parent[key] = child
            stack.append((child, key, indent))

    return result


def load_platforms_config(ahrena_dir: Path) -> dict:
    """Load and merge platforms.yaml from framework (default) and .ahrena (override)."""
    default_path = ahrena_dir / "framework" / "platforms.yaml"
    override_path = ahrena_dir / "platforms.yaml"
    config: dict = {}

    for path in (default_path, override_path):
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            data = _parse_platforms_yaml(content)
            if not data:
                continue
            for platform, platform_data in data.items():
                if not isinstance(platform_data, dict):
                    continue
                config.setdefault(platform, {})
                for key, value in platform_data.items():
                    if key in ("rules", "docs") and isinstance(value, dict):
                        existing = config[platform].get(key)
                        if isinstance(existing, dict):
                            config[platform][key] = {**existing, **value}
                        else:
                            config[platform][key] = dict(value)
                    else:
                        config[platform][key] = value
        except (OSError, TypeError) as e:
            if path == default_path:
                pass  # ignore missing or invalid default
            else:
                print(f"  WARNING: Could not load {path}: {e}", file=sys.stderr)

    return config


def load_mcp_server_config(ahrena_dir: Path, server_name: str) -> dict | None:
    """Load JSON config for a named MCP server.

    Checks .ahrena/mcp/<name>.json first (user override), then
    framework/mcp/<name>.json (framework default).
    Returns the raw dict or None if not found.
    """
    import json
    for base in (ahrena_dir, ahrena_dir / "framework"):
        path = base / "mcp" / f"{server_name}.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
    return None


def _is_pipx_ahrena_mcp_installed(pipx_path: str) -> bool:
    """Return True if `ahrena-mcp` shows up in `pipx list --short`."""
    import subprocess
    try:
        proc = subprocess.run(
            [pipx_path, "list", "--short"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if proc.returncode != 0:
        return False
    for line in (proc.stdout or "").splitlines():
        if line.strip().startswith("ahrena-mcp"):
            return True
    return False


def install_mcp_package(ahrena_dir: Path, dry_run: bool = False) -> None:
    """Install the ahrena-mcp Python package via pipx so `ahrena-mcp` is on PATH.

    Reads `mcp.servers` from .ahrena/.directives. Skips silently when
    `ahrena` is not listed. Uses `.ahrena/tools/ahrena-mcp/` as the
    source for `pipx install -e`. When pipx is missing, prints a
    WARNING with install instructions and skips (non-fatal). When the
    package is already installed via pipx, this is a no-op on first
    install and a prompt on subsequent runs (default-no, preserve).
    """
    import subprocess

    directives_path = ahrena_dir / ".directives"
    if not directives_path.exists():
        return
    directives = parse_directives(directives_path.read_text(encoding="utf-8"))
    servers = get_directive(directives, "mcp", "servers", default=[])
    if not isinstance(servers, list) or "ahrena" not in servers:
        return  # not requested

    pipx = shutil.which("pipx")
    if not pipx:
        print(
            "  WARNING: `pipx` not found on PATH; ahrena-mcp not installed.\n"
            "    Install pipx (https://pipx.pypa.io/stable/installation/)\n"
            "    and re-run install.py to activate the Ahrena MCP server.",
            file=sys.stderr,
        )
        return

    pkg_path = ahrena_dir / "tools" / "ahrena-mcp"
    if not pkg_path.is_dir():
        print(
            f"  WARNING: {pkg_path} not found; cannot install ahrena-mcp.",
            file=sys.stderr,
        )
        return

    already_installed = _is_pipx_ahrena_mcp_installed(pipx)

    if already_installed and sys.stdin.isatty():
        try:
            ans = input(
                "  ahrena-mcp already installed via pipx. Reinstall/upgrade? [y/N]: "
            ).strip().lower()
        except EOFError:
            ans = ""
        if ans not in ("y", "yes"):
            print("  Skipping reinstall (existing pipx install preserved).")
            return
    elif already_installed:
        # Non-interactive: preserve existing install, do nothing.
        return

    if dry_run:
        action = "reinstall" if already_installed else "install"
        print(f"  [DRY-RUN] pipx {action} -e {pkg_path}")
        return

    cmd = [pipx, "install", "--force", "-e", str(pkg_path)]
    print("  Installing ahrena-mcp via pipx ...")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"  ERROR: pipx invocation failed: {exc}", file=sys.stderr)
        return
    if proc.returncode != 0:
        print(
            f"  ERROR: pipx install failed (exit {proc.returncode}):\n"
            f"    stdout: {(proc.stdout or '').strip()}\n"
            f"    stderr: {(proc.stderr or '').strip()}",
            file=sys.stderr,
        )
        return
    print("  Installed: ahrena-mcp on PATH (managed by pipx)")


def install_mcp(ahrena_dir: Path, target_dir: Path, directives: dict, dry_run: bool = False) -> None:
    """Merge MCP server configs into platform-specific files.

    Reads mcp.servers list from directives. For each server, loads the
    platform-specific block from framework/mcp/<name>.json (or the user
    override in .ahrena/mcp/<name>.json) and merges it additively.

    Cursor:      .cursor/mcp.json        → {"mcpServers": {...}}
    Claude Code: .mcp.json (project root) → {"mcpServers": {...}}
                 .claude/settings.json    → {"enabledMcpjsonServers": [...]}

    Note for Claude Code: the project-level Claude Code schema rejects
    a top-level `mcpServers` field in `.claude/settings.json`. Servers
    must be declared in `.mcp.json` at the project root, then approved
    via `enabledMcpjsonServers` in settings.json. This function writes
    both.

    Merge is additive — existing entries for other servers are preserved.
    Only the keys listed in mcp.servers are written/overwritten.
    """
    import json

    servers = get_directive(directives, "mcp", "servers", default=[])
    if not servers or not isinstance(servers, list):
        return  # mcp section absent or empty

    cursor_mcp: dict = {}
    claude_mcp: dict = {}

    for server_name in servers:
        raw = load_mcp_server_config(ahrena_dir, server_name)
        if raw is None:
            print(f"  WARNING: No MCP config found for server '{server_name}' — skipping", file=sys.stderr)
            continue
        cursor_block = raw.get("cursor")
        claude_block = raw.get("claude-code")
        # `requires` is Ahrena-internal metadata used by mcp_enable.py to install
        # local dependencies before activating the server; it is NOT part of the
        # MCP server spec and MUST NOT leak into the platform config files.
        ahrena_meta_keys = {"requires"}
        if cursor_block and isinstance(cursor_block, dict):
            cursor_mcp[server_name] = {k: v for k, v in cursor_block.items() if k not in ahrena_meta_keys}
        if claude_block and isinstance(claude_block, dict):
            claude_mcp[server_name] = {k: v for k, v in claude_block.items() if k not in ahrena_meta_keys}

    if dry_run:
        if cursor_mcp:
            print(f"    [DRY-RUN] .cursor/mcp.json ({', '.join(cursor_mcp)})")
        if claude_mcp:
            print(f"    [DRY-RUN] .mcp.json ({', '.join(claude_mcp)})")
            print(f"    [DRY-RUN] .claude/settings.json enabledMcpjsonServers ({', '.join(claude_mcp)})")
        return

    # ── Cursor: .cursor/mcp.json ──────────────────────────────────
    if cursor_mcp:
        cursor_dir = target_dir / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        mcp_path = cursor_dir / "mcp.json"
        existing: dict = {}
        if mcp_path.exists():
            try:
                existing = json.loads(mcp_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = {}
        existing.setdefault("mcpServers", {})
        existing["mcpServers"].update(cursor_mcp)
        mcp_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  Updated .cursor/mcp.json ({', '.join(cursor_mcp)})")

    # ── Claude Code: .mcp.json (project root) + settings approval ─
    if claude_mcp:
        # 1. Declare servers in the project-level .mcp.json
        mcpjson_path = target_dir / ".mcp.json"
        existing_mj: dict = {}
        if mcpjson_path.exists():
            try:
                existing_mj = json.loads(mcpjson_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing_mj = {}
        existing_mj.setdefault("mcpServers", {})
        existing_mj["mcpServers"].update(claude_mcp)
        mcpjson_path.write_text(
            json.dumps(existing_mj, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  Updated .mcp.json ({', '.join(claude_mcp)})")

        # 2. Pre-approve in .claude/settings.json via enabledMcpjsonServers
        claude_dir = target_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        settings_path = claude_dir / "settings.json"
        existing_s: dict = {}
        if settings_path.exists():
            try:
                existing_s = json.loads(settings_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing_s = {}
        enabled = existing_s.get("enabledMcpjsonServers", [])
        if isinstance(enabled, bool) and enabled is True:
            # Some Claude Code schemas accept a literal `true` meaning "enable
            # all servers from .mcp.json". Preserving that intent — do not
            # rewrite to a list, since that would silently scope-down the
            # user's choice. The new servers are already covered by `true`.
            print(
                "  NOTE: enabledMcpjsonServers is `true` (enable-all); "
                "leaving as-is (already covers new servers).",
                file=sys.stderr,
            )
        else:
            if not isinstance(enabled, list):
                print(
                    f"  WARNING: enabledMcpjsonServers had unexpected type "
                    f"{type(enabled).__name__!r}; coercing to list.",
                    file=sys.stderr,
                )
                enabled = []
            for name in claude_mcp:
                if name not in enabled:
                    enabled.append(name)
            existing_s["enabledMcpjsonServers"] = enabled
        settings_path.write_text(
            json.dumps(existing_s, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  Updated .claude/settings.json enabledMcpjsonServers ({', '.join(claude_mcp)})")


def install_pr_cost_attribution_hook(
    ahrena_dir: Path,
    target_dir: Path,
    directives: dict,
    dry_run: bool = False,
) -> None:
    """Wire pr-cost-attribution.sh into project .claude/settings.json hooks.

    Activated when:
      pr_cost_tracking.enabled == true
      AND pr_cost_tracking.attribution_mode == "hook"  (default when omitted)

    Side effects:
      1. Copies framework/templates/claude-code-hooks/pr-cost-attribution.sh
         to <target>/.claude/hooks/pr-cost-attribution.sh (chmod +x).
      2. Adds hook entries to <target>/.claude/settings.json under
         `hooks.UserPromptSubmit` and `hooks.SessionStart`. Existing entries
         from other tooling are preserved; idempotent re-runs do not duplicate.
    """
    import json

    enabled = bool(get_directive(directives, "pr_cost_tracking", "enabled", default=False))
    if not enabled:
        return

    mode = str(
        get_directive(directives, "pr_cost_tracking", "attribution_mode", default="hook")
    ).strip().lower()
    if mode != "hook":
        return  # legacy "project" mode does not require the hook

    src_hook = ahrena_dir / "framework" / "templates" / "claude-code-hooks" / "pr-cost-attribution.sh"
    if not src_hook.exists():
        print(
            f"  WARNING: pr-cost-attribution.sh not found at {src_hook} — skipping hook install",
            file=sys.stderr,
        )
        return

    claude_dir = target_dir / ".claude"
    hooks_dir = claude_dir / "hooks"
    hook_dst = hooks_dir / "pr-cost-attribution.sh"
    settings_path = claude_dir / "settings.json"

    # The command we wire into settings.json. Using $CLAUDE_PROJECT_DIR keeps
    # the path portable across machines (Claude Code expands it at runtime).
    hook_cmd = "$CLAUDE_PROJECT_DIR/.claude/hooks/pr-cost-attribution.sh"

    if dry_run:
        print(f"    [DRY-RUN] .claude/hooks/pr-cost-attribution.sh (copy from framework template)")
        print(f"    [DRY-RUN] .claude/settings.json (wire UserPromptSubmit + SessionStart)")
        return

    # ── 1. Copy hook script ──
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_dst.write_text(src_hook.read_text(encoding="utf-8"), encoding="utf-8")
    hook_dst.chmod(0o755)

    # ── 2. Merge hooks block into settings.json ──
    existing: dict = {}
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}

    hooks_block = existing.get("hooks")
    if not isinstance(hooks_block, dict):
        hooks_block = {}

    def _merge_event(event_name: str, matcher: str) -> None:
        groups = hooks_block.get(event_name)
        if not isinstance(groups, list):
            groups = []
        # Idempotency: drop any existing matcher-group whose hooks include our
        # command, then append a single canonical entry.
        cleaned: list = []
        for g in groups:
            if not isinstance(g, dict):
                cleaned.append(g)
                continue
            inner = g.get("hooks")
            if not isinstance(inner, list):
                cleaned.append(g)
                continue
            ours = any(
                isinstance(h, dict)
                and h.get("type") == "command"
                and isinstance(h.get("command"), str)
                and "pr-cost-attribution.sh" in h["command"]
                for h in inner
            )
            if not ours:
                cleaned.append(g)
        cleaned.append(
            {
                "matcher": matcher,
                "hooks": [{"type": "command", "command": hook_cmd}],
            }
        )
        hooks_block[event_name] = cleaned

    _merge_event("UserPromptSubmit", "")
    _merge_event("SessionStart", "startup")
    existing["hooks"] = hooks_block

    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("  Wired PR cost attribution hook (UserPromptSubmit, SessionStart) into .claude/settings.json")


# Canonical RTK PreToolUse command per Decision 4 of Plan #214.
# Strict fallback semantics: when `rtk` is absent from PATH the hook exits 0
# with empty stdout so Claude Code proceeds with the original tool input;
# when `rtk` is present runtime failures propagate normally (no silent mask).
RTK_HOOK_COMMAND = "if command -v rtk >/dev/null 2>&1; then rtk hook claude; fi"


def _install_rtk_binary(dry_run: bool = False) -> bool:
    """Detect or install the rtk binary; return True if available afterward.

    Platform support:
      Linux/macOS : curl install script (or Homebrew on macOS)
      Windows     : WSL > bash (Git Bash) > cargo; falls back to manual notice

    Idempotent: returns immediately when `rtk` is already on PATH.
    """
    _INSTALL_URL = "https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh"
    _REPO_URL = "https://github.com/rtk-ai/rtk"

    if shutil.which("rtk"):
        print("  RTK binary already installed.")
        return True

    if sys.platform.startswith("win"):
        _os = "windows"
    elif sys.platform == "darwin":
        _os = "macos"
    else:
        _os = "linux"

    if dry_run:
        print(f"  [DRY-RUN] Would install rtk binary on {_os}")
        return False

    print(f"  Installing rtk binary ({_os})...")
    try:
        if _os == "macos":
            brew = shutil.which("brew")
            via_brew = False
            if brew:
                result = subprocess.run([brew, "install", "rtk"], check=False)
                via_brew = result.returncode == 0
            if not via_brew:
                subprocess.run(
                    ["bash", "-c", f"curl -fsSL {_INSTALL_URL} | sh"],
                    check=True,
                )
        elif _os == "linux":
            subprocess.run(
                ["bash", "-c", f"curl -fsSL {_INSTALL_URL} | sh"],
                check=True,
            )
        else:  # windows
            installed = False
            for shell in (shutil.which("wsl"), shutil.which("bash")):
                if shell:
                    result = subprocess.run(
                        [shell, "-c", f"curl -fsSL {_INSTALL_URL} | sh"],
                        check=False,
                    )
                    installed = result.returncode == 0
                    if installed:
                        break
            if not installed:
                cargo = shutil.which("cargo")
                if cargo:
                    subprocess.run(
                        [cargo, "install", "--git", _REPO_URL],
                        check=True,
                    )
                else:
                    print("  rtk: automatic install unavailable on native Windows without bash/cargo.")
                    print("  Options:")
                    print(f"    WSL (recommended) : wsl bash -c \"curl -fsSL {_INSTALL_URL} | sh\"")
                    print(f"    Cargo             : cargo install --git {_REPO_URL}")
                    print(f"    Binary download   : {_REPO_URL}/releases")
                    return False
    except (subprocess.CalledProcessError, OSError, FileNotFoundError) as exc:
        print(f"  WARNING: rtk binary install failed ({exc}). Hook will no-op until installed.")
        return False

    return shutil.which("rtk") is not None


def install_rtk_bundle(
    ahrena_dir: Path,
    target_dir: Path,
    directives: dict,
    dry_run: bool = False,
) -> None:
    """Bundle RTK (Rust Token Killer) into the target Claude Code project.

    Activated when:
      rtk.enabled is true (default true when the section is omitted)

    Side effects (when enabled):
      1. Detects or installs the rtk binary (brew/curl/cargo, OS-aware).
      2. Adds a single canonical PreToolUse entry to settings.json.hooks with
         matcher "Bash" and the strict-fallback command (RTK_HOOK_COMMAND).
         Existing PreToolUse entries whose command contains "rtk hook claude"
         (legacy bare form or non-canonical matcher) are collapsed to the
         canonical shape. Other PreToolUse entries are preserved.
      3. Copies framework/templates/.rtk/filters.toml to <target>/.rtk/filters.toml
         only when the destination is absent (never overwrites user filters).

    Idempotent on every install/update run; no-op when rtk.enabled is false.
    """
    import json

    # parse_directives is stdlib-only and returns scalars as strings (e.g. "false"),
    # so `bool("false")` would incorrectly be truthy. Coerce strings to real bools
    # before gating on the directive.
    raw_enabled = get_directive(directives, "rtk", "enabled", default=True)
    if isinstance(raw_enabled, str):
        enabled = raw_enabled.strip().lower() not in ("false", "no", "0", "off")
    else:
        enabled = bool(raw_enabled)
    if not enabled:
        return

    raw_auto_install = get_directive(directives, "rtk", "auto_install_binary", default=True)
    if isinstance(raw_auto_install, str):
        auto_install = raw_auto_install.strip().lower() not in ("false", "no", "0", "off")
    else:
        auto_install = bool(raw_auto_install)

    # 1. Ensure rtk binary is present (best-effort; hook stays safe if absent)
    if auto_install:
        _install_rtk_binary(dry_run=dry_run)

    claude_dir = target_dir / ".claude"
    settings_path = claude_dir / "settings.json"
    rtk_dir = target_dir / ".rtk"
    filters_dst = rtk_dir / "filters.toml"
    filters_src = ahrena_dir / "framework" / "templates" / ".rtk" / "filters.toml"

    if dry_run:
        print("    [DRY-RUN] .claude/settings.json (wire RTK PreToolUse hook)")
        if filters_src.exists() and not filters_dst.exists():
            print("    [DRY-RUN] .rtk/filters.toml (copy from framework template)")
        return

    # 2. Merge canonical PreToolUse entry into settings.json
    existing: dict = {}
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}

    hooks_block = existing.get("hooks")
    if not isinstance(hooks_block, dict):
        hooks_block = {}

    groups = hooks_block.get("PreToolUse")
    if not isinstance(groups, list):
        groups = []

    # Idempotency: drop any existing matcher-group whose hooks reference our
    # command (legacy bare or canonical wrapped), then append the canonical
    # entry. Other PreToolUse entries (unrelated tools) are preserved.
    cleaned: list = []
    for g in groups:
        if not isinstance(g, dict):
            cleaned.append(g)
            continue
        inner = g.get("hooks")
        if not isinstance(inner, list):
            cleaned.append(g)
            continue
        ours = any(
            isinstance(h, dict)
            and h.get("type") == "command"
            and isinstance(h.get("command"), str)
            and "rtk hook claude" in h["command"]
            for h in inner
        )
        if not ours:
            cleaned.append(g)

    cleaned.append({
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": RTK_HOOK_COMMAND}],
    })
    hooks_block["PreToolUse"] = cleaned
    existing["hooks"] = hooks_block

    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("  Wired RTK PreToolUse hook (matcher Bash, strict fallback) into .claude/settings.json")

    # 3. Copy filters template if absent at destination
    if filters_src.exists() and not filters_dst.exists():
        rtk_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(filters_src, filters_dst)
        print("  Created .rtk/filters.toml from framework template")

    # 4. Final hint when binary install was best-effort and did not succeed
    if shutil.which("rtk") is None:
        print(
            "  WARNING: rtk binary still not on PATH. Hook is wired with strict "
            "fallback (no-op when binary is absent). Install manually to enable "
            "token-savings rewriting: https://github.com/rtk-ai/rtk"
        )


def _framework_rel_path_to_rule_key(rel_path: Path) -> str:
    """Convert framework-relative path (e.g. en/_foundation/process/lexis/lex-directives.md) to rule key."""
    parts = list(rel_path.parts)
    if not parts or not rel_path.suffix == ".md":
        return ""
    # Drop first segment (language)
    if len(parts) > 1:
        parts = parts[1:]
    return str(Path(*parts).with_suffix("")).replace("\\", "/")


def parse_clades(value: str | None) -> list[str] | None:
    """Parse a comma-separated clades string into a sorted list, or None for all."""
    if not value:
        return None
    clades = [c.strip() for c in value.split(",") if c.strip()]
    return sorted(clades) if clades else None


def parse_languages(value: str | None) -> list[str] | None:
    """Parse a comma-separated languages string into a list, or None for all."""
    if not value:
        return None
    KNOWN = {"pt-BR", "en", "es"}
    langs = [l.strip() for l in value.split(",") if l.strip()]
    unknown = set(langs) - KNOWN
    if unknown:
        print(f"WARNING: unknown language(s) in --languages: {', '.join(sorted(unknown))}; "
              f"known: {', '.join(sorted(KNOWN))}", file=sys.stderr)
    filtered = [l for l in langs if l in KNOWN]
    return filtered if filtered else None


def override_language_default(content: str, language: str) -> str:
    """Replace language.default value in raw directives text."""
    lines = content.splitlines()
    in_language = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("language:"):
            in_language = True
        elif in_language and stripped.startswith("default:"):
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + f"default: {language}"
            break
        elif in_language and stripped and not stripped.startswith("#") \
                and not stripped.startswith("-") and not line[0:1] == " ":
            break
    return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GitHub downloader
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def download_and_extract(repo_url: str, version: str) -> Path:
    """Download a zipball from GitHub and extract to a temp directory."""
    parts = repo_url.rstrip("/").split("/")
    owner_repo = f"{parts[-2]}/{parts[-1]}"

    urls = [
        f"https://github.com/{owner_repo}/archive/refs/tags/{version}.zip",
        f"https://github.com/{owner_repo}/archive/refs/heads/{version}.zip",
    ]

    data: bytes | None = None
    for url in urls:
        try:
            print(f"  Trying {url} ...")
            req = urllib.request.Request(url, headers={"User-Agent": "ahrena-installer"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            print(f"  Downloaded ({len(data)} bytes)")
            break
        except urllib.error.HTTPError:
            continue
        except urllib.error.URLError as exc:
            print(f"  Network error: {exc.reason}")
            continue

    if data is None:
        print(f"\nERROR: Could not download version '{version}' from {repo_url}")
        print("Check your network connection and verify the version/tag exists.")
        sys.exit(1)

    temp_dir = Path(tempfile.mkdtemp(prefix="ahrena-"))
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(temp_dir)

    extracted = list(temp_dir.iterdir())
    if len(extracted) == 1 and extracted[0].is_dir():
        return extracted[0]
    return temp_dir


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Markdown → Cursor transformer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_pilar(filename: str) -> str | None:
    """Detect the pilar type from a filename's prefix."""
    for prefix in PILAR_NAMES:
        if filename.startswith(f"{prefix}-"):
            return prefix
    return None


def extract_description(content: str) -> str:
    """Build a description from the H1 title and the scope in the blockquote."""
    title = ""
    scope = ""

    for line in content.splitlines():
        if not title and line.startswith("# ") and not line.startswith("## "):
            raw = line.lstrip("# ").strip()
            if ": " in raw:
                raw = raw.split(": ", 1)[1]
            title = raw

        elif line.startswith("> ") and "|" in line and not scope:
            text = line[2:].strip()
            text = re.sub(r"\*\*", "", text)
            text = re.sub(r"`([^`]*)`", r"\1", text)
            for part in text.split("|"):
                part = part.strip()
                lower = part.lower()
                if lower.startswith("scope:") or lower.startswith("escopo:"):
                    scope = part.split(":", 1)[1].strip()
                    break

    if title and scope:
        return f"{title}. {scope}"
    return title or scope or "Ahrena framework artifact"


def build_frontmatter(
    pilar: str,
    filename: str,
    description: str,
    is_sample: bool = False,
    resource: str | None = None,
    rule_config: dict | None = None,
) -> str:
    """Generate the YAML frontmatter block for a Cursor .mdc file.

    Frontmatter varies by Cursor resource type:
      - rules  (lex/codex):  description + alwaysApply [+ globs]
      - skills (kata/warrior): name + description
      - commands (cry):        description only

    When rule_config is provided for rules, uses alwaysApply/globs/description from it;
    default for unlisted rules: alwaysApply false, description from content.
    """
    if resource is None:
        raise ValueError(f"resource is required for Cursor frontmatter (pilar={pilar}); define cursor.transposition in framework/platforms.yaml")
    desc = rule_config.get("description", description) if rule_config else description
    safe_desc = (desc or description).replace('"', '\\"')
    lines = ["---"]

    if resource == "rules":
        lines.append(f'description: "{safe_desc}"')
        if is_sample:
            lines.append("globs: ")
            lines.append("alwaysApply: false")
        else:
            if rule_config is not None and "alwaysApply" in rule_config:
                always_apply = bool(rule_config["alwaysApply"])
            else:
                always_apply = False
            lines.append(f"alwaysApply: {str(always_apply).lower()}")
            if rule_config and rule_config.get("globs"):
                globs = rule_config["globs"]
                if isinstance(globs, list):
                    lines.append("globs:")
                    for g in globs:
                        lines.append(f"  - {g!r}" if " " in str(g) else f"  - {g}")
                else:
                    lines.append(f"globs: {globs!r}")
    elif resource == "skills":
        name = Path(filename).stem
        lines.append(f"name: {name}")
        lines.append(f'description: "{safe_desc}"')
    elif resource == "commands":
        lines.append(f'description: "{safe_desc}"')

    lines.append("---")
    return "\n".join(lines)


def filter_sections(content: str, pilar: str) -> str:
    """Remove non-essential H2 sections from markdown content."""
    removable = SECTIONS_TO_REMOVE.get(pilar, set()) | ALWAYS_REMOVE

    lines = content.splitlines()
    result: list[str] = []
    skipping = False

    for line in lines:
        h2_match = re.match(r"^##(?!#)\s+(.+)$", line)
        if h2_match:
            section_title = h2_match.group(1).strip().lower()
            if section_title in removable:
                skipping = True
                continue
            else:
                skipping = False

        if not skipping:
            result.append(line)

    cleaned: list[str] = []
    prev_blank = False
    for line in result:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank

    text = "\n".join(cleaned)
    return text.strip() + "\n"


def transform_md_to_mdc(
    content: str,
    pilar: str,
    filename: str,
    is_sample: bool = False,
    resource: str | None = None,
    rule_config: dict | None = None,
) -> str:
    """Transform a framework .md file into a Cursor .mdc file."""
    if is_sample:
        description = SAMPLE_DESCRIPTIONS.get(pilar, extract_description(content))
        body = content
    else:
        description = extract_description(content)
        body = filter_sections(content, pilar)
    if resource is None:
        raise ValueError(f"resource is required for transform (pilar={pilar}); define cursor.transposition in framework/platforms.yaml")
    frontmatter = build_frontmatter(
        pilar, filename, description, is_sample, resource=resource, rule_config=rule_config
    )
    return frontmatter + "\n\n" + body


def transform_md_to_agent(content: str, pilar: str, filename: str) -> str:
    """Transform a framework warrior .md into a Cursor agent .md file.

    Agents use plain .md with name + description frontmatter.
    The body becomes the agent's system prompt.
    """
    description = extract_description(content)
    body = filter_sections(content, pilar)
    safe_desc = description.replace('"', '\\"')
    name = Path(filename).stem
    frontmatter = f'---\nname: {name}\ndescription: "{safe_desc}"\n---'
    return frontmatter + "\n\n" + body


def build_cursor_path(framework_rel_path: Path, pilar: str, resource: str | None = None) -> Path:
    """
    Map a framework-relative path to a .cursor/ path.

    Each Cursor resource type has its own native format:
      rules:    .cursor/rules/{clade}/{subclade}/{file}.mdc
      skills:   .cursor/skills/{skill-name}/SKILL.md
      agents:   .cursor/agents/{name}.md
      commands: .cursor/commands/{clade}/{subclade}/{file}.md

    When resource is None, raises ValueError (cursor.transposition must be defined in platforms.yaml).
    """
    if resource is None:
        raise ValueError(f"resource is required for Cursor path (pilar={pilar}); define cursor.transposition in framework/platforms.yaml")
    parts = list(framework_rel_path.parts)
    if len(parts) > 1:
        parts = parts[1:]  # drop language segment
    pilar_folder = PILAR_FOLDER_NAME.get(pilar, "")
    parts_no_pilar = [p for p in parts if p != pilar_folder]

    if resource == "agents":
        stem = Path(framework_rel_path).stem
        return Path(".cursor") / "agents" / f"{stem}.md"
    if resource == "skills":
        skill_name = Path(parts_no_pilar[-1]).stem
        return Path(".cursor") / "skills" / skill_name / "SKILL.md"
    if resource == "commands":
        return Path(".cursor") / "commands" / Path(*parts_no_pilar)
    parts_no_pilar[-1] = re.sub(r"\.md$", ".mdc", parts_no_pilar[-1])
    return Path(".cursor") / "rules" / Path(*parts_no_pilar)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Markdown → Claude Code transformer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AHRENA_MARKER_START = "<!-- AHRENA:START -->"
AHRENA_MARKER_END = "<!-- AHRENA:END -->"


def transform_md_to_claude_rule(content: str, pilar: str, rule_config: dict | None = None) -> str:
    """Transform a framework lex .md into a Claude Code rule .md.

    Generates a frontmatter block with optional paths: list (for file-scoped rules).
    Rules without paths apply to every session (equivalent to CLAUDE.md injection).
    """
    import ast as _ast
    body = filter_sections(content, pilar)
    paths = rule_config.get("paths") if rule_config else None
    if paths:
        if isinstance(paths, str):
            try:
                paths = _ast.literal_eval(paths)
            except (ValueError, SyntaxError):
                paths = [paths]
        lines = ["---"]
        if isinstance(paths, list):
            lines.append("paths:")
            for p in paths:
                lines.append(f"  - {p!r}")
        else:
            lines.append(f"paths: {paths!r}")
        lines.append("---")
        return "\n".join(lines) + "\n\n" + body
    return body


def transform_md_to_claude_doc(content: str, pilar: str) -> str:
    """Transform a framework codex .md into a plain Claude Code doc .md.

    Claude Code docs are plain markdown — no frontmatter, no format conversion.
    Non-essential sections are filtered out to reduce token usage.
    """
    return filter_sections(content, pilar)


def transform_md_to_claude_command(content: str, pilar: str) -> str:
    """Transform a framework cry .md into a Claude Code command .md.

    Claude Code commands use plain markdown. The first line is the description,
    followed by a blank line and the filtered body.
    """
    description = extract_description(content)
    body = filter_sections(content, pilar)
    return description + "\n\n" + body


def transform_md_to_claude_skill(content: str, pilar: str, filename: str) -> str:
    """Transform a framework kata .md into a Claude Code SKILL.md.

    Claude Code skills use SKILL.md with instructions and metadata,
    following the same structure as Cursor skills.
    """
    description = extract_description(content)
    body = filter_sections(content, pilar)
    safe_desc = description.replace('"', '\\"')
    name = Path(filename).stem
    frontmatter = f'---\nname: {name}\ndescription: "{safe_desc}"\n---'
    return frontmatter + "\n\n" + body


def transform_md_to_claude_agent(content: str, pilar: str, filename: str) -> str:
    """Transform a framework warrior .md into a Claude Code agent .md.

    Claude Code agents use .md files with name + description frontmatter.
    The body becomes the agent's system prompt.
    """
    description = extract_description(content)
    body = filter_sections(content, pilar)
    safe_desc = description.replace('"', '\\"')
    name = Path(filename).stem
    frontmatter = f'---\nname: {name}\ndescription: "{safe_desc}"\n---'
    return frontmatter + "\n\n" + body


def build_claude_code_path(framework_rel_path: Path, pilar: str, resource: str | None = None) -> Path:
    """Map a framework-relative path to a .claude/ path.

    Each Claude Code resource type maps to:
      docs:     .claude/docs/{clade}/{subclade}/{file}.md
      skills:   .claude/skills/{skill-name}/SKILL.md
      agents:   .claude/agents/{name}.md
      commands: .claude/commands/{stem}.md  (flat namespace)

    When resource is None, raises ValueError.
    """
    if resource is None:
        raise ValueError(f"resource is required for Claude Code path (pilar={pilar}); define claude-code.transposition in framework/platforms.yaml")
    parts = list(framework_rel_path.parts)
    if len(parts) > 1:
        parts = parts[1:]  # drop language segment
    pilar_folder = PILAR_FOLDER_NAME.get(pilar, "")
    parts_no_pilar = [p for p in parts if p != pilar_folder]

    if resource == "agents":
        stem = Path(framework_rel_path).stem
        return Path(".claude") / "agents" / f"{stem}.md"
    if resource == "skills":
        skill_name = Path(parts_no_pilar[-1]).stem
        return Path(".claude") / "skills" / skill_name / "SKILL.md"
    if resource == "commands":
        stem = Path(framework_rel_path).stem
        return Path(".claude") / "commands" / f"{stem}.md"
    if resource == "rules":
        return Path(".claude") / "rules" / Path(*parts_no_pilar)
    # docs: preserve clade/subclade hierarchy
    return Path(".claude") / "docs" / Path(*parts_no_pilar)


def generate_claude_md(
    target_dir: Path,
    platforms_config: dict,
) -> None:
    """Generate CLAUDE.md at the project root with a reference index of Ahrena docs.

    Lexis are installed to .claude/rules/ and auto-injected by Claude Code natively
    (via paths: frontmatter or always-on when no paths are defined).
    Codex are installed to .claude/docs/ and listed here for @-reference by warriors/skills.
    """
    claude_docs_dir = target_dir / ".claude" / "docs"
    if not claude_docs_dir.exists():
        return

    reference_docs: list[str] = []
    for md_file in sorted(claude_docs_dir.rglob("*.md")):
        rel_path = md_file.relative_to(target_dir / ".claude" / "docs")
        reference_docs.append(str(rel_path))

    lines = [
        AHRENA_MARKER_START,
        "# Ahrena Framework",
        "",
        "> Auto-generated by Ahrena. Do not edit between AHRENA markers.",
        "",
    ]

    if reference_docs:
        lines.append("## Reference Docs")
        lines.append("")
        lines.append("Available in `.claude/docs/` — use `@` to import when needed:")
        lines.append("")
        for ref in reference_docs:
            lines.append(f"- `.claude/docs/{ref}`")
        lines.append("")

    lines.append(AHRENA_MARKER_END)

    claude_md_path = target_dir / "CLAUDE.md"

    # Preserve user content outside markers if CLAUDE.md already exists
    if claude_md_path.exists():
        existing = claude_md_path.read_text(encoding="utf-8")
        start_idx = existing.find(AHRENA_MARKER_START)
        end_idx = existing.find(AHRENA_MARKER_END)
        if start_idx != -1 and end_idx != -1:
            before = existing[:start_idx]
            after = existing[end_idx + len(AHRENA_MARKER_END):]
            new_content = before + "\n".join(lines) + after
        else:
            new_content = existing.rstrip() + "\n\n" + "\n".join(lines) + "\n"
    else:
        new_content = "\n".join(lines) + "\n"

    claude_md_path.write_text(new_content, encoding="utf-8")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Installation phases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def copy_framework(src: Path, dst: Path, clades: list[str] | None,
                   languages: list[str] | None = None) -> int:
    """Copy framework/ to destination, optionally filtering by clade and language.

    `languages` (e.g. `["en"]` or `["pt-BR", "en"]`) limits which language directories
    are copied; `None` copies all. Language directories are recognized by matching
    known language codes (pt-BR, en, es). Non-language files and directories
    (templates/, platforms.yaml, mcp/) are copied unconditionally.

    Returns the number of clades copied.
    """
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    KNOWN_LANGUAGES = {"pt-BR", "en", "es"}
    clade_count = 0

    for item in sorted(src.iterdir()):
        dst_item = dst / item.name
        if item.is_file():
            shutil.copy2(item, dst_item)
        elif item.name == "templates":
            shutil.copytree(item, dst_item)
        elif item.is_dir():
            # Language filtering: if item is a known language and `languages`
            # is set, skip unless in list.
            if item.name in KNOWN_LANGUAGES and languages is not None:
                if item.name not in languages:
                    continue
            if clades is None:
                shutil.copytree(item, dst_item)
                clade_count = max(clade_count,
                                  sum(1 for d in item.iterdir() if d.is_dir()))
            else:
                dst_item.mkdir(exist_ok=True)
                for sub in sorted(item.iterdir()):
                    if sub.is_file():
                        shutil.copy2(sub, dst_item / sub.name)
                    elif sub.is_dir() and sub.name in clades:
                        shutil.copytree(sub, dst_item / sub.name)
                        clade_count += 1

    return clade_count


def install_ahrena(source_dir: Path, target_dir: Path, args: argparse.Namespace) -> Path:
    """Phase 1: install .ahrena/ (framework + directives + tooling)."""
    framework_src = source_dir / "framework"
    ahrena_dir = target_dir / ".ahrena"
    ahrena_framework = ahrena_dir / "framework"

    if not framework_src.exists():
        print(f"\nERROR: 'framework/' not found in downloaded archive.")
        sys.exit(1)

    clades = parse_clades(getattr(args, "clades", None))
    languages = parse_languages(getattr(args, "languages", None))

    # 1. Copy framework/ (filtered by clades and/or languages if specified)
    filter_parts = []
    if clades:
        filter_parts.append(f"clades: {', '.join(clades)}")
    if languages:
        filter_parts.append(f"languages: {', '.join(languages)}")
    if filter_parts:
        print(f"  Copying framework ({'; '.join(filter_parts)}) to {ahrena_framework}/ ...")
    else:
        print(f"  Copying framework to {ahrena_framework}/ ...")

    ahrena_dir.mkdir(parents=True, exist_ok=True)
    copy_framework(framework_src, ahrena_framework, clades, languages)

    # Persist clade selection for future updates
    clades_file = ahrena_dir / ".installed-clades"
    if clades:
        clades_file.write_text("\n".join(clades) + "\n", encoding="utf-8")
    elif clades_file.exists():
        clades_file.unlink()

    # 2. Resolve and write .directives
    directives_path = ahrena_dir / ".directives"
    directives_content: str | None = None
    should_write = False

    if args.directives:
        if args.directives.startswith("http://") or args.directives.startswith("https://"):
            print(f"  Downloading directives from {args.directives} ...")
            req = urllib.request.Request(args.directives, headers={"User-Agent": "ahrena-installer"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                directives_content = resp.read().decode("utf-8")
        else:
            custom = Path(args.directives)
            if not custom.exists():
                print(f"\nERROR: Directives file not found: {custom}")
                sys.exit(1)
            print(f"  Loading directives from {custom} ...")
            directives_content = custom.read_text(encoding="utf-8")
        should_write = True

    elif args.language:
        sample = ahrena_framework / ".directives.sample"
        directives_content = sample.read_text(encoding="utf-8")
        should_write = True

    elif not directives_path.exists():
        sample = ahrena_framework / ".directives.sample"
        directives_content = sample.read_text(encoding="utf-8")
        should_write = True

    if args.language and directives_content:
        directives_content = override_language_default(directives_content, args.language)

    if should_write and directives_content:
        directives_path.write_text(directives_content, encoding="utf-8")
        print(f"  Installed .directives")
    else:
        print(f"  .directives already exists — preserved")

    # 2.5. Sync contributing_templates to .ahrena/contributing_templates/
    # (framework-managed: always refresh on install/update so new templates land
    # and existing ones track the framework version)
    ct_src = ahrena_framework / "templates" / "contributing_templates"
    ct_dst = ahrena_dir / "contributing_templates"
    if ct_src.exists():
        if ct_dst.exists():
            shutil.rmtree(ct_dst)
        shutil.copytree(ct_src, ct_dst)
        print(f"  Synced contributing_templates to .ahrena/contributing_templates/")

    # 2.5b. Sync GitHub Issue Templates to target/.github/ISSUE_TEMPLATE/
    # The .yml forms under source_dir/.github/ISSUE_TEMPLATE/ are the canonical
    # GitHub-rendered counterparts of the .md sources in contributing_templates.
    # Copy each file individually so user-authored templates (file names not in
    # the framework set) are preserved in the consumer repo.
    gh_tpl_src = source_dir / ".github" / "ISSUE_TEMPLATE"
    gh_tpl_dst = target_dir / ".github" / "ISSUE_TEMPLATE"
    if gh_tpl_src.exists():
        gh_tpl_dst.mkdir(parents=True, exist_ok=True)
        synced = 0
        for yml in sorted(gh_tpl_src.glob("*.yml")):
            dst = gh_tpl_dst / yml.name
            # Skip self-copy when source and target are the same path
            # (ahrena dev-install with target = repo root).
            if yml.resolve() == dst.resolve():
                continue
            shutil.copy2(yml, dst)
            synced += 1
        if synced:
            print(f"  Synced {synced} GitHub Issue Template(s) to .github/ISSUE_TEMPLATE/")

    # 2.6. Copy mcp/ templates to .ahrena/mcp/ (never overwrite user overrides)
    mcp_src = ahrena_framework / "mcp"
    mcp_dst = ahrena_dir / "mcp"
    if mcp_src.exists():
        mcp_dst.mkdir(exist_ok=True)
        for json_file in mcp_src.glob("*.json"):
            dst_file = mcp_dst / json_file.name
            if not dst_file.exists():
                shutil.copy2(json_file, dst_file)
        print(f"  Installed MCP templates to .ahrena/mcp/")

    # 2.7. Copy tools/ahrena-mcp/ source so pipx can install -e from .ahrena/
    pkg_src = source_dir / "tools" / "ahrena-mcp"
    pkg_dst = ahrena_dir / "tools" / "ahrena-mcp"
    if pkg_src.is_dir():
        pkg_dst.parent.mkdir(parents=True, exist_ok=True)
        if pkg_dst.exists():
            shutil.rmtree(pkg_dst)
        shutil.copytree(
            pkg_src,
            pkg_dst,
            ignore=shutil.ignore_patterns(
                ".venv", "dist", "build", "*.egg-info",
                "__pycache__", ".pytest_cache", ".mypy_cache", ".coverage",
            ),
        )
        print(f"  Installed ahrena-mcp source to .ahrena/tools/ahrena-mcp/")

    # 2.8. Install ahrena-mcp Python package via pipx so the
    # `ahrena-mcp` console script lands on PATH. Default-on per
    # mcp.servers in .directives; idempotent across re-runs.
    install_mcp_package(ahrena_dir, getattr(args, "dry_run", False))

    # 3. Copy scripts for future use (install, update, uninstall, preflight, mcp_enable)
    scripts_src = source_dir / "scripts"
    for script_name in ("install.py", "update.py", "uninstall.py", "preflight.py", "mcp_enable.py"):
        src = scripts_src / script_name
        if src.exists():
            shutil.copy2(src, ahrena_dir / script_name)
            print(f"  Installed {script_name} to .ahrena/")

    # 3.1. Copy bootstrap_labels.sh and ensure it is executable
    bootstrap_src = scripts_src / "bootstrap_labels.sh"
    if bootstrap_src.exists():
        bootstrap_dst = ahrena_dir / "bootstrap_labels.sh"
        shutil.copy2(bootstrap_src, bootstrap_dst)
        bootstrap_dst.chmod(bootstrap_dst.stat().st_mode | 0o111)
        print(f"  Installed bootstrap_labels.sh to .ahrena/")

    # 4. Copy Makefile for future use
    makefile_src = source_dir / "Makefile"
    if makefile_src.exists():
        makefile_dst = ahrena_dir / "Makefile"
        shutil.copy2(makefile_src, makefile_dst)
        print(f"  Installed Makefile to .ahrena/")

    # 5. Bootstrap framework labels when a GitHub remote is detected.
    #    Runs scripts/bootstrap_labels.sh from .ahrena/ against the target repo.
    #    Skipped silently when target is not a git repo, has no GitHub remote,
    #    or gh CLI is missing/unauthenticated (the script handles those cases).
    bootstrap_script = ahrena_dir / "bootstrap_labels.sh"
    if bootstrap_script.exists() and not getattr(args, "dry_run", False):
        try:
            remote_result = subprocess.run(
                ["git", "-C", str(target_dir), "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=False,
            )
            remote_url = (remote_result.stdout or "").strip()
            if remote_result.returncode == 0 and "github.com" in remote_url:
                print("")
                print("--- Phase 4: Bootstrap framework labels ---")
                subprocess.run(
                    ["bash", str(bootstrap_script)],
                    cwd=str(target_dir),
                    check=False,
                )
            else:
                print("  Skipping label bootstrap (no GitHub remote detected).")
        except Exception as exc:  # noqa: BLE001 — best-effort; never abort install
            print(f"  Warning: label bootstrap step failed: {exc}")

    # Persist install-time framework version manifest consumed by kata-ahrena-version.
    write_version_file(ahrena_dir, resolve_install_version(args), dry_run=getattr(args, "dry_run", False))

    return ahrena_dir


def _process_lang_dir_to_cursor(
    lang_dir: Path,
    base_dir: Path,
    target_dir: Path,
    dry_run: bool,
    cursor_config: dict | None = None,
) -> tuple[int, int]:
    """Process a language dir (framework or artifacts) and write .cursor files. Returns (file_count, agent_count)."""
    file_count = 0
    agent_count = 0
    cursor_config = cursor_config or {}
    transposition = cursor_config.get("transposition") or {}
    rules_config = cursor_config.get("rules") or {}

    for md_file in sorted(lang_dir.rglob("*.md")):
        pilar = detect_pilar(md_file.name)
        if pilar is None:
            continue

        resource = transposition[pilar]
        rel_path = md_file.relative_to(base_dir)

        if resource == "agents":
            cursor_path = build_cursor_path(rel_path, pilar, "agents")
            full_path = target_dir / cursor_path
            content = md_file.read_text(encoding="utf-8")
            out_content = transform_md_to_agent(content, pilar, md_file.name)
            if dry_run:
                print(f"    [DRY-RUN] {cursor_path}")
            else:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(out_content, encoding="utf-8")
            agent_count += 1
            continue

        # rules, skills, commands
        rule_key = _framework_rel_path_to_rule_key(rel_path) if resource == "rules" else None
        if resource == "rules" and rule_key and rule_key not in rules_config:
            print(f"\nERROR: Lexis/Codex '{rule_key}' has no entry in cursor.rules (framework/platforms.yaml or .ahrena/platforms.yaml).")
            print("  Per lex-platforms-rules, every lex and codex MUST have a cursor.rules entry with at least 'description'.")
            sys.exit(1)
        rule_config = rules_config.get(rule_key) if rule_key else None
        content = md_file.read_text(encoding="utf-8")
        mdc_content = transform_md_to_mdc(
            content, pilar, md_file.name, resource=resource, rule_config=rule_config
        )
        cursor_path = build_cursor_path(rel_path, pilar, resource)
        full_path = target_dir / cursor_path
        if dry_run:
            print(f"    [DRY-RUN] {cursor_path}")
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(mdc_content, encoding="utf-8")
        file_count += 1

    # Generate agent files only for pilar in PILAR_GENERATES_AGENT when NOT already written as agents by transposition
    for md_file in sorted(lang_dir.rglob("*.md")):
        pilar = detect_pilar(md_file.name)
        if pilar not in PILAR_GENERATES_AGENT:
            continue
        resource = transposition[pilar]
        if resource == "agents":
            continue  # already written in first loop
        agent_name = md_file.stem + ".md"
        agent_path = Path(".cursor") / "agents" / agent_name
        full_path = target_dir / agent_path
        content = md_file.read_text(encoding="utf-8")
        agent_content = transform_md_to_agent(content, pilar, md_file.name)
        if dry_run:
            print(f"    [DRY-RUN] {agent_path}")
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(agent_content, encoding="utf-8")
        agent_count += 1

    return file_count, agent_count


def _process_lang_dir_to_claude_code(
    lang_dir: Path,
    base_dir: Path,
    target_dir: Path,
    dry_run: bool,
    claude_code_config: dict | None = None,
) -> tuple[int, int, int, int]:
    """Process a language dir and write .claude/ files.

    Returns (doc_count, skill_count, agent_count, command_count).
    """
    rule_count = 0
    doc_count = 0
    skill_count = 0
    agent_count = 0
    command_count = 0
    claude_code_config = claude_code_config or {}
    transposition = claude_code_config.get("transposition") or {}
    rules_config = claude_code_config.get("rules") or {}

    for md_file in sorted(lang_dir.rglob("*.md")):
        pilar = detect_pilar(md_file.name)
        if pilar is None:
            continue

        resource = transposition.get(pilar)
        if resource is None:
            continue

        rel_path = md_file.relative_to(base_dir)
        claude_path = build_claude_code_path(rel_path, pilar, resource)
        full_path = target_dir / claude_path

        content = md_file.read_text(encoding="utf-8")
        if resource == "rules":
            rule_key = _framework_rel_path_to_rule_key(rel_path)
            rule_config = rules_config.get(rule_key)
            out_content = transform_md_to_claude_rule(content, pilar, rule_config)
            rule_count += 1
        elif resource == "docs":
            out_content = transform_md_to_claude_doc(content, pilar)
            doc_count += 1
        elif resource == "skills":
            out_content = transform_md_to_claude_skill(content, pilar, md_file.name)
            skill_count += 1
        elif resource == "agents":
            out_content = transform_md_to_claude_agent(content, pilar, md_file.name)
            agent_count += 1
        else:
            out_content = transform_md_to_claude_command(content, pilar)
            command_count += 1

        if dry_run:
            print(f"    [DRY-RUN] {claude_path}")
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(out_content, encoding="utf-8")

    return doc_count + rule_count, skill_count, agent_count, command_count


def install_claude_code(ahrena_dir: Path, target_dir: Path, dry_run: bool = False) -> None:
    """Phase 2: generate .claude/ files and CLAUDE.md from .ahrena/framework/ and .ahrena/artifacts/."""
    directives_path = ahrena_dir / ".directives"
    if not directives_path.exists():
        print(f"\nERROR: .directives not found at {directives_path}")
        sys.exit(1)

    directives = parse_directives(directives_path.read_text(encoding="utf-8"))
    claude_lang = str(get_directive(directives, "language", "claude-code", default="en"))

    framework_dir = ahrena_dir / "framework"
    lang_dir = framework_dir / claude_lang
    templates_dir = framework_dir / "templates"
    artifacts_dir = ahrena_dir / "artifacts"

    if not lang_dir.exists():
        print(f"\nERROR: Language directory not found: {lang_dir}")
        print(f"Available: {[d.name for d in framework_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]}")
        sys.exit(1)

    print(f"  Source language for Claude Code: '{claude_lang}'")

    platforms = load_platforms_config(ahrena_dir)
    claude_code_config = platforms.get("claude-code")
    if not claude_code_config or not isinstance(claude_code_config, dict):
        print("\nERROR: claude-code config not found in platforms.yaml.")
        print("  Define 'claude-code' with 'transposition' in framework/platforms.yaml (or .ahrena/platforms.yaml).")
        sys.exit(1)
    transposition = claude_code_config.get("transposition")
    if not transposition or not isinstance(transposition, dict):
        print("\nERROR: claude-code.transposition not found in platforms.yaml.")
        print("  Define claude-code.transposition (lex, codex, kata, warrior, cry -> docs/commands) in framework/platforms.yaml.")
        sys.exit(1)
    missing = [p for p in PILAR_NAMES if p not in transposition]
    if missing:
        print(f"\nERROR: claude-code.transposition in platforms.yaml must define all pilars. Missing: {', '.join(missing)}")
        print("  Required keys: lex, codex, kata, warrior, cry.")
        sys.exit(1)

    # 1. Process framework
    docs_fw, skills_fw, agents_fw, cmds_fw = _process_lang_dir_to_claude_code(
        lang_dir, framework_dir, target_dir, dry_run, claude_code_config
    )

    # 2. Process templates (samples)
    if templates_dir.exists():
        for md_file in sorted(templates_dir.glob("*-sample.md")):
            pilar = detect_pilar(md_file.name)
            if pilar is None:
                continue

            resource = transposition[pilar]
            if resource == "skills":
                claude_path = Path(".claude") / "skills" / md_file.stem / "SKILL.md"
            elif resource == "agents":
                claude_path = Path(".claude") / "agents" / md_file.name
            elif resource == "commands":
                claude_path = Path(".claude") / "commands" / md_file.name
            else:
                claude_path = Path(".claude") / "docs" / "samples" / md_file.name
            full_path = target_dir / claude_path

            content = md_file.read_text(encoding="utf-8")
            if resource == "docs":
                out_content = transform_md_to_claude_doc(content, pilar)
                docs_fw += 1
            elif resource == "skills":
                out_content = transform_md_to_claude_skill(content, pilar, md_file.name)
                skills_fw += 1
            elif resource == "agents":
                out_content = transform_md_to_claude_agent(content, pilar, md_file.name)
                agents_fw += 1
            else:
                out_content = transform_md_to_claude_command(content, pilar)
                cmds_fw += 1

            if dry_run:
                print(f"    [DRY-RUN] {claude_path}")
            else:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(out_content, encoding="utf-8")

    # 3. Process project artifacts
    docs_art, skills_art, agents_art, cmds_art = 0, 0, 0, 0
    if artifacts_dir.exists():
        artifacts_lang_dir = artifacts_dir / claude_lang
        if artifacts_lang_dir.exists():
            docs_art, skills_art, agents_art, cmds_art = _process_lang_dir_to_claude_code(
                artifacts_lang_dir, artifacts_dir, target_dir, dry_run, claude_code_config
            )

    # 4. Generate CLAUDE.md
    if not dry_run:
        generate_claude_md(target_dir, platforms)
    else:
        print(f"    [DRY-RUN] CLAUDE.md")

    total_docs = docs_fw + docs_art
    total_skills = skills_fw + skills_art
    total_agents = agents_fw + agents_art
    total_cmds = cmds_fw + cmds_art
    has_art = docs_art > 0 or skills_art > 0 or agents_art > 0 or cmds_art > 0
    if has_art:
        print(f"  Generated from framework: {docs_fw} docs, {skills_fw} skills, {agents_fw} agents, {cmds_fw} commands")
        print(f"  Generated from artifacts: {docs_art} docs, {skills_art} skills, {agents_art} agents, {cmds_art} commands")
    else:
        print(f"  Generated {total_docs} docs, {total_skills} skills, {total_agents} agents, {total_cmds} commands")

    # MCP: merge server configs (also runs during sync-claude-code)
    directives = parse_directives(directives_path.read_text(encoding="utf-8"))
    install_mcp(ahrena_dir, target_dir, directives, dry_run=dry_run)

    # PR cost attribution hook: opt-in via pr_cost_tracking.enabled in .directives.
    # Keeps the hook script under .claude/hooks/ and wires it into settings.json.
    install_pr_cost_attribution_hook(ahrena_dir, target_dir, directives, dry_run=dry_run)

    # RTK (Rust Token Killer) bundle: opt-out via rtk.enabled=false in .directives.
    # Ensures the binary is installed, wires the per-project PreToolUse hook with
    # strict fallback, and copies the filters template. Runs on every install/update
    # so the canonical shape is reconciled idempotently.
    install_rtk_bundle(ahrena_dir, target_dir, directives, dry_run=dry_run)


def install_cursor(ahrena_dir: Path, target_dir: Path, dry_run: bool = False) -> None:
    """Phase 2: generate .cursor/ files from .ahrena/framework/ and .ahrena/artifacts/."""
    directives_path = ahrena_dir / ".directives"
    if not directives_path.exists():
        print(f"\nERROR: .directives not found at {directives_path}")
        sys.exit(1)

    directives = parse_directives(directives_path.read_text(encoding="utf-8"))
    cursor_lang = str(get_directive(directives, "language", "cursor", default="en"))

    framework_dir = ahrena_dir / "framework"
    lang_dir = framework_dir / cursor_lang
    templates_dir = framework_dir / "templates"
    artifacts_dir = ahrena_dir / "artifacts"

    if not lang_dir.exists():
        print(f"\nERROR: Language directory not found: {lang_dir}")
        print(f"Available: {[d.name for d in framework_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]}")
        sys.exit(1)

    print(f"  Source language for Cursor: '{cursor_lang}'")

    platforms = load_platforms_config(ahrena_dir)
    cursor_config = platforms.get("cursor")
    if not cursor_config or not isinstance(cursor_config, dict):
        print("\nERROR: cursor config not found in platforms.yaml.")
        print("  Define 'cursor' with 'transposition' in framework/platforms.yaml (or .ahrena/platforms.yaml).")
        sys.exit(1)
    transposition = cursor_config.get("transposition")
    if not transposition or not isinstance(transposition, dict):
        print("\nERROR: cursor.transposition not found in platforms.yaml.")
        print("  Define cursor.transposition (lex, codex, kata, warrior, cry -> rules/skills/agents/commands) in framework/platforms.yaml.")
        sys.exit(1)
    missing = [p for p in PILAR_NAMES if p not in transposition]
    if missing:
        print(f"\nERROR: cursor.transposition in platforms.yaml must define all pilars. Missing: {', '.join(missing)}")
        print("  Required keys: lex, codex, kata, warrior, cry.")
        sys.exit(1)

    # 1. Process framework (so artifacts can overwrite later)
    file_count_fw, agent_count_fw = _process_lang_dir_to_cursor(
        lang_dir, framework_dir, target_dir, dry_run, cursor_config
    )

    # 2. Process templates (samples) — framework only
    if templates_dir.exists():
        for md_file in sorted(templates_dir.glob("*-sample.md")):
            pilar = detect_pilar(md_file.name)
            if pilar is None:
                continue

            resource = cursor_config["transposition"][pilar]
            if resource == "skills":
                cursor_path = Path(".cursor") / "skills" / md_file.stem / "SKILL.md"
            elif resource == "commands":
                cursor_path = Path(".cursor") / "commands" / "samples" / md_file.name
            elif resource == "agents":
                cursor_path = Path(".cursor") / "agents" / md_file.name
            else:
                mdc_name = md_file.name.replace(".md", ".mdc")
                cursor_path = Path(".cursor") / resource / "samples" / mdc_name
            full_path = target_dir / cursor_path

            content = md_file.read_text(encoding="utf-8")
            if resource == "agents":
                out_content = transform_md_to_agent(content, pilar, md_file.name)
            else:
                out_content = transform_md_to_mdc(content, pilar, md_file.name, is_sample=True, resource=resource)
            if dry_run:
                print(f"    [DRY-RUN] {cursor_path}")
            else:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(out_content, encoding="utf-8")
            file_count_fw += 1

    # 3. Process project artifacts (same paths overwrite framework)
    file_count_art = 0
    agent_count_art = 0
    if artifacts_dir.exists():
        artifacts_lang_dir = artifacts_dir / cursor_lang
        if artifacts_lang_dir.exists():
            file_count_art, agent_count_art = _process_lang_dir_to_cursor(
                artifacts_lang_dir, artifacts_dir, target_dir, dry_run, cursor_config
            )

    total_files = file_count_fw + file_count_art
    total_agents = agent_count_fw + agent_count_art
    if file_count_art > 0 or agent_count_art > 0:
        print(f"  Generated {file_count_fw} files from framework, {file_count_art} from project artifacts; {total_agents} agent files")
    else:
        print(f"  Generated {total_files} files from framework; {total_agents} agent files")

    # MCP: merge server configs (also runs during sync-cursor)
    directives = parse_directives(directives_path.read_text(encoding="utf-8"))
    install_mcp(ahrena_dir, target_dir, directives, dry_run=dry_run)


def clean(target_dir: Path) -> None:
    """Remove Ahrena-installed files from the project."""
    ahrena_dir = target_dir / ".ahrena"
    cursor_dir = target_dir / ".cursor"
    claude_dir = target_dir / ".claude"

    if ahrena_dir.exists():
        shutil.rmtree(ahrena_dir)
        print(f"  Removed .ahrena/")

    if cursor_dir.exists():
        prefixes = tuple(f"{p}-" for p in PILAR_NAMES)
        removed = 0

        # Clean .mdc rules
        for mdc_file in list(cursor_dir.rglob("*.mdc")):
            if mdc_file.name.startswith(prefixes):
                mdc_file.unlink()
                removed += 1

        # Clean .md commands
        commands_dir = cursor_dir / "commands"
        if commands_dir.exists():
            for md_file in list(commands_dir.rglob("*.md")):
                if md_file.name.startswith(prefixes):
                    md_file.unlink()
                    removed += 1

        # Clean skill directories (native SKILL.md format)
        skills_dir = cursor_dir / "skills"
        if skills_dir.exists():
            for skill_dir in list(skills_dir.iterdir()):
                if skill_dir.is_dir() and skill_dir.name.startswith(prefixes):
                    shutil.rmtree(skill_dir)
                    removed += 1

        # Clean warrior agents
        agent_prefixes = tuple(f"{p}-" for p in PILAR_GENERATES_AGENT)
        agent_removed = 0
        agents_dir = cursor_dir / "agents"
        if agents_dir.exists():
            for md_file in list(agents_dir.glob("*.md")):
                if md_file.name.startswith(agent_prefixes):
                    md_file.unlink()
                    agent_removed += 1

        # Remove empty directories left behind
        for dirpath in sorted(cursor_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()

        if removed:
            print(f"  Removed {removed} Ahrena files from .cursor/")
        else:
            print(f"  No Ahrena files found in .cursor/")
        if agent_removed:
            print(f"  Removed {agent_removed} Ahrena agent files from .cursor/agents/")

    # Clean Claude Code files
    if claude_dir.exists():
        prefixes = tuple(f"{p}-" for p in PILAR_NAMES)
        removed = 0

        # Clean docs and commands (files with pilar prefixes)
        for md_file in list(claude_dir.rglob("*.md")):
            if md_file.name.startswith(prefixes):
                md_file.unlink()
                removed += 1

        # Clean skill directories (contain SKILL.md; dir name has pilar prefix)
        skills_dir = claude_dir / "skills"
        if skills_dir.exists():
            for skill_dir in list(skills_dir.iterdir()):
                if skill_dir.is_dir() and skill_dir.name.startswith(prefixes):
                    shutil.rmtree(skill_dir)
                    removed += 1

        # Clean agent files (pilar prefix in filename)
        agents_dir = claude_dir / "agents"
        agent_prefixes = tuple(f"{p}-" for p in PILAR_GENERATES_AGENT)
        if agents_dir.exists():
            for md_file in list(agents_dir.glob("*.md")):
                if md_file.name.startswith(agent_prefixes):
                    md_file.unlink()
                    removed += 1

        # Remove empty directories left behind
        for dirpath in sorted(claude_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()

        if removed:
            print(f"  Removed {removed} Ahrena files from .claude/")
        else:
            print(f"  No Ahrena files found in .claude/")

    # MCP entries in .cursor/mcp.json and .claude/settings.json are NOT removed.
    # They cannot be safely distinguished from user-managed entries in the same file.
    print(f"  NOTE: MCP server entries in .cursor/mcp.json and .claude/settings.json were preserved.")
    print(f"        Remove them manually if needed.")

    # Clean CLAUDE.md if it has Ahrena markers
    claude_md = target_dir / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if AHRENA_MARKER_START in content and AHRENA_MARKER_END in content:
            start_idx = content.find(AHRENA_MARKER_START)
            end_idx = content.find(AHRENA_MARKER_END) + len(AHRENA_MARKER_END)
            remaining = (content[:start_idx] + content[end_idx:]).strip()
            if remaining:
                claude_md.write_text(remaining + "\n", encoding="utf-8")
                print(f"  Removed Ahrena section from CLAUDE.md")
            else:
                claude_md.unlink()
                print(f"  Removed CLAUDE.md")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="Ahrena: AI-First Capability Framework — Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  %(prog)s                                                Install .ahrena/ only (from remote)
  %(prog)s --platform cursor                              Install .ahrena/ + .cursor/ (remote)
  %(prog)s --platform claude-code                         Install .ahrena/ + .claude/ + CLAUDE.md (remote)
  %(prog)s --local --platform cursor                      Install from current dir (Ahrena repo root)
  %(prog)s --source /path/to/ahrena --platform cursor     Install from a local clone
  %(prog)s --clades _foundation,documentation             Install only specific clades
  %(prog)s --version v0.1.0                               Install specific version (remote)
  %(prog)s --language en                                  Override default language
  %(prog)s --directives ./my-directives                   Use custom directives
  %(prog)s --clean                                        Remove installed files
  %(prog)s --dry-run --platform cursor                    Preview without changes

offline (run this script directly from a cloned Ahrena repo):
  python scripts/install.py --self --target /path/to/project --platform cursor
  python scripts/install.py --self --target /path/to/project --platform claude-code
  python scripts/install.py --self --target /path/to/project --platform cursor --language en
        """,
    )
    parser.add_argument(
        "--target", default=".",
        help="target project directory (default: current directory)",
    )
    parser.add_argument(
        "--version", default=DEFAULT_VERSION,
        help=f"git tag, release, or branch (default: {DEFAULT_VERSION})",
    )
    parser.add_argument(
        "--repo", default=DEFAULT_REPO,
        help=f"GitHub repository URL (default: {DEFAULT_REPO})",
    )
    parser.add_argument(
        "--platform", choices=["cursor", "claude-code"],
        help="target platform to generate files for (e.g., cursor, claude-code)",
    )
    parser.add_argument(
        "--clades",
        help="comma-separated list of clades to install (default: all)",
    )
    parser.add_argument(
        "--language",
        help="override language.default in .directives (e.g., pt-BR, en, es)",
    )
    parser.add_argument(
        "--languages",
        help="comma-separated list of language directories to copy into .ahrena/framework/ "
             "(default: all; known: pt-BR, en, es). Use to reduce .ahrena/ footprint when "
             "a project only needs a subset.",
    )
    parser.add_argument(
        "--directives",
        help="path or URL to a custom .directives file",
    )
    parser.add_argument(
        "--local", action="store_true",
        help="use current directory as source (Ahrena repo root)",
    )
    parser.add_argument(
        "--source", type=Path, metavar="PATH",
        help="path to local Ahrena repo (use instead of downloading from GitHub)",
    )
    parser.add_argument(
        "--self", action="store_true", dest="self_source",
        help="use the Ahrena repo containing this script as source (offline install to --target)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="show what would be done without making changes",
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="remove all Ahrena-installed files from the project",
    )
    parser.add_argument(
        "--skip-preflight", action="store_true",
        help="skip preflight checks for host tooling (git, make, gh, gpg)",
    )
    parser.add_argument(
        "--non-interactive", action="store_true",
        help="never prompt; soft preflight failures become warnings only",
    )
    return parser


def _run_preflight(args: argparse.Namespace) -> None:
    """Run hard + soft preflight checks. Hard exits the process on failure;
    soft only warns or offers install. No-op for --skip-preflight or --clean."""
    if args.skip_preflight or args.clean:
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import preflight as _preflight  # type: ignore[import-not-found]
    except ImportError as exc:
        print(f"  Preflight unavailable ({exc}); skipping host-tool checks.")
        return
    interactive = False if args.non_interactive else None
    _preflight.run("hard", _preflight.HARD_TOOLS, interactive=interactive)
    _preflight.run("soft", _preflight.SOFT_TOOLS, interactive=interactive)


def main() -> None:
    if sys.version_info < MIN_PYTHON:
        print(f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required "
              f"(found {sys.version_info[0]}.{sys.version_info[1]})")
        sys.exit(1)

    parser = build_parser()
    args = parser.parse_args()
    target_dir = Path(args.target).resolve()

    print("Ahrena: AI-First Capability Framework — Installer")
    print("=" * 52)

    _run_preflight(args)

    # ── Clean mode ──
    if args.clean:
        print(f"\nCleaning Ahrena files from {target_dir} ...")
        if args.dry_run:
            print("  [DRY-RUN] Would remove .ahrena/ and Ahrena .mdc files")
        else:
            clean(target_dir)
        print("\nDone!")
        return

    # ── Install mode ──
    if args.source is not None:
        source_label = str(args.source.resolve())
    elif args.self_source:
        source_label = f"SELF ({Path(__file__).resolve().parent.parent})"
    elif args.local:
        source_label = "LOCAL (CWD)"
    else:
        source_label = args.version
    print(f"\n  Target:   {target_dir}")
    print(f"  Source:   {source_label}")
    print(f"  Platform: {args.platform or 'none (framework only)'}")
    if args.clades:
        print(f"  Clades:   {args.clades}")
    if args.language:
        print(f"  Language:  {args.language}")
    if args.directives:
        print(f"  Directives: {args.directives}")

    # Phase 1: download and install .ahrena/
    print(f"\n--- Phase 1: Install .ahrena/ ---")

    if args.dry_run:
        print("  [DRY-RUN] Would download and install framework to .ahrena/")
        ahrena_dir = target_dir / ".ahrena"
    elif args.source is not None:
        source_dir = Path(args.source).resolve()
        if not (source_dir / "framework").exists():
            print(f"\nERROR: 'framework/' not found in {source_dir}")
            print("--source must point to the Ahrena repository root (containing framework/ and scripts/).")
            sys.exit(1)
        if not (source_dir / "scripts").exists():
            print(f"\nERROR: 'scripts/' not found in {source_dir}")
            print("--source must point to the Ahrena repository root (containing framework/ and scripts/).")
            sys.exit(1)
        ahrena_dir = install_ahrena(source_dir, target_dir, args)
    elif args.self_source:
        source_dir = Path(__file__).resolve().parent.parent
        if not (source_dir / "framework").exists():
            print(f"\nERROR: 'framework/' not found at {source_dir}")
            print("--self assumes this script lives in <ahrena-repo>/scripts/. Check your clone.")
            sys.exit(1)
        ahrena_dir = install_ahrena(source_dir, target_dir, args)
    elif args.local:
        source_dir = Path(".").resolve()
        if not (source_dir / "framework").exists():
            print(f"\nERROR: 'framework/' not found in {source_dir}")
            print("--local requires running from the Ahrena source repository root.")
            sys.exit(1)
        ahrena_dir = install_ahrena(source_dir, target_dir, args)
    else:
        source_dir = download_and_extract(args.repo, args.version)
        try:
            ahrena_dir = install_ahrena(source_dir, target_dir, args)
        finally:
            temp_root = source_dir
            if source_dir.parent != Path(tempfile.gettempdir()):
                temp_root = source_dir.parent
            shutil.rmtree(temp_root, ignore_errors=True)

    # Phase 2: generate platform files
    if args.platform == "cursor":
        print(f"\n--- Phase 2: Generate .cursor/ ---")
        if args.dry_run and not ahrena_dir.exists():
            print("  [DRY-RUN] Would generate .cursor/ files")
        else:
            install_cursor(ahrena_dir, target_dir, dry_run=args.dry_run)
    elif args.platform == "claude-code":
        print(f"\n--- Phase 2: Generate .claude/ + CLAUDE.md ---")
        if args.dry_run and not ahrena_dir.exists():
            print("  [DRY-RUN] Would generate .claude/ files and CLAUDE.md")
        else:
            install_claude_code(ahrena_dir, target_dir, dry_run=args.dry_run)

    print(f"\nDone!")


if __name__ == "__main__":
    main()
