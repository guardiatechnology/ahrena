# Cry: New User Story (Frontend)

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to open a frontend user story issue in the repository

## Invocation

```
/cry-new-user-story-frontend [title or context]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| title or context | No | Summary or context to fill the template. If omitted, the agent collects from the user. |

## Behavior

1. Invokes **kata-contributing-issue** with type `user-story-for-frontend` (implicit from this cry's name).
2. The kata uses the template `.ahrena/contributing_templates/user-story-for-frontend.md`, fills it with the user, and creates the issue via GitHub MCP (or `gh`).

## Associated Kata

`kata-contributing-issue` — Procedure for opening an issue using one of the 4 templates (in this case, user-story-for-frontend).

## References

- `codex-contributing` — Guardia contribution flow (Cry context)
- `kata-contributing-issue` — Procedure executed by this Cry (see Kata documentation)
- `.ahrena/contributing_templates/user-story-for-frontend.md` — Issue template
