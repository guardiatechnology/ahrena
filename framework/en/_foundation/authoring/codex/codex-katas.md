# Codex: How to Write Good Katas

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creation of Katas (repeatable procedures)

## Overview

This Codex documents how to design effective structured procedures in Ahrena. It covers task decomposition, input and output design, validation criteria, and when to use a Kata vs a Cry. It is consulted by `kata-create-kata` during the creation of new Katas. The kata uses this Codex in **Step 1** (reading criteria) and **Step 3** (drafting sections); the kata's **Final Validation** checks the Technical Constraints and Anatomy described below.

## Context

- **Domain:** Design of standardized procedures for AI agents
- **Audience:** AI agents executing `kata-create-kata` and framework maintainers
- **Update:** When new quality standards are identified for Katas

## Content

### Principles

1. **Reproducibility:** Two agents executing the same Kata with the same inputs MUST produce equivalent outputs.
2. **Progressiveness:** Each step MUST be verifiable before advancing to the next. If a step fails, it MUST be possible to correct without restarting from scratch.
3. **Completeness:** The Kata MUST cover the entire flow — from input to validated output. It MUST NOT depend on implicit knowledge.
4. **Step atomicity:** Each step performs a single well-defined action. If a step does two things, split it.

### Anatomy of a Good Kata

| Section | Purpose | Quality Criteria |
|---------|---------|-----------------|
| **Objective** | What this procedure produces | One clear sentence about the output |
| **When to Use** | Activation conditions | List of specific triggers |
| **Inputs** | What the agent needs to receive | Table with name, requirement status, and description |
| **Workflow** | Numbered steps with checklist | Each step with detailed sub-actions |
| **Outputs** | What is produced | Table with format and destination |
| **Constraints** | What the Kata cannot do | List of explicit limits |

### Input Design

Best practices for defining inputs:

| Practice | Example |
|----------|---------|
| Distinguish required vs optional | "Source file (Yes) / Target language (No)" |
| Define defaults for optionals | "If omitted, translate to all languages in `language.i18n`" |
| Specify expected format | "BCP 47 code (e.g., pt-BR, en, es)" |
| Validate inputs in the first step | "Confirm that the file exists and is .md" |

### Workflow Design

Each workflow step MUST follow this structure:

1. **Descriptive name** — what this step does (e.g., "Read Directives")
2. **Numbered sub-actions** — specific instructions (1. Read X, 2. Verify Y)
3. **Checkpoint** — how to confirm the step completed successfully

The progress checklist at the beginning of the workflow enables execution tracking:

```
Progress:
- [ ] 1. Step 1 name
- [ ] 2. Step 2 name
- [ ] 3. Final validation
```

### Validation Design

Final validation is the last step of every Kata. It MUST include:

- Checklist of verifiable criteria (checkboxes)
- Criteria for both form (structure, formatting) and content (completeness, correctness)
- Reference to the Lexis that MUST be obeyed

### Standards and Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| Number of steps | 4-8 (ideal) | Fewer than 4: it might be a Cry. More than 8: decompose |
| References | Cite consulted artifacts | "Consult `codex-lexis` for quality criteria" |
| Examples | Include sample input and output | Code block with real data |
| Idempotency | Executing the Kata twice MUST NOT generate duplicates | Check existence before creating |

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Overly generic Kata | "Create documentation" — no specificity | Narrow the scope: "Create an ADR" |
| Vague steps | "Analyze the code" — how? | Detail specific sub-actions |
| No validation | Output is not verified | Always include a final validation step |
| Implicit inputs | The Kata assumes undeclared context | Declare every input in the table |
| Circular dependency | Kata A needs Kata B which needs Kata A | Refactor to eliminate the cycle |

### Kata vs Cry — When to Use Each

| Characteristic | Kata | Cry |
|---------------|------|-----|
| Complexity | Multiple steps (4-8) | 1-2 steps |
| Inputs | Several, with validation | Few, simple |
| Configures agent? | Yes (defines behavior) | No (only invokes) |
| Output | Structured and validated | Quick and direct |
| Example | Create a complete ADR | Generate changelog |

### Technical Constraints

- Every Kata MUST have a **progress checklist** at the beginning of the Workflow (checkboxes `- [ ]` per step)
- The **last step** of the Workflow MUST be "Final Validation" (or equivalent) and contain verifiable checkboxes
- The file name MUST use the prefix defined in `naming.prefixes.katas` (consult `.ahrena/.directives`) and kebab-case: `{prefix}-{descriptive-name}.md`
- The structure MUST follow the official template: consult `paths.samples.katas` in `.directives` (e.g. `templates/kata-sample.md`)
- Required inputs MUST be validated in the first step

## Glossary

| Term | Definition |
|------|------------|
| Reproducibility | Ability to obtain the same result across different executions |
| Checkpoint | Verification at the end of a step that confirms success |
| Idempotency | Property of producing the same result even when executed multiple times |
| Decomposition | Division of a complex task into atomic steps |

## References

- `lex-pilars` — Law that canonically defines the Pilars; Kata applies Lexis and consults Codex
- `codex-pilars` — Pilar system overview and validation checklists (Artifact validation section)
- `lex-directives` — Mandatory consultation of `.ahrena/.directives` (paths, naming.prefixes)
- `codex-cries` — Manual on Cries (to understand the Kata vs Cry difference)
- `lex-template-usage` — Mandatory template usage law
- `kata-create-kata` — Procedure for creating new Katas (consults this Codex in steps 1 and 3)
- `paths.samples.katas` in `.directives` — Path to the official template (e.g. `templates/kata-sample.md`)
