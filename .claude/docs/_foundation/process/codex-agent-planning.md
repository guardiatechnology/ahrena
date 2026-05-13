# Codex: Agent Task Planning

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creating, maintaining, and managing the lifecycle of agent task plans in the Ahrena context

## 1. Three-layer storage model (per ADR-002)

| Layer | Location | Role | Versioning |
|---|---|---|---|
| **Issue body** | `https://github.com/{owner}/{repo}/issues/{N}` | Canonical. Summary + Plan section (Objective, Steps, Risks, Dependencies, Open Questions) | GitHub-native audit log (timestamp + author per edit) |
| **`.plans/{N}.md`** | Repo root, gitignored | AI working memory + scratch. Superset of the Issue body + `<!-- not-flushed -->` blocks | Regenerable local cache |
| **`.ahrena/issues/{N}/`** | Repo root, committed | Phase artifacts (`01-brief.md` … `06-quality-report.md`) | Git |

### Local cache path resolution

```
1. Read .ahrena/.directives
2. If paths.plans exists → use that value
3. Otherwise → use default `.plans/` (repo root, gitignored)
```

Override example:
```yaml
# .ahrena/.directives
paths:
  plans: ".cache/ai-plans/"
```

> **Legacy model (pre-ADR-002, deprecated):** files `plan-{NNN}-{slug}.md` in `.claude/plans/` were migrated to `.ahrena/issues/_legacy/` in the plan-046 PR. Do not create new files in this format — the Issue body is now canonical; `.plans/{N}.md` is the local cache named by the Issue number.

---

## 2. Local cache naming

```
.plans/{N}.md
```

| Field | Rule |
|---|---|
| `{N}` | Number of the corresponding GitHub Issue. No padding, no prefix — `.plans/96.md`, not `.plans/plan-096.md` or `.plans/96-slug.md` |

Examples:
- `.plans/42.md` — cache of the plan for Issue #42
- `.plans/96.md` — cache of the plan for Issue #96
- `.plans/100.md` — cache of the plan for release Issue #100 (Axis B)

The cache is gitignored — it does not appear in `git status` nor in `git log`. To inspect plans without cloning:

```bash
gh issue view {N} --json body --jq .body
```

To sync locally: `kata-load-plan-from-issue {N}`.

---

## 3. Issue body template (canonical) and local cache

### 3a. Issue body (canonical per ADR-002)

```markdown
## Summary

**As** {user_role},
**I want** {specific_objective},
**So that** {benefit_and_value}.

(or free text 2-4 sentences describing the high-level objective)

## Plan

### Objective
Align the lifecycle of the plan and the GitHub Issue to a single
status enum (todo → development → to review → review → done for Axis A;
to release → release → done for Axis B), with an explicit owner for
each transition and provider-agnostic notifications via MCP.

### Steps
- [x] 1. Issue + branch + worktree (Eunomia or fallback)
- [x] 2. ADR-002 (simplified MADR)
- [x] 3. lex-agent-planning (pt-BR)
- [ ] 4. codex-agent-planning (pt-BR)
- [ ] 5. lex-issue-status split (pt-BR)
- ...

### Dependencies
- plan-043 (PR #93) — merged
- plan-044 (Eunomia) — absorbed by plan-046 Step 10
- plan-045 (Janus pointer) — absorbed by plan-046 Step 3.5

### Risks
- .plans/ lost on fresh clone — mitigated by kata-load-plan-from-issue
- Conflicting flush across sessions — drift preflight detects
- 3×15min loop may be short outside business hours — mitigate via .directives

### Open Questions
All resolved on 2026-05-11.
```

The Issue body is written by:
- `kata-plan-task` on initial creation (Step 5 of the `— → todo` HARD-GATE)
- `kata-flush-plan-to-issue` on each sync trigger (transition, completed Step, end of session)

### 3b. Local cache `.plans/{N}.md` (working memory)

```markdown
## Summary
... (mirrors the Issue body)

## Plan
... (mirrors the Issue body)

<!-- not-flushed -->
## Working notes
- 23:30 — finished Step 3
- Decision: use git mv to preserve history in Step 14

## Next actions
1. Step 4 — codex-agent-planning
2. Step 5 — path move
3. Step 17 — open draft PR

## Scratch
gh issue develop registers branch as "Development" in the sidebar.
Issue body limit: ~65KB (tested with plan-046).
<!-- /not-flushed -->
```

The cache **has no YAML front-matter** — the GitHub Issue already carries all metadata (assignees, `status:*` labels, milestones, dates). `<!-- not-flushed -->` blocks are filtered before flushing to the Issue.

