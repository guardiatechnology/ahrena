# Kata: Plan a Task

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creation of a Plan sub-issue linked to a parent Issue, per `lex-agent-planning` (hierarchical Issue → Plan → PR model)

## Objective

Create a Plan sub-issue (Issue Type Task) linked to an existing parent Issue, with a canonical body (Summary + Plan section), the `status: todo` label applied, and the Issue Type verified. This is the procedure that `warrior-eunomia` executes in top-level mode (standalone Plan linked to an existing Issue) and that the session agent follows as a fallback while Eunomia is not shipped.

Per the `lex-agent-planning` HARD-GATE for Gate 1, the `status: todo` label may only be applied to the Plan sub-issue when the 4 canonical steps are complete: (1) parent Issue open and conformant with `lex-issue-first` and `lex-issue-quality`; (2) Plan sub-issue created via MCP `create_issue` (preferred) or `gh issue create --type Task` (fallback), linked to the parent Issue, with the Plan template and required labels; (3) body filled with the canonical plan (Summary + Plan); (4) Issue Type verified as `Task` per `lex-issue-type-verified`.

Branch, worktree, and assignee are **NOT** preconditions of this kata. They belong to `todo → development` (Athena, codified in `lex-agent-planning` Gate 2).

## When to Use

- When the user asks to register a standalone Plan linked to an existing parent Issue.
- When `kata-decompose-issue-into-plans` needs to create each Plan sub-issue of the decomposition (one call per Plan).
- At the start of any multi-step task whose plan is not yet materialized as a sub-issue on GitHub.
- Before invoking `kata-load-plan-from-subissue` (the load kata refuses if the sub-issue does not exist).

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `parent_issue_number` | Yes | Number `{N}` of the parent Issue (User Story, Bug, or Tech Task) the Plan connects to |
| `plan_summary` | Yes | Executable summary of the Plan (2-4 sentences). Typically a slice of the parent Issue's scope |
| `plan_objective` | Yes | Why this unit exists and what it delivers at the end (1-3 sentences) |
| `plan_steps` | Yes | List of atomic, verifiable Steps (minimum 1) |
| `plan_dependencies` | No | Other Plans, Issues, or PRs this task depends on. Default: `"None"` |
| `plan_risks` | No | Known risks and mitigations. Default: `"None identified"` |
| `plan_open_questions` | No | Pending questions that need a decision. Default: `"None"` |
| `owner/repo` | No | Repo where the parent Issue lives. Default: current repo of the worktree |

## Workflow

```
Progress:
- [ ] 1. Confirm parent Issue exists and is well-formed
- [ ] 2. Draft the Plan with the user and confirm
- [ ] 3. Create the Plan sub-issue (Task) linked to the parent Issue
- [ ] 4. Fill the sub-issue body with the canonical plan
- [ ] 5. Verify Issue Type post-creation
- [ ] 6. Apply `status: todo` label and confirm with the user
```

### Step 1: Confirm parent Issue exists and is well-formed

Before creating the Plan sub-issue, verify that the parent Issue `{N}` exists and satisfies `lex-issue-first` and `lex-issue-quality`:

```bash
# Preferred — via MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)

# Fallback — via gh
gh issue view {N} --repo {owner}/{repo} --json number,title,state,labels,body,assignees
```

Verify:

- Parent Issue exists and is open (state `open`).
- Body contains Why/What/How (per `lex-issue-quality`).
- Required template labels are present.
- Compatible Issue Type (`Feature` for User Story; `Bug` for bug; `Task` for Tech Task).

If any criterion fails, **abort** with a message directing the user to invoke `kata-contributing-issue` to open or fix the parent Issue first.

### Step 2: Draft the Plan with the user and confirm

Using the inputs (`plan_summary`, `plan_objective`, `plan_steps`, `plan_dependencies`, `plan_risks`, `plan_open_questions`), assemble the candidate body (per the *Plan sub-issue body schema* section in `lex-agent-planning`):

```markdown
## Summary

{plan_summary — 2-4 sentences}

Parent: #{N}

## Plan

### Objective
{plan_objective — 1-3 sentences}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{plan_dependencies or "None"}

### Risks
{plan_risks or "None identified"}

### Open Questions
{plan_open_questions or "None"}
```

Present the draft to the user:

> "This is the Plan linked to #{N}. Do you want to adjust anything before I open the sub-issue?"

Wait for confirmation. Incorporate adjustments. **Do not create the sub-issue before confirmation.**

### Step 3: Create the Plan sub-issue (Task) linked to the parent Issue

Prefer MCP `create_issue` per `lex-mcp` rule 1:

```python
# Preferred — via MCP
result = mcp.github.create_issue(
    owner=owner,
    repo=repo,
    title="plan: {short title derived from plan_summary}",
    body=body_content,
    labels=["plan 📋"] + parent_labels_mirror,
    type="Task",
)
M = result["number"]
M_db_id = result["id"]  # node ID required for the sub-issue link
```

CLI fallback per `lex-mcp` rule 4:

```bash
# CLI fallback — capture number and database ID atomically from the create response
result=$(gh issue create \
  --repo {owner}/{repo} \
  --title "plan: {short title}" \
  --body-file /tmp/plan-{M}-body.md \
  --label "plan 📋" \
  --label "{mirror parent labels}" \
  --json number,id)

M=$(echo "$result" | jq -r .number)
M_db_id=$(echo "$result" | jq -r .id)
```

Link the sub-issue as a child of the parent Issue:

```bash
gh api -X POST repos/{owner}/{repo}/issues/{N}/sub_issues -F sub_issue_id={M_db_id}
```

