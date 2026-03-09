# Ahrena: AI-First Capability Framework

**Ahrena** is an AI-first Capability Framework that structures knowledge, processes, and AI agent behavior through a **unified taxonomy** applicable to any business discipline.

Unbreakable laws (Lexis), knowledge bases (Codex), repeatable procedures (Katas), specialized agents (Warriors), and recurring commands (Cries) are organized by discipline (Clade) and knowledge area (Subclade), creating an extensible system that guides how humans and AI collaborate in any domain.

### Principles

1. **AI as Copilot, not Pilot:** Humans retain final control over critical decisions
2. **Process over Tool:** Process standardization takes priority over tool standardization
3. **Artifacts as Code:** Laws, manuals, procedures, and commands are versioned, auditable, and portable
4. **Platform Agnostic:** `framework/` is the source of truth; `.cursor/` and other IDEs are derivations

---

## Installation

### Prerequisites

- **Python 3.8+** — required to run the installer
- **Make** (optional) — for bootstrap and updates via Makefile
  - **Windows:** `choco install make` or `winget install GnuWin32.Make`
  - **macOS:** included with Xcode Command Line Tools (`xcode-select --install`)
  - **Linux:** included in most distributions (`sudo apt install make`)

### First Installation

The installer downloads the framework from GitHub and configures the project. Cloning the repository is not required.

#### Via Makefile (recommended)

Download the `Makefile` to the project root and use `make bootstrap`. The Makefile can be committed to the repository so the entire team uses the same workflow.

**macOS / Linux:**

```bash
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -o Makefile
make bootstrap PLATFORM=cursor
```

**Windows (PowerShell):**

```powershell
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -OutFile Makefile
make bootstrap PLATFORM=cursor
```

**With options:**

```bash
make bootstrap PLATFORM=cursor VERSION=v0.1.0 LANGUAGE=en
make bootstrap PLATFORM=cursor CLADES=_foundation,documentation
make bootstrap  # framework only, no platform
```

#### Via one-liner (without Make)

**macOS / Linux:**

```bash
# Framework only (.ahrena/)
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 -

# Framework + Cursor IDE
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor

# Specific version + default language
curl -sSL https://github.com/guardiafinance/ahrena/releases/download/v0.1.0/install.py | python3 - --version v0.1.0 --language en --platform cursor

# Specific clades only
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --clades _foundation,documentation --platform cursor
```

**Windows (PowerShell):**

```powershell
# Framework only (.ahrena/)
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py; Remove-Item install.py

# Framework + Cursor IDE
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

### Update

The update automatically detects the installed platform and preserves the `.directives`:

**Via Makefile (project root):**

```bash
make update
make update VERSION=v0.2.0
```

**Via Makefile (.ahrena/):**

```bash
make -f .ahrena/Makefile update
```

**Via direct script:**

```bash
# macOS / Linux
python3 .ahrena/update.py
python3 .ahrena/update.py --version v0.2.0

# Windows (PowerShell)
python .ahrena/update.py
python .ahrena/update.py --version v0.2.0
```

### Uninstallation

Removes all files installed by Ahrena (`.ahrena/` and files generated in `.cursor/` — rules, skills, commands, and agents). Prompts for confirmation before removing.

**Via Makefile:**

```bash
make uninstall
```

**Via direct script:**

```bash
# macOS / Linux
python3 .ahrena/uninstall.py
python3 .ahrena/uninstall.py --force    # no confirmation

