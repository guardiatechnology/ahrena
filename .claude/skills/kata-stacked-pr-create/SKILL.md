---
name: kata-stacked-pr-create
description: "Create Stacked Pull Requests. Decompose a large feature into a chain of PRs reviewable in isolation, using git + gh (vanilla path)"
---

# Kata: Create Stacked Pull Requests

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Decompose a large feature into a chain of PRs reviewable in isolation, using `git` + `gh` (vanilla path)

## Workflow

```
Progress:
- [ ] 0. Pre-flight: Decision Checklist
- [ ] 1. Validate the umbrella issue
- [ ] 2. Confirm layer decomposition with the user
- [ ] 3. Create the shared worktree
- [ ] 4. For each layer: branch + commits + push + PR
- [ ] 5. Mirror labels/assignee/reviewers on each PR
- [ ] 6. Final verification
```

### Step 0: Pre-flight — Decision Checklist

Apply the canonical Decision Checklist from [codex-stacked-prs](../codex/codex-stacked-prs.md), section 2:

1. **Count high signals** against issue + expected scope:
   - Estimated diff > 500 lines (1 point)
   - ≥ 4 independent ACs (1 point)
   - ≥ 2 technical Pillars crossed (1 point)
   - Obvious layers present (schema → API → UI; equivalent) (1 point)
   - Review independence between layers (1 point)
   - Per-layer rollback risk (1 point)
2. **Check anti-signals** (any vetoes the stack):
   - Hotfix / incident response
   - Cross-fork PR
   - Monolithic refactor without natural layers
3. **Decide:**
   - **≥ 3 high signals AND 0 anti-signals** → propose a stack to the user
   - **Otherwise** → stop and recommend the user invoke `kata-contributing-pr` (or `cry-new-pr`) for a single PR

**Present the proposal to the user** in concrete form, e.g.:

```
This issue looks like a stacked PR candidate:
  High signals: 4 (estimated diff ~800 lines, 5 ACs, 2 Pillars, obvious layers)
  Anti-signals: 0

Proposed decomposition:
  Layer 1 (schema): AC-1, AC-2 — migration + entity
  Layer 2 (api):    AC-3, AC-4 — repository + use case + router
  Layer 3 (ui):     AC-5      — frontend components

Confirm and proceed? (y/n/adjust)
```

If the user rejects or asks for a single PR, end this kata and recommend the user invoke `kata-contributing-pr` (or `cry-new-pr`) — katas do not chain-call other katas; cross-kata orchestration is the Warriors' role.

### Step 1: Validate the umbrella issue

1. Read the issue: `gh issue view $N --repo $OWNER/$REPO --json number,title,labels,assignees,body`
2. Confirm it satisfies `lex-issue-quality`:
   - Template used (feature-request / user-story-* / epic / simple-task)
   - Required labels present
   - Issue Type set (Feature / Task / Epic)
   - At least one assignee
   - Body answers Why / What / How
3. If any criterion is missing, alert the user and stop — the issue MUST be fixed before the branch (`lex-issue-first`).

### Step 2: Confirm layer decomposition

After user confirmation in Step 0, formalize the decomposition:

1. For each layer, record:
   - Short slug (kebab-case): `schema`, `api`, `ui`, `tests`, etc.
   - ACs covered: subset of the umbrella issue's ACs
   - Components touched: informal list of modules/directories
2. Present the final decomposition as a table to the user (e.g., see Step 0).
3. Save mentally — it will be used in each PR's body.

### Step 3: Create the shared worktree

Canonical naming (`codex-stacked-prs` section 4):

```bash
ISSUE_NUMBER=42
SLUG="scheduled-payments"   # without the stack-{layer} segment
WORKTREE_DIR=".worktrees/${ISSUE_NUMBER}-${SLUG}-stack"
BASE_BRANCH="feat/${ISSUE_NUMBER}-stack-1-${SLUG}"

git worktree add "$WORKTREE_DIR" -b "$BASE_BRANCH" main
cd "$WORKTREE_DIR"
```

The layer-1 branch is created together with the worktree, starting from `main`. Unlike the standard flow (`lex-git-worktrees`), the entire stack uses **a single** shared worktree — exception declared in the Lexis.

### Step 4: For each layer — branch + commits + push + PR

**Layer 1 (already on `feat/${N}-stack-1-${SLUG}`):**

1. Implement the layer's scope
2. Atomic signed commits (follow `lex-conventional-commits`, `lex-small-commits`, `lex-signed-commits`)
3. Push:
   ```bash
   git push -u origin "feat/${ISSUE_NUMBER}-stack-1-${SLUG}"
   ```
