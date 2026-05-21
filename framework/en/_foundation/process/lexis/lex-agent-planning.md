# Lexis: Mandatory Planning for Agent Tasks

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Every multi-step task initiated by any agent or subagent (Claude, Cursor, IDEs, warriors, katas, cries)

## Purpose

Agents that execute without prior planning produce partial results, leave files in inconsistent states, and force the user to rebuild context manually. This Lexis eliminates that pattern by requiring every agent to record its plan before executing, making intent, scope, and sequence auditable by humans and by other agents. It also defines a unified lifecycle across Plan, GitHub Issue, and PR — with an explicit owner for each transition — to eliminate drift and give visibility into the review "waiting room."

The canonical model is hierarchical: each **Issue** (User Story, Bug, or Tech Task) carries the problem (Why/What/How/AC); from each Issue derive **1..N Plans**, materialized as **GitHub sub-issues** (Issue Type Task) that encapsulate executable units of work; from each Plan derive **1..N PRs**. Plans never exist as a canonical local file — the sub-issue body is the source of truth. Provider-specific local caches (`.claude/plans/`, `.cursor/plans/`) are regenerable derivatives, gitignored.

## Law

> **Every agent MUST record a canonical plan as a GitHub sub-issue (Issue Type Task) linked to the parent Issue BEFORE starting execution of any task that involves 2 or more steps, affects multiple files, or produces permanent artifacts. The plan MUST be presented to the user for confirmation before execution begins. Starting multi-step execution (creating a branch, committing, opening a PR) without a created and confirmed Plan sub-issue is FORBIDDEN. Drafting a plan locally in `.claude/plans/plan-{slug}.md` or `.cursor/plans/plan-{slug}.md` with `status: draft` in the front-matter is PERMITTED as a plan-first entry point, provided the agent promotes the draft to a sub-issue before starting execution (transition `draft → todo` via `kata-contributing-issue` + `kata-decompose-issue-into-plans` or `kata-plan-task`). The plan's `status:` lives as a **canonical label** on the sub-issue (and on the PR, starting at `to review`); the canonical enum is `todo | development | to review | review | to release | release | done` (plus the alternate terminal `abandoned`, and the local-only state `draft` pre-promotion, which does not exist as a GitHub label); each transition MUST be performed by the owner declared in this Lex. The `— → todo` transition applies the creation gate (template + labels + Issue Type + Why/What/How); the `todo → development` transition applies the execution-start gate (remote branch + worktree + assignee).**

## Coverage

- **Applies to:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, any AI agent or subagent that invokes katas, warriors, or cries in the Ahrena context
- **Bound agents:** all, without role exception
- **Allowed exceptions:** trivial single-step operations (editing a single file with a direct instruction, pure read queries, isolated commands with no permanent side effects)

## Hierarchical Issue → Plan → PR model

```
Issue (User Story | Bug | Tech Task)            ← problem, Why/What/How, AC
   │
   ├─ Plan sub-issue (Task)                     ← executable unit #1
   │     ├─ status: todo | development | to review | review | done
   │     ├─ branch: {type}/{M}-{slug}
   │     └─ PR(s) that close this Plan
   │
   ├─ Plan sub-issue (Task)                     ← executable unit #2
   │     └─ ...
   │
   └─ Plan sub-issue (Task)                     ← executable unit #N
         └─ ...
```

| Layer | Location | Role | Versioning |
|---|---|---|---|
| **Issue (parent)** | `https://github.com/{owner}/{repo}/issues/{N}` | Carries problem, motivation, acceptance criteria. Has no branch of its own | GitHub audit log |
| **Plan sub-issue** | `https://github.com/{owner}/{repo}/issues/{M}`, sub-issue of #{N} | Canonical. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Carries dedicated branch and PR(s) | GitHub audit log |
| **Provider cache** | `.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`, gitignored | AI working memory + scratch. Superset of the sub-issue body + `<!-- not-flushed -->` blocks. Named by the sub-issue number | Regenerable local cache |
| **Phase artifacts** | `.ahrena/issues/issue-{N}/`, committed | `01-brief.md` … `06-quality-report.md` of the Issue-Driven flow (tied to the parent Issue) | Git |

