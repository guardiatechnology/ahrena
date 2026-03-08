#!/usr/bin/env python3
"""
Ahrena: AI-First Capability Framework — Installer

Downloads the Ahrena framework from GitHub and installs it locally.
Optionally generates platform-specific files (e.g., Cursor IDE).

Bootstrap (nothing exists locally):
  macOS/Linux:
    curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor
  Windows (PowerShell):
    irm https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; del install.py

After first install:
  make -f .ahrena/Makefile install-cursor
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEFAULT_REPO = "https://github.com/guardiafinance/ahrena"
DEFAULT_VERSION = "main"
MIN_PYTHON = (3, 8)

PILAR_TO_CURSOR_RESOURCE: dict[str, str] = {
    "lex": "rules",
    "codex": "rules",
    "kata": "skills",
    "warrior": "skills",
    "cry": "commands",
}

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
    """Parse the simple YAML-like .directives format (stdlib only, no PyYAML)."""
    result: dict = {}
    stack: list[tuple[dict, int]] = [(result, -1)]
    pending_list_key: str | None = None

    for line in content.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(stripped)

        if stripped.startswith("- "):
            value = stripped[2:].strip().strip('"').strip("'")
            parent, _ = stack[-1]
            if pending_list_key is not None and pending_list_key in parent:
                if not isinstance(parent[pending_list_key], list):
                    parent[pending_list_key] = []
                parent[pending_list_key].append(value)
            continue

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")

            while len(stack) > 1 and stack[-1][1] >= indent:
                stack.pop()

            parent, _ = stack[-1]

            if val:
                parent[key] = val
                pending_list_key = key
            else:
                parent[key] = {}
                stack.append((parent[key], indent))
                pending_list_key = key

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


def parse_clades(value: str | None) -> list[str] | None:
    """Parse a comma-separated clades string into a sorted list, or None for all."""
    if not value:
        return None
    clades = [c.strip() for c in value.split(",") if c.strip()]
    return sorted(clades) if clades else None


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
    for prefix in PILAR_TO_CURSOR_RESOURCE:
        if filename.startswith(f"{prefix}-"):
            return prefix
    return None


def extract_description(content: str) -> str:
    """Build a description from the H1 title and the scope in the blockquote."""
    title = ""
    scope = ""

    for line in content.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
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


def build_frontmatter(pilar: str, filename: str, description: str,
                      is_sample: bool = False) -> str:
    """Generate the YAML frontmatter block for a Cursor .mdc file.

    Frontmatter varies by Cursor resource type:
      - rules  (lex/codex):  description + alwaysApply
      - skills (kata/warrior): name + description
      - commands (cry):        description only
    """
    resource = PILAR_TO_CURSOR_RESOURCE[pilar]
    safe_desc = description.replace('"', '\\"')
    lines = ["---"]

    if resource == "rules":
        lines.append(f'description: "{safe_desc}"')
        if is_sample:
            lines.append("globs: ")
            lines.append("alwaysApply: false")
        else:
            always_apply = "true" if pilar == "lex" else "false"
            lines.append(f"alwaysApply: {always_apply}")
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


def transform_md_to_mdc(content: str, pilar: str, filename: str,
                        is_sample: bool = False) -> str:
    """Transform a framework .md file into a Cursor .mdc file."""
    if is_sample:
        description = SAMPLE_DESCRIPTIONS.get(pilar, extract_description(content))
        body = content
    else:
        description = extract_description(content)
        body = filter_sections(content, pilar)

    frontmatter = build_frontmatter(pilar, filename, description, is_sample)
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


def build_cursor_path(framework_rel_path: Path, pilar: str) -> Path:
    """
    Map a framework-relative path to a .cursor/ path.

    Each Cursor resource type has its own native format:
      rules:    .cursor/rules/{clade}/{subclade}/{file}.mdc
      skills:   .cursor/skills/{skill-name}/SKILL.md
      commands:  .cursor/commands/{clade}/{subclade}/{file}.md
    """
    resource = PILAR_TO_CURSOR_RESOURCE[pilar]
    parts = list(framework_rel_path.parts)

    parts = parts[1:]

    pilar_folder = PILAR_FOLDER_NAME.get(pilar, "")
    parts = [p for p in parts if p != pilar_folder]

    if resource == "skills":
        skill_name = Path(parts[-1]).stem
        return Path(".cursor") / "skills" / skill_name / "SKILL.md"
    elif resource == "commands":
        return Path(".cursor") / "commands" / Path(*parts)
    else:
        parts[-1] = re.sub(r"\.md$", ".mdc", parts[-1])
        return Path(".cursor") / "rules" / Path(*parts)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Installation phases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def copy_framework(src: Path, dst: Path, clades: list[str] | None) -> int:
    """Copy framework/ to destination, optionally filtering by clade.

    Returns the number of clades copied.
    """
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    clade_count = 0

    for item in sorted(src.iterdir()):
        dst_item = dst / item.name
        if item.is_file():
            shutil.copy2(item, dst_item)
        elif item.name == "templates":
            shutil.copytree(item, dst_item)
        elif item.is_dir():
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

    # 1. Copy framework/ (filtered by clades if specified)
    if clades:
        print(f"  Copying framework (clades: {', '.join(clades)}) to {ahrena_framework}/ ...")
    else:
        print(f"  Copying framework to {ahrena_framework}/ ...")

    ahrena_dir.mkdir(parents=True, exist_ok=True)
    copy_framework(framework_src, ahrena_framework, clades)

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

    # 3. Copy scripts for future use (install, update, uninstall)
    scripts_src = source_dir / "scripts"
    for script_name in ("install.py", "update.py", "uninstall.py"):
        src = scripts_src / script_name
        if src.exists():
            shutil.copy2(src, ahrena_dir / script_name)
            print(f"  Installed {script_name} to .ahrena/")

    # 4. Copy Makefile for future use
    makefile_src = source_dir / "Makefile"
    if makefile_src.exists():
        makefile_dst = ahrena_dir / "Makefile"
        shutil.copy2(makefile_src, makefile_dst)
        print(f"  Installed Makefile to .ahrena/")

    return ahrena_dir


def install_cursor(ahrena_dir: Path, target_dir: Path, dry_run: bool = False) -> None:
    """Phase 2: generate .cursor/ files from .ahrena/framework/."""
    directives_path = ahrena_dir / ".directives"
    if not directives_path.exists():
        print(f"\nERROR: .directives not found at {directives_path}")
        sys.exit(1)

    directives = parse_directives(directives_path.read_text(encoding="utf-8"))
    cursor_lang = str(get_directive(directives, "language", "cursor", default="en"))

    framework_dir = ahrena_dir / "framework"
    lang_dir = framework_dir / cursor_lang
    templates_dir = framework_dir / "templates"

    if not lang_dir.exists():
        print(f"\nERROR: Language directory not found: {lang_dir}")
        print(f"Available: {[d.name for d in framework_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]}")
        sys.exit(1)

    print(f"  Source language for Cursor: '{cursor_lang}'")
    file_count = 0

    # Process language-specific artifacts
    for md_file in sorted(lang_dir.rglob("*.md")):
        pilar = detect_pilar(md_file.name)
        if pilar is None:
            continue

        rel_path = md_file.relative_to(framework_dir)
        cursor_path = build_cursor_path(rel_path, pilar)
        full_path = target_dir / cursor_path

        content = md_file.read_text(encoding="utf-8")
        mdc_content = transform_md_to_mdc(content, pilar, md_file.name)

        if dry_run:
            print(f"    [DRY-RUN] {cursor_path}")
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(mdc_content, encoding="utf-8")
        file_count += 1

    # Process templates (samples) — full body, only frontmatter added
    if templates_dir.exists():
        for md_file in sorted(templates_dir.glob("*-sample.md")):
            pilar = detect_pilar(md_file.name)
            if pilar is None:
                continue

            resource = PILAR_TO_CURSOR_RESOURCE[pilar]
            if resource == "skills":
                cursor_path = Path(".cursor") / "skills" / md_file.stem / "SKILL.md"
            elif resource == "commands":
                cursor_path = Path(".cursor") / "commands" / "samples" / md_file.name
            else:
                mdc_name = md_file.name.replace(".md", ".mdc")
                cursor_path = Path(".cursor") / resource / "samples" / mdc_name
            full_path = target_dir / cursor_path

            content = md_file.read_text(encoding="utf-8")
            mdc_content = transform_md_to_mdc(content, pilar, md_file.name, is_sample=True)

            if dry_run:
                print(f"    [DRY-RUN] {cursor_path}")
            else:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(mdc_content, encoding="utf-8")
            file_count += 1

    # Generate .cursor/agents/ for warriors (isolated subagents)
    agent_count = 0
    for md_file in sorted(lang_dir.rglob("*.md")):
        pilar = detect_pilar(md_file.name)
        if pilar not in PILAR_GENERATES_AGENT:
            continue

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

    print(f"  Generated {file_count} .mdc files + {agent_count} agent files")


def clean(target_dir: Path) -> None:
    """Remove Ahrena-installed files from the project."""
    ahrena_dir = target_dir / ".ahrena"
    cursor_dir = target_dir / ".cursor"

    if ahrena_dir.exists():
        shutil.rmtree(ahrena_dir)
        print(f"  Removed .ahrena/")

    if cursor_dir.exists():
        prefixes = tuple(f"{p}-" for p in PILAR_TO_CURSOR_RESOURCE)
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
  %(prog)s                                           Install .ahrena/ only
  %(prog)s --platform cursor                         Install .ahrena/ + .cursor/
  %(prog)s --local --platform cursor                 Install from local source (dev)
  %(prog)s --clades _foundation,documentation        Install only specific clades
  %(prog)s --version v0.1.0                          Install specific version
  %(prog)s --language en                             Override default language
  %(prog)s --directives ./my-directives              Use custom directives
  %(prog)s --clean                                   Remove installed files
  %(prog)s --dry-run --platform cursor               Preview without changes
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
        "--platform", choices=["cursor"],
        help="target platform to generate files for (e.g., cursor)",
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
        "--directives",
        help="path or URL to a custom .directives file",
    )
    parser.add_argument(
        "--local", action="store_true",
        help="use local source directory instead of downloading from GitHub",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="show what would be done without making changes",
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="remove all Ahrena-installed files from the project",
    )
    return parser


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
    source_label = "LOCAL" if args.local else args.version
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

    print(f"\nDone!")


if __name__ == "__main__":
    main()
