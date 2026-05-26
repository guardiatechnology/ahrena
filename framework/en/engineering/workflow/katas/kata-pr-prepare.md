# Kata: Prepare Pull Request

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 7 of the Issue-Driven flow — creating a branch, pushing files, and opening a PR on GitHub via MCP, with a structured body referencing all flow artifacts

## Objective

After Gate 2 results in `go`, create the branch, push the modified files, and open a Pull Request on GitHub via MCP. The PR body is structured referencing the original issue, the numbered ACs, the created ADRs, and the flow artifacts in `.ahrena/issues/{n}/`. The result is a PR ready for human review, with full traceability.

## When to Use

- Phase 7 (final) of the flow orchestrated by `warrior-athena`, after `kata-quality-gate` results in `go`
- When a validated implementation must be submitted for review via PR

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Issue number | Yes | Number of the original issue (e.g., `42`) |
| Repository | Yes | `owner/repo` |
| Base branch | No | Target branch of the PR; default: `main` |
| Flow artifacts | Yes | `.ahrena/issues/{n}/*` and `docs/adr/ADR-*` created in previous phases |
| PR strategy | No | `draft` (default: `false`) |
| `--warrior <name>` | No | Name of the warrior invoking the kata (e.g., `athena`). Enables the warriors-default-author route in Step 6 when `warriors_default_author.enabled=true` AND the name is in `warriors_default_author.apply_to`. When omitted, the PR is created with the caller's default `gh` token (human author). |

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
2. Confirm `GH_TOKEN` is defined.
3. Read `.ahrena/issues/{n}/06-quality-report.md` and confirm the result is `go`. If `no-go`, refuse to create the PR and return to the orchestrator.
4. Consult `codex-mcp-github` to identify the correct tools (`create_branch`, `push_files`, `create_pull_request`).
5. **Resolve PR author identity** — source `scripts/ahrena-auth.sh` (no-op when `warriors_default_author.enabled=false`) and decide routing:
   - If `warriors_default_author.enabled == true` AND `--warrior <name>` was provided AND `<name>` is in `warriors_default_author.apply_to`: the PR will be opened as `ahrena-bot[bot]` using `GH_TOKEN_AHRENA_WARRIORS_DEFAULT` (Step 6 details).
   - Otherwise: the PR will be opened with the caller's default `gh` token (human author).

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

<!-- Copied from .ahrena/issues/{n}/02-requirements.md -->

- [x] **AC-1:** {description}
- [x] **AC-2:** {description}
- [x] **AC-3:** {description}

## Architecture

See [architecture document](.ahrena/issues/{n}/03-architecture.md).

### Created ADRs

- [ADR-{n}: {title}](docs/adr/ADR-{n}-{slug}.md)

(omit if no ADR was created)

## Quality

- ✅ Gate 2 approved ([report](.ahrena/issues/{n}/06-quality-report.md))
- ✅ Security review approved ([report](.ahrena/issues/{n}/05-security-review.md))
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

- Plan(s): plan-{M}-{slug}
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

### Step 5c: Plan flush

Before invoking `create_pull_request`, ensure that the Issue body reflects the current state of the work:

1. Invoke `kata-flush-plan-to-issue` passing the Issue number.
2. The kata reads `.plans/{N}.md`, filters `<!-- not-flushed -->` blocks, runs the remote drift preflight, and writes the filtered content to the Issue body via MCP `update_issue` (preferred) or `gh issue edit --body-file` (fallback).
3. On remote drift detected (default `force=false`), the kata pauses and offers manual merge — do not proceed until resolved.

This step replaces the old mechanic of "update `status:` in the plan front-matter" (legacy pre- model): in the Issue-as-plan model, the Issue body is canonical; the local cache `.plans/{N}.md` is regenerable.

### Step 6: Create PR linked to the issue