The local cache is provider-specific: Claude agents use `.claude/plans/plan-{M}-{slug}.md`; Cursor agents use `.cursor/plans/plan-{M}-{slug}.md`. There is no shared cache between providers — each one carries its working memory independently, regenerated from the sub-issue via `kata-load-plan-from-subissue`.

## Plan sub-issue body schema (canonical)

```markdown
## Summary

{2-4 sentences describing the executable objective of this Plan. Typically a slice of the parent Issue scope.}

Parent: #{N}

## Plan

### Objective
{Why this unit exists and what it delivers when done — 1 to 3 sentences.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{Other Plans, Issues, or PRs this task depends on; "None" if none.}

### Risks
{Known risks and mitigations; "None identified" if none.}

### Open Questions
{Open questions that need a decision before/during execution; "None" if none.}
```

Local cache schema (`.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`): **superset** of the sub-issue body. Carries YAML front-matter for session metadata + the full mirrored body + marked local sections.

**Front-matter** (canonical):

```yaml
---
plan_id: "{M}"              # Plan sub-issue number; "draft" pre-promotion
title: "{slug}"             # slug used on the branch (and on the file name while draft)
status: todo | development | to review | review | done | abandoned
                            # | draft (local-only state, pre-promotion)
                            # | to release | release (release axis)
agent: claude | cursor
issue: "{owner/repo#M}"     # "TBD" while draft
parent: "{owner/repo#N}"    # parent Issue (User Story | Bug | Tech Task)
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
promoted_at: "YYYY-MM-DDTHH:MM:SSZ"   # OPTIONAL — filled on the draft → todo transition
---
```

The `merge_commit:` and `closed_at:` fields do NOT appear in the front-matter — they are derived from GitHub APIs on the post-merge audit (see §Closure audit). The `promoted_at:` field records the UTC timestamp of the plan-first promotion (transition `draft → todo`); fill in only for plans that started in `draft`.

**Body**: superset of the sub-issue body + local sections marked with `<!-- not-flushed -->` blocks:

```markdown
<!-- not-flushed -->
## Working notes
- debugging decision X at 14:32
- error Y reproduced in test-Z

## Next actions
1. try approach A; if it fails, B

## Scratch
any free text the AI wants to keep as local context
<!-- /not-flushed -->
```

`kata-flush-plan-to-subissue` filters out `<!-- not-flushed -->` blocks before writing to the sub-issue body. The front-matter is NEVER flushed to GitHub — it lives only in the local cache.

## Plan lifecycle

The cycle operates on **two disjoint axes**:

### Axis A — Dev cycle (Plan derived from User Story / Bug / Tech Task)

```
(draft, local-only) ⇢ — → todo → development → to review → review → done
                                                       ↘
                                                       abandoned (alternate terminal, any stage)
```

- `(draft)` — **local-only** state pre-`todo`. Lives in the plan-file front-matter (`.claude/plans/plan-{slug}.md` or `.cursor/plans/plan-{slug}.md`) with `status: draft, issue: TBD`. Does not exist as a canonical label on GitHub. The `draft → todo` transition is the **plan-first promotion** (see Plan-first guardrail below).
- `— → todo` — Plan sub-issue created with template + labels + Issue Type + Why/What/How; no branch, no worktree, no assignee yet.
- `todo → development` — Plan picked up for execution: remote branch created via `gh issue develop`; worktree per `lex-git-worktrees`; assignee applied (who commits to execute); first commit imminent.
- `development → to review` — implementation complete; PR opened; prior flush of the local cache via `kata-flush-plan-to-subissue`.
- `to review ↔ review` — reviewer (human or Argos) enters and exits the active review cycle.
- `to review → done` — PR merged; Plan sub-issue closed via `Closes #{M}`.
- `abandoned` — alternate terminal; Plan discarded at any stage.

