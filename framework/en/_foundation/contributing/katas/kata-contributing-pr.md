# Kata: Contribute via Pull Request

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Create Pull Request in the origin repository via GitHub MCP or gh CLI

## Objective

This Kata defines the standardized procedure for opening a Pull Request in the project's origin repository using the template at `.ahrena/contributing_templates/pull_request_template.md` (or `.github/pull_request_template.md`). The agent mirrors labels from the associated issue, self-assigns the PR, and ensures every contribution follows the unified flow defined in `codex-contributing`. It aligns with the existing `kata-contribute`.

## When to Use

- When changes are ready for submission to the repository
- When the user requests to create a PR
- When invoked by cry-new-pr or by cry-contribute with pr action

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Committed changes | Yes | Commits ready on the local branch (already validated by `kata-commit`) |
| Title | No | PR title in Conventional Commits format. If omitted, the agent infers from the commits |
| Related issue | No | Issue number that the PR resolves. If omitted, the agent asks |

## Workflow

```
Progress:
- [ ] 1. Analyze changes
- [ ] 2. Prepare branch
- [ ] 3. Push to remote
- [ ] 4. Compose PR (template in .ahrena/contributing_templates/)
- [ ] 5. Create PR via GitHub MCP (or gh)
- [ ] 6. Apply labels and assignee
- [ ] 7. Stamp cost (optional, per `.directives`)
- [ ] 8. Final verification
```

### Step 1: Analyze changes

1. Run `git status` to verify the repository state.
2. Run `git log main..HEAD --oneline` to list commits to be included.
3. Verify that all commits follow the Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`).
4. If there are uncommitted changes, invoke `kata-commit` first.

### Step 2: Prepare branch

1. Verify the current branch name: `git branch --show-current`.
2. The branch MUST follow the format `{type}/{issue-number}-{slug}` per `lex-git-branches`. If it does not, rename it before proceeding.
3. Confirm the associated issue exists and is complete per `lex-issue-quality`.

### Step 3: Push to remote

1. Push the branch:
   ```bash
   git push -u origin $(git branch --show-current)
   ```
2. If push fails (branch does not exist on remote), `git push` creates it automatically.

### Step 4: Compose PR (template)

1. Extract `owner` and `repo` from the remote URL (e.g., `git remote get-url origin`).
2. Compose the title in Conventional Commits (English): single commit → commit subject; multiple commits → a title summarizing the change set.
3. **Template:** Read `.ahrena/contributing_templates/pull_request_template.md`; if it does not exist, use `.github/pull_request_template.md`.
4. Fill the body: Description, Type of Change, Prerequisites, How Has This Been Tested, Checklist, Related Issues (`Closes #N` or `Refs #N`); Breaking Changes, Security, Performance when applicable.

### Step 5: Create PR via GitHub MCP (or gh)

**Preferred:** Use GitHub MCP tool `pull_request_create` (or `issue_write` with method `create_pr`) with: `owner`; `repo`; `title`; `source_branch`; `target_branch`: `main`; `body`; `assignees`: `["@me"]`; `is_draft` as needed.

**Fallback (gh CLI):**
```bash
gh pr create \
  --title "..." \
  --base main \
  --body "..." \
  --assignee "@me"
```

Record the PR number returned — needed for Step 6.

### Step 6: Apply labels and assignee

Size labels are applied **automatically** by GitHub Actions — do not apply them manually.

Apply labels manually:

1. **Get labels from the associated issue:**
   ```bash
   gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO \
     --json labels --jq '[.labels[].name] | join(",")'
   ```
2. **Mirror each label to the PR:**
   ```bash
   gh pr edit $PR_NUMBER --repo $OWNER/$REPO \
     --add-label "label1" --add-label "label2"
   ```
3. **Apply additional PR-specific labels when applicable** (see `codex-labels`):
   - `breaking change 💥` — if any commit introduces an incompatible API change
   - `security 🛡️` — if the PR resolves a security issue

### Step 7: Stamp cost (optional)

Optional step, gated by `pr_cost_tracking.enabled: true` in `.ahrena/.directives`. Non-blocking: stamp failure does not block the PR.

1. Consult `.ahrena/.directives`. If `pr_cost_tracking.enabled` is absent or `false`, skip this step.
2. Invoke `kata-pr-cost-stamp` with `$PR_NUMBER` recorded in Step 5.
3. If the stamp fails (network, tool unavailable, parsing), log a warning and proceed to Step 8.

### Step 8: Final verification

- [ ] The PR was created successfully
- [ ] The title follows Conventional Commits in English
- [ ] The body is filled with the repository template
- [ ] The issue is referenced with `Closes #N` or `Refs #N`
- [ ] All labels from the issue are mirrored on the PR
- [ ] PR-specific labels applied when applicable (`breaking change 💥`, `security 🛡️`)
- [ ] The PR is self-assigned (`@me`)
- [ ] All commits are signed (GPG verified)
- [ ] The source branch follows `lex-git-branches` format
- [ ] Cost stamp executed successfully or skipped per `pr_cost_tracking.enabled` in `.directives` (Step 7)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Pull Request | GitHub PR | Origin repository |
| PR URL | Link | Presented to the user |

## Constraints

- Do not create a PR unless commits comply with the 4 commit Lexis.
- Do not create a PR directly on `main` (always use a branch following `lex-git-branches`).
- Do not apply `size/*` labels manually — they are auto-applied by GitHub Actions.
- If there is no template in `.ahrena/` or `.github/`, use the default format (Description + Related Issues).
- Always self-assign the PR (`--assignee "@me"`) unless the user explicitly specifies a different assignee.

## References

- `codex-contributing` — Guardia contribution flow
- `codex-labels` — Full label taxonomy: mirroring rules, size thresholds, PR-specific labels
- `lex-issue-quality` — Issue quality requirements (template, labels, Why/What/How)
- `lex-git-branches` — Branch naming: `{type}/{issue-number}-{slug}`
- `codex-commit-standards` — Commit message standards
- `kata-commit` — Procedure for making compliant commits
- `kata-contribute` — Canonical PR procedure (this kata aligns with or reuses it)
- `kata-pr-cost-stamp` — Optional step that stamps token cost (Claude Code) on the PR
- `codex-pr-cost-tracking` — Reference manual for the cost stamp
- cry-new-pr, cry-contribute — Shortcuts that invoke this Kata
- `.ahrena/contributing_templates/pull_request_template.md` — PR template (canonical source after install)
