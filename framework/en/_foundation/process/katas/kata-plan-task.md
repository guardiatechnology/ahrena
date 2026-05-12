# Kata: Plan a Task

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creating and maintaining task plans by agents, per `lex-agent-planning` (3-layer model — ADR-002)

## Objective

Create the canonical plan of a task before execution, ensuring that objective, scope, steps, and dependencies live in the **GitHub Issue body** (canonical per ADR-002) and are confirmed by the user before any irreversible action starts. This is the procedure that **`warrior-eunomia` executes in top-level mode** (per plan-046 / absorption of plan-044) and that the session agent follows as fallback while Eunomia is not available.

Per `lex-agent-planning` HARD-GATE, the `status: todo` label may only be applied to the Issue when the 5 canonical steps are complete: (1) Issue opened per `lex-issue-quality`; (2) Issue Type verified per `lex-issue-type-verified`; (3) remote branch created via `gh issue develop` and linked to the Issue; (4) worktree created per `lex-git-worktrees`; (5) **Issue body populated with the canonical plan** (Summary + Plan section).

## When to Use

- At the start of any multi-step task.
- Before invoking warriors, katas in sequence, or cries.
- Before modifying multiple files in a single session.
- When the user requests "do X" and X has more than one discernible step.

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Task description | Yes | What the agent needs to do (can be vague — the kata clarifies) |
| Repo (`owner/repo`) | No | Default: current repo of the worktree |
| Issue template | No | `feature-request` (default), `simple-task`, `user-story-for-api`, `user-story-for-frontend` |

## Workflow

```
Progress:
- [ ] 1. Draft the plan with the user
- [ ] 2. Open Issue with canonical body (Summary + Plan)
- [ ] 3. Verify Issue Type
- [ ] 4. Create branch via `gh issue develop`
- [ ] 5. Create worktree
- [ ] 6. Materialize local cache via kata-load-plan-from-issue
- [ ] 7. Apply `status: todo` label and confirm with the user
```

### Step 1: Draft the plan with the user

Based on the task description:

1. Identify the **Objective** (why this task exists — 1-3 sentences).
2. Decompose into atomic and verifiable **Steps**.
3. Identify **Dependencies** (other plans, Issues, pending decisions; "None" if there are none).
4. List known **Risks** (mitigations; "None identified" if there are none).
5. List **Open Questions** (pending decisions that affect execution; "None" if there are none).

Present the draft with:

> "This is the plan for the task. Do you want to adjust anything before I open the Issue?"

Wait for response. Incorporate adjustments. **Do not open the Issue before confirmation.**

### Step 2: Open Issue with canonical body (Summary + Plan)

Build the body following the schema in `lex-agent-planning`:

```markdown
## Summary

{2-4 sentences describing the objective. Typically inherited from the template.}

## Plan

### Objective
{Objective from the draft — 1-3 sentences.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{List or "None".}

### Risks
{List or "None identified".}

### Open Questions
{List or "None".}
```

Open the Issue (prefer MCP `create_issue` per `lex-mcp` rule 1, fallback `gh issue create`):

```bash
# Preferred MCP
mcp.github.create_issue(
    owner=owner, repo=repo,
    title="{type}: {summary}",
    body=body_content,
    labels=["feature request ➕"],  # or applicable template label
    assignees=["@me"],
)

# CLI fallback
gh issue create \
  --title "{type}: {summary}" \
  --body-file /tmp/plan-body.md \
  --label "feature request ➕" \
  --assignee "@me"
```

Capture the returned `{N}` number.

### Step 3: Verify Issue Type

Per `lex-issue-type-verified`, confirm that the native type was applied by the template:

```bash
gh api repos/{owner}/{repo}/issues/{N} --jq '.type.name'
```

