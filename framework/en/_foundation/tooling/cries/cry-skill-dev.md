# Cry: Local skill dev server

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to bring up widgets HMR + script runner + tool stub on localhost for a skill project

## Description

Shortcut that invokes `kata-skill-dev-server` to bring up the local development environment of a skill at `{paths.skills_root}/{slug}/`. Brings up only the subservers applicable to the project (widgets/scripts/tools) according to the presence of each subdirectory. Default ports are `5173` (widgets), `5174` (scripts), `5175` (tool stub), with override via parameters.

## Usage

```
/cry-skill-dev <slug> [options]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `slug` | Yes | Project at `{paths.skills_root}/{slug}/` | `hello-skill` |
| `widgets_port=` | No | Override (default `5173` or `dev_server.widgets_port`) | `widgets_port=5180` |
| `scripts_port=` | No | Override (default `5174`) | `scripts_port=5181` |
| `tools_stub_port=` | No | Override (default `5175`) | `tools_stub_port=5182` |
| `only=` | No | Subset (`widgets`, `scripts`, `tools`); default all | `only=widgets` |

## What the Command Does

1. Resolves `paths.skills_root` in `.ahrena/.directives`
2. Confirms the project exists and reads `skill.config.json`
3. Invokes `kata-skill-dev-server` with the received parameters
4. Keeps the foreground with prefixed logs (`[widgets]`, `[scripts]`, `[tools]`) until Ctrl-C

## Prompt Template

```
Context:
- slug: {{slug}}
- widgets_port: {{widgets_port}} (optional)
- scripts_port: {{scripts_port}} (optional)
- tools_stub_port: {{tools_stub_port}} (optional)
- only: {{only}} (optional)

Task:
Invoke kata-skill-dev-server with the parameters above. The kata:
1. Resolves paths and config
2. Verifies preconditions (manifests, deps, ports)
3. Brings up widgets (Vite HMR), script runner, and tool stub when applicable
4. Reports URLs and instructions
5. Keeps the foreground until the user interrupts

Abort if: project does not exist, invalid manifest, port occupied without override.

Output format:
Active URLs + foreground with logs until Ctrl-C. On error, a specific
message and a suggested correction.
```

## Invocation Example

```
/cry-skill-dev hello-skill
```

**Expected output:**

```
✅ Dev server active for hello-skill:
   Widgets:      http://localhost:5173/        (Vite HMR)
   (no scripts/ — skipped)
   (no tools/ — skipped)

Press Ctrl-C to terminate.
```

## Restrictions

- The Cry **does not modify** `skills/{slug}/` (read only)
- The Cry **does not write** to `.build/` or `.dist/`
- Messages to the user in `language.default`; technical identifiers preserved
- `lex-terminal-type`: respects the terminal defined in `.directives`

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | 1:1 shortcut | Operational procedure (7 steps) |
| **Validation** | Parameter form | Preconditions, manifests, ports |
| **Effect** | Invokes the kata | Brings up processes, keeps foreground |

## References

- `kata-skill-dev-server` — invoked procedure
- `codex-skill-build-pipeline` — tooling defaults and ports
- `codex-skill-tools-and-widgets` — schemas validated before bring-up
- `cry-skill-build` — next step to generate `.build/`
