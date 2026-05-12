# Lexis: Mandatory Structure of a Skill Project

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Skill projects versioned in the Ahrena repository (source under `skills/{slug}/`, intermediates under `.build/`, deliveries under `.dist/`)

## Law

> **Every skill project MUST reside in `{paths.skills_root}/{slug}/` (default `skills/{slug}/`) with the canonical layout defined in `codex-skill-project-architecture`: `SKILL.md` and `skill.config.json` MUST exist at the root; `{slug}` MUST be valid kebab-case per the Anthropic Agent Skills spec and identical to the `name` field in the `SKILL.md` frontmatter; physical separation MUST hold between source (`{paths.skills_root}/`), intermediates (`{paths.skills_build}/`, gitignored), and deliveries (`{paths.skills_dist}/`, committed); the project content MUST respect every quality Lexis applicable to each artifact's type (widgets → `lex-frontend-*`; Python scripts/tools → `lex-python-*`; cross-language logging → `lex-logging-decorator`; MCP → `lex-mcp`). Editing artifacts directly under `{paths.skills_build}/` or `{paths.skills_dist}/` is FORBIDDEN — those directories are derived; changes flow through the source.**

## Coverage

- **Applies to:** every skill project maintained in the Ahrena repository, in any language declared in `metadata.language`
- **Bound agents:** `kata-init-skill` (scaffold), `cry-new-skill` (shortcut), `warrior-claudionor` (end-to-end orchestration of the `implement → validate → package` cycle), `kata-skill-validate` (deterministic validation of this Lex), `warrior-hephaestus` (widgets), `warrior-apollo` (Python scripts/tools), and any agent that edits the project during the dev → build → dist cycle
- **Exceptions:** None. Lexis admit no exceptions. Experimental or test skills follow the same layout — ad-hoc exploration directories outside `paths.skills_root` are not skill projects and are not governed by this Lex

## Rules

### 1. Location and naming

- Project root directory: `{paths.skills_root}/{slug}/` (default `skills/{slug}/`)
- `{slug}`: 1-64 chars, only `a-z`, `0-9`, and hyphen; cannot start or end with hyphen; no consecutive `--` (per Anthropic spec — `codex-skill-anthropic-agent-skills`)
- `{slug}` MUST be **identical** to the `name` value in the `SKILL.md` frontmatter
- Reserved words from Anthropic documentation (`anthropic`, `claude`) MUST NOT be used

### 2. Required files at the project root

| File | Role |
|------|------|
| `SKILL.md` | Anthropic Agent Skills frontmatter + Markdown body |
| `skill.config.json` | Local project configuration (language, runtimes, dev server ports, external refs to snapshot) |

A `.skill-manifest.json` skeleton MUST exist after scaffold but is **written** only by the build. In PR 1 the skeleton holds `schema_version` and empty fields.

### 3. Optional subdirectories

Allowed in the source project per `codex-skill-project-architecture`:

- `references/` — additional Markdown (level 3 of the spec)
- `scripts/` — JS or Python executable code invoked by the agent
- `tools/` — MCP tools owned by the skill (Ahrena convention)
- `widgets/` — React components (Ahrena convention)
- `assets/` — static resources from the spec

Subdirectories outside this list require explicit justification in `SKILL.md` or `skill.config.json` (e.g., a `metadata.notes` field). Editors do not introduce new top-level directories without justification.

### 4. Source / intermediate / delivery separation

