# Kata: Bottom-Up Merge of Stacked PRs

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Merge a chain of stacked Pull Requests in the correct order (base → top), explicitly updating the next layer's `base` after each merge, using `gh` + `git` (vanilla path)

## Objective

This Kata defines the procedure to merge an entire stack respecting the bottom-up policy: the bottom layer (`stack-1`) merges first into `main`; then the layer-2 PR has its `base` updated from `stack-1` to `main` via `gh pr edit`, the branch is rebased onto `main` and force-pushed; the cycle repeats up to the last layer. After the last layer (which carries `Closes #N`) merges, the umbrella issue closes automatically, and the agent cleans up the shared worktree and local branches.

## When to Use

- When the base layer (`stack-1`) has review approval and is ready to merge
- When an intermediate layer is approved and the previous one has already merged
- When all layers are approved and the user wants to close the entire stack in sequence

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Active stack | Yes | N PRs on GitHub created by `kata-stacked-pr-create`, in order `stack-1` → `stack-N` |
| Review approval | Yes | At least the base layer approved per `lex-pr-quality` (CODEOWNERS) |
| Merge strategy | No | `--squash` (recommended default), `--merge`, or `--rebase` — inherit the repo's setting |
| Shared worktree | Yes | `.worktrees/${N}-${SLUG}-stack/` still exists |

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

Order matters: delete remote refs **first**, then the worktree, then local branches. If cleanup is interrupted midway, orphan remote refs are the worst state possible (they pollute `git branch -r`, complicate PR-list tooling); keeping the worktree and local branches is recoverable.

```bash
# Exit the worktree
cd ../..  # back to repo root

# 1. Confirm every layer was merged
for i in $(seq 1 $N); do
  STATE=$(gh pr view "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" \
    --repo "$OWNER/$REPO" --json state --jq .state 2>/dev/null)
  if [ "$STATE" != "MERGED" ]; then
    echo "Layer $i not merged yet (state: $STATE) — aborting cleanup"
    exit 1
  fi
done

# 2. Delete remote refs (layer N may already have been deleted by --delete-branch on merge)
for i in $(seq 1 $N); do
  git push origin --delete "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" 2>/dev/null || true
done

# 3. Remove the shared worktree
git worktree remove ".worktrees/${ISSUE_NUMBER}-${SLUG}-stack" --force

# 4. Delete local branches (all layers)
for i in $(seq 1 $N); do
  git branch -D "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" 2>/dev/null || true
done

# Verify
git worktree list
git branch --list "feat/${ISSUE_NUMBER}-stack-*"
git branch -r --list "origin/feat/${ISSUE_NUMBER}-stack-*"
```

The three final `git branch` calls MUST return nothing. `git worktree list` MUST no longer show the stack worktree.

### Step 6: Final verification

- [ ] N PRs merged into `main`, in order `stack-1` → `stack-N`
- [ ] For each intermediate PR (`stack-2` through `stack-N`), the `base` was explicitly updated to `main` before merging
- [ ] Each upper layer was rebased onto `main` before merging (linear history preserved)
- [ ] Umbrella issue is `CLOSED` (auto-closed by the last `Closes #N` or manually)
- [ ] Shared worktree removed
- [ ] All local stack branches deleted
- [ ] Corresponding plan (`plan-{M}-{slug}`) moved to `archived/` if it exists

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

## Variant: git-spice

Applicable when `.ahrena/.directives` declares `stacked_prs.tool: gs`. The merge itself is **not** covered by `gs` — it remains `gh pr merge` (gs has no equivalent command). The gs gain here is in the **post-merge**: `gs repo sync` replaces the manual loop of "update next PR base → rebase onto main → force-push" with a single command. Consult `codex-git-spice` for the full mapping.

### Step 1 (gs): Verify prerequisites

Identical to the vanilla path — `gh pr checks`, `gh pr view --json reviews`, `gh pr view --json mergeable`. No changes.

### Step 2 (gs): Merge the bottom layer (1)

Identical to vanilla. `gs` does not automate PR merging; use `gh pr merge`:

```bash
gh pr merge "$PR_NUMBER" \
  --repo "$OWNER/$REPO" \
  --squash \
  --delete-branch=false
```

`--delete-branch=false` still matters: layer 1's branch is still referenced by layer 2's PR until `gs repo sync` rebuilds the state.

### Step 3 (gs): Sync and merge remaining layers

Unlike vanilla, `gs repo sync` automates the "update base + rebase + force-push" phase for all remaining layers:

```bash
# From inside the shared worktree
git-spice repo sync
# Automatic gs actions:
#   1. Pull updated trunk (with layer 1 squash-merged)
#   2. Detect layer 1 as already merged and delete it locally
#   3. Rebase layer 2 onto main
#   4. Same for layers 3..N
#   5. Update gs internal tracking
```

After `gs repo sync`, update PRs on GitHub (idempotent):

```bash
# Re-submits each layer updating base and force-pushing with lease
git-spice stack submit
```

> **Important:** `gs branch submit` / `gs stack submit` automatically updates the remote PR's `base` field when it differs from the new local base. You **don't need** `gh pr edit --base main` first — key difference vs. vanilla.

Merge each subsequent layer:

```bash
for i in $(seq 2 $N); do
  THIS_BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}"
  THIS_PR=$(gh pr view "$THIS_BRANCH" --json number --jq .number)

  # Verify prerequisites (CI, approval, mergeable)
  gh pr checks "$THIS_PR"

  # Merge (delete-branch only on the last)
  if [ "$i" -eq "$N" ]; then
    gh pr merge "$THIS_PR" --squash --delete-branch
  else
    gh pr merge "$THIS_PR" --squash --delete-branch=false
  fi

  # Sync gs after each merge
  git-spice repo sync
done
```

`gs repo sync` is idempotent — calling it after each merge keeps state coherent at negligible cost.

### Step 4 (gs): Confirm the umbrella issue closed

Identical to vanilla — `gh issue view $ISSUE_NUMBER --json state` should return `CLOSED`. No `gs` involvement.

### Step 5 (gs): Cleanup of worktree and local branches

`gs repo sync` already did part of the work (deleted merged branches locally). What remains:

```bash
# Exit the worktree
cd ../..

# (Optional) confirm no stack branches still tracked
git-spice log short
# Should show only trunk and unrelated branches

# Remove the shared worktree
git worktree remove ".worktrees/${ISSUE_NUMBER}-${SLUG}-stack" --force

# Local stack branches should already be deleted by gs repo sync;
# if any survived (e.g., interrupted gs repo sync):
git branch --list "feat/${ISSUE_NUMBER}-stack-*" | xargs -r git branch -D

# Remote refs: --delete-branch on the layer N merge deleted the last;
# intermediate layers may have leftovers:
for i in $(seq 1 $((N-1))); do
  git push origin --delete "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" 2>/dev/null || true
done
```

### Operational notes (gs)

- **Merge is still `gh pr merge`:** `gs` does not operate against GitHub to close PRs; it remains via `gh`.
- **`gs repo sync` is the real win:** eliminates the manual update-base+rebase+push loop in the post-merge phase.
- **Stack edit rarely needed here:** if you need to reorder layers during the merge, it signals the Decision Checklist failed — abort and invoke `kata-stacked-pr-rebase`.
- **Post-merge rebase conflicts:** delegate to `kata-stacked-pr-rebase` (gs variant) — do not try to resolve inside this kata.

## References

- `codex-stacked-prs` — conceptual model; lifecycle; bottom-up policy
- `codex-git-spice` — `gs repo sync`, `gs stack submit`, post-merge flow
- `kata-stacked-pr-create` — initial stack creation
- `kata-stacked-pr-rebase` — cascade rebase when conflicts occur
- `lex-pr-quality` — 8-criteria HARD-GATE met by each PR before merge
- `lex-protected-trunk` — `main` receives code only via approved PR merge
- `lex-issue-first` — `Closes #N` on the last layer closes the issue
- `lex-git-worktrees` — exception stack=shared worktree
