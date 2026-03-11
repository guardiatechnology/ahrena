# Lexis: Mandatory Use of Templates

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Creation of any Ahrena artifact

## Purpose

Ahrena maintains official templates (samples) for each Pilar of the taxonomy — Lexis, Codex, Katas, Warriors, and Cries. These templates ensure structural consistency, completeness of information, and standardization across all framework artifacts.

Without this standardization, agents may produce artifacts with missing sections, inconsistent structure, or divergent naming, compromising interoperability and system governance.

This Lexis exists to ensure that **every new artifact is created from the corresponding official template**, preserving the structural integrity of the framework.

## Law

> **Every agent MUST use the official template (sample) of the corresponding Pilar as the structural base when creating any new Ahrena artifact — Lexis, Codex, Kata, Warrior, or Cry.**

## Rules

### 1. Mandatory template per Pilar

Before creating a new artifact, the agent **MUST** consult the template (sample) for the corresponding Pilar. Canonical paths are in `.ahrena/.directives` under the `paths.samples` section (e.g. `paths.samples.lexis`, `paths.samples.codex`). Typical values in the Ahrena repository:

| Pilar | Template (paths.samples in .directives) | Template (.cursor/) |
|-------|----------------------------------------|---------------------|
| **Lexis** | `templates/lex-sample.md` | `.cursor/rules/samples/lex-sample.mdc` |
| **Codex** | `templates/codex-sample.md` | `.cursor/rules/samples/codex-sample.mdc` |
| **Katas** | `templates/kata-sample.md` | `.cursor/skills/samples/kata-sample.mdc` |
| **Warriors** | `templates/warrior-sample.md` | `.cursor/agents/warrior-sample.md` |
| **Cries** | `templates/cry-sample.md` | `.cursor/commands/samples/cry-sample.mdc` |

The agent **MUST** use the `paths.samples` values from `.directives` when available; the table above reflects the default convention.

### 2. Creation process

When receiving a request to create a new artifact, the agent **MUST**:

1. **Identify the Pilar** — determine whether the artifact is a Lexis, Codex, Kata, Warrior, or Cry.
2. **Read the template** — load the content of the corresponding sample using the table above.
3. **Use as structural base** — create the new artifact keeping all sections, headings, and structure of the template.
4. **Fill in the fields** — replace the fields in square brackets `[]` with the artifact-specific content.
5. **Remove template instructions** — remove generic explanatory text from the sample (e.g. "Describe why this law exists") and replace it with real content.
6. **Respect addressing** — save to the correct path per the taxonomy: `<clade>/<subclade>/<pilar>/<prefix>-<name>.md`.

### 3. Inviolable structure

The agent **MUST NOT**:

- Omit mandatory sections defined in the template.
- Invent its own structure ignoring the template.
- Change the template’s standard headings (it may add sub-sections, never remove existing ones).

### 4. Dual creation (framework + IDE)

When the context requires it, the agent **MUST** create the artifact in both places:

- **`framework/`** — canonical version in plain `.md`, without IDE frontmatter.
- **`.cursor/`** (or other IDE) — derived version in `.mdc` with appropriate YAML frontmatter.

### 5. Mandatory frontmatter in `.cursor/`

When creating the `.mdc` version for Cursor, the agent **MUST** include the correct YAML frontmatter at the start of the file, delimited by `---`. The frontmatter varies by Cursor resource:

#### Rules (Lexis and Codex)

```yaml
---
description: "Concise description of what the rule does and when it should be consulted."
globs: "glob/pattern/if/applicable"
alwaysApply: false
---
```

| Field | Required | Description |
|-------|:--------:|-------------|
| `description` | Yes | Text Cursor shows so the agent knows when to consult this rule |
| `globs` | Conditional | Glob pattern of files the rule applies to. **Omit or leave empty** when the rule applies to all files or is not tied to specific file types |
| `alwaysApply` | Yes | `true` if the rule must be loaded on every interaction; `false` if activated on demand or by glob |

#### Skills (Katas and Warriors)

```yaml
---
name: prefix-name
description: "Concise description of what the skill does and when to use it."
---
```

| Field | Required | Description |
|-------|:--------:|-------------|
| `name` | Yes | Skill identifier, using the Pilar prefix (e.g. `kata-code-review`, `warrior-spartacus`) |
| `description` | Yes | Text Cursor shows so the agent knows when to activate this skill |

#### Commands (Cries)

```yaml
---
description: "Concise description of what the command does when invoked."
---
```

| Field | Required | Description |
|-------|:--------:|-------------|
| `description` | Yes | Text Cursor shows so the user understands what the command does |

### 6. Mandatory prefix

Every artifact **MUST** use the correct prefix of its Pilar in the file name:

| Pilar | Prefix | Example |
|-------|--------|---------|
| Lexis | `lex-` | `lex-no-secrets.md` |
| Codex | `codex-` | `codex-architecture.md` |
| Katas | `kata-` | `kata-code-review.md` |
| Warriors | `warrior-` | `warrior-spartacus.md` |
| Cries | `cry-` | `cry-changelog.md` |

## Scope

- **Applies to:** creation of any artifact in any Clade and Subclade
- **Bound agents:** all Warriors and generic agents
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **Artifact rejection:** artifacts created without following the official template must be rewritten before being accepted.
2. **Structural inconsistency:** artifacts that do not follow the standard compromise navigability and framework governance.
3. **Remediation:** the agent must recreate the artifact using the correct template, preserving the content already produced but fitting it to the standard structure.

## Examples

### Correct

```
User: Create a new Lexis about mandatory code review.

Agent:
1. Identifies Pilar: Lexis
2. Reads template: framework/lexis/lex-sample.md
3. Creates artifact following the structure:
   - # Lexis: Mandatory Code Review
   - > Prefix: lex- | Type: Unbreakable Law | Scope: ...
   - ## Purpose
   - ## Law
   - ## Scope
   - ## Consequences of Violation
   - ## Examples
   - ## Automated Validation
4. Saves to: engineering/quality/lexis/lex-code-review.md
5. Creates .cursor version with frontmatter:
   ---
   description: "Mandatory code review. Every PR must be reviewed before merge."
   alwaysApply: false
   ---
6. Saves to: .cursor/rules/engineering/quality/lex-code-review.mdc
```

### Incorrect

```
User: Create a new Lexis about mandatory code review.

Agent: Here is the law:

# Code Review Law
Every PR needs review.

# ❌ The agent ignored the template, created its own structure,
# omitted mandatory sections, and did not use the correct prefix.
# The .mdc version was created without YAML frontmatter.
```

## Automated Validation

- **Tool:** verification by the agent itself before saving the artifact
- **When:** during creation of any new Ahrena artifact
- **Metric:** 100% of artifacts must follow the structure of the official template for their Pilar
