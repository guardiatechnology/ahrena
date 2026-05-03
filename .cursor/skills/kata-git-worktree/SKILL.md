---
name: kata-git-worktree
description: "Create and Manage a Git Worktree. Creates an isolated git worktree for a branch-based task following lex-git-worktrees: verify issue → compose branch {type}/{N}-{slug} + directory ../{repo}-{N}-{slug}/ → create via EnterWorktree or CLI → work inside → PR → cleanup after merge."
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
2. Record the issue number — mandatory part of branch and directory names
3. If issue does not exist → stop, ask user to create it first

### Step 2: Compose branch and directory names

```
branch = {type}/{issue-number}-{slug}
wtDir  = .worktrees/{issue-number}-{slug}/
```

Example: Issue #42, type `feat`, slug `scheduled-payments-api`
→ Branch: `feat/42-scheduled-payments-api`
→ Directory: `.worktrees/42-scheduled-payments-api`

Present to user for confirmation before creating.

### Step 3: Check existing worktrees

```powershell
git worktree list
```

- Branch already checked out in another worktree → ask: resume (skip to Step 5) or create new?
- Target directory exists but is not a worktree → alert user, request confirmation

### Step 4: Create the worktree

**Via Claude Code (preferred):** use `EnterWorktree` tool with branch from Step 2.

**Via CLI:**
```powershell
git worktree add $wtDir -b $branch
git worktree list  # confirm
```

### Step 5: Enter the worktree and execute the task

```powershell
Set-Location $wtDir
# implement, commit with Conventional Commits format
git push -u origin $branch
```

### Step 6: Commit and open PR

```powershell
gh pr create --title "{type}({scope}): {description}" `
             --body "Closes #$issue" --base main --head $branch
```

Communicate PR URL to user.

### Step 7: Cleanup after merge

```powershell
Set-Location ../..
git worktree remove $wtDir --force
git branch -d $branch
git worktree list  # verify removed
```

## Restrictions

- Never create worktree without existing issue
- Never reuse worktree from another issue
- Never edit files outside the worktree during task execution
- Never skip cleanup
- Never delete branch before removing worktree

## References

- `lex-git-worktrees` — Law
- `codex-git-worktrees` — Manual with conventions, lifecycle, and troubleshooting
- `lex-git-branches` — Branch naming convention
- `lex-issue-first` — Issue required before branch
