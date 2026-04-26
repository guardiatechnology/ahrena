# Ahrena — Concepts

## The Five Pilars

Ahrena organizes all knowledge and capabilities into five Pilars. Each Pilar has a distinct role, a canonical prefix, and a position in the authority hierarchy.

```
Lexis  (authority)
  └── governs all
Codex  (knowledge)
  └── guides Katas and Warriors
Katas  (execution)
  └── applied by Warriors; invoked by Cries
Warriors  (orchestration)
  └── orchestrate Katas; invoked by Cries
Cries  (entry points)
  └── invoke Katas or Warriors; never Lexis or Codex directly
```

### Lexis

> **"Unbreakable law. Admits no exception."**

| Property | Value |
|---|---|
| Prefix | `lex-` |
| Authority | Highest — governs all other Pilars |
| Can be invoked by | Never invoked directly; consulted by Codex, Katas, Warriors |
| Exceptions | None. A Lexis is absolute. |

A Lexis establishes a rule that every agent, human, and AI must follow in every context. Breaking a Lexis is not a technical issue — it's a governance violation. Examples: `lex-signed-commits`, `lex-issue-driven`, `lex-brand-colors`.

---

### Codex

> **"Reference manual. Organizes knowledge to guide decisions."**

| Property | Value |
|---|---|
| Prefix | `codex-` |
| Authority | Second — source of truth for knowledge |
| Can be invoked by | Consulted by Katas and Warriors; not invoked by Cries |
| Exceptions | N/A — Codex guides, not enforces |

A Codex is a detailed reference document. It explains *how* things work, *why* they're structured a certain way, and *when* to apply different approaches. Examples: `codex-restful-apis`, `codex-python-architecture`, `codex-brand-voice`.

---

### Katas

> **"Repeatable skill. Applies Lexis and consults Codex to execute a clear, reproducible task."**

| Property | Value |
|---|---|
| Prefix | `kata-` |
| Authority | Third — executes by applying Lexis and consulting Codex |
| Can be invoked by | Cries (directly or via Warrior); Warriors |
| Exceptions | N/A |

A Kata is an executable skill — a procedure an agent follows step by step. When invoked, a Kata has a defined input, a sequence of steps, and a defined output. Examples: `kata-contributing-issue`, `kata-api-design-oas`, `kata-quality-gate`.

---

### Warriors

> **"Specialized agent. Orchestrates one or more Katas."**

| Property | Value |
|---|---|
| Prefix | `warrior-` |
| Authority | Fourth — orchestrates Katas; consults Lexis and Codex |
| Can be invoked by | Cries or users |
| Exceptions | N/A |

A Warrior is a specialized AI agent with domain expertise. It selects, sequences, and combines Katas to accomplish complex goals. Warriors are declared with a role, a persona, and a toolset. Examples: `warrior-athena` (workflow), `warrior-apollo` (backend), `warrior-hephaestus` (frontend).

---

### Cries

> **"High-level command. Activates a Kata or Warrior."**

| Property | Value |
|---|---|
| Prefix | `cry-` |
| Authority | Fifth — entry points; invoke Katas or Warriors only |
| Can be invoked by | Users |
| Exceptions | Cries MUST NOT invoke Lexis or access Codex directly |

A Cry is a user-facing command — the `/` commands users type to trigger a capability. A Cry is the entry point into the framework. Examples: `/cry-implement-issue`, `/cry-new-lex`, `/cry-api-design`.

---

## Invocation Rules

```
User
  → invokes → Cry
                → invokes → Kata (one-to-one)
                → invokes → Warrior (one-to-many Katas)
                              → orchestrates → Katas
                                               → apply → Lexis
                                               → consult → Codex
```

**Critical constraint:** A Cry that needs multiple Katas MUST invoke a Warrior that orchestrates them. A Cry must not invoke Katas directly if more than one is needed.

---

## Clades and Subclades

The framework organizes artifacts by **discipline** using a two-level taxonomy:

