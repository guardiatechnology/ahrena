Sync with upstream remote. Shortcut to sync the local repository with the remote (fetch, pull, push)

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

## What the Command Does

1. Invokes **kata-sync**, which encapsulates the repository sync procedure (fetch, pull, push, and conflict handling).
2. The detailed procedure is in the Kata; the Cry does not define steps with external commands — it only invokes the Kata.
3. While `kata-sync` is pending creation, the agent may guide the user based on `codex-contributing`; once created, the Cry will invoke it exclusively.

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
