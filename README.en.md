# Ahrena: AI-First Capability Framework

**Ahrena** is an AI-first Capability Framework that structures knowledge, processes, and AI agent behavior through a **unified taxonomy** (Clade → Subclade → Pilar). Lexis, Codex, Katas, Warriors, and Cries are organized by discipline and area, guiding how humans and AI collaborate in any domain.

**Principles:** AI as copilot (not pilot); process over tool; artifacts versioned as code; `framework/` as source of truth, platform-agnostic.

---

## Installation

### Prerequisites

Ahrena verifies the host in three tiers during `make bootstrap` / `make install` (preflight). Run `make preflight` to execute the checks in isolation.

**Hard (blocks the install if missing):**
- **Python 3.8+** — interpreter for the scripts
- **git** — version control
- **make** — Makefile entrypoint

**Soft (warns and offers to install):**
- **gh** (GitHub CLI) — used by the Issue-Driven flow, stacked PRs, and the cost-stamp
- **gpg** — required by `lex-signed-commits`

**Lazy (installed on demand when the corresponding MCP is activated via `make mcp-enable`):**
- **Node.js** — only for the Figma MCP server (npx tier). GitHub and Notion use remote HTTP, with no local dependency.

**How to install manually:**
- **Windows:** `winget install --id Git.Git -e`, `winget install --id GnuWin32.Make -e`, `winget install --id GitHub.cli -e`, `winget install --id GnuPG.Gpg4win -e`, `winget install --id OpenJS.NodeJS.LTS -e`.
- **macOS:** `xcode-select --install` covers git and make (via Command Line Tools); `brew install gh gnupg node` for the rest.
- **Linux (Debian/Ubuntu):** `sudo apt-get install -y git build-essential gh gnupg nodejs npm`. RHEL/Fedora: `sudo dnf install -y git gh gnupg2 nodejs npm` + `sudo dnf groupinstall -y 'Development Tools'`.

### Platforms