```
Clade (discipline)
  └── Subclade (area within discipline)
        └── Pilar directory (lexis/ codex/ katas/ warriors/ cries/)
              └── artifacts
```

### Clade `_foundation`

The `_foundation` clade is **transversal** — its rules apply to all other clades. It is prefixed with `_` to sort first alphabetically and signal its cross-cutting nature.

| Subclade | Focus |
|---|---|
| `authoring` | Creating and managing framework artifacts (Lexis, Codex, Katas, Warriors, Cries) |
| `contributing` | Code contribution process — commits, branches, issues, PRs, versioning |
| `i18n` | Framework language structure and navigation |
| `process` | Agent session management — directives, checkpoint, naming conventions |
| `quality` | Cross-cutting quality rules — observability, templates, tone |
| `tooling` | Platform tooling — Makefile, MCP servers, terminal type |

### Clade `design`

| Subclade | Focus |
|---|---|
| `brand` | Guardia brand identity — colors, logo, typography, voice |
| `system` | Product design system — AI-First experience, component library |

### Clade `documentation`

| Subclade | Focus |
|---|---|
| `i18n` | Documentation translation rules and language-specific standards |

### Clade `engineering`

| Subclade | Focus |
|---|---|
| `backend` | Python services — architecture, FastAPI, SQLAlchemy, testing, tooling |
| `data` | Data modeling, schema design, migrations, retention policies |
| `devops` | AWS infrastructure — Well-Architected, IaC, security, cost |
| `frontend` | Web interfaces — React/TypeScript, accessibility, testing, security |
| `mobile` | iOS and Android — React Native/Flutter, offline-first, platform parity |
| `platform` | Guardia platform standards — REST APIs, entities, events, auth, error handling |
| `quality` | Test strategy — pyramid, isolation, coverage |
| `sre` | Site Reliability — SLO, alerting, incident response |
| `workflow` | Development workflow — Issue-Driven Development, Gates, ADRs |

---

## Addressing Taxonomy

Every framework artifact lives at a canonical path:

```
framework/{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md
```

| Segment | Examples |
|---|---|
| `{lang}` | `en`, `pt-BR`, `es` |
| `{clade}` | `_foundation`, `design`, `documentation`, `engineering` |
| `{subclade}` | `authoring`, `contributing`, `backend`, `platform`, ... |
| `{pilar}` | `lexis`, `codex`, `katas`, `warriors`, `cries` |
| `{prefix}-{name}` | `lex-issue-driven`, `codex-restful-apis`, `kata-quality-gate` |

**Example:** The law governing the Issue-Driven workflow lives at:
```
framework/en/engineering/workflow/lexis/lex-issue-driven.md
framework/pt-BR/engineering/workflow/lexis/lex-issue-driven.md
framework/es/engineering/workflow/lexis/lex-issue-driven.md
```

Language is always the first level of navigation. Every artifact must exist in all three languages.

---

## `.ahrena/.directives`

The `.ahrena/.directives` file is the project-level configuration file. It defines:

| Section | Controls |
|---|---|
| `paths` | Canonical paths for framework artifacts, templates, and generated configs |
| `language.default` | Default language for artifact creation (`pt-BR` at Guardia) |
| `language.i18n` | Required language versions (`["pt-BR", "es", "en"]`) |
| `naming.prefixes` | Pilar prefixes (`lex-`, `codex-`, `kata-`, `warrior-`, `cry-`) |
| `naming.casing` | File and directory naming convention (kebab-case) |
| `naming.addressing` | Canonical addressing pattern |
| `naming.reserved_clades` | Special clade names (`_foundation`) |
| `naming.tone_and_writing_style` | Tone and style rules for artifacts and communication |
| `terminal` | Shell type for commands (`bash` or `powershell`) |
| `mcp.servers` | Authorized MCP servers (`github`, `notion`, `figma`) |

Every agent MUST read `.ahrena/.directives` before producing any artifact — enforced by `lex-directives`.
