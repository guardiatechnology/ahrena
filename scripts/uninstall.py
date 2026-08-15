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
AHRENA_CODEX_MARKER_START = "<!-- AHRENA:CODEX:START -->"
AHRENA_CODEX_MARKER_END = "<!-- AHRENA:CODEX:END -->"


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


def count_ahrena_codex_files(target: Path) -> int:
    docs = target / ".codex" / "docs"
    agents = target / ".codex" / "agents"
    skills = target / ".agents" / "skills"
    count = sum(
        1 for f in docs.rglob("*.md")
        if f.name.startswith(("lex-", "codex-")) or f == docs / "AHRENA.md"
    ) if docs.exists() else 0
    count += sum(1 for f in agents.glob("warrior-*.toml")) if agents.exists() else 0
    if skills.exists():
        count += sum(
            1 for d in skills.iterdir()
            if d.is_dir() and d.name.startswith(("kata-", "cry-", "ahrena-reference"))
        )
    return count


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
    codex_dir = target / ".codex"
    skills_dir = target / ".agents" / "skills"

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

    if codex_dir.exists():
        docs_dir = codex_dir / "docs"
        if docs_dir.exists():
            for doc in list(docs_dir.rglob("*.md")):
                if doc.name.startswith(("lex-", "codex-")) or doc == docs_dir / "AHRENA.md":
                    doc.unlink()
            for directory in sorted(docs_dir.rglob("*"), reverse=True):
                if directory.is_dir() and not any(directory.iterdir()):
                    directory.rmdir()
            if docs_dir.exists() and not any(docs_dir.iterdir()):
                docs_dir.rmdir()
        agents_dir = codex_dir / "agents"
        if agents_dir.exists():
            for agent in agents_dir.glob("warrior-*.toml"):
                agent.unlink()
            if not any(agents_dir.iterdir()):
                agents_dir.rmdir()
        marker = codex_dir / ".ahrena-platform"
        if marker.exists():
            marker.unlink()
        config_path = codex_dir / "config.toml"
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            start = "# AHRENA:CODEX:MCP:START"
            end = "# AHRENA:CODEX:MCP:END"
            if start in content and end in content:
                start_idx = content.find(start)
                end_idx = content.find(end) + len(end)
                remaining = (content[:start_idx] + content[end_idx:]).strip()
                if remaining:
                    config_path.write_text(remaining + "\n", encoding="utf-8")
                else:
                    config_path.unlink()
        if not any(codex_dir.iterdir()):
            codex_dir.rmdir()
        print("  Removed Ahrena OpenAI Codex resources")

    if skills_dir.exists():
        for skill in list(skills_dir.iterdir()):
            if skill.is_dir() and skill.name.startswith(("kata-", "cry-", "ahrena-reference")):
                shutil.rmtree(skill)

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

    agents_md = target / "AGENTS.md"
    if agents_md.exists():
        content = agents_md.read_text(encoding="utf-8")
        if AHRENA_CODEX_MARKER_START in content and AHRENA_CODEX_MARKER_END in content:
            start_idx = content.find(AHRENA_CODEX_MARKER_START)
            end_idx = content.find(AHRENA_CODEX_MARKER_END) + len(AHRENA_CODEX_MARKER_END)
            remaining = (content[:start_idx] + content[end_idx:]).strip()
            if remaining:
                agents_md.write_text(remaining + "\n", encoding="utf-8")
            else:
                agents_md.unlink()
            print("  Removed Ahrena section from AGENTS.md")


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
    codex_files = count_ahrena_codex_files(target)
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
    if codex_files:
        print(f"    Codex resources    {codex_files} Ahrena files/directories")
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