1. Resolve the PR-author token based on the Step 1 routing decision:
   - **Warriors-default-author path** (selected in Step 1): invoke the PR-creation command in a subshell with `GH_TOKEN=$GH_TOKEN_AHRENA_WARRIORS_DEFAULT` so the PR author resolves to `ahrena-bot[bot]`. Example for the CLI fallback path:
     ```bash
     GH_TOKEN="${GH_TOKEN_AHRENA_WARRIORS_DEFAULT}" gh pr create \
       --title "<title>" --body "<body>" \
       --head "<branch>" --base "<base>"
     ```
     When the MCP path is active, pass the equivalent token override through the MCP server configuration (per `codex-mcp-github`).
   - **Human path:** use the caller's default `gh auth` token (no override).
2. Invoke `create_pull_request` with:
   - `owner`, `repo`
   - `title` — from Step 2
   - `head` — branch name
   - `base` — target branch
   - `body` — from Step 5
   - `draft` — per input (default `false`)
3. Capture the `html_url` of the created PR.
4. If `Resolves #{n}` is in the body, GitHub will automatically link the issue.
5. **Soft-fail to human token** — if the warriors-default-author path returns a non-zero status (e.g., the App lacks `pull_requests:write` on this repo), emit a visible warning and retry once with the caller's default token. Never silence the degradation.

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

The label is the single source of truth for the state — the Issue body (canonical plan) was already updated in Step 5c.

### Step 6c: Argos pre-flight cycles (up to 3, interactive via AskUserQuestion)

Before nudging a human reviewer, Athena offers up to **3 cycles of automated review by Argos**. Each cycle is gated by AskUserQuestion — Athena never invokes Argos without user confirmation. The goal is to raise the quality of the PR (resolve P0/P1 findings) before taking the reviewer's time.

**Initial state:** PR open, label `status: to review` applied (per Step 6b).

**Argos loop (up to 3 cycles `A1, A2, A3`):**

For each cycle `A{n}`:

1. Athena asks via `AskUserQuestion`:

   ```
   Athena: "Cycle A{n}/3 — run an Argos review on the current HEAD? (PR #{N}, HEAD {short_sha})"

     (a) yes, invoke Argos now
     (b) no, skip Argos and go straight to human review
     (c) stop — end the entire flow
   ```

2. Behavior per choice:
   - **(a)** Athena transitions `status: to review → review`, invokes the `warrior-argos` subagent (via the Agent tool with `subagent_type=warrior-argos` or via `/cry-pr-review` — see feedback `argos_via_subagent`), waits for Argos to post the review with marker `argos-review-id:...`, transitions `status: review → to review`, and proceeds to step 3.
   - **(b)** Athena records the refusal in working notes (`<!-- not-flushed -->` block in `.plans/{N}.md`), jumps directly to **Step 6d**.
   - **(c)** Athena records "Loop ended by the user at Argos cycle A{n}" in the Issue body via `kata-flush-plan-to-issue`, does NOT proceed to Step 6d or Step 7. Flow ends here.

3. Athena reads the review findings:
   - **P0 BLOCKER** → Athena MUST address (modify code) before continuing; no opt-out.
   - **P1 WARNING** → Athena presents each finding to the user via `AskUserQuestion` ("Address now or defer to a follow-up Issue?"). Address → modify code; defer → record TODO in the Issue body.
   - **P2 SUGGESTION** → Athena records as an informational note in the Issue body (no prompt).

4. If Athena modified code in step 3, she **MUST** commit and push before the next cycle. Each commit triggers `kata-flush-plan-to-issue` (per Step 5c — completed Step counts as a flush trigger). The next Argos check will have a new HEAD (non-idempotent — Argos actually runs).

5. If `n < 3`, return to step 1 (next cycle). If `n == 3`, exit the Argos loop and proceed to **Step 6d**.

**Early-exit criteria for the Argos loop:**
- Argos returns "Argos approves, awaiting human" with no actionable P0/P1 findings → Athena MAY offer "Want another Argos cycle, or go straight to the human review?" and exit if the user chooses to skip.
- User picks (c) stop at any cycle → flow ends without Step 6d/7.

**Idempotency:** if HEAD has not changed since Argos's last review (same commit_id), Athena MUST warn the user ("HEAD unchanged since last review — a new review will be idempotent; Argos will abort by its own marker"). Suggest addressing at least one finding before re-invoking Argos.

#### Sub-step: AI reviewers parallel to Argos