| Type | Default path | Versioned | Writer |
|------|--------------|:---------:|--------|
| Source | `skills/{slug}/` | Yes | Author (human or agent, during authoring) |
| Intermediate | `.build/{slug}/` | **No** (in `.gitignore`) | Build (consuming project's stack) |
| Delivery | `.dist/{slug}.skill` | Yes | Packaging (consuming project's stack) |

Editing `.build/` or `.dist/` manually breaks build determinism and auditability. **Changes flow through the source**, always.

### 5. Conformance with applicable Pillars and Lexis

The project content **inherits** the quality Lexis already codified in the framework:

| Skill content | Applicable quality Lexis and codex |
|---------------|------------------------------------|
| `widgets/` (React/TS) | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` (when rendered on Guardia surfaces), `codex-frontend-architecture` |
| `scripts/` Python | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object`, `codex-python-architecture`, `codex-python-tooling` |
| `scripts/` JS/TS | `lex-frontend-typing` (when TS), idiomatic error handling |
| `tools/` MCP | `lex-mcp`, `codex-mcp-common`, plus the language Lexis of the handler |
| Logging in any language | `lex-logging-decorator` |
| Text in `SKILL.md` and `references/` | `lex-tone` |
| Skill used as tooling for an agent PoV | `lex-agent-construction-directives` (Directive 03 — Concrete Tools at pre-operational rigor; `stage: pre-operational` declared in the consuming PoV's system prompt) |

Violating a quality Lexis inside a skill project is a direct violation — there is no "skill mode" that loosens an existing rule.

**Note on skills consumed by an agent PoV:** when the skill is the implementation artifact of a `warrior-claudionor` PoV (`cry-pov --kind skill`), the consumer — not the skill itself — declares `stage: pre-operational` in the PoV's system prompt (`docs/{context}/agents-pov/system-prompt.md`), per `lex-agent-construction-directives`. The skill as a distributable artifact remains governed solely by this Lexis.

### 6. Minimum `.gitignore`

A repository hosting skill projects **must** have `.build/` in `.gitignore` (root or equivalent path when `paths.skills_build` is overridden).

`.dist/` **does not** go into `.gitignore` — it is a versioned deliverable.

`kata-init-skill` ensures the entry exists when the first project is created.

## Consequences of Violation

1. **Review block:** a PR containing a project outside the layout (slug failing the regex, missing `SKILL.md`, missing `skill.config.json`, direct edits in `.build/`/`.dist/`) is rejected by the reviewer (human or Gate 2 once `kata-quality-gate` integrates the check).
2. **Alert:** divergence between the directory `slug` and the frontmatter `name` detected by `kata-init-skill` or by the build → immediate error with correction guidance.
3. **Remediation:** move files to `skills/{slug}/`, create the missing required files, rename directory/`name` to match, or discard changes in `.build/`/`.dist/` and redo through the source.

## Examples

### Correct

```
skills/scheduled-payments-skill/
├── SKILL.md                    # frontmatter with name: scheduled-payments-skill
├── skill.config.json
├── .skill-manifest.json        # skeleton
├── widgets/
│   ├── package.json
│   └── src/transfer-form/index.tsx
└── scripts/
    └── src/validate_amount.py

.build/                         # gitignored
.dist/                          # committed
```

```yaml
# SKILL.md
---
name: scheduled-payments-skill   # identical to the directory
description: Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer.
license: Apache-2.0
metadata:
  version: "0.1.0"
  language: en
---
```

### Incorrect

```
my-skills/payments/              # ❌ outside paths.skills_root with no override declared
skills/Payments_Skill/           # ❌ slug with underscore and uppercase
skills/payments-skill/SKILL.md   # ❌ frontmatter with name: payments (does not match the directory)
.build/payments-skill/widgets/   # ❌ direct edit in the intermediate
.dist/payments-skill.skill/      # ❌ direct edit in the delivery
```

```
skills/payments-skill/
├── SKILL.md
└── widgets/src/Form.jsx         # ❌ TS strict not applied; violates lex-frontend-typing
                                 # even inside a skill project, lex-frontend-* still applies
```

## Automated Validation

- **Tool:**
  - `kata-init-skill` validates slug, frontmatter, and required-file presence at creation
  - `kata-skill-validate` (via `scripts/skills/validate.py`) runs the deterministic check of this Lex — invoked by `warrior-claudionor` and by `cry-skill --mode validate`
  - PR review (human) checks the layout while `kata-quality-gate` does not integrate the check
  - Generic existing lint detects violations of `lex-frontend-*` / `lex-python-*` inside the project, no new rule needed
  - Root `.gitignore` contains `.build/` (verifiable by inspection)
- **When:** scaffold (`kata-init-skill`); on each edit (`kata-skill-validate`); PR review; future Gate 2 integration
- **Metric:** 0 skill projects with `name` diverging from slug; 0 commits editing `.build/` or `.dist/` directly; 100% of projects with `SKILL.md` + `skill.config.json` at the root

## References

- `codex-skill-project-architecture` — full layout and the role of each subdirectory
- `codex-skill-anthropic-agent-skills` — spec constraints on `name` and structure
- `lex-directives` — reading of `paths.skills_root/build/dist`
- `lex-template-usage` — mandatory template usage when creating `SKILL.md` and `skill.config.json`
- `lex-frontend-*`, `lex-python-*`, `lex-mcp`, `lex-logging-decorator`, `lex-tone` — quality Lexis inherited by the project content
- `warrior-claudionor`, `kata-skill-validate` — orchestrator and validator that give operational voice to this Lex
- `scripts/skills/validate.py` — deterministic implementation used by `kata-skill-validate`
