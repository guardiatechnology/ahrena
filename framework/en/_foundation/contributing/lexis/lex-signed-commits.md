# Lexis: Mandatory Signed Commits

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All commits in Guardia repositories

## Purpose

GPG-signed commits guarantee the authenticity and integrity of every change, allowing reviewers and the community to trust the origin of the code. Without a signature, there is no way to cryptographically verify who made the change.

This Lexis ensures that every commit is signed and verifiable, as required by Guardia's CONTRIBUTING guidelines.

## Law

> **Every commit MUST be signed with a GPG key and marked as "Verified" by GitHub.**

## Rules

### 1. Mandatory signature

Every commit pushed to Guardia repositories MUST contain a valid GPG signature that GitHub can verify.

### 2. Accepted status

| Status | Accepted | Description |
|--------|:--------:|-------------|
| Verified | Yes | Signed commit, verified signature, committer is the author |
| Partially verified | No | Signed commit but author differs from committer with vigilant mode |
| Unverified | No | Signature could not be verified |
| No status | No | Unsigned commit |

### 3. Recommended configuration

Configure Git to sign commits automatically:

```
git config --global commit.gpgsign true
git config --global user.signingkey <GPG-KEY-ID>
```

### 4. Tags

Release tags MUST also be signed with GPG.

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
