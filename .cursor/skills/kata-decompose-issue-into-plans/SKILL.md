---
name: kata-decompose-issue-into-plans
description: "Decompose Issue into Sub-issue Plans. Decomposition of a parent Issue (User Story, Bug, Tech Task) into N executable Plan sub-issues, per lex-agent-planning"
---

# Kata: Decompose Issue into Sub-issue Plans

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Decomposition of a parent Issue (User Story, Bug, Tech Task) into N executable Plan sub-issues, per `lex-agent-planning`

## Workflow

```
Progress:
- [ ] 1. Confirm parent Issue exists and is well-formed
- [ ] 2. Determine the decomposition strategy
- [ ] 3. Draft N Plans with the user and confirm the decomposition
- [ ] 4. For each Plan: invoke kata-plan-task
- [ ] 5. Present the decomposition summary to the user
```

### Step 1: Confirm parent Issue exists and is well-formed

Before decomposing, verify that the parent Issue `{N}` exists and satisfies `lex-issue-first` and `lex-issue-quality`:

```bash
# Preferred — via MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)

# Fallback — via gh
gh issue view {N} --repo {owner}/{repo} --json number,title,state,labels,body,assignees
```

Validate:

- Parent Issue exists and is open (state `open`).
- Body contains Why/What/How (per `lex-issue-quality`).
- Required template labels are present.
- Compatible Issue Type (`Feature`, `Bug`, or `Task`).

If any criterion fails, abort with a message directing the user to invoke `kata-contributing-issue` to fix the parent Issue before decomposing.

### Step 2: Determine the decomposition strategy

If `decomposition_strategy` was passed explicitly, use it.

Otherwise, **infer** from the analysis of the parent Issue scope. Common strategies:

| Strategy | When to prefer | Example split |
|---|---|---|
| By layer | Work spans the stack (backend + frontend + infra) | Plan 1: backend; Plan 2: frontend; Plan 3: migration |
| By endpoint/feature flag | Multiple REST endpoints or independent flags | Plan 1: POST endpoint; Plan 2: GET endpoint; Plan 3: PATCH endpoint |
| By workflow phase | Work has sequential phases (design → impl → docs) | Plan 1: design + ADR; Plan 2: implementation; Plan 3: documentation |
| By bounded context | Work crosses DDD contexts | Plan 1: context A; Plan 2: context B |
| By dependency | Clear chain of prerequisites | Plan 1: spike; Plan 2: base refactor; Plan 3: feature on top |

Present the strategy to the user and ask for confirmation before drafting the Plans.

### Step 3: Draft N Plans with the user and confirm the decomposition

If `plan_drafts` was passed, use it as a starting point.

Otherwise, draft with the user. For each Plan, fill:

| Field | Content |
|---|---|
| `plan_summary` | 2-4 sentences — executable slice of the parent Issue scope |
| `plan_objective` | 1-3 sentences — what this Plan delivers at the end |
| `plan_steps` | Atomic and verifiable list (minimum 1 step) |
| `plan_dependencies` | Other Plans of this decomposition, Issues, PRs, or `"None"` |
| `plan_risks` | Risks + mitigations, or `"None identified"` |
| `plan_open_questions` | Pending questions, or `"None"` |

Pay special attention to **dependencies between Plans of the same decomposition**: Plan 2 of the decomposition of Issue #N may depend on Plan 1; Plan 3 on Plans 1 and 2. Document explicitly — it will become `plan_dependencies` in `kata-plan-task`.

Present the set of drafted Plans to the user:

> "This is the decomposition of #{N} into {len(plans)} Plans. Do you want to adjust the split, merge Plans, or split further before I create the sub-issues?"

Wait for confirmation. Incorporate adjustments. **Do not create any sub-issue before confirmation of the complete set.**

### Step 4: For each Plan: invoke kata-plan-task

For each confirmed `plan_draft`, invoke `kata-plan-task` passing the filled fields:

