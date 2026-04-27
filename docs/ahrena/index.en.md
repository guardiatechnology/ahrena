# Ahrena — AI-First Capability Framework

> **Product:** Ahrena · **Owner:** Guardia · **Status:** Active · **Type:** Internal Platform

## What is Ahrena?

**Ahrena** is Guardia's AI-First Capability Framework. It structures knowledge, processes, and AI agent behavior through a unified taxonomy, enabling consistent, auditable, and repeatable collaboration between humans and AI across any engineering discipline.

Ahrena defines *how* Guardia's teams and AI agents think, decide, and execute — from a commit message to a full product feature design.

## Why We Built It

As Guardia adopted AI agents as first-class participants in engineering workflows, the need for a structured, versioned, and platform-agnostic operating model became critical. Without it:

- Agents made inconsistent decisions across sessions
- Knowledge lived in chat history, not in versioned artifacts
- Onboarding new engineers or agents required tribal knowledge transfer
- There was no single source of truth for process, conventions, and standards

Ahrena solves this by treating agent behavior rules, reference knowledge, executable skills, and commands as **code** — versioned, reviewable, and deployable.

## Core Principles

| Principle | What it means |
|---|---|
| **AI as copilot, not pilot** | Humans set direction; agents execute and propose, never decide alone |
| **Process over tool** | Rules and procedures are platform-agnostic; tools come and go |
| **Artifacts as code** | Every convention, law, and skill is a versioned file in `framework/` |
| **`framework/` as source of truth** | One canonical source; all platform configs (Cursor, Claude Code) are generated from it |

## Architecture at a Glance

```
framework/
├── en/                  ← English artifacts (source of truth)
├── pt-BR/               ← Brazilian Portuguese artifacts
├── es/                  ← Spanish artifacts
└── templates/           ← Official templates per Pilar
```

The framework is organized by **Clade → Subclade → Pilar**. Within each Pilar, artifacts are named by type prefix:

| Pilar | Prefix | Role |
|---|---|---|
| **Lexis** | `lex-` | Unbreakable laws — no exception |
| **Codex** | `codex-` | Reference manuals — knowledge and guidance |
| **Katas** | `kata-` | Executable skills — repeatable procedures |
| **Warriors** | `warrior-` | Specialized agents — orchestrate Katas |
| **Cries** | `cry-` | High-level commands — activate Warriors or Katas |

## Scale

| Dimension | Count |
|---|---|
| Total artifacts in framework | ~649 |
| Languages | 3 (en, pt-BR, es) |
| Lexis (unbreakable laws) | 39 |
| Codex (reference manuals) | 55 |
| Katas (executable skills) | 53 |
| Warriors (specialized agents) | 14 |
| Cries (commands) | 31 |
| Clades | 4 |
| Subclades | 16 |

## Platform Support

Ahrena is platform-agnostic. The installer (`scripts/install.py`) generates IDE-specific configurations from `framework/`:

| Platform | Generated Config | Notes |
|---|---|---|
| **Claude Code** | `.claude/` (skills, commands, agents, docs) + `CLAUDE.md` | Primary platform at Guardia |
| **Cursor** | `.cursor/` (rules, skills, commands, agents) | Full IDE integration |

## Key Capabilities

### Issue-Driven Development

Warrior `warrior-athena` orchestrates a complete 7-phase development flow — from reading a GitHub issue to opening a reviewed PR — with 2 mandatory gates (Scope and Quality), full AC↔test traceability, and ADR creation for architectural decisions.

[→ lex-issue-driven](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/workflow/lexis/lex-issue-driven.md)

### Platform Design Cycle

Warriors `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, and `warrior-kronos` cover the full feature design cycle: domain modeling (DDD), API design (OAS), and event documentation (CloudEvents).

### AI-First Product Experience

Lexis `lex-ai-first-experience` mandates that every human-facing interface at Guardia uses Isac (the AI agent) as the primary interaction surface — not a feature sidebar.

[→ lex-ai-first-experience](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/design/system/lexis/lex-ai-first-experience.md)

### Multilingual by Default

Every framework artifact exists in English, Brazilian Portuguese, and Spanish. The `warrior-translator` and `kata-translate` automate translation with language-specific rules enforced by `lex-language-*` laws.

## Documentation Index

| Document | Description |
|---|---|
| [Concepts](concepts.md) | Pilars, Clades, Subclades, addressing taxonomy |
| [Clades & Subclades](clades.md) | Full catalog with pilar coverage per subclade |
| [Lexis Catalog](lexis.md) | All 39 unbreakable laws |
| [Codex Catalog](codex.md) | All 55 reference manuals |
| [Katas Catalog](katas.md) | All 53 executable skills |
| [Warriors Catalog](warriors.md) | All 14 specialized agents |
| [Cries Catalog](cries.md) | All 31 high-level commands |
