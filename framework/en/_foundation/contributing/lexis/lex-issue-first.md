# Lexis: Issue-First Development

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All code changes in Guardia repositories

## Law

> **Every code change — feature, bugfix, refactoring, dependency update, or configuration change — MUST originate from an existing GitHub Issue. Before opening a new Issue, the contributor MUST verify whether one already exists (open or recently closed) covering the topic; the first matching Issue owns the work, and parallel Issues for the same scope are FORBIDDEN. No branch MAY be created and no PR MAY be opened without an associated Issue. The PR body MUST reference the Issue with `Closes #N` (fully resolves it) or `Refs #N` (partially addresses it). PRs without an Issue reference are FORBIDDEN. The only exception is trivial corrections (typos, punctuation, or formatting with no logic change), which MAY be submitted without a prior Issue using the `docs:` or `style:` Conventional Commits type.**

## Coverage

- **Applies to:** all code contributions in all Guardia repositories.
- **Bound agents:** developers, AI agents (warrior-athena, warrior-apollo, warrior-hephaestus).
- **Exceptions:** trivial corrections (`docs:` or `style:` type only, zero logic change). All other exceptions require explicit justification recorded in the Issue.

## Rules

### 1. Issue before branch

Before creating a branch:

1. **Search existing Issues** (open and recently closed) for one already covering the planned work — by title, label, scope, or related discussion. Use `gh issue list --search "<terms>"` or the GitHub UI search. The first matching Issue owns the work.
2. **If a matching Issue exists** for the topic: use it as the anchor — reference it via `Closes #N` (full resolution) or `Refs #N` (partial). Do not open a parallel Issue covering the same scope. Valid cases for a new Issue even when a related topic exists: (a) the current work is genuinely independent of the existing Issue, (b) the scope evolved and warrants a documented split recorded in the original Issue's comments.
3. **If no Issue exists**: open one using `kata-contributing-issue` with: **what** (clear description of the goal), **why** (motivation and impact), **expected outcome** (acceptance criteria or definition of done).
4. Only then create the branch following `lex-git-branches`: `{type}/{issue-number}-{slug}`.

### 2. Issue quality

An Issue MUST contain at minimum:

- A clear title summarizing the goal.
- A body describing the problem or objective, context, and expected outcome.
- A type assigned via the template in `.ahrena/contributing_templates/` (`feature-request`, `epic`, `user-story-for-api`, `user-story-for-frontend`, `tech-task`, `bug`, or `plan`).

### 3. PR references the Issue

Every PR body MUST include one of:

- `Closes #N` — the PR fully resolves the Issue (GitHub auto-closes it on merge).
- `Refs #N` — the PR partially addresses the Issue (Issue remains open).

PRs without an Issue reference are rejected during review.

**Plan sub-issues (`lex-agent-planning`):** a PR MAY use `Closes #M` where `#M` is a Plan sub-issue under a parent Issue `#N`. The `Closes #M` closes only the Plan sub-issue; the parent Issue `#N` closes only when ALL its Plan sub-issues reach `status: done`. When the PR partially contributes to the Plan or contextualizes the work in the parent Issue, use `Refs #M` or `Refs #N` respectively — never `Closes` on both simultaneously.

### 4. Exception: trivial corrections

Changes limited exclusively to typos, punctuation, or formatting (no behavior or logic change) MAY be submitted directly as a PR without a prior Issue. These MUST use the `docs:` or `style:` Conventional Commits type.

## Examples

### Correct

```
# Issue #42 exists: "Add OAuth2 authentication"
Branch: feat/42-oauth2-authentication
PR body includes: "Closes #42"
```

```
# Issue #123 exists: "Null pointer in transaction processing"
Branch: fix/123-null-pointer-in-transaction
PR body includes: "Closes #123"
```

```
# Trivial fix — no Issue required
Commit: docs: fix typo in CONTRIBUTING guide
```

### Incorrect

```
# ❌ Branch created without an Issue
Branch: feat/new-payment-dashboard
# No corresponding Issue exists

# ❌ PR body missing Issue reference
PR body: "This PR adds the new payment feature."
# No "Closes #N" or "Refs #N"

# ❌ Non-trivial change submitted without an Issue
Commit: refactor: restructure entire auth module
# Refactoring is not a trivial correction
```

## Automated Validation

- **Tool:** PR template with required `Closes #` or `Refs #` field; GitHub Actions check on PR body for Issue reference.
- **When:** on PR creation and update.
- **Metric:** 0 merged PRs (excluding trivial exceptions) without an associated Issue.
