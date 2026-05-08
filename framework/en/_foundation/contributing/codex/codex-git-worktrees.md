# Codex: Git Worktrees in the Ahrena Context

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Conventions, lifecycle, and commands for using git worktrees by AI agents in the Ahrena context

## Overview

This Codex is the canonical manual for using git worktrees. It complements `lex-git-worktrees` (the Law) with explanations, naming conventions, full lifecycle, commands, and integration with the Claude Code SDK. Every agent that creates or manages worktrees MUST consult this Codex.

## Context

- **Domain:** per-task development environment isolation
- **Audience:** all agents (Claude, Cursor, warriors, katas) and human reviewers
- **Update:** when commands or conventions change

---

## 1. What is a git worktree

A git worktree is an additional working directory linked to the same git repository. Each worktree has its own active branch, but shares the history, objects, and configuration of the root repository.

```
root repository (main)
├── .git/                         ← single shared git object
├── src/
└── framework/

worktree (feat/42-payments-api)   ← separate directory, own branch
├── .git                          ← pointer file, not a directory
├── src/
└── framework/
```

**Why use it:** each feature task runs in an isolated environment — no risk of mixing changes, no need for `stash`, no active branch conflict between parallel tasks.

---

## 2. Naming convention

### Branch

Follows `lex-git-branches` mandatorily:

```
{type}/{issue-number}-{slug}
```

| Field | Rule |
|---|---|
| `type` | One of: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `issue-number` | Integer number of the associated GitHub Issue |
| `slug` | kebab-case, maximum 50 characters |

Valid examples:
- `feat/42-scheduled-payments-api`
- `fix/87-null-pointer-transfer`
- `docs/101-update-contributing-guide`

### Worktree directory

```
.worktrees/{issue-number}-{slug}/
```

| Field | Rule |
|---|---|
| `issue-number` | Same issue number as the branch |
| `slug` | Same slug as the branch |

Examples:
- `.worktrees/42-scheduled-payments-api/`
- `.worktrees/87-null-pointer-transfer/`

The `.worktrees/` directory is inside the repository and ignored by git via `.gitignore`. The path is configurable via `paths.worktrees` in `.ahrena/.directives`.

---

## 3. Lifecycle

```
issue exists
    ↓
create worktree  →  work inside  →  commit + push  →  PR opened  →  PR merged
                                                                        ↓
                                                              remove worktree
                                                              delete local branch
```

### 3.1 Create the worktree

**Via Claude Code (recommended):**

Claude Code exposes the `EnterWorktree` tool that automatically creates and enters the worktree, with a branch following the Ahrena convention.

**Via CLI:**

```powershell
# PowerShell (terminal: powershell per .ahrena/.directives)
$repo    = "ahrena"
$issue   = 42
$type    = "feat"
$slug    = "scheduled-payments-api"
$branch  = "$type/$issue-$slug"
$wtDir   = ".worktrees/$issue-$slug"

git worktree add $wtDir -b $branch
```

### 3.2 Work in the worktree

```powershell
Set-Location $wtDir

# edit files, commit normally
git add .
git commit -m "feat(payments): add scheduled transfer entity"

# push the worktree branch
git push -u origin $branch
```

### 3.3 Open the PR

Open the PR referencing the issue per `lex-issue-first`:

```powershell
gh pr create --title "feat(payments): add scheduled payments API" `
             --body "Closes #$issue" `
             --base main `
             --head $branch
```

### 3.4 Cleanup after merge

```powershell
# Navigate to the repository root (if inside the worktree)
Set-Location ../..

# Remove the worktree
git worktree remove $wtDir --force

# Delete the local branch
git branch -d $branch

# Verify
git worktree list
```

---

## 4. Claude Code integration

The Claude Code SDK exposes the `EnterWorktree` tool to create and navigate worktrees in an automated way. The agent should prefer it over manual CLI.

Expected parameters for `EnterWorktree`:
- `branch`: branch name in `lex-git-branches` format
- Automatically creates the `.worktrees/{issue-number}-{slug}/` directory
- Returns the path of the created worktree

After the task is complete and the PR is merged, the agent uses `ExitWorktree` to exit and then runs the CLI cleanup.

---

## 5. Parallel worktrees

A repository supports multiple simultaneous worktrees — each task has its own:

```
git worktree list

/c/Workspace/guardia/public/ahrena                [main]
/c/Workspace/guardia/public/ahrena/.worktrees/42-payments    [feat/42-scheduled-payments-api]
/c/Workspace/guardia/public/ahrena/.worktrees/87-fix-null    [fix/87-null-pointer-transfer]
```

Git restrictions:
- The same branch **cannot** be active in two worktrees at the same time
- Operations like `git branch -d` fail if the branch is in use in an active worktree — remove the worktree first

---

## 6. Shared worktree for Stacked Pull Requests

When a feature is decomposed into N stacked layers (Stacked PRs), the "one worktree per branch" rule from sections 2-4 **does not apply**. The whole stack operates inside **a single** shared worktree.

| Aspect | Standard worktree (1-1) | Shared worktree (Stacked PRs) |
|---|---|---|
| Number of worktrees | One per branch | One per stack (N branches inside) |
| Directory | `.worktrees/{N}-{slug}/` of the main issue | `.worktrees/{N}-{slug}/` of the stack issue |
| Active branch | Always the same | Switched via `git checkout` between layers |
| Cleanup | Remove on PR merge | Remove **only** after every PR in the stack is merged |

The binding rule lives in `lex-git-worktrees` §5 ("Shared worktree for Stacked Pull Requests"). The full operation (stack creation, cascade rebase, bottom-up merge) is in `codex-stacked-prs` and in `kata-stacked-pr-create`, `kata-stacked-pr-rebase`, `kata-stacked-pr-merge`.

**Why a single worktree:** switching branches inside the same checkout is cheaper than recreating a worktree per layer. The cost of `git checkout` across stack branches is negligible because they share the same `.git/`. Replicating `node_modules/` or IDE state across N worktrees would be wasteful for a job that is conceptually one cohesive unit.

---

## 7. Troubleshooting

| Problem | Likely cause | Solution |
|---|---|---|
| `fatal: '{dir}' already exists` | Directory created manually | Remove the directory and recreate with `git worktree add` |
| `error: branch already checked out` | Branch active in another worktree | List with `git worktree list`; remove the stale worktree |
| `git branch -d` fails | Branch still referenced by active worktree | `git worktree remove {dir} --force` first |
| `git worktree list` shows worktree without directory | Directory deleted manually without `remove` | `git worktree prune` to clean up stale references |

---

## 8. Best practices

1. **Name descriptively.** The slug should be human-readable — anyone running `ls ..` should understand the worktree's purpose without opening it.
2. **One worktree per issue.** Do not reuse worktrees across different issues — create a new one for each task.
3. **Commit before switching.** Before switching to another worktree, commit or stash changes in the current one.
4. **Immediate cleanup after merge.** Do not accumulate stale worktrees — cleanup must be part of the task finalization flow.
5. **Do not edit `.git` in the worktree.** The `.git` file in the worktree directory is a pointer — it is not a full `.git` directory; do not modify it manually.

---

## References

- `lex-git-worktrees` — corresponding Law
- `kata-git-worktree` — step-by-step procedure
- `lex-git-branches` — branch naming convention
- `lex-issue-first` — issue required before the branch
- `lex-agent-planning` — task planning before execution
