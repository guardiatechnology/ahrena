# Kata: Cascade Rebase in Stacked PRs

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Propagate changes made in a lower stack layer up to all upper layers, using `git rebase` + `git push --force-with-lease` (vanilla path)

## Objective

This Kata defines the manual procedure to handle the case where a stack layer receives a new change (extra commit, amend, or squash via review) and the layers above must rebase to absorb it. The agent works bottom-up inside the shared worktree, always with `--force-with-lease` to avoid overwriting commits from other reviewers.

## When to Use

- When review asked for adjustments on an already submitted layer (e.g., amend on layer 1)
- When `main` advanced and layer 1 must rebase (`git rebase main`)
- When an upper layer needs to absorb changes from a lower layer before becoming mergeable
- When upstream squash merge created divergence (requires `git rebase --onto`)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Active stack worktree | Yes | `.worktrees/${N}-${SLUG}-stack/` exists, created by `kata-stacked-pr-create` |
| Modified layer | Yes | Identifier of the layer where the change happened (e.g., `stack-1-schema`) |
| Upper layers | Yes | List of branches that need rebase (`stack-2-...`, `stack-3-...`) |

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

## Variant: git-spice

Applicable when `.ahrena/.directives` declares `stacked_prs.tool: gs`. The big advantage of the gs path in this kata is **auto-restack**: changing a lower layer (new commit, amend, or rebase against trunk) automatically reapplies the upper layers' commits on top of the new base. The agent rarely needs a manual loop; on conflict, `gs rebase continue` replaces `git rebase --continue`. Consult `codex-git-spice` for the full mapping.

### Case 1: amend or new commit on an already-submitted layer

While inside the shared worktree and on the modified layer:

```bash
git-spice branch checkout "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"

# (a) Additional commit on the same layer
git add <files>
git-spice commit create -m "fix(scope): adjust requested in review"
# → gs reapplies layers i+1..N on top of the new commit

# (b) Amend the layer's last commit
git add <files>
git-spice commit amend --no-edit
# → same; auto-restack happens after the amend

# Submit the stack to reflect on the PRs (idempotent)
git-spice stack submit
# or just the affected layers:
git-spice upstack submit
```

`gs commit create` and `gs commit amend` call `git commit` underneath (GPG signature preserved when `commit.gpgsign=true` is global) and then trigger `gs upstack restack` for all upper layers.

### Case 2: trunk (`main`) advanced and the base layer needs rebase

```bash
# From any layer in the shared worktree
git-spice repo sync --restack
# Pulls trunk + deletes locally-merged branches +
# rebases the current stack against the updated trunk
```

Equivalent to the vanilla loop `git fetch && git rebase origin/main && manual cascade rebase`, in a single command.

### Case 3: upstream squash merge created divergence

If the previous layer was squash-merged (into trunk) and the unsquashed history vanished:

```bash
git-spice repo sync --restack
# Covers most cases: gs detects the squash and adjusts the base.
```

If inconsistency remains (rare):

```bash
# Move the upper layer directly on top of main
git-spice upstack onto main
# or onto another explicit base
git-spice upstack onto "feat/${ISSUE_NUMBER}-stack-3-${LAYER_SLUG}"
```

### Case 4: conflict during auto-restack

`gs` stops with a message similar to `git rebase` on conflict. Resolution:

```bash
git status
# resolve <<<<<<< / >>>>>>> markers manually
git add <resolved-files>
git-spice rebase continue
# or to abort:
git-spice rebase abort
```

`gs rebase continue` resumes the auto-restack from where it stopped — including upper layers not yet touched. Do not use `git rebase --continue` directly; it can desync gs metadata in multi-layer cascade cases.

### Case 5: push after changes

`gs` applies `--force-with-lease` automatically in `branch submit` and `stack submit`:

```bash
git-spice stack submit             # safe default: --force-with-lease
git-spice stack submit --force     # bypasses lease (DO NOT use without reason)
git-spice stack submit --no-verify # skips pre-push hooks (explicit authorization)
```

### Operational notes (gs)

- **Order matters, and gs handles it:** always start from the modified layer — `gs` propagates upward by itself.
- **Did you skip `gs commit create`?** If you ran `git commit` directly, the upper layer was not auto-restacked. Run `gs upstack restack` manually.
- **Slow hooks:** auto-restack repeats `pre-commit` per upper layer; optimize or use `--no-verify` with authorization (same discipline as vanilla).
- **GPG signing:** preserved on the resulting commits of auto-restack if `commit.gpgsign=true` is global; verify with `git log --show-signature`.

## References

- `codex-stacked-prs` — conceptual model and lifecycle
- `codex-git-spice` — `gs commit create/amend`, `gs repo sync`, `gs rebase continue/abort` commands
- `kata-stacked-pr-create` — initial stack creation
- `kata-stacked-pr-merge` — bottom-up merge (next stage in the stack's life)
- `lex-protected-trunk` — trunk never receives force-push
- `lex-signed-commits` — GPG signature preserved in rebase when `commit.gpgsign=true`
- `lex-conventional-commits` — commit discipline preserved
