# Kata: Prepare Release (Bump + Changelog)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 1 of the release cycle orchestrated by `warrior-janus` — commit analysis, SemVer bump proposal, changelog generation, and trunk-state verification

## Objective

This Kata defines the standardized procedure to analyze Conventional Commits since the last tag, propose the appropriate SemVer bump (major/minor/patch or "no release"), draft a changelog grouped by type, and verify that the trunk is in a suitable state to release. The Kata **finishes by presenting the proposal to the human**; publication happens in `kata-release-publish` only after explicit approval.

## When to Use

- When `warrior-janus` is invoked to start a release cycle
- When the user invokes `cry-release` (with or without `--dry-run` / `--type`)
- As an independent step to preview the version and changelog without publishing

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Bump override | No | `major`, `minor`, or `patch` to override the heuristic (via `cry-release --type`) |
| Dry-run mode | No | When active, generates the proposal but persists nothing (via `cry-release --dry-run`) |
| Base ref | No | Tag or ref to start from (default: latest SemVer tag on the remote) |

## Workflow

```
Progress:
- [ ] 1. Sync tags and identify the latest version
- [ ] 2. Collect commits since the latest tag
- [ ] 3. Classify Conventional Commits and propose bump
- [ ] 4. Generate changelog draft
- [ ] 5. Check trunk state
- [ ] 6. Present proposal to the human
```

### Step 1: Sync Tags and Identify the Latest Version

1. Run `git fetch --tags --prune-tags origin` to ensure an up-to-date view.
2. Identify the latest SemVer tag:
   ```bash
   LAST_TAG=$(git describe --tags --abbrev=0 --match 'v[0-9]*.[0-9]*.[0-9]*' 2>/dev/null || true)
   ```
   - If no tag exists, record **first-release** and treat it as `v0.0.0` for analysis purposes; the suggested initial bump is `v0.1.0` (minor) when there is a `feat:`, or `v1.0.0` if the team decides to mark GA (the human decides in Step 6).
3. Resolve the SHA matching the tag for use in `git log <SHA>..HEAD`.

### Step 2: Collect Commits Since the Latest Tag

1. Run:
   ```bash
   git log "${LAST_TAG:-$(git rev-list --max-parents=0 HEAD | tail -1)}"..HEAD \
     --no-merges \
     --pretty=format:'%H%x09%s%x09%b%x1e'
   ```
2. Split each commit into three fields: SHA, subject, body.
3. Discard commits whose subject does not start with a valid Conventional Commits prefix — record them separately under "commits without type" (to be listed to the human as potential noise).

### Step 3: Classify Conventional Commits and Propose Bump

Apply the table:

| Signal in the commit | Bump |
|----------------------|------|
| Body contains a line starting with `BREAKING CHANGE:` | **major** |
| Subject uses `<type>!:` or `<type>(<scope>)!:` | **major** |
| Subject starts with `feat:` or `feat(...):` | **minor** |
| Subject starts with `fix:`, `perf:`, or `revert:` | **patch** |
| Only `docs:`, `chore:`, `ci:`, `style:`, `test:`, `refactor:`, `build:` commits | **none** (no release) |

Combination rule: apply the **highest** bump among those found (major > minor > patch).

If a `--type` override is present, **use the override** but record the calculated heuristic in the proposal so the human can compare.

Compute the next version:
```
v1.2.3 + major → v2.0.0
v1.2.3 + minor → v1.3.0
v1.2.3 + patch → v1.2.4
v1.2.3 + none  → (no release; exit with a clear message)
```

### Step 4: Generate Changelog Draft

Group classified commits by type, in the order: `feat` → `fix` → `perf` → `refactor` → `docs` → `build` → `ci` → `chore` → `test` → `style` → `revert`. For each commit, format:

```
- <scope-if-any>: <subject without the prefix> (<short-sha>) by @<author>
```

Changelog structure:

```markdown
# Release vX.Y.Z

> **Date:** YYYY-MM-DD
> **Bump:** major | minor | patch (vAAA.BBB.CCC → vXXX.YYY.ZZZ)
> **Closed issues:** #N1, #N2, ...

## ⚠ Breaking Changes
- ...

## ✨ Features
- ...

## 🐛 Fixes
- ...

## ⚡ Performance
- ...

## 🔧 Other (refactor, docs, build, ci, chore, test, style)
- ...
```

List closed issues by extracting `Closes #N` or `Fixes #N` from commit bodies.

Persist the draft to `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (create the directory if necessary) — except in `--dry-run`, where the draft is presented only in memory.

### Step 5: Check Trunk State

1. Identify the trunk branch (default: `main`) and resolve the **target commit SHA** (`TARGET_SHA=$(git rev-parse HEAD)`).
2. Check CI status on the target commit (filter by SHA, not by branch — the branch may have advanced between the decision and the check):
   ```bash
   gh run list --commit "$TARGET_SHA" --limit 5 --json status,conclusion,workflowName
   ```
   - Failure (`conclusion: failure` on a required workflow) → **block the proposal**; report to the human.
   - In progress (`status: in_progress`) → **wait up to 5 minutes**; if still running, signal and let the human decide.
   - Success → proceed.
3. List open PRs in the repository (informative, non-blocking):
   ```bash
   gh pr list --state open --limit 20 --json number,title,labels
   ```
   - Present to the human with the notice: "These PRs will be excluded from the release; confirm whether that is intentional."

### Step 6: Present the Proposal to the Human

Structured output presenting:

1. **Current and next version:** `LAST_TAG` → `NEXT_TAG`
2. **Bump:** `minor` (heuristic) or `minor (override via --type)`
3. **Commit summary:** count per type (`feat: 3, fix: 5, ...`)
4. **Changelog draft path:** `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (or inline if dry-run)
5. **Trunk status:** ✅ CI green / ⚠ open PRs / ❌ CI broken
6. **Explicit question:** "Approve and publish this release? (yes / edit / cancel)"

The Kata **ends here**. Approval is the human's responsibility; publication is `kata-release-publish`'s responsibility. Without explicit "yes" input, `warrior-janus` does not invoke the next phase.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Proposed next version | SemVer string (e.g., `v1.3.0`) | Presented to the human + payload for `kata-release-publish` |
| Changelog draft | Markdown | `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (or stdout in dry-run) |
| Trunk diagnosis | Structured (status, counts) | Presented to the human |
| Untyped commit list | List of SHAs + subjects | Presented to the human (potential noise) |

## Restrictions

- **Never publish** — this Kata stops at the proposal. Publication is the exclusive privilege of `kata-release-publish` upon human approval.
- **Never infer the bump silently** — always show the applied heuristic and the commits that triggered each level.
- **Never confuse override and heuristic** — if the human used `--type major` but commits suggest `patch`, both MUST appear in the proposal to reduce the risk of human error.
- **Never skip the CI check** — a trunk with red CI does not deserve a release, except by documented human decision.
- **No release** (bump `none`) is NOT a Kata failure; it is a valid outcome. Exit with a clear message.

## References

- `lex-conventional-commits` — format of the analyzed commits
- `lex-semantic-version` — format of the proposed next version
- `lex-annotated-tags` — prerequisite for publication (consumed by the next Kata)
- `kata-release-publish` — next Kata; receives the approved version and changelog
- `warrior-janus` — Warrior orchestrating this Kata + human gate + `kata-release-publish`
- `cry-release` — cry that invokes `warrior-janus`
