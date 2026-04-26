# Codex: .directives File Manual

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Canonical configuration of the Ahrena framework

## Content

### Purpose of the file

The `.directives` file is the single source of truth for:

- Canonical framework paths (where templates, artifacts, specs live)
- Default language and mandatory languages for artifacts
- Terminal type for commands (bash or PowerShell)
- Naming conventions (prefixes, extensions, casing, addressing, reserved clades)
- Tone and writing style for artifacts and communication

No agent must infer these values without consulting the file (per `lex-directives`).

### Section `paths`

| Key | Meaning | Use |
|-----|---------|-----|
| `paths.root` | Framework root directory in the project | `.ahrena/` — entry point in any project that adopts Ahrena |
| `paths.directives` | Path to the directives file | `.ahrena/.directives` — always relative to repository root |
| `paths.templates` | Templates directory in the framework repo | `templates/` — contains samples (lex, codex, kata, warrior, cry) |
| `paths.framework` | Framework directory in the Ahrena repo | `framework/` — tree by language and clade |
| `paths.project_artifacts` | Where to create project-specific artifacts before pushing to framework | `.ahrena/artifacts/` — same structure as framework |
| `paths.oas` | Destination for OpenAPI specifications | E.g. `docs/oas` |
| `paths.events` | Destination for CloudEvents documentation | E.g. `docs/events` |
| `paths.samples.lexis` | Lexis template path | E.g. `templates/lex-sample.md` |
| `paths.samples.codex` | Codex template path | E.g. `templates/codex-sample.md` |
| `paths.samples.katas` | Katas template path | E.g. `templates/kata-sample.md` |
| `paths.samples.warriors` | Warriors template path | E.g. `templates/warrior-sample.md` |
| `paths.samples.cries` | Cries template path | E.g. `templates/cry-sample.md` |

When creating artifacts, always use the paths from `paths.samples` (or the equivalent in `.directives`) to locate the template. For when to use `project_artifacts` vs `framework`, see `codex-paths`.

### Section `language`

| Key | Meaning | Use |
|-----|---------|-----|
| `language.default` | Default framework language | E.g. `pt-BR` — artifacts are created in this language first; source of truth |
| `language.i18n` | List of mandatory languages | E.g. `pt-BR`, `es`, `en` — every framework artifact must exist in all |
| `language.cursor` | Language used in generated Cursor artifacts (`.mdc`) | E.g. `en` — single language in `.cursor/`; no language folders |

See `lex-framework-language` and `codex-framework-language` for the folder structure by language.

### Section `terminal`

| Key | Meaning | Use |
|-----|---------|-----|
| `terminal` | Shell type for commands | Values: `bash` or `powershell` — agents must use this type when proposing or executing commands (see `lex-terminal-type` and `codex-terminal-type`) |

If absent, the agent infers from the operating system or asks the user.

### Section `naming`

| Key | Meaning | Use |
|-----|---------|-----|
| `naming.prefixes.lexis` | Lexis file prefix | `lex-` |
| `naming.prefixes.codex` | Codex file prefix | `codex-` |
| `naming.prefixes.katas` | Katas file prefix | `kata-` |
| `naming.prefixes.warriors` | Warriors file prefix | `warrior-` |
| `naming.prefixes.cries` | Cries file prefix | `cry-` |
| `naming.extensions.framework` | Extension in framework | `.md` |
| `naming.extensions.cursor` | Extension in Cursor (rules) | `.mdc` |
| `naming.casing.files` | File naming convention | E.g. `kebab-case` |
| `naming.casing.directories` | Directory naming convention | E.g. `kebab-case` |
| `naming.addressing` | Artifact addressing pattern | `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}` |
| `naming.reserved_clades` | Clades with special rules (prefix `_`) | E.g. `_foundation` |
| `naming.tone_and_writing_style` | List of tone and style guidelines | Applied when producing artifacts and communication (see `lex-tone` and `codex-tone`) |

See `codex-naming` for details and examples; see `lex-naming` for the law that mandates these conventions.

### Artifact header (block quote)

In the first line of every framework artifact (Lexis, Codex, Katas, Warriors, Cries), the block quote contains **Prefix**, **Type**, and **Scope**. The **Prefix** field **MUST** state the **actual prefix value** (e.g. `lex-`, `codex-`, `kata-`, `warrior-`, `cry-`), and **NOT** only a reference to the directive.

| Form | Correct | Incorrect |
|------|---------|-----------|
| **Prefix** | `**Prefix:** \`lex-\` \| **Type:** ...` | `**Prefix:** per naming.prefixes.lexis in .directives \| ...` |
| Reason | The artifact is self-describing; the reader sees the Pilar prefix immediately | The directive reference requires consulting `.directives` to know the value; in printed docs or outside the repo context, the prefix is ambiguous |

The prefix value MUST match the one defined in `naming.prefixes.{pilar}` in `.directives` (in the Ahrena repo, typically `lex-`, `codex-`, `kata-`, `warrior-`, `cry-`). When creating or reviewing artifacts, use the actual prefix value in the header.

### Extensibility

New sections may be added to `.directives` (e.g. `security`, `notifications`). The agent must interpret unknown sections reasonably. The file **MUST NOT** be modified by the agent without explicit user request (`lex-directives`).

### Relationship with lex-directives

- **lex-directives:** Establishes that every agent MUST read and apply `.directives` before producing artifacts or communication. Defines application per section (paths, language, naming.*).
- **codex-directives:** Explains what each section and key mean and when to use them. Use the Lex for the obligation; use this Codex for interpretation and quick reference.
