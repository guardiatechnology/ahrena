# Codex: Framework Language Structure

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Language-based folder organization within `framework/`

## Content

### Principles

1. **Language as root:** the language code (e.g., `pt-BR`, `es`, `en`) is always the first directory within `framework/`.
2. **Full mirroring:** each language folder fully replicates the tree of clades, subclades, and pilares.
3. **Source of truth:** the language defined in `language.default` (currently `pt-BR`) is the source of truth.
4. **Monolingual Cursor:** `.mdc` files in `.cursor/` exclusively use the `language.cursor` language.

### Folder Structure

```
framework/
├── .directives.sample
├── pt-BR/                          # Default language (source of truth)
│   ├── _foundation/
│   │   └── i18n/
│   │       ├── lexis/lex-framework-language.md
│   │       └── codex/codex-framework-language.md
│   └── documentation/i18n/
│       ├── lexis/
│       ├── codex/
│       ├── katas/kata-translate.md
│       ├── warriors/warrior-translator.md
│       └── cries/cry-translate.md
├── es/                             # Spanish (same structure)
│   └── ...
└── en/                             # English (same structure)
    └── ...
```

### Patterns and Conventions

| Aspect | Pattern | Example |
|--------|---------|---------|
| Framework addressing | `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md` | `en/_foundation/i18n/lexis/lex-framework-language.md` |
| Cursor addressing | `{clade}/{subclade}/{prefix}-{name}.mdc` | `_foundation/i18n/lex-framework-language.mdc` |
| Default language | Defined in `language.default` | `pt-BR` |
| Required languages | Listed in `language.i18n` | `pt-BR`, `es`, `en` |
| Cursor language | Defined in `language.cursor` | `en` |
| Folder names | BCP 47 code | `pt-BR`, `es`, `en` |

### Artifact Creation Flow

1. Create the artifact in the default language (`language.default`)
2. Translate to each language in `language.i18n` (using `warrior-translator` from `documentation/i18n/`)
3. Create the `.mdc` version for Cursor in `language.cursor`
4. Validate that the artifact exists in all required languages

### Update Flow

1. Modify the artifact in the default language
2. Flag that translations need updating
3. Use `cry-translate` or `warrior-translator` to update each translation
4. Update the `.mdc` version if needed

### Separation of Responsibilities

| Clade | Scope | Artifacts |
|-------|-------|-----------|
| `_foundation/i18n/` | Folder **structure** and language navigation rules | `lex-framework-language`, `codex-framework-language` |
| `documentation/i18n/` | Content **translation** — per-language rules, procedures, agent | `lex-language`, `lex-language-{lang}`, `codex-language`, `codex-language-{lang}`, `kata-translate`, `warrior-translator`, `cry-translate` |
