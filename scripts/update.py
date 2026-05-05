#!/usr/bin/env python3
"""
Ahrena: AI-First Capability Framework — Updater

Updates an existing Ahrena installation to the latest (or specified) version.
Automatically detects the installed platform and preserves .directives.

Usage:
  python .ahrena/update.py
  python .ahrena/update.py --version v0.2.0
  make -f .ahrena/Makefile update
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = "https://github.com/guardiatechnology/ahrena"
DEFAULT_VERSION = "main"
MIN_PYTHON = (3, 8)

CURSOR_DIRS = ("rules", "skills", "commands")
CLAUDE_CODE_DIRS = ("docs", "commands")


def detect_platform(target: Path) -> str | None:
    """Detect which platform was previously installed."""
    cursor_dir = target / ".cursor"
    if any((cursor_dir / d).exists() for d in CURSOR_DIRS):
        return "cursor"
    claude_dir = target / ".claude"
    if any((claude_dir / d).exists() for d in CLAUDE_CODE_DIRS):
        return "claude-code"
    return None


def detect_clades(target: Path) -> str | None:
    """Read saved clade selection from a previous install, if any."""
    clades_file = target / ".ahrena" / ".installed-clades"
    if not clades_file.exists():
        return None
    content = clades_file.read_text(encoding="utf-8").strip()
    return content.replace("\n", ",") if content else None


def main() -> None:
    if sys.version_info < MIN_PYTHON:
        print(f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="update.py",
        description="Ahrena: AI-First Capability Framework — Updater",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  %(prog)s                                  Update from remote (default)
  %(prog)s --version v0.2.0                 Update to specific version (remote)
  %(prog)s --local                          Update from current directory (local repo)
  %(prog)s --source /path/to/ahrena         Update from local clone
  %(prog)s --clades _foundation,docs        Override saved clade selection
  %(prog)s --dry-run                        Preview without changes
  %(prog)s --sync-cursor                    Only regenerate .cursor/ from .ahrena/framework/ and .ahrena/artifacts/
  %(prog)s --sync-cursor --dry-run          Preview .cursor sync without writing
  %(prog)s --sync-claude-code               Only regenerate .claude/ + CLAUDE.md from .ahrena/framework/ and .ahrena/artifacts/
  %(prog)s --sync-claude-code --dry-run     Preview .claude sync without writing
        """,
    )
    parser.add_argument(
        "--target", default=".",
        help="target project directory (default: current directory)",
    )
    parser.add_argument(
        "--version", default=DEFAULT_VERSION,
        help=f"version to update to (default: {DEFAULT_VERSION})",
    )
    parser.add_argument(
        "--repo", default=DEFAULT_REPO,
        help=f"GitHub repository URL (default: {DEFAULT_REPO})",
    )
    parser.add_argument(
        "--local", action="store_true",
        help="update from current directory (Ahrena repo root)",
    )
    parser.add_argument(
        "--source", type=Path, metavar="PATH",
        help="update from local Ahrena repo at PATH",
    )
    parser.add_argument(
        "--clades",
        help="comma-separated list of clades (overrides saved selection)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="show what would be done without making changes",
    )
    parser.add_argument(
        "--sync-cursor", action="store_true",
        help="only regenerate .cursor/ from .ahrena/framework/ and .ahrena/artifacts/ (no download)",
    )
    parser.add_argument(
        "--sync-claude-code", action="store_true",
        help="only regenerate .claude/ + CLAUDE.md from .ahrena/framework/ and .ahrena/artifacts/ (no download)",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    ahrena_dir = target / ".ahrena"
    install_py = ahrena_dir / "install.py"
    directives_path = ahrena_dir / ".directives"

    # Verify installation exists
    if not ahrena_dir.exists():
        print("Ahrena: AI-First Capability Framework — Updater")
        print("=" * 52)
        print("\nERROR: Ahrena is not installed in this project.")
        print("Run install.py first to set up the framework.")
        sys.exit(1)

    if not install_py.exists():
        print("Ahrena: AI-First Capability Framework — Updater")
        print("=" * 52)
        print("\nERROR: .ahrena/install.py not found.")
        print("Re-run the original installer to restore it.")
        sys.exit(1)

    if args.sync_cursor or args.sync_claude_code:
        if not directives_path.exists():
            print("Ahrena: AI-First Capability Framework — Updater")
            print("=" * 52)
            print("\nERROR: .ahrena/.directives not found.")
            print("Re-run the installer or restore .directives.")
            sys.exit(1)
        sync_target = ".cursor" if args.sync_cursor else ".claude/ + CLAUDE.md"
        print("Ahrena: AI-First Capability Framework — Updater")
        print("=" * 52)
        print(f"\n  Target:       {target}")
        print(f"  Mode:         sync {sync_target} only (no download)")
        if args.dry_run:
            print("  Dry-run:      yes")
        print()
        sys.path.insert(0, str(ahrena_dir))
        import install as install_mod
        if args.sync_cursor:
            install_mod.install_cursor(ahrena_dir, target, dry_run=args.dry_run)
        else:
            install_mod.install_claude_code(ahrena_dir, target, dry_run=args.dry_run)
        sys.exit(0)

    platform = detect_platform(target)
    clades = args.clades or detect_clades(target)

    use_local = args.local or args.source is not None

    print("Ahrena: AI-First Capability Framework — Updater")
    print("=" * 52)
    print(f"\n  Target:   {target}")
    if use_local:
        if args.source is not None:
            print(f"  Source:   {Path(args.source).resolve()}")
        else:
            print(f"  Source:   local (CWD)")
    else:
        print(f"  Version:  {args.version}")
    print(f"  Platform: {platform or 'none (framework only)'}")
    if clades:
        print(f"  Clades:   {clades}")
    print()

    cmd = [sys.executable, str(install_py), "--target", str(target)]
    if use_local:
        if args.source is not None:
            cmd.extend(["--source", str(Path(args.source).resolve())])
        else:
            cmd.append("--local")
    else:
        cmd.extend(["--version", args.version, "--repo", args.repo])
    if platform:
        cmd.extend(["--platform", platform])
    if clades:
        cmd.extend(["--clades", clades])
    if args.dry_run:
        cmd.append("--dry-run")

    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
