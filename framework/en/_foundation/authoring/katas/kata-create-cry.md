# Kata: Create New Cry

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Cries creation (recurring commands)

## Objective

This Kata defines the standardized procedure for creating a new Cry in Ahrena — from designing the command and its parameters to creating the artifact in all three mandatory languages.

## When to Use

- When it is necessary to create a quick shortcut for a recurring task
- When the user explicitly requests the creation of a new Cry
- When invoked by `cry-new-cry`
- When an existing Kata needs a simplified entry point

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Action | Yes | What the command does (e.g., "translate document", "generate changelog") |
| Associated Kata | No | Kata that the Cry invokes. If omitted, the agent MUST identify or suggest creating a Kata |
| Associated Warrior | No | Warrior that executes the Kata, if one exists |
| Clade/Subclade | No | Where to save in the taxonomy. If omitted, the agent MUST infer from the action |

## Workflow

```
Progress:
- [ ] 1. Read directives and references
- [ ] 2. Design the command
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
   - `naming.prefixes.cries` — prefix (`cry-`)
2. Read `codex-cries` to internalize quality criteria
3. Read `templates/cry-sample.md` to obtain the base structure
4. Check existing Cries to avoid duplication
5. Confirm that the associated Kata exists (or mark it as pending creation)

### Step 2: Design the Command

1. Define the **invocation syntax**: `/cry-{name} <required> [optional]`
2. Define **parameters**:
   - Minimum required parameters (only the essential ones)
   - Smart defaults for optional parameters (from `.directives` when possible)
   - Explicit format for each parameter
3. Define the **invocation chain**:
   - Pattern 1: Cry → Kata (when there is no Warrior)
   - Pattern 2: Cry → Warrior → Kata (when a dedicated Warrior exists)
4. Compose the **prompt template**:
   - Context with `{{param}}` variables
   - Task referencing the Kata by name
   - Explicit output format
5. Prepare an **invocation example** with concrete input and output

### Step 3: Write the Artifact

Use `templates/cry-sample.md` as a base and fill in all sections:

1. **Title:** `# Cry: [Command Name]`
2. **Blockquote:** Prefix, type, and scope
3. **Description:** One sentence about what the command does
4. **Usage:** Syntax with `/cry-{name}`
5. **Parameters:** Table with name, requirement status, description, and example
6. **What the Command Does:** Numbered list of 3-6 high-level actions
7. **Prompt Template:** Code block with context, task, and format
8. **Invocation Example:** Concrete input and output
9. **Constraints:** Command limits
10. **Cry vs Kata:** Comparative table between Cry and Kata for this case

### Step 4: Save to Correct Path

1. Determine the appropriate Clade and Subclade
2. Compose the path: `framework/{lang}/{clade}/{subclade}/cries/cry-{name}.md`
3. Use kebab-case for the file name
4. Create intermediate directories if necessary
5. Save the artifact in the default language (`language.default`)

### Step 5: Create in Remaining Languages

1. For each language in `language.i18n` (except the default):
   - Execute `kata-translate` with the file created in Step 4
   - Or translate directly by consulting `lex-language-{lang}` and `codex-language-{lang}`
2. Save each translation in the equivalent path under `framework/{lang}/`

### Step 6: Final Validation

- [ ] The file follows the complete structure from `templates/cry-sample.md`
- [ ] The invocation syntax is clear (`/cry-{name} <args>`)
- [ ] Required parameters are minimal (1-2 ideally)
- [ ] The prompt template uses `{{variables}}` and references the Kata
- [ ] The invocation example has concrete input and output
- [ ] The "Cry vs Kata" table is filled in
- [ ] The associated Kata exists or is marked as pending
- [ ] The file is saved in the correct taxonomy path
- [ ] Versions exist in all languages from `language.i18n`
- [ ] The file name uses the Pilar prefix defined in `naming.prefixes.cries` (consult `.directives`) and kebab-case

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Cry in default language | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/cries/cry-{name}.md` |
| Translations | Markdown (`.md`) | Same path in each `framework/{lang}/` |

## Constraints

- Every Cry MUST reference at least one Kata — Cries without a Kata delegate poorly
- Never create a Cry with many required parameters — if it needs many inputs, the user should use the Kata directly
- Always consult `codex-cries` before writing
- Always check existing Cries to avoid duplication

## References

- `lex-pilars` — Canonical definition of the Pilars; validate produced artifact (Cry invokes only Kata/Warrior)
- `codex-pilars` — Validation checklist for Cries (Artifact validation section)
- `codex-cries` — Quality criteria for Cries
- `codex-pilars` — Overview of the Pilar system
- `lex-template-usage` — Mandatory template usage law
- `lex-framework-language` — Language structure law
- `kata-translate` — Translation procedure
- `templates/cry-sample.md` — Official template
