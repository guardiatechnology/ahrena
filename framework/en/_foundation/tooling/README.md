# Tooling — Automation and Tools

> Documentation for Ahrena repository automation tools.

## Overview

The `tooling` Subclade contains artifacts that automate framework development and maintenance tasks. These are Ahrena repository-specific tools (not generic framework tools) that facilitate installation, build, and day-to-day operations.

## Artifact Inventory

### Cries (shortcuts)

| Artifact | Description |
|----------|-------------|
| `cry-make` | Executes Makefile targets in the repository |

## How to Use

### Run the Makefile

```
/cry-make <target> [variables]
```

Examples:

```
/cry-make dev-install PLATFORM=cursor    # Install using local sources
/cry-make bootstrap PLATFORM=cursor      # First-time installation
/cry-make clean                          # Clean temporary artifacts
```

### Available Targets

| Target | Description |
|--------|-------------|
| `dev-install` | Install using local sources (`framework/`) |
| `bootstrap` | First-time installation (downloads from GitHub) |
| `install` | Reinstall from `.ahrena/install.py` |
| `update` | Update to latest version |
| `uninstall` | Remove framework installation |
| `clean` | Remove temporary artifacts |

## References

- `Makefile` — Automation file at repository root
- `scripts/install.py` — Framework installation script
