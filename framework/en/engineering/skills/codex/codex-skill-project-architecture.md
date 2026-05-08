# Codex: Skill Project Architecture (Ahrena)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Internal structure of a skill project in the Ahrena repository (`skills/{slug}/`), the role of each subdirectory, the `dev → build → dist` cycle, and reuse of existing architecture codex during authoring

## Overview

Each external skill is a **first-class project** in the Ahrena repository, with versioned source under `skills/{slug}/`. The project follows the Ahrena Pilars during authoring — widgets adopt `codex-frontend-architecture`, scripts and tools in Python adopt `codex-python-architecture`, quality rules come from the corresponding Lexis — without duplication. The final result is a package in the Anthropic Agent Skills format (per `codex-skill-anthropic-agent-skills`), delivered in `.dist/`.

This Codex defines **only the source project layout and the dev/build/dist cycle**. It does not cover:

- Details of the Anthropic Agent Skills format → `codex-skill-anthropic-agent-skills`
- Convention for MCP tools and React widgets (manifests, bindings) → `codex-skill-tools-and-widgets`
- Final package structure in `.dist/` → `lex-skill-package-structure`

## Context

- **Domain:** skill projects versioned in the Ahrena repository
- **Audience:** skill authors, `kata-init-skill`, agents that delegate editing (`warrior-hephaestus` for widgets, `warrior-apollo` for Python scripts/tools)
- **Update:** when the subdirectory convention changes; when new artifact types are introduced

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

## References
- Form details: [references/FORM.md](references/FORM.md)
- Creation tool: `tools/handlers/create_transfer.py`
```

Spec recommendations apply: **< 500 lines**, **< 5,000 tokens**, extensive content goes to `references/`.

### `skill.config.json`

Local project configuration, **does not go to the final package**. Read by `kata-init-skill` (scaffold) and by the consuming project's build/release stack.

Canonical skeleton:

```json
{
  "schema_version": 1,
  "language": "pt-BR",
  "runtimes": {
    "scripts": "python | node",
    "widgets": "react"
  },
  "external_refs": [
    {
      "kind": "lexis",
      "id": "_foundation/tooling/lexis/lex-mcp"
    }
  ]
}
```

`external_refs` lists Ahrena framework artifacts (lex/codex/kata) that the consuming project's build snapshots into `references/` at delivery time, validated by `lex-skill-package-structure`. Stack-specific keys (bundler, ports, runners) belong to the consuming project's own configuration, not to `skill.config.json`.

### Subdirectories — role and details

#### `SKILL.md` + `references/` (spec native)

Author's domain; no Ahrena rule beyond what `codex-skill-anthropic-agent-skills` defines.

#### `scripts/` (spec native)

Executable code invoked by the agent. **Language:** JS (Node) or Python — choose by context:

- Python for domain logic, integration with structured APIs, data processing (aligned with `codex-python-architecture`, `codex-python-tooling`)
- JS for DOM utilities, markup generation, browser runtime interaction
- Mixing is allowed (a skill MAY have both)

Each script follows the Lexis and codex of its language **without adjustment**:

| Aspect | Python | JS/TS |
|--------|--------|-------|
| Typing | `lex-python-typing` (mypy strict) | `lex-frontend-typing` (TS strict) — when applicable |
| Errors | `lex-python-error-handling`, `lex-python-result-type` | idiomatic handling |
| Testing | `lex-python-testing` | `lex-frontend-testing` |
| Logging | `lex-logging-decorator` (cross-language) | `lex-logging-decorator` |
| Security | `lex-python-security` | `lex-frontend-security` |

Details of **script ↔ widget connection** live in `codex-skill-tools-and-widgets`.

#### `tools/` (Ahrena convention, optional)

MCP tools that the external agent invokes during skill execution. They serve as domain tools owned by the skill, without exposing raw Ahrena artifacts.

Details (manifest, registration, connection) in `codex-skill-tools-and-widgets`. In PR 1 (scaffold), the directory exists empty with a placeholder `mcp.config.json` and a trivial example in `handlers/`.

#### `widgets/` (Ahrena convention, optional)

React components that the agent renders in the chat. **Architecture inherits in full** from `codex-frontend-architecture`:

- Layers (Pages → Features → Components → Hooks → Services → State)
- Server state via TanStack Query / SWR; client state via Zustand / Context as scoped
- Types derived from OpenAPI when available (via `openapi-typescript`)
- WCAG 2.1 AA accessibility per `lex-frontend-accessibility`
- Security per `lex-frontend-security` (no `dangerouslySetInnerHTML` without sanitization, no secrets in the bundle)
- Tests per `lex-frontend-testing`
- Guardia design system per `lex-design-system-library` when the widget is rendered on a Guardia surface

Details of manifest, props, events, and binding with scripts/tools in `codex-skill-tools-and-widgets`. In PR 1, the directory ships empty with a minimum `package.json` and an example component.

### Reuse of codex and Lexis during authoring

| Project content | Applicable architecture codex | Applicable Lexis (without adjustment) |
|-----------------|-------------------------------|---------------------------------------|
| `widgets/` (React) | `codex-frontend-architecture` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` |
| `scripts/` Python | `codex-python-architecture`, `codex-python-tooling`, `codex-python-testing`, `codex-python-logging` | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object`, `lex-logging-decorator` |
| `scripts/` JS | (future `codex-js-architecture` when it emerges) | `lex-frontend-typing` when TS; `lex-logging-decorator` |
| `tools/` (MCP) | `codex-mcp-common`, `codex-python-architecture` when handler is in Python | `lex-mcp`, plus the Python/JS Lexis depending on the handler |
| `SKILL.md` body | `codex-skill-anthropic-agent-skills` | `lex-tone` (direct style, no buzzwords) |

**Principle:** the skill project is a client of the same rules that govern the rest of the platform. There are no parallel "skill rules" that duplicate quality already codified.

### dev → build → dist cycle

```
skills/{slug}/                            # SOURCE (versioned, authoring with Pilars)
       │
       │ consuming project's dev/build/release stack
       ▼
