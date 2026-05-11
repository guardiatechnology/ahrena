# Kata: Publish Release (Annotated Tag + GitHub Release)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 2 of the release cycle orchestrated by `warrior-janus` — annotated/signed tag creation, push to the remote, wait/edit the release via GitHub Action, and post-condition verification

## Objective

This Kata defines the procedure that **actually publishes** the release after the human approval obtained in `kata-release-prepare`. The Kata creates the annotated and signed tag (via `kata-tag`), pushes it to the remote, **detects whether there is a `release.yml`-style workflow that creates the GitHub Release automatically** and acts accordingly: it either waits for the auto-generated Release or, in repositories without such a workflow, creates the Release via `gh release create`. It verifies that `validate-tag.yml` approved the tag.

## When to Use

- When `warrior-janus` has received explicit human approval after `kata-release-prepare`
- Never directly without the preparation step — the Kata assumes the version and changelog were agreed upon

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Next version | Yes | Approved SemVer string (e.g., `v1.3.0`) — coming from `kata-release-prepare` |
| Changelog path | Yes | `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` approved by the human |
| Target commit | No | Specific SHA for the tag (default: trunk HEAD at the time of approval) |

## Preconditions (blocking)

- [ ] `kata-release-prepare` ran and the human responded **"yes"** explicitly
- [ ] The version complies with `lex-semantic-version`
- [ ] GPG configured (`lex-signed-commits` / `lex-annotated-tags`)
- [ ] `.github/workflows/validate-tag.yml` exists in the target repository
- [ ] Trunk branch has green CI on the target commit (revalidate — the window may have opened between prepare and publish)

If any precondition fails: **abort**, record the reason, return control to the human.

## Workflow

```
Progress:
- [ ] 1. Revalidate preconditions
- [ ] 2. Detect release workflow in the target repository
- [ ] 3. Create annotated and signed tag (via kata-tag)
- [ ] 4. Push the tag to the remote
- [ ] 5. Wait for validate-tag.yml to complete successfully
- [ ] 6. Handle the GitHub Release cycle (workflow or fallback)
- [ ] 7. Verify post-conditions and report
```

### Step 1: Revalidate Preconditions

Re-run the checks listed under "Preconditions" (do not trust state from minutes ago). If any item fails, abort and return control to the human.

### Step 2: Detect Release Workflow

This step is **critical** — its absence caused a bug in v0.11.0 (race condition between `gh release create` and an automatic workflow).

```bash
RELEASE_WORKFLOW=""
for wf in .github/workflows/*release*.yml .github/workflows/*release*.yaml; do
  [ -f "$wf" ] || continue
  # Detects workflows that trigger on tag push (release-creating)
  if grep -qE '^\s*tags:\s*\[' "$wf" || grep -qE '^\s*-\s*"?v\*"?\s*$' "$wf"; then
    RELEASE_WORKFLOW="$wf"
    break
  fi
done
```

Record in the log:
- `RELEASE_WORKFLOW="<path>"` → "workflow-driven" path
- `RELEASE_WORKFLOW=""` → "fallback" path (`gh release create`)

### Step 3: Create Annotated and Signed Tag

Invoke `kata-tag` passing:
- Approved version (e.g., `v1.3.0`)
- Tag message: first line of the changelog (`# Release v1.3.0`) or the default `"Release v1.3.0"`
- Target commit (default HEAD; honor the human override if provided)

`kata-tag` returns the locally created tag. Validate with `git tag -v <version>` before proceeding.

### Step 4: Push the Tag to the Remote

```bash
git push origin "$NEXT_TAG"
```

Capture the exit code. If push fails (e.g., tag already exists on the remote), abort with a clear message — do not reuse the tag.

From this point onward, the tag is visible on GitHub and reactive workflows may trigger.

### Step 5: Wait for validate-tag.yml

The `validate-tag.yml` Action (introduced by `lex-annotated-tags`) verifies that the tag is annotated + signed + SemVer-valid. **Wait for its completion**:

```bash
RUN_ID=$(gh run list \
  --workflow validate-tag.yml \
  --commit "$(git rev-parse "$NEXT_TAG")" \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')

gh run watch "$RUN_ID" --exit-status
```

If `validate-tag.yml` fails: the remote tag is deleted by the Action itself; report to the human and exit with failure. Remediation is to recreate the local tag (likely a signature issue) and try to publish again.

