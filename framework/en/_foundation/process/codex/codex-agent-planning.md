# Codex: Agent Task Planning

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creating, maintaining, and managing the lifecycle of Plans in the Ahrena context

## Overview

This Codex is the canonical manual for agent task planning under the **Issue → Plan → PR** hierarchical model. It complements `lex-agent-planning` (the Law) with templates, fill-in examples, Top-down and Plan-first walkthroughs, load/flush cadence, transition owners, and guidelines for edge cases. Every agent that creates or maintains Plans MUST consult this Codex.

## Context

- **Domain:** discipline for executing tasks via AI agents
- **Audience:** all agents (Claude, Cursor, warriors, katas) and human reviewers
- **Update:** when the template, status enum, owner table, or sync cadence changes (ADR recommended for structural changes)

---

## 1. Hierarchical Issue → Plan → PR model

```
Issue (User Story | Bug | Tech Task)            ← problem, Why/What/How, AC
   │
   ├─ Plan sub-issue #M1 (Task)                  ← executable unit #1
   │     ├─ status: todo | development | to review | review | done
   │     ├─ branch: {type}/{M1}-{slug}
   │     └─ PR(s) that close this Plan
   │
   ├─ Plan sub-issue #M2 (Task)
   │     └─ ...
   │
   └─ Plan sub-issue #M3 (Task)
         └─ ...
```

| Layer | Location | Role | Versioning |
|---|---|---|---|
| **Parent Issue** | `https://github.com/{owner}/{repo}/issues/{N}` | Problem, AC, motivation. Has no branch of its own | GitHub audit log |
| **Plan sub-issue** | `https://github.com/{owner}/{repo}/issues/{M}`, sub-issue of #{N} | Canonical. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Carries branch and PR(s) | GitHub audit log |
| **Provider cache** | `.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`, gitignored | AI working memory + scratch. Superset of the body + `<!-- not-flushed -->` blocks. Named by sub-issue number | Regenerable local cache |
| **Phase artifacts** | `.ahrena/issues/issue-{N}/`, committed | `01-brief.md` … `06-quality-report.md` of the Issue-Driven flow (tied to the parent Issue) | Git |

### Resolving the local cache path

```
1. Determine the provider (Claude Code → .claude/plans/, Cursor → .cursor/plans/)
2. Name the file plan-{M}-{slug}.md, where {M} is the sub-issue number
3. Confirm via .gitignore that the provider's directory is excluded
```

> **Legacy model (deprecated):** files in `.claude/plans/` **without a corresponding Plan sub-issue on GitHub** are considered zombies (regardless of the filename pattern — the new canonical `plan-{M}-{slug}.md` always maps 1:1 with `{M}` = the sub-issue number). Do not create new files without an open Plan sub-issue in GitHub. Existing caches that do not map to a sub-issue must be triaged into `.ahrena/issues/_legacy/` or discarded.

---

## 2. Local cache naming

```
.claude/plans/plan-{M}-{slug}.md      (Claude agent)
.cursor/plans/plan-{M}-{slug}.md      (Cursor agent)
```

| Field | Rule |
|---|---|
| `{M}` | GitHub Plan sub-issue number. No padding, no prefix — `plan-201.md`, not `plan-0201.md` nor `plan-201-slug.md` |

Examples:
- `.claude/plans/plan-201.md` — cache for the Plan in sub-issue #201
- `.cursor/plans/plan-222.md` — cache for the Plan in sub-issue #222

The cache is gitignored — it does not appear in `git status` or `git log`. To inspect Plans without cloning:

```bash
gh issue view {M} --json body --jq .body
```

To sync locally: `kata-load-plan-from-subissue {M}`.

---

## 3. Plan sub-issue body template (canonical) and local cache

### 3a. Plan sub-issue body (canonical)

```markdown
## Summary

{2-4 sentences describing the executable objective of this Plan — typically
a slice of the parent Issue scope.}

Parent: #{N}

## Plan

### Objective
Refactor the Ledger aggregate for event sourcing — replace direct PostgreSQL
CRUD with an append-only event store + write-side projection.

### Steps
- [x] 1. Map current Ledger commands
- [x] 2. Model canonical events (LedgerEntryRecorded, LedgerEntryReversed)
- [ ] 3. Implement EventStore with optimistic concurrency
- [ ] 4. Migrate handlers to emit-only
- [ ] 5. Invariant tests (balance never negative)

### Dependencies
- Plan #202 (write-side projection) — can run in parallel
- Plan #203 (read-side) — blocked by this Plan

### Risks
- Migration of existing data — mitigated by shadow-write during cutover
- Optimistic concurrency under high contention — benchmark in staging first

### Open Questions
- None
```

