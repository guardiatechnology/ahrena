# Lexis: Mandatory Planning for Agent Tasks

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Every multi-step task initiated by any agent or subagent (Claude, Cursor, IDEs, warriors, katas, cries)

## Purpose

Agents that execute without prior planning produce partial results, leave files in inconsistent states, and force the user to manually reconstruct context. This Lexis eliminates that pattern by requiring every agent to document its plan before executing, making intention, scope, and sequence auditable by humans and other agents.

## Law

> **Every agent MUST create a plan document at `./{agent_dir}/plans/plan-{NNN}-{slug}.md` (or the path defined in `paths.plans` in `.ahrena/.directives`) BEFORE starting any task that involves 2 or more steps, affects multiple files, or produces permanent artifacts. The plan MUST be presented to the user for confirmation before execution begins. Starting multi-step execution without a documented and confirmed plan is FORBIDDEN.**

## Coverage

- **Applies to:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, any AI agent or subagent that invokes katas, warriors, or cries in the Ahrena context
- **Bound agents:** all, without role exceptions
- **Allowed exceptions:** trivial single-step operations (editing a single file with a direct instruction, pure read queries, isolated commands with no permanent side effects)

## Plan Path Resolution (precedence)

| Priority | Source | Value |
|:---:|---|---|
| 1 | `paths.plans` in `.ahrena/.directives` | Project override — supersedes everything else |
| 2 | Agent-specific default | `.claude/plans/` for Claude Code; `.cursor/plans/` for Cursor; `.plans/` for unknown agent |

File name: `plan-{NNN}-{slug}.md` where `{NNN}` is sequential per directory (001, 002, …), no gaps.

## Minimum Required Plan Structure

```markdown
---
plan_id: "{NNN}"
title: "{slug}"
status: pending | in-progress | done | archived | abandoned
agent: claude | cursor | unknown
issue: "{owner/repo#N}"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Plan: {human-readable title}

## Objective
{Why this task is being done — 1 to 3 sentences}

## Scope
{What will be modified: files, systems, affected artifacts}

## Steps
- [ ] Step 1
- [ ] Step 2
...

## Dependencies
{Plans or issues this task depends on; "None" if there are none}

## Risks
{Known risks and mitigations; "None identified" if there are none}
```

## Plan Lifecycle

```
pending → in-progress → done
                     ↘ abandoned
done → archived
```

- The agent MUST update `status` in the front-matter when starting (`in-progress`) and when completing (`done`)
- Steps MUST be marked with `[x]` as they are completed
- `done` or `abandoned` plans MUST be moved to `archived` after the corresponding PR is merged
- Plans MUST be committed alongside the work they describe (not ephemeral like `.checkpoint`)

## Relationship to Other Artifacts

- **GitHub Issue:** a plan references an issue; an issue may have multiple plans (e.g.: design, implementation, tests)
- **Checkpoint (`.checkpoint`):** the checkpoint tracks session state; the plan tracks intention and structured progress — they are complementary, not mutually exclusive
- **ADR:** when a plan identifies a relevant architectural decision, an ADR MUST be opened per `lex-issue-driven`

## Examples

### Correct

```
Task: update 4 cries and 2 katas to the new paths structure
→ Agent creates .claude/plans/plan-001-complete-feature-design-docs.md
→ Presents to user: objective, 12 files to edit, sequence
→ User confirms
→ Agent executes marking steps, updates status to done
→ Plan committed alongside the edits
```

### Incorrect

```
Task: update 4 cries and 2 katas
→ Agent starts editing cry-api-design.md directly without creating a plan
→ ❌ Violates lex-agent-planning — multi-step execution without documented plan
```

## Automated Validation

- **Tool:** agent self-check before any multi-step execution; `kata-plan-task` as canonical entry point
- **Timing:** before any multi-step task execution — without exception
- **Metric:** 0 multi-step tasks executed without a plan documented in `{agent_dir}/plans/`

## References

- `codex-agent-planning` — manual with full template, examples, and best practices
- `kata-plan-task` — operational procedure to create and maintain plans
- `lex-checkpoint` — session state tracking (complementary)
- `lex-issue-driven` — issue-driven development flow
