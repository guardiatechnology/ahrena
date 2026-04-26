New Pull Request. Shortcut to open a Pull Request in the origin repository

# Cry: New Pull Request

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to open a Pull Request in the origin repository

## Invocation

```
/cry-new-pr [--draft] [--title "..."]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--draft` | No | Create the PR as a draft |
| `--title` | No | PR title in Conventional Commits format. If omitted, the agent infers from commits. |

## Behavior

1. Invokes **kata-contributing-pr** (which aligns with kata-contribute).
2. The kata uses the template `.ahrena/contributing_templates/pull_request_template.md` (or `.github/pull_request_template.md`), validates commits against the Lexis, and creates the PR via GitKraken MCP (`pull_request_create`).

## Associated Kata

`kata-contributing-pr` — Procedure for contributing via Pull Request.