### Step 6: Handle the GitHub Release Cycle

**Path A — workflow-driven (`RELEASE_WORKFLOW != ""`):**

1. Wait for the release workflow to complete:
   ```bash
   REL_RUN_ID=$(gh run list \
     --workflow "$(basename "$RELEASE_WORKFLOW")" \
     --commit "$(git rev-parse "$NEXT_TAG")" \
     --limit 1 \
     --json databaseId \
     --jq '.[0].databaseId')

   gh run watch "$REL_RUN_ID" --exit-status
   ```
2. Verify the Release exists: `gh release view "$NEXT_TAG"`.
3. Compare the auto-generated notes to the changelog from `kata-release-prepare`:
   - If the draft is **substantially more informative** (grouping by type, closed issues, highlighted breaking changes): overwrite with `gh release edit`.
   - Otherwise: **preserve the auto-generated Release** (default path).
4. Record in the Kata log which path was followed — auditable.

```bash
# Optional overwrite, only when the draft is more informative
gh release edit "$NEXT_TAG" --notes-file "$CHANGELOG_PATH"
```

**Path B — fallback (`RELEASE_WORKFLOW == ""`):**

```bash
gh release create "$NEXT_TAG" \
  --title "Release $NEXT_TAG" \
  --notes-file "$CHANGELOG_PATH"
```

### Step 7: Verify Post-conditions and Report

- [ ] Local tag exists and `git tag -v <version>` verifies the signature
- [ ] Remote tag exists (`gh api repos/$OWNER/$REPO/git/refs/tags/<version>`)
- [ ] `validate-tag.yml` completed successfully
- [ ] The GitHub Release exists and is reachable
- [ ] Changelog (draft) path moved to `.ahrena/workflow/release/changelog-<version>.published.md` (simple rename)
- [ ] Final report to the human: Release URL, path followed (workflow-driven / fallback), changelog size (auto vs custom)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Published tag | Annotated + signed Git tag | Remote (`origin`) |
| GitHub Release | HTTPS URL | Presented to the human and recorded in the log |
| Published changelog | Markdown | `.ahrena/workflow/release/changelog-<version>.published.md` |
| Path followed | `workflow-driven` or `fallback` | Kata log (auditing) |

## Restrictions

- **NEVER invoke `gh release create`** when the target repository has a workflow of the form `on: push: tags: ['v*']` that already creates the Release — the race condition causes HTTP 422 (confirmed in v0.11.0, PR #68).
- **NEVER skip the `validate-tag.yml` wait** — without it, invalid releases can be visible to consumers for seconds before the Action deletes the tag.
- **NEVER overwrite silently** auto-generated notes — require the "substantially more informative draft" criterion and record the decision.
- **NEVER re-push** after a `validate-tag.yml` failure on the same SHA without fixing the root cause (likely an invalid signature).
- **NEVER invoke this Kata** without an explicit human approval recorded by `kata-release-prepare` — Janus is an orchestrator, not an autonomous executor.

## Anti-pattern (lesson learned — v0.11.0)

```bash
# ❌ INCORRECT — causes HTTP 422 when the workflow creates the Release first
git push origin v1.2.3
gh release create v1.2.3 --notes-file ./changelog.md
# → pushed tag triggers release.yml, which creates the Release
# → 5 seconds later, gh release create attempts to create again and fails with:
#    "tag_name was used by an immutable release"
```

```bash
# ✅ CORRECT — detects workflow, waits, edits only when necessary
git push origin v1.2.3
gh run watch "$(gh run list --workflow release.yml --commit "$(git rev-parse v1.2.3)" \
                 --limit 1 --json databaseId --jq '.[0].databaseId')"
# Workflow completed; the Release was created automatically.
# Only edit the notes if the prepared changelog is substantially more informative.
gh release edit v1.2.3 --notes-file ./changelog.md
```

## References

- `lex-annotated-tags` — every tag MUST be annotated + signed
- `lex-semantic-version` — version format
- `lex-signed-commits` — GPG configuration
- `kata-tag` — creates the tag locally
- `kata-release-prepare` — preceding Kata; provides the approved version + changelog
- `warrior-janus` — Warrior orchestrating prepare + human gate + publish
- `cry-release` — cry that invokes `warrior-janus`
- History: v0.11.0 (PR #68) — race condition that motivated workflow detection
