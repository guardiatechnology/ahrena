---
paths:
  - ".github/PULL_REQUEST_TEMPLATE.md"
  - ".github/PULL_REQUEST_TEMPLATE/**"
  - ".github/CODEOWNERS"
---

# Lexis: Pull Request Quality Requirements

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All Pull Requests in Guardia repositories

## Law

> **Every PR in a Guardia repository MUST: (1) mirror all labels from the associated issue; (2) carry exactly one size label (`size/XS` to `size/XXL`), applied automatically by GitHub Actions or manually when automation is not yet configured; (3) apply PR-specific labels when applicable (`breaking change 💥`, `security 🛡️`, `release ↗️`); (4) be assigned to the author with `--assignee @me`; (5) have reviewers requested from the repository's `.github/CODEOWNERS` — automatically by GitHub when auto-request is enabled, or manually via `gh pr edit --add-reviewer` before merge. The repository MUST have a `.github/CODEOWNERS` file with at least one default owner (`* @{team}`). PRs that do not satisfy these requirements MUST NOT be merged.**

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
- **Metric:** 0 PRs merged without a size label; 0 PRs merged without mirrored issue labels; 0 PRs without an assignee; 0 PRs merged without any requested reviewer; 100% of Guardia repositories with `.github/CODEOWNERS` configured.
