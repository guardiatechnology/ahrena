# Codex: Agent Task Planning

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creating, maintaining, and managing the lifecycle of agent task plans in the Ahrena context

## Overview

This Codex is the canonical manual for agent task planning. It complements `lex-agent-planning` (the Law) with templates, fill examples, numbering rules, best practices, and guidance for edge cases. Every agent that creates plans MUST consult this Codex.

## Context

- **Domain:** AI agent task execution discipline
- **Audience:** all agents (Claude, Cursor, warriors, katas) and human reviewers
- **Update:** when the template or conventions change (ADR recommended for front-matter changes)

---

## 1. Plan Path Resolution

The agent resolves the plans directory in the following order:

```
1. Read .ahrena/.directives
2. If paths.plans exists → use that value (e.g.: ".plans/")
3. Otherwise → use agent-specific default:
   - Claude Code (CLI, VSCode, Desktop, claude.ai) → .claude/plans/
   - Cursor                                         → .cursor/plans/
   - Unknown agent                                  → .plans/
```

Example project override:
```yaml
# .ahrena/.directives
paths:
  root: ".ahrena/"
  plans: ".plans/"    # override: all agents use .plans/
```

---

## 2. File Naming Convention

```
plan-{NNN}-{slug}.md
```

| Field | Rule |
|---|---|
| `{NNN}` | 3-digit zero-padded sequential number (001, 002, …). Increment from the highest existing number in the directory. No gaps when possible; if a gap exists (abandoned plan), do not reuse the number |
| `{slug}` | kebab-case, maximum 60 characters, summary of the task |

Examples:
- `plan-001-complete-feature-design-docs.md`
- `plan-002-create-warrior-hecate.md`
- `plan-003-update-discovery-warriors.md`

---

## 3. Full Plan Template

```markdown
---
plan_id: "001"
title: "complete-feature-design-docs"
status: pending
agent: claude
issue: "guardiafinance/ahrena#42"
created_at: "2026-05-02T14:30:00Z"
updated_at: "2026-05-02T14:30:00Z"
---

# Plan: Complete Feature Design Docs — update cries and katas

## Objective

Complete the migration of feature design artifacts to the canonical structure
`docs/{context}/{category}/` defined by `lex-feature-design-docs`. Warriors and katas
are already updated; what remains are the Cries (user entry points) and 2 katas with residual references.

## Scope

Files to modify:
- `framework/pt-BR/engineering/platform/cries/cry-api-design.md`
- `framework/pt-BR/engineering/platform/cries/cry-event-storm.md`
- `framework/pt-BR/engineering/platform/cries/cry-feature-design.md`
- `framework/pt-BR/engineering/platform/cries/cry-full-design.md`
- `framework/pt-BR/engineering/platform/katas/kata-api-design-review.md`
- `framework/pt-BR/engineering/platform/katas/kata-api-design-doc.md`
- Equivalents in `framework/en/` and `framework/es/`
- `.cursor/skills/` and `.cursor/commands/` corresponding

Total: ~18 files.

## Steps

- [ ] 1. Open GitHub issue to track this work
- [ ] 2. Create branch `feat/{N}-complete-feature-design-docs`
- [ ] 3. Update `cry-api-design.md` (pt-BR, en, es)
- [ ] 4. Update `cry-event-storm.md` (pt-BR, en, es)
- [ ] 5. Update `cry-feature-design.md` (pt-BR, en, es)
- [ ] 6. Update `cry-full-design.md` (pt-BR, en, es)
- [ ] 7. Update `kata-api-design-review.md` (pt-BR, en, es)
- [ ] 8. Fix `kata-api-design-doc.md` (pt-BR, en, es)
- [ ] 9. Update `.cursor/commands/` and `.cursor/skills/` affected
- [ ] 10. Commit all previous artifacts (new feature-design-docs + cries + katas)
- [ ] 11. Open PR referencing the issue

## Dependencies

- Previous (uncommitted) work: `lex-feature-design-docs`, `codex-feature-design-docs`, `kata-feature-design-docs` + warriors + katas already updated

## Risks

- en/es cries require consistent translation — use pt-BR versions as source of truth
- cry-feature-design has more references (paths.domain + paths.oas + paths.events) — verify all
```

---

## 4. Lifecycle States

| Status | When to use | Who updates |
|---|---|---|
| `pending` | Plan created, awaiting user confirmation or start | Agent on creation |
| `in-progress` | Execution started | Agent on first step |
| `done` | All steps marked with `[x]` | Agent on completion |
| `abandoned` | Task cancelled before completion | Agent with reason note |
| `archived` | PR merged, plan no longer needs active attention | Agent after merge |

---

## 5. When a Plan is Required (and When It Is Not)

### Required

- Task with 2+ chained steps
- Any operation touching 2+ files
- Every warrior or cry invocation (by definition multi-step)
- Any task producing permanent artifacts (files, commits, PRs, posts)

### Not Required (trivial single step)

- Editing a single file with a direct and precise instruction
- Reading/querying files without writing
- Executing a single isolated command with no permanent side effect
- Answering a factual question

### Gray Area — use a plan as precaution

- Apparently simple task that may branch (e.g.: "fix the bug" without knowing the scope)
- Irreversible operation even if single-step (e.g.: deleting files)

---

## 6. Relationship Between Plans and Other Artifacts

```
GitHub Issue
    └── Plan (task plan — committed)
            ├── ADR (if relevant architectural decision)
            └── ─ ─ ─ do not confuse with ─ ─ ─
                Checkpoint (.checkpoint — gitignored, session)
```

- A plan **references** an issue but does not replace it
- A plan may **generate** an ADR when an impactful decision is identified during execution
- The **checkpoint** is NOT subordinate to the plan; it is a parallel artifact of **session**, not of **task**

### Plan vs `.checkpoint` — canonical delineation

The plan covers the **task**: Objective, Scope, `[x]` Steps, closed Decisions, Risks, Verification. Committed.
The checkpoint covers the **session**: Session focus, Active plans (pointers), Open threads, Notes. Gitignored.

| Content | Plan | Checkpoint |
|---|:---:|:---:|
| `[x]` Steps | ✅ | ❌ |
| Closed task decisions | ✅ | ❌ |
| Task risks | ✅ | ❌ |
| Artifacts produced | ✅ | ❌ |
| Overall focus of the working window | ❌ | ✅ |
| List of plans active in the session | ❌ | ✅ |
| Parallel threads that did not become a plan | ❌ | ✅ |
| Free scratchpad, links, reminders | ❌ | ✅ |

If content repeats in both, there is overlap — the plan wins (committed). Overlap is FORBIDDEN per `lex-checkpoint` rule 5 and per `lex-agent-planning` "Relationship to Other Artifacts".

---

## 7. Best Practices

1. **Write the plan before knowing everything.** The goal is to make intention visible, not to produce perfect documentation. An imprecise plan that evolves is better than no plan.
2. **Keep steps atomic.** Each step must be verifiable: done or not done. Avoid vague steps like "take care of the events part".
3. **Update in real time.** Mark `[x]` as each step completes, not at the end of everything.
4. **No ghost plans.** If the task is cancelled before starting, mark `abandoned` with reason — do not delete the file.
5. **Commit the plan.** The plan is part of the work; it must go in the same PR as the artifacts it describes.

---

## References

- `lex-agent-planning` — corresponding Law
- `kata-plan-task` — operational procedure to create and maintain plans
- `lex-checkpoint` — session state tracking
- `lex-issue-driven` — Issue-Driven flow
