# Codex: How to Write Good Codex

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creation of Codex (reference manuals)

## Overview

This Codex documents how to structure effective knowledge bases in Ahrena. It covers how to organize domain information, what to include and exclude, and how to keep a Codex up to date over time. It is consulted by `kata-create-codex` during the creation of new Codex. The kata uses this Codex in **Step 1** (reading criteria) and **Step 3** (drafting sections); the kata's **Final Validation** checks the Technical Constraints and Anatomy described below.

## Context

- **Domain:** Design of structured knowledge bases for AI agents
- **Audience:** AI agents executing `kata-create-codex` and framework maintainers
- **Update:** When new quality standards are identified for Codex

## Content

### Principles

1. **Lookup, not reading:** A Codex is designed for targeted lookup, not sequential reading. Each section MUST function independently.
2. **Decision, not information:** The value of a Codex lies in helping the agent make decisions, not in accumulating information. Each section MUST answer "what to do when...".
3. **Currency:** An outdated Codex is worse than no Codex. Each Codex MUST include clear criteria for when it needs updating.
4. **Bounded scope:** A Codex covers one domain. If the scope grows too large, split it into separate Codex.

### Anatomy of a Good Codex

| Section | Purpose | Quality Criteria |
|---------|---------|-----------------|
| **Overview** | Guides whether this is the right Codex to consult | One sentence that delimits the scope |
| **Context** | Domain, audience, and update frequency | Specific and verifiable |
| **Principles** | Fundamentals that guide decisions | Actionable principles, not platitudes |
| **Standards and Conventions** | Practical rules with examples | Table with aspect, standard, and example |
| **Active Decisions** | Current state of technical choices | Traceable (ADR, date, status) |
| **Technical Constraints** | Limits that MUST NOT be exceeded | Concrete and justified |
| **Glossary** | Domain terms | Definitions in the context of this Codex |

### Standards and Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| Granularity | One domain per Codex | `codex-api-patterns` (not `codex-everything-about-backend`) |
| Tone | Technical and direct | Avoid long explanations; prefer tables and lists |
| Examples | Concrete and project-specific | Real code, not generic pseudocode |
| Cross-references | Cite other artifacts by identifier | "Consult `codex-architecture`" |
| Update | Include update trigger in Context | "Update: on each approved ADR" |

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Encyclopedic Codex | Covers everything, impossible to look up | Split into smaller Codex by domain |
| Narrative Codex | Written as an article, not as a reference | Restructure into tables, lists, and independent sections |
| Static Codex | Never updated after creation | Define update trigger in Context |
| Duplicate Codex | Repeats information from another Codex | Reference the other Codex instead of duplicating |
| Opinionated Codex without justification | "Use X because it is better" | Include trade-offs and technical justification |

### Codex vs Other Pilars

| Situation | Correct Pilar | Why |
|-----------|---------------|-----|
| "Never do X" | **Lexis** | Absolute constraint, not a recommendation |
| "When doing X, consider Y and Z" | **Codex** | Domain knowledge for decision-making |
| "To do X, follow these steps" | **Kata** | Procedure, not knowledge |
| "Do X quickly" | **Cry** | Shortcut, not reference |

### Technical Constraints

- The **Overview** section MUST describe the scope in at most two paragraphs
- The **Context** section MUST include **Update** with a concrete trigger (when the Codex needs review)
- **Content** MUST include: Principles, Standards and Conventions, Active Decisions (if applicable), Technical Constraints
- Tables are preferable to long paragraphs for structured information
- The file name MUST use the prefix defined in `naming.prefixes.codex` (consult `.ahrena/.directives`) and kebab-case: `{prefix}-{descriptive-name}.md`
- The structure MUST follow the official template: consult `paths.samples.codex` in `.directives` (e.g. `templates/codex-sample.md`)

## Glossary

| Term | Definition |
|------|------------|
| Domain | Bounded area of knowledge that a Codex covers |
| Targeted lookup | Accessing a specific section to answer a question |
| Cross-reference | Citation of another framework artifact by its identifier |
| Update trigger | Event indicating that the Codex needs review |

## References

- `lex-pilars` — Law that canonically defines the Pilars; Codex as manual consulted, not invoked by Cry
- `codex-pilars` — Pilar system overview and validation checklists (Artifact validation section)
- `lex-directives` — Mandatory consultation of `.ahrena/.directives` (paths, naming.prefixes)
- `lex-template-usage` — Mandatory template usage law
- `kata-create-codex` — Procedure for creating new Codex (consults this Codex in steps 1 and 3)
- `paths.samples.codex` in `.directives` — Path to the official template (e.g. `templates/codex-sample.md`)
