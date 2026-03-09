# Ahrena: AI-First Capability Framework

**Ahrena** is an AI-first Capability Framework that structures knowledge, processes, and AI agent behavior through a **unified taxonomy** (Clade → Subclade → Pilar). Lexis, Codex, Katas, Warriors, and Cries are organized by discipline and area, guiding how humans and AI collaborate in any domain.

**Principles:** AI as copilot (not pilot); process over tool; artifacts versioned as code; `framework/` as source of truth, platform-agnostic.

---

## Installation

### Prerequisites

- **Python 3.8+** — required for the installer
- **Make** (optional) — for bootstrap and updates
  - **Windows:** `choco install make` or `winget install GnuWin32.Make`
  - **macOS:** Xcode Command Line Tools (`xcode-select --install`)
  - **Linux:** included in most distros (`sudo apt install make`)

### Platforms

| Name | Description |
|------|-------------|
| **Cursor** | IDE with integrated support: the installer generates `.cursor/` (rules, skills, commands, agents) from the framework. [Cursor support](#cursor-support) |

### First-time installation

The installer downloads the framework from GitHub and configures the project (no need to clone the repository).

**Via Makefile (recommended):**

```powershell
# Windows (PowerShell)
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -OutFile Makefile
make bootstrap PLATFORM=cursor
```

```bash
# macOS / Linux
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -o Makefile
make bootstrap PLATFORM=cursor
```

**Via one-liner (no Make):**

```powershell
# Windows — framework only
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py; Remove-Item install.py

# Windows — framework + Cursor IDE
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

```bash
# macOS / Linux — framework + Cursor
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor
```

**Installer options:**

| Flag | Description |
|------|-------------|
| `--platform cursor` | Generate `.cursor/` (rules, skills, commands, agents) |
| `--clades X,Y` | Install only specified clades (e.g. `_foundation,documentation`) |
| `--version v0.1.0` | Specific version (tag or branch) |
| `--language en` | Override default language in `.directives` |
| `--directives PATH` | Use custom `.directives` (local path or URL) |
| `--target PATH` | Install to another directory |
| `--dry-run` | Simulate without making changes |
| `--clean` | Remove files installed by Ahrena |

When `--clades` is used, the selection is saved in `.ahrena/.installed-clades` and respected by `update.py`.

### Update and uninstall

| Action | Makefile | Direct script |
|--------|----------|----------------|
| **Update** | `make update` or `make update VERSION=v0.2.0` | `python .ahrena/update.py` |
| **Uninstall** | `make uninstall` | `python .ahrena/uninstall.py` (or `--force` to skip confirmation) |

**Local development (contributors):** `make dev-install PLATFORM=cursor` — uses local `framework/` sources instead of downloading from GitHub.

### What gets installed

| Command | `.ahrena/` | `.cursor/` |
|---------|------------|------------|
| Without `--platform` | framework, directives, scripts, Makefile | — |
| `--platform cursor` | same | rules, skills, commands, agents |

---

## Pilars (capability types)

| Pilar | Function | Prefix | Details |
|-------|----------|--------|---------|
| **Lexis** | Unbreakable laws (security, quality, process) | `lex-` | [Templates and conventions](./framework/en/README.md#structure) |
| **Codex** | Reference manuals for contextualized decisions | `codex-` | [Templates and conventions](./framework/en/README.md#structure) |
| **Katas** | Repeatable procedures (skills) | `kata-` | [Templates and conventions](./framework/en/README.md#structure) |
| **Warriors** | Specialized agents (persona + scope) | `warrior-` | [Templates and conventions](./framework/en/README.md#structure) |
| **Cries** | Recurring commands (shortcuts) | `cry-` | [Templates and conventions](./framework/en/README.md#structure) |

Full description of each Pilar and when to use it: [Framework — Developer Guide](./framework/en/README.md).

### Clades and Subclades

**Clade** = business discipline. **Subclade** = knowledge area within the discipline. Details and README links per Clade:

| Clade | Subclades | Documentation |
|-------|-----------|----------------|
| **product** | discovery, strategy, analytics, delivery | Extensible by organization |
| **engineering** | platform, backend, frontend, devops, security, quality | [Platform (Guardia)](framework/en/engineering/platform/README.md) |
| **finance** | accounting, treasury, controllership | Extensible by organization |
| **operations** | support, infrastructure, monitoring | Extensible by organization |
| **documentation** | i18n (translation) | [Translation system / Hermes](framework/en/documentation/i18n/README.md) |
| **_foundation** | authoring, contributing, process, quality, security, tooling, i18n | Cross-cutting for all Clades; [Contributing](framework/en/_foundation/contributing/README.md), [Authoring](framework/en/_foundation/authoring/README.md), [Tooling](framework/en/_foundation/tooling/README.md) |

Clades and Subclades are **extensible**: each organization defines what makes sense.

### Available Warriors

| Warrior | Name | Clade | Use |
|---------|------|-------|-----|
| `warrior-translator` | Hermes | documentation/i18n | Technical documentation translation; [details](framework/en/documentation/i18n/README.md) |
| `warrior-daedalus` | Daedalus | engineering/platform | RESTful API design (OAS); `/cry-api-design`, `/cry-full-design` |
| `warrior-kronos` | Kronos | engineering/platform | Event Storm and CloudEvents; `/cry-event-storm`, `/cry-full-design` |

For framework architecture (paths, diagrams, mapping to `.cursor/`), see the [Developer Guide](./framework/en/README.md#framework-architecture).

---

## Cursor support

Ahrena provides **integrated support for Cursor IDE**. With `--platform cursor` (or `PLATFORM=cursor` in the Makefile), the installer generates the `.cursor/` directory from the `framework/`, so that Lexis, Codex, Katas, Warriors, and Cries are available directly in the editor:

| Cursor resource | Origin in framework |
|-----------------|---------------------|
| **Rules** (`.mdc`) | Lexis and Codex — context injected into the agent |
| **Skills** (`SKILL.md`) | Katas and Warriors — capabilities on demand |
| **Commands** (`.md`) | Cries — quick commands via `/cry-name` |
| **Agents** (`.md`) | Warriors — specialized subagents |

Rules are applied automatically according to project scope; skills and commands are available in the chat. To install with Cursor, use `make bootstrap PLATFORM=cursor` or `python install.py --platform cursor`.
