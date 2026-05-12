# Lexis: Mandatory Planning for Agent Tasks

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Every multi-step task initiated by any agent or subagent (Claude, Cursor, IDEs, warriors, katas, cries)

## Purpose

Agents that execute without prior planning produce partial results, leave files in inconsistent states, and force the user to manually reconstruct context. This Lexis eliminates that pattern by requiring every agent to document its plan before executing, making intention, scope, and sequence auditable by humans and other agents. It also defines a unified lifecycle across plan, GitHub Issue, and PR — with an explicit owner for each transition — to eliminate drift and make the review "waiting room" visible.

## Law

> **Every agent MUST create a plan document at `./{agent_dir}/plans/plan-{NNN}-{slug}.md` (or the path defined in `paths.plans` in `.ahrena/.directives`) BEFORE starting any task that involves 2 or more steps, affects multiple files, or produces permanent artifacts. The plan MUST be presented to the user for confirmation before execution begins. Starting multi-step execution without a documented and confirmed plan is FORBIDDEN. The plan `status:` MUST belong to the unified enum `todo | development | to review | review | to release | release | done` (plus the alternative terminal `abandoned`); each transition MUST be executed by the owner declared in this Lex.**

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
status: todo | development | to review | review | to release | release | done | abandoned
agent: claude | cursor | unknown
issue: "{owner/repo#N}"
branch: "{type}/{N}-{slug}"
worktree: ".worktrees/{N}-{slug}"
claude_session: "{short-uuid}"        # optional; populated by kata-session-heartbeat
session_entrypoint: "claude-vscode | claude-cli | claude-desktop | claude-web"
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
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (alternative terminal, any stage)
```

Semantics of each state:

- `todo` — plan created, Issue opened, remote branch linked, worktree ready, work not yet started.
- `development` — Athena has delegated and implementation is in progress.
- `to review` — PR opened, waiting for a reviewer (human or Argos) to pick it up.
- `review` — Argos (or human) actively reviewing.
- `to release` — review approved, waiting for the release agent to start.
- `release` — release in execution (tag/build/deploy).
- `done` — release completed, PR merged, cycle closed.
- `abandoned` — alternative terminal (any stage → `abandoned`); plan discarded.

The `archived/` folder remains as a filesystem organization convention for post-merge plans — **it is no longer a state** of the enum.

## Owner of `— → todo`: warrior-eunomia

Every plan (top-level or subtask) MUST be created by `warrior-eunomia` via `kata-plan-task` (top-level) or `kata-create-subtasks` (subtask, downstream of Athena Phase 4). Eunomia executes the 5 steps below before marking `status: todo` as definitive:

1. Open the corresponding Issue (per `lex-issue-first` and `lex-issue-quality`).
2. Verify Issue Type after creation (per `lex-issue-type-verified`).
3. Create the remote branch and link it to the Issue via `gh issue develop {N} --base main --name {type}/{N}-{slug}` (registers the branch as "Development" on the GitHub sidebar).
4. Create the worktree per `lex-git-worktrees`.
5. Record the Issue number, branch name, and worktree path in the plan front-matter (`issue:`, `branch:`, `worktree:`). Without this anchoring, the plan remains a draft — it cannot be presented as `todo` to the user.

**Fallback while Eunomia is not yet shipped:** the responsibility falls to the current session agent, following the same contract — with no subsequent refactor when Eunomia ships.

<HARD-GATE>
warrior-eunomia (or the session agent acting as fallback while Eunomia
is not yet shipped) MUST NOT mark `status: todo` as definitive in a plan
without satisfying ALL 5 canonical steps:

  (a) Issue opened per lex-issue-first and lex-issue-quality
      (template, label, Issue Type, assignee, Why/What/How)
  (b) Issue Type verified per lex-issue-type-verified (delivered
      in plan-044). Until plan-044 ships, satisfy via
      `gh api repos/{owner}/{repo}/issues/{N}` returning a populated
      `type` compatible with the template — same contract, without
      the dedicated Lex yet
  (c) Remote branch created and linked to the Issue via
      gh issue develop {N} --base main --name {type}/{N}-{slug}
  (d) Worktree created per lex-git-worktrees at
      `.worktrees/{N}-{slug}/`
  (e) Plan front-matter updated with issue, branch, and worktree

This rule applies to EVERY plan (top-level or subtask), regardless of:
  - perceived size ("it's just a chore")
  - urgency ("production fire")
  - who asked ("the CEO requested it")
  - team confidence ("we already tested a lot")

Single declared exception: none. Even on hotfix, the 5 steps execute
in sequence — Eunomia (or fallback) does not skip the Issue↔branch↔worktree
anchoring.
</HARD-GATE>

## Owners of Each Transition

| Transition | Owner | Trigger |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: session agent) | Creates plan + opens Issue + `gh issue develop` + worktree |
| `todo → development` | `warrior-athena` | Phase 4 (implementation delegation) |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` opens PR |
| `to review → review` | `warrior-argos` | Argos begins automated review cycle |
| `review → to review` | `warrior-argos` | Argos ends cycle without approving (changes-requested or awaiting-human) |
| `to review → to release` | `warrior-athena` | Human approves PR (wake-up loop detects `APPROVED`) |
| `to release → release` | `warrior-janus` | `kata-release-prepare` begins; human gate for bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` completes (tag pushed, `validate-tag.yml` passes, Release created); notification via MCP at `notifications.channels.release_notify` |
| `any → abandoned` | creator or current owner | Plan discarded |

Each owner MUST:

- Update `status:` in the plan front-matter.
- Apply the corresponding `status: <name>` label on the GitHub Issue (per `lex-issue-status`).
- Apply the corresponding `status: <name>` label on the PR (starting at `to review`).

## Relationship to Other Artifacts

- **GitHub Issue:** a plan references an issue; an issue may have multiple plans (e.g.: design, implementation, tests). The `status: <name>` label on the Issue mirrors the plan `status:`.
- **PR:** starting at `to review`, the PR carries the corresponding `status: <name>` label, updated by Athena/Argos/Janus as the state advances.
- **Checkpoint (`.checkpoint`):** the plan covers the **task** (committed, with Steps, Decisions, Risks); the checkpoint covers the **session** (working-window focus, hand-off between plans, parallel threads, scratchpad). Overlap is FORBIDDEN — see `lex-checkpoint` rule 5
- **ADR:** when a plan identifies a relevant architectural decision, an ADR MUST be opened per `lex-issue-driven`
- **Session heartbeat:** the plan front-matter references the Claude Code session currently operating on the plan (`claude_session`, `session_entrypoint`); details in `codex-session-tracking`.

### Plan vs `.checkpoint` — what goes where

| Content | Lives in |
|---|---|
| Objective, `[x]` Steps, Status (from the unified enum), closed Decisions, Risks, Verification | Plan — committed |
| Activity, detailed Progress, Artifacts produced, Next steps of a task | Plan — committed |
| Overall focus of the working window (Session focus) | `.checkpoint` — gitignored |
| Pointers to multiple active plans (Active plans) | `.checkpoint` — gitignored |
| Parallel threads that did not become a plan (Open threads) | `.checkpoint` — gitignored |
| Free scratchpad, links, reminders (Notes) | `.checkpoint` — gitignored |

When in doubt, content goes to the plan. The plan wins on durability (committed) and on scope (it covers the task; the checkpoint covers the session).

## Examples

### Correct

```
Task: implement unified status across plan and Issue
→ Eunomia opens Issue #90 (feature-request template, Issue Type Feature, labels)
→ Eunomia verifies type via gh api (per lex-issue-type-verified)
→ Eunomia creates branch via gh issue develop 90 --base main --name feat/90-...
→ Eunomia creates worktree at .worktrees/90-.../
→ Eunomia writes plan-043 with status: todo, issue, branch, worktree in the front-matter
→ Athena takes Phase 4: status → development
→ Athena opens PR: status → to review
→ Argos starts review: status → review
→ Argos ends without changes: status → to review (human nudged at 3×15min)
→ Human approves: status → to release
→ Janus begins release: status → release
→ Janus concludes: status → done
```

### Incorrect

```
Task: implement feature X
→ Agent creates branch directly via git checkout -b without opening an Issue
→ ❌ Violates lex-issue-first; without an Issue, the plan cannot be marked todo
→ Agent marks status: todo on the plan without a remote branch linked to the Issue
→ ❌ Violates the HARD-GATE in this Lex (precondition (c) not satisfied)
```

## Automated Validation

- **Tool:** agent self-check before any multi-step execution; `kata-plan-task` as canonical entry point; PR review confirms that plan `status:`, Issue `status:*` label, and PR `status:*` label are aligned.
- **Timing:** before any multi-step task execution — without exception; and on every state transition.
- **Metric:** 0 multi-step tasks executed without a plan documented in `{agent_dir}/plans/`; 0 PRs merged with divergent `status:` between plan, Issue, and PR; 100% of transitions executed by the declared owner.

## References

- `codex-agent-planning` — manual with full template, examples, and best practices
- `kata-plan-task` — operational procedure to create and maintain plans (Eunomia top-level mode)
- `kata-create-subtasks` — procedure for decomposing a child Issue into subtasks (Eunomia subtask mode)
- `kata-session-heartbeat` — session heartbeat update
- `lex-issue-status` — canonical status labels on Issue/PR
- `lex-issue-type-verified` — programmatic Issue Type verification after creation
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — preconditions of the `— → todo` step
- `lex-checkpoint` — session state tracking (complementary)
- `lex-issue-driven` — issue-driven development flow
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners of the transitions