### Axis B — Release cycle (Plan dedicated to a release)

```
— → to release → release → done
                       ↘
                       abandoned (alternate terminal, any stage)
```

- `— → to release` — release sub-issue created by Janus, listing PRs merged since the last tag.
- `to release → release` — release in execution; human approved bump/changelog.
- `release → done` — tag pushed, release build passed, GitHub Release published.
- `abandoned` — release aborted before tag.

Label mutex is **intra-artifact** (within each Issue/PR), not cross-artifact: a sub-issue carries exactly one `status: <name>` label at a time. The HARD-GATE in `lex-issue-status` forbids applying Axis B labels on a feature sub-issue, and vice versa.

## Gate 1 — Plan created (`— → todo`)

Owner: `warrior-eunomia` (fallback: session agent while Eunomia is not shipped).

Every Plan sub-issue MUST be created by Eunomia via `kata-decompose-issue-into-plans` (downstream of parent Issue analysis) or `kata-plan-task` (standalone Plan top-level linked to an existing Issue). The agent executes the 4 steps below before marking the `status: todo` label:

1. **Confirm the parent Issue exists and is well-formed** (per `lex-issue-first` and `lex-issue-quality`). Without an open parent Issue, there is no Plan to create — invoke `kata-contributing-issue` first to open the Issue.
2. **Create the Plan sub-issue** linked to the parent Issue via MCP `create_issue` (preferred) or `gh issue create --type Task` (fallback), applying the Plan template, required labels, and Issue Type `Task`.
3. **Fill the sub-issue body with the canonical plan** (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) via MCP `update_issue` or `gh issue edit --body-file <path>` (fallback per `lex-mcp` rule 4).
4. **Verify Issue Type post-creation** (per `lex-issue-type-verified`) — Plans are always `Task`.

Branch, worktree, and assignee are **NOT** preconditions of `— → todo`. They belong to `todo → development`.

```
<HARD-GATE>
warrior-eunomia (or the session agent acting as fallback while Eunomia
is not shipped) MUST NOT apply the `status: todo` label to a Plan
sub-issue without satisfying ALL 4 canonical steps:

  (a) Parent Issue open and compliant with lex-issue-first and
      lex-issue-quality (template, labels, compatible Issue Type,
      Why/What/How populated)
  (b) Plan sub-issue created linked to the parent Issue via MCP
      create_issue (preferred) or gh issue create --type Task (fallback),
      with Plan template and required labels applied
  (c) Sub-issue body populated with the canonical plan (Summary + Plan
      containing Objective, Steps, Risks, Dependencies, Open Questions)
      via MCP update_issue or gh issue edit --body-file (fallback)
  (d) Issue Type verified as Task per lex-issue-type-verified

This rule applies to EVERY Plan (top-level or decomposition subtask),
regardless of:
  - perceived size ("it's just a chore")
  - urgency ("production fire")
  - who requested ("the CEO asked")
  - team confidence ("we already tested a lot")

Declared exception: none. Branch, worktree, and assignee are NOT
preconditions of this gate — they belong to the todo → development gate.
</HARD-GATE>
```

### Plan-first guardrail

Plan-first is a legitimate path: the agent (or human) MAY draft a plan locally in `.claude/plans/plan-{slug}.md` or `.cursor/plans/plan-{slug}.md` carrying `status: draft` in the front-matter (and `issue: TBD` while no sub-issue exists). What is FORBIDDEN is starting execution (branch, commits, PR) without first promoting the draft to a Plan sub-issue on GitHub.

When the user signals plan intent without referencing an Issue (e.g., "let's plan X"), the agent MAY follow one of two paths:

