# Codex: Ahrena Pilar System

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creation and evolution of framework artifacts

## Overview

This Codex is the central reference on the Ahrena Pilar system. It describes the nature of each Pilar, how they relate to each other, and how the framework uses its own artifacts to evolve — the concept of self-sufficiency.

## Context

- **Domain:** Taxonomy and architecture of the Ahrena framework
- **Audience:** AI agents and framework maintainers
- **Update:** Whenever a new Pilar is created or the relationships between Pilars change

## Content

### The Five Pilars

Ahrena organizes all knowledge into five Pilars, each with a distinct role:

| Pilar | Prefix | Nature | Question it answers |
|-------|--------|--------|---------------------|
| **Lexis** | `lex-` | Unbreakable Law | "What is prohibited or required?" |
| **Codex** | `codex-` | Reference Manual | "What do I need to know about this domain?" |
| **Katas** | `kata-` | Repeatable Procedure | "How do I perform this task step by step?" |
| **Warriors** | `warrior-` | Specialized Agent | "Who is responsible for this domain?" |
| **Cries** | `cry-` | Recurring Command | "How do I invoke this action quickly?" |

### Authority Hierarchy

The Pilars have an implicit authority hierarchy:

1. **Lexis** — highest authority. No other artifact can contradict a Lexis. They are absolute.
2. **Codex** — source of truth for domain knowledge. Guides decisions.
3. **Katas** — procedures that obey Lexis and consult Codex.
4. **Warriors** — agents that follow Lexis, consult Codex, and execute Katas.
5. **Cries** — shortcuts that trigger Katas or invoke Warriors.

### Relationships Between Pilars

```
Lexis ─────────── governs ─────────► all others
Codex ─────────── informs ─────────► Katas, Warriors
Katas ─────────── executed by ─────► Warriors, generic agents
Warriors ─────── invoked by ───────► Cries, users
Cries ──────────── triggers ───────► Katas (via Warriors or directly)
```

Each Pilar can reference artifacts from other Pilars:

| Pilar | References | Referenced by |
|-------|------------|---------------|
| Lexis | — | Codex, Katas, Warriors |
| Codex | Lexis | Katas, Warriors |
| Katas | Lexis, Codex | Warriors, Cries |
| Warriors | Lexis, Codex, Katas | Cries |
| Cries | Katas, Warriors | — |

### Creation Kit

For the framework to be self-sufficient, each Pilar has a **Creation Kit** composed of:

| Piece | Pilar | Function |
|-------|-------|----------|
| Pilar Codex | Codex | Knowledge about what it is and how to write it well |
| Creation Kata | Kata | Step-by-step procedure to create a new artifact |
| Invocation Cry | Cry | Quick shortcut to trigger creation |

The execution chain is:

```
/cry-new-{pilar} → kata-create-{pilar} → codex-{pilar} + template + lexis
```

### How to Decide Which Pilar to Use

| Situation | Pilar | Justification |
|-----------|-------|---------------|
| Need to establish an absolute rule that no one can violate | **Lexis** | Laws do not admit exceptions |
| Need to document domain knowledge for reference | **Codex** | Structured knowledge base |
| Need to standardize how a recurring task is performed | **Kata** | Procedure with inputs, steps, and outputs |
| Need a dedicated agent with identity and scope | **Warrior** | Specialist with persona and responsibilities |
| Need a quick shortcut for an everyday action | **Cry** | Quick invocation of 1-2 steps |

Refinement questions:

- **Is it an absolute constraint?** → Lexis
- **Is it knowledge for reference?** → Codex
- **Is it a multi-step procedure?** → Kata
- **Does it need a persona and ongoing scope?** → Warrior
- **Is it a simple and quick invocation?** → Cry

### Standards and Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| File naming | `{prefix}-{name}.md` | `lex-no-secrets.md` |
| Casing | kebab-case | `codex-framework-language.md` |
| Addressing | `{lang}/{clade}/{subclade}/{pilar}/{file}` | `pt-BR/engineering/quality/lexis/lex-code-review.md` |
| Dual creation | framework (`.md`) + IDE (platform format) | `.md` + `.mdc` (Cursor) |

