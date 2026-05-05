---
paths:
  - '**/.checkpoint'
---

# Lexis: Session Checkpoint

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All work sessions with AI agents

## Law

> **Every agent MUST check the `.checkpoint` file before starting any activity and MUST save the checkpoint when concluding each activity or ending a session.**

## Rules

### 1. Mandatory check at start

Before starting any activity, the agent **MUST**:

1. Check whether a `.checkpoint` file exists at the workspace root.
2. If it exists, read its content and present the user with a summary of the saved context.
3. Ask the user whether to **resume** the saved activity or **start a new one** (discarding the previous checkpoint).
4. If it does not exist, proceed as usual.

### 2. Mandatory save on conclusion

When concluding an activity or ending a session, the agent **MUST**:

1. Ask the user their save preference (only the first time in the session):
   - **Automatic:** the checkpoint is saved automatically at the end of each activity, without asking again.
   - **Manual:** the agent asks before each save whether the user wants to save.
2. Respect the indicated preference for the rest of the session.
3. Persist the checkpoint to the `.checkpoint` file at the workspace root.

### 3. Checkpoint structure

The `.checkpoint` file MUST contain at least:

```markdown
# Checkpoint

- **Activity:** [brief description of the activity in progress]
- **Status:** [in progress | completed | blocked]
- **Date:** [date and time of save]
- **Session:** [session or chat identifier]

## Context

[Summary of what was discussed, decided, or produced]

## Progress

- [x] [completed step]
- [ ] [next pending step]

## Decisions made

- [decision 1]
- [decision 2]

## Next steps

1. [pending action]
2. [pending action]

## Artifacts produced

- [path/to/file-1]
- [path/to/file-2]
```

### 4. Shared responsibility

- Any agent (Warrior) acting in the session **inherits** this obligation.
- The checkpoint is **discipline-agnostic** — it applies to activities in any Clade.
- The `.checkpoint` file **MUST NOT** be committed to the repository (it MUST be in `.gitignore`).

## Examples

### Correct

```
Agent: I found a saved checkpoint:
  - Activity: Authentication module implementation
  - Status: in progress
  - Last session: 2026-03-07 14:30
  - Progress: 3 of 5 steps completed

  Do you want to resume this activity or start a new one?

User: Resume.

Agent: Resuming from where we left off...
  Pending next steps:
  1. Implement refresh token
  2. Add integration tests
```

### Incorrect

```
Agent: Hello! How can I help?

User: Let's continue the authentication module implementation.

Agent: Sure! Let's start from scratch. What's the scope?

# ❌ The agent ignored the existing checkpoint and forced the user
# to re-explain the entire context of the previous session.
```

## Automated Validation

- **Tool:** verification by the agent itself at the start and end of each session
- **When:** start of each session (read) and end of each activity (write)
- **Metric:** 100% of sessions MUST have the checkpoint checked on entry and saved on exit
