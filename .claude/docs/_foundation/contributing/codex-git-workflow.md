# Codex: Git Workflow

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Complete git contribution workflow — Issue → Branch → Commits → PR → Merge

## Purpose

This Codex describes the canonical git workflow for all Guardia repositories. It connects the individual Lexis into a single end-to-end reference so developers and agents can follow the complete contribution cycle without consulting each artifact separately.

## Workflow Overview

```
Issue → Branch → Commits → PR → Review → Merge
```

Every step is governed by at least one Lexis. Skipping a step violates the workflow.

## Step 1 — Issue (`lex-issue-first`)

**Rule:** No branch without an Issue.

1. Check whether an Issue already exists for the planned work.
2. If not: open one using `kata-contributing-issue` (or the corresponding cry: `cry-new-feature-request`, `cry-new-epic`, etc.).
3. The Issue MUST describe: **what** (goal), **why** (motivation and impact), **expected outcome** (acceptance criteria).
4. Note the Issue number — it is required for the branch name.

**Available templates (`.ahrena/contributing_templates/`):**

| Type | Template |
|------|----------|
| Feature request | `feature-request.md` |
| Epic | `epic.md` |
| User story (API) | `user-story-for-api.md` |
| User story (frontend) | `user-story-for-frontend.md` |

## Step 2 — Branch (`lex-git-branches`)

**Format:** `{type}/{issue-number}-{slug}`

```bash
git checkout main
git pull origin main
git checkout -b feat/42-oauth2-authentication
```

**Valid types:** `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test`

| Example | Type |
|---------|------|
| `feat/42-oauth2-authentication` | New feature |
| `fix/123-null-pointer-in-transaction` | Bug fix |
| `chore/89-update-rust-dependencies` | Maintenance |
| `docs/201-contributing-guide-revision` | Documentation |
| `refactor/77-extract-payment-service` | Refactoring |

## Step 3 — Commits

Four Lexis govern every commit:

| Lexis | Rule |
|-------|------|
| `lex-conventional-commits` | Format: `{type}[scope]: {description}` |
| `lex-signed-commits` | Every commit MUST be GPG-signed (`-S` flag or `commit.gpgsign true`) |
| `lex-small-commits` | One logical change per commit (atomic) |
| `lex-commit-language` | Subject in English; body MAY use `[lang]` tag |

### Commit format

```
{type}[optional scope]: {description in English}

[optional body — use [lang] tag for local language]

[optional footer: Closes #N, BREAKING CHANGE: ...]
```

### Examples

```bash
# ✅ Correct: atomic, signed, conventional, English subject
git commit -S -m "feat(auth): add OAuth2 client configuration"
git commit -S -m "test(auth): add unit tests for OAuth2 flow"

# ❌ Incorrect: mixed concerns, unsigned
git commit -m "add OAuth2, fix header bug, update README"
```

### Auto-sign setup

See `kata-setup-gpg-signing` to configure automatic GPG signing. Once configured:

```bash
# git automatically signs — no -S needed
git commit -m "feat(auth): implement token refresh"
```

## Step 4 — Pull Request (`lex-issue-first`)

1. Push the branch:
   ```bash
   git push -u origin feat/42-oauth2-authentication
   ```
2. Open the PR using `kata-contributing-pr` or `gh pr create`.
3. PR title: Conventional Commits format in English.
4. PR body MUST include `Closes #N` or `Refs #N`.

### PR body structure

```markdown
## Description
{summary of the change}

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Related Issues
Closes #42

## How Has This Been Tested?
{describe local tests or automated checks}

## Checklist
- [ ] Commits are signed (GPG Verified)
- [ ] Existing tests pass
- [ ] New tests added for new behavior
- [ ] No out-of-scope changes
```

## Step 5 — Review and Merge

Merge requirements:

- Minimum 1 approval from a maintainer (per CODEOWNERS).
- All CI checks pass.
- All commits show **Verified** (GPG signed).
- No merge conflicts with `main`.
- PR references an Issue.

After merge: `main` is updated; the branch is deleted.

## Releases (`lex-semantic-version`)

Releases follow Semantic Versioning (`MAJOR.MINOR.PATCH`). Tags MUST be signed:

```bash
git tag -s v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

Breaking changes increment `MAJOR`. New features increment `MINOR`. Fixes increment `PATCH`.