### Technical Constraints

- Every artifact **MUST** follow the official template for its Pilar (`templates/{pilar}-sample.md`)
- Every artifact **MUST** exist in the languages defined in `language.i18n`
- The default language (`language.default`) is the source of truth
- File names use the Pilar prefix and kebab-case
- Canonical terms (Lexis, Codex, Katas, Warriors, Cries, Clade, Subclade, Pilar) are never translated

### Project Artifacts (.ahrena)

Artifacts can be created first in the **project space** (`.ahrena/artifacts/`), specific to that repository. This allows iteration and validation before incorporating them into the canonical framework.

| Aspect | Project (`.ahrena/artifacts/`) | Framework (`framework/`) |
|--------|--------------------------------|---------------------------|
| **Use** | Project-specific; local validation | Part of the Ahrena repository; shared |
| **Structure** | Same as framework: `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md` | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| **Languages** | May exist only in the default language; on Push, others are generated if missing | **MUST** exist in all languages in `language.i18n` |
| **When to create here** | Rules or procedures still under validation; artifacts that may never go to the framework | Stable, approved artifacts for the framework |

**Recommended flow:**

1. **Create in project:** use the creation Katas (`kata-create-lexis`, `kata-create-codex`, etc.) with destination **project** — the artifact is saved under `.ahrena/artifacts/{lang}/{clade}/{subclade}/{pilar}/`.
2. **Sync .cursor local:** run `python .ahrena/update.py --sync-cursor` (or `make sync-cursor`). The update regenerates `.cursor/` from `.ahrena/framework/` and `.ahrena/artifacts/`.
3. **Validate and compare (optional):** use `kata-diff-artifacts --local` to see differences between `.ahrena/artifacts` and local `framework/`; use `kata-diff-artifacts --remote` to compare with the latest version of the framework on the remote.
4. **Push to framework:** run `kata-push-to-framework` (or `cry-push-to-framework`) with **--local** (copy to `framework/` in the current repo) or **--remote** (sync with the framework repository on GitHub).
5. **Update installation:** run `python .ahrena/update.py` (and optionally `--sync-cursor`) to bring in the latest version of the framework.

**Push: local and remote mode**

- **Local:** the current repo contains (or has access to) the `framework/` folder. Push = copy `.ahrena/artifacts/` to `paths.framework`, complete i18n, and optionally remove from the project. No network use.
- **Remote:** in a consumer project, the framework lives on GitHub. Push = send changes to the framework repository using the **GitHub MCP** (branch, push, open PR). The agent **MUST** use the GitHub MCP tools for all remote operations.

The canonical path for the project space is defined in `paths.project_artifacts` in `.ahrena/.directives` (default value: `.ahrena/artifacts/`).

## Glossary

| Term | Definition |
|------|------------|
| Pilar | One of the five artifact categories in Ahrena |
| Clade | First level of thematic organization (e.g., engineering, documentation) |
| Subclade | Second level of organization within a Clade (e.g., quality, i18n) |
| Creation Kit | The Codex + Kata + Cry set that enables creating new artifacts for a Pilar |
| Dual creation | Pattern of creating the canonical artifact (`.md`) and the derived version for the IDE |
| Addressing | Full path of an artifact within the framework taxonomy |
| Project artifacts | Artifacts created in `.ahrena/artifacts/`, repository-specific, before being incorporated into the framework |
| Push to framework | Procedure (kata-push-to-framework) that incorporates artifacts from `.ahrena/artifacts/` into the framework, in **local** mode (copy to `framework/` in the repo) or **remote** mode (sync with the framework repository on GitHub). |
| Diff artifacts | Procedure (kata-diff-artifacts) that compares `.ahrena/artifacts` and the framework in **local** mode (vs local framework) or **remote** mode (vs latest version of the framework on the remote). |

## References

- `.ahrena/.directives` — Canonical framework directives
- `lex-template-usage` — Mandatory template usage law
- `lex-framework-language` — Language structure law
- `codex-lexis`, `codex-codex`, `codex-katas`, `codex-warriors`, `codex-cries` — Individual Codex for each Pilar