4. Create PR with `main` as base:
   ```bash
   gh pr create \
     --base main \
     --head "feat/${ISSUE_NUMBER}-stack-1-${SLUG}" \
     --title "feat(scope): layer 1 — schema (1/N)" \
     --body "Refs #${ISSUE_NUMBER} (1/N — schema)
   
   Covers: AC-1, AC-2.
   Next layer: feat/${ISSUE_NUMBER}-stack-2-${SLUG}." \
     --assignee "@me"
   ```
5. Capture the returned PR number.

**Layers 2..N:**

For each layer `i` from `2..N`, starting from the previous layer's branch:

```bash
PREV_BRANCH="feat/${ISSUE_NUMBER}-stack-$((i-1))-${SLUG}"
THIS_BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG}"

git checkout -b "$THIS_BRANCH" "$PREV_BRANCH"
# implement
# commit
git push -u origin "$THIS_BRANCH"

gh pr create \
  --base "$PREV_BRANCH" \
  --head "$THIS_BRANCH" \
  --title "feat(scope): layer ${i} — ${LAYER_NAME} (${i}/N)" \
  --body "Refs #${ISSUE_NUMBER} (${i}/N — ${LAYER_NAME})

Covers: AC-X, AC-Y.
Base: ${PREV_BRANCH} (PR #PREV_PR_NUMBER).
$( [ "$i" -eq "$N" ] && echo "Last layer — closes the issue on merge." )" \
  --assignee "@me"
```

**Layer N (last):** replace `Refs #${ISSUE_NUMBER}` with `Closes #${ISSUE_NUMBER}` in the PR body.

### Step 5: Mirror labels/assignee/reviewers on each PR

Size labels (`size/*`) are auto-applied by GitHub Actions — do not apply manually.

For each PR created in Step 4:

```bash
# Pull labels from the umbrella issue
LABELS=$(gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" \
  --json labels --jq '[.labels[].name] | join(",")')

# Mirror on the PR
gh pr edit "$PR_NUMBER" --repo "$OWNER/$REPO" --add-label "$LABELS"

# Check reviewers via CODEOWNERS (auto-request when configured)
gh pr view "$PR_NUMBER" --json reviewRequests \
  --jq '[.reviewRequests[].login]'

# If empty, add manually per .github/CODEOWNERS:
gh pr edit "$PR_NUMBER" --add-reviewer "org/team"
```

Apply PR-specific labels when applicable (see `codex-labels`):
- `breaking change 💥` — a commit breaks a contract
- `security 🛡️` — resolves a vulnerability

### Step 6: Final verification

- [ ] Decision Checklist documented (signals counted, anti-signals at zero)
- [ ] Umbrella issue satisfies `lex-issue-quality`
- [ ] Shared worktree created at `.worktrees/${N}-${SLUG}-stack/`
- [ ] N branches created following `feat/${N}-stack-{i}-{slug}`
- [ ] N PRs opened with the correct `base` (layer 1 → main; layers 2..N → previous layer)
- [ ] Each PR's body references the issue: `Refs #N` (intermediate) or `Closes #N` (last)
- [ ] Each PR's body states AC coverage and relation to adjacent layers
- [ ] Issue labels mirrored on **each** PR
- [ ] CODEOWNERS reviewers requested on each PR
- [ ] Each PR self-assigned (`@me`)
- [ ] Each layer's commits signed (GPG verification)
- [ ] Each PR satisfies `lex-pr-quality` HARD-GATE individually

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Stack of chained PRs | N PRs on GitHub | Origin repository |
| Shared worktree | Local directory | `.worktrees/${N}-${SLUG}-stack/` |
| PR URLs | List | Presented to the user in order (layer 1 → N) |

## Constraints

- **Never** proceed without explicit user confirmation in Step 0 — the agent proposes, the user decides
- **Never** create stack branches without a corresponding shared worktree
- **Never** merge PRs on GitHub via the UI during the creation phase — bottom-up merge has its own kata (`kata-stacked-pr-merge`)
- **Do not** apply `size/*` labels manually — GitHub Actions applies them
- If the Decision Checklist fails, **do not argue** — redirect immediately to `kata-contributing-pr`
- Each commit in any layer MUST follow the 4 commit Lexis (`lex-conventional-commits`, `lex-commit-language`, `lex-small-commits`, `lex-signed-commits`)
