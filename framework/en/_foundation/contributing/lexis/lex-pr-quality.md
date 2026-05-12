# Lexis: Pull Request Quality Requirements

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All Pull Requests in Guardia repositories

## Law

> **Every PR in a Guardia repository MUST: (1) mirror all labels from the associated issue; (2) carry exactly one size label (`size/XS` to `size/XXL`), applied automatically by GitHub Actions or manually when automation is not yet configured; (3) apply PR-specific labels when applicable (`breaking change 💥`, `security 🛡️`, `release ↗️`); (4) be assigned to the author with `--assignee @me`; (5) have reviewers requested from the repository's `.github/CODEOWNERS` — automatically by GitHub when auto-request is enabled, or manually via `gh pr edit --add-reviewer` before merge; (6) when the PR receives review comments (human or bot — Gemini, Argos, claude[bot], CodeRabbit, etc.) and fixes are applied, EACH addressed comment MUST receive an individual reply on its original thread containing the SHA of the fix commit + a one-line rationale, before re-requesting review or marking the PR as ready to merge. The repository MUST have a `.github/CODEOWNERS` file with at least one default owner (`* @{team}`). PRs that do not satisfy these requirements MUST NOT be merged.**

## Coverage

- **Applies to:** every Pull Request in every Guardia repository.
- **Bound agents:** developers, AI agents (warrior-athena, warrior-apollo, warrior-hephaestus) that create or review PRs.
- **Exceptions:** automatic PRs from Dependabot and security scanning tools, which follow their own flow. Every other exception requires explicit justification in the PR.

## Rules

### 1. Mirror labels from the issue

When creating a PR, the agent MUST:

1. Fetch all labels from the associated issue.
2. Apply the same labels to the PR.
3. Add PR-specific labels when applicable (see Rule 3).

```bash
# Fetch labels from the associated issue
LABELS=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(",")')

# Mirror them on the PR
gh pr edit $PR_NUMBER --repo $OWNER/$REPO --add-label "$LABELS"
```

### 2. Mandatory size label

Every PR MUST carry exactly one size label (`size/XS`, `size/S`, `size/M`, `size/L`, `size/XL`, or `size/XXL`):

- **When GitHub Actions is configured:** the label is applied automatically on PR creation/update. Do not apply manually.
- **When GitHub Actions is not configured or has not run yet:** the agent MUST compute the size manually and apply the label before opening the PR for review.

**Manual size computation:**

```bash
# Count modified lines against the base branch (ignoring generated files)
git diff main...HEAD --stat | tail -1
```

| Label | Modified lines |
|-------|:--------------:|
| `size/XS` | 0–9 |
| `size/S` | 10–29 |
| `size/M` | 30–99 |
| `size/L` | 100–499 |
| `size/XL` | 500–999 |
| `size/XXL` | 1,000+ |

### 3. PR-specific labels

Add additionally when applicable:

| Label | When to apply |
|-------|---------------|
| `breaking change 💥` | PR introduces an incompatible API change; requires major version bump |
| `security 🛡️` | PR resolves a security vulnerability |
| `release ↗️` | Release PR — maintainers only |

### 4. Author assignment

Every PR MUST be assigned to the author:

```bash
gh pr create ... --assignee "@me"
# or after creation:
gh pr edit $PR_NUMBER --add-assignee "@me"
```

### 5. Reviewers via CODEOWNERS

Every PR MUST have reviewers requested from the repository's `.github/CODEOWNERS`:

1. **Precondition (repo configuration):** the repository MUST have `.github/CODEOWNERS` with at least one default owner (`* @org/team`) and Branch Protection settings with code-owner review auto-request enabled.
2. **When auto-request is enabled:** GitHub automatically requests CODEOWNERS reviewers on PR creation. The agent MUST verify (`gh pr view $PR --json reviewRequests`) that at least one reviewer was requested.
3. **When no reviewers are requested after creation:** the agent MUST apply manually before marking the PR as ready:

```bash
# Check current reviewers
gh pr view $PR_NUMBER --json reviewRequests --jq '[.reviewRequests[].login]'

# Manually request the default CODEOWNERS team
gh pr edit $PR_NUMBER --add-reviewer "org/team"
```

