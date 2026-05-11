# Codex: Annotated and Signed Tags

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Operation of Git tags in Guardia repositories — creation, signing, verification, and server-side validation

## Overview

This Codex is the operational manual for creating, signing, and verifying Git tags in Guardia repositories. It documents the commands, options, failure modes, and GPG configuration required to satisfy `lex-annotated-tags`. It is consulted by the Katas `kata-tag` and `kata-release-publish`, and by the Warrior `warrior-janus`.

## Context

- **Domain:** Git tag lifecycle (local creation, signing, push, remote validation)
- **Audience:** AI agents that create tags (`kata-tag`, `kata-release-publish`), human maintainers preparing releases
- **Update:** when the tag creation/validation flow changes, or when the `validate-tag.yml` Action evolves

## Content

### Principles

1. **Annotated before signed.** A lightweight tag (`git tag NAME`) has no object of its own in Git — it is only a pointer to a commit. With no object, there is no body to sign. That is why `git tag -s` implies `git tag -a`.
2. **Local signing, best-effort server-side verification.** The signature is generated on the contributor's machine with their GPG key. Verification on the GitHub runner depends on the public key being available to the runner — it frequently is not. The authoritative server-side block is the object type (annotated vs lightweight) plus the SemVer name; the signature is verified locally before push.
3. **No direct creation on the remote.** GitHub's UI/API that creates tags produces lightweight tags. For this reason, creating a tag through the UI/API is forbidden by `lex-annotated-tags`.

### GPG Configuration for Tags

To sign tags automatically whenever `git tag -a` is used:

```bash
git config --global tag.gpgSign true
git config --global user.signingkey <GPG-KEY-ID>
```

Verify configuration:

```bash
git config --get tag.gpgSign      # expected: true
git config --get user.signingkey  # expected: GPG key ID (16 or 40 hex characters)
```

Prerequisites: GPG key generated and published on GitHub (see `kata-setup-gpg-signing`).

### Creation Commands

| Form | Result | Conformance with Lex |
|------|--------|:--------------------:|
| `git tag -s v1.2.3 -m "Release 1.2.3"` | Annotated + signed tag (canonical) | ✅ |
| `git tag -a v1.2.3 -m "Release 1.2.3"` | Annotated tag without signature | ❌ (violates `lex-annotated-tags` rule 2) |
| `git tag v1.2.3` | Lightweight tag | ❌ (violates `lex-annotated-tags` rule 1) |
| `git tag -s v1.2.3 <sha>` | Annotated + signed tag pointing at a specific `<sha>` | ✅ |

When `tag.gpgSign true` is configured, `git tag -a` already produces a signed tag — `-s` becomes redundant but harmless. The Kata always passes `-s` explicitly for defense in depth.

### Local Verification

Before pushing:

```bash
git tag -v v1.2.3
```

Expected output (valid signature):

```
object <sha>
type commit
tag v1.2.3
tagger <Author> <email> <timestamp>

Release 1.2.3
gpg: Signature made <date>
gpg: Good signature from "<Author> <email>"
```

Lightweight tag output (`git tag -v` fails):

```
error: <tag>: cannot verify a non-tag object of type commit.
```

Annotated tag without signature output:

```
object <sha>
type commit
tag v1.2.3
...
error: no signature found
```

### Push

```bash
git push origin v1.2.3
```

The pushed tag triggers `validate-tag.yml` on GitHub. To delete a local tag that has not yet been pushed: `git tag -d v1.2.3`.

### Server-side Validation (`validate-tag.yml`)

The workflow validates every tag pushed to `origin`:

1. **Object type** — `git cat-file -t $TAG`:
   - Annotated → returns `tag` → proceed
   - Lightweight → returns `commit` → **fails + deletes the remote tag**
2. **SemVer format** — regex `^v?[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$`. A tag outside the pattern → **fails + deletes**.
3. **GPG signature** — `git tag -v $TAG` on a best-effort basis:
   - Good signature → log `✓ GPG signature verified`
   - Public key missing on the runner → log `WARNING` (does not fail — the signature is validated locally)
   - No signature → log `WARNING` (signing is a local rule; see Principle 2)

### Delete Invalid Remote Tag

When the Action detects an invalid tag (lightweight or invalid name), it deletes the remote reference before failing. Command:

```bash
gh api -X DELETE repos/:owner/:repo/git/refs/tags/$TAG
```

The `repos/:owner/:repo/git/` prefix is **mandatory** — without it the call returns HTTP 404. In GitHub Actions, `${{ github.repository }}` replaces `:owner/:repo`.

### Failure Modes and Remediation

| Symptom | Cause | Remediation |
|---------|-------|-------------|
| `validate-tag.yml` Action fails with `Lightweight tag rejected` | The tag was created with `git tag NAME` | Delete locally (`git tag -d`), recreate with `git tag -s NAME -m`, push |
| `git tag -v` fails with `no signature found` | `tag.gpgSign` is not `true`; GPG key not configured | Configure `tag.gpgSign` + `user.signingkey` (see above); recreate the tag |
| Push accepted but the Release does not appear | `validate-tag.yml` rejected; the tag was deleted from the remote | Check the Action log; recreate the tag respecting all 3 rules |
| `gh api -X DELETE refs/tags/$TAG` returns 404 | Incomplete path (missing `repos/:owner/:repo/git/`) | Use the full path |
| `git tag -v` on the runner emits `WARNING` about a missing key | The signer's public key is not on the runner; the signature was validated locally | Accept — runner-side verification is best-effort by design |

### Operational Examples

**Canonical flow — minor release:**

```bash
# 1. Confirm trunk HEAD and green CI
git fetch origin
git checkout main && git pull
gh run list --commit "$(git rev-parse HEAD)" --limit 5 --json status,conclusion

# 2. Create annotated + signed tag
git tag -s v1.3.0 -m "Release v1.3.0: warrior-janus orchestrator"

# 3. Validate locally before push
git tag -v v1.3.0

# 4. Push
git push origin v1.3.0

# 5. Wait for validate-tag.yml + the release workflow
gh run watch "$(gh run list --workflow validate-tag.yml --commit $(git rev-parse v1.3.0) \
                 --limit 1 --json databaseId --jq '.[0].databaseId')"
```

**Pointing at a specific commit (not HEAD):**

```bash
git tag -s v1.3.0 -m "Release v1.3.0" abc123f
```

**Recovery after an invalid tag push:**

```bash
# Scenario: a lightweight tag reached the remote; the Action deleted it and failed
git tag -d v1.3.0                            # delete locally (was lightweight)
git tag -s v1.3.0 -m "Release v1.3.0"        # recreate correctly
git tag -v v1.3.0                            # confirm local signature
git push origin v1.3.0                       # push again
```

### Technical Constraints

- The tag **MUST** be created locally — the GitHub UI/API do not natively support annotated + signed tags.
- `tag.gpgSign true` in Git **MUST** be configured in the agent/contributor environment before the first release.
- The `validate-tag.yml` Action **MUST** be present in every Guardia repository that adopts Ahrena — otherwise the rule is client-side only and can be bypassed.

## References

- `lex-annotated-tags` — Law that this Codex operationalizes
- `lex-semantic-version` — Tag name format
- `lex-signed-commits` — Same GPG-signing root applied to commits
- `codex-semantic-version` — SemVer manual (companion to this Codex)
- `kata-tag` — Skill that applies this manual to create a tag
- `kata-release-publish` — Skill that pushes the tag and awaits validation
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
- [`git tag -v` reference](https://git-scm.com/docs/git-tag#Documentation/git-tag.txt--v)
