# Codex: How to Write Good Cries

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creation of Cries (recurring commands)

## Overview

This Codex documents how to design effective recurring commands in Ahrena. It covers when to create a Cry vs using a Kata directly, prompt template design, parameters, and the Cry → Kata/Warrior chain. It is consulted by `kata-create-cry` during the creation of new Cries. The kata uses this Codex in **Step 1** (reading criteria) and **Step 3** (drafting sections); the kata's **Final Validation** checks the Technical Constraints and Anatomy described below.

## Context

- **Domain:** Design of productivity commands for AI agents
- **Audience:** AI agents executing `kata-create-cry` and framework maintainers
- **Update:** When new quality standards are identified for Cries

## Content

### Principles

1. **Speed:** A Cry exists to save time. If the invocation is as complex as executing the Kata directly, the Cry has no value.
2. **Delegation:** The Cry does not contain its own logic — it delegates to a Kata (optionally via a Warrior). The Cry is the entry point, not the procedure.
3. **Minimal parameters:** The Cry MUST require the minimum information from the user, using smart defaults from `.directives` for the rest.
4. **Predictability:** The same Cry with the same parameters MUST produce the same result.
5. **Invocation rule (unbreakable):** The Cry **MUST NOT** invoke Lexis. The Cry **MUST NOT** access Codex directly. The Cry invokes **ONLY** Katas and/or Warriors. Consultation of Lexis and Codex is done by the invoked Kata or Warrior, never by the Cry as a direct action.
6. **No external commands without Kata:** The Cry **MUST NOT** define or prescribe as the main procedure the execution of external commands (e.g. `git`, `make`, `npm`, `pnpm`, `python`, shell scripts) unless a **Kata** exists that encapsulates that procedure and that the Cry invokes. If the command flow involves running external tools, a Kata (e.g. `kata-sync`, `kata-rebase`) MUST exist that describes the steps, and the Cry only invokes that Kata (or a Warrior that orchestrates it). A Cry that describes "run git X, then Y" in the artifact body without invoking an existing Kata is non-compliant — the procedure MUST be in the Kata; the Cry is only the invocation shortcut.

### Anatomy of a Good Cry

| Section | Purpose | Quality Criteria |
|---------|---------|-----------------|
| **Description** | What the command does in one sentence | Clear and direct |
| **Usage** | Invocation syntax | Format: `/cry-name <required> [optional]` |
| **Parameters** | Argument table | Name, requirement status, description, and example |
| **What the Command Does** | Numbered list of actions | 3-6 high-level steps |
| **Prompt Template** | Instructions sent to the agent | Context + Task + Output format |
| **Invocation Example** | Concrete input and output | Demonstrates real usage |
| **Difference from Kata** | Comparative table | Cry vs Kata for this case |

### Parameter Design

| Practice | Example |
|----------|---------|
| Minimum required parameters | Only the essentials that cannot have a default |
| Smart defaults | Languages come from `.directives`, not from the user |
| Explicit format | "BCP 47 code" is clearer than "language" |
| Consistency with other Cries | Same naming pattern and order |

### Prompt Template Design

The prompt template is the functional core of the Cry. Recommended structure:

```
Context:
- {{parameter1}}
- {{parameter2}}

Task:
[Clear instruction of what to do, referencing Kata and/or Warrior]

Output format:
[How the result should be presented]
```

Best practices:
- Reference the Kata to execute by name
- If there is a Warrior, instruct the agent to assume the role
- Define the output format explicitly
- Use variables with `{{double braces}}` for parameters

### Invocation Chain

A Cry can follow two patterns:

**Pattern 1: Cry → Kata (direct)**
```
/cry-new-lex "code review" → kata-create-lexis
```
Use when there is no dedicated Warrior for the domain.

**Pattern 2: Cry → Warrior → Kata**
```
/cry-translate file.md → warrior-translator → kata-translate
```
Use when a Warrior exists that adds persona and context.

### Standards and Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| Naming | `cry-{verb}-{noun}` or `cry-new-{pilar}` | `cry-translate`, `cry-new-lex` |
| Syntax | `/cry-name <required> [optional]` | `/cry-translate <file> [language]` |
| Positional parameters | Required first, optional after | `<file> [language] [--flag]` |
| Flags | Prefixed with `--` | `--order en,es` |

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Complex Cry | Too many required parameters | Reduce to 1-2 required, use defaults |
| Cry without Kata | All logic in the prompt template | Extract procedure into a Kata |
| Cry with external commands without Kata | Cry describes "run git X", "run make Y" without invoking a Kata that encapsulates the flow | Create the Kata (e.g. kata-sync, kata-rebase) and have the Cry invoke it; the Cry MUST NOT be the only place where the procedure is defined |
| Redundant Cry | Duplicates another existing Cry | Check existing Cries before creating |
| Vague prompt | "Do something with the file" | Reference specific Kata and output format |
| No example | User does not know how to use it | Always include an example with input and output |

### Cry vs Kata — When to Create Each

| Characteristic | Cry | Kata |
|---------------|-----|------|
| Entry point | User invokes directly | Agent executes internally |
| Complexity | Simple invocation (1 command) | Multi-step procedure |
| Parameters | From user (CLI-like) | Validated and processed |
| Contains logic? | No — delegates to Kata | Yes — defines the steps |
| Analogy | Shell command | Script called by the command |

### Technical Constraints

- Every Cry MUST **reference and invoke at least one Kata** (or Warrior that orchestrates a Kata) that exists and executes the procedure — Cry has no logic of its own. **Violation:** Cry that describes steps with external commands (git, make, etc.) without invoking a Kata that encapsulates those steps; Cry with "Associated Kata: kata-X — Pending creation" remains non-compliant until the Kata exists and the Cry invokes it.
- Every Cry that involves execution of external tools (git, make, npm, etc.) **MUST** invoke a Kata that documents and executes that flow; the Cry MUST NOT be the only place where the procedure is defined.
- The **Prompt Template** section MUST use `{{variables}}` for parameters and explicitly reference the Kata (and Warrior, if any)
- The file name MUST use the prefix defined in `naming.prefixes.cries` (consult `.ahrena/.directives`) and kebab-case: `{prefix}-{descriptive-name}.md`
- The structure MUST follow the official template: consult `paths.samples.cries` in `.directives` (e.g. `templates/cry-sample.md`)
- The **Difference from Kata** section (or equivalent) MUST contain a comparative Cry vs Kata table for this command

## Glossary

| Term | Definition |
|------|------------|
| Prompt template | Parameterized text sent to the agent when the Cry is invoked |
| Smart default | Default value derived from `.directives` or context |
| Invocation chain | Cry → (Warrior) → Kata sequence that defines the execution flow |
| Positional parameter | Argument identified by position, not by name |

## References

- `lex-pilars` — Law that canonically defines the Pilars; Cry invokes only Kata(s) and/or Warrior(s), never Lexis nor Codex
- `codex-pilars` — Pilar system overview and validation checklists (Artifact validation section)
- `lex-directives` — Mandatory consultation of `.ahrena/.directives` (paths, naming.prefixes)
- `codex-katas` — Manual on Katas (to understand the Cry vs Kata difference)
- `lex-template-usage` — Mandatory template usage law
- `kata-create-cry` — Procedure for creating new Cries (consults this Codex in steps 1 and 3)
- `paths.samples.cries` in `.directives` — Path to the official template (e.g. `templates/cry-sample.md`)
