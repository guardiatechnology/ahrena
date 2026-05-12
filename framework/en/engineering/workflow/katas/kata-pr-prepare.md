# Kata: Prepare Pull Request

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 7 of the Issue-Driven flow — creating a branch, pushing files, and opening a PR on GitHub via MCP, with a structured body referencing all flow artifacts

## Objective

After Gate 2 results in `go`, create the branch, push the modified files, and open a Pull Request on GitHub via MCP. The PR body is structured referencing the original issue, the numbered ACs, the created ADRs, and the flow artifacts in `docs/issues/issue-{n}/`. The result is a PR ready for human review, with full traceability.

## When to Use

- Phase 7 (final) of the flow orchestrated by `warrior-athena`, after `kata-quality-gate` results in `go`
- When a validated implementation must be submitted for review via PR

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Issue number | Yes | Number of the original issue (e.g., `42`) |
| Repository | Yes | `owner/repo` |
| Base branch | No | Target branch of the PR; default: `main` |
| Flow artifacts | Yes | `docs/issues/issue-{n}/*` and `docs/adr/ADR-*` created in previous phases |
| PR strategy | No | `draft` (default: `false`) |

## Workflow

```
Progress:
- [ ] 1. Verify MCP and Gate 2 preconditions
- [ ] 2. Determine branch name and PR title
- [ ] 3. Create branch via GitHub MCP
- [ ] 4. Push modified files
- [ ] 5. Compose PR body with references
- [ ] 6. Create PR linked to the issue
- [ ] 7. Update ADR status (proposed → accepted)
- [ ] 8. Update final checkpoint
```

### Step 1: Verify MCP and Gate 2 preconditions

1. Confirm that `github` is in `mcp.servers` (per `lex-mcp`). If not, report and end.
2. Confirm `GITHUB_PAT` is defined.
3. Read `docs/issues/issue-{n}/06-quality-report.md` and confirm the result is `go`. If `no-go`, refuse to create the PR and return to the orchestrator.
4. Consult `codex-mcp-github` to identify the correct tools (`create_branch`, `push_files`, `create_pull_request`).

### Step 2: Determine branch name and PR title

**Branch name** — convention:

```
{type}/issue-{n}-{short-slug}
```

Where:
- `{type}` — extract from the Phase 1 brief ("Work type" section): `feat`, `fix`, `refactor`, `chore`
- `{short-slug}` — from the issue title, converted to kebab-case, limited to ~40 chars

**Example:** `feat/issue-42-add-refund-endpoint`

**PR title** — in Conventional Commits format:

```
{type}({scope}): {description} (#{n})
```

Where:
- `{scope}` — main affected module (detected via the Phase 3 components)
- `{description}` — short summary of the change

**Example:** `feat(refunds): add refund creation endpoint (#42)`

### Step 3: Create branch via GitHub MCP

1. Invoke `create_branch` with:
   - `owner`, `repo`
   - `branch` — name generated in Step 2
   - `from_branch` — base branch (`main` or the configured one)
2. If the branch already exists (from a previous iteration), skip this step.

### Step 4: Push modified files

1. Run `git diff --name-only {base}...HEAD` to list touched files.
2. For each file, read content from the working tree.
3. Invoke `push_files` with:
   - `owner`, `repo`, `branch` (created in Step 3)
   - `message` — commit message in Conventional Commits format:
     ```
     {type}({scope}): {description}
     
     Refs: #{n}
     ```
   - `files` — array of `{path, content}`
4. If there are multiple logical commits (recommended for large PRs), invoke `push_files` multiple times with distinct messages.

### Step 5: Compose PR body with references

Structure:

```markdown
## Summary

{1-2 paragraphs describing the change, extracted from the brief and requirements}

Resolves #{n}

## Acceptance Criteria

<!-- Copied from docs/issues/issue-{n}/02-requirements.md -->

- [x] **AC-1:** {description}
- [x] **AC-2:** {description}
- [x] **AC-3:** {description}

## Architecture

See [architecture document](docs/issues/issue-{n}/03-architecture.md).

### Created ADRs

- [ADR-{n}: {title}](docs/adr/ADR-{n}-{slug}.md)

(omit if no ADR was created)

## Quality

- ✅ Gate 2 approved ([report](docs/issues/issue-{n}/06-quality-report.md))
- ✅ Security review approved ([report](docs/issues/issue-{n}/05-security-review.md))
- Coverage: {current}% (threshold: {threshold}%)

## How to test

{Instructions extracted from the architecture-brief — how to run, required variables, key scenarios}

## Review checklist

- [ ] ACs met (check traceability matrix in the Gate 2 report)
- [ ] ADRs reviewed (if applicable)
- [ ] Tests run locally
- [ ] Usage documentation updated (if applicable)

## Session Trace

<!-- Built by Step 5b from .ahrena/workflow/sessions/*.json
     filtered by branch == {branch}. Mandatory when session_tracking.enabled
     == true and the branch has heartbeat files. Human-driven PRs may use
     the phrase "_(human-driven; no session trace)_". Per lex-pr-quality
     and codex-session-tracking. -->

| Session | Entrypoint | Role | Started | Last Heartbeat |
|---|---|---|---|---|
| `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |

- Plan(s): plan-{NNN}
- Worktree: `.worktrees/{N}-{slug}`
- Cumulative active time: ~Xh Ymin

---

🤖 Generated by the Ahrena Issue-Driven Development flow (`warrior-athena`)
```

### Step 5b: Build the "Session Trace" section

Per `lex-pr-quality` (rules 9, j) and `codex-session-tracking` §7, before invoking `create_pull_request` aggregate all heartbeat files of the current branch:

1. Verify `session_tracking.enabled` in `.ahrena/.directives` (default `true`). If `false`, skip this step.
2. Resolve `session_tracking.heartbeat_dir` (default `.ahrena/workflow/sessions/`).
3. List `*.json` in the directory; filter by those whose `branch` matches the current branch (`git rev-parse --abbrev-ref HEAD`).
4. Sort by `started_at` ascending.
5. Compute `cumulative_active_time` = sum of `(last_heartbeat - started_at)` per session. Format as `~Xh Ymin`.
6. Build the table with columns `Session` (short UUID — first 8 chars), `Entrypoint`, `Role`, `Started`, `Last Heartbeat`.
7. Insert the section into the PR body before the "🤖 Generated..." block.
8. **PR with no associated heartbeats** (pure human, no Claude Code agent running): replace the table with the canonical phrase `_(human-driven; no session trace)_`.

This section is a complementary metric to `cry-pr-cost-stamp` (which measures tokens/USD). Here it measures real session time.

### Step 5c: Plan flush (per ADR-002)

Before invoking `create_pull_request`, ensure that the Issue body reflects the current state of the work:

1. Invoke `kata-flush-plan-to-issue` passing the Issue number.
2. The kata reads `.plans/{N}.md`, filters `<!-- not-flushed -->` blocks, runs the remote drift preflight, and writes the filtered content to the Issue body via MCP `update_issue` (preferred) or `gh issue edit --body-file` (fallback).
3. On remote drift detected (default `force=false`), the kata pauses and offers manual merge — do not proceed until resolved.

This step replaces the old mechanic of "update `status:` in the plan front-matter" (legacy pre-ADR-002 model): in the Issue-as-plan model, the Issue body is canonical; the local cache `.plans/{N}.md` is regenerable.

### Step 6: Create PR linked to the issue

1. Invoke `create_pull_request` with:
   - `owner`, `repo`
   - `title` — from Step 2
   - `head` — branch name
   - `base` — target branch
   - `body` — from Step 5
   - `draft` — per input (default `false`)
2. Capture the `html_url` of the created PR.
3. If `Resolves #{n}` is in the body, GitHub will automatically link the issue.

### Step 6b: Apply `status: to review` (transition `development → to review`)

Per `lex-issue-status` Axis A and `lex-agent-planning` Table A, when opening the PR Athena executes the transition `development → to review`:

```bash
# 1. PR — enters "to review" immediately
gh pr edit {pr_number} --add-label "status: to review"

# 2. Issue — sync (intra-artifact mutex)
gh issue edit {issue_number} \
  --remove-label "status: development" \
  --add-label "status: to review"
```

Per `lex-issue-status` Rule 3 (intra-artifact mutex), ensure each artifact carries exactly one `status:*`. Per Rule 5 (Issue↔PR sync), update simultaneously.

The label is the single source of truth for the state per ADR-002 — the Issue body (canonical plan) was already updated in Step 5c.

### Step 6c: Ask the user about scheduling the 3×15min loop

Per `codex-agent-planning` §10 (Pending review loop), Athena schedules 3 cycles of 15 min after opening the PR to nudge the human reviewer. However, the concrete scheduling mechanism depends on the Claude Code session context:

- **`/loop` dynamic mode** (auto-paced within the current session) — the agent reschedules via `ScheduleWakeup` at each cycle. Appropriate when the human stays in the editor; the session must stay alive.
- **Remote cron** (3 triggers every 15 min via `CronCreate`) — a remote schedule agent runs `gh pr view {N} --json reviewDecision` and reports back on completion. Appropriate for long-lived PRs where the local session may end.
- **Manual** — no scheduling; the human notifies when the review happens. Appropriate for meta-PRs in the framework itself, contexts without operational urgency, or when the reviewer is already attentive.

Athena **MUST** explicitly present these 3 options to the user before completing the step:

```
Athena: "PR #{N} opened in status: to review. How should the 3×15min
nudge loop be scheduled for the human reviewer?

  (a) /loop 15m — I reschedule within this session (session must stay alive)
  (b) remote cron — a schedule agent runs `gh pr view --json reviewDecision`
      3× every 15 min and reports on completion
  (c) manual — no scheduling; notify me when the review happens

Which option?"
```

Behavior per choice:

