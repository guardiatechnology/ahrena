# Framework — Developer Guide

🇧🇷 [Português](README.md) | 🇪🇸 [Español](README.es.md)

> Practical guide for contributors to the Ahrena repository. For framework usage in projects, see the [main README](../README.md).

## Structure

```
framework/
├── .directives.sample           # Directive template (copied to .ahrena/.directives on install)
├── templates/                   # Base templates for each Pilar
│   ├── lex-sample.md
│   ├── codex-sample.md
│   ├── kata-sample.md
│   ├── warrior-sample.md
│   └── cry-sample.md
│
├── pt-BR/                       # Default language (source of truth)
│   ├── _foundation/
│   │   ├── authoring/           # Artifact creation guides
│   │   ├── contributing/        # Contribution flow and commit
│   │   ├── process/             # Process conventions (checkpoints, directives)
│   │   ├── quality/             # Minimum quality standards
│   │   ├── tooling/             # Automation (Makefile)
│   │   └── i18n/                # Framework language structure
│   ├── engineering/
│   │   └── platform/            # Guardia platform specifications (API, events, Lexis, Codex, Katas, Warriors, Cries)
│   └── documentation/
│       └── i18n/                # Translation system (Hermes)
│
├── en/                          # English (same structure)
└── es/                          # Spanish (same structure)
```

The default language (`pt-BR`) is the **source of truth**. Changes start there and are translated to other languages via `/cry-translate`.

## Development Flow

### 1. Edit artifacts in `framework/`

Edit `.md` files inside `framework/{lang}/`. Follow:

- **Addressing:** `{lang}/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md`
- **Templates:** use templates from `framework/templates/` as base (`lex-template-usage`)
- **i18n:** every change in the default language MUST be propagated to other languages

### 2. Test locally

After editing, regenerate the local installation to validate that Cursor artifacts are generated correctly:

```bash
make dev-install PLATFORM=cursor
```

This copies `framework/` to `.ahrena/framework/`, generates `.cursor/` (rules, skills, commands, agents), and preserves the existing `.directives`.

### 3. Verify generated artifacts

The installer converts each Pilar into the native Cursor format:

| Pilar | Source | Cursor Destination |
|-------|--------|-------------------|
| Lexis | `framework/{lang}/.../lexis/lex-*.md` | `.cursor/rules/.../lex-*.mdc` |
| Codex | `framework/{lang}/.../codex/codex-*.md` | `.cursor/rules/.../codex-*.mdc` |
| Katas | `framework/{lang}/.../katas/kata-*.md` | `.cursor/skills/kata-*/SKILL.md` |
| Warriors | `framework/{lang}/.../warriors/warrior-*.md` | `.cursor/skills/warrior-*/SKILL.md` + `.cursor/agents/warrior-*.md` |
| Cries | `framework/{lang}/.../cries/cry-*.md` | `.cursor/commands/.../cry-*.md` |

The language used to generate Cursor artifacts is defined by `language.cursor` in `.directives` (default: `en`).

### 4. Commit

Use `/cry-commit` to create compliant commits. The 4 commit Lexis are:

- `lex-conventional-commits` — format `type(scope): description`
- `lex-small-commits` — one purpose per commit
- `lex-commit-language` — subject in English
- `lex-signed-commits` — mandatory GPG signature

### 5. Version a release (tags)

Use `/cry-tag` to create or list release tags in SemVer format. The `kata-tag` applies `lex-semantic-version` and `lex-signed-commits`. See `_foundation/contributing/README.md` for the full artifact inventory.

### 6. Contribute

Use `/cry-contribute pr` to open the Pull Request. The `kata-contribute` guides the entire flow via MCP.

## Creating New Artifacts

### Via commands (recommended)

```
/cry-new-lex          # New Lexis
/cry-new-codex        # New Codex
/cry-new-kata         # New Kata
/cry-new-warrior      # New Warrior
/cry-new-cry          # New Cry
```

Each command invokes the corresponding kata (`kata-create-*`) which:
1. Uses the official template as base
2. Places the artifact in the correct taxonomy
3. Creates it in all 3 required languages

### Manually

1. Copy the template from `framework/templates/{pilar}-sample.md`
2. Place it in `framework/pt-BR/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md`
3. Fill in the required sections
4. Translate to `en/` and `es/` (via `/cry-translate`)
5. Run `make dev-install PLATFORM=cursor` to validate

## Conventions

| Aspect | Standard |
|--------|----------|
| File casing | `kebab-case` (`lex-no-secrets.md`) |
| Directory casing | `kebab-case` (`engineering/backend/`) |
| Framework extension | `.md` |
| Cursor extension | `.mdc` (rules), `.md` (skills, commands, agents) |
| Prefixes | `lex-`, `codex-`, `kata-`, `warrior-`, `cry-` |
| Reserved Clades | `_foundation` (prefix `_`) |

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make dev-install PLATFORM=cursor` | Install using local sources |
| `make bootstrap PLATFORM=cursor` | First-time install (downloads from GitHub) |
| `make install PLATFORM=cursor` | Reinstall from `.ahrena/install.py` |
| `make update` | Update to latest version |
| `make clean` | Remove installed files |

## References

- [Main README](../README.md) — Ahrena public documentation
- [Translation System](pt-BR/documentation/i18n/README.md) — Hermes documentation
- `.ahrena/.directives` — Framework canonical directives
- `_foundation/contributing/codex/codex-contributing` — Contribution flow
- `_foundation/contributing/katas/kata-contribute` — PR procedure
