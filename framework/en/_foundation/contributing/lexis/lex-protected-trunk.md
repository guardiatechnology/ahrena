# Lexis: Trunk Branches Are Protected Against Direct Writes

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Trunk branches (`main`, `master`, `release/*`) in every Guardia repository

## Purpose

Allowing direct commits to `main`/`master`/`release/*` collapses the entire contributing flow: the issue stops being required in practice, the convention-named branch (`lex-git-branches`) becomes optional, PR review never happens, the CI gate cannot block broken code, and the trunk history becomes a linear log without traceability. This Law closes the loop by making explicit the invariant the other contributing Lexis assume implicitly: the trunk receives code exclusively through merged PRs originating from a properly named branch, with all required checks satisfied.

## Law

> **Trunk branches (`main`, `master`, `release/*`) MUST be protected against direct writes. Every development MUST start on a branch created per `lex-git-branches` (`{type}/{N}-{slug}`) and code MUST reach the trunk exclusively through a merged Pull Request, with the associated issue referenced by `Closes #N` or `Refs #N` (`lex-issue-first`) and all required CI checks passing. Direct push, direct commit on the trunk's working copy, force-push, admin bypass, and web-UI edits on the trunk are FORBIDDEN.**

## Coverage

- **Applies to:** every Guardia repository, without exception. The branches `main`, `master`, and `release/*` are considered trunk in any repository where they exist.
- **Bound agents:** every contributor (human and AI) — including `warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-atlas`, repository maintainers and administrators.
- **Exceptions:** None. Lexis admit no exceptions. Emergency incident fixes follow the same flow (`fix/{N}-...` branch → PR with fast-track review and merge), never a direct commit.

## Violation Consequences

1. **Automatic block:** GitHub Branch Protection Rules configured on the repository reject direct push, force-push, web-UI edits, and merge without an approved PR on `main`, `master`, and `release/*`. Admin bypass is disabled in protection settings (`allow_force_pushes: false`, `enforce_admins: true`, `required_pull_request_reviews`, `required_status_checks`).
2. **Alert:** a rejected attempt generates an audit event; a `Lex-bypass` by an administrator (if the protection is loosened) triggers an alert to the repository owner and to Security.
3. **Remediation:** if a commit reached the trunk outside a PR (e.g., protection settings temporarily disabled), the remediation is (a) revert the commit via a revert PR, (b) restore the protection settings, (c) open a post-mortem recording how the bypass was possible.

## Examples

### Correct

```
# Issue #42 opened with template and labels (lex-issue-quality)
git checkout main
git pull
git checkout -b feat/42-oauth2-authentication
# ... implementation, atomic signed commits (lex-small-commits, lex-signed-commits) ...
git push -u origin feat/42-oauth2-authentication
gh pr create --base main --head feat/42-oauth2-authentication --title "feat(auth): add OAuth2 authentication" --body "Closes #42"
# Review approved, CI green, merge via UI/CLI; main advances exclusively through the PR's merge commit.
```

### Incorrect

```
# ❌ Direct commit on the main working copy
git checkout main
git commit -am "fix: small typo"
git push origin main
# Even with an associated issue, the trunk received writes outside a PR — VIOLATES THE LAW.

# ❌ Force push to main to "clean up history"
git push --force origin main

# ❌ Web-UI edit on a trunk file without opening a PR
# (GitHub allows this when protection is disabled — VIOLATES THE LAW)

# ❌ Admin bypass to merge a PR without required review
gh pr merge 19 --admin
```

## Automated Validation

- **Tool:**
  - GitHub Branch Protection Rules on `main`, `master`, `release/*`: `required_pull_request_reviews` (≥1 approval), `required_status_checks` (CI required), `allow_force_pushes: false`, `allow_deletions: false`, `enforce_admins: true`, `required_linear_history` optional, `required_conversation_resolution: true`.
  - GitHub Actions workflow auditing history: detects commits on trunk whose `parent count` ≠ 2 (non-merge) and whose SHA is not the tip of a merged PR, failing the pipeline and raising an alert.
  - `kata-quality-gate` (Phase 6 of the Issue-Driven flow) verifies the branch is not `main`/`master`/`release/*` before proceeding.
- **When:** repository setup configuration; continuous audit on every push to trunk; check at Gate 2.
- **Metric:** 0 non-merge commits on trunk outside an approved PR; 100% of Guardia repositories with Branch Protection Rules configured per spec; 0 admin-bypass incidents undocumented in post-mortem.
