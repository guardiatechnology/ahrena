---
paths:
  - '.github/CODEOWNERS'
  - '.gitignore'
  - '.github/workflows/**.yml'
---

# Lexis: Mandatory Use of Git Worktrees

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Every branch-based task executed by AI agents in the Ahrena context

## Law

> **Every agent that needs to create a branch to implement a task MUST do so inside a dedicated git worktree, created from the main repository. The worktree branch MUST follow `lex-git-branches` (`{type}/{issue-number}-{slug}`) and a GitHub Issue MUST exist before creation (per `lex-issue-first`). The worktree directory MUST use the branch slug as a human-readable name. Working directly on the main checkout with changes belonging to a task branch is FORBIDDEN. The worktree MUST be removed after the corresponding PR is merged.**

## Coverage

- **Applies to:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, any AI agent that creates branches to implement tasks
- **Bound agents:** all warriors and katas that produce code or artifacts on dedicated branches (`warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`)
- **Allowed exceptions:** direct commits to `main` for trivial typo or formatting fixes (per `lex-issue-first`); read-only operations that produce no branch

## Rules

### 1. Issue before worktree

Before creating the worktree, the agent MUST:

1. Verify that a GitHub Issue exists for the task (per `lex-issue-first`)
2. Note the issue number — it is a mandatory part of the branch name and worktree directory

### 2. Branch and directory naming

The branch MUST follow the `lex-git-branches` format:

```
{type}/{issue-number}-{slug}
```

The worktree directory MUST follow the path defined in `paths.worktrees` in `.ahrena/.directives` (default: `.worktrees/`) and use `{issue-number}-{slug}` as its name:

```
.worktrees/{issue-number}-{slug}/
```

Example: branch `feat/42-scheduled-payments-api` → directory `.worktrees/42-scheduled-payments-api/`

The `.worktrees/` path is inside the repository and ignored by git via `.gitignore`.

### 3. Worktree as isolated environment

The agent MUST use the worktree as the exclusive environment for the task:

- All file edits occur **inside** the worktree
- Commits are made in the worktree context
- The main checkout remains clean — no unrelated changes

### 4. Mandatory cleanup after merge

After the corresponding PR is merged:

1. Exit the worktree directory (if currently inside)
2. Remove the worktree: `git worktree remove .worktrees/{issue-number}-{slug} --force`
3. Delete the local branch: `git branch -d {branch}`
4. Confirm: `git worktree list` must no longer show the removed worktree

## Examples

### Correct

```
Issue #42 exists: "Add scheduled payments API"
Branch: feat/42-scheduled-payments-api
Worktree: .worktrees/42-scheduled-payments-api/

→ Agent enters worktree via EnterWorktree or git worktree add
→ All edits made inside the worktree
→ Main checkout stays on main, clean
→ After PR merge: worktree removed, branch deleted
```

### Incorrect

```
# Agent edits files on main checkout to implement a feature branch task
# ❌ Main checkout accumulates mixed changes

# Branch created without an associated issue
# ❌ Violates lex-issue-first and lex-git-branches

# Worktree not removed after merge — stale directories accumulate
# ❌ git worktree list shows dead worktrees
```

## Automated Validation

- **Tool:** `git worktree list` to verify active worktrees; Claude Code `EnterWorktree` for creation and navigation; `kata-git-worktree` as canonical entry point
- **Timing:** before starting any task that produces a branch; after PR merge (cleanup)
- **Metric:** 0 feature tasks executed outside a dedicated worktree; 0 worktrees created without a corresponding GitHub Issue; main checkout always clean during feature executions
