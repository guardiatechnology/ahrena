# Kata: Plan a Task

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creating and maintaining task plan documents by agents, per `lex-agent-planning`

## Objective

Create or update a task plan document before execution, ensuring that objective, scope, steps, and dependencies are documented and confirmed by the user before any irreversible action begins.

## When to Use

- At the start of any multi-step task
- Before invoking warriors, katas in sequence, or cries
- Before modifying multiple files in a single session
- When the user asks "do X" and X has more than one discernible step

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Task description | Yes | What the agent needs to do (may be vague — the kata clarifies) |
| Reference issue | No | `owner/repo#N` when the task originates from a GitHub issue |
| Agent dir | No | Default resolved automatically; may be overridden by `paths.plans` in `.directives` |

## Workflow

```
Progress:
- [ ] 1. Resolve plan file path and name
- [ ] 2. Check existing plans
- [ ] 3. Draft the plan
- [ ] 4. Present to user and confirm
- [ ] 5. Write the plan file
- [ ] 6. Execute the task updating the plan
- [ ] 7. Finalize the plan
```

### Step 1: Resolve Plan File Path and Name

1. Read `.ahrena/.directives` and check whether `paths.plans` is defined
2. If yes → use that value as the base directory
3. If not → use agent-specific default:
   - Claude Code → `.claude/plans/`
   - Cursor → `.cursor/plans/`
   - Unknown → `.plans/`
4. List existing files in the directory (if it exists) to determine the next sequential number
5. Compose the name: `plan-{NNN}-{slug}.md` where `{slug}` is the task summary in kebab-case (max 60 chars)

### Step 2: Check Existing Plans

1. If the plans directory does not exist → will create in Step 5
2. If it exists → list plans with `in-progress` or `pending` status:
   - If there is an `in-progress` plan for the same task → ask the user whether to resume or create new
   - If resuming → load the existing plan and skip to Step 6

### Step 3: Draft the Plan

Based on the task description:

1. Identify the **objective** (why this task exists — max 3 sentences)
2. List all files or systems that will be affected (**scope**)
3. Decompose the task into **atomic and verifiable steps** (each step = one completable action)
4. Identify **dependencies** (other plans, issues, pending decisions)
5. List **known risks** (what could go wrong; if none, write "None identified")

### Step 4: Present to User and Confirm

Present the plan draft with the question:

> "This is the plan for the task. Would you like to adjust anything before I start?"

Wait for response. Incorporate adjustments if requested. **Do not start execution before confirmation.**

### Step 5: Write the Plan File

1. Create the directory if it does not exist
2. Write the file with complete front-matter (`status: pending`) and the plan body
3. Confirm to the user: "Plan saved at `{path}`. Starting execution."
4. Update `status` to `in-progress` and `updated_at`

### Step 6: Execute the Task Updating the Plan

During execution:
- Mark each step with `[x]` when completed
- Update `updated_at` at each step change
- If a new step is discovered during execution → add it to the plan before executing it
- If a blocker arises → record it in the plan as a note and communicate to the user

### Step 7: Finalize the Plan

When all steps are `[x]`:
1. Update `status` to `done`
2. Update `updated_at`
3. Inform the user: "Task completed. Plan at `{path}` marked as `done`."
4. Remind the user that the plan should be committed alongside the produced artifacts
5. (Optional) Suggest invoking `cry-checkpoint` to update `Active plans` in `.checkpoint`, removing this plan from the list if it was listed there

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Plan file | Markdown with YAML front-matter | `{plans_dir}/plan-{NNN}-{slug}.md` |

## Example Execution

### Input

```
Task: complete migration of cries to lex-feature-design-docs
Issue: guardiafinance/ahrena#42
```

### Step 1 — Path resolved

```
Agent: Claude Code
Directory: .claude/plans/
Next number: 001 (empty directory)
File: .claude/plans/plan-001-complete-feature-design-docs.md
```

### Step 3 — Draft

```markdown
## Objective
Complete the update of Cries and katas that still reference paths.oas/paths.events/paths.domain
after the creation of lex-feature-design-docs. Warriors and main katas are already updated;
remaining are the entry points (Cries) and 2 katas with residual references.

## Scope
- cry-api-design.md, cry-event-storm.md, cry-feature-design.md, cry-full-design.md (pt-BR, en, es)
- kata-api-design-review.md (pt-BR, en, es)
- kata-api-design-doc.md — fix .directives references (pt-BR, en, es)
- .cursor/commands/ corresponding

## Steps
- [ ] 1. Open GitHub issue to track the work
- [ ] 2. Create branch feat/{N}-complete-feature-design-docs
- [ ] 3-6. Update 4 cries (× 3 languages)
- [ ] 7. Update kata-api-design-review (× 3 languages)
- [ ] 8. Fix kata-api-design-doc (× 3 languages)
- [ ] 9. Update .cursor/commands/ affected
- [ ] 10. Commit everything (new artifacts + cries + katas)
- [ ] 11. Open PR
```

### Step 4 — Confirmation

```
Agent: "This is the plan to complete the feature-design-docs migration.
  Total: ~18 files. Would you like to adjust anything before I start?"
```

## Restrictions

- **Never start execution without user confirmation** in Step 4
- **Never create an empty plan** — if the description is insufficient to decompose steps, ask clarifying questions first
- **Never delete a plan** — cancelled plans become `abandoned`, not removed
- **Never omit the front-matter** — `plan_id`, `title`, `status`, `agent`, `created_at`, `updated_at` are mandatory; `issue` when applicable

## References

- `lex-agent-planning` — Law
- `codex-agent-planning` — Manual with full template and best practices
- `lex-checkpoint` — Session scratchpad (clear delineation: plan = task; checkpoint = session)
- `cry-checkpoint` — Shortcut to record plan-id in `Active plans` when multiple plans coexist in the session
- `lex-directives` — Reading `.ahrena/.directives`