The sub-issue body is written by:
- `kata-decompose-issue-into-plans` at creation (downstream of the parent Issue)
- `kata-plan-task` when the Plan is standalone (top-level linked to an existing Issue)
- `kata-flush-plan-to-subissue` at every sync trigger (transition, completed Step, session end)

### 3b. Local cache `.claude/plans/plan-{M}-{slug}.md` (working memory)

```markdown
## Summary
... (mirrors the sub-issue body)

## Plan
... (mirrors the sub-issue body)

<!-- not-flushed -->
## Working notes
- 23:30 — finished Step 2; events modeled in src/ledger/events.py
- Decision: use UUID v7 as event_id (per lex-entities)
- Bug found in EventStore: retry without idempotency key — write test
  reproducing before fixing

## Next actions
1. Step 3 — EventStore with optimistic concurrency
2. Step 4 — emit-only handlers
3. Step 5 — invariant tests

## Scratch
gh issue develop registers the branch as "Development" in the sidebar.
Issue body limit: ~65KB.
<!-- /not-flushed -->
```

The cache has **no YAML front-matter** — the GitHub sub-issue already carries all metadata (assignees, `status:*` labels, milestones, dates). `<!-- not-flushed -->` blocks are filtered before flushing to the sub-issue.

> **Legacy front-matter:** files in `.ahrena/issues/_legacy/` (deprecated) retain historical YAML front-matter (`plan_id`, `status`, `claude_session`, `merge_commit`, `closed_at`). That format is recognized for audit, but DO NOT replicate it in new Plans.

---

## 4. Lifecycle states (unified enum)

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (alternate terminal, any stage)
```

| Status | When to use | Transitioning owner |
|---|---|---|
| `todo` | Plan sub-issue created with canonical body, no branch nor worktree, not started yet | Creator: `warrior-eunomia` (fallback: session agent) |
| `development` | Implementation in progress (Athena Phase 4); branch + worktree + assignee applied | `warrior-athena` |
| `to review` | PR open, waiting for a reviewer | `warrior-athena` (entry); `warrior-argos` (return from `review`) |
| `review` | Argos or human actively reviewing | `warrior-argos` (entry and exit) |
| `to release` | (Axis B only) Release sub-issue created, waiting to start | `warrior-janus` |
| `release` | (Axis B only) Release in execution (tag/build/publish) | `warrior-janus` |
| `done` | PR merged and Plan sub-issue closed via `Closes #{M}` (Axis A) OR release published (Axis B) | `warrior-athena` (Axis A) / `warrior-janus` (Axis B) |
| `abandoned` | Plan discarded (any stage) | Creator or current owner |

**Canonical state:** `status:` lives as a **label** on the Plan sub-issue on GitHub (and on the PR, starting at `to review`). There is no "Plan front-matter" — the sub-issue body is canonical; the local cache is regenerable.

### Split into two axes

- **Axis A — Dev cycle** (Plan derived from User Story / Bug / Tech Task): `todo → development → to review → review → done` + `abandoned`. Owners: Eunomia/Athena/Argos.
- **Axis B — Release cycle** (release sub-issue exclusively): `to release → release → done` + `abandoned`. Owner: Janus.

Mutex is **intra-artifact** (within each sub-issue/PR), not cross-artifact. Applying an Axis B label on a feature sub-issue (or vice versa) is forbidden per the HARD-GATE in `lex-issue-status`.

---

## 5. Transition owners (flow view)

### Axis A — Dev cycle (Eunomia/Athena/Argos)

```
Eunomia: — ──→ todo                                                  [Plan sub-issue created]
                 │
                 ▼
Athena:  todo ──→ development ──→ to review                          [branch + worktree + assignee]
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ done   (human approves; merge closes sub-issue)
                                       │
                  any ──→ abandoned (alternate terminal)
```

### Axis B — Release cycle (Janus)

```
Janus:   — ──→ to release ──→ release ──→ done                      [dedicated release sub-issue]
                  │
                  any ──→ abandoned (release aborted before tag)
```

