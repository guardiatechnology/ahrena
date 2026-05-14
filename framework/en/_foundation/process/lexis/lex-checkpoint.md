# Lexis: Session Checkpoint

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Session context between conversations with AI agents, complementary to `lex-agent-planning`

## Purpose

Sessions with AI agents are ephemeral — when they end, the context accumulated outside the plan (parallel threads, pre-plan scratchpad, hand-off between multiple active plans, resumption notes) is lost. `lex-agent-planning` covers the source of truth for the **task** (committed, with `[x]` Steps, closed Decisions, Risks). The checkpoint covers the **session** — what does not fit in a single plan.

This Lexis exists to ensure that **session context outside the plan** remains recoverable across conversations, without duplicating what the plan already records. The checkpoint is a working-window scratchpad, not a plan duplicate.

## Law

> **Every agent MUST check the `.checkpoint` file when starting a session and MUST save the checkpoint on user demand or when ending the session if context changed. The content of `.checkpoint` MUST follow the canonical schema (Session focus, Active plans, Open threads, Notes) and MUST NOT duplicate what lives in the plan (Activity, Steps, closed Decisions, Risks, Artifacts). Overlap with `lex-agent-planning` is FORBIDDEN.**

## Rules

### 1. Mandatory check at start

When starting a session, the agent **MUST**:

1. Check whether a `.checkpoint` file exists at the workspace root.
2. If it exists and follows the new schema (4 canonical sections): read it and present a summary to the user (Session focus + Active plans + Open threads).
3. If it exists and follows the old schema (Activity/Status/Progress/Decisions made/Next steps/Artifacts produced): emit a deprecation warning, proceed as if no checkpoint were present, and mark for overwrite on the next save invocation.
4. Ask the user whether to **resume** the saved context or **start a new window** (discarding the previous checkpoint).
5. If it does not exist, proceed normally. The absence of `.checkpoint` is a valid scenario — it is not a violation.

### 2. Save on demand + end of session

The agent **MUST** persist the checkpoint:

1. **On demand** — when the user invokes `cry-checkpoint` or explicitly requests it.
2. **When ending the session** — only if real context change occurred (new Session focus, new Active plan, new Open thread, new Notes). Ending a session without context change does NOT require a save.

The automatic obligation to save after each activity has been removed — activity granularity already lives in the plan (`lex-agent-planning`).

### 3. Canonical schema

The `.checkpoint` file **MUST** contain exactly the 4 sections below, in any order:

```markdown
# Session checkpoint

- **Last update:** YYYY-MM-DDTHH:MM:SSZ
- **Session id:** {chat/session id or HEAD commit short SHA}

## Session focus

{1-3 sentences describing the overall focus of the working window. This is not a formal Activity — it is the mental pointer that helps the agent reorient on resume. Example: "Repositioning lex-checkpoint in parallel with plan-026 review."}

## Active plans

{List of plan-IDs active in the session, with 1 line of context each. Do not duplicate plan content — only pointers.}

- `plan-026` — commit-readiness-observer; awaiting `.checkpoint` dependency adjustment
- `plan-040` — `.checkpoint` repositioning; drafting pt-BR artifacts

## Open threads

{Conversation threads that did not become a formal plan but should be resumed. Each thread in 1-2 lines. Covers what escapes a single plan — pending cross-cutting decisions, parallel ideas worth returning to.}

- Evaluate whether `lex-agent-planning` should absorb "Session risks" as a non-blocking category
- Decide whether Brand-related cries should live in `_foundation` or in `design/`

## Notes

{Free text. Thoughts, links, references, snippets, reminders. No required schema. Pure scratchpad.}
```

The fields `Activity`, `Status`, `Progress`, `Decisions made`, `Next steps`, `Artifacts produced` (from the old schema) **MUST NOT** appear in the new checkpoint — that content lives in the plan (`lex-agent-planning`).

### 4. Shared responsibility

- Any agent (Warrior) acting in the session **inherits** this obligation.
- The checkpoint is **discipline-agnostic** — it applies to sessions in any Clade.
- The `.checkpoint` file **MUST NOT** be committed to the repository (it MUST be in `.gitignore`).

### 5. Relationship to `lex-agent-planning`

The delineation between plan and checkpoint is categorical:

| Content | Lives in |
|---|---|
| Objective, `[x]` Steps, Status (`pending → in-progress → done`), closed Decisions, Risks, Verification | Plan: Plan sub-issue on GitHub (canonical body) + provider cache `.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md` (gitignored, regenerable) |
| Activity, detailed Progress, Artifacts produced, Next steps of a task | Plan — sub-issue body on GitHub |
| Overall focus of the working window (Session focus) | Checkpoint — gitignored |
| Pointers to multiple active plans (Active plans) | Checkpoint — gitignored |
| Parallel threads that did not become a plan (Open threads) | Checkpoint — gitignored |
| Free scratchpad, links, reminders (Notes) | Checkpoint — gitignored |

When in doubt, content goes to the plan. The plan wins on durability (committed) and on scope (it covers the task; the checkpoint covers the session).

## Coverage

- **Applies to:** all sessions with AI agents in any Clade
- **Bound agents:** all Warriors and generic agents
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **Overlap with the plan:** if the checkpoint contains old-schema content (Activity, Progress, Artifacts produced), `kata-checkpoint-read` emits a warning and ignores the content — there is no real data loss because the source of truth is the plan.
2. **Loss of session context:** sessions without a checkpoint result in loss of Open threads and Notes; the plan remains intact.
3. **Remediation:** the agent overwrites the old `.checkpoint` on the next save invocation with the new schema. Content redundant with the plan is discarded.

## Examples

### Correct

```
Agent: I found a `.checkpoint` in the new schema:
  - Session focus: Repositioning lex-checkpoint in parallel with plan-026 review
  - Active plans: plan-026, plan-040
  - Open threads: 2 pending items

  Do you want to resume this context or start a new window?

User: Resume.

Agent: Continuing. Plan-040 was in pt-BR artifact drafting.
        Pending open threads:
          1. Evaluate absorption of "Session risks" in lex-agent-planning
          2. Decide the clade for Brand-related cries
        I can proceed with plan-040 or address one of the threads first?
```

### Incorrect

```
Agent: I found a `.checkpoint`:
  ## Activity: Implementation of module X
  ## Progress: [x] step 1 [ ] step 2
  ## Artifacts produced: app/foo.py, tests/test_foo.py

# ❌ Old schema. Content already lives (or should live) in the plan.
# Agent MUST emit deprecation warning, ignore the content,
# and proceed as if no checkpoint were present.
```

```
# Checkpoint that duplicates plan — VIOLATES THE LAW
# .checkpoint
## Active plans
- plan-040

## Progress
- [x] Rewrite lex-checkpoint
- [ ] Rewrite codex-checkpoint

# ❌ Progress lives in the plan. The checkpoint only points (Active plans).
```

## Automated Validation

- **Tool:** `kata-checkpoint-read` validates the canonical schema on read; checkpoint lint in CI verifies that mandatory old-schema sections are absent (Activity, Progress, Artifacts produced)
- **Timing:** start of session (read) and save (on demand + end of session with change)
- **Metric:** 0 occurrences of old-schema sections in newly written `.checkpoint`; 100% of `.checkpoint` files conforming to the canonical schema
