# Codex: Makefile of the Ahrena Repository

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Variables, targets, and equivalence without Make for the Makefile at the repository root

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

### Equivalence without Make (Windows)

When `make` is not available (e.g. PowerShell on Windows), run the scripts directly:

**Remote installation:**
```powershell
python .ahrena/install.py --target . --version main --repo https://github.com/guardiafinance/ahrena --platform cursor
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
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
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
