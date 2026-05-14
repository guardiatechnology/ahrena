# Codex: Session Checkpoint

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Operational use of `.checkpoint` complementary to `lex-checkpoint` and `lex-agent-planning`

## Overview

`.checkpoint` is a **session scratchpad** file located at the workspace root, gitignored, that captures working-window context that does NOT fit in a single plan. This Codex documents how `.checkpoint` relates to `lex-agent-planning`, when it is worth invoking, and how to debug inconsistencies.

The corresponding Law is `lex-checkpoint`. The operational procedures are `kata-checkpoint-read` (start of session) and `kata-checkpoint-save` (on demand + end of session). The user shortcut is `cry-checkpoint`.

## Context

- **Domain:** continuity of context across sessions with AI agents
- **Audience:** Warriors, Katas, generic agents, and human users invoking `cry-checkpoint`
- **Update:** when `lex-checkpoint` changes, or when the surrounding ecosystem of Katas/Cries evolves

## Content

### Principles

1. **Session, not task.** The plan (`lex-agent-planning`) is the source of truth for the task — committed, with Steps, Decisions, Risks. The checkpoint covers what does not fit in a single plan: working-window focus, hand-off between multiple active plans, parallel threads, free scratchpad.
2. **Slim, canonical schema.** 4 fixed sections (Session focus, Active plans, Open threads, Notes). Nothing beyond that — fields that would duplicate the plan (Activity, Progress, Decisions made, Next steps, Artifacts produced) are forbidden.
3. **Discrete triggers.** Read at start of session; save on user demand or when ending a session with context change. No auto-save per activity.
4. **Graceful degradation.** Missing `.checkpoint` is a valid scenario. Old schema produces a deprecation warning, not an error. Silent overwrite on the next save.

### When it is worth invoking

| Scenario | Action |
|---------|--------|
| Start of new conversation with an agent that has `.checkpoint` saved | `kata-checkpoint-read` (automatic at boot) |
| Exploratory conversation with no formal plan, with cross-cutting decisions | `cry-checkpoint` at the end to preserve Open threads and Notes |
| Multiple active plans in parallel within the session | `cry-checkpoint` to record Active plans with 1-line context |
| Long pause before resuming tomorrow | `cry-checkpoint` before closing |
| Simple task encapsulated in a single plan, without parallel threads | DO NOT invoke — the plan already covers everything |
| Plan change (closed plan-N, starting plan-M) | Update Active plans via `cry-checkpoint` |

### When NOT to use

- **To record formal task progress** — goes in the plan (`lex-agent-planning`)
- **To list produced artifacts** — `git diff` + plan cover this
- **To version architectural decisions** — ADR (`docs/adr/ADR-NNN-*.md`)
- **For active bug tracking** — GitHub Issue
- **For developer-to-developer handoff** — does not work; `.checkpoint` is gitignored and per-machine

### Patterns and Conventions

| Aspect | Pattern | Example |
|---------|--------|---------|
| File name | `.checkpoint` (dot-prefixed, no extension) | `.checkpoint` |
| Location | workspace root | `/path/to/repo/.checkpoint` |
| Encoding | UTF-8, LF line endings | — |
| Schema | 4 mandatory sections + 2-field frontmatter | See `lex-checkpoint` rule 3 |
| Active plans entries | `\`plan-{M}-{slug}\` — slug; 1-line context ≤ 80 chars` | `` `plan-040` — repositioning; drafting `` |
| Open threads entries | 1-2 lines as bullet | `- Evaluate absorption of Session risks` |
| Notes | free text, no schema | any markdown |
| Typical size | < 4 KB | — |

### Active Decisions

| Decision | Status | Origin |
|---------|--------|--------|
| Slim schema (4 sections) replaces old schema (8 fields) | Active | plan-040, issue #73 |
| Save on demand + end of session (not automatic per activity) | Active | plan-040 |
| No dedicated migration tool — read detects old schema, emits warning, save overwrites | Active | plan-040 |
| `Active plans` is an optional hint for other agents (e.g.: plan-026 observer); not a scope source | Active | plan-040 |

### Technical Restrictions

- `.checkpoint` is **per-machine, per-developer** — does not sync across machines, is not committed
- Writes are **last-write-wins** — multiple simultaneous agents compete for the file (rare scenario)
- Reading old schema is **silent reading** — does not attempt to parse or migrate; only emits warning and proceeds
- Size has no hard limit, but > 8 KB indicates plan content has leaked — audit

## Troubleshooting

### `.checkpoint` missing after several sessions

- **Probable cause:** the user never invoked `cry-checkpoint` and no session had context change outside the plan.
- **Action:** expected behavior. If there is context to preserve, invoke `cry-checkpoint`.

### `kata-checkpoint-read` emits an old-schema warning

- **Cause:** `.checkpoint` was written before the rewrite (issue #73).
- **Action:** `rm .checkpoint` or wait for the next save invocation (overwrites with new schema).

### Plan content appeared in checkpoint Notes

- **Cause:** the agent confused scopes.
- **Action:** move the content to `## Steps` or `## Closed decisions` of the corresponding plan; remove from Notes.

### `Active plans` grows indefinitely

- **Cause:** done plans were not removed from the list.
- **Action:** when closing a plan (status `done`), update `Active plans` removing the entry via `cry-checkpoint`.

### Inconsistent checkpoint across parallel sessions (same workspace)

- **Cause:** multiple Claude Code/Cursor agents writing simultaneously.
- **Action:** `.checkpoint` is per-workspace; parallel active sessions in the same workspace are rare. If it occurs, last-write-wins resolves — the user invokes `cry-checkpoint` in the session that holds the correct state to overwrite.

## Glossary

| Term | Definition |
|-------|-----------|
| Session focus | 1-3 sentences describing the focus of the current working window |
| Active plans | List of plan-IDs active in the session with 1-line context each |
| Open threads | Conversation threads that did not become a formal plan but should be resumed |
| Notes | Free scratchpad — text, links, reminders |
| Old schema | Pre-issue-#73 structure with Activity/Status/Progress/Decisions/Next steps/Artifacts produced |
| New schema | Canonical 4-section structure (Session focus, Active plans, Open threads, Notes) |

## References

- `lex-checkpoint` — Law that defines the schema and triggers
- `lex-agent-planning` — Plan Law (source of truth for the task)
- `kata-checkpoint-read` — read procedure at start of session
- `kata-checkpoint-save` — save procedure on demand + end of session
- `cry-checkpoint` — user shortcut for `kata-checkpoint-save`
- Issue #73 — `.checkpoint` repositioning
- Plan-040 — repositioning execution
