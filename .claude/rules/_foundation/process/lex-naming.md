# Lexis: Mandatory Naming Conventions

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Naming and addressing of Ahrena framework artifacts

## Law

> **Every artifact of the Ahrena framework MUST follow the naming conventions defined in the `naming` section of `.ahrena/.directives`: mandatory Pilar prefix (`naming.prefixes`), extension per context (`naming.extensions`), casing for files and directories (`naming.casing`), addressing pattern (`naming.addressing`), and respect for reserved clades (`naming.reserved_clades`).**

## Rules

### 1. Prefixes

Every artifact MUST use the prefix of its Pilar per `naming.prefixes` in `.ahrena/.directives`. Prefixes are defined by the user or project; the keys are `lexis`, `codex`, `katas`, `warriors`, `cries`. The agent identifies the artifact type (Lexis, Codex, Kata, etc.) by observing which configured prefix the file name uses — it must not assume fixed values.

Example: if `naming.prefixes.lexis` is `lex-`, a Law file must be named `lex-{name}.md`; if the project defines another value (e.g. `law-`), that value is mandatory. Never use another Pilar's prefix or omit the prefix.

### 2. Extensions

- In the framework (tree `framework/`): use `naming.extensions.framework` (typically `.md`).
- In Cursor (rules): use `naming.extensions.cursor` (typically `.mdc`).

### 3. Casing

- Files: follow `naming.casing.files` (typically kebab-case). Example: `lex-no-secrets.md`.
- Directories: follow `naming.casing.directories` (typically kebab-case). Example: `engineering/backend/`.

### 4. Addressing

Every artifact in the framework MUST be placed according to `naming.addressing`. The canonical pattern is:

`{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`

Language is the first level of navigation (`lex-framework-language`). No artifact may sit outside this structure (e.g. at the root of `framework/` without language/clade/subclade/pilar).

### 5. Reserved clades

Values in `naming.reserved_clades` (e.g. `_foundation`) are special clades. The agent MUST recognize them and respect their rules (e.g. prefix `_` for transversal clades). Do not create clades whose names conflict with reserved ones.

### 6. Source of truth

Exact keys and values (prefixes, extensions, casing) are defined in `.ahrena/.directives`. In the absence of the file, the agent MUST warn the user. Do not infer conventions without consulting the file (`lex-directives`).

## Examples

### Correct

- `framework/pt-BR/_foundation/authoring/lexis/lex-pilars.md` — language, clade, subclade, pilar, prefix, and kebab-case.
- `framework/pt-BR/engineering/platform/codex/codex-restful-apis.md` — conventions respected.

### Incorrect

- `framework/lexis/lex-pilars.md` — missing language and clade/subclade.
- `framework/pt-BR/_foundation/authoring/lexis/pilars.md` — missing the Lexis Pilar prefix (consult `naming.prefixes.lexis` in `.directives`).
- `framework/pt-BR/_foundation/Authoring/lexis/lex-pilars.md` — directory not in kebab-case.

## Automated Validation

- **Tool:** verification by the agent when creating or reviewing an artifact; possible extension with a validation script.
- **When:** at creation (kata-create-*), at PR review, and when pushing to the framework.
- **Metric:** 0 artifacts with incorrect prefix, casing, or placement outside the canonical addressing.
