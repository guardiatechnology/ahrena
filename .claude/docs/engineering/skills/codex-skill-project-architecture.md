# Codex: Skill Project Architecture (Ahrena)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Internal structure of a skill project in the Ahrena repository (`skills/{slug}/`), the role of each subdirectory, the `dev → build → dist` cycle, and reuse of existing architecture codex during authoring

## Content

### Canonical source project layout

```
skills/{slug}/
├── SKILL.md                    # Agent Skills frontmatter + body (orchestrates the other artifacts)
├── .skill-manifest.json        # Skeleton; populated with refs+hashes by the build
├── skill.config.json           # Local project config (language, runtimes, dev server ports)
├── references/                 # Additional Markdown (level-3 of the spec) — optional
├── scripts/                    # JS or Python — utilities executable by the agent — optional
│   ├── package.json            # when JS
│   ├── pyproject.toml          # when Python
│   └── src/
├── tools/                      # MCP tools (logic) — Ahrena convention, optional
│   ├── mcp.config.json
│   └── handlers/
└── widgets/                    # React (TS) — UI — Ahrena convention, optional
    ├── package.json
    ├── manifest.json
    └── src/
```

`{slug}` is valid kebab-case per the Anthropic spec (`a-z`, `0-9`, hyphen; no leading/trailing hyphen; no `--`; **identical to `name` in SKILL.md**).

### Anthropic spec ↔ Ahrena project mapping

| Item | Where in the spec (`.dist/{slug}/`) | Where in the source project (`skills/{slug}/`) | Status |
|------|--------------------------------------|--------------------------------------------------|--------|
| `SKILL.md` | root | root | spec native |
| `references/` | root | root | native |
| `scripts/` | root (ready executables) | root (source; build freezes in `.build/`) | native |
| `assets/` | root | (created by the author when needed) | native |
| `tools/` (MCP) | root | root | **Ahrena convention**, outside the spec |
| `widgets/` (React) | root | root | **Ahrena convention**, outside the spec |
| `.skill-manifest.json` | root | root (skeleton, completed at build) | **Ahrena convention** |
| `skill.config.json` | (does not go to the package) | root | **Ahrena convention** (dev/build only) |

Ahrena conventions (`tools/`, `widgets/`, `.skill-manifest.json`) are **extensions** of the spec — external agents that only know the spec ignore these directories; agents that know the Ahrena convention consume them.

### `SKILL.md` in the source project

The `SKILL.md` in the source project is the same file that goes to the final package (the build only rewrites relative paths when necessary). Minimum structure:

```markdown
---
name: scheduled-payments-skill
description: Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer.
license: Apache-2.0
metadata:
  version: "0.1.0"
  language: pt-BR
  spec_version: "agentskills.io/specification@2026-04"
---

# Scheduled Payments Skill

## When to use
{...}

## Flow
1. Render the `widgets/transfer-form/` widget for the user.
2. When the user confirms, invoke the `tools/handlers/create_transfer.py` tool.
3. Show the result in the confirmation widget.

## Restrictions

- **A skill is not a framework Pilar.** It does not have a prefix in `framework/`, does not appear in `naming.prefixes`. It is an external project governed by the artifacts of this codex and `lex-skill-project-structure`.
- **Ahrena conventions (`tools/`, `widgets/`) are optional.** Skills MAY exist with only `SKILL.md` + spec-pure `scripts/`/`references/`. The convention applies when the skill needs UI or its own MCP.
- **Single-language per skill.** `metadata.language` declares one language; producing the same skill in pt-BR and en requires two projects `skills/{slug}-ptbr/` and `skills/{slug}-en/` or an internal localization mechanism (not governed in this PR).
- **Directory slug == frontmatter `name`.** The spec requires it; `kata-init-skill` validates it.
