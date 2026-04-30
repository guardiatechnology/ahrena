# Lexis: Git Branch Naming Convention

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All git branches in Guardia repositories

## Law

> **Every branch MUST follow the format `{type}/{issue-number}-{kebab-slug}`, where `type` MUST be one of the Conventional Commits types (`feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test`), `{issue-number}` is the GitHub Issue number the branch is tied to, and `{kebab-slug}` is a brief, lowercase, hyphen-separated description of the change. Creating or pushing a branch without an associated Issue is FORBIDDEN. Branch names outside this format are FORBIDDEN.**

## Coverage

- **Applies to:** all working branches in all Guardia repositories. Trunk branches (`main`, `master`, `release/*`) **are not working branches** — they are protected targets governed by `lex-protected-trunk` and receive code only through merged PRs from a branch named per this Law.
- **Bound agents:** developers, AI agents that create branches (warrior-athena, warrior-apollo, warrior-hephaestus).
- **Exceptions:** None. Branches outside the valid format are rejected at push.

## Rules

### 1. Format

```
{type}/{issue-number}-{slug}
```

| Part | Rule |
|------|------|
| `type` | One of: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `issue-number` | Positive integer matching the associated GitHub Issue number |
| `slug` | Lowercase, kebab-case, maximum 50 characters; summarizes the change |

### 2. Issue before branch

A branch MUST NOT be created before the corresponding Issue exists. See `lex-issue-first`.

### 3. Work never starts on trunk

Before any commit, the developer (human or AI) **MUST** verify the active branch via `git rev-parse --abbrev-ref HEAD`. If it is `main`, `master`, or starts with `release/`, they **MUST** create a working branch per this Law (`git checkout -b {type}/{N}-{slug}`) before producing any change. Editing files with the working copy positioned on trunk is FORBIDDEN. The protection regime is detailed in `lex-protected-trunk`.

### 4. One branch per Issue (default)

Each Issue typically corresponds to one branch. Exceptions (multiple branches for a single complex Issue) require explicit justification in the Issue comments.

## Examples

### Correct

```
feat/42-oauth2-authentication
fix/123-null-pointer-in-transaction
chore/89-update-rust-dependencies
docs/201-contributing-guide-revision
refactor/77-extract-payment-service
test/310-coverage-for-refund-module
ci/95-add-github-actions-lint
```

### Incorrect

```
seguim/wizardly-ptolemy-adb24b   # ❌ generated name, no type, no issue number
my-feature                       # ❌ no type, no issue number
wip/auth                         # ❌ wip is not a valid Conventional Commits type
feat-42-oauth2                   # ❌ slash separator required between type and rest
feat/oauth2-authentication       # ❌ missing issue number
```

## Automated Validation

- **Tool:** pre-push hook with regex `^(feat|fix|docs|build|chore|ci|style|refactor|perf|test)\/[0-9]+-[a-z0-9][a-z0-9-]{0,49}$`; GitHub branch protection rules.
- **When:** on branch push to remote; on PR creation.
- **Metric:** 0 branches on remote outside the defined format.
