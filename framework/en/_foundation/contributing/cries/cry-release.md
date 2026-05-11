# Cry: Publish Release

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to invoke `warrior-janus` and close the delivery cycle — commit analysis, SemVer bump proposal, human approval, and publication of annotated/signed tag + GitHub Release

## Invocation

```
/cry-release [--type major|minor|patch] [--dry-run]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `--type` | No | Overrides the SemVer bump heuristic computed from commits. Values: `major`, `minor`, `patch` | `--type minor` |
| `--dry-run` | No | Presents the proposal without persisting anything (no changelog draft file, no tag, no push) | `--dry-run` |

When `--type` is provided, `warrior-janus` displays **both the computed heuristic and the override** so the human can compare before approving. Without flags, Janus uses only the heuristic.

When `--dry-run` is provided, the command exits after presenting the proposal — no persistent write happens.

## Usage Examples

```
# Full flow: analysis + human gate + publication
/cry-release

# Bump override (the human knows it deserves major even without a BREAKING CHANGE)
/cry-release --type major

# Preview without side effects
/cry-release --dry-run

# Override + dry-run combined
/cry-release --type minor --dry-run
```

## Behavior

1. Invokes `warrior-janus`.
2. Janus runs `kata-release-prepare`:
   - `git fetch --tags`, identifies the latest SemVer tag
   - Collects and classifies commits since the latest tag (Conventional Commits)
   - Computes the heuristic bump; applies the override (`--type`) when present
   - Generates the changelog draft (to a file, except in `--dry-run`)
   - Checks trunk CI and lists open PRs
3. Janus presents the structured proposal and waits for **explicit human approval** ("yes" / "edit" / "cancel").
4. In `--dry-run`, exits after presenting the proposal.
5. After "yes", Janus runs `kata-release-publish`:
   - Creates an annotated + signed tag via `kata-tag`
   - Pushes to `origin`
   - Waits for `validate-tag.yml` (server-side, `lex-annotated-tags`)
   - Detects the release workflow in the target repo; waits for the auto-generated Release OR falls back to `gh release create`
   - Overwrites notes only if the draft is substantially more informative
6. Reports the Release URL, the path taken, and the final state.

## Associated Warrior

`warrior-janus` — orchestrates both Katas with an explicit human gate between them.

## References

- `warrior-janus` — Warrior invoked by this Cry
- `kata-release-prepare` — Phase 1 (analysis + proposal)
- `kata-release-publish` — Phase 2 (publication after approval)
- `lex-annotated-tags` — Law governing the validity of the pushed tag
- `lex-semantic-version`, `lex-signed-commits`, `lex-conventional-commits` — Lexis consulted throughout the flow
