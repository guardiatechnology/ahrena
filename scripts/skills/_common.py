"""Shared helpers for the skill validator and packager (stdlib only)."""

from __future__ import annotations

import dataclasses
import re
import subprocess
from pathlib import Path
from typing import Literal

Severity = Literal["error", "warning"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Anthropic Agent Skills slug regex (codex-skill-anthropic-agent-skills).
SLUG_REGEX = re.compile(r"^[a-z0-9](?:[a-z0-9]|-(?!-)){0,62}[a-z0-9]?$")
RESERVED_SLUG_TOKENS = ("anthropic", "claude")

DESCRIPTION_MIN = 1
DESCRIPTION_MAX = 1024

# SemVer (lex-semantic-version).
SEMVER_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

# Skill manifest schema version (lex-skill-package-structure).
MANIFEST_SCHEMA_VERSION = 1

# Default paths (lex-skill-project-structure).
DEFAULT_SKILLS_ROOT = "skills"
DEFAULT_SKILLS_BUILD = ".build"
DEFAULT_SKILLS_DIST = ".dist"


@dataclasses.dataclass(frozen=True)
class Violation:
    rule: str
    severity: Severity
    file: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return dataclasses.asdict(self)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Frontmatter parsing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_frontmatter(text: str) -> dict[str, object] | None:
    """Parse the YAML frontmatter at the top of `text`.

    Supports the subset used by SKILL.md: scalar top-level keys plus a single
    nested block (e.g., `metadata:`) with scalar leaves. Returns None when no
    frontmatter is detected.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None

    out: dict[str, object] = {}
    current_block: dict[str, object] | None = None

    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.lstrip(" ")
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        unquoted = value.strip("'\"")

        if indent == 0:
            current_block = None
            if not value:
                current_block = {}
                out[key] = current_block
            else:
                out[key] = unquoted
        else:
            if current_block is None:
                continue
            current_block[key] = unquoted

    return out


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Directives reading
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def read_directives_paths(directives_path: Path) -> dict[str, str]:
    """Extract `paths.skills_root`, `paths.skills_build`, `paths.skills_dist`.

    Falls back to defaults when `.ahrena/.directives` does not exist or when a
    given key is absent. Stdlib-only parsing tuned for the simple structure
    used by the framework.
    """
    out = {
        "skills_root": DEFAULT_SKILLS_ROOT,
        "skills_build": DEFAULT_SKILLS_BUILD,
        "skills_dist": DEFAULT_SKILLS_DIST,
    }
    if not directives_path.is_file():
        return out
    try:
        text = directives_path.read_text(encoding="utf-8")
    except OSError:
        return out

    in_paths = False
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.lstrip(" ")

        if indent == 0:
            in_paths = stripped.startswith("paths:")
            continue

        if not in_paths:
            continue
        if indent == 0:
            in_paths = False
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip().split("#", 1)[0].strip().strip("'\"")
        if key in out and value:
            out[key] = value
    return out


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Git helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def current_head_sha(repo: Path) -> str | None:
    """Return the SHA of HEAD in `repo`, or None when git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    sha = result.stdout.strip()
    return sha or None
