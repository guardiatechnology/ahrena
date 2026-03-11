# Cry: Translate Document

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Technical documentation translation

## Description

Quick command to translate a document to one or more languages. Invokes the `warrior-translator` (Hermes) who executes `kata-translate`, consulting the rules and guides specific to each target language.

## Usage

```
/cry-translate <file> [language] [--order]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `file` | Yes | Path to the document to translate | `framework/pt-BR/_foundation/process/lexis/lex-directives.md` |
| `language` | No | BCP 47 code(s) of the target language. If omitted, translates to all `language.i18n` languages except the source | `es`, `en`, `es,en` |
| `--order` | No | Specifies translation order. If omitted, follows `language.i18n` order | `--order en,es` |

## Translation Order

When multiple languages are targeted, the Cry defines the **execution order**:

1. **Default:** follows the order defined in `language.i18n` in `.ahrena/.directives`, excluding the source language
2. **Custom:** when `--order` is specified, follows the given order
3. **Sequential:** each language is fully translated before moving to the next

**Default order example (source in pt-BR):**
1. Translate to es (consulting `lex-language-es` + `codex-language-es`)
2. Translate to en (consulting `lex-language-en` + `codex-language-en`)

## What the Command Does

1. Reads `.ahrena/.directives` for languages and order
2. Identifies the source language from the path or content
3. Determines target language(s) and execution order
4. Invokes `warrior-translator` with `kata-translate`
5. For each language in order, the Warrior (via kata-translate) consults `lex-language-{lang}` and `codex-language-{lang}`, translates the document, and saves to the correct path
6. Reports created files

## Prompt Template

```
Context:
- Source file: {{file}}
- Target language(s): {{language}} (or all from language.i18n except source)
- Order: {{order}} (or as per language.i18n)

Task:
Assume the role of warrior-translator (Hermes). Read .ahrena/.directives for required languages. For each target language in the defined order, execute **kata-translate** (the Kata consults the language Lexis and Codex per its documentation). Read the source file, execute the Kata, and save the translation to the correct path.

Output format:
List of created files with per-language validation confirmation.
```

## Invocation Examples

**Translate to all languages:**

```
/cry-translate framework/pt-BR/_foundation/process/lexis/lex-directives.md
```

**Output:**
```
Hermes — Translation complete.

Execution order: es → en

Files created:
1. framework/es/_foundation/process/lexis/lex-directives.md ✓
2. framework/en/_foundation/process/lexis/lex-directives.md ✓

Per-language validation:
- es: ✓ sections preserved, canonical terms intact, impersonal voice applied
- en: ✓ sections preserved, canonical terms intact, active voice applied
```

**Translate to specific language:**

```
/cry-translate docs/architecture.md en
```

## Restrictions

- Does not modify the source file — only generates translations
- Follows `lex-language` and `lex-language-{lang}` rules
- Ahrena canonical terms are not translated
- Translation order respects `language.i18n` or `--order`

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation (command) | Complete procedure (6 steps) |
| **Complexity** | Low (command + parameters) | High (detailed workflow) |
| **Sets up agent?** | Yes (invokes warrior-translator) | Yes (defines the procedure) |
| **Translation order** | Defines the order | Does not define order (one language at a time) |

## References

- `warrior-translator` — Agent invoked by this Cry
- `kata-translate` — Procedure executed by the Warrior (the Kata consults the language Lexis and Codex; see Kata documentation)
