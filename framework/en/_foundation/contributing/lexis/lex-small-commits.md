# Lexis: Mandatory Atomic Commits

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All commits in Guardia repositories

## Purpose

Small, atomic commits facilitate review, reduce the risk of errors, maintain a clear history, and allow safe reverts. Large commits that mix multiple changes make code review difficult and debugging risky.

This Lexis ensures that every commit represents a single logical unit of work, as recommended by Guardia's CONTRIBUTING guidelines.

## Law

> **Every commit MUST be atomic — representing a single logical change that can be integrated independently.**

## Rules

### 1. One change per commit

Each commit MUST contain changes related to a single purpose. Do not mix:
- Feature + bug fix
- Refactoring + new feature
- Formatting + logic change

### 2. Isolated functionality

Each commit MUST leave the code in a functional state. The project MUST compile and existing tests MUST pass after each individual commit.

### 3. Adequate granularity

If a commit is too large, it MUST be split into smaller commits. If a commit is too trivial (e.g., renaming a variable in a single place), it may be grouped with related changes.

### 4. Independence

Each commit MUST be understandable and, if necessary, revertible without impacting unrelated parts of the code.

## Scope

- **Applies to:** all Guardia repositories
- **Bound agents:** all
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Automatic block:** PR with mixed commits may be requested to be reorganized
2. **Alert:** reviewer requests squash or rebase to separate changes
3. **Remediation:** use `git rebase -i` to split commits or reorganize the history

## Examples

### Correct

```
# Commit 1: feature only
feat(auth): add OAuth2 client configuration

# Commit 2: tests only
test(auth): add unit tests for OAuth2 flow

# Commit 3: documentation only
docs(auth): document OAuth2 setup instructions
```

### Incorrect

```
# One commit with everything mixed — VIOLATES THE LAW
feat(auth): add OAuth2, fix header bug, update README, refactor utils

# This commit does 4 unrelated things:
# 1. Adds OAuth2 (feat)
# 2. Fixes header bug (fix)
# 3. Updates README (docs)
# 4. Refactors utils (refactor)
# It should be 4 separate commits.
```

## Automated Validation

- **Tool:** human review + AI agent diff analysis
- **Trigger:** code review in the PR
- **Metric:** each commit must have a single Conventional Commits type and affect a coherent scope

## References

- [Guardia CONTRIBUTING](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `lex-conventional-commits` — Mandatory commit format
- `codex-commit-standards` — Complete guide on commit standards
- `kata-commit` — Procedure for creating compliant commits