- **Path A (issue-first):** invoke `kata-contributing-issue` to open the parent Issue immediately; then `kata-decompose-issue-into-plans` or `kata-plan-task` to create the Plan sub-issue(s); then `kata-load-plan-from-subissue` to materialize the local cache. There is no `draft` state on this path.

- **Path B (plan-first / draft):** draft the plan directly in `.claude/plans/plan-{slug}.md` (or `.cursor/plans/...`) with front-matter `status: draft, issue: TBD`. When the draft matures, **promote** in an atomic step:
  1. `kata-contributing-issue` creates the parent Issue if there is not one yet.
  2. `kata-decompose-issue-into-plans` or `kata-plan-task` creates the canonical Plan sub-issue.
  3. Rename the file from `plan-{slug}.md` to `plan-{M}-{slug}.md` (where `{M}` is the number of the created sub-issue).
  4. Update the front-matter — `status: draft → todo`, `issue: TBD → {owner/repo#M}`, record `promoted_at` with a UTC timestamp.
  5. Apply the canonical `status: todo` label on the newly created sub-issue (Eunomia's Gate 1).

`status: draft` is a **purely local** state — it lives in the front-matter of the plan-file, does NOT exist as a canonical label on GitHub. The `status: todo` label only appears after promotion. `kata-load-plan-from-subissue` returns `PROMOTION_REQUIRED` (flow signal, not a fatal error) when it receives an orphan plan-file with `status: draft` or `issue: TBD`, directing the invoking agent to trigger promotion before canonical materialization.

## Gate 2 — Plan started (`todo → development`)

Owner: `warrior-athena`.

Athena takes the Plan when execution is about to start (not before). On `todo → development`, Athena executes the 3 canonical steps:

1. **Create the remote branch** and link it to the Plan sub-issue via `gh issue develop {M} --base main --name {type}/{M}-{slug}` (registers the branch as "Development" in the GitHub sidebar).
2. **Create the worktree** per `lex-git-worktrees` at `.worktrees/{M}-{slug}/`.
3. **Apply assignee** on the Plan sub-issue (whoever commits to execute — human or agent identity).

Applying `status: development` without all 3 steps complete is FORBIDDEN. Athena does not start Phase 4 of Issue-Driven without the gate satisfied.

```
<HARD-GATE>
warrior-athena MUST NOT apply the `status: development` label to a
Plan sub-issue without satisfying ALL 3 canonical steps:

  (a) Remote branch created and linked to the Plan sub-issue via
      gh issue develop {M} --base main --name {type}/{M}-{slug}
  (b) Worktree created per lex-git-worktrees at
      `.worktrees/{M}-{slug}/`
  (c) Assignee applied on the Plan sub-issue (the person or agent
      committing to execute)

This rule applies to EVERY todo → development transition, regardless of:
  - perceived size ("it's just a chore")
  - urgency ("production fire")
  - who requested ("the CEO asked")
  - team confidence ("we already tested a lot")

Declared exception: none. Athena does not start execution without branch,
worktree, and assignee — these three are the minimum binding for audit
and to prevent phantom work outside a Plan sub-issue.
</HARD-GATE>
```

## Owners of each transition

### Table A — Dev cycle (Eunomia / Athena / Argos)

| Transition | Owner | Trigger |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: session agent) | Creates Plan sub-issue + fills canonical body + verifies Issue Type |
| `todo → development` | `warrior-athena` | Creates branch via `gh issue develop` + worktree + assignee; starts Phase 4 |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` opens PR; prior flush of cache via `kata-flush-plan-to-subissue` |
| `to review → review` | `warrior-argos` | Argos starts the automated review cycle |
| `review → to review` | `warrior-argos` | Argos ends the cycle without approving (changes-requested or awaiting-human) |
| `to review → done` | `warrior-athena` | Human approves PR; merge closes Plan sub-issue via `Closes #{M}` |
| `any → abandoned` | creator or current owner | Plan discarded |

