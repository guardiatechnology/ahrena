# Lexis: Cross-Language Translation Rules

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All technical documentation translation

## Law

> **Every translation MUST preserve the structural and semantic equivalence of the original document, respecting the cross-cutting rules defined in this Lexis AND the target-language-specific rules defined in `lex-language-{lang}`.**

## Rules

### 1. Structural equivalence

The translation **MUST** maintain exactly the same structure as the original:
- Same sections and headings (translated, but in the same order and hierarchy)
- Same Markdown formatting (tables, lists, code blocks, blockquotes)
- Same number of sections — never omit, merge, or reorder

### 2. Semantic fidelity

The translation **MUST** preserve the original meaning. This is not free paraphrasing — it is technical translation:
- The meaning of each sentence must be equivalent to the original
- Technical nuances must be preserved
- Imperative instructions ("MUST", "MUST NOT") must maintain the same force in the target language

### 3. Preservation of technical elements

The following elements **MUST NEVER** be translated or altered:
- Code blocks and their contents
- File paths (e.g., `framework/pt-BR/`, `.ahrena/.directives`)
- URLs and links
- Variable, function, and command names
- File names (e.g., `lex-framework-language.md`)

### 4. Ahrena canonical terms

Framework proper names are **NEVER** translated:
- **Lexis**, **Codex**, **Katas**, **Warriors**, **Cries**
- **Ahrena**, **Clade**, **Subclade**, **Pilar**
- Warrior names (e.g., **Hermes**)

### 5. Rule hierarchy

For each translation, the agent **MUST** consult:
1. This `lex-language` (cross-cutting rules — always apply)
2. `lex-language-{lang}` for the target language (specific rules — complement the cross-cutting ones)
3. `codex-language` (cross-cutting reference guide)
4. `codex-language-{lang}` for the target language (specific guide)

Language-specific rules **complement** the cross-cutting ones but **do not contradict** them.

### 6. Source-language agnostic

The translator does **NOT** assume which language is the source. The default language is determined by `language.default` in `.ahrena/.directives`. The translator knows how to translate **to** languages, not **from** a fixed language.

### 7. Translation completeness

Every translation **MUST** be complete. The following are not allowed:
- Leaving fragments in the source language
- Using placeholders like "TODO: translate"
- Omitting sections due to complexity
