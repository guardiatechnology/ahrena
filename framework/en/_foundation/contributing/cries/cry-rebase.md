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

The command guides conflict resolution using rebase:

1. **Check state:** confirm there are conflicts or the branch is behind the remote (e.g. after a pull with divergence).
2. **Run rebase:** `git rebase <base>` — reapplies local commits on top of `<base>`.
3. **Resolve conflicts (if any):** for each conflict, the agent helps edit files, `git add`, and `git rebase --continue`; or `git rebase --abort` to cancel.
4. **Final check:** after rebase completes, inform the user they can run `git push` (possibly `--force-with-lease` if the branch had already been pushed).

If the user ran `/cry-sync` and the pull had conflicts, use this Cry to rebase onto the remote and then complete the push.

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

## References

- `cry-sync` — Repository sync (fetch, pull, push); use rebase when there are conflicts
- `codex-contributing` — Contribution flow
