# Codex: How to Write Good Lexis

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creation of Lexis (unbreakable laws)

## Overview

This Codex documents what makes a Lexis effective: how to write a clear law, how to define testable scope, and how to ensure the law is enforceable in practice. It is consulted by `kata-create-lexis` during the creation of new Lexis. The kata uses this Codex in **Step 1** (reading quality criteria) and **Step 3** (drafting sections); the kata's **Final Validation** checks the Technical Constraints and Anatomy described below.

## Context

- **Domain:** Design of unbreakable laws for agent and process governance
- **Audience:** AI agents executing `kata-create-lexis` and framework maintainers
- **Update:** When new quality standards are identified for Lexis

## Content

### Principles

1. **Unambiguity:** A Lexis MUST have a single possible interpretation. If two people can read the law and reach different conclusions, it needs rewriting.
2. **Testability:** It MUST be possible to verify automatically whether the law is being followed. If it cannot be tested, it is not a good Lexis.
3. **Necessity:** Each Lexis MUST solve a real problem. Unnecessary laws create bureaucracy without value.
4. **Immutability:** Lexis do not admit exceptions. If the law needs exceptions, it should probably be a Codex (recommendation) instead of a Lexis (obligation).

### Anatomy of a Good Lexis

| Section | Purpose | Quality Criteria |
|---------|---------|-----------------|
| **Purpose** | Explains why the law exists | MUST connect the law to a real risk or problem |
| **Law** | Imperative statement of the rule | One sentence, clear, unambiguous, using "MUST" or "MUST NOT" |
| **Scope** | Defines where and to whom it applies | Specific enough to leave no doubt |
| **Consequences** | What happens if violated | Concrete actions (block, alert, remediation) |
| **Examples** | Correct vs incorrect | Real cases, not hypothetical |
| **Validation** | How to verify compliance | Specific tool, timing, and metric |

### How to Write the Law Statement

The law statement is the heart of a Lexis. It MUST be:

**Good statement:**
> "Every PR MUST have at least one approved reviewer before merge."

- Clear subject (every PR)
- Imperative verb (MUST)
- Specific action (have approved reviewer)
- Temporal condition (before merge)

**Bad statement:**
> "Code reviews are important and should be done when possible."

- No specific subject
- "When possible" creates a loophole
- "Are important" is an opinion, not a law

### Standards and Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| Imperative verbs | MUST, MUST NOT | "Every agent MUST consult the .directives" |
| Exceptions | None — Lexis are absolute | "Exceptions: None. Lexis do not admit exceptions." |
| Scope | Always explicit | "Applies to: all repositories" |
| Validation | Always automatable | "Tool: gitleaks; Timing: pre-commit" |

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Vague law | "Code should be high quality" — what is quality? | Define measurable criteria |
| Infeasible law | "Test coverage must be 100%" — unrealistic in many contexts | Calibrate with project reality |
| Redundant law | Repeats what another Lexis already covers | Check existing Lexis before creating |
| Opinionated law | "Use TypeScript" — a preference, not security/quality | Move to Codex as a recommendation |
| Embedded exception | "Except when approved by the Tech Lead" — invalidates the law | If it needs an exception, it is not a Lexis |

### Lexis vs Codex — When to Use Each

| Characteristic | Lexis | Codex |
|---------------|-------|-------|
| Nature | Required | Recommended |
| Exceptions | Never | May have |
| Verification | Automated | Manual or automated |
| Example | "No secrets in repositories" | "Prefer PostgreSQL for transactional data" |

### Technical Constraints

- The **Law** section MUST contain exactly one imperative statement in a blockquote (`> **[statement]**`)
- The **Scope** section MUST include "Exceptions: None" (or equivalent) — Lexis do not admit exceptions
- The **Automated Validation** section MUST specify tool, timing, and metric
- The file name MUST use the prefix defined in `naming.prefixes.lexis` (consult `.ahrena/.directives`) and kebab-case: `{prefix}-{descriptive-name}.md`
- The structure MUST follow the official template: consult `paths.samples.lexis` in `.directives` (e.g. `templates/lex-sample.md`)

## Glossary

| Term | Definition |
|------|------------|
| Law statement | Imperative sentence that defines the absolute rule |
| Unambiguity | Property of having a single interpretation |
| Testability | Ability to verify compliance automatically |
| Automated validation | Technical mechanism that verifies law compliance |

## References

- `lex-pilars` — Law that canonically defines the Pilars; Lexis as unbreakable law
- `codex-pilars` — Pilar system overview and validation checklists (Artifact validation section)
- `lex-directives` — Mandatory consultation of `.ahrena/.directives` (paths, naming.prefixes)
- `lex-template-usage` — Mandatory template usage law
- `kata-create-lexis` — Procedure for creating new Lexis (consults this Codex in steps 1 and 3)
- `paths.samples.lexis` in `.directives` — Path to the official template (e.g. `templates/lex-sample.md`)