# Windows (PowerShell)
python .ahrena/uninstall.py
python .ahrena/uninstall.py --force
```

### Local Development (for Ahrena contributors)

If you are working on the Ahrena repository and want to test framework changes locally:

```bash
make dev-install PLATFORM=cursor
```

This uses local sources from `framework/` instead of downloading from GitHub. The `.ahrena/` and `.cursor/` directories are regenerated from the current repository state.

### Options

| Flag | Description |
|------|-------------|
| `--platform cursor` | Generate `.cursor/` (rules, skills, commands, agents) |
| `--local` | Use local sources (for framework development) |
| `--clades X,Y` | Install only the specified clades (e.g., `_foundation,documentation`) |
| `--version v0.1.0` | Specific version (tag or branch) |
| `--language en` | Override the default language in `.directives` |
| `--directives PATH` | Use a custom `.directives` (local path or URL) |
| `--target PATH` | Install to a different directory |
| `--dry-run` | Show what would be done without making changes |
| `--clean` | Remove files installed by Ahrena |

> **Note:** when `--clades` is used, the selection is saved in `.ahrena/.installed-clades` and automatically respected by `update.py`. To change the clades during an update, pass `--clades` again.

### What Gets Installed

| Command | `.ahrena/` | `.cursor/` |
|---------|------------|------------|
| Without `--platform` | framework + directives + scripts + Makefile | — |
| `--platform cursor` | framework + directives + scripts + Makefile | rules, skills, commands, agents |

---

## Taxonomy

Ahrena organizes knowledge into **three levels**:

```
Clade (discipline) → Subclade (area) → Pilar (capability type) → Capability
```

### Pilares

Pilares define the **type** of each capability. There are five:

#### Lexis — Unbreakable Laws

Absolute security, quality, or process constraints that **no agent — human or AI — can violate**.

| Aspect | Detail |
|--------|--------|
| **Nature** | Restrictive and imperative — defines what **never** can happen or what **always** must happen |
| **Prefix** | `lex-` |
| **When to use** | When there is risk of security, quality, or critical process violation |
| **Governance** | No exceptions; automated validation whenever possible |
| **Template** | [`framework/templates/lex-sample.md`](framework/templates/lex-sample.md) |

#### Codex — Reference Manuals

Structured knowledge base that AI consults to make contextualized decisions.

| Aspect | Detail |
|--------|--------|
| **Nature** | Informative and guiding — defines **how** the system works |
| **Prefix** | `codex-` |
| **When to use** | When a relevant decision, standard, or convention needs documentation |
| **Governance** | Updated with every relevant decision or structural change; consulted by team and AI |
| **Template** | [`framework/templates/codex-sample.md`](framework/templates/codex-sample.md) |

#### Katas — Repeatable Skills

Procedures that define how agents execute recurring tasks in a standardized way, with inputs, outputs, and validation criteria.

| Aspect | Detail |
|--------|--------|
| **Nature** | Procedural — defines **what to do** step by step |
| **Prefix** | `kata-` |
| **When to use** | When a recurring task needs standardized execution |
| **Governance** | Validation criteria verified before delivery |
| **Template** | [`framework/templates/kata-sample.md`](framework/templates/kata-sample.md) |

#### Warriors — Specialized Agents

AI agents with defined identity, scope, and responsibilities. Each Warrior consults relevant Lexis, Codex, and Katas.

| Aspect | Detail |
|--------|--------|
| **Nature** | Persona — defines **who** the agent is and how it behaves |
| **Prefix** | `warrior-` |
| **When to use** | When a specialized agent with defined identity and scope is needed |
| **Governance** | Links Lexis, Codex, and Katas; clear escalation criteria to human |
| **Template** | [`framework/templates/warrior-sample.md`](framework/templates/warrior-sample.md) |

#### Cries — Recurring Commands

Productivity shortcuts that automate repetitive tasks. They differ from Katas by being quick invocations, not complete procedures.

| Aspect | Detail |
|--------|--------|
| **Nature** | Invocation — defines a quick, reusable **shortcut** |
| **Prefix** | `cry-` |
| **When to use** | When a simple, repetitive task can be automated via a quick command |
| **Governance** | Low complexity (1-2 steps); invoked via `/cry-[name]` in chat |
| **Template** | [`framework/templates/cry-sample.md`](framework/templates/cry-sample.md) |

---

### Clades and Subclades

**Clade** — Business discipline. Groups all knowledge relevant to a single discipline.

**Subclade** — Knowledge area within the discipline. Refines the Clade scope by specialty.

#### Product

Product management, lifecycle, and strategy. Covers from opportunity discovery to continuous value delivery to the user.

| Subclade | Focus |
|----------|-------|
| Discovery | Research, hypothesis validation, and prioritization |
| Strategy | Product vision, roadmap, and success metrics |
| Analytics | Usage data, experimentation, and insights |
| Delivery | Release planning, rollout, and communication |

#### Engineering

Development, architecture, and infrastructure. Spans the entire technical cycle — from code to deploy — including quality and security.

| Subclade | Focus |
|----------|-------|
| **Platform** | Guardia platform specifications: Lexis/Codex (RESTful, CloudEvents, entities, auth), Katas (API design OAS/doc, events documentation), Warriors (Daedalus — API, Kronos — Event Storm), and Cries (api-design, event-storm, full-design). Destinations: `docs/oas`, `docs/events`. [Details](framework/pt-BR/engineering/platform/README.md) |
| Backend | APIs, services, business logic, and integrations |
| Frontend | Interfaces, components, and developer experience |
| DevOps | CI/CD, infrastructure as code, and observability |
| Security | Data protection, authentication, and technical compliance |
| Quality | Testing, code review, and quality standards |

#### Finance

Financial management, accounting, and controllership. Structures processes that require precision, traceability, and compliance with fiscal and accounting standards.

| Subclade | Focus |
|----------|-------|
| Accounting | Journal entries, reconciliation, and accounting close |
| Treasury | Cash flow, payments, receivables, and liquidity management |
| Controllership | Financial planning, budgeting, management reports, and KPIs |

#### Operations

Operational processes and support. Ensures that systems and teams operate stably and efficiently on a daily basis.

| Subclade | Focus |
|----------|-------|
| Support | Customer service, escalation, and knowledge base |
| Infrastructure | Servers, networks, capacity, and disaster recovery |
| Monitoring | Alerts, dashboards, and incident response |

#### Documentation

Translation, internationalization, and technical documentation management. Contains generic artifacts that apply to any type of documentation — framework, project, or any other technical content.

| Subclade | Focus |
|----------|-------|
| i18n | Multilingual translation — per-language rules, procedures, translator agent, and command |

> The `documentation/i18n/` Clade includes **Warrior Hermes** — a specialist translator agent that consults target-language-specific rules and guides (pt-BR, en, es) to ensure precise and consistent translations. For complete details, see the [Translation System README](framework/pt-BR/documentation/i18n/README.md).

#### _Foundation — Cross-Cutting Clade

_Foundation is a **special Clade** that does not belong to a specific discipline. Its artifacts operate **cross-functionally**, applying to all other Clades simultaneously.

While Clades like Product or Engineering contain discipline-specific knowledge, _Foundation defines the **rules, processes, and standards that cut across all of them** — global security, minimum quality, and common processes that every agent and every artifact must respect, regardless of domain.

| Subclade | Focus |
|----------|-------|
| Authoring | Artifact creation guides (how to create Lexis, Codex, Katas, Warriors, and Cries) |
| Contributing | Unified contribution flow, commit standards, and PR creation |
| Process | SDLC, workflows, and conventions common to all disciplines |
| Quality | Minimum quality standards valid for any artifact |
| Security | Security policies applicable to the entire system |
| Tooling | Automation and development tools (Makefile, installer) |
| i18n | Per-language folder structure within `framework/` — navigation and mirroring rules |

> In practice: a Lexis in `_foundation/security/` applies to **all** Clades — not just Engineering. When creating an artifact in any Clade, the agent must consult _Foundation first to ensure compliance with cross-cutting rules.

---

> Clades and Subclades are **extensible**: each organization creates whichever ones make sense for its context.

### Available Warriors

Warriors are specialized agents ready for use. Ahrena includes the following built-in Warriors:

| Warrior | Name | Clade | Description |
|---------|------|-------|-------------|
| `warrior-translator` | **Hermes** | `documentation/i18n` | Technical documentation translator. Consults target-language-specific rules and guides (pt-BR, en, es) to ensure precise translations. Invocable via `/cry-translate`. [Complete documentation](framework/pt-BR/documentation/i18n/README.md) |
| `warrior-daedalus` | **Daedalus** | `engineering/platform` | RESTful API design specialist. Produces OpenAPI specification and API document in `docs/oas`. Invocable via `/cry-api-design` or `/cry-full-design`. |
| `warrior-kronos` | **Kronos** | `engineering/platform` | Event Storm and CloudEvents documentation specialist. Produces events documentation in `docs/events`. Invocable via `/cry-event-storm` or `/cry-full-design`. |

#### Addressing

The language is always the first path segment in the framework:

```
{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md
```

| Path | Reading |
|------|---------|
| `pt-BR/_foundation/security/lexis/lex-security.md` | Cross-cutting security law in pt-BR |
| `en/product/discovery/codex/codex-prioritization.md` | Prioritization manual in English |
| `es/engineering/security/lexis/lex-no-secrets.md` | Secrets law in Spanish |
| `pt-BR/documentation/i18n/warriors/warrior-translator.md` | Hermes agent (translator) in pt-BR |
| `pt-BR/engineering/platform/warriors/warrior-daedalus.md` | Daedalus agent (API design) in pt-BR |
| `pt-BR/engineering/platform/warriors/warrior-kronos.md` | Kronos agent (event storm) in pt-BR |
| `en/engineering/quality/warriors/warrior-spartacus.md` | Spartacus agent in English |

#### Visualization

```
┌───────────────────────────────────────────────────────────────────┐
│                        AHRENA TAXONOMY                            │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Clade               Subclade              Pilar                  │
│  ─────               ────────              ─────                  │
│                                                                   │
│  product/ ──────┬── discovery/ ──────────┬── lexis/               │
│                 ├── strategy/            ├── codex/               │
│                 ├── analytics/           ├── katas/               │
│                 └── delivery/            ├── warriors/            │
│                                          └── cries/               │
│  engineering/ ──┬── platform/     Daedalus, Kronos (API + events) │
│                 ├── backend/                                      │
│                 ├── frontend/                                     │
│                 ├── devops/                                       │
│                 ├── security/                                     │
│                 └── quality/                                      │
│                                                                   │
│  finance/ ──────┬── accounting/                                   │
│                 ├── compliance/                                   │
│                 └── reporting/                                    │
│                                                                   │
│  operations/ ───┬── support/                                      │
│                 ├── infrastructure/                               │
│                 └── monitoring/                                   │
│                                                                   │
│  documentation/ ──── i18n/           Hermes (translator)          │
│                                                                   │
│  ═══════════════════════════════════════════════════════          │
│  _foundation/ ──┬── authoring/      ← applies to ALL              │
│  (cross-cutting)├── contributing/     Clades above                │
│                 ├── process/                                      │
│                 ├── quality/                                      │
│                 ├── security/                                     │
│                 ├── tooling/                                      │
│                 └── i18n/                                         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

### `.ahrena/`

Canonical entry point for the framework. Every project that adopts Ahrena **MUST** have this directory at the repository root. Contains the global directives that govern the behavior of all agents.

```
.ahrena/
├── .directives          # Canonical settings (language, naming, paths)
```

### `framework/`

Templates and artifacts in pure `.md`, platform agnostic. **Language is the first navigation level** — each language folder contains the complete tree of Clades, Subclades, and Pilares:

```
framework/
├── .directives.sample
│
├── templates/                          # Templates (base models for each Pilar)
│   ├── lex-sample.md
│   ├── codex-sample.md
│   ├── kata-sample.md
│   ├── warrior-sample.md
│   └── cry-sample.md
│
├── pt-BR/                              # Default language (source of truth)
│   │
│   │   # Artifacts by Clade → Subclade → Pilar
│   ├── _foundation/
│   │   ├── authoring/                 # Artifact creation guides
│   │   │   ├── codex/codex-*.md
│   │   │   ├── katas/kata-create-*.md
│   │   │   └── cries/cry-new-*.md
│   │   ├── contributing/              # Contribution flow
│   │   │   ├── codex/codex-contributing.md, codex-commit-standards.md, codex-semantic-version.md
│   │   │   ├── lexis/lex-conventional-commits.md, lex-semantic-version.md, ...
│   │   │   ├── katas/kata-commit.md, kata-contribute.md, kata-tag.md
│   │   │   └── cries/cry-commit.md, cry-contribute.md, cry-tag.md
│   │   ├── process/lexis/lex-*.md
│   │   ├── quality/lexis/lex-*.md
│   │   ├── tooling/cries/cry-make.md
│   │   └── i18n/
│   │       ├── lexis/lex-framework-language.md
│   │       └── codex/codex-framework-language.md
│   │
│   ├── engineering/platform/           # Guardia platform specifications
│   │   ├── lexis/lex-*.md               # RESTful, CloudEvents, entities, auth, errors
│   │   ├── codex/codex-*.md             # RESTful, CloudEvents manuals, etc.
│   │   ├── katas/kata-api-design-oas.md, kata-api-design-doc.md, kata-events-doc.md
│   │   ├── warriors/warrior-daedalus.md, warrior-kronos.md
│   │   └── cries/cry-api-design.md, cry-event-storm.md, cry-full-design.md
│   │
│   └── documentation/i18n/             # Translation system
│       ├── README.md                   # Complete documentation
│       ├── lexis/
│       │   ├── lex-language.md         # Cross-cutting rules
│       │   ├── lex-language-ptbr.md    # pt-BR rules
│       │   ├── lex-language-en.md      # en rules
│       │   └── lex-language-es.md      # es rules
│       ├── codex/
│       │   ├── codex-language.md       # Cross-cutting guide
│       │   ├── codex-language-ptbr.md
│       │   ├── codex-language-en.md
│       │   └── codex-language-es.md
│       ├── katas/kata-translate.md     # Procedure (6 steps)
│       ├── warriors/warrior-translator.md  # Hermes
│       └── cries/cry-translate.md      # Quick command
│
├── es/                                 # Spanish (same structure)
│   └── ...
└── en/                                 # English (same structure)
    └── ...
```

To create a new artifact: copy the corresponding template from `framework/templates/` (e.g., `lex-sample.md`), place it in the appropriate Clade/Subclade, and fill in the `[]` fields. The artifact **MUST** exist in all languages from `language.i18n` — use `/cry-translate` to generate the translations.

### Mapping: `framework/` → `.cursor/`

When implementing in Cursor, each Pilar maps to the corresponding native resource. Each Cursor resource has its own format:

| Pilar | Cursor Resource | Format | Destination |
|-------|-----------------|--------|-------------|
| **Lexis** | Rules | `.mdc` | `.cursor/rules/<clade>/<subclade>/lex-*.mdc` |
| **Codex** | Rules | `.mdc` | `.cursor/rules/<clade>/<subclade>/codex-*.mdc` |
| **Katas** | Skills | `SKILL.md` | `.cursor/skills/kata-*/SKILL.md` |
| **Warriors** | Skills + Agents | `SKILL.md` + `.md` | `.cursor/skills/warrior-*/SKILL.md` + `.cursor/agents/warrior-*.md` |
| **Cries** | Commands | `.md` | `.cursor/commands/<clade>/<subclade>/cry-*.md` |

**Cursor Native Formats:**

| Resource | Extension | Frontmatter | Description |
|----------|-----------|-------------|-------------|
| Rules | `.mdc` | `description` + `alwaysApply` | Context injected into the main agent |
| Skills | `SKILL.md` | `name` + `description` | Capabilities the agent adopts on demand |
| Commands | `.md` | `description` | Slash commands invocable via `/name` |
| Agents | `.md` | `name` + `description` | Isolated subagents with their own system prompt |

> Warriors generate **two artifacts**: a Skill (the main agent adopts the persona) and an Agent (isolated subagent delegated via Task). This enables both inline usage and delegation.

```
.cursor/
├── rules/                              # .mdc — Lexis + Codex
│   ├── samples/
│   │   ├── lex-sample.mdc
│   │   └── codex-sample.mdc
│   ├── _foundation/
│   │   ├── authoring/codex-*.mdc
│   │   ├── contributing/
│   │   │   ├── codex-contributing.mdc
│   │   │   ├── codex-commit-standards.mdc
│   │   │   ├── codex-semantic-version.mdc
│   │   │   └── lex-*.mdc
│   │   ├── process/lex-*.mdc
│   │   ├── quality/lex-*.mdc
│   │   └── i18n/
│   │       ├── lex-framework-language.mdc
│   │       └── codex-framework-language.mdc
│   └── documentation/i18n/
│       ├── lex-language.mdc, lex-language-{ptbr,en,es}.mdc
│       └── codex-language.mdc, codex-language-{ptbr,en,es}.mdc
│   └── engineering/platform/
│       ├── lex-*.mdc, codex-*.mdc
│       └── (API, events, entities, auth rules)
│
├── skills/                             # SKILL.md — Katas + Warriors
│   ├── kata-sample/SKILL.md
│   ├── warrior-sample/SKILL.md
│   ├── kata-commit/SKILL.md
│   ├── kata-contribute/SKILL.md
│   ├── kata-tag/SKILL.md
│   ├── kata-create-*/SKILL.md
│   ├── kata-translate/SKILL.md
│   ├── warrior-translator/SKILL.md
│   ├── kata-api-design-oas/SKILL.md, kata-api-design-doc/SKILL.md, kata-events-doc/SKILL.md
│   └── warrior-daedalus/SKILL.md, warrior-kronos/SKILL.md
│
├── commands/                           # .md — Cries
│   ├── samples/cry-sample.md
│   ├── _foundation/
│   │   ├── authoring/cry-new-*.md
│   │   ├── contributing/cry-commit.md, cry-contribute.md, cry-tag.md
│   │   └── tooling/cry-make.md
│   ├── documentation/i18n/cry-translate.md
│   └── engineering/platform/
│       └── cry-api-design.md, cry-event-storm.md, cry-full-design.md
│
└── agents/                             # .md — Warriors (subagents)
    ├── warrior-translator.md
    ├── warrior-daedalus.md
    └── warrior-kronos.md
```
