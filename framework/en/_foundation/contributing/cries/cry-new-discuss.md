# Cry: New Discussion

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to open a discussion on GitHub Discussions (Golden Circle)

## Invocation

```
/cry-new-discuss [WHAT] [WHY] [HOW]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| WHAT / WHY / HOW | No | If provided, the agent uses them to structure the discussion. Otherwise, it collects from the user. |

## Behavior

1. Invokes **kata-contributing-discuss**.
2. The kata structures the proposal in the Golden Circle (WHAT, WHY, HOW) and creates the discussion on GitHub Discussions via GitHub MCP when available (or indicates manual opening).

## Associated Kata

`kata-contributing-discuss` — Procedure for opening a discussion on GitHub Discussions (Golden Circle).

## References

- `codex-contributing` — Guardia contribution flow (Cry context)
- `kata-contributing-discuss` — Procedure executed by this Cry (see Kata documentation)
- Golden Circle — WHAT, WHY, HOW
