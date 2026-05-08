# Codex: Ahrena Convention — `tools/` (MCP) and `widgets/` (React)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Ahrena extension to the Anthropic Agent Skills format — convention for packaging MCP tools (logic) and React widgets (UI) inside a skill project, and how widgets bind to scripts and tools

## Overview

The Anthropic Agent Skills spec (per `codex-skill-anthropic-agent-skills`) **does not define** a layout for MCP tools or for UI widgets. This Codex establishes the **Ahrena convention** that fills that gap: how to organize `tools/` and `widgets/` inside `skills/{slug}/`, the schema of each manifest, and how widgets declare bindings to scripts and tools.

External agents that only know the spec **ignore** these directories — they continue consuming `SKILL.md`, `references/`, `scripts/`, `assets/` normally. The convention is additive: skills without `tools/`/`widgets/` remain 100% spec-compliant. Skills with these directories deliver additional capabilities to hosts that recognize the convention (Claude Code with Ahrena integration, Guardia agentic surface).

## Context

- **Domain:** internal structure of `tools/` and `widgets/` inside skill projects, and the binding contract between them
- **Audience:** skill authors who need their own UI or MCP logic
- **Update:** when manifest schemas evolve; when the Anthropic spec absorbs equivalent primitives (if it occurs, this codex documents the transition)

## Status — Convention, not Spec

> **Attention:** `tools/` and `widgets/` are **not** part of the Anthropic Agent Skills spec. This is an Ahrena framework convention. The `SKILL.md` generated in projects with these directories **MUST** include an explicit warning header so external consumers know what to expect.

## Content

### `tools/` — MCP tools owned by the skill

MCP tools bundled with the skill expose domain capabilities that the external agent invokes during execution. They do not replace global MCP servers (GitHub, Notion, Figma) — they address skill-specific needs.

#### Layout

```
tools/
├── mcp.config.json     # tool registry
└── handlers/           # implementations
    ├── validate_amount.py
    └── ...
```

Handler languages: Python (default — aligned with `codex-python-architecture`) or JavaScript/TypeScript (Node). Mixing is permitted.

#### `mcp.config.json` — schema

```json
{
  "schema_version": 1,
  "mcp": {
    "name": "{slug}-tools",
    "description": "MCP tools bundled with this skill (Ahrena convention).",
    "tools": [
      {
        "name": "validate_amount",
        "description": "Validate that a transfer amount is within the allowed range and currency.",
        "input_schema": {
          "type": "object",
          "properties": {
            "amount": { "type": "integer", "minimum": 1 },
            "currency": { "type": "string", "pattern": "^[A-Z]{3}$" }
          },
          "required": ["amount", "currency"]
        },
        "handler": "handlers/validate_amount.py:run"
      }
    ]
  }
}
```

| Field | Description |
|-------|-------------|
| `schema_version` | Integer; reserved for schema evolution (current: `1`) |
| `mcp.name` | `{slug}-tools` by convention; local identifier of the server |
| `mcp.description` | Single sentence describing the purpose of the bundle |
| `mcp.tools[].name` | snake_case; tool identifier inside the server |
| `mcp.tools[].description` | Text the agent reads to decide when to invoke |
| `mcp.tools[].input_schema` | JSON Schema Draft 7+ |
| `mcp.tools[].handler` | `<relative-path>:<function>` — the build resolves to a runnable |

#### Conventions for handlers

- Python: handler is `def run(input: dict) -> dict | Result[T, E]`. Apply `lex-python-typing`, `lex-python-error-handling`, `lex-python-result-type` (when use of Result is natural), `lex-python-security`, `lex-mcp`.
- JS/TS: handler is `export async function run(input): Promise<unknown>`. Apply `lex-frontend-typing` (when TS), idiomatic error handling.
- Logging in any language follows `lex-logging-decorator`.

### `widgets/` — React Components

Widgets are React (TypeScript) components rendered by the host agent on the chat surface. The architecture inherits **entirely** from `codex-frontend-architecture`: layers (Pages → Features → Components → Hooks → Services → State), state management appropriate for scope, typed props, server state via TanStack Query / SWR when there is real fetching.

#### Layout

```
widgets/
├── package.json        # React 18 + TS strict + Vite
├── tsconfig.json       # strict: true, noUncheckedIndexedAccess: true
├── manifest.json       # registry of exposed components
└── src/
    ├── components/     # reusable primitives
    ├── features/       # blocks per feature
    └── transfer-form/  # example feature component
        └── index.tsx
```

#### `manifest.json` — schema

