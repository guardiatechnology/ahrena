---
name: __SLUG__
description: __ONE_SENTENCE_DESCRIPTION_INCLUDING_WHEN_TO_USE__
license: __LICENSE_OR_REFERENCE__
metadata:
  version: "0.1.0"
  language: __BCP47__
  spec_version: agentskills.io/specification@2026-04
---

# __HUMAN_TITLE__

> Replace placeholders enclosed by `__...__` before publishing. See
> `codex-skill-anthropic-agent-skills` for field semantics and limits.

## When to use

Describe in one short paragraph the situations in which an agent should
activate this skill. Be concrete — name the user intents and keywords
that signal a fit. Generic descriptions reduce activation accuracy.

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `__input_1__` | Yes | __what it is and where it comes from__ |

## Workflow

1. __Step 1 — concrete action the agent performs__
2. __Step 2 — typically a tool/script call or widget render__
3. __Step 3 — confirmation or hand-off__

## Tools, scripts, and widgets

This skill bundles (Ahrena convention — see
`codex-skill-tools-and-widgets` once PR 2 lands):

- `tools/` — MCP tools the agent invokes for domain logic
- `scripts/` — utility code (Python or JS) callable from tools or widgets
- `widgets/` — React components rendered in the chat surface

Reference each by relative path:

```
Run validation: scripts/src/validate.py
Render confirmation: widgets/src/confirm/index.tsx
```

## References

- [Detailed reference](references/REFERENCE.md)
- __link to project-specific docs if any__

## Edge cases

- __What happens when input is missing or invalid__
- __What happens when an external dependency is unavailable__
- __What the skill explicitly does NOT handle__
