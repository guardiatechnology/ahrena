#!/usr/bin/env python3
"""
Ahrena: AI-First Capability Framework — Pilar Structure Validator

Validates the framework content tree for:
  - naming:   Every .md file has the correct pilar prefix or is README.md
  - path:     Pilar files are placed in the correct pilar directory
  - sections: Required sections are present per pilar type
  - i18n:     Every pt-BR file has a counterpart in en/ and es/
  - platforms: Every lex-/codex- entry is registered in cursor.rules in platforms.yaml

Usage:
  python scripts/validate.py [--framework PATH] [--check CHECKS]

  --framework   Path to the framework/ directory (default: framework/)
  --check       Comma-separated list of checks to run:
                naming, path, sections, i18n, platforms, all (default: all)

Exit codes:
  0  All checks pass
  1  One or more violations found

Can be used as a pre-commit hook (check naming,platforms is fast):
  python scripts/validate.py --check naming,platforms
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PILAR_PREFIXES: dict[str, str] = {
    "lex-": "lexis",
    "codex-": "codex",
    "kata-": "katas",
    "warrior-": "warriors",
    "cry-": "cries",
}

KNOWN_LANGUAGES = ("pt-BR", "en", "es")
REFERENCE_LANGUAGE = "pt-BR"
I18N_LANGUAGES = ("en", "es")

# Required H2 section keywords per pilar (case-insensitive, any one must match per group).
# Each inner list is a group: at least one keyword from the group must appear in any H2 heading.
REQUIRED_SECTIONS: dict[str, list[list[str]]] = {
    "lex": [
        ["lei", "law", "ley"],  # The unbreakable law declaration
    ],
    "codex": [
        # Overview section — pt-BR: "Visão Geral", en: "Overview", es: "Visión general" or "Resumen General"
        ["visão geral", "overview", "resumen", "visión"],
    ],
    "kata": [
        # Workflow checklist — the most critical section; same keyword in all languages
        ["workflow"],
        # Outputs or the equivalent — accept "objective" as alternative since some
        # translated katas (en/es) use "objective" but omit "outputs"
        ["saídas", "outputs", "salidas", "objetivo", "objective", "objetivo"],
    ],
    "warrior": [
        ["missão", "mission", "misión"],  # Mission statement
    ],
    "cry": [
        # Cries use different structure per language: Invocação / Invocation / Invocación / Uso / Usage
        ["invocação", "invocation", "invocación", "uso", "usage", "comportamento", "behavior", "comportamiento"],
    ],
}

ALWAYS_ALLOWED_NAMES = {"README.md"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_pilar_from_name(filename: str) -> str | None:
    """Return the short pilar name (lex, codex, kata, warrior, cry) from filename."""
    for prefix, folder in PILAR_PREFIXES.items():
        if filename.startswith(prefix):
            return prefix.rstrip("-")
    return None


def expected_pilar_folder(pilar: str) -> str:
    """Return the expected directory name for a pilar."""
    prefix = f"{pilar}-"
    return PILAR_PREFIXES.get(prefix, "")


def get_h2_sections(content: str) -> list[str]:
    """Extract all H2 section headings from markdown content (lowercased)."""
    sections = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            sections.append(heading)
    return sections


def _parse_platforms_yaml_rules(yaml_path: Path) -> set[str]:
    """Extract all keys from cursor.rules in platforms.yaml (stdlib only)."""
    if not yaml_path.exists():
        return set()

    rules: set[str] = set()
    content = yaml_path.read_text(encoding="utf-8")
    in_cursor = False
    in_rules = False
    cursor_indent = -1
    rules_indent = -1

    for line in content.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)

        if stripped.startswith("cursor:"):
            in_cursor = True
            cursor_indent = indent
            in_rules = False
            continue

        if in_cursor:
            if indent <= cursor_indent and stripped and not stripped.startswith("#"):
                in_cursor = False
                in_rules = False
                continue
            if stripped.startswith("rules:"):
                in_rules = True
                rules_indent = indent
                continue

        if in_rules:
            if indent <= rules_indent and stripped and not stripped.startswith("#"):
                in_rules = False
                continue
            # Rule keys are at rules_indent + 4 (or + 2) with a colon
            if ":" in stripped and indent > rules_indent:
                # Only top-level keys under rules (direct children)
                # Nested keys (alwaysApply, description, globs) are deeper
                # Heuristic: rule key lines end with ":" and their value is empty
                first_colon = stripped.index(":")
                rest = stripped[first_colon + 1:].strip()
                if not rest:
                    rule_key = stripped[:first_colon].strip()
                    if rule_key not in ("alwaysApply", "description", "globs", "cursor", "rules", "transposition"):
                        rules.add(rule_key)

    return rules


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Checks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_naming(framework_dir: Path) -> list[str]:
    """Every .md file must start with a pilar prefix or be in ALWAYS_ALLOWED_NAMES."""
    failures: list[str] = []
    for lang_dir in framework_dir.iterdir():
        if not lang_dir.is_dir() or lang_dir.name.startswith("."):
            continue
        for md_file in lang_dir.rglob("*.md"):
            name = md_file.name
            if name in ALWAYS_ALLOWED_NAMES:
                continue
            # Allow files in templates/ directory (they end with -sample.md)
            if "templates" in md_file.parts:
                continue
            has_prefix = any(name.startswith(p) for p in PILAR_PREFIXES)
            if not has_prefix:
                rel = md_file.relative_to(framework_dir)
                failures.append(f"NAMING_PREFIX_VIOLATION  {rel}")
    return failures


def check_path(framework_dir: Path) -> list[str]:
    """Pilar files must be placed in the directory matching their prefix."""
    failures: list[str] = []
    for lang_dir in framework_dir.iterdir():
        if not lang_dir.is_dir() or lang_dir.name.startswith("."):
            continue
        for md_file in lang_dir.rglob("*.md"):
            name = md_file.name
            if name in ALWAYS_ALLOWED_NAMES:
                continue
            if "templates" in md_file.parts:
                continue
            pilar = detect_pilar_from_name(name)
            if pilar is None:
                continue  # naming check will catch this
            expected_folder = expected_pilar_folder(pilar)
            # The immediate parent directory should match the expected pilar folder
            parent_name = md_file.parent.name
            if parent_name != expected_folder:
                rel = md_file.relative_to(framework_dir)
                failures.append(
                    f"PATH_WRONG_PILAR_DIR     {rel}  "
                    f"(in '{parent_name}/', expected '{expected_folder}/')"
                )
    return failures


def check_sections(framework_dir: Path) -> list[str]:
    """Required sections must be present per pilar type."""
    failures: list[str] = []
    for lang_dir in framework_dir.iterdir():
        if not lang_dir.is_dir() or lang_dir.name.startswith("."):
            continue
        for md_file in lang_dir.rglob("*.md"):
            name = md_file.name
            if name in ALWAYS_ALLOWED_NAMES:
                continue
            if "templates" in md_file.parts:
                continue
            pilar = detect_pilar_from_name(name)
            if pilar is None:
                continue
            required = REQUIRED_SECTIONS.get(pilar)
            if not required:
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            sections = get_h2_sections(content)
            rel = md_file.relative_to(framework_dir)
            for group in required:
                # At least one keyword in the group must appear in any section heading
                found = any(
                    any(kw in section for kw in group)
                    for section in sections
                )
                if not found:
                    failures.append(
                        f"MISSING_SECTION          {rel}  "
                        f"(need one of: {', '.join(group)})"
                    )
    return failures


def check_i18n(framework_dir: Path) -> list[str]:
    """Every file in REFERENCE_LANGUAGE must have counterparts in I18N_LANGUAGES."""
    failures: list[str] = []
    ref_dir = framework_dir / REFERENCE_LANGUAGE
    if not ref_dir.exists():
        return [f"I18N_MISSING_REF_DIR     {REFERENCE_LANGUAGE}/ not found in framework/"]

    for md_file in ref_dir.rglob("*.md"):
        name = md_file.name
        if name in ALWAYS_ALLOWED_NAMES:
            continue
        if "templates" in md_file.parts:
            continue
        rel = md_file.relative_to(ref_dir)
        for lang in I18N_LANGUAGES:
            target = framework_dir / lang / rel
            if not target.exists():
                failures.append(
                    f"I18N_MISSING             {REFERENCE_LANGUAGE}/{rel}  "
                    f"(missing in {lang}/)"
                )
    return failures


def check_platforms(framework_dir: Path, platforms_yaml: Path) -> list[str]:
    """Every lex-/codex- file must have a cursor.rules entry in platforms.yaml."""
    failures: list[str] = []
    registered_rules = _parse_platforms_yaml_rules(platforms_yaml)

    # Check against any one language (use REFERENCE_LANGUAGE as source of truth)
    ref_dir = framework_dir / REFERENCE_LANGUAGE
    if not ref_dir.exists():
        return [f"PLATFORMS_NO_REF_DIR     {REFERENCE_LANGUAGE}/ not found"]

    for md_file in ref_dir.rglob("*.md"):
        name = md_file.name
        if name in ALWAYS_ALLOWED_NAMES:
            continue
        if "templates" in md_file.parts:
            continue
        pilar = detect_pilar_from_name(name)
        if pilar not in ("lex", "codex"):
            continue  # only lex/codex require platforms.yaml entries

        # Reconstruct rule key: {clade}/{subclade}/{pilar_folder}/{stem}
        # md_file relative to ref_dir: e.g. _foundation/tooling/lexis/lex-mcp.md
        rel = md_file.relative_to(ref_dir)
        rule_key = str(rel.with_suffix("")).replace("\\", "/")

        if rule_key not in registered_rules:
            failures.append(
                f"PLATFORMS_YAML_MISSING   {REFERENCE_LANGUAGE}/{rel}  "
                f"(key '{rule_key}' not in cursor.rules)"
            )
    return failures


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate.py",
        description="Ahrena: AI-First Capability Framework — Pilar Structure Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
checks:
  naming    Every .md file has correct pilar prefix or is README.md
  path      Pilar files are in the correct pilar directory
  sections  Required H2 sections present per pilar type
  i18n      Every pt-BR file has counterpart in en/ and es/
  platforms Every lex-/codex- file is registered in cursor.rules in platforms.yaml
  all       Run all checks (default)

examples:
  %(prog)s
  %(prog)s --check naming,platforms
  %(prog)s --framework .ahrena/framework --check all
  %(prog)s --check naming,platforms   # fast pre-commit hook
        """,
    )
    parser.add_argument(
        "--framework", default="framework",
        help="path to the framework/ directory (default: framework/)",
    )
    parser.add_argument(
        "--check", default="all",
        help="comma-separated checks to run: naming,path,sections,i18n,platforms,all",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    framework_dir = Path(args.framework).resolve()
    if not framework_dir.exists():
        print(f"ERROR: framework directory not found: {framework_dir}", file=sys.stderr)
        sys.exit(1)

    platforms_yaml = framework_dir / "platforms.yaml"

    selected_raw = [c.strip().lower() for c in args.check.split(",") if c.strip()]
    if "all" in selected_raw:
        selected = {"naming", "path", "sections", "i18n", "platforms"}
    else:
        valid = {"naming", "path", "sections", "i18n", "platforms"}
        unknown = set(selected_raw) - valid
        if unknown:
            print(f"ERROR: unknown check(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            print(f"  Valid: {', '.join(sorted(valid))}", file=sys.stderr)
            sys.exit(1)
        selected = set(selected_raw)

    print(f"Ahrena Validator — framework: {framework_dir}")
    print(f"Checks: {', '.join(sorted(selected))}")
    print("=" * 60)

    all_failures: list[str] = []

    if "naming" in selected:
        failures = check_naming(framework_dir)
        all_failures.extend(failures)
        label = "naming   "
        if failures:
            print(f"FAIL [{label}] {len(failures)} violation(s)")
        else:
            print(f"PASS [{label}]")

    if "path" in selected:
        failures = check_path(framework_dir)
        all_failures.extend(failures)
        label = "path     "
        if failures:
            print(f"FAIL [{label}] {len(failures)} violation(s)")
        else:
            print(f"PASS [{label}]")

    if "sections" in selected:
        failures = check_sections(framework_dir)
        all_failures.extend(failures)
        label = "sections "
        if failures:
            print(f"FAIL [{label}] {len(failures)} violation(s)")
        else:
            print(f"PASS [{label}]")

    if "i18n" in selected:
        failures = check_i18n(framework_dir)
        all_failures.extend(failures)
        label = "i18n     "
        if failures:
            print(f"FAIL [{label}] {len(failures)} violation(s)")
        else:
            print(f"PASS [{label}]")

    if "platforms" in selected:
        failures = check_platforms(framework_dir, platforms_yaml)
        all_failures.extend(failures)
        label = "platforms"
        if failures:
            print(f"FAIL [{label}] {len(failures)} violation(s)")
        else:
            print(f"PASS [{label}]")

    if all_failures:
        print()
        print(f"{'=' * 60}")
        print(f"VIOLATIONS ({len(all_failures)} total):")
        for f in all_failures:
            print(f"  {f}")
        print()
        sys.exit(1)
    else:
        print()
        print("All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
