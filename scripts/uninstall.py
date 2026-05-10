#!/usr/bin/env python3
"""
Ahrena: AI-First Capability Framework — Uninstaller

Removes all Ahrena-installed files from the project.
Asks for confirmation unless --force is passed.

Usage:
  python .ahrena/uninstall.py
  python .ahrena/uninstall.py --force
  make -f .ahrena/Makefile uninstall
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 8)

PILAR_PREFIXES = ("lex-", "codex-", "kata-", "warrior-", "cry-")


AHRENA_MARKER_START = "<!-- AHRENA:START -->"
AHRENA_MARKER_END = "<!-- AHRENA:END -->"


def count_ahrena_cursor_files(cursor_dir: Path) -> int:
    if not cursor_dir.exists():
        return 0
    return sum(
        1 for f in cursor_dir.rglob("*.mdc")
        if f.name.startswith(PILAR_PREFIXES)
    )


def count_ahrena_claude_code_files(claude_dir: Path) -> int:
    if not claude_dir.exists():
        return 0
    return sum(
        1 for f in claude_dir.rglob("*.md")
        if f.name.startswith(PILAR_PREFIXES)
    )


def uninstall_mcp_package() -> None:
    """Best-effort `pipx uninstall ahrena-mcp`.

    Silent no-op when pipx is missing or the package is not installed.
    Failures here MUST NOT block the rest of the uninstall.
    """
    pipx = shutil.which("pipx")
    if not pipx:
        return
    try:
        listing = subprocess.run(
            [pipx, "list", "--short"],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if listing.returncode != 0:
        return
    if not any(line.strip().startswith("ahrena-mcp") for line in (listing.stdout or "").splitlines()):
        return  # not installed via pipx
    try:
        proc = subprocess.run(
            [pipx, "uninstall", "ahrena-mcp"],
            capture_output=True, text=True, timeout=60, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"  WARNING: pipx uninstall raised {exc}; skipping.", file=sys.stderr)
        return
    if proc.returncode == 0:
        print("  Removed ahrena-mcp via pipx")
    else:
        print(
            f"  WARNING: pipx uninstall ahrena-mcp failed (exit {proc.returncode}). "
            f"Run `pipx uninstall ahrena-mcp` manually if needed.",
            file=sys.stderr,
        )


def remove_ahrena(target: Path) -> None:
    """Remove .ahrena/ and Ahrena files from .cursor/ and .claude/."""
    ahrena_dir = target / ".ahrena"
    cursor_dir = target / ".cursor"
    claude_dir = target / ".claude"

    # Remove the pipx-installed MCP package before deleting source dirs.
    uninstall_mcp_package()

    if ahrena_dir.exists():
        shutil.rmtree(ahrena_dir)
        print(f"  Removed .ahrena/")

    if cursor_dir.exists():
        removed = 0
        for mdc_file in list(cursor_dir.rglob("*.mdc")):
            if mdc_file.name.startswith(PILAR_PREFIXES):
                mdc_file.unlink()
                removed += 1

        for dirpath in sorted(cursor_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()

        if removed:
            print(f"  Removed {removed} Ahrena .mdc files from .cursor/")

    if claude_dir.exists():
        removed = 0
        for md_file in list(claude_dir.rglob("*.md")):
            if md_file.name.startswith(PILAR_PREFIXES):
                md_file.unlink()
                removed += 1

        for dirpath in sorted(claude_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()

        if removed:
            print(f"  Removed {removed} Ahrena .md files from .claude/")

    # Clean CLAUDE.md — remove only the Ahrena section, preserve user content
    claude_md = target / "CLAUDE.md"
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


def main() -> None:
    if sys.version_info < MIN_PYTHON:
        print(f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="uninstall.py",
        description="Ahrena: AI-First Capability Framework — Uninstaller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  %(prog)s                 Uninstall with confirmation
  %(prog)s --force         Uninstall without asking
        """,
    )
    parser.add_argument(
        "--target", default=".",
        help="target project directory (default: current directory)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="skip confirmation prompt",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    ahrena_dir = target / ".ahrena"
    cursor_dir = target / ".cursor"

    print("Ahrena: AI-First Capability Framework — Uninstaller")
    print("=" * 54)

    if not ahrena_dir.exists():
        print("\nAhrena is not installed in this project.")
        sys.exit(0)

    framework_files = sum(1 for _ in ahrena_dir.rglob("*") if _.is_file())
    cursor_files = count_ahrena_cursor_files(cursor_dir)
    claude_dir = target / ".claude"
    claude_files = count_ahrena_claude_code_files(claude_dir)
    claude_md = target / "CLAUDE.md"
    has_claude_md = claude_md.exists() and AHRENA_MARKER_START in claude_md.read_text(encoding="utf-8")

    print(f"\n  Target: {target}")
    print(f"\n  Will be removed:")
    print(f"    .ahrena/           {framework_files} files")
    if cursor_files:
        print(f"    .cursor/ (.mdc)    {cursor_files} Ahrena files")
    if claude_files:
        print(f"    .claude/ (.md)     {claude_files} Ahrena files")
    if has_claude_md:
        print(f"    CLAUDE.md          1 file")
    print()

    if not args.force:
        try:
            answer = input("  Continue? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n\nAborted.")
            sys.exit(1)
        if answer not in ("y", "yes"):
            print("  Aborted.")
            sys.exit(0)

    remove_ahrena(target)
    print("\nDone! Ahrena has been uninstalled.")


if __name__ == "__main__":
    main()
