New User Story (API). Shortcut to open an API user story issue in the repository

# Cry: New User Story (API)

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to open an API user story issue in the repository

## Invocation

```
/cry-new-user-story-api [title or context]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| title or context | No | Summary or context to fill the template. If omitted, the agent collects from the user. |

## Behavior

1. Invokes **kata-contributing-issue** with type `user-story-for-api` (implicit from this cry's name).
2. The kata uses the template `.ahrena/contributing_templates/user-story-for-api.md`, fills it with the user, and creates the issue via GitHub MCP (or `gh`).

## Associated Kata

`kata-contributing-issue` — Procedure for opening an issue using one of the 4 templates (in this case, user-story-for-api).
