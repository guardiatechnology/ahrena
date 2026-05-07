---
name: kata-stacked-pr-rebase
description: "Cascade Rebase in Stacked PRs. Propagate changes made in a lower stack layer up to all upper layers, using git rebase + git push --force-with-lease (vanilla path)"
---

# Kata: Cascade Rebase in Stacked PRs

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Propagate changes made in a lower stack layer up to all upper layers, using `git rebase` + `git push --force-with-lease` (vanilla path)

## Workflow

```
Progress:
- [ ] 1. Identify modified layer and chain above
- [ ] 2. Push the modified layer with --force-with-lease
- [ ] 3. For each upper layer: rebase + push
- [ ] 4. Resolve conflicts when they happen
- [ ] 5. Final verification
```

### Step 1: Identify modified layer and chain above

1. Enter the shared worktree:
   ```bash
   cd .worktrees/${ISSUE_NUMBER}-${SLUG}-stack
   ```
2. List all stack branches in order (base → top):
   ```bash
   git branch --list "feat/${ISSUE_NUMBER}-stack-*-${SLUG}" | sort
   ```
3. Identify the modified layer and the layers above it. E.g., if layer 2 changed, layers 3..N need rebase.

### Step 2: Push the modified layer with `--force-with-lease`

The modified layer is already committed locally (amend, new commit, or rebase against `main`). Push with lease:

```bash
git checkout "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"
git push --force-with-lease origin "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"
```

**Never use blind `--force`.** `--force-with-lease` rejects the push if another reviewer committed on top since the last fetch — it protects against overwriting someone else's work.

### Step 3: For each upper layer — rebase + push

Ascending loop, from layer `MODIFIED_LAYER + 1` up to `N`:

```bash
for i in $(seq $((MODIFIED_LAYER + 1)) $N); do
  PREV="feat/${ISSUE_NUMBER}-stack-$((i-1))-${PREV_SLUG}"
  THIS="feat/${ISSUE_NUMBER}-stack-${i}-${THIS_SLUG}"

  git checkout "$THIS"
  git rebase "$PREV"

  # if conflict, see Step 4 before continuing

  git push --force-with-lease origin "$THIS"
done
```

Each iteration:
1. Checkout of the upper layer
2. `git rebase {previous layer}` — replay of the upper layer's unique commits on top of the updated previous layer
3. `git push --force-with-lease`

### Step 4: Resolve conflicts

When `git rebase` stops with a conflict:

1. **Identify conflicting files:**
   ```bash
   git status
   ```
2. **Resolve manually** the `<<<<<<<` / `=======` / `>>>>>>>` markers. The resolution choice depends on context — if uncertain, stop and consult the user.
3. **Mark resolved and continue:**
   ```bash
   git add <resolved-files>
   git rebase --continue
   ```
4. **Abort when unrecoverable** (rare):
   ```bash
   git rebase --abort
   ```
   Returns to the pre-rebase state. Investigate and try again, possibly with a different decomposition.

**Special case — upstream squash merge created divergence:**

If the previous layer was squash-merged into `main`, the original commits are gone and a regular rebase produces "artificial conflicts." Use `--onto`:

```bash
# Instead of:
# git rebase feat/${N}-stack-1-${SLUG}
# Do:
git rebase --onto main "feat/${N}-stack-1-${SLUG}" "feat/${N}-stack-2-${SLUG}"
```

`--onto` replays only the unique commits of layer 2 (excluding those of layer 1 already squashed) on top of `main`.

### Step 5: Final verification

- [ ] The modified layer was pushed with `--force-with-lease` (not `--force`)
- [ ] All upper layers were rebased in ascending order
- [ ] All pushes succeeded (none rejected due to unexpected divergence)
- [ ] `git log --oneline {top} ^main` shows the expected linear history
- [ ] Resolved conflicts preserved both layers' intent (no accidentally discarded changes)
- [ ] Commented on GitHub PRs if the change is significant enough that reviewers need to re-contextualize

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Rebased upper branches | Linear git history | Remote repository |
| Updated PRs | GitHub PRs | Auto-updated via push (same `head` ref) |

## Constraints

- **Never** use blind `--force` — always `--force-with-lease`
- **Never** rebase `main` in the cascade flow — only rebase stack branches
- **Do not** rebase in the wrong order (top-down) — this can reintroduce already obsolete changes
- If a conflict is large or ambiguous, **stop** and consult the user instead of guessing
- If the stack is left inconsistent (rebase failed in the middle), **do not hide the state** — list remaining branches to the user and propose `git rebase --abort` or manual continuation
- Heavy pre-push hooks (linters, tests) can make the cascade very slow; in extreme cases, consider `--no-verify` **with explicit user authorization** and recorded justification
