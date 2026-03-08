---
description: "Translate a document to one or more languages. Invokes warrior-translator (Hermes) with kata-translate, consulting per-language lex and codex."
alwaysApply: false
---

# Cry: Translate Document

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Documentation translation

## Usage

```
/cry-translate <file> [language] [--order]
```

## Parameters

- `file` (required): Path to the document to translate
- `language` (optional): BCP 47 code(s). Defaults to all `language.i18n` except source
- `--order` (optional): Translation execution order. Defaults to `language.i18n` order

## What It Does

1. Read `.ahrena/.directives` for languages and order
2. Identify source language from path
3. For each target language (in order):
   - Consult `lex-language` + `lex-language-{lang}` + `codex-language` + `codex-language-{lang}`
   - Execute `kata-translate`
   - Save to correct path
4. Report created files with per-language validation

## Prompt Template

```
Assume the role of warrior-translator (Hermes). Consult .ahrena/.directives.
For each target language in order: consult per-language rules, execute
kata-translate, save translation, validate. Report results.
```