> **Legacy front-matter:** plans in `.ahrena/issues/_legacy/` (pre-ADR-002) keep historical YAML front-matter (`plan_id`, `status`, `claude_session`, `merge_commit`, `closed_at`). This format is recognized for audit, but do NOT replicate it in new plans.

---

## 4. Lifecycle states (unified enum)

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (alternative terminal, at any stage)
```

| Status | When to use | Transitioning owner |
|---|---|---|
| `todo` | Plan created, Issue opened, remote branch linked, worktree ready, not yet started | Creator: `warrior-eunomia` (fallback: session agent) |
| `development` | Implementation in progress (Athena Phase 4) | `warrior-athena` |
| `to review` | PR opened, waiting for a reviewer to pick it up | `warrior-athena` (entry); `warrior-argos` (return from `review`) |
| `review` | Argos or human actively reviewing | `warrior-argos` (entry and exit) |
| `to release` | Review approved, waiting for release to start | `warrior-athena` (detects `APPROVED`) |
| `release` | Release in execution (tag/build/deploy) | `warrior-janus` |
| `done` | Release completed, PR merged, cycle closed | `warrior-janus` |
| `abandoned` | Plan discarded (any stage) | Creator or current owner |

**Canonical state per ADR-002:** the `status:` lives as a **label** on the GitHub Issue (and on the PR, starting at `to review`). There is no more "plan front-matter" — the Issue body is canonical; `.plans/{N}.md` is the regenerable cache. Legacy plans in `.ahrena/issues/_legacy/` keep historical front-matter for audit, without retrofit.

### Split into two axes (per ADR-002 / absorbed plan-045)

- **Axis A — Dev cycle** (feature/fix/chore Issues/PRs): `todo → development → to review → review → done` + `abandoned`. Owners: Eunomia/Athena/Argos.
- **Axis B — Release cycle** (release Issue exclusively): `to release → release → done` + `abandoned`. Owner: Janus.

Mutex is **intra-artifact** (within each Issue/PR), not cross-artifact. Applying an Axis B label to a feature Issue/PR (or vice versa) is forbidden per HARD-GATE in `lex-issue-status`.

---

## 5. Owners of each transition (flow view)

### Axis A — Dev cycle (Eunomia/Athena/Argos)

```
Eunomia: — ──→ todo                                                  [feature Issue + PR]
                 │
                 ▼
Athena:  todo ──→ development ──→ to review
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ done   (human approves; merge closes Issue)
                                       │
                  any ──→ abandoned (alternative terminal)
```

### Axis B — Release cycle (Janus)

```
Janus:   — ──→ to release ──→ release ──→ done                      [dedicated release Issue]
                  │
                  any ──→ abandoned (release aborted before tag)
```

Each owner simultaneously updates:

1. Issue body via `kata-flush-plan-to-issue` (canonical per ADR-002 — only if the local cache was edited).
2. `status: <name>` label on the GitHub Issue (per `lex-issue-status` intra-artifact mutex).
3. `status: <name>` label on the PR (starting at `to review`, only on Axis A).

---

## 6. Owner of `— → todo`: 5 canonical steps

Eunomia (or fallback) executes in sequence before marking `status: todo`:

| Step | Action | Reference Lex |
|---|---|---|
| 1 | Open Issue (template, label, type, assignee, Why/What/How) | `lex-issue-first`, `lex-issue-quality` |
| 2 | Verify Issue Type after creation | `lex-issue-type-verified` |
| 3 | Create remote branch and link to Issue: `gh issue develop {N} --base main --name {type}/{N}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 4 | Create worktree in `.worktrees/{N}-{slug}/` | `lex-git-worktrees` |
| 5 | Populate Issue body with the canonical plan (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) via MCP `update_issue` (preferred) or `gh issue edit --body-file` (fallback) | `lex-agent-planning`, `lex-mcp` |

Failure in any step leaves the plan as a draft (it cannot be presented as `todo`). Per HARD-GATE in `lex-agent-planning`, even in a hotfix the 5 steps are mandatory.

---

## 7. When a plan is mandatory (and when it is not)

### Mandatory

- Task with 2+ chained steps
- Any operation that touches 2+ files
- Every warrior or cry invocation (multi-step by definition)
- Any task that produces permanent artifacts (files, commits, PRs, posts)

### Not mandatory (trivial single step)

- Editing a single file with a direct and precise instruction
- Reading/consulting files without writing
- Executing a single isolated command without permanent side effects
- Answering a factual question

### Gray zone — use a plan as a precaution

- An apparently simple task that may branch out (e.g., "fix the bug" without knowing the scope)
- An irreversible operation even if single-step (e.g., deleting files)

