# Getting Started

Ahrena is an **AI-First capability framework** — a collection of Lexis (laws), Codex (guides), Katas (skills), and Warriors (agents) that transforms any AI-enabled IDE into a standardized, auditable engineering environment.

Installing Ahrena in a project means every AI agent operating in it shares the same rules, the same vocabulary, and the same workflows.

---

## Prerequisites

| Requirement | Minimum version |
|---|---|
| Python | 3.9+ |
| make | any modern version |
| AI-enabled IDE | Cursor or Claude Code |

=== "macOS / Linux"

    ```bash
    python3 --version
    make --version
    ```

=== "Windows"

    ```powershell
    python --version
    # make via chocolatey or winget
    winget install GnuWin32.Make
    ```

---

## Installation

### Bootstrap (first use)

The `bootstrap` command downloads the installer directly from the latest GitHub release and runs the installation in the current project.

=== "macOS / Linux"

    ```bash
    make bootstrap
    ```

=== "Windows"

    ```powershell
    make bootstrap
    ```

This creates the `.ahrena/` directory at the project root with the framework installed and generates the configuration files for the detected platform (Cursor or Claude Code).

### Explicit platform

By default, the installer automatically detects which IDE is present. To force a platform:

```bash
# Cursor
make bootstrap PLATFORM=cursor

# Claude Code
make bootstrap PLATFORM=claude-code
```

### Language

The default language is `pt-BR`. To install in another language:

```bash
make bootstrap LANGUAGE=en
make bootstrap LANGUAGE=es
```

### Selective clades

To install only the clades relevant to the project (reduces noise from irrelevant rules):

```bash
# Backend and platform only
make bootstrap CLADES=engineering/backend,engineering/platform

# Workflow and contributing only
make bootstrap CLADES=_foundation/contributing,engineering/workflow
```

---

## Update

After the initial bootstrap, use `update` to fetch the latest framework version:

```bash
make update
```

To update to a specific version:

```bash
make update VERSION=v1.2.0
```

---

## Sync

If you already have Ahrena installed and only need to regenerate the IDE configuration files (without downloading anything):

```bash
# Regenerates .cursor/
make sync-cursor

# Regenerates .claude/ and CLAUDE.md
make sync-claude-code
```

Useful after manually editing directives or after a `git pull` that brought changes to the framework.

---

## Removal

```bash
# With interactive confirmation
make uninstall

# Without confirmation (CI, scripts)
make clean
```

---

## Dev Mode

Dev mode is for those who want to **contribute to Ahrena itself** — testing local framework changes before submitting a PR.

### Why it exists

`make bootstrap` and `make install` always download the framework from GitHub. `make dev-install` ignores the network and uses the local repository code as the source — allowing iteration without commit/push.

### Setup

Clone the Ahrena repository and, inside it, run:

```bash
# Install the framework from local code in the current project
make dev-install
```

To install in another project from this local copy:

```bash
make install-to TARGET=/path/to/the/project
```

### Typical contribution workflow

```
1. fork + clone guardiafinance/ahrena
2. create the branch: feat/{issue}-{slug}
3. edit artifacts in framework/
4. make dev-install           ← install locally to test
5. test in the configured IDEs
6. make validate              ← validate structure and coverage
7. commit (GPG-signed, Conventional Commits)
8. /cry-new-pr                ← open the PR following standards
```

### Available variables in dev

```bash
make dev-install PLATFORM=cursor LANGUAGE=en CLADES=engineering/backend
make dev-install TARGET=../my-other-project
```

---

## Command Reference

| Command | What it does |
|---|---|
| `make bootstrap` | First install (downloads installer from GitHub) |
| `make install` | Reinstall from `.ahrena/install.py` |
| `make dev-install` | Install from local code (dev mode) |
| `make install-to TARGET=…` | Install this repo into another project (offline) |
| `make update` | Update to the latest version |
| `make sync-cursor` | Regenerate `.cursor/` without downloading anything |
| `make sync-claude-code` | Regenerate `.claude/` and `CLAUDE.md` |
| `make validate` | Validate framework structure and consistency |
| `make uninstall` | Remove Ahrena with confirmation |
| `make clean` | Remove installed files without confirmation |

---

## Next Steps

- [Core Concepts](ahrena/concepts.md) — understand Lexis, Codex, Katas, Warriors, and Cries
- [Cries Catalog](ahrena/cries.md) — all commands available in the IDEs
- [Katas Catalog](ahrena/katas.md) — all executable skills
- [Contributing](https://github.com/guardiafinance/ahrena/blob/main/CONTRIBUTING.md) — how to contribute to the framework