### Table B — Release cycle (Janus)

| Transition | Owner | Trigger |
|---|---|---|
| `— → to release` | `warrior-janus` | Opens release sub-issue; populates `Tracks: #N1, #N2, ...` with PRs merged since the last tag |
| `to release → release` | `warrior-janus` | `kata-release-prepare` starts; human gate for bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` completes (tag pushed, validate-tag passes, Release created); notification via MCP at `notifications.channels.release_notify` |
| `any → abandoned` | `warrior-janus` | Release aborted before tag |

Each owner MUST:

- Apply the corresponding `status: <name>` label on the Plan sub-issue on GitHub (per `lex-issue-status`).
- Apply the corresponding `status: <name>` label on the PR (starting at `to review`).
- Trigger `kata-flush-plan-to-subissue` if the local cache is ahead of the sub-issue body.

## Closure audit

For post-merge audit, two fields are derived from native GitHub APIs (no dedicated front-matter in the Plan):

| Logical field | Canonical source | Command |
|---|---|---|
| `closed_at` | `Issue.closedAt` | `gh issue view {M} --json closedAt --jq .closedAt` |
| `merge_commit` | `PullRequest.mergeCommit.oid` | `gh pr view {PR} --json mergeCommit --jq .mergeCommit.oid` |

For legacy files in `.ahrena/issues/_legacy/` that still carry historical YAML front-matter, `merge_commit:` and `closed_at:` are recognized as accepted optional front-matter — preserves audit without retrofit.

## Load/flush cadence

Sync between the local cache and the Plan sub-issue body occurs at **4 canonical triggers** (not at every toggle):

| Trigger | Operation |
|---|---|
| Session start / handoff between agents | `kata-load-plan-from-subissue` |
| `status:` label transition on the sub-issue/PR | `kata-flush-plan-to-subissue` |
| Plan step marked as complete (`[ ]` → `[x]`) | `kata-flush-plan-to-subissue` |
| Session end (heartbeat ends or owner leaves) | `kata-flush-plan-to-subissue` |

Intermediate toggles, scratch edits (`<!-- not-flushed -->`), and working notes are **free** — they do not trigger a flush. Operational documentation in `codex-agent-planning` §9.

## Relationship to other artifacts

- **Parent Issue (User Story / Bug / Tech Task):** carries problem, motivation, AC. Has no branch of its own. Typically closes via `Closes #{N}` on the final PR of the final Plan sub-issue.
- **Plan sub-issue:** carries the canonical plan in the body; the `status: <name>` label is the only source of truth for state.
- **PR:** starting at `to review`, the PR carries the corresponding `status: <name>` label, updated by Athena/Argos/Janus as state advances. Label sync is the transition owner's responsibility.
- **`.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`:** provider-specific regenerable local cache; never committed; rebuilt by `kata-load-plan-from-subissue` on fresh clone.
- **`.ahrena/issues/issue-{N}/`:** committed; receives Phase artifacts of the Issue-Driven flow for parent Issue #{N} (per `lex-issue-driven`).
- **Checkpoint (`.checkpoint`):** the Plan covers **task** (Steps, Decisions, Risks in the sub-issue body); the checkpoint covers **session** (window focus, hand-off between Plans, parallel threads). Overlap is FORBIDDEN — see `lex-checkpoint` rule 5.
- **ADR:** when a Plan identifies a relevant architectural decision, an ADR MUST be opened per `lex-issue-driven`. Example filenames: `ADR-008-use-event-sourcing-for-refund-audit-trail.md`, `ADR-007-use-fastapi-routers.md`, `ADR-001-use-event-sourcing-for-ledger.md`, `ADR-002-migrate-to-fastapi.md`.
- **Session heartbeat:** the Claude Code session operating on the Plan is recorded at `.ahrena/workflow/sessions/<session-id>.json` (per `codex-session-tracking`); it does not live in the sub-issue body.

