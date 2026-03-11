---
name: kata-create-warrior
description: "Create New Warrior. Warriors creation (specialized agents)"
---

# Kata: Create New Warrior

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Warriors creation (specialized agents)

## Workflow

```
Progress:
- [ ] 1. Read directives and references
- [ ] 2. Design the identity
- [ ] 3. Define responsibilities and consultation chain
- [ ] 4. Write the artifact
- [ ] 5. Save to correct path
- [ ] 6. Create in remaining languages
- [ ] 7. Final validation
```

### Step 1: Read Directives and References

1. Read `.ahrena/.directives` to obtain:
   - `language.default` — default language
   - `language.i18n` — mandatory languages
   - `naming.addressing` — addressing pattern
   - `naming.prefixes.warriors` — prefix (`warrior-`)
2. Read `codex-warriors` to internalize quality criteria
3. Read `templates/warrior-sample.md` to obtain the base structure
4. Check existing Warriors to avoid responsibility overlap

### Step 2: Design the Identity

1. **Name:** Choose a memorable name that evokes the role (mythological, historical, or symbolic)
2. **Role:** Clear professional title (e.g., "Specialist Technical Documentation Translator")
3. **Domain:** Specific area of operation with clear boundaries
4. **Persona:** 2-3 adjectives that define the tone (e.g., "methodical, rigorous, focused on trade-offs")
5. **Mission:** 1-2 sentences in blockquote summarizing the core purpose

### Step 3: Define Responsibilities and Consultation Chain

1. List positive responsibilities ("Does") — concrete and specific actions
2. List exclusions ("Does Not") — clear limits to prevent unbounded scope
3. Map the consultation chain:
   - **Lexis:** which laws the Warrior follows (always include `lex-directives`)
   - **Codex:** which manuals it consults for decision-making
   - **Katas:** which procedures it executes
4. Define escalation criteria — when the Warrior stops and requests human assistance
5. Define the operation flow: Receives → Consults → Analyzes → Produces → Validates

### Step 4: Write the Artifact

Use `templates/warrior-sample.md` as a base and fill in all sections:

1. **Title:** `# Warrior: [Name] — [Brief Description]`
2. **Blockquote:** Prefix, type, and scope
3. **Identity:** Name, role, domain, and persona
4. **Mission:** Quote in blockquote
5. **Responsibilities:** "Does" and "Does Not" lists
6. **Consultation:** Lexis, Codex, and Katas tables
7. **Behavior:** Tone, operation flow, and escalation criteria
8. **Interaction Example:** User input + structured Warrior response

### Step 5: Save to Correct Path

1. Determine the appropriate Clade and Subclade
2. Compose the path: `framework/{lang}/{clade}/{subclade}/warriors/warrior-{name}.md`
3. Use kebab-case for the file name (Warrior name)
4. Create intermediate directories if necessary
5. Save the artifact in the default language (`language.default`)

### Step 6: Create in Remaining Languages

1. For each language in `language.i18n` (except the default):
   - Execute `kata-translate` with the file created in Step 5
   - Or translate directly by consulting `lex-language-{lang}` and `codex-language-{lang}`
2. Save each translation in the equivalent path under `framework/{lang}/`

### Step 7: Final Validation

- [ ] The file follows the complete structure from `templates/warrior-sample.md`
- [ ] The identity has name, role, domain, and persona
- [ ] The mission is in blockquote with 1-2 sentences
- [ ] "Does" and "Does Not" lists are balanced and unambiguous
- [ ] The consultation chain includes at least `lex-directives`
- [ ] The escalation criteria are concrete
- [ ] The interaction example has complete input and output
- [ ] The file is saved in the correct taxonomy path
- [ ] Versions exist in all languages from `language.i18n`
- [ ] The file name uses the Pilar prefix defined in `naming.prefixes.warriors` (consult `.directives`) and kebab-case

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Warrior in default language | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/warriors/warrior-{name}.md` |
| Translations | Markdown (`.md`) | Same path in each `framework/{lang}/` |

## Constraints

- Never create a generic Warrior without a delimited scope
- Never create a Warrior without an explicit consultation chain
- Never create a Warrior without escalation criteria
- Always consult `codex-warriors` before writing
- Always check existing Warriors to avoid responsibility overlap