If empty (creation via CLI without a template), apply manually:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{N} -f type={Feature|Task|Bug|Epic}
```

### Step 4: Create branch via `gh issue develop`

```bash
gh issue develop {N} --base main --name {type}/{N}-{slug}
```

`{slug}` is the kebab-case version of the summary (max 50 chars). This command registers the branch as "Development" in the GitHub sidebar, satisfying HARD-GATE precondition (c).

### Step 5: Create worktree

Per `lex-git-worktrees`:

```bash
git fetch origin {type}/{N}-{slug}
git worktree add .worktrees/{N}-{slug} {type}/{N}-{slug}
```

### Step 6: Materialize local cache via kata-load-plan-from-issue

Run `kata-load-plan-from-issue` passing `{N}` — materializes `.plans/{N}.md` mirroring the body just written. This ensures that subsequent AI edits have a local reference cache (populates `<!-- not-flushed -->` blocks with working notes during execution).

### Step 7: Apply `status: todo` label and confirm with the user

```bash
gh issue edit {N} --add-label "status: todo"
```

Confirm with the user:

> "Plan registered in #{N} (canonical body). Branch `{type}/{N}-{slug}` and worktree `.worktrees/{N}-{slug}/` ready. Local cache in `.plans/{N}.md`. Status: todo. May I start?"

Wait for user OK before any subsequent irreversible execution.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Canonical Issue body | Markdown (Summary + Plan section) | GitHub Issue `{N}` |
| Remote branch | git ref | `origin/{type}/{N}-{slug}` |
| Worktree | git worktree | `.worktrees/{N}-{slug}/` |
| Local cache | Markdown | `.plans/{N}.md` (gitignored) |
| Label | GitHub label | `status: todo` on the Issue |

## Execution Example

### Input

```
Task: migrate plan storage to the Issue-as-plan model
(3-layer: Issue body + .plans/ cache + .issues/ artifacts)
```

### Step 2 — Body written on Issue #96

```markdown
## Summary

**As** an Ahrena framework contributor,
**I want** to migrate plan storage to a 3-layer model,
**So that** plans live where they belong (audit in GitHub Issue,
scratch in .plans/ cache, Phase artifacts in .issues/).

## Plan

### Objective
Refactor the plan storage layer so that it lives in three
layers with clear roles: Issue body (canonical) + .plans/{N}.md
(AI working memory, gitignored) + .issues/{N}/ (committed Phase
artifacts).

### Steps
- [ ] Step 1 — Open Issue + branch + worktree (HARD-GATE)
- [ ] Step 2 — ADR-002
- [ ] Step 3 — Rewrite lex-agent-planning (3 langs)
- [ ] Step 3.5 — Split lex-issue-status (3 langs)
...

### Dependencies
plan-043 (PR #93) merged.

### Risks
- .plans/ lost on fresh clone — mitigated by kata-load-plan-from-issue.
- Conflicting flush across sessions — preflight detects drift.
...

### Open Questions
All resolved on 2026-05-11 (see draft).
```

### Step 4 — Branch created

```
$ gh issue develop 96 --base main --name feat/96-issue-as-plan-and-issues-folder
github.com/guardiatechnology/ahrena/tree/feat/96-issue-as-plan-and-issues-folder
```

### Step 7 — User confirmation

```
Agent: "Plan registered in #96 (canonical body).
  Branch feat/96-issue-as-plan-and-issues-folder and worktree
  .worktrees/96-issue-as-plan-and-issues-folder/ ready.
  Local cache in .plans/96.md.
  Status: todo. May I start?"
```

## Restrictions

- **Never apply `status: todo` before Step 7** — `lex-agent-planning` HARD-GATE requires all 5 canonical steps completed.
- **Never create a `.claude/plans/*.md` file as canonical** — legacy pre-ADR-002 model. The Issue body is canonical; `.plans/{N}.md` is the regenerable cache.
- **Never skip the user OK in Step 7** — subsequent irreversible execution requires explicit confirmation.
- **Never omit Summary or Plan sections** — a body without Summary, Steps, Risks, Dependencies, Open Questions does not satisfy HARD-GATE precondition (e).
- **Prefer MCP > CLI** — per `lex-mcp` rule 1.

## References

- `lex-agent-planning` — Law (3-layer model)
- `lex-issue-status` — canonical labels (`status: todo` applied in Step 7)
- `lex-issue-quality` — Issue body requirements
- `lex-issue-type-verified` — Issue Type verification
- `lex-issue-first`, `lex-git-branches`, `lex-git-worktrees` — preconditions
- `lex-mcp` — MCP preference + CLI fallback
- `codex-agent-planning` — operational manual
- ADR-002 — 3-layer storage model
- `kata-load-plan-from-issue` — Step 6 (materializes local cache)
- `kata-flush-plan-to-issue` — used in subsequent transitions (not in this kata)
- `kata-create-subtasks` — Eunomia subtask mode (child Issue decomposition)
- `warrior-eunomia` — top-level owner of this kata
