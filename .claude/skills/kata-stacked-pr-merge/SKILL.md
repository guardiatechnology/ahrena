---
name: kata-stacked-pr-merge
description: "Bottom-Up Merge of Stacked PRs. Merge a chain of stacked Pull Requests in the correct order (base → top), explicitly updating the next layer's base after each merge, using gh + git (vanilla path)"
---

# Kata: Bottom-Up Merge of Stacked PRs

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Merge a chain of stacked Pull Requests in the correct order (base → top), explicitly updating the next layer's `base` after each merge, using `gh` + `git` (vanilla path)

## Workflow

```
Progress:
- [ ] 1. Verify preconditions (CI green, approval, no conflict)
- [ ] 2. Merge the bottom layer (1)
- [ ] 3. For each upper layer: update base → rebase → force-push → merge
- [ ] 4. Confirm umbrella issue closure
- [ ] 5. Cleanup of worktree and local branches
- [ ] 6. Final verification
```

### Step 1: Verify preconditions

For the layer about to be merged (`current_layer`):

```bash
PR_NUMBER=$(gh pr view "$LAYER_BRANCH" --json number --jq .number)

# CI green?
gh pr checks "$PR_NUMBER" --repo "$OWNER/$REPO"

# Approval present?
gh pr view "$PR_NUMBER" --json reviews \
  --jq '[.reviews[] | select(.state=="APPROVED")] | length'

# No conflict declared by GitHub?
gh pr view "$PR_NUMBER" --json mergeable --jq .mergeable
```

If any criterion fails, stop and report to the user. Do not try to force.

### Step 2: Merge the bottom layer (1)

Layer 1 has `base: main`. Direct merge:

```bash
gh pr merge "$PR_NUMBER" \
  --repo "$OWNER/$REPO" \
  --squash \
  --delete-branch=false
```

| Flag | Reason |
|---|---|
| `--squash` | Recommended default — produces linear history on `main` |
| `--delete-branch=false` | Important: the `feat/${N}-stack-1-${SLUG}` branch is still the base of the layer-2 PR; deleting it breaks the reference |

After the merge, refresh `main` in the worktree:

```bash
git fetch origin main
```

### Step 3: For each upper layer — update base → rebase → force-push → merge

Loop for layers `2..N`:

```bash
PREV_PR="$PR_NUMBER"   # PR already merged (layer i-1)
for i in $(seq 2 $N); do
  THIS_BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}"
  THIS_PR=$(gh pr view "$THIS_BRANCH" --json number --jq .number)

  # 3a. Update PR base to main (GitHub does not migrate automatically)
  gh pr edit "$THIS_PR" --repo "$OWNER/$REPO" --base main

  # 3b. Local rebase of the branch onto main
  git checkout "$THIS_BRANCH"
  git rebase origin/main

  # if conflict, resolve per kata-stacked-pr-rebase step 4

  # 3c. Force-push with lease
  git push --force-with-lease origin "$THIS_BRANCH"

  # 3d. Verify preconditions (CI green after force-push, approval)
  gh pr checks "$THIS_PR"
  gh pr view "$THIS_PR" --json reviews \
    --jq '[.reviews[] | select(.state=="APPROVED")] | length'

  # 3e. Merge (if last layer, delete branch after)
  if [ "$i" -eq "$N" ]; then
    gh pr merge "$THIS_PR" --squash --delete-branch
  else
    gh pr merge "$THIS_PR" --squash --delete-branch=false
  fi

  PREV_PR="$THIS_PR"
  git fetch origin main
done
```

**Critical points:**

- `gh pr edit --base main` MUST run **before** rebase + push. If the PR's base is still `feat/${N}-stack-1-...` (which just merged), GitHub gets confused; switching first prevents surprises.
- `--delete-branch=false` on intermediate layers preserves the reference used by upcoming layers (even though their base is already changed, keep consistency).
- `--delete-branch` on the **last layer** triggers automatic cleanup on GitHub.

### Step 4: Confirm umbrella issue closure

The last layer carries `Closes #N` in the body. After its merge, GitHub closes the issue.

```bash
gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" --json state --jq .state
# expected: CLOSED
```

If still `OPEN`, check whether the last layer carried `Closes #N` in the body — if missing, close manually with reference in the comment:

```bash
gh issue close "$ISSUE_NUMBER" --comment "Closed by #${LAST_PR_NUMBER} (last stack layer)."
```

### Step 5: Cleanup of worktree and local branches

After all layers are merged:

```bash
# Exit the worktree
cd ../..  # back to repo root

# Remove the shared worktree
git worktree remove ".worktrees/${ISSUE_NUMBER}-${SLUG}-stack" --force

# Delete local branches (all layers)
for i in $(seq 1 $N); do
  git branch -D "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" 2>/dev/null || true
done

# Verify
git worktree list
git branch --list "feat/${ISSUE_NUMBER}-stack-*"
```

`git worktree list` MUST no longer show the stack worktree. `git branch --list` MUST return nothing.

### Step 6: Final verification

- [ ] N PRs merged into `main`, in order `stack-1` → `stack-N`
- [ ] For each intermediate PR (`stack-2` through `stack-N`), the `base` was explicitly updated to `main` before merging
- [ ] Each upper layer was rebased onto `main` before merging (linear history preserved)
- [ ] Umbrella issue is `CLOSED` (auto-closed by the last `Closes #N` or manually)
- [ ] Shared worktree removed
- [ ] All local stack branches deleted
- [ ] Corresponding plan (`plan-NNN-...`) moved to `archived/` if it exists

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Merged stack | N squash commits on `main` | Repository's `main` |
| Closed issue | GitHub Issue state CLOSED | Repository |
| Clean worktree | Removed directory | Local filesystem |
| Deleted branches | Local and remote branches removed | Local + remote |

## Constraints

- **Never** merge out of order (layer 3 before layer 2) — it breaks the next PR's base and forces manual reconstruction
- **Never** delete the layer `i-1` branch before merging layer `i` (reference used by the next PR)
- **Do not** change merge strategy between layers — keep `--squash` (or whatever the repo standardizes) consistent
- **Do not** merge via the GitHub UI during the sequence — use exclusively `gh pr merge` via CLI to coordinate with the rebase steps
- If a conflict appears during an upper layer's rebase, **stop** and invoke `kata-stacked-pr-rebase` (step 4) — do not try to resolve inside this kata
- If the umbrella issue does not auto-close, **investigate before closing manually** — it may indicate that `Closes #N` is missing on the wrong PR