PRs without any requested reviewer (after creation and manual fallback) MUST NOT be merged.

### 6. Prerequisites before creating the PR

The agent MUST verify, in this order, before running `gh pr create`:

1. The associated issue exists and complies with `lex-issue-quality`.
2. The branch follows the format defined in `lex-git-branches`.
3. The PR body includes `Closes #N` or `Refs #N` per `lex-issue-first`.
4. The repository has `.github/CODEOWNERS` configured.

And verify, **immediately after** `gh pr create`:

5. Labels from the issue have been mirrored.
6. The size label has been applied (manually if needed).
7. At least one reviewer has been requested (auto via CODEOWNERS or manual via `--add-reviewer`).
8. `status: <name>` label applied (`status: to review` by default when opening the PR; per `lex-issue-status`).
9. **"Session Trace"** section present in the PR body when `session_tracking.enabled == true` in `.ahrena/.directives` and the branch has associated heartbeat files (per `codex-session-tracking` §7). Built by `kata-pr-prepare` by aggregating `.ahrena/workflow/sessions/*.json` filtered by the current branch. In PRs driven exclusively by a human (no Claude Code agent), the section may be `_(human-driven; no session trace)_`.

### 7. Per-thread reply to addressed review comments

When the PR receives review comments (human or bot — `gemini-code-assist`, `warrior-argos`, `claude[bot]`, `coderabbitai`, etc.) and the author (or an agent acting on their behalf) applies fixes, EACH comment addressed by the commit MUST receive an individual reply on its original thread. A single top-level comment summarizing "applied N fixes" is NOT enough — auto-resolve bots rely on the in-thread reply to mark a thread as resolved, and human reviewers need per-thread closure on PRs with more than 5 comments.

**Canonical reply format:**

```
Addressed in {short-SHA}: {one-line rationale explaining what changed and why}
```

**Mechanism (GitHub CLI):**

```bash
# List PR review comments (review summary + per-line code comments)
gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments" --jq '.[] | {id, user: .user.login, body: .body, path, line}'

# Post a reply on the original thread
gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments/$COMMENT_ID/replies" \
  -f body="Addressed in ${SHA}: ${RATIONALE}"
```

> **Rule 7 scope:** applies to **PR review comments** — those returned by `/pulls/{N}/comments` (review summary + per-line code comments). **Issue comments on the PR *Conversation* tab** (returned by `/issues/{N}/comments`) are NOT threaded and have no `/replies` endpoint; they are out of scope for Rule 7. If a reviewer leaves remarks on the Conversation tab, the author responds with a free-form issue comment (quote-and-reply) — there is no per-thread closure requirement because the thread does not exist.

**When to add a top-level comment (allowed alongside, not as a substitute):**

- A top-level comment summarizing the batch (commit + list of fixes) is allowed to give the reviewer aggregate context.
- But every addressed thread STILL needs its individual reply. Top-level does not replace per-thread.

**Comments not addressed (rejected, deferred):** also receive a reply, stating the reason:

- `Deferred to #{issue-number} — out of scope for this PR.`
- `Disagreed — keeping as is because {rationale}. Happy to discuss.`
- `Not applicable — {explanation}.`

The rule is "every thread has closure," not "I agree with every comment."

**When the rule kicks in:** any time the agent (or human author) pushes fix commits in response to a review round. A PR that has not yet received review comments is NOT subject to Rule 7 — it becomes mandatory from the first addressed comment onward.

