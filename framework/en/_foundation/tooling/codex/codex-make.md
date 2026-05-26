# Codex: Makefile of the Ahrena Repository

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Variables, targets, and equivalence without Make for the Makefile at the repository root

## Overview

This Codex is the reference for executing **Makefile** targets at the root of the Ahrena repository. It defines the available variables, targets, usage examples, and **equivalence without Make** (PowerShell/Python commands) for when `make` is not available (e.g. Windows). It is consulted by the specialized make katas (install, update, dev-install, bootstrap, sync-cursor, uninstall, clean) and by the agent when handling `/cry-make`.

## Context

- **Domain:** Installation, update, bootstrap, and maintenance of the Ahrena framework via Makefile or equivalent scripts.
- **Audience:** AI agents that run `/cry-make` or the associated Kata; developers who run `make` or the scripts in PowerShell.
- **Update:** When new targets or variables are added to the Makefile or when the equivalence without Make changes.

## Content

### Variables

| Variable | Description |
|----------|-------------|
| `PLATFORM` | Target platform (e.g. `cursor`) |
| `TARGET` | Project directory (default: `.`) |
| `VERSION` | Tag or branch for remote install/update (default: `main`) |
| `REPO` | GitHub repository URL |
| `SOURCE` | Path to local Ahrena clone (install/update from local) |
| `LOCAL` | If set (e.g. `LOCAL=1`), install/update from current directory as source |
| `LANGUAGE` | Override default language in `.directives` |
| `DIRECTIVES` | Path or URL to custom `.directives` file |
| `CLADES` | Comma-separated clades (default: all) |

**Default:** installation and update are always from **remote** (GitHub). To use a local source, use `SOURCE=/path/to/ahrena` or `LOCAL=1`.

### Available targets

| Target | Description |
|--------|-------------|
| `bootstrap` | First install (downloads installer from GitHub) |
| `install` | Install the framework (default: remote). With `LOCAL=1` or `SOURCE=...`: local |
| `dev-install` | Install from current directory (run from Ahrena repo root) |
| `update` | Update the installation (default: remote). After dev-install use `update LOCAL=1` or `SOURCE=...` to bring the latest from the development environment |
| `sync-cursor` | Regenerate `.cursor/` from `.ahrena/framework/` and `.ahrena/artifacts/` (no download) |
| `uninstall` | Remove the framework installation |
| `clean` | Remove Ahrena-installed files (no confirmation) |

### Usage examples

```powershell
# Remote installation (default)
make install PLATFORM=cursor
make install PLATFORM=cursor VERSION=1.0.0

# Installation from local clone
make install PLATFORM=cursor SOURCE=../ahrena
make install PLATFORM=cursor LOCAL=1

# Bootstrap the environment
make bootstrap

# Remote update (default)
make update

# Update from local (e.g. after dev-install)
make update LOCAL=1
make update SOURCE=../ahrena

# Clean artifacts
make clean
```

### Preference-driven install

The first install of `scripts/install.py` materializes `.directives` from a preference selection. When stdin is a TTY and `--non-interactive` is not passed, the installer prompts the user to toggle every MCP, hook, and optional feature (pre-checked = Full default). For non-interactive runs (CI, scripts), pick a profile and adjust:

```powershell
# Discover the catalog (MCPs, hooks, optional features)
python scripts/install.py --list-catalog

# Full default (no flag, no prompt): every MCP, every hook, every optional feature
python scripts/install.py --self --target . --platform claude-code --non-interactive

# Minimal profile (ahrena MCP + rtk hook only)
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=minimal

# Full minus selected MCPs
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=full --without-mcp=notion,figma

# Standard profile plus the default CODEOWNERS bootstrap (resolves org from `git remote get-url origin`)
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=standard --with-setup=github-codeowners

# Full minus the .gitignore merge (project already manages its own .gitignore)
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=full --without-setup=gitignore-merge
```

Resolution order: explicit `--with-*` / `--without-*` overrides `--profile`, which overrides Full default. The `ahrena` MCP is always kept (framework's own server). Existing `.directives` files are preserved on re-install.

The project setup dimension (`--with-setup` / `--without-setup`) materializes `.github/ISSUE_TEMPLATE/*.yml`, `.github/pull_request_template.md`, `.github/CODEOWNERS` (skipped when the file already exists), and merges a managed block into `.gitignore` between `AHRENA-GITIGNORE` markers (idempotent). Profile defaults: Full ships all four; Standard ships three (no auto-CODEOWNERS, since the org guess from `git remote` is fragile in solo or fork repos); Minimal ships none.

### Equivalence without Make (Windows)

When `make` is not available (e.g. PowerShell on Windows), run the scripts directly:

**Remote installation:**
```powershell
python .ahrena/install.py --target . --version main --repo https://github.com/guardiatechnology/ahrena --platform cursor
```

**Local installation (in the Ahrena repo):**
```powershell
python scripts/install.py --local --target . --platform cursor
```

**Local installation (path):**
```powershell
python .ahrena/install.py --target . --source C:\path\to\ahrena --platform cursor
```

**Remote update (default):**
```powershell
python .ahrena/update.py --target .
```

**Local update:**
```powershell
python .ahrena/update.py --target . --local
# or
python .ahrena/update.py --target . --source C:\path\to\ahrena
```

**Bootstrap (first install):** download the installer from GitHub and run it; in PowerShell, for example:
```powershell
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

**Sync-cursor (regenerate .cursor/):**
```powershell
python .ahrena/update.py --target . --sync-cursor
```

**Uninstall (remove installation):**
```powershell
python .ahrena/uninstall.py --target .
```

**Clean (remove files without confirmation):**
```powershell
python .ahrena/install.py --target . --clean
```

## References

- `Makefile` — Automation file at the repository root
- Make katas (`kata-make-install-framework`, `kata-make-update-framework`, etc.) — Procedure per target (consult this Codex)
- `lex-terminal-type` — Terminal type defined in `.ahrena/.directives`
- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