### Plan vs local cache vs `.checkpoint` — what goes where

| Content | Lives in |
|---|---|
| Objective, Steps `[x]`, Risks, Dependencies, Open Questions | Plan sub-issue body (canonical) |
| Relevant architectural decisions | ADR in `docs/adr/` (referenced by the Plan) |
| Working notes, debugging diary, scratch | Local cache in `<!-- not-flushed -->` blocks |
| General work-window focus (Session focus) | `.checkpoint` — gitignored |
| Pointers to multiple active Plans (Active plans) | `.checkpoint` — gitignored |
| Parallel threads that did not become a Plan (Open threads) | `.checkpoint` — gitignored |

When in doubt: structural content goes to the Plan sub-issue body; volatile content goes to the local cache in a not-flushed block; session focus goes to `.checkpoint`.

## Examples

### Correct — Top-down flow (Issue first)

```
User: "We need to migrate the ledger to event sourcing — open a User Story"
→ Agent invokes kata-contributing-issue (user-story-for-api template)
→ Issue #200 created (Why/What/How, numbered AC, Issue Type Feature,
  `user story 🎯` label, status: todo via lex-issue-quality Gate 1)

Next session, agent decomposes:
→ Eunomia invokes kata-decompose-issue-into-plans 200
→ 3 Plan sub-issues created:
   #201 (Task) — refactor Ledger aggregate for event sourcing
   #202 (Task) — implement projection write-side
   #203 (Task) — migrate read-side via projection
→ Each sub-issue carries Summary + Plan section
→ Eunomia applies status: todo on the 3 sub-issues (Gate 1 OK)
→ Issue #200 stays at status: todo until the first PR starts

Plan #201 execution:
→ Athena (Gate 2): gh issue develop 201 --base main --name refactor/201-ledger-event-sourcing
→ Athena creates worktree at .worktrees/201-ledger-event-sourcing/
→ Athena applies assignee fernandoseguim on sub-issue #201
→ Athena applies status: development on sub-issue #201
→ kata-load-plan-from-subissue 201 materializes .claude/plans/plan-201.md
→ Implementation runs; kata-flush-plan-to-subissue 201 on each completed Step
→ Athena opens PR via kata-pr-prepare: status: to review on #201 + PR
→ Argos enters: status: review; leaves without approving: status: to review
→ Human approves; merge closes #201 via Closes #201: status: done

Repeat for #202, #203. When #203 merges with Closes #200 in the PR body,
parent Issue #200 auto-closes.

Release cycle (separate):
→ Janus opens release sub-issue (e.g., #210); Tracks: #201-PR, #202-PR, #203-PR
→ Janus applies status: to release on the release sub-issue
→ Janus starts kata-release-prepare: status: release
→ Janus completes kata-release-publish: status: done
```

### Correct — Plan-first flow, Path A (immediate issue-first)

```
User: "let's plan the migration of the logger to Loguru"
→ Agent recognizes: no Issue referenced
→ Agent invokes kata-contributing-issue (tech-task or user-story template)
→ Parent Issue #220 created (Why/What/How, AC)
→ Agent invokes kata-decompose-issue-into-plans 220
→ 2 Plan sub-issues #221, #222 created
→ Eunomia applies status: todo on the 2 sub-issues
→ kata-load-plan-from-subissue 221 materializes .claude/plans/plan-221.md
→ Execution follows per Gate 2 (Athena)
```

### Correct — Plan-first flow, Path B (draft → promotion)