- **(a)** The agent calls `ScheduleWakeup` with `delaySeconds=900` and a prompt re-checking `gh pr view {N} --json reviewDecision,reviews`. If `APPROVED` by a human → transition to `done` on merge per Table A. If 3 cycles without approval → fires the MCP notification on `notifications.channels.pr_review_timeout`. **At every cycle, Athena suggests to the user invoking `warrior-argos` for automated review** (see "Argos suggestion per cycle" below).
- **(b)** The agent invokes the `schedule` skill creating a cron routine `*/15 * * * *` with an agent that executes the check and reports back. Same notification behavior on the 3rd cycle without human approval. **The remote agent suggests invoking Argos at every cycle** (same rules as option (a)).
- **(c)** Athena records the choice in the Issue body (via `kata-flush-plan-to-issue`) with the note: "Manual loop — human notifies when review happens." No `ScheduleWakeup` and no cron. **Athena still suggests invoking Argos once** at the end of Step 6c (recorded in the body), before proceeding.

#### Argos suggestion per cycle

At every wake-up (or cron execution), before deciding to reschedule, Athena MUST evaluate whether to propose an automated review by `warrior-argos` (the `to review ↔ review` sub-cycle of Table A):

1. **Collect two data points via `gh`:**
   - `gh pr view {N} --json commits --jq '.commits[-1].oid'` → current HEAD SHA of the PR.
   - `gh pr view {N} --json reviews --jq '[.reviews[] | select(.author.login == "argos[bot]" or (.body | contains("argos-review-id"))) | .submittedAt] | last'` → timestamp of the last review marked with the Argos idempotent marker (`argos-review-id:...`).
2. **Criterion to suggest:** suggest if (a) Argos has never reviewed OR (b) there were new commits since the last Argos review (HEAD SHA differs from the SHA captured in the last marker).
3. **Criterion to NOT suggest:** Argos has already reviewed the current HEAD (idempotent — Argos itself would abort by detecting its marker on the same commit).
4. **When suggesting:** present to the user (in chat or via PR comment depending on context):

   ```
   Athena: "Cycle {n}/3 — no human approval yet. Should I invoke
   /cry-review-pr {N} so Argos runs an automated review before
   the next wake-up? (yes / no)"
   ```

   If **yes** → invoke `cry-review-pr` (which delegates to `warrior-argos`); Argos operates the sub-cycle `to review → review → to review`; once finished, control returns to Athena who continues the normal loop.

   If **no** → record the refusal in working notes (a `<!-- not-flushed -->` block in `.plans/{N}.md`) to avoid re-proposing within the same cycle; reschedule normally.

5. **Inter-cycle idempotency:** if Argos has already reviewed the current HEAD without P0/P1 findings (the "Argos approves, awaiting human" case), Athena does NOT re-suggest in the next cycle until the PR receives new commits. This avoids polluting history with redundant calls.

The suggestion is **optional** and respects the human's choice. Athena never invokes Argos without explicit confirmation.

Without the human's choice about scheduling (options a/b/c above), Athena **MUST NOT** proceed to Step 7 — the loop is the responsibility declared in Table A; assuming a default option without confirmation would contradict the AI-First principle (which requires explicit approval on actions with side effects, see `lex-ai-first-experience`).

### Step 7: Update ADR status (proposed → accepted)

For each ADR created in Phase 3 (listed in the checkpoint):

1. Read `docs/adr/ADR-{n}-{slug}.md`.
2. Change `**Status:** proposed` to `**Status:** accepted`.
3. The ADR was approved at Gate 1 and survived Gate 2 — it is now official.
4. Include these modified files in the push (or make an additional commit if a push was already done).

### Step 8: Update final checkpoint

1. Update `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - phase completed: 7
   - final status: `completed`
   - created PR URL
   - created branch
   - ADRs transitioned to `accepted`
2. Inform `warrior-athena` (and the human):
   - PR created at `{URL}`
   - Next human step: review and approve

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Branch | Git branch | GitHub (via `create_branch` MCP) |
| Commits | Git commits with Conventional messages | GitHub (via `push_files` MCP) |
| Pull Request | PR with structured body | GitHub (via `create_pull_request` MCP) |
| PR URL | String | Return to orchestrator |
| Transitioned ADRs | Updated Markdown | `docs/adr/ADR-*` with `Status: accepted` |
| Final checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrictions

- **Use MCP only:** do not use `git push` directly nor `gh pr create` when the GitHub MCP is active (per `lex-mcp`).
- **No hardcoded credentials:** authentication exclusively via `GITHUB_PAT`.
- **Gate 2 `go` is an inviolable prerequisite:** do not open a PR if `06-quality-report.md` resulted in `no-go`.
- **PR body MUST reference docs/issues/issue-{n}/:** traceability from issue to PR requires these links.
- **Conventional Commits mandatory:** PR title and commit messages must follow the format (per `lex-conventional-commits`).

## References

- `lex-issue-driven` — flow laws
- `codex-issue-workflow` — position of this kata
- `kata-mcp-github-read` — analogous pattern of GitHub MCP usage
- `codex-mcp-github` — tools and parameters
- `lex-conventional-commits` — format of commits and PR title
- `codex-contributing` — project contribution flow