Each owner simultaneously updates:

1. Plan sub-issue body via `kata-flush-plan-to-subissue` (only if there were edits in the local cache).
2. `status: <name>` label on the Plan sub-issue (per `lex-issue-status` intra-artifact mutex).
3. `status: <name>` label on the PR (starting at `to review`, Axis A only).

---

## 6. Walkthrough A — Top-down (parent Issue exists)

Scenario: the user points at an existing parent Issue and asks to decompose it into executable Plans.

### Step 1 — Verify the parent Issue

```bash
gh issue view 200 --repo {owner}/{repo} --json title,body,labels,issueType
```

Confirm: Issue Type `Feature` (or `Bug`/`Task`), template used, numbered AC, required labels, Why/What/How populated. If something is missing, invoke `kata-contributing-issue` to complete it first.

### Step 2 — Decompose into Plan sub-issues

```bash
# Eunomia invokes kata-decompose-issue-into-plans
# Reads the parent Issue, proposes N Plan sub-issues, confirms with the user,
# creates each sub-issue via MCP create_issue (Issue Type Task) linked to
# the parent, fills canonical body (Summary + Plan), applies required labels,
# verifies Issue Type, applies status: todo
```

Typical result:

```
Issue #200 (Feature) — "Event sourcing for ledger"
├── #201 (Task)   — "Refactor Ledger aggregate"
├── #202 (Task)   — "Implement projection write-side"
└── #203 (Task)   — "Migrate read-side via projection"
```

### Step 3 — Eunomia applies `status: todo` on the 3 sub-issues (Gate 1 OK)

Each sub-issue now has canonical body, Issue Type `Task`, required labels. Branch, worktree, assignee have NOT been applied — they belong to Athena at Gate 2.

### Step 4 — Athena picks the first executable Plan (#201)

```bash
# Gate 2 — todo → development
gh issue develop 201 --base main --name refactor/201-ledger-event-sourcing
git worktree add .worktrees/201-ledger-event-sourcing refactor/201-ledger-event-sourcing
gh issue edit 201 --add-assignee fernandoseguim
gh issue edit 201 --add-label "status: development" --remove-label "status: todo"
```

### Step 5 — Load local cache and execute

```bash
kata-load-plan-from-subissue 201   # materializes .claude/plans/plan-201.md
# implementation runs in the worktree
# on each completed Step: kata-flush-plan-to-subissue 201
# on session end: kata-flush-plan-to-subissue 201
```

### Step 6 — Open PR

```bash
# Athena via kata-pr-prepare:
# - kata-flush-plan-to-subissue 201 (final flush)
# - gh pr create --title "..." --body "Closes #201\nRefs #200" ...
# - applies status: to review on sub-issue #201 + PR
```

### Step 7 — Review and merge

Argos enters (`status: review`), leaves (`status: to review`); human approves; merge closes sub-issue #201 via `Closes #201`; Athena applies `status: done`. Repeat for #202, #203. When the final PR closes parent Issue #200 (`Closes #200`), everything ends.

---

## 7. Walkthrough B — Plan-first (intent without a parent Issue)

Scenario: the user says "let's plan the migration of the logger to Loguru" without referencing any Issue.

### Step 1 — Agent does NOT materialize a local file

Materializing `.claude/plans/plan-XXX.md` now would violate the plan-first guardrail in `lex-agent-planning`. The agent pauses and follows the canonical sequence.

### Step 2 — Create the parent Issue

```bash
# Agent invokes kata-contributing-issue
# Asks type: User Story, Bug, or Tech Task?
# User picks Tech Task (internal refactor without user-facing AC)
# Issue #220 created with tech-task template, Issue Type Task,
# Why/What/How populated, required labels, status: todo
```

### Step 3 — Decompose into Plans

```bash
# Eunomia invokes kata-decompose-issue-into-plans 220
# Proposes 2 sub-issues:
#   #221 (Task) — "Migrate framework code to loguru"
#   #222 (Task) — "Migrate tooling and scripts to loguru"
# Confirms with the user; creates sub-issues; fills canonical body;
# applies status: todo on both
```

### Step 4 — From here, it is Walkthrough A

Athena picks #221, executes Gate 2 (`todo → development`), implements, opens a PR, etc.

