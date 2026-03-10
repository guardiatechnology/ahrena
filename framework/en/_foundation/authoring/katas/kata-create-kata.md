# Kata: Create New Kata

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Katas creation (repeatable procedures)

## Objective

This Kata defines the standardized procedure for creating a new Kata in Ahrena — from decomposing the task into steps to creating the artifact in all three mandatory languages. This is the Kata that creates Katas — the self-replication mechanism of the framework.

## When to Use

- When it is necessary to standardize a recurring task into a structured procedure
- When the user explicitly requests the creation of a new Kata
- When invoked by `cry-new-kata`

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Task | Yes | Description of the task to standardize (e.g., "create ADR", "perform code review") |
| Context | No | Additional information about the domain or task constraints |
| Clade/Subclade | No | Where to save in the taxonomy. If omitted, the agent MUST infer from the task |

## Workflow

```
Progress:
- [ ] 1. Read directives and references
- [ ] 2. Decompose the task
- [ ] 3. Write the artifact
- [ ] 4. Save to correct path
- [ ] 5. Create in remaining languages
- [ ] 6. Final validation
```

### Step 1: Read Directives and References

1. Read `.ahrena/.directives` to obtain:
   - `language.default` — default language
   - `language.i18n` — mandatory languages
   - `naming.addressing` — addressing pattern
   - `naming.prefixes.katas` — prefix (`kata-`)
2. Read `codex-katas` to internalize quality criteria
3. Read `templates/kata-sample.md` to obtain the base structure
4. Check existing Katas to avoid duplication

### Step 2: Decompose the Task

1. Identify the required **inputs**:
   - What is required?
   - What can have defaults?
   - What is the expected format for each input?
2. Decompose the task into **atomic steps** (4-8 steps ideal):
   - Each step performs a single action
   - Each step has numbered sub-actions
   - Each step is verifiable before proceeding
3. Identify the **outputs**:
   - What is produced?
   - In what format?
   - Where is it saved?
4. Define **validation criteria**:
   - Form checklist (structure, formatting)
   - Content checklist (completeness, correctness)
5. If the task has fewer than 4 steps, consider whether it should be a Cry instead of a Kata

### Step 3: Write the Artifact

Use `templates/kata-sample.md` as a base and fill in all sections:

1. **Title:** `# Kata: [Procedure Name]`
2. **Blockquote:** Prefix, type, and scope
3. **Objective:** One sentence about what the procedure produces
4. **When to Use:** List of activation conditions (3-4 items)
5. **Inputs:** Table with name, requirement status, and description
6. **Workflow:**
   - Progress checklist at the beginning (checkboxes)
   - Each step with a descriptive title and numbered sub-actions
   - Last step is always "Final Validation"
7. **Outputs:** Table with format and destination
8. **Constraints:** List of limits on what the Kata cannot do

### Step 4: Save to Correct Path

1. Determine the appropriate Clade and Subclade for the task
2. Compose the path: `framework/{lang}/{clade}/{subclade}/katas/kata-{name}.md`
3. Use kebab-case for the file name
4. Create intermediate directories if necessary
5. Save the artifact in the default language (`language.default`)

### Step 5: Create in Remaining Languages

1. For each language in `language.i18n` (except the default):
   - Execute `kata-translate` with the file created in Step 4
   - Or translate directly by consulting `lex-language-{lang}` and `codex-language-{lang}`
2. Save each translation in the equivalent path under `framework/{lang}/`

### Step 6: Final Validation

- [ ] The file follows the complete structure from `templates/kata-sample.md`
- [ ] The Objective describes the output in one clear sentence
- [ ] Inputs have requirement status and defaults defined
- [ ] The Workflow has a progress checklist at the beginning
- [ ] Each step performs a single action (atomic)
- [ ] The last step is "Final Validation" with checkboxes
- [ ] The number of steps is between 4 and 8
- [ ] Outputs specify format and destination
- [ ] The file is saved in the correct taxonomy path
- [ ] Versions exist in all languages from `language.i18n`
- [ ] The file name uses the Pilar prefix defined in `naming.prefixes.katas` (consult `.directives`) and kebab-case

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Kata in default language | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/katas/kata-{name}.md` |
| Translations | Markdown (`.md`) | Same path in each `framework/{lang}/` |

## Constraints

- If the task has fewer than 4 steps, consider creating a Cry instead of a Kata
- If the task has more than 8 steps, consider splitting it into smaller Katas
- Never create a Kata with vague steps — each step MUST have concrete sub-actions
- Always consult `codex-katas` before writing
- Always include final validation as the last step

## References

- `lex-pilars` — Canonical definition of the Pilars; validate produced artifact
- `codex-pilars` — Validation checklist for Katas (Artifact validation section)
- `codex-katas` — Quality criteria for Katas
- `codex-pilars` — Overview of the Pilar system
- `lex-template-usage` — Mandatory template usage law
- `lex-framework-language` — Language structure law
- `kata-translate` — Translation procedure
- `templates/kata-sample.md` — Official template
