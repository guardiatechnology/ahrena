# Codex: Framework Naming Conventions

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Naming and addressing of Ahrena artifacts

## Overview

This Codex details the naming conventions defined in the `naming` section of `.ahrena/.directives`. It complements `lex-naming` (which establishes the obligation) with examples, good practices, and common pitfalls. Use this Codex when creating or reviewing file names, directory names, and artifact placement in the taxonomy.

## Context

- **Domain:** Artifact naming and framework directory structure
- **Audience:** AI agents that create or move artifacts; framework maintainers
- **Update:** When conventions in `.directives` change or new reserved clades are defined

## Content

### Prefixes per Pilar

The prefix for each Pilar is the value defined in `naming.prefixes` in `.ahrena/.directives` (keys: `lexis`, `codex`, `katas`, `warriors`, `cries`). The user or project defines it; the agent MUST consult the file to know the value in use.

| Pilar | Key in naming.prefixes | Example file (when default value is used) |
|-------|------------------------|------------------------------------------|
| Lexis | `lexis` | `lex-directives.md`, `lex-pilars.md` |
| Codex | `codex` | `codex-naming.md`, `codex-pilars.md` |
| Katas | `katas` | `kata-create-lexis.md`, `kata-translate.md` |
| Warriors | `warriors` | `warrior-translator.md`, `warrior-daedalus.md` |
| Cries | `cries` | `cry-new-lex.md`, `cry-translate.md` |

Never use another Pilar's prefix (e.g. do not name a Codex `manual-xyz.md`). The prefix identifies the artifact type; identification is by the value configured in `.directives`, not a fixed value.

### Extensions

| Context | Extension | Example |
|---------|------------|---------|
| Framework (.md files in repo) | `.md` | `lex-pilars.md` |
| Cursor rules | `.mdc` | `lex-pilars.mdc` (generated from .md) |
| Skills and commands in Cursor | Per resource (e.g. SKILL.md, .md) | Defined by the installer |

### Casing

| Element | Convention | Correct example | Incorrect example |
|---------|------------|-----------------|-------------------|
| File name | kebab-case | `codex-restful-apis.md` | `codex_restful_apis.md`, `codexRestfulApis.md` |
| Directory name | kebab-case | `project_artifacts`, `_foundation` | `ProjectArtifacts`, `_Foundation` |

Note: reserved clades use the `_` prefix (e.g. `_foundation`); the rest of the name follows kebab-case.

### Addressing (taxonomy)

Pattern: `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`

| Segment | Meaning | Example |
|---------|---------|---------|
| `lang` | BCP 47 language code | `pt-BR`, `es`, `en` |
| `clade` | First-level discipline or domain | `_foundation`, `engineering`, `documentation` |
| `subclade` | Area within the clade | `authoring`, `platform`, `i18n` |
| `pilar` | Pilar name (plural in folders): lexis, codex, katas, warriors, cries | `lexis`, `codex`, `katas` |
| `prefix-name.ext` | File name with prefix and extension | `lex-pilars.md` |

Full example: `pt-BR/_foundation/authoring/lexis/lex-pilars.md`

### Reserved clades

Defined in `naming.reserved_clades`. E.g. `_foundation`.

- They use the `_` prefix to indicate they are transversal or special.
- Do not create a clade with the same name without the prefix (e.g. do not use `foundation` as a clade if `_foundation` is reserved).
- Consult `.directives` for the current list.

### Tone and style (naming.tone_and_writing_style)

The `naming.tone_and_writing_style` section in `.directives` contains tone and writing-style guidelines. Their application is mandatory per `lex-tone` and detailed in `codex-tone`. It is not part of file/directory naming but sits under the `naming` section in the file.

### Good practices

| Practice | Description |
|----------|-------------|
| Descriptive name after prefix | Use `lex-no-secrets` instead of `lex-1`; the name should indicate the content |
| Consistency across languages | The same artifact in pt-BR, es, and en must have the same file name (e.g. `lex-pilars.md` in all language folders) |
| Avoid obscure acronyms | Prefer `codex-restful-apis` to `codex-ra` if the context is not obvious |
| Specific subclade | Choose the most specific subclade that makes sense (e.g. `authoring` within `_foundation`) |

### Common pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Forgetting prefix | File `directives.md` in the lexis directory | Name it `lex-directives.md` |
| Wrong casing | `Lex-Pilars.md` or `lex_pilars.md` | Use kebab-case: `lex-pilars.md` |
| Artifact outside tree | File at root of `framework/` or without language | Place in `{lang}/{clade}/{subclade}/{pilar}/` |
| Pilar as folder | Folder name must be plural (lexis, codex, katas, warriors, cries) | Use `lexis/`, not `lex/` |

## Glossary

| Term | Definition |
|------|------------|
| Addressing | Full position of the artifact in the taxonomy (lang/clade/subclade/pilar/file) |
| Reserved clade | Clade listed in `naming.reserved_clades` with special rules (e.g. prefix `_`) |
| kebab-case | Lowercase words separated by a hyphen (e.g. `lex-no-secrets`) |

## References

- `lex-naming` — Law that mandates naming conventions
- `lex-directives` — Mandatory consultation of `.ahrena/.directives`
- `codex-directives` — Manual for the .directives file (naming section)
- `lex-framework-language` — Language structure and first level of navigation
- `codex-tone` — Application of tone_and_writing_style (under naming in .directives)