The difference between Walkthrough A and B is only the initial step. Once parent Issue + Plan sub-issues exist on GitHub, the flow converges.

---

## 8. Gate 1 — full checklist (`— → todo`)

Eunomia (or fallback) executes in sequence before marking `status: todo`:

| Step | Action | Reference Lex |
|---|---|---|
| 1 | Confirm parent Issue open and compliant | `lex-issue-first`, `lex-issue-quality` |
| 2 | Create Plan sub-issue linked to parent via MCP `create_issue` (preferred) or `gh issue create --type Task` (fallback) | `lex-mcp` |
| 3 | Fill sub-issue body with Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions) via MCP `update_issue` or `gh issue edit --body-file` | `lex-agent-planning` |
| 4 | Verify Issue Type post-creation (must be `Task`) | `lex-issue-type-verified` |

Branch, worktree, and assignee are NOT preconditions of this gate.

## 9. Gate 2 — full checklist (`todo → development`)

Athena executes in sequence before marking `status: development`:

| Step | Action | Reference Lex |
|---|---|---|
| 1 | Create remote branch and link to sub-issue: `gh issue develop {M} --base main --name {type}/{M}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 2 | Create worktree at `.worktrees/{M}-{slug}/` per `lex-git-worktrees` | `lex-git-worktrees` |
| 3 | Apply assignee on Plan sub-issue (human or agent identity that commits to execute) | `lex-issue-quality` |

Applying `status: development` without all 3 steps is FORBIDDEN.

---

## 10. When a Plan is required (and when it is not)

### Required

- Task with 2+ chained steps
- Any operation that touches 2+ files
- Every invocation of a warrior or cry (multi-step by definition)
- Any task that produces permanent artifacts (files, commits, PRs, posts)

### Not required (trivial single step)

- Editing a single file with a direct, precise instruction
- Reading/inspecting files without writing
- Running a single isolated command with no permanent side effect
- Answering a factual question

### Gray zone — use a Plan as a precaution

- Apparently simple task that may branch out (e.g., "fix the bug" without knowing scope)
- Irreversible operation even if single-step (e.g., deleting files)

---

## 11. Relationship between Plans and other artifacts

```
Parent Issue (#N) — User Story | Bug | Tech Task
    │
    ├── label: status: <name> (Axis A or Axis B on the release sub-issue)
    │
    ├── Plan sub-issues (#M1, #M2, ..., Task)              canonical for each unit
    │   ├── body: Summary + Plan
    │   ├── label: status: <name>
    │   │
    │   ├── PR (label: status: <name>, starting at "to review")    [Axis A only]
    │   │
    │   ├── .claude/plans/plan-{M}-{slug}.md or .cursor/plans/plan-{M}-{slug}.md  local cache
    │   │   └── superset of body + <!-- not-flushed --> blocks      gitignored
    │   │
    │   └── docs/adr/ADR-{n}-*.md (committed)                       if architectural decision
    │
    ├── .ahrena/issues/issue-{N}/ (committed)                       Phase artifacts
    │   ├── 01-brief.md
    │   ├── 02-requirements.md
    │   ├── 03-architecture.md
    │   ├── 05-security-review.md
    │   └── 06-quality-report.md
    │
    ├── Session heartbeat (.ahrena/workflow/sessions/<uuid>.json, gitignored)
    │
    └── ─ ─ ─ not to be confused with ─ ─ ─
        Checkpoint (.checkpoint — gitignored, session)
```

- Plan sub-issue body, sub-issue label, and PR label are kept in sync by the owner at every transition.
- ADR is opened when the Plan identifies a relevant architectural decision (lives in `docs/adr/`, not in `.ahrena/issues/`). Example filenames: `ADR-008-use-event-sourcing-for-refund-audit-trail.md`, `ADR-007-use-fastapi-routers.md`, `ADR-001-use-event-sourcing-for-ledger.md`, `ADR-002-migrate-to-fastapi.md`.
- Session heartbeat (`codex-session-tracking`) records which Claude Code session is operating on the Plan right now.
- Checkpoint is NOT subordinate to the Plan; it is a parallel **session** artifact, not a **task** artifact.

### Plan vs `.checkpoint` — canonical delimitation

The Plan covers **task**: Objective, Scope, Steps `[x]`, Closed decisions, Risks, Verification. Lives in GitHub.
The checkpoint covers **session**: Session focus, Active plans (pointers), Open threads, Notes. Gitignored.

| Content | Plan sub-issue body (canonical) | Local cache (working memory) | `.checkpoint` (session) |
|---|:---:|:---:|:---:|
| Steps `[x]` | ✅ | ✅ (mirrored) | ❌ |
| Closed task decisions | ✅ (or ADR) | ✅ (mirrored) | ❌ |
| Task risks | ✅ | ✅ (mirrored) | ❌ |
| Working notes / debugging diary | ❌ | ✅ (`<!-- not-flushed -->` block) | ❌ |
| General work-window focus | ❌ | ❌ | ✅ |
| List of active Plans in the session | ❌ | ❌ | ✅ |
| Parallel threads that did not become Plans | ❌ | ❌ | ✅ |
| Free scratchpad, links, reminders | ❌ | ❌ | ✅ |

If content repeats in both, there is overlap — Plan wins (canonical). Overlap is FORBIDDEN per `lex-checkpoint` rule 5 and per `lex-agent-planning`.

---

## 12. Load/flush cadence

Sync between the Plan sub-issue body (canonical) and the local cache occurs at **4 canonical triggers**:

| Trigger | Operation | Who triggers |
|---|---|---|
| Session start / handoff between agents | `kata-load-plan-from-subissue` | Athena, Argos, Janus (at the start of each work session on a Plan) |
| `status:` label transition on sub-issue/PR | `kata-flush-plan-to-subissue` | Eunomia, Athena, Argos, Janus (at the moment of transition) |
| Plan step marked complete (`[ ]` → `[x]`) | `kata-flush-plan-to-subissue` | Agent that completes the Step |
| Session end (heartbeat ends or agent leaves) | `kata-flush-plan-to-subissue` | `kata-session-heartbeat` on shutdown |

Intermediate toggles, scratch edits (`<!-- not-flushed -->` blocks), and working notes are **free** — they do not trigger a flush. The rule is: the sub-issue body must reflect the **stable** state (between transitions and Steps), not the **transient** state (during working).

### Typical work session flow

```
1. Athena enters (receives handoff from Eunomia):
   → kata-load-plan-from-subissue {M}    (materializes local cache)
   → Gate 2: gh issue develop + worktree + assignee
   → applies status: development label on the sub-issue + PR (if it exists)
   → kata-flush-plan-to-subissue {M}     (records the transition)

2. Athena works:
   → edits files in the worktree
   → records notes in the local cache (`<!-- not-flushed -->` blocks)
   → marks Step [x] in the cache
   → kata-flush-plan-to-subissue {M}     (completed Step)

3. Athena opens PR via kata-pr-prepare:
   → final flush of the cache before PR
   → create_pull_request (Closes #{M}, Refs #{N})
   → applies status: to review on sub-issue + PR
   → kata-flush-plan-to-subissue {M}     (transition recorded)

4. Athena leaves:
   → kata-session-heartbeat on shutdown triggers
   → kata-flush-plan-to-subissue {M}     (final cleanup)

5. Argos enters:
   → kata-load-plan-from-subissue {M}    (refresh local cache)
   → ...
```

### Remote drift detection (preflight)

`kata-flush-plan-to-subissue` runs a preflight by default: reads the current sub-issue body, compares against the last known state, and blocks if there is an unknown remote edit (another session, GitHub UI edit). Offers: (a) show diff and abort, (b) manual merge, (c) overwrite via `force=true`. The session heartbeat allows identifying the concurrent session.

---

## 13. Pending review loop (state `to review`)

After Athena opens the PR, the review cycle operates in **two distinct sequential phases** + a handler for CHANGES_REQUESTED:

### Phase A — Argos pre-flight cycles

Up to 3 interactive cycles `A1, A2, A3`, gated by `AskUserQuestion` (Athena never invokes Argos without confirmation). Each cycle: Athena asks "Run Argos review on the current HEAD?" — options (a) yes, (b) skip to human review, (c) stop. If (a) → Argos runs, publishes review with an idempotent marker; Athena reads findings; P0 BLOCKER address mandatory; P1 AskUserQuestion (address or defer); P2 note. Commit + push if changes happened → new HEAD. Repeat until A3 or the user picks (b)/(c).

### Phase B — Human nudge loop

After Phase A ends, Athena asks the scheduling mode: (a) `/loop` in the session, (b) remote cron, (c) manual. Modes (a)/(b) schedule 3 cycles `H1, H2, H3` 15 minutes apart. At each cycle, Athena fires a notification via MCP at `notifications.channels.pr_review_timeout` — the message escalates in urgency (H1 "PR ready", H2 "reminder #1", H3 "reminder #2, 2nd nudge"). Queries `gh pr view {N} --json reviewDecision,mergedAt`:

- `mergedAt != null` → transition `status: to review → done`, captures `mergeCommit.oid`, ends loop.
- `reviewDecision == APPROVED` (no merge) → comments "PR approved, awaiting merge", ends loop.
- `reviewDecision == CHANGES_REQUESTED` → **triggers Phase C**.
- Otherwise → if H<3, reschedule; if H==3, end silently.

### Phase C — CHANGES_REQUESTED handler

If a human requests changes during Phase B: Athena reads the reviewer's comments and asks via AskUserQuestion: (a) address now, (b) defer to follow-up Issue, (c) stop. If (a) → Athena implements, commits, pushes (new HEAD). After (a) or (b) → **full reset**: Athena reschedules the loop starting from **Phase A** (3 new Argos cycles on the new HEAD) — because new commits invalidate the previous Argos review. It does not skip straight to Phase B.

Argos operates the sub-cycle `to review ↔ review` during Phase A (with label change during execution) and during Phase C when re-invoked. Argos never moves to `done`; the `to review → done` transition is exclusive to Athena upon detecting merge.

---

## 14. Best practices

1. **Write the Plan before knowing everything.** The goal is to make intent visible, not to produce perfect documentation. An imprecise Plan that evolves is better than no Plan.
2. **Keep Steps atomic.** Each Step must be verifiable: done or not done. Avoid vague Steps like "handle the events part."
3. **Update in real time.** Mark `[x]` as each Step completes, not at the end of everything — and trigger `kata-flush-plan-to-subissue` to persist.
4. **Sync `status:` label on sub-issue + PR.** Every owner transition touches the Plan sub-issue and the PR. Skipping either produces drift that surfaces in audit.
5. **Do not create phantom Plans.** If the task is cancelled before it starts, apply `status: abandoned` on the sub-issue with a comment explaining why — do not delete the sub-issue.
6. **Canonical Plan lives on GitHub.** Do not create `.claude/plans/*.md` or `.cursor/plans/*.md` files as canonical. The sub-issue body is canonical; the local cache is regenerable; `.ahrena/issues/issue-{N}/` carries Phase artifacts.
7. **Free working notes in the local cache.** Use `<!-- not-flushed -->` blocks to record draft decisions, debugging notes, and volatile next steps — those blocks are filtered on flush, so they do not pollute the canonical body.
8. **Decomposition is part of planning.** Before picking up a large Issue, decompose it into Plan sub-issues via `kata-decompose-issue-into-plans`. A single giant Plan covering an entire Feature is an antipattern — break it into executable units.

---

## References

- `lex-agent-planning` — corresponding Law (Gate 1 of `— → todo` + Gate 2 of `todo → development` + Tables A and B)
- `lex-issue-status` — canonical status labels; split Axis A (dev) + Axis B (release)
- `lex-issue-type-verified` — programmatic verification of Issue Type
- `lex-issue-first`, `lex-issue-quality` — preconditions for creating parent Issue and Plan sub-issues
- `lex-git-branches`, `lex-git-worktrees` — Gate 2 preconditions
- `lex-mcp` — MCP preference + CLI fallback
- `kata-contributing-issue` — creates the parent Issue (Gate 1 precondition)
- `kata-decompose-issue-into-plans` — decomposes a parent Issue into Plan sub-issues
- `kata-plan-task` — creates a standalone top-level Plan linked to an existing Issue
- `kata-load-plan-from-subissue` — materializes local cache from canonical sub-issue body
- `kata-flush-plan-to-subissue` — flushes local cache (filtering scratch) to the sub-issue body
- `kata-session-heartbeat` — Claude Code session heartbeat
- `codex-session-tracking` — session tracking manual
- `codex-notifications` — provider-agnostic notification manual via MCP
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — transition owners
- `lex-checkpoint` — session state tracking (complementary)
- `lex-issue-driven` — Athena's Issue-Driven flow
