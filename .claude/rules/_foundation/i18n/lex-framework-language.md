# Lexis: Framework Language Structure

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Folder structure and language-based navigation within `framework/`

## Law

> **The language MUST be the first level of navigation within `framework/`, following the addressing pattern `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`. Every artifact MUST exist in all languages defined in `language.i18n`.**

## Rules

### 1. Language as navigation root

Within `framework/`, the first directory level is **always** the BCP 47 language code (e.g., `pt-BR`, `es`, `en`). The entire tree of clades, subclades, and pilares is replicated inside each language folder:

```
framework/
├── pt-BR/
│   └── _foundation/process/lexis/lex-directives.md
├── es/
│   └── _foundation/process/lexis/lex-directives.md
└── en/
    └── _foundation/process/lexis/lex-directives.md
```

### 2. Mandatory completeness

Every artifact created in the default language (`language.default`) **MUST** have corresponding versions in all other languages listed in `language.i18n`. An artifact is considered incomplete as long as it does not exist in all required languages.

### 3. Structural equivalence

Versions across languages **MUST** maintain the same directory structure. If an artifact exists at `pt-BR/_foundation/process/lexis/lex-directives.md`, it **MUST** exist at the same relative path in every language.

### 4. Cursor in single language

`.mdc` files in the `.cursor/` directory **MUST** be written exclusively in the language defined in `language.cursor` in `.ahrena/.directives`. Cursor does **NOT** use language folders — only one language is maintained.

### 5. Change propagation

When an artifact in the default language is modified, versions in other languages **MUST** be updated. The agent making the change **MUST** flag the need for translation updates.

### 6. Default language as source of truth

The artifact in the language defined in `language.default` is the **source of truth**. In case of divergence between versions, the content in the default language prevails.

### 7. No loose content at the root

No `.md` artifact should exist directly in `framework/` outside of language folders, except meta-configuration files such as `.directives.sample`.

## Examples

### Correct

```
framework/pt-BR/_foundation/process/lexis/lex-directives.md
framework/es/_foundation/process/lexis/lex-directives.md
framework/en/_foundation/process/lexis/lex-directives.md
# Same relative path in each language; artifact complete for language.i18n.
```

### Incorrect

```
framework/lex-directives.md
# ❌ Artifact outside language folder; breaks addressing {lang}/{clade}/...

framework/pt-BR/_foundation/process/lexis/lex-directives.md
# Exists only in pt-BR; es and en missing.
# ❌ Incomplete artifact; violates mandatory completeness.
```

## Automated Validation

- **Tool:** verification by the agent or script that compares `framework/{lang}/` for each `lang` in `language.i18n`
- **When:** on artifact creation (kata-create-*), on push to framework, and on PR review
- **Metric:** 0 artifacts in only one language when `language.i18n` requires all; 0 artifacts outside `{lang}/`
