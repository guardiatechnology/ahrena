---
description: "Resolve conflicts via rebase. Use after cry-sync when pull has conflicts."
---

# Cry: Run Rebase

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to resolve conflicts and update the branch via rebase

## Invocation

```
/cry-rebase [base]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `base` | No | Reference to rebase onto (default: tracking branch or `origin/main`) | `origin/main`, `upstream/develop` |

## Behavior

Guide the user through `git rebase <base>`, resolving conflicts (edit, `git add`, `git rebase --continue`) or `git rebase --abort`. After completion, suggest `git push` or `git push --force-with-lease` if the branch was already pushed.

## Associated Kata

`kata-rebase` — Pending creation.
