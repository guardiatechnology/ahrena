---
name: kata-translate
description: "Documentation Translation. Translation of any technical documentation"
---

# Kata: Documentation Translation

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Translation of any technical documentation

## Workflow

```
Progress:
- [ ] 1. Read directives and rules
- [ ] 2. Identify context
- [ ] 3. Consult target language rules
- [ ] 4. Translate content
- [ ] 5. Save to correct path
- [ ] 6. Final validation
```

### Step 1: Read Directives and Rules

1. Read `.ahrena/.directives` to obtain:
   - `language.default` — default language (source of truth)
   - `language.i18n` — required languages list
   - `naming.addressing` — addressing pattern
2. Confirm target language(s) are in `language.i18n`

### Step 2: Identify Context

1. Read the source file completely
2. Identify the source language (from path or content)
3. Determine if the document belongs to the Ahrena framework (in `framework/`) or is generic
4. If framework: check if `lex-framework-language` applies
5. Calculate the destination path for each target language

**Example (framework):**
- Source: `framework/pt-BR/documentation/i18n/lexis/lex-language.md`
- Target (es): `framework/es/documentation/i18n/lexis/lex-language.md`
- Target (en): `framework/en/documentation/i18n/lexis/lex-language.md`

### Step 3: Consult Target Language Rules

For **each target language**, consult in this order:

1. `lex-language` — cross-cutting rules (always)
2. `lex-language-{lang}` — target-language-specific rules
3. `codex-language` — cross-cutting guide
4. `codex-language-{lang}` — target-language-specific guide

Internalize the rules before starting the translation.

### Step 4: Translate Content

1. Translate content applying the target language rules
2. **Mandatory preservation:** all Markdown structure, Ahrena proper names, code blocks, file paths, URLs
3. **Translate:** titles, body text, table descriptions, headers (Type, Scope) to target language equivalents
4. **Apply language particularities:** tone, formality, technical terms, false cognates per reference tables

### Step 5: Save to Correct Path

1. Create intermediate directories if they do not exist
2. Save the translated file to the path calculated in Step 2
3. The file name remains unchanged (prefix + kebab-case name)

### Step 6: Final Validation

- [ ] Translated file exists at the correct path
- [ ] All sections from the original are present
- [ ] Headings follow the same hierarchy
- [ ] Ahrena canonical terms were not translated
- [ ] Paths and references are preserved
- [ ] Content language is correct (no source-language fragments)
- [ ] Markdown formatting is intact
- [ ] `lex-language-{lang}` rules were respected

## Restrictions

- Never alter the source file during translation
- Never translate Ahrena canonical terms
- Never omit or merge sections from the original
- Always consult target language rules before translating
- Always use the default language as the source of truth