```python
for draft in plan_drafts:
    result = invoke("kata-plan-task",
        parent_issue_number=N,
        plan_summary=draft.summary,
        plan_objective=draft.objective,
        plan_steps=draft.steps,
        plan_dependencies=draft.dependencies,
        plan_risks=draft.risks,
        plan_open_questions=draft.open_questions,
        owner=owner,
        repo=repo,
    )
    created_plans.append(result.subissue_number)
```

For each Plan, `kata-plan-task` executes the 6 canonical steps: confirm the parent Issue, draft (already confirmed), create the sub-issue, fill the body, verify Issue Type, apply `status: todo`. Each invocation is independent — if one fails, the previously created Plans remain (it is not transactional).

If an invocation fails:

1. Capture the error.
2. Report to the user with the list of already created Plans (`created_plans`) and the failed Plan.
3. Offer: (a) retry only the failed one, (b) pause for investigation, (c) abort the decomposition (already created Plans remain as orphan sub-issues until a manual decision).

### Step 5: Present the decomposition summary to the user

After creating all sub-issues, present:

> "Decomposition of #{N} complete. {len(created_plans)} Plans created:
> - #{M1} — {truncated summary of Plan 1}
> - #{M2} — {truncated summary of Plan 2}
> - ...
>
> All with `status: todo`. Ready for Athena to start `todo → development` on each one, in the order of the mapped dependencies."

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| N Plan sub-issues | GitHub Issues (Task) | `{owner}/{repo}#{M_i}`, each a sub-issue of `#{N}` |
| Canonical bodies | Markdown (Summary + Plan section) | Body of each sub-issue |
| `status: todo` labels | GitHub label | On each created sub-issue |
| `Task` Issue Types | GitHub Issue Type | On each created sub-issue |
| Decomposition summary | Message to the user with URLs | Agent session |

## Execution Example

### Input

```
parent_issue_number: 200
decomposition_strategy: "by event sourcing layer"
plan_drafts: (will be drafted in session)
```

### After Step 2 (strategy confirmed)

Strategy: "by event sourcing layer" — separate aggregate write-side, read-side projection, and legacy migration.

### After Step 3 (3 Plans drafted and confirmed)

```
Plan 1: Refactor Ledger aggregate to event sourcing (write-side)
Plan 2: Implement read-side projection
Plan 3: Migration helper legacy state → events

Dependencies:
- Plan 2 depends on Plan 1
- Plan 3 depends on Plans 1 and 2
```

### After Step 4 (3 Plan sub-issues created)

```
#201 — Refactor Ledger aggregate to event sourcing (write-side) [status: todo]
#202 — Implement read-side projection [status: todo, depends on #201]
#203 — Migration helper legacy state → events [status: todo, depends on #201, #202]
```

### Summary presented to the user

```
Agent: "Decomposition of #200 complete. 3 Plans created:
  - #201 — Refactor Ledger aggregate to event sourcing (write-side)
  - #202 — Implement read-side projection
  - #203 — Migration helper legacy state → events

  All with `status: todo`. Ready for Athena to start
  `todo → development` on each one, in the order: #201 → #202 → #203."
```

## Restrictions

- **Never decompose without a confirmed parent Issue** — the parent Issue precedes any Plan; without an Issue, there is no decomposition.
- **Never skip the confirmation of the complete set in Step 3** — presenting the full decomposition to the user before creating the first sub-issue avoids inconsistent half-decompositions.
- **Never create branch, worktree, or apply assignee in this kata** — delegated to `kata-plan-task` (which also does not create them — they belong to `todo → development`).
- **Never decompose an already-decomposed parent Issue without checking existing sub-issues** — before creating, list current sub-issues (`gh api repos/{owner}/{repo}/issues/{N}/sub_issues`) and present to the user; manual decision to create more, merge, or abort the operation.
- **Document dependencies between Plans of the same decomposition** — `plan_dependencies` must explicitly list other Plans of this decomposition when applicable; Athena uses this order to sequence `todo → development`.
- **Not transactional** — if the 3rd `kata-plan-task` invocation fails, the previous 2 remain; recovery is manual.