| Name | Description |
|------|-------------|
| **Cursor** | IDE with integrated support: the installer generates `.cursor/` (rules, skills, commands, agents) from the framework. [Cursor support](#cursor-support) |
| **Claude Code** | Claude Code support: the installer generates `.claude/` (docs, skills, commands, agents) and `CLAUDE.md` from the framework. [Claude Code support](#claude-code-support) |

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

# Windows — framework + Claude Code
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform claude-code; Remove-Item install.py
```

```bash
# macOS / Linux — framework + Cursor
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor

# macOS / Linux — framework + Claude Code
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform claude-code
```

**Installer options:**

| Flag | Description |
|------|-------------|
| `--platform cursor` | Generate `.cursor/` (rules, skills, commands, agents) |
| `--platform claude-code` | Generate `.claude/` (docs, skills, commands, agents) and `CLAUDE.md` |
| `--clades X,Y` | Install only specified clades (e.g. `_foundation,documentation`) |
| `--version v0.1.0` | Specific version (tag or branch) — remote install |
| `--local` | Use current directory as source (run from Ahrena repo root) |
| `--source PATH` | Use a local Ahrena clone at PATH instead of downloading from GitHub |
| `--self` | Use the Ahrena repo containing this script as source — offline install |
| `--language en` | Override default language in `.directives` |
| `--directives PATH` | Use custom `.directives` (local path or URL) |
| `--target PATH` | Install to another directory |
| `--dry-run` | Simulate without making changes |
| `--clean` | Remove files installed by Ahrena |

When `--clades` is used, the selection is saved in `.ahrena/.installed-clades` and respected by `update.py`.

### Offline installation

If there is no internet access, or you want to distribute Ahrena in restricted environments, use the `--self` flag from a local clone of the repository:

```bash
# Clone the repo once (with network access)
git clone https://github.com/guardiafinance/ahrena.git

# Install into any project, from any directory, without network
python /path/to/ahrena/scripts/install.py --self --target /path/to/project --platform cursor
python /path/to/ahrena/scripts/install.py --self --target /path/to/project --platform claude-code
```

**Via Makefile** (from the Ahrena repo root):

```bash
make install-to TARGET=/path/to/project PLATFORM=cursor
make install-to TARGET=/path/to/project PLATFORM=claude-code LANGUAGE=en
```

`--self` automatically detects the Ahrena repo root from the script's own location, regardless of the current working directory.

### Update and uninstall

| Action | Makefile | Direct script |
|--------|----------|----------------|
| **Update (remote)** | `make update` or `make update VERSION=v0.2.0` | `python .ahrena/update.py` |
| **Update (local)** | `make update LOCAL=1` or `make update SOURCE=../ahrena` | `python .ahrena/update.py --local` or `--source /path/to/ahrena` |
| **Re-sync Cursor** | `make sync-cursor` | `python .ahrena/update.py --sync-cursor` |
| **Re-sync Claude Code** | `make sync-claude-code` | `python .ahrena/update.py --sync-claude-code` |
| **Uninstall** | `make uninstall` | `python .ahrena/uninstall.py` (or `--force` to skip confirmation) |

**Default:** install and update come from **remote** (GitHub). For local source use `--local` / `--source` or in the Makefile `LOCAL=1` / `SOURCE=...`.

**Local development (contributors):** `make dev-install PLATFORM=cursor` — installs from the current directory (Ahrena repo root). To bring in the latest from the dev environment, use `make update LOCAL=1` or `make update SOURCE=...` in the installed project.

### What gets installed

| Command | `.ahrena/` | `.cursor/` | `.claude/` + `CLAUDE.md` |
|---------|------------|------------|--------------------------|
| Without `--platform` | framework, directives, scripts, Makefile | — | — |
| `--platform cursor` | same | rules, skills, commands, agents | — |
| `--platform claude-code` | same | — | docs, skills, commands, agents + CLAUDE.md |

---

## MCP (Model Context Protocol)

Ahrena supports MCP servers for GitHub, Notion, and Figma. When enabled, the installer automatically generates the corresponding entries in `.cursor/mcp.json` and `.claude/settings.json`.

### Enabling MCP servers

Add the `mcp` section to your `.ahrena/.directives`:

```yaml
mcp:
  servers:
    - github
    - notion
    - figma
```

On the next run of `make sync-cursor`, `make sync-claude-code`, or `make install-to`, MCP entries will be merged **additively** — servers you manage outside Ahrena are preserved.

### Available servers

| Server | Environment variable | Use |
|--------|---------------------|-----|
| `github` | `GITHUB_PAT` | Create issues, PRs, push files, list commits |
| `notion` | `NOTION_API_KEY` | Create and sync pages, search databases |
| `figma` | `FIGMA_API_KEY` | Extract design tokens, component specs, export frames |

Credentials are always referenced via environment variables — **never** hardcoded in versioned files.

### MCP Katas

| Kata | Platform | Description |
|------|----------|-------------|
| `kata-mcp-github-read` | GitHub | Queries repositories, issues, PRs, commits, and code (read-only) |
| `kata-mcp-notion-read` | Notion | Queries Notion pages, databases, and blocks (read-only) |
| `kata-mcp-figma-extract` | Figma | Extracts design tokens and component specs from Figma |

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
| **engineering** | platform, backend, frontend, devops, security, quality, workflow | [Platform (Guardia)](framework/en/engineering/platform/README.md) · [Workflow (Issue-Driven)](framework/en/engineering/workflow/README.md) · Backend (Apollo) · Frontend (Hephaestus) · DevOps (Atlas) |
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
| `warrior-apollo` | Apollo | engineering/backend | Python implementation with Clean Architecture; `/cry-python-implement` |
| `warrior-hephaestus` | Hephaestus | engineering/frontend | Frontend implementation (React/TS) with a11y and behavioral testing |
| `warrior-atlas` | Atlas | engineering/devops | AWS solutions architecture; Well-Architected; IaC and cost |
| `warrior-hera` | Hera | engineering/quality | Test strategy, coverage planning, suite audit |
| `warrior-hestia` | Hestia | engineering/sre | SLO, runbooks, incident response, blameless post-mortem |
| `warrior-demeter` | Demeter | engineering/data | Data modeling, safe migrations, LGPD/GDPR retention |
| `warrior-iris` | Iris | engineering/mobile | iOS/Android parity implementation, offline-first, accessibility |
| `warrior-athena` | Athena | engineering/workflow | Issue-Driven flow orchestrator; `/cry-implement-issue` |

For framework architecture (paths, diagrams, mapping to `.cursor/`), see the [Developer Guide](./framework/en/README.md#framework-architecture).

---

## Issue-Driven Development Flow

Ahrena provides a **complete development flow driven by GitHub issues**, led by `warrior-athena`. Starting from an issue, the flow goes through 7 phases (analysis → requirements → architecture → implementation → security → quality gate → PR), with 2 human/automated gates, ADR generation (`docs/adr/`), and documentation structured under `docs/issues/issue-{n}/`.

```bash
# Prerequisite: mcp.servers includes github (and optionally notion) in .ahrena/.directives
/cry-implement-issue 42 guardiafinance/ahrena
```

**Gate 1 (Scope):** human approves brief + ACs + architecture before implementation.
**Gate 2 (Quality):** automated with 6 checks — AC↔test traceability (bidirectional), scope creep, best practices, tests, coverage, types.

Full guide: [engineering/workflow/README.md](framework/en/engineering/workflow/README.md).

---

## Workflow Status

Per ADR-002 (Issue-as-plan model), the canonical plan lives in three layers:

1. **GitHub Issue body** — canonical. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Audit log = GitHub's native timeline.
2. **`.plans/{N}.md`** (gitignored) — AI working memory. Superset of the Issue body + `<!-- not-flushed -->` blocks for scratch. Materialized by `kata-load-plan-from-issue`; flushed by `kata-flush-plan-to-issue`.
3. **`.issues/{N}/`** (committed) — Phase artifacts (`01-brief.md` … `06-quality-report.md`) from the Issue-Driven flow.

The `status:` enum lives as a **label** on the Issue (and on the PR starting at `to review`), split into two disjoint axes (`lex-issue-status`):

**Axis A — Dev cycle** (feature/fix/chore Issues/PRs):
```
todo → development → to review → review → done
                          ↘
                          abandoned (alternative terminal)
```

**Axis B — Release cycle** (dedicated release Issue created by Janus):
```
to release → release → done
                  ↘
                  abandoned
```

Mutex is **intra-artifact** (each Issue/PR carries exactly one `status:*` label); cross-axis labeling is forbidden by the `lex-issue-status` HARD-GATE.

Transition owners (`lex-agent-planning`):

| Transition | Owner | Axis |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: session agent) | A |
| `todo → development → to review` | `warrior-athena` | A |
| `to review ↔ review` | `warrior-argos` | A |
| `to review → done` | `warrior-athena` (on merge) | A |
| `— → to release → release → done` | `warrior-janus` (dedicated release Issue with `Tracks: #N1, ...`) | B |

Create the canonical labels with `scripts/bootstrap_status_labels.sh [owner/repo]`.

**Load/flush cadence:** synchronization between `.plans/{N}.md` and the Issue body runs on 3 canonical triggers: (a) each `status:` label transition, (b) each Step marked as completed, (c) end of session (heartbeat finishes). Intermediate toggles and scratch edits (`<!-- not-flushed -->`) are free. Operational documentation in `codex-agent-planning`.

**3×15min loop:** after opening the PR, Athena schedules 3 cycles of 15 min and nudges the human reviewer via the notification MCP (`notifications.provider` in `.ahrena/.directives`, channel `notifications.channels.pr_review_timeout`) if no approval lands on the third cycle. Manuals: `codex-notifications` (provider-agnostic) and `codex-mcp-slack` (initial provider).

---

## Cursor support

Ahrena provides **integrated support for Cursor IDE**. With `--platform cursor` (or `PLATFORM=cursor` in the Makefile), the installer generates the `.cursor/` directory from the `framework/`, so that Lexis, Codex, Katas, Warriors, and Cries are available directly in the editor:

| Cursor resource | Origin in framework |
|-----------------|---------------------|
| **Rules** (`.mdc`) | Lexis and Codex — context injected into the agent |
| **Skills** (`SKILL.md`) | Katas and Warriors — capabilities on demand |
| **Commands** (`.md`) | Cries — quick commands via `/cry-name` |
| **Agents** (`.md`) | Warriors — specialized subagents |

Rules are applied automatically according to project scope; skills and commands are available in the chat.

**Platform configuration:** transposition (which Pilar becomes which resource) and rule application (alwaysApply, globs, description) are defined in **`platforms.yaml`** (default in `framework/platforms.yaml`, override in `.ahrena/platforms.yaml`). See [codex-platforms](framework/en/_foundation/process/codex/codex-platforms.md) for details.

---

## Claude Code support

Ahrena provides **integrated support for Claude Code**. With `--platform claude-code`, the installer generates `.claude/` and `CLAUDE.md` from the `framework/`:

| Claude Code resource | Origin in framework |
|----------------------|---------------------|
| **Docs** (`.md`) | Lexis and Codex — reference documentation injected into context |
| **Skills** (`SKILL.md`) | Katas — repeatable procedures on demand |
| **Commands** (`.md`) | Cries — quick commands via `/cry-name` |
| **Agents** (`.md`) | Warriors — specialized subagents |
| **CLAUDE.md** | Essential Lexis injected directly into session context |

The `claude-code.docs` configuration in `platforms.yaml` controls which artifacts are injected directly into `CLAUDE.md` (`essential: true`) versus listed as references (`essential: false`).

---

## Structure validator

Ahrena includes a validator to ensure framework content follows conventions before transposition.

```bash
# Validate everything
make validate
# or
python scripts/validate.py

# Validate specific checks
python scripts/validate.py --check naming,platforms
```

| Check | What it validates |
|-------|------------------|
| `naming` | Every `.md` starts with a Pilar prefix or is `README.md` |
| `path` | File is in the correct Pilar directory (`lexis/`, `katas/`, etc.) |
| `sections` | Required sections are present (law in Lexis, workflow in Kata, etc.) |
| `i18n` | Every file in `pt-BR/` has a counterpart in `en/` and `es/` |
| `platforms` | Every `lex-` and `codex-` has an entry in `cursor.rules` in `platforms.yaml` |

Exit code `0` = all passed; `1` = violations found. Can be used as a pre-commit hook.
