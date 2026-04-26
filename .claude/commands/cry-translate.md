Translate Document. Technical documentation translation

# Cry: Translate Document

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Technical documentation translation

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

## Restrictions

- Does not modify the source file — only generates translations
- Follows `lex-language` and `lex-language-{lang}` rules
- Ahrena canonical terms are not translated
- Translation order respects `language.i18n` or `--order`
