rebase then push. Shortcut to resolve conflicts and update the branch via rebase

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

## What the Command Does

1. Invokes **kata-rebase**, which encapsulates the rebase and conflict-resolution procedure.
2. The detailed procedure (check state, run rebase, resolve conflicts, final check) is in the Kata; the Cry does not define steps with external commands — it only invokes the Kata.
3. While `kata-rebase` is pending creation, the agent may guide the user based on `codex-contributing`; once created, the Cry will invoke it exclusively.

## Usage Examples

```
# Rebase current branch onto origin/main
/cry-rebase

# Rebase onto upstream/develop
/cry-rebase upstream/develop

# After sync conflict: rebase then push
/cry-rebase origin/main
```

## Associated Kata

`kata-rebase` — Full rebase procedure with conflict resolution. **Pending creation.**
