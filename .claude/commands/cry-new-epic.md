New Epic. Shortcut to open an epic issue in the repository

# Cry: New Epic

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to open an epic issue in the repository

## Invocation

```
/cry-new-epic [title or context]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| title or context | No | Summary or context to fill the template. If omitted, the agent collects from the user. |

## Behavior

1. Invokes **kata-contributing-issue** with type `epic` (implicit from this cry's name).
2. The kata uses the template `.ahrena/contributing_templates/epic.md`, fills it with the user, and creates the issue via GitHub MCP (or `gh`).

## Associated Kata

`kata-contributing-issue` — Procedure for opening an issue using one of the 4 templates (in this case, epic).
