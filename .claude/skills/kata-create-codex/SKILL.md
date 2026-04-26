---
name: kata-create-codex
description: "Create New Codex. Codex creation (reference manuals)"
---

# Kata: Create New Codex

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Codex creation (reference manuals)

## Workflow

```
Progress:
- [ ] 1. Read directives and references
- [ ] 2. Structure the knowledge
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
   - `naming.prefixes.codex` — prefix (`codex-`)
2. Read `codex-codex` to internalize quality criteria
3. Read `templates/codex-sample.md` to obtain the base structure
4. Check existing Codex in the target Clade/Subclade to avoid duplication

### Step 2: Structure the Knowledge

1. Define the scope: what this Codex covers and what it does not cover
2. Identify the fundamental principles of the domain (3-5 principles)
3. Map relevant patterns and conventions (table: aspect, pattern, example)
4. List current decisions, if applicable
5. Identify technical constraints of the domain
6. Define the update trigger (when the Codex needs revision)

### Step 3: Write the Artifact

Use `templates/codex-sample.md` as a base and fill in all sections:

1. **Title:** `# Codex: [Manual Name]`
2. **Blockquote:** Prefix, type, and scope
3. **Overview:** A concise description of the covered domain (maximum 2 paragraphs)
4. **Context:** Domain, target audience, and update trigger
5. **Content:**
   - Principles: numbered list with description and justification
   - Patterns and Conventions: structured table
   - Current Decisions: table with ADR, decision, and status (if applicable)
   - Technical Constraints: list of concrete limits
6. **Reference Diagram:** When the domain benefits from visualization
7. **Glossary:** Domain terms with contextual definitions
8. **References:** Links to related artifacts

### Step 4: Save to Correct Path

1. Determine the appropriate Clade and Subclade for the domain
2. Compose the path: `framework/{lang}/{clade}/{subclade}/codex/codex-{name}.md`
3. Use kebab-case for the file name
4. Create intermediate directories if necessary
5. Save the artifact in the default language (`language.default`)

### Step 5: Create in Remaining Languages

1. For each language in `language.i18n` (except the default):
   - Execute `kata-translate` with the file created in Step 4
   - Or translate directly by consulting `lex-language-{lang}` and `codex-language-{lang}`
2. Save each translation in the equivalent path under `framework/{lang}/`

### Step 6: Final Validation

- [ ] The file follows the complete structure from `templates/codex-sample.md`
- [ ] The Overview defines the scope in a maximum of 2 paragraphs
- [ ] The Context includes a concrete update trigger
- [ ] The principles are actionable (not generic platitudes)
- [ ] Tables are used for structured information
- [ ] The Glossary defines terms in the context of this Codex
- [ ] The file is saved in the correct taxonomy path
- [ ] Versions exist in all languages from `language.i18n`
- [ ] The file name uses the Pilar prefix defined in `naming.prefixes.codex` (consult `.directives`) and kebab-case

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Codex in default language | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/codex/codex-{name}.md` |
| Translations | Markdown (`.md`) | Same path in each `framework/{lang}/` |

## Constraints

- Never create an encyclopedic Codex — if the scope is too broad, split it into smaller Codex artifacts
- Never create a Codex without an update trigger — static Codex artifacts become obsolete
- Always consult `codex-codex` before writing
- Always check existing Codex to avoid duplication or overlap
