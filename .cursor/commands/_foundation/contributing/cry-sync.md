---
description: "Sync repository with remote: fetch, then pull, then push. Use cry-rebase if there are conflicts."
---

# Cry: Sync Repository

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to sync the local repository with the remote (fetch, pull, push)

## Invocation

```
/cry-sync [remote] [branch]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `remote` | No | Remote name (default: `origin`) | `origin`, `upstream` |
| `branch` | No | Branch to sync (default: current branch) | `main`, `develop` |

## Behavior

Run, **in this order**: (1) `git fetch <remote>`, (2) `git pull <remote> <branch>`, (3) `git push <remote> <branch>`. If the pull has conflicts, guide the user to `/cry-rebase` before pushing.

## Associated Kata

`kata-sync` — Pending creation.
