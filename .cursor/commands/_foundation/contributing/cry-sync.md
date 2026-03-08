---
description: "Sync with upstream remote. Shortcut to sync the local repository with the remote (fetch, pull, push)"
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

The command runs, **in this order**:

1. **Fetch:** `git fetch <remote>` — updates remote references and objects without changing the working tree.
2. **Pull:** `git pull <remote> <branch>` — fetches and merges (or rebases, per config) remote commits into the current branch.
3. **Push:** `git push <remote> <branch>` — pushes local commits to the remote.

If the pull has conflicts, the agent reports them and guides the user to use `/cry-rebase` to resolve before attempting push.

## Usage Examples

```
# Sync current branch with origin
/cry-sync

# Sync main with origin
/cry-sync origin main

# Sync with upstream remote
/cry-sync upstream main
```

## Associated Kata

`kata-sync` — Full sync procedure (fetch, pull, push, and conflict handling). **Pending creation.**