Capture `{M}` (Plan sub-issue number) for the next steps.

### Step 4: Fill the sub-issue body with the canonical plan

If the body was already written in Step 3 via MCP `create_issue` with `body=body_content`, this step is confirmatory. If the default Plan template was applied by GitHub (instead of the candidate body), write via update:

```python
# Preferred — via MCP
mcp.github.update_issue(
    owner=owner, repo=repo, issue_number=M,
    body=body_content,
)

# CLI fallback
gh issue edit {M} --repo {owner}/{repo} --body-file /tmp/plan-{M}-body.md
```

Validate that the written body contains the 5 canonical sections: Summary, Plan → Objective, Steps, Risks, Dependencies, Open Questions.

### Step 5: Verify Issue Type post-creation

Per `lex-issue-type-verified`, confirm the native type is `Task`:

```bash
gh api repos/{owner}/{repo}/issues/{M} --jq '.type.name'
```

If empty or different from `Task`, apply manually:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{M} -f type=Task
```

### Step 6: Apply `status: todo` label and confirm with the user

```bash
gh issue edit {M} --repo {owner}/{repo} --add-label "status: todo"
```

Confirm with the user:

> "Plan registered at #{M} (sub-issue of #{N}). Canonical body, `status: todo` label applied, Issue Type `Task` verified. Ready for `todo → development` when you decide to start execution."

Branch, worktree, and assignee are **not** applied in this kata — they belong to `todo → development`, owned by Athena.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Plan sub-issue | GitHub Issue (Task) | `{owner}/{repo}#{M}`, sub-issue of `#{N}` |
| Canonical body | Markdown (Summary + Plan section) | Body of sub-issue `{M}` |
| `status: todo` label | GitHub label | Sub-issue `{M}` |
| `Task` Issue Type | GitHub Issue Type | Sub-issue `{M}` |
| Sub-issue URL | Link | Presented to the user |

## Execution Example

### Input

```
parent_issue_number: 200
plan_summary: "Refactor the Ledger aggregate to event sourcing, separating
  commands (write-side) from reads (read-side projection)."
plan_objective: "Deliver the first executable slice of User Story #200:
  Ledger rewritten as an event-sourced aggregate with factory + repository."
plan_steps:
  - "Step 1 — Model LedgerEvent base class"
  - "Step 2 — Rewrite Ledger.apply() as event projection"
  - "Step 3 — Repository persisting events instead of state"
  - "Step 4 — Migration helper for legacy state → events"
  - "Step 5 — Aggregate tests"
plan_dependencies: "None"
plan_risks: "- migration helper may fail on datasets with historical
  inconsistency — mitigated by dry-run + checksum."
plan_open_questions: "None"
```

### Plan sub-issue #201 created

```markdown
## Summary

Refactor the Ledger aggregate to event sourcing, separating commands
(write-side) from reads (read-side projection).

Parent: #200

## Plan

### Objective
Deliver the first executable slice of User Story #200: Ledger rewritten
as an event-sourced aggregate with factory + repository.

### Steps
- [ ] Step 1 — Model LedgerEvent base class
- [ ] Step 2 — Rewrite Ledger.apply() as event projection
- [ ] Step 3 — Repository persisting events instead of state
- [ ] Step 4 — Migration helper for legacy state → events
- [ ] Step 5 — Aggregate tests

### Dependencies
None

### Risks
- migration helper may fail on datasets with historical inconsistency
  — mitigated by dry-run + checksum.

### Open Questions
None
```

### User confirmation

```
Agent: "Plan registered at #201 (sub-issue of #200).
  Canonical body, `status: todo` label applied, Issue Type `Task` verified.
  Ready for `todo → development` when you decide to start execution."
```

## Restrictions

- **Never apply `status: todo` before Step 6** — `lex-agent-planning` Gate 1 HARD-GATE requires the 4 canonical steps completed.
- **Never create the Plan sub-issue without a confirmed parent Issue** — without an open and conformant parent Issue, there is no Plan to create; invoke `kata-contributing-issue` first.
- **Never create a branch, worktree, or apply an assignee in this kata** — they belong to `todo → development` (Athena, `lex-agent-planning` Gate 2).
- **Never create a file in `.claude/plans/` or `.cursor/plans/` in this kata** — the local cache is materialized by `kata-load-plan-from-subissue` later, and the load kata refuses if the sub-issue does not exist.
- **Never omit Summary, Parent, or Plan sections from the body** — a body without Summary, Objective, Steps, Risks, Dependencies, Open Questions does not satisfy Gate 1 precondition (c).
- **Prefer MCP > CLI** — per `lex-mcp` rule 1; CLI `gh issue create` is the fallback per rule 4.

## References

- `lex-agent-planning` — Law (hierarchical Issue → Plan → PR model; Gate 1 owned by Eunomia)
- `lex-issue-status` — canonical labels; `status: todo` applied in Step 6
- `lex-issue-quality` — parent Issue body requirements
- `lex-issue-type-verified` — programmatic Issue Type verification
- `lex-issue-first` — parent Issue precedes the Plan sub-issue
- `lex-mcp` — MCP preference + CLI fallback
- `codex-agent-planning` — operational manual
- `kata-contributing-issue` — parent Issue creation (precondition)
- `kata-decompose-issue-into-plans` — decomposes the parent Issue into N Plan sub-issues; invokes this kata per Plan
- `kata-load-plan-from-subissue` — materializes the local cache after the Plan sub-issue exists
- `kata-flush-plan-to-subissue` — used in later transitions (not in this kata)
- `warrior-eunomia` — top-level owner of this kata