.build/{slug}/                            # INTERMEDIATE (gitignored)
   ├── widgets/    (compiled React)
   ├── scripts/    (locked deps)
   ├── tools/      (validated config)
   ├── references/ (external_refs snapshots)
   ├── SKILL.md    (rewritten paths)
   ├── .skill-manifest.json (with hashes)
   └── {slug}.zip  (testable in another agent)
       │
       │ consuming project's packaging step
       ▼
.dist/{slug}.skill                        # DELIVERY (committed, validated by lex-skill-package-structure)
```

Rules:

- **Source is the truth.** `.build/` and `.dist/` are derivatives; no agent edits these directories manually
- **`.build/` is gitignored.** `.dist/` is committed (consumable by agents that do not have Ahrena)
- **Determinism.** The build MUST produce identical hashes for the same input; lexicographic ordering, no volatile timestamps
- **Snapshots by commit hash.** `.skill-manifest.json` records `source_commit` for each framework ref
- **Build agnostic.** Bundler, runtime, packaging tool, ports — all decided by the consuming project's stack. Ahrena validates only the output shape via `lex-skill-package-structure`.

### Related directives

`.ahrena/.directives` introduces three paths to locate source and outputs:

```yaml
paths:
  skills_root: skills        # source directory of skill projects
  skills_build: .build       # intermediate (gitignored)
  skills_dist: .dist         # final delivery (committed)
```

Projects MAY override (e.g., `skills_root: my-skills/`); agents consult the key instead of assuming the literal.

### Recommended `.gitignore`

`.build/` in the root `.gitignore`; `.dist/` remains versioned:

```
.build/
```

`kata-init-skill` (scope of this PR) ensures the entry exists when initializing the first skill.

## Restrictions

- **A skill is not a framework Pilar.** It does not have a prefix in `framework/`, does not appear in `naming.prefixes`. It is an external project governed by the artifacts of this codex and `lex-skill-project-structure`.
- **Ahrena conventions (`tools/`, `widgets/`) are optional.** Skills MAY exist with only `SKILL.md` + spec-pure `scripts/`/`references/`. The convention applies when the skill needs UI or its own MCP.
- **Single-language per skill.** `metadata.language` declares one language; producing the same skill in pt-BR and en requires two projects `skills/{slug}-ptbr/` and `skills/{slug}-en/` or an internal localization mechanism (not governed in this PR).
- **Directory slug == frontmatter `name`.** The spec requires it; `kata-init-skill` validates it.

## Glossary

| Term | Definition |
|------|------------|
| Skill project | `skills/{slug}/` directory versioned in the Ahrena repository |
| Slug | Project name in kebab-case, identical to the spec's `name` |
| Package | Output in `.dist/{slug}.skill` (Anthropic Agent Skills format) |
| Intermediate build | Output in `.build/{slug}/` (testable on localhost; not delivery) |
| Ahrena convention | Directories and files not defined by the spec (`tools/`, `widgets/`, `.skill-manifest.json`, `skill.config.json`) |
| External ref | Ahrena framework artifact (lex/codex/kata) snapshotted in `references/` at build time |

## References

- `codex-skill-anthropic-agent-skills` — external spec
- `codex-frontend-architecture` — architecture for `widgets/`
- `codex-python-architecture`, `codex-python-tooling` — architecture for Python `scripts/` and `tools/`
- `codex-mcp-common` — MCP patterns used in `tools/`
- `lex-skill-project-structure` — law of the layout
- `lex-directives` — where `skills_root/build/dist` paths are read
- `lex-frontend-*`, `lex-python-*` — quality applicable to artifacts by language
