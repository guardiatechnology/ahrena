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

## Author identity: human vs warriors-default

Ahrena projects choose how warrior-driven commits and PRs are attributed: as the human contributor (default) or as the fleet-default GitHub App `[bot]` identity (opt-in).

### Default mode — human author

When `warriors_default_author.enabled` is `false` (or the section is absent from `.ahrena/.directives`), warriors commit using the developer's git identity and GPG key, exactly as if a human typed the commands. `git log --pretty='%an <%ae>'` shows the developer; PRs appear under the developer's GitHub login. This is the historical behavior; upgrading the framework does not change it.

| Aspect | Default (human author) |
|--------|------------------------|
| Commit author | Developer's `user.name` / `user.email` |
| Commit signature | Developer's GPG key (per `lex-signed-commits`) |
| PR author on GitHub | Developer's GitHub login |
| `gh pr view` | `Author: <developer-login>` |
| Audit trail | Each contributor surfaces individually in commits and PRs |

### Opt-in mode — warriors default author

When `warriors_default_author.enabled` is `true`, the warriors listed in `warriors_default_author.apply_to` invoke `scripts/ahrena-auth.sh` before every `git commit` / `gh pr create`. The script exchanges the Ahrena GitHub App credentials for a short-lived installation token and exports the App's `[bot]` identity to the calling shell:

```
GH_TOKEN_AHRENA_WARRIORS_DEFAULT=<installation-token>
GIT_AUTHOR_NAME=ahrena-bot[bot]
GIT_AUTHOR_EMAIL=<numeric-user-id>+ahrena-bot[bot]@users.noreply.github.com
GIT_COMMITTER_NAME=ahrena-bot[bot]
GIT_COMMITTER_EMAIL=<same as author>
```

Commits produced under this identity are signed server-side by the App's installation token (no GPG key on the developer's machine needed for the warriors-default identity). When `warriors_default_author.commit_co_author` is `human`, the commit body carries `Co-authored-by: <human name> <human email>` so the individual driver of the work remains traceable.

| Aspect | Opt-in (warriors default author) |
|--------|----------------------------------|
| Commit author | `ahrena-bot[bot]` |
| Commit signature | Server-signed by the GitHub App installation token |
| PR author on GitHub | `ahrena-bot[bot]` |
| `gh pr view` | `Author: ahrena-bot[bot]` |
| Co-author trailer | `Co-authored-by: <human>` (when `commit_co_author=human`) |
| Audit trail | Agent vs human is answerable from the GitHub UI without parsing trailers |

### Trade-offs

- **Warriors default author** — clearer separation between human-driven and agent-driven contributions, simpler audit trail at the identity layer, no GPG on the developer's machine for agent commits, and a clean signal for cost-tracking and PR-review tooling that already recognizes `[bot]` identities. Requires registering the fleet-default GitHub App and provisioning the credentials.
- **Human author** — preserves per-contributor recognition in `git log`, keeps the existing GPG flow, and removes one moving piece for solo developers or projects where the human is the only sender. No additional GitHub App registration required.

### Per-warrior opt-out

`warriors_default_author.apply_to` is a list of warrior names. Only the warriors in that list call the auth resolver; warriors omitted from the list keep human-author behavior even when the master switch is on. This allows partial adoption (for example, warriors-default identity for `apollo` and `hephaestus` while `iris` keeps the developer's identity).

### Out-of-band commits

A direct human-typed commit (no warrior involvement) keeps the developer's identity regardless of the directive — the auth resolver only fires when a warrior wraps the commit. The directive governs warrior attribution, not raw `git commit` invocations. Warriors that own their own GitHub App (e.g., Argos consumes `AHRENA_WARRIOR_ARGOS_GH_*`) do not depend on this default identity — they answer to their specific App.

### Credential storage

The GitHub App credentials follow the same storage convention as `scripts/argos/auth.sh`. The auth resolver consults each source in order and accepts any subset of values per source — APP_ID can come from env while the private key comes from the Keychain, etc.

| Source | Used when |
|--------|-----------|
| Environment variables (`AHRENA_WARRIORS_DEFAULT_GH_APP_ID`, `AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID`, `AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH`) | CI / non-interactive environments |
| `.env.local` at the repository root | Local development on Linux/Windows |
| macOS Keychain (three `security` entries listed below) | Local development on macOS — keys never live on disk |

#### macOS Keychain setup

On macOS, store each credential as a separate `security` entry. The auth resolver fills any variable still missing after `.env.local` + env have been loaded:

```bash
security add-generic-password -s ahrena-warriors-default-gh-app-id -a "$USER" -w "<APP_ID>"
security add-generic-password -s ahrena-warriors-default-gh-installation-id -a "$USER" -w "<INSTALLATION_ID>"
security add-generic-password -s ahrena-warriors-default-gh-private-key -a "$USER" -w "$(cat /path/to/key.pem)"
```

The `ahrena-warriors-default-gh-private-key` entry stores the PEM content verbatim — the auth resolver materializes it into a chmod-600 tempfile at signing time and removes the tempfile via the `_ahrena_auth_cleanup` trap on every exit path. The private key never persists on disk under the operator's `$HOME`.

On Linux / Windows / non-macOS hosts, the `security` CLI is absent; the Keychain block short-circuits via `command -v security` and the resolver falls back to env / `.env.local` without error.

Credentials are NEVER committed to the repository; the auth resolver materializes them only into the calling shell's environment, never to stdout or to logs.

## Releases (`lex-semantic-version`)

Releases follow Semantic Versioning (`MAJOR.MINOR.PATCH`). Tags MUST be signed:

```bash
git tag -s v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

Breaking changes increment `MAJOR`. New features increment `MINOR`. Fixes increment `PATCH`.

## References

| Artifact | Purpose |
|----------|---------|
| `lex-issue-first` | Every change must originate from an Issue |
| `lex-git-branches` | Branch naming: `{type}/{issue-number}-{slug}` |
| `lex-conventional-commits` | Commit message format |
| `lex-signed-commits` | GPG signing requirement |
| `lex-small-commits` | Atomic commits |
| `lex-commit-language` | Subject in English |
| `lex-semantic-version` | Release tagging |
| `kata-setup-gpg-signing` | Configure GPG signing |
| `kata-contributing-issue` | Open a GitHub Issue |
| `kata-contributing-pr` | Open a Pull Request |
| `codex-contributing` | Contribution process overview |
