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
