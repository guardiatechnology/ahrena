# Lexis: Mandatory Use of Git Worktrees

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Every branch-based task executed by AI agents in the Ahrena context

## Law

> **Every agent that needs to create a branch to implement a task MUST do so inside a dedicated git worktree, created from the main repository. The worktree branch MUST follow `lex-git-branches` (`{type}/{issue-number}-{slug}`) and a GitHub Issue MUST exist before creation (per `lex-issue-first`). The worktree directory MUST use the branch slug as a human-readable name. Working directly on the main checkout with changes belonging to a task branch is FORBIDDEN. The worktree MUST be removed after the corresponding PR is merged.**

## Coverage

- **Applies to:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, any AI agent that creates branches to implement tasks
- **Bound agents:** all warriors and katas that produce code or artifacts on dedicated branches (`warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`)
- **Allowed exceptions:**
  - Direct commits to `main` for trivial typo or formatting fixes (per `lex-issue-first`)
  - Read-only operations that produce no branch
  - **Stacked Pull Requests** — an entire stack uses a single shared worktree instead of one worktree per branch. Detailed rule in section 5 below

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

### 5. Shared worktree for Stacked Pull Requests

When a feature is decomposed into N stacked layers (per `codex-stacked-prs`), the "one worktree per branch" rule from sections 2-4 does NOT apply. The entire stack operates inside **a single** shared worktree.

**Reason:** the cascade rebase (`kata-stacked-pr-rebase`) operates by reading and rewriting the stack branches in sequence, and requires a single working dir. One worktree per branch breaks that assumption.

#### 5.1 Directory naming

```
.worktrees/{issue-number}-{slug}-stack/
```

| Field | Rule |
|---|---|
| `issue-number` | Umbrella issue number (1 issue → N layers) |
| `slug` | Descriptive feature slug, **without** the `stack-{layer}` segment |
| `-stack` suffix | Literal and mandatory — canonical signal that the directory hosts a stack |

Example: for issue #42 ("Scheduled Payments"), the worktree is `.worktrees/42-scheduled-payments-stack/`. Inside it coexist branches `feat/42-stack-1-schema`, `feat/42-stack-2-api`, `feat/42-stack-3-ui`.

#### 5.2 Branches inside the shared worktree

Each layer has its own branch, following the `lex-git-branches` pattern:

```
{type}/{issue-number}-stack-{layer}-{slug}
```

The base layer (`layer = 1`) is created together with the worktree, starting from `main`. Upper layers (`layer ≥ 2`) are created from the previous layer:

```bash
git worktree add .worktrees/${N}-${SLUG}-stack -b feat/${N}-stack-1-${SLUG} main
cd .worktrees/${N}-${SLUG}-stack
# work on layer 1, commit, push
git checkout -b feat/${N}-stack-2-${SLUG} feat/${N}-stack-1-${SLUG}
# work on layer 2, commit, push
```

#### 5.3 Switching between layers

The agent switches between layers using `git checkout` inside the same directory — **never** by creating additional worktrees for the same stack:

```bash
git checkout feat/${N}-stack-1-${SLUG}    # back to base layer
git checkout feat/${N}-stack-3-${SLUG}    # go to top
```

#### 5.4 Cleanup after the stack merges

When the last stack layer merges (the one carrying `Closes #N`), the issue closes and cleanup is unified:

```bash
cd ../..
git worktree remove .worktrees/${N}-${SLUG}-stack --force
# delete ALL local stack branches
for i in $(seq 1 $N); do
  git branch -D feat/${N}-stack-${i}-${SLUG_i} 2>/dev/null || true
done
```

See `kata-stacked-pr-merge` (Step 5) for the full procedure.

#### 5.5 Specific constraints

- **Never** create more than one worktree for the same stack — all layers live in the `-stack/` directory
- **Never** mix branches from different stacks in the same worktree
- **Never** work on a stack branch from the main checkout — the entire stack is the dedicated worktree's task
- The `-stack` suffix in the directory name is **literal** — do not replace it with an internal convention

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

## References

- `codex-git-worktrees` — manual with conventions, lifecycle, and commands
- `kata-git-worktree` — step-by-step procedure
- `lex-git-branches` — branch naming convention
- `lex-issue-first` — issue required before the branch
- `codex-stacked-prs` — declared exception: a stack uses a single shared worktree