```json
{
  "schema_version": 1,
  "components": [
    {
      "name": "TransferForm",
      "entry": "src/transfer-form/index.tsx",
      "props_schema": {
        "type": "object",
        "properties": {
          "default_amount": { "type": "integer" },
          "currency": { "type": "string" }
        }
      },
      "events": [
        {
          "name": "submit",
          "payload_schema": {
            "type": "object",
            "properties": {
              "amount": { "type": "integer" },
              "currency": { "type": "string" }
            },
            "required": ["amount", "currency"]
          }
        }
      ],
      "bindings": [
        {
          "kind": "tool",
          "ref": "validate_amount"
        },
        {
          "kind": "script",
          "ref": "scripts/src/format_currency.py",
          "called_via": "http://localhost:5174/format-currency"
        }
      ]
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `schema_version` | Integer; reserved (current: `1`) |
| `components[].name` | PascalCase; identifier exposed to the host |
| `components[].entry` | Relative path of the component the build packages |
| `components[].props_schema` | JSON Schema of the accepted props |
| `components[].events[]` | Events the component emits, with typed payload |
| `components[].bindings[]` | External dependencies (MCP tools or scripts) — see below |

### Binding widget ↔ script ↔ tool

Widgets explicitly declare their external dependencies in `bindings[]`. The host resolves at runtime according to the environment:

| `kind` | When to use | Resolution in dev (localhost) | Resolution in prod (host agent) |
|--------|-------------|-------------------------------|---------------------------------|
| `tool` | Skill MCP logic (`tools/`) or from another active MCP server | Local tool stub at `localhost:5175` | Host invokes the MCP tool directly |
| `script` | Utility in `scripts/` called via HTTP/JSON | `fetch(called_via)` to the script runner at `localhost:5174` | Host runs the bundled script and exposes an ephemeral endpoint, or routes via an equivalent MCP tool |

**Principle:** the widget **does not import** scripts directly. Every dependency crosses a typed boundary (HTTP/JSON or MCP) — this keeps the widget renderable in isolation (Storybook preview, Playwright smoke) without needing the entire skill runtime.

`called_via` in `kind: script` bindings:

- In **dev**, points to the local script runner (`http://localhost:{scripts_port}/...`)
- In **prod**, it is rewritten by the consuming project's build stack: it becomes a relative path the host resolves via the equivalent MCP tool, or an ephemeral endpoint. The rewrite is part of the build, not of the spec.

### Reuse of codex and Lexis

| Content | Architecture Codex | Applicable Lexis |
|---------|--------------------|------------------|
| `widgets/` React+TS | `codex-frontend-architecture` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` (on the Guardia surface), `lex-tone` (microcopy) |
| `tools/handlers/` Python | `codex-mcp-common`, `codex-python-architecture`, `codex-python-tooling` | `lex-mcp`, `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-logging-decorator` |
| `tools/handlers/` JS/TS | `codex-mcp-common` | `lex-mcp`, `lex-frontend-typing` (when TS), `lex-logging-decorator` |
| Manifest and schemas | (this codex) | `lex-skill-project-structure` |

### Compatibility with the spec

| Aspect | Anthropic Spec | Ahrena Convention |
|--------|----------------|-------------------|
| `SKILL.md`, frontmatter, body | Defined | Unchanged |
| `references/`, `scripts/`, `assets/` | Defined | Unchanged — Ahrena does not modify these directories |
| `tools/`, `widgets/` | **Not covered** | Added — spec-only agents ignore |
| `.skill-manifest.json` | Not covered | Ahrena root manifest (audit, hashes — see `lex-skill-project-structure` and `lex-skill-package-structure`) |

When the spec evolves and covers tools/widgets, this codex documents the transition (mapping, deprecations). Skills that adopted the convention continue working as long as Ahrena agents recognize the layout — migration to the canonical form of the spec will be incremental.

## Restrictions

- The author **does not infer** bindings — every external dependency is declared in `manifest.json` (widgets) or `mcp.config.json` (tools)
- Widget **does not import** a script directly; always crosses an HTTP/MCP boundary
- `bindings[].kind: script` is resolved with `called_via` in dev and rewritten by the build for prod — do not use a hardcoded production URL
- Manifests are validated before build by the consuming project's build stack; a schema failure aborts with a specific error

## Glossary

| Term | Definition |
|------|------------|
| Binding | Explicit declaration, in the widget's `manifest.json`, of a dependency on an MCP tool or a script |
| Root manifest | `.skill-manifest.json` at the project root — distinct from the manifests of `tools/` and `widgets/` |

## References

- `codex-skill-anthropic-agent-skills` — external spec
- `codex-skill-project-architecture` — project layout and role of the directories
- `codex-frontend-architecture` — architecture applied to widgets
- `codex-python-architecture`, `codex-python-tooling` — architecture applied to Python handlers
- `codex-mcp-common` — shared MCP server patterns
- `lex-skill-project-structure` — layout law
- `lex-frontend-*`, `lex-python-*`, `lex-mcp`, `lex-logging-decorator` — applicable quality