After the user picks (a) at step 1 of cycle A{n}, Athena MUST evaluate whether it makes sense to invoke **parallel AI reviewers** (GitHub Apps integrated with the repo), based on the diff content:

| Reviewer | When it makes sense | How to invoke | Idempotent detection |
|---|---|---|---|
| **Gemini** (`gemini-code-assist[bot]`) | PR touches new code in any language; good at idiomatic suggestions and security | `gh pr comment {N} --body "/gemini review"` | `gh pr view {N} --json reviews --jq '[.reviews[] | select(.author.login == "gemini-code-assist[bot]") | .commit_id] | last'` |
| **Coderabbit** (`coderabbitai[bot]`) | Multi-file PR; good at consistency checks and best practices | `gh pr comment {N} --body "@coderabbitai review"` | similar (`.author.login == "coderabbitai[bot]"`) |
| **Qodo-Merge** (`qodo-merge-pro[bot]`) | Backend PR (Python, Node) — strong at test coverage and edge cases | `gh pr comment {N} --body "/review"` | similar |

**Proposal criterion:** Athena inspects `gh pr view {N} --json files --jq '[.files[].path]'` and decides which reviewers are useful:

- Docs-only PR (`docs/**`, `README*`, `*.md`) → no additional AI reviewer (Argos suffices).
- PR with production code (`src/**`, `framework/**` in Ahrena's own case) → propose 1-2 reviewers per stack.
- Mixed PR → propose the subset covering the predominant stack.

**Presentation:** Athena gathers the candidate reviewers into a single `AskUserQuestion`:

```
Athena: "Parallel AI reviewers to Argos for A{n}/3? (multi-select)

  [ ] Gemini (/gemini review)
  [ ] Coderabbit (@coderabbitai review)
  [ ] Qodo-Merge (/review)
  [ ] none — only Argos
```

**Behavior:**

1. For each marked reviewer, Athena posts the invocation comment sequentially (not in parallel — reduces timeline noise).
2. Athena **does NOT block** waiting for these reviewers — they are asynchronous (GitHub App webhook); results appear as reviews/comments on the PR on the app's schedule (~30s to a few min).
3. Athena proceeds to step 2 of cycle A{n} (transition `to review → review` and invoking the Argos subagent). Argos runs its review in parallel with the external AI reviewers.
4. At step 3 (Athena reads findings), Athena collects findings from **all reviewers** with new `submittedAt > HEAD push time` (Argos + Gemini + Coderabbit + Qodo). Treats each finding via the same P0/P1/P2 schema:
   - Argos publishes P0/P1/P2 explicitly with a marker.
   - Gemini/Coderabbit/Qodo publish free-form suggestions — Athena classifies heuristically (words: "must", "blocker", "critical" → P0; "should", "consider" → P1; "nit", "optional" → P2).
5. Idempotency: if an AI reviewer has already reviewed the current HEAD (via captured commit_id), Athena does NOT re-invoke that reviewer in the next cycle until there are new commits.

**Criterion to NOT propose:** if A{n} is a re-validation cycle after fixing findings from A{n-1} (new HEAD after addressing), and Argos was confirmed, extra AI reviewers may be skipped — the re-validation is primarily about closing findings, not raising new ones. Athena proposes `none` as the default in these cases.

### Step 6d: Human nudge loop (3 cycles via ScheduleWakeup, with a Slack notification per cycle)

After the Argos cycles (Step 6c), Athena schedules the human-reviewer nudge loop. Unlike the Argos cycle (interactive), the human nudge loop uses `ScheduleWakeup` for periodic wake-ups.

**Scheduling mechanism:** Athena asks via `AskUserQuestion`:

```
Athena: "Ready for the human nudge loop (3×15min). How should it be scheduled?

  (a) /loop 15m — I reschedule via ScheduleWakeup within this session
  (b) remote cron — the `schedule` skill creates a */15 routine that checks and reports
  (c) manual — no scheduling; the human notifies when the review happens

Which option?"
```

**Behavior per choice:**

- **(a)** Athena calls `ScheduleWakeup` with `delaySeconds=900` and a prompt re-checking `gh pr view {N} --json reviewDecision,mergedAt`. At every cycle: fires the Slack notification (see "Per-cycle Slack notification" below) + checks state.
- **(b)** Athena invokes the `schedule` skill creating a cron routine `*/15 * * * *` with an agent that runs the check, fires the Slack notification, and reports back.
- **(c)** Athena records "Manual loop" in the Issue body. No scheduling; the human notifies.

**Per-cycle Slack notification:**

At every cycle `H1, H2, H3`, Athena fires a message via the notification MCP configured in `.ahrena/.directives` (`notifications.provider`) on the channel `notifications.channels.pr_review_timeout`. The urgency escalates:

| Cycle | Default message |
|---|---|
| H1 (start) | `PR #{N} ready for review — {title}. {url}` |
| H2 (+15min) | `Reminder #1: PR #{N} awaiting review for ~15min. {url}` |
| H3 (+30min) | `Reminder #2: PR #{N} awaiting review for ~30min — second nudge. {url}` |

After H3 with no approval → the loop ends silently (3 nudges were enough).

**Detectable states during the loop:**

| `gh pr view` returns | Athena's action |
|---|---|
| `mergedAt != null` | Transition `status: to review → done` on PR + Issue; capture `mergeCommit.oid`; end loop. |
| `reviewDecision == "APPROVED"` and `mergedAt == null` | Comment "PR approved, waiting for merge"; end loop. |
| `reviewDecision == "CHANGES_REQUESTED"` | → **Step 6e** (CHANGES_REQUESTED handler). |
| Otherwise (`REVIEW_REQUIRED` or null) | If `H < 3` → reschedule; if `H == 3` → end. |

### Step 6e: CHANGES_REQUESTED handler (loop reset)

If during Step 6d the human reviewer requests changes (`reviewDecision == "CHANGES_REQUESTED"`):

1. Athena reads the human's review comments via `gh pr view {N} --json reviews --jq '.reviews[-1]'`.
2. Athena presents a summary of the requests to the user via `AskUserQuestion`:
   ```
   Athena: "Reviewer requested changes. Address now?

     (a) yes, I'll implement the changes
     (b) defer — record as a follow-up Issue and keep the PR open
     (c) stop — close the loop and the PR
   ```
3. Behavior per choice:
   - **(a)** Athena implements the changes (modify code, commit, push). Each commit triggers `kata-flush-plan-to-issue`. The push produces a new HEAD SHA.
   - **(b)** Athena records a TODO in the Issue body + opens a follow-up Issue referencing the request. Keeps `status: to review`.
   - **(c)** Athena closes the PR (`gh pr close 97`), transitions the Issue to `status: abandoned` with an explanatory note. Flow ends.

4. After (a) or (b), Athena **restarts the loop from Step 6c** (3 fresh Argos pre-flight cycles on the new HEAD) — because new commits invalidate the previous Argos review. Does not jump directly to Step 6d.

5. If the user chose (b) defer (no new commits), Athena MAY skip Step 6c and go straight to Step 6d (since HEAD has not changed).

**This handler ensures CHANGES_REQUESTED resets the full quality cycle, not just the human nudge loop.**

Without the human's choice about scheduling (options a/b/c of Step 6d), Athena **MUST NOT** proceed to Step 7 — the loop is the responsibility declared in Table A; assuming a default option without confirmation would contradict the AI-First principle (which requires explicit approval on actions with side effects, see `lex-ai-first-experience`).

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
- **No hardcoded credentials:** authentication exclusively via `GH_TOKEN`.
- **Gate 2 `go` is an inviolable prerequisite:** do not open a PR if `06-quality-report.md` resulted in `no-go`.
- **PR body MUST reference .ahrena/issues/{n}/:** traceability from issue to PR requires these links.
- **Conventional Commits mandatory:** PR title and commit messages must follow the format (per `lex-conventional-commits`).

## References

- `lex-issue-driven` — flow laws
- `codex-issue-workflow` — position of this kata
- `kata-mcp-github-read` — analogous pattern of GitHub MCP usage
- `codex-mcp-github` — tools and parameters
- `lex-conventional-commits` — format of commits and PR title
- `codex-contributing` — project contribution flow