> **Who decides what is "addressed":** the PR author. The per-thread reply declares *the author's intent to have addressed that comment*. The reviewer retains the power to reopen the thread if they disagree — `Re-opening: the fix doesn't address {detail}` is a valid response and Rule 7 reactivates until the next closure. Rejected/deferred/not-applicable comments are also "addressed" in the Rule's sense (they receive a reply explaining why). The criterion is not "agreement" — it is "documented closure".

## HARD-GATE

Per [`lex-hard-gate-pattern`](framework/en/_foundation/quality/lexis/lex-hard-gate-pattern.md), the textual block of this Lex is canonically expressed as:

```
<HARD-GATE>
warrior-athena, warrior-apollo, warrior-hephaestus and any other
agent MUST NOT merge PR without it satisfying ALL criteria:

  (a) Associated issue conforms with lex-issue-quality
  (b) Branch follows format {type}/{issue-number}-{slug} per lex-git-branches
  (c) PR body includes Closes #N or Refs #N per lex-issue-first
  (d) Issue labels mirrored on the PR
  (e) Exactly one size label (size/XS to size/XXL) applied
  (f) PR-specific labels (breaking change, security, release)
      applied when applicable
  (g) Assignee = PR author
  (h) At least one reviewer requested from .github/CODEOWNERS
  (i) `status: <name>` label applied per lex-issue-status (entry at
      `status: to review` when opening the PR; mirrors plan `status:`)
  (j) "Session Trace" section present in the body when
      session_tracking.enabled == true and the branch has associated
      heartbeat files, per codex-session-tracking §7 (human-driven PRs
      may use the canonical exception phrase)
  (k) Each review comment addressed by a fix commit has an individual
      reply on its original thread with the SHA + a one-line
      rationale, per Rule 7 (comments not addressed — rejected,
      deferred — also receive a reply explaining why). A top-level
      summary comment is allowed alongside but does NOT replace the
      per-thread reply.

This rule applies to EVERY PR, regardless of:
  - perceived size ("it's a trivial change")
  - urgency ("production fire")
  - who requested ("the CEO asked")
  - team confidence ("the reviewer already saw it")

Single declared exception: automatic PRs from Dependabot and security
scanning tools follow their own flow. Every other exception requires
explicit justification in the PR.
</HARD-GATE>
```

### Application to Stacked PRs

In **stacked Pull Request** flows (`codex-stacked-prs`), every layer of the chain is a **real PR** on GitHub. The HARD-GATE above is evaluated **per PR of the stack**, not once for the whole chain: each layer must satisfy **all** criteria (a)–(k) before merging. The criteria themselves do not change; only the application scope is per layer.

Operational implications:

- **Issue labels (d):** mirrored on every PR of the stack.
- **Size label (e):** computed from **each layer's** diff against its base (not against `main` for the whole stack).
- **Closes/Refs (c, via `lex-issue-first`):** intermediate layers use `Refs #N`; the last layer uses `Closes #N`.
- **CODEOWNERS reviewers (h):** requested on every PR; they may be the same when the touched files map to the same owner.

`kata-stacked-pr-create` automates mirroring across all layers to reduce manual effort, but does not relax any criterion.

## Examples

### Correct

```bash
# Issue #42 with labels: documentation 📃, ci 🏗️
# Diff: 4,516 additions + 2,877 deletions → size/XXL

gh pr create \
  --title "docs: create public documentation site with MkDocs" \
  --body "Closes #42" \
  --base main \
  --assignee "@me"

gh pr edit 42 --add-label "documentation 📃,ci 🏗️,size/XXL"
```

### Incorrect

```bash
# ❌ PR created without labels
gh pr create --title "docs: add site" --body "Closes #42"
# Missing: mirrored issue labels, size label, assignee

# ❌ Size label skipped because "Actions will do it"
# When Actions is not configured, the agent MUST apply manually
```

## Automated Validation

- **Tool:** GitHub Actions PR size labeler (auto-applies `size/*`); GitHub Branch Protection with `required_pull_request_reviews` requiring code-owner approval; review checklist verifies mirrored labels, assignee, and reviewers; `kata-contributing-pr` applies every rule from this Lexis when creating PRs.
- **When:** on PR creation and update; during the review checklist; monthly audit of repository CODEOWNERS files.
- **Metric:** 0 PRs merged without a size label; 0 PRs merged without mirrored issue labels; 0 PRs without an assignee; 0 PRs merged without any requested reviewer; 0 PRs merged with review comments addressed by commits but missing per-thread replies; 100% of Guardia repositories with `.github/CODEOWNERS` configured.
