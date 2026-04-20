# Codex: Framework application per platform (platforms.yaml)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Transposition and application of Ahrena artifacts to each platform (Cursor, future ones)

## Overview

This Codex documents the **`platforms.yaml`** file, which defines per platform **how framework artifacts are transposed and applied**: which Pilar maps to which platform resource (transposition) and with which options (alwaysApply, globs, description) each artifact is generated. The installer and sync (e.g. `python .ahrena/update.py --sync-cursor`) use this file to generate `.cursor/` (or another IDE) in a controlled, token-efficient way.

## Context

- **Domain:** Ahrena integration with platforms (Cursor today; OpenAI, Claude, others in the future)
- **Audience:** Framework maintainers, integrators, and anyone customizing per-platform artifact generation
- **Update when:** A new platform is supported or the application policy (alwaysApply, globs) changes

## Content

### File location

| Source | Path | Use |
|--------|------|-----|
| **Default (framework)** | `framework/platforms.yaml` | Shipped with the framework; copied to `.ahrena/framework/platforms.yaml` on install |
| **Override (project)** | `.ahrena/platforms.yaml` | Optional; the project can override or extend the default |

The install/sync script merges: it loads the default first, then applies the override (by platform key and, under `rules`, by rule key).

### Structure per platform

Each platform has a top-level key (e.g. `cursor`) with:

1. **`transposition`** — mapping Ahrena Pilar → platform resource  
   - Cursor example: `lex` → `rules`, `codex` → `rules`, `kata` → `skills`, `warrior` → `agents`, `cry` → `commands`
2. **Resource sections** (e.g. `rules`) — per-artifact application config  
   - For Cursor: under `rules`, each key is the **rule key** (artifact path without language and without `.md`); the value defines `alwaysApply`, `globs`, and `description`.

### Rule key

The **rule key** identifies the artifact in a way that is invariant across languages and platforms:

- Framework-relative path **without** the language segment and **without** `.md`  
- Example: `en/_foundation/process/lexis/lex-directives.md` → `_foundation/process/lexis/lex-directives`

### Default policy (Cursor)

- **Default for all rules:** `alwaysApply: false`; **description** always present (from YAML or derived from the artifact body) so Cursor can apply the rule intelligently.
- **Exceptions with `alwaysApply: true`** (defined in `platforms.yaml`): e.g. `lex-directives`, `lex-checkpoint`.

### Discipline around `alwaysApply: true` / `essential: true`

Both flags inflate baseline context on every session (Cursor rules with `alwaysApply: true` are always loaded; Claude Code docs with `essential: true` are inlined in `CLAUDE.md`). Adding an artifact with these flags costs context tokens on 100% of sessions, not just relevant ones.

Rules:

1. **Default is always `false`.** Marking `true` requires an explicit justification in the PR introducing the change.
2. **A PR that adds `alwaysApply: true` or `essential: true` to a Lexis or Codex MUST include an ADR** (via `kata-adr-write`) explaining why the artifact is essential enough to live in every session's base context.
3. **Review candidates periodically** (suggested: each major framework version): is the artifact still being read in most sessions? If no → demote to `false`.

### YAML subset supported by the custom parser

`scripts/install.py` ships a stdlib-only YAML parser intentionally narrow in scope. The parser supports:

- Top-level keys with nested keys (2+ space indentation).
- Scalar values: strings (quoted or not, `"` escape supported), booleans (`true`/`false` case-insensitive), integers via plain conversion.
- Nested maps via indentation.
- Lists via `- item` entries under a list-valued key.

The parser does **NOT** support:

- Anchors (`&anchor`) and aliases (`*alias`).
- Multi-line scalars with `|` or `>` folding.
- Flow-style sequences/maps (`[a, b]`, `{k: v}`).
- Quoted strings spanning multiple lines.

If `platforms.yaml` or `.directives` needs a feature outside this subset, either (a) refactor to stay within subset, or (b) install the optional `pyyaml` dependency — `scripts/install.py` auto-detects and uses it when available.

### Use in Cursor sync

When running `python .ahrena/update.py --sync-cursor` (or `make sync-cursor`):

1. The script loads `platforms.yaml` (default + override).
2. Uses `cursor.transposition` to decide the destination of each Pilar (path and format).
3. Uses `cursor.rules` to build the frontmatter of `.mdc` files (alwaysApply, globs, description). Rules not listed get the default: alwaysApply false, description derived from the body.

## References

- **`lex-platforms-rules`** — every Lexis and Codex must have an entry in `cursor.rules` in `platforms.yaml` (at least `description`); consult when creating or publishing lex/codex
- `lex-directives` — obligation to read `.directives`; paths and conventions
- `codex-pilars` — Pilar system and creation flow
- Sync-cursor Kata/Cry (e.g. `kata-make-sync-cursor`, `cry-make`) — when to regenerate `.cursor/`
