# Lexis: Annotated and Signed Tags

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Git tags in Guardia repositories

## Law

> **Every tag pushed to a Guardia remote MUST be an annotated tag (not lightweight) signed with a GPG key. Pushing a lightweight tag to `origin` is FORBIDDEN. The tag MUST follow Semantic Versioning per `lex-semantic-version` and the signature MUST be verifiable locally before push per `lex-signed-commits`.**

## Coverage

- **Applies to:** every Git tag pushed to any Guardia remote (release, pre-release, internal). Local unpublished tags fall outside the rule's reach but become subject to it the moment they are pushed.
- **Bound agents:** every contributor (human and AI) — including `warrior-janus`, `warrior-athena`, and any Kata that creates a tag (`kata-tag`, `kata-release-publish`).
- **Exceptions:** None. Lexis admit no exceptions. Pre-existing lightweight tags in remote history remain (the rule is forward-looking) — there is no retroactive migration.

## Rules

### 1. Object type: annotated

Every pushed tag MUST be of type `tag` in Git (an object of its own, carrying author, date, message, and signature). Lightweight tags (a mere pointer to a commit, with no object of their own) do not satisfy this Lex.

### 2. Mandatory GPG signature

Every pushed tag MUST be signed with GPG. Lightweight tags are technically incapable of carrying a signature — only annotated tags support GPG. The signature MUST be verified locally before the push.

### 3. Semantic Versioning

The tag name MUST follow the format defined in `lex-semantic-version` (MAJOR.MINOR.PATCH, with optional pre-release and build metadata). Tags outside the SemVer format are rejected by the combined validation of the two Lexis.

### 4. Mandatory server-side validation

Every Guardia repository that adopts Ahrena MUST have the workflow `.github/workflows/validate-tag.yml` active. This workflow:

- Blocks lightweight tags (verifies the object type on the remote).
- Blocks tags outside the SemVer format.
- Verifies the GPG signature on a best-effort basis (does not fail when the public key is unavailable to the runner — the signature is an authoritative local rule).
- Deletes the invalid remote tag before exiting with failure, preventing reactive workflows from consuming an invalid tag.

### 5. No direct creation on the remote

Tag creation via GitHub UI/API (which produces a lightweight tag automatically) is FORBIDDEN. Tags MUST originate locally, be signed locally, and only then be pushed to the remote.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../../quality/lexis/lex-hard-gate-pattern.md), the textual block of this Lex is canonically expressed as:

```
<HARD-GATE>
warrior-janus, warrior-athena and any other agent (human or AI)
MUST NOT push a tag to a Guardia remote without it satisfying
ALL criteria:

  (a) The tag is of type `tag` in Git (annotated — not lightweight)
  (b) The tag is GPG-signed and the signature has been verified
      locally before push
  (c) The name follows Semantic Versioning (lex-semantic-version)
  (d) The target repository has `.github/workflows/validate-tag.yml` active

This rule applies to EVERY tag, regardless of:
  - declared purpose ("it's just a debug tag")
  - urgency ("I need to publish now")
  - release type (major, minor, patch, pre-release)
  - perceived change size

Single declared exception: None. Pre-existing lightweight tags in
history remain (forward-looking rule); no retroactive migration,
but no new lightweight tag may be pushed.

Note: server-side GPG signature verification is best-effort (it
depends on the public key being available to the runner). The
hard server-side block stays on (a) "annotated" + (c) "SemVer-
valid"; the signature is enforced locally before the push.
</HARD-GATE>
```

## Violation Consequences

1. **Automatic block:** the `validate-tag.yml` workflow deletes the remote tag and fails the run.
2. **Alert:** the push author receives the failed Action notification; the release that depended on the tag does not happen.
3. **Remediation:** recreate the tag locally as annotated + signed, validate locally, and push again.

## Automated Validation

- **Tool:** workflow `.github/workflows/validate-tag.yml` (server-side, authoritative) + local verification before push by the agent/contributor.
- **Timing:** when the tag is pushed to `origin` (server-side); before the push (client-side).
- **Metric:** 0 lightweight tags on `origin` after this Lex takes effect; 100% of tags with a locally verifiable GPG signature.

## References

- `lex-semantic-version` — MAJOR.MINOR.PATCH format for the tag name
- `lex-signed-commits` — GPG signing (same root applied to commits)
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