```
User: "let's draft a plan to refactor the logger"
→ Agent creates .claude/plans/plan-logger-refactor.md with front-matter:
   status: draft, issue: TBD, parent: TBD, plan_id: "draft"
→ Draft matures over N edits (Objective, Steps, Risks)
→ User approves: "ok, let's move to execution"
→ Agent promotes in an atomic step:
   1. kata-contributing-issue → parent Issue #220 (tech-task)
   2. kata-plan-task → Plan sub-issue #221 (Task), draft body copied
   3. mv .claude/plans/plan-logger-refactor.md .claude/plans/plan-221.md
   4. front-matter: status: draft → todo, issue: TBD → guardiatechnology/ahrena#221,
      parent: guardiatechnology/ahrena#220, promoted_at: 2026-05-13T19:00:00Z
   5. Eunomia applies label "status: todo" on #221 (Gate 1 OK)
→ Execution follows per Gate 2 (Athena)
```

### Incorrect

```
Task: implement feature X
→ Agent creates branch directly via git checkout -b without opening a parent Issue
→ ❌ Violates lex-issue-first; without a parent Issue, no Plan can be created

→ Agent creates file .claude/plans/plan-feature-x.md with status: draft
  and then creates a branch via git checkout -b feat/x without promoting
  the draft to a Plan sub-issue on GitHub
→ ❌ Violates the plan-first guardrail; a local draft with status: draft
  is permitted, but starting execution (branch, commits, PR) without
  first promoting the draft via kata-contributing-issue +
  kata-decompose-issue-into-plans (Path B) is forbidden

→ Agent applies status: todo label on the Plan sub-issue without filling the body
→ ❌ Violates Gate 1 precondition (c): body must carry Summary +
   Plan section before status: todo is final

→ Agent applies status: development label on the sub-issue without creating
  the remote branch or the worktree
→ ❌ Violates Gate 2 preconditions (a), (b), and (c): branch via gh issue develop,
  worktree under .worktrees/, and assignee applied are the three minimum steps

→ Agent applies status: to release label on a feature sub-issue
→ ❌ Violates intra-artifact mutex of lex-issue-status: `to release`
   belongs to Axis B (release sub-issue), forbidden in Axis A
```

## Automated Validation

- **Tool:** agent self-check before any multi-step execution; `kata-plan-task` and `kata-decompose-issue-into-plans` as canonical entry points; PR review confirms that the Plan sub-issue `status:*` label and the PR `status:*` label are aligned, and that the sub-issue body carries Summary + Plan section. Argos enumerates `.claude/plans/*.md` and `.cursor/plans/*.md` during review; for each `plan_id` in the cache, verifies a corresponding sub-issue exists in GitHub (orphans are a block).
- **Timing:** before any multi-step task execution — no exception; and at every state transition.
- **Metric:** 0 multi-step tasks executed without an open Plan sub-issue; 0 files in `.claude/plans/` or `.cursor/plans/` without a corresponding sub-issue; 0 PRs merged with `status:` divergent between sub-issue and PR; 100% of transitions performed by the declared owner; 100% of release sub-issues with `Tracks:` listing PRs merged since the last tag.

## References

- `lex-issue-status` — canonical status labels; split Table A (dev) / Table B (release)
- `lex-issue-type-verified` — programmatic verification of Issue Type post-creation
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — gate preconditions
- `lex-mcp` — MCP preference + CLI fallback for `gh issue edit`
- `lex-checkpoint` — session state tracking (complementary)
- `lex-issue-driven` — Issue-Driven flow; Phase artifacts in `.ahrena/issues/issue-{N}/`
- `codex-agent-planning` — operational manual for the hierarchical model (load → edit → flush)
- `kata-plan-task` — operational procedure for creating a standalone top-level Plan
- `kata-decompose-issue-into-plans` — decomposes a parent Issue into Plan sub-issues
- `kata-contributing-issue` — creates the parent Issue (Gate 1 precondition)
- `kata-load-plan-from-subissue` — materializes local cache from the canonical sub-issue body
- `kata-flush-plan-to-subissue` — flushes local cache (filtering `<!-- not-flushed -->`) to the sub-issue body
- `kata-session-heartbeat` — Claude Code session heartbeat update
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — transition owners
