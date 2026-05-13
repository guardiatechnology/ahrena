# Codex: Claude Code Session Tracking

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Recording the Claude Code session operating on each plan and the chain of sessions that touched each PR

## Overview

This Codex defines the heartbeat system that lets the framework track which Claude Code session is operating on each plan and which sequence of sessions produced each PR. Without it, Eunomia's plans digest cannot distinguish "plan in motion now" from "plan forgotten"; the PR body loses implementation-time audit; and handoffs between sessions become unexplained gaps in the history.

The contract is simple: every agent touching a plan executes `kata-session-heartbeat` at significant points, writing/updating `.ahrena/workflow/sessions/<session-id>.json`. The canonical persistence goes into the PR body ("Session Trace" section) via `kata-pr-prepare`; the local directory is runtime-only and gitignored.

## Context

- **Domain:** operational tracking of Claude Code sessions in the Issue-Driven flow.
- **Audience:** every agent operating on a plan (Eunomia on creation, Athena on transitions, Argos on review, Janus on release).
- **Update:** when the heartbeat schema changes or a new Claude Code environment variable is added.

## Content

### 1. Claude Code environment variables

Claude Code exposes three stable variables in every session. The agent reads and propagates:

| Variable | Content | Origin |
|---|---|---|
| `CLAUDE_CODE_SESSION_ID` | Stable session UUID (e.g.: `85846253-4edf-443d-b294-187ef287d1bb`) | Claude Code injects in the shell |
| `CLAUDE_CODE_ENTRYPOINT` | Where the session runs: `claude-vscode`, `claude-cli`, `claude-desktop`, `claude-web` | Same |
| `AI_AGENT` | Agent version (e.g.: `claude-code_2-1-138_agent`) | Same |

When the agent runs outside Claude Code (CI, Cursor without env), the variables are treated as absent and the heartbeat is skipped without error — `kata-session-heartbeat` is idempotent in that case.

### 2. Heartbeat file schema

Each session writes a JSON file at `.ahrena/workflow/sessions/<session-id>.json`:

```json
{
  "session_id": "85846253-4edf-443d-b294-187ef287d1bb",
  "entrypoint": "claude-vscode",
  "agent_version": "claude-code_2-1-138_agent",
  "plan_id": "043",
  "branch": "feat/90-workflow-status-review-loop",
  "cwd": "/Users/.../worktrees/90-workflow-status-review-loop",
  "started_at": "2026-05-11T12:30:00Z",
  "last_heartbeat": "2026-05-11T14:00:00Z",
  "last_activity": "kata-pr-prepare:step3",
  "role": "creator",
  "previous_session": null
}
```

| Field | Type | Description |
|---|---|---|
| `session_id` | UUID string | Value of `CLAUDE_CODE_SESSION_ID` |
| `entrypoint` | enum | Value of `CLAUDE_CODE_ENTRYPOINT` |
| `agent_version` | string | Value of `AI_AGENT` |
| `plan_id` | string `NNN` | Read from the active plan front-matter |
| `branch` | string | `git rev-parse --abbrev-ref HEAD` in the worktree |
| `cwd` | string | Current working directory |
| `started_at` | ISO 8601 | First heartbeat write |
| `last_heartbeat` | ISO 8601 | Latest update (overwritten on every call) |
| `last_activity` | string | Name of the current step/kata/cry (format `kata-name:stepN` or `cry-name`) |
| `role` | enum | `creator`, `executor`, `reviewer`, `releaser` (depends on who is writing) |
| `previous_session` | UUID or null | On handoff, points to the previous session |

### 3. Cadence

Heartbeat updated:

- **Start**: when the agent enters the plan (Eunomia on creation; Athena on handoff; Argos at review start; Janus at release start).
- **At significant points**: on completion of each plan Step, of each invoked kata, on status changes.
- **Minimum**: every 5–10 minutes of active work.
- **Stale threshold**: 30 min without heartbeat → Eunomia considers offline in the digest. Configurable via `session_tracking.stale_threshold_minutes`.

Idempotency: calling `kata-session-heartbeat` 100×/day is safe — it overwrites `last_heartbeat` and `last_activity` with no side effect.

### 4. Cleanup

- When moving the plan to `done` or `abandoned`: remove the session heartbeat file (no longer needed).
- When restarting a session with the same `session_id` (entrypoint detects pre-existing heartbeat): continue from the existing one, do not recreate.

### 5. Multi-session per plan (handoff)

When a session hands off to another (e.g.: session A started, session B continued):

1. Session B writes a new heartbeat with `previous_session: <session A UUID>`.
2. Session A's old heartbeat remains until cleaned up at the end of the cycle.
3. Eunomia's digest shows the chain: "session B (current, inherited from A)".

### 6. Gitignored directory

`.ahrena/workflow/sessions/` is runtime-only:

```gitignore
# .ahrena/workflow/sessions/ — runtime heartbeat dir (codex-session-tracking)
.ahrena/workflow/sessions/
```

The canonical history of sessions that touched a piece of work persists in the PR body ("Session Trace" section), not in the filesystem.

### 7. Session Trace in the PR body

`kata-pr-prepare` builds the "Session Trace" section by aggregating all heartbeat files whose `branch` matches the current branch:

```markdown
## Session Trace

| Session | Entrypoint | Role | Started | Last Heartbeat |
|---|---|---|---|---|
| `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |
| `abc12345` | claude-cli | reviewer (Argos) | 2026-05-11T13:45Z | 2026-05-11T13:55Z |

- Worktree: `.worktrees/90-workflow-status-review-loop`
- Cumulative active time: ~1h30min
```

**Cumulative active time** computation: sum of `started_at → last_heartbeat` intervals per session. This metric complements `cry-pr-cost-stamp` (which measures tokens/USD); here it measures actual session time.

PRs missing `Session Trace`, when the branch has associated heartbeat files, are rejected at Gate 2 (per `lex-pr-quality`).

### 8. Agent-less PRs (pure human)

In manual hotfixes or PRs made by a human without a Claude Code agent, the section may be:

```markdown
## Session Trace

_(human-driven; no session trace)_
```

Accepted at Gate 2.

## Restrictions

- **Do not persist credentials or sensitive data** in the heartbeat file — `cwd`, `branch`, `plan_id`, IDs, and timestamps are the boundary.
- **Do not commit the `.ahrena/workflow/sessions/` directory** — always gitignored.
- **Do not confuse `previous_session` with session merging** — handoff is sequential; there are no multiple sessions `running` simultaneously on the same plan.

## References

- `lex-agent-planning` — plan front-matter references `claude_session` + `session_entrypoint`
- `lex-pr-quality` — requires "Session Trace" section in the PR body
- `kata-session-heartbeat` — canonical operational procedure
- `kata-pr-prepare` — builds the "Session Trace" section before opening the PR
- `lex-directives` — `session_tracking.*` keys in `.ahrena/.directives`
- `codex-pr-cost-tracking` — cost metric (tokens/USD), complementary to the time metric here
