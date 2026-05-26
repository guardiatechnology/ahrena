# Lexis: Mandatory Signed Commits

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All commits in Guardia repositories

## Purpose

Signed commits guarantee the authenticity and integrity of every change, allowing reviewers and the community to trust the origin of the code. Without a signature, there is no way to cryptographically verify who made the change.

This Lexis ensures that every commit is signed and verifiable, as required by Guardia's CONTRIBUTING guidelines.

## Law

> **Every commit MUST be signed (with a local GPG key OR by GitHub's server-side signing via an Ahrena warriors-default App installation token) and marked as "Verified" by GitHub.**

## Rules

### 1. Mandatory signature

Every commit pushed to Guardia repositories MUST contain a valid signature that GitHub can verify. The signature MAY come from a local GPG key held by the contributor OR from GitHub's server-side signing performed when an App installation token authors the commit via the Git Data API.

### 2. Accepted status

| Status | Accepted | Description |
|--------|:--------:|-------------|
| Verified | Yes | Signed commit, verified signature, committer is the author |
| Partially verified | No | Signed commit but author differs from committer with vigilant mode |
| Unverified | No | Signature could not be verified |
| No status | No | Unsigned commit |

### 3. Recommended configuration (local GPG path)

Configure Git to sign commits automatically:

```
git config --global commit.gpgsign true
git config --global user.signingkey <GPG-KEY-ID>
```

### 4. Tags

Release tags MUST also be signed with GPG (local key path; tags created by the App installation token follow the same server-side signing flow as commits).

### 5. Signing modalities

Two paths satisfy this Lex, both producing the "Verified" status on GitHub:

| Modality | When | How |
|----------|------|-----|
| **Local GPG signing** | Default for human-authored commits | The contributor configures `commit.gpgsign true` + a valid signing key (`lex-signed-commits` Rule 3). The signature is produced locally before the push. |
| **App-installation signing** | When `warriors_default_author.enabled: true` and the executing warrior is in `warriors_default_author.apply_to` | Warriors call `scripts/ahrena-auth.sh` + `scripts/ahrena-api-commit.sh`, which create the commit through the GitHub Git Data API with the App's installation token. GitHub signs the commit server-side; the "Verified" badge appears on the commit page and no local GPG key is involved. See `codex-git-workflow` ("Author identity"). |

Both modalities produce commits whose verification status MUST be "Verified". A commit that lacks either signature path (no local GPG and no API-commit path) violates this Lex.

## Scope

- **Applies to:** all Guardia repositories
- **Bound agents:** all
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Automatic block:** PR rejected — only PRs with all commits "Verified" are accepted
2. **Alert:** PR marked with insufficient verification status
3. **Remediation:** re-sign commits with `git commit --amend -S` or `git rebase --exec 'git commit --amend -S --no-edit'`

## Examples

### Correct

```
$ git log --show-signature -1
commit abc123...
gpg: Signature made Mon Mar 08 10:00:00 2026 UTC
gpg: Good signature from "Developer <dev@guardia.finance>"
```

### Incorrect

```
$ git log --show-signature -1
commit def456...
gpg: No signature found

# Unsigned commit — VIOLATES THE LAW
# PR will be automatically rejected
```

## Automated Validation

- **Tool:** GitHub branch protection rules (require signed commits)
- **Trigger:** when opening or updating a PR
- **Metric:** 100% of commits must have "Verified" status

## References

- [Signing commits — GitHub Docs](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
- [Signing commits — Guardia](https://hub.guardia.finance/docs/tutorials/signing-commits/)
- [Guardia CONTRIBUTING](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `codex-commit-standards` — Complete guide on commit standards
