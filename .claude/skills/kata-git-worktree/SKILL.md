---
name: kata-git-worktree
description: "Deleted branch feat/42-scheduled-payments-api. Creating, using, and removing git worktrees for branch-based tasks, per lex-git-worktrees"
---

# Kata: Create and Manage a Git Worktree

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creating, using, and removing git worktrees for branch-based tasks, per `lex-git-worktrees`

## Workflow

```
Progress:
- [ ] 1. Verify the issue
- [ ] 2. Compose branch and directory names
- [ ] 3. Check existing worktrees
- [ ] 4. Create the worktree
- [ ] 5. Enter the worktree and execute the task
- [ ] 6. Commit and open PR
- [ ] 7. Perform cleanup after merge
```

### Step 1: Verify the issue

1. Confirm the GitHub Issue exists and is open (per `lex-issue-first`)
2. Record the issue number — it will be a mandatory part of the branch and directory
3. If the issue does not exist → stop and ask the user to create the issue before proceeding

### Step 2: Compose branch and directory names

Based on inputs:

```
branch  = {type}/{issue-number}-{slug}
wtDir   = .worktrees/{issue-number}-{slug}/
```

Examples:
- Issue #42, type `feat`, slug `scheduled-payments-api`
- Branch: `feat/42-scheduled-payments-api`
- Directory: `.worktrees/42-scheduled-payments-api`

Present to the user for confirmation before creating.

### Step 3: Check existing worktrees

```powershell
git worktree list
```

- If the branch is already in use in an existing worktree → ask the user whether to resume that worktree (skip to Step 5) or create a new one
- If the target directory already exists but is not a worktree → alert the user and request confirmation before overwriting

### Step 4: Create the worktree

**Via Claude Code (preferred):**

Use the `EnterWorktree` tool with the branch composed in Step 2.

**Via CLI (PowerShell):**

```powershell
git worktree add $wtDir -b $branch
```

Confirm creation:
```powershell
git worktree list
```

### Step 5: Enter the worktree and execute the task

```powershell
Set-Location $wtDir
```

Inside the worktree:
- Execute the entire implementation inside this directory
- Commit with Conventional Commits format messages (per `lex-conventional-commits`)
- Push the branch regularly to the remote:
  ```powershell
  git push -u origin $branch
  ```

### Step 6: Commit and open PR

When the task is complete:

1. Ensure all commits are made and the branch is up to date on the remote
2. Open the PR referencing the issue:

```powershell
gh pr create --title "{type}({scope}): {description}" `
             --body "Closes #$issue" `
             --base main `
             --head $branch
```

3. Record the PR URL and communicate it to the user

### Step 7: Perform cleanup after merge

After confirming the PR has been merged:

```powershell
# 1. Navigate to the repository root (if inside the worktree)
Set-Location ../..

# 2. Remove the worktree
git worktree remove $wtDir --force

# 3. Delete the local branch
git branch -d $branch

# 4. Verify
git worktree list
```

Confirm to the user: "Worktree `{wtDir}` removed. Branch `{branch}` deleted."

## Outputs

| Output | Description |
|--------|-------------|
| Worktree created | Directory `.worktrees/{issue-number}-{slug}/` with the active branch |
| Branch created | `{type}/{issue-number}-{slug}` in the repository |
| PR opened | PR URL referencing the issue |
| Cleanup | Worktree and branch removed after merge |

## Execution Example

### Input

```
Issue: #42 "Add scheduled payments API"
Type: feat
Slug: scheduled-payments-api
Repository: ahrena
```

### Step 2 — Composed names

```
Branch:    feat/42-scheduled-payments-api
Directory: .worktrees/42-scheduled-payments-api
```

### Step 4 — Creation

```powershell
git worktree add .worktrees/42-scheduled-payments-api -b feat/42-scheduled-payments-api
# Preparing worktree (new branch 'feat/42-scheduled-payments-api')
# HEAD is now at 4df8e43 Merge pull request #33...
```

### Step 6 — PR

```powershell
gh pr create --title "feat(payments): add scheduled payments API" `
             --body "Closes #42" --base main --head feat/42-scheduled-payments-api
# https://github.com/guardiatechnology/ahrena/pull/43
```

### Step 7 — Cleanup

```powershell
git worktree remove .worktrees/42-scheduled-payments-api --force
git branch -d feat/42-scheduled-payments-api
# Deleted branch feat/42-scheduled-payments-api
```

## Restrictions

- **Never create a worktree without an existing issue** — stop and inform the user if the issue does not exist
- **Never reuse a worktree from another issue** — each task has its own worktree
- **Never make edits outside the worktree** during task execution
- **Never skip cleanup** — stale worktrees accumulate and pollute `git worktree list`
- **Never delete the branch before removing the worktree** — git rejects the operation
