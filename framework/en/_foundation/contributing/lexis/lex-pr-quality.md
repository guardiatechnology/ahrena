# Lexis: Pull Request Quality Requirements

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All Pull Requests in Guardia repositories

## Law

> **Every PR in a Guardia repository MUST: (1) mirror all labels from the associated issue; (2) carry exactly one size label (`size/XS` to `size/XXL`), applied automatically by GitHub Actions or manually when automation is not yet configured; (3) apply PR-specific labels when applicable (`breaking change 💥`, `security 🛡️`, `release ↗️`); (4) be assigned to the author with `--assignee @me`. PRs that do not satisfy these requirements MUST NOT be merged.**

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

### 5. Prerequisites before creating the PR

The agent MUST verify, in this order, before running `gh pr create`:

1. The associated issue exists and complies with `lex-issue-quality`.
2. The branch follows the format defined in `lex-git-branches`.
3. The PR body includes `Closes #N` or `Refs #N` per `lex-issue-first`.
4. Labels from the issue have been mirrored.
5. The size label has been applied (manually if needed).

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

- **Tool:** GitHub Actions PR size labeler (auto-applies `size/*`); review checklist verifies mirrored labels and assignee; `kata-contributing-pr` applies every rule from this Lexis when creating PRs.
- **When:** on PR creation and update; during the review checklist.
- **Metric:** 0 PRs merged without a size label; 0 PRs merged without mirrored issue labels; 0 PRs without an assignee.
