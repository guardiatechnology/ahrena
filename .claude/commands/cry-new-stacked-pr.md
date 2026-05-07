New Stacked Pull Request. Shortcut to start a chain of stacked Pull Requests in the origin repository

# Cry: New Stacked Pull Request

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to start a chain of stacked Pull Requests in the origin repository

## Invocation

```
/cry-new-stacked-pr [<issue-number>] [--draft]
```

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `<issue-number>` | No | Umbrella issue number. If omitted, the agent asks. |
| `--draft` | No | Create all stack PRs as drafts. |

## Behavior

1. Invokes **kata-stacked-pr-create**.
2. The kata runs **Phase 0 — Decision Checklist** even on explicit user invocation, using the canonical criteria from `codex-stacked-prs` (≥ 3 high signals AND 0 anti-signals).
3. **If the checklist fails** (anti-signal present or high signals < 3), the agent warns:
   ```
   This issue does not meet the canonical checklist for a stacked PR:
     High signals: X (minimum 3)
     Anti-signals detected: [list]

   Proposal: proceed with a single PR via kata-contributing-pr.

   Force the stack anyway? (y/n)
   ```
   - If `n` (default), redirect to `kata-contributing-pr` (single PR)
   - If `y` (explicit user override), proceed with the stack and record the override decision
4. **If the checklist passes**, the kata proposes a concrete layer decomposition (see kata for details), confirms with the user, and creates the chain: shared worktree, N branches, N stacked PRs, label mirroring.
5. Reads `.ahrena/.directives` for `stacked_prs.tool`:
   - `vanilla` (default) → follow this Kata's flow
   - `gs` → follow the kata's "Variant: git-spice" section (available after plan-005)

## Associated Kata

`kata-stacked-pr-create` — Procedure to decompose a feature into a stack and create the PR chain.

## Constraints

- **Never** proceed without explicit user confirmation on the layer decomposition
- **Never** ignore anti-signals without explicit user override
- If the umbrella issue does not satisfy `lex-issue-quality`, warn and stop — the issue must be fixed first
- If `stacked_prs.tool` is not declared in `.ahrena/.directives`, assume `vanilla`
