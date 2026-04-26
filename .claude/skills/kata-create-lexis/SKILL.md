---
name: kata-create-lexis
description: "Create New Lexis. Lexis creation (unbreakable laws)"
---

# Kata: Create New Lexis

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Lexis creation (unbreakable laws)

## Workflow

```
Progress:
- [ ] 1. Read directives and references
- [ ] 2. Conceive the law
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
   - `naming.prefixes.lexis` — prefix (`lex-`)
2. Read `codex-lexis` to internalize quality criteria
3. Read `templates/lex-sample.md` to obtain the base structure
4. Check existing Lexis in the target Clade/Subclade to avoid duplication

### Step 2: Conceive the Law

1. Formulate the law statement following the criteria from `codex-lexis`:
   - Clear subject
   - Imperative verb (MUST, MUST NOT)
   - Specific action
   - Temporal condition (if applicable)
2. Verify unambiguity: does the law have a single interpretation?
3. Verify testability: can it be verified automatically?
4. Verify necessity: does it solve a real problem?
5. Verify immutability: does it need exceptions? If so, consider a Codex instead of Lexis

### Step 3: Write the Artifact

Use `templates/lex-sample.md` as a base and fill in all sections:

1. **Title:** `# Lexis: [Descriptive Name]`
2. **Blockquote:** Prefix, type, and scope
3. **Purpose:** Why this law exists — connect to a real risk or problem
4. **Law:** Imperative statement in blockquote (`> **[statement]**`)
5. **Coverage:**
   - Applies to: specific scope
   - Bound agents: all or specific Warriors
   - Exceptions: None (always)
6. **Violation Consequences:**
   - Automatic block: technical action
   - Alert: who is notified
   - Remediation: how to fix
7. **Examples:** Correct and Incorrect with code blocks
8. **Automated Validation:** Tool, timing, and metric

### Step 4: Save to Correct Path

1. Determine the appropriate Clade and Subclade for the subject
2. Compose the path: `framework/{lang}/{clade}/{subclade}/lexis/lex-{name}.md`
3. Use kebab-case for the file name
4. Create intermediate directories if necessary
5. Save the artifact in the default language (`language.default`)

### Step 5: Create in Remaining Languages

1. For each language in `language.i18n` (except the default):
   - Execute `kata-translate` with the file created in Step 4
   - Or, if the agent is proficient in the language, translate directly by consulting `lex-language-{lang}` and `codex-language-{lang}`
2. Save each translation in the equivalent path under `framework/{lang}/`

### Step 6: Final Validation

- [ ] The file follows the complete structure from `templates/lex-sample.md`
- [ ] The law statement is clear, unambiguous, and imperative
- [ ] The "Exceptions" section states "None"
- [ ] The "Automated Validation" section specifies tool, timing, and metric
- [ ] The examples (Correct/Incorrect) are concrete
- [ ] The file is saved in the correct taxonomy path
- [ ] Versions exist in all languages from `language.i18n`
- [ ] The file name uses the Pilar prefix defined in `naming.prefixes.lexis` (consult `.directives`) and kebab-case

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Lexis in default language | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/lexis/lex-{name}.md` |
| Translations | Markdown (`.md`) | Same path in each `framework/{lang}/` |

## Constraints

- Never create a Lexis that admits exceptions — if it needs an exception, it MUST be a Codex
- Never create a Lexis without automated validation — if it cannot be tested, rethink the formulation
- Always consult `codex-lexis` before writing
- Always check existing Lexis to avoid duplication or contradiction