---

## 8. Relationship between plans and other artifacts

```
GitHub Issue                                    canonical (per ADR-002)
    ├── body: canonical plan (Summary + Plan)
    ├── label: status: <name> (Axis A or Axis B)
    │
    ├── PR (label: status: <name>, starting at "to review")        [Axis A only]
    │
    ├── .plans/{N}.md (gitignored)                                  AI's local cache
    │   └── superset of body + <!-- not-flushed --> blocks
    │
    ├── .ahrena/issues/{N}/ (committed)                                    Phase artifacts
    │   ├── 01-brief.md
    │   ├── 02-requirements.md
    │   ├── 03-architecture.md
    │   ├── 05-security-review.md
    │   └── 06-quality-report.md
    │
    ├── docs/adr/ADR-{n}-*.md (committed)                           if architectural decision
    │
    ├── Session heartbeat (.ahrena/workflow/sessions/<uuid>.json, gitignored)
    │
    └── ─ ─ ─ do not confuse with ─ ─ ─
        Checkpoint (.checkpoint — gitignored, session)
```

- Issue body, Issue label, and PR label are synchronized by the owner at every transition.
- ADR is opened when the plan identifies a relevant architectural decision (lives in `docs/adr/`, not `.ahrena/issues/`).
- Session heartbeat (`codex-session-tracking`) records which Claude Code session is currently operating on the plan.
- Checkpoint is NOT subordinate to the plan; it is a parallel **session** artifact, not a **task** one.

### Plan vs `.checkpoint` — canonical boundary

The plan covers **task**: Objective, Scope, Steps `[x]`, Closed decisions, Risks, Verification. Committed.
The checkpoint covers **session**: Session focus, Active plans (pointers), Open threads, Notes. Gitignored.

| Content | Issue body (canonical plan) | `.plans/{N}.md` (cache + scratch) | `.checkpoint` (session) |
|---|:---:|:---:|:---:|
| Steps `[x]` | ✅ | ✅ (mirrored) | ❌ |
| Closed decisions of the task | ✅ (or ADR) | ✅ (mirrored) | ❌ |
| Task risks | ✅ | ✅ (mirrored) | ❌ |
| Working notes / debugging diary | ❌ | ✅ (`<!-- not-flushed -->` block) | ❌ |
| Overall focus of the work window | ❌ | ❌ | ✅ |
| List of active plans in the session | ❌ | ❌ | ✅ |
| Parallel threads that have not become a plan | ❌ | ❌ | ✅ |
| Free scratchpad, links, reminders | ❌ | ❌ | ✅ |

If content repeats in both, there is overlap — plan wins (committed). Overlap is FORBIDDEN by `lex-checkpoint` rule 5 and by `lex-agent-planning`.

---

## 9. Load/flush cadence (per ADR-002)

