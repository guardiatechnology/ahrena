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
2. The kata runs **Phase 0 — Decision Checklist** even on explicit user invocation, applying the canonical checklist defined in `codex-stacked-prs`.
3. **If the checklist fails**, the kata warns the user with the actual signals counted, proposes proceeding with a single PR via `kata-contributing-pr`, and only continues with the stack on explicit user override (recording the decision).
4. **If the checklist passes**, the kata proposes a concrete layer decomposition (see kata for details), confirms with the user, and creates the chain: shared worktree, N branches, N stacked PRs, label mirroring.
5. The kata selects the operational tool by consulting the `stacked_prs.tool` directive in `.ahrena/.directives`. Accepted values: `vanilla` (default — `git` + `gh`) and `gs` (git-spice — auto-restack documented in `codex-git-spice`). Each value activates the corresponding section of the Kata (main procedure vs. "Variant: git-spice" section); the Cry does not read the directive directly.

## Associated Kata

`kata-stacked-pr-create` — Procedure to decompose a feature into a stack and create the PR chain.

## Constraints

- **Never** proceed without explicit user confirmation on the layer decomposition
- **Never** ignore anti-signals without explicit user override
- If the umbrella issue does not satisfy `lex-issue-quality`, warn and stop — the issue must be fixed first
- If `stacked_prs.tool` is not declared in `.ahrena/.directives`, assume `vanilla`

## References

- `kata-stacked-pr-create` — Kata invoked by this Cry
- `codex-stacked-prs` — Canonical Decision Checklist and conceptual model
- `codex-git-spice` — Manual for the `gs` variant when the project declares `stacked_prs.tool: gs`
- `kata-contributing-pr` — Fallback to a single PR
- `cry-new-pr` — Equivalent shortcut for a single PR
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-pr-quality` — Applicable Lexis