Synchronization between the Issue body (canonical) and the local cache `.plans/{N}.md` happens at **3 canonical triggers** (per plan-046 Open Question #3):

| Trigger | Operation | Who triggers |
|---|---|---|
| Session start / handoff between agents | `kata-load-plan-from-issue` | Athena, Argos, Janus (at the start of each work session on a plan) |
| `status:` label transition on the Issue/PR | `kata-flush-plan-to-issue` | Eunomia, Athena, Argos, Janus (at the moment of the transition) |
| Plan step marked complete (`[ ]` → `[x]`) | `kata-flush-plan-to-issue` | Agent that completes the Step |
| Session end (heartbeat finishes or agent exits) | `kata-flush-plan-to-issue` | `kata-session-heartbeat` on shutdown |

Intermediate toggles, scratch edits (`<!-- not-flushed -->` blocks), and working notes are **free** — they do not trigger a flush. The rule is: the Issue body must reflect the **stable** state (between transitions and Steps), not the **transient** state (during work).

### Typical work session flow

```
1. Athena enters (receives handoff from Eunomia):
   → kata-load-plan-from-issue {N}    (materializes .plans/{N}.md)
   → applies status: development label on the Issue + PR
   → kata-flush-plan-to-issue {N}     (records the transition)

2. Athena works:
   → edits files
   → records notes in .plans/{N}.md (<!-- not-flushed --> blocks)
   → marks Step [x] in .plans/{N}.md
   → kata-flush-plan-to-issue {N}     (Step completed)

3. Athena opens PR via kata-pr-prepare:
   → Step 5c: kata-flush-plan-to-issue {N}  (final state pre-PR)
   → Step 6: create_pull_request
   → Step 6b: applies status: to review on Issue + PR
   → kata-flush-plan-to-issue {N}     (transition recorded)

4. Athena exits:
   → kata-session-heartbeat on shutdown triggers
   → kata-flush-plan-to-issue {N}     (final cleanup)

5. Argos enters:
   → kata-load-plan-from-issue {N}    (refresh local cache)
   → ...
```

### Remote drift detection (preflight)

`kata-flush-plan-to-issue` by default runs a preflight: it reads the current Issue body, compares it with the last known state, and blocks if there is an unknown remote edit (another session, edit via the GitHub UI). It offers: (a) show diff and abort, (b) manual merge, (c) overwrite via `force=true`. The session heartbeat enables identifying the concurrent session.

---

## 10. Pending review loop (state `to review`)

After Athena opens the PR (Step 6/6b of `kata-pr-prepare`), the review cycle operates in **two distinct sequential phases** plus a handler for CHANGES_REQUESTED:

### Phase A — Argos pre-flight cycles (Step 6c of `kata-pr-prepare`)

Up to 3 interactive cycles `A1, A2, A3`, gated by `AskUserQuestion` (Athena never invokes Argos without confirmation). Each cycle: Athena asks "Run an Argos review on the current HEAD?" — options (a) yes, (b) skip to human review, (c) stop. If (a) → Argos runs, posts review with an idempotent marker; Athena reads findings; P0 BLOCKER addressing is mandatory; P1 AskUserQuestion (address or defer); P2 note. Commit + push if there were changes → new HEAD. Repeat until A3 or user picks (b)/(c). Full detail in `kata-pr-prepare` Step 6c.

### Phase B — Human nudge loop (Step 6d of `kata-pr-prepare`)

After Phase A ends, Athena asks for the scheduling mode: (a) `/loop` in the session (`ScheduleWakeup`), (b) remote cron, (c) manual. Modes (a)/(b) schedule 3 cycles `H1, H2, H3` with 15 min between each. At every cycle, Athena fires a Slack notification via MCP on `notifications.channels.pr_review_timeout` — message escalates in urgency (H1 "PR ready", H2 "reminder #1", H3 "reminder #2, 2nd nudge"). Queries `gh pr view {N} --json reviewDecision,mergedAt`:

- `mergedAt != null` → transition `status: to review → done`, capture `mergeCommit.oid`, close the loop.
- `reviewDecision == APPROVED` (no merge) → comment "PR approved, awaiting merge", close the loop.
- `reviewDecision == CHANGES_REQUESTED` → **trigger Phase C**.
- Otherwise → if H<3, reschedule; if H==3, close silently.

### Phase C — CHANGES_REQUESTED handler (Step 6e of `kata-pr-prepare`)

If the human requests changes during Phase B: Athena reads the reviewer's comments and asks via AskUserQuestion: (a) address now, (b) defer to a follow-up Issue, (c) stop. If (a) → Athena implements, commits, pushes (new HEAD). After (a) or (b) → **full reset**: Athena restarts the loop from **Phase A** (3 new Argos cycles on the new HEAD) — because new commits invalidate the previous Argos review. Does not jump directly to Phase B. This handler ensures CHANGES_REQUESTED resets the full quality cycle, not only the human nudge loop. Detail in `kata-pr-prepare` Step 6e.

---

Argos operates the `to review ↔ review` sub-cycle in Phase A (with label transitions during execution) and in Phase C when re-invoked. Argos never moves to `done`; the `to review → done` transition is exclusive to Athena upon detecting merge.

---

## 11. Best practices

1. **Write the plan before knowing everything.** The goal is to make intent visible, not to produce perfect documentation. An imprecise plan that evolves is better than no plan.
2. **Keep steps atomic.** Each step must be verifiable: done or not done. Avoid vague steps such as "take care of the events part".
3. **Update in real time.** Mark `[x]` as each step completes, not at the end of everything — and trigger `kata-flush-plan-to-issue` to persist it.
4. **Sync `status:` label on Issue + PR.** Every owner transition touches the Issue and the PR. Skipping either produces drift that surfaces in audit.
5. **Do not create phantom plans.** If the task is cancelled before starting, apply `status: abandoned` on the Issue with a comment explaining — do not delete the Issue.
6. **Canonical plan lives on GitHub.** Do not create `.claude/plans/*.md` files as canonical (legacy pre-ADR-002 model). The Issue body is canonical; `.plans/{N}.md` is the regenerable cache; `.ahrena/issues/{N}/` carries the Phase artifacts.
7. **Free working notes in `.plans/{N}.md`.** Use `<!-- not-flushed -->` blocks to record draft decisions, debugging notes, and volatile next steps — these blocks are filtered on flush, so they do not pollute the canonical body.

---
