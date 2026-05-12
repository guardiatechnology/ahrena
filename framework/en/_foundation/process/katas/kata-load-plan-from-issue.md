# Kata: Load Plan from Issue

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Materializing the local cache `.plans/{N}.md` from the canonical GitHub Issue body, per the 3-layer storage model in ADR-002

## Objective

Sync the body content of an Issue (canonical per `lex-agent-planning`) to the AI's local cache `.plans/{N}.md`. Idempotent operation: it can run as many times as needed and the result is deterministic. It runs at the start of every session that will operate on a plan and on every handoff between agents.

## When to Use

- Start of a Claude Code session (any agent: Athena, Argos, Janus, etc.) before any edit to `.plans/{N}.md`.
- Handoff between agents (e.g., Athena hands off to Argos on `to review → review`).
- Fresh clone of the repo (local cache does not exist).
- Suspicion of drift between `.plans/{N}.md` and the Issue body (e.g., another session edited the body via the GitHub UI).

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `issue_number` | Yes | Issue number (`{N}` in `{owner}/{repo}#{N}`) |
| `owner/repo` | No | Repo where the Issue lives. Default: current repo of the worktree |
| `dest_path` | No | Cache file path. Default: `<paths.plans>/{N}.md` (resolution in `lex-agent-planning`) |

## Workflow

```
Progress:
- [ ] 1. Resolve owner/repo + destination path
- [ ] 2. Try MCP `get_issue` (preferred)
- [ ] 3. Fallback `gh issue view --json body`
- [ ] 4. Write body to `.plans/{N}.md`
- [ ] 5. Validate idempotence
```

### Step 1: Resolve owner/repo + destination path

1. If `owner/repo` was passed, use it. Otherwise, derive from the worktree via `gh repo view --json owner,name`.
2. Resolve destination path:
   - If `dest_path` was passed, use it.
   - Otherwise, read `paths.plans` in `.ahrena/.directives` (default `.plans/`).
   - Final path: `<paths.plans>/{N}.md`.
3. Ensure the destination directory exists (`mkdir -p`).

### Step 2: Try MCP `get_issue` (preferred)

Per `lex-mcp` rule 1, if the GitHub MCP server is listed in `mcp.servers` and active:

```python
issue = mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)
body = issue["body"]
```

On success, skip to Step 4.

### Step 3: Fallback `gh issue view --json body`

Per `lex-mcp` rule 4 (MCP unavailable), execute the documented CLI fallback:

```bash
gh issue view {N} --repo {owner}/{repo} --json body --jq .body > .plans/{N}.md
```

If `gh` also fails:

1. Single retry after 5 seconds of backoff.
2. If it persists, offer the user: (a) try again with another command, (b) pause for investigation, (c) abort.

### Step 4: Write body to `.plans/{N}.md`

1. If `.plans/{N}.md` already exists and has content, **preserve existing `<!-- not-flushed -->` ... `<!-- /not-flushed -->` blocks**:
   - Extract all `<!-- not-flushed -->` blocks from the current file.
   - Replace the main body with the new Issue body.
   - Append the `<!-- not-flushed -->` blocks at the end.
2. If `.plans/{N}.md` does not exist, write the body directly (no `<!-- not-flushed -->` blocks yet).

Preserving local blocks enables re-load without losing AI scratch — re-load only re-syncs the canonical content.

### Step 5: Validate idempotence

After writing, execute a second (read-only) call and compare:

```bash
# Canonical comparison (after filtering not-flushed blocks from both sides)
diff <(strip-not-flushed .plans/{N}.md) <(gh issue view {N} --json body --jq .body)
```

Expected result: no difference.

If there is a difference outside `<!-- not-flushed -->` blocks, the re-load silently failed — abort and investigate.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `{N}.md` | Markdown (superset of the Issue body + preserved `<!-- not-flushed -->` blocks) | `<paths.plans>/{N}.md` |

## Execution Example

### Example Input

```
issue_number: 96
owner/repo: guardiatechnology/ahrena
dest_path: (default) .plans/96.md
```

### Example Output

`.plans/96.md` (right after the first load, no not-flushed blocks yet):

```markdown
## Summary

**As** an Ahrena framework contributor,
**I want** to migrate plan storage to a 3-layer model,
**So that** plans live where they belong.

## Plan

### Objective
Refactor the plan storage layer so that content lives in
three layers with clear roles: Issue body (canonical) + .plans/ (AI cache)
+ .issues/ (Phase artifacts).

### Steps
- [x] Step 1 — Open Issue + branch + worktree
- [x] Step 2 — ADR-002
- [ ] Step 3 — Rewrite lex-agent-planning (3 langs)
...

### Risks
- .plans/ lost on fresh clone — mitigated by kata-load-plan-from-issue.
...
```

After some AI edits to the local cache, the file carries not-flushed blocks:

```markdown
## Summary
...
(body content — mirrored)
...

<!-- not-flushed -->
## Working notes
- 23:30 — started Step 3; lex-agent-planning rewrite in pt-BR

## Next actions
1. Step 3.5 (split lex-issue-status)
2. Steps 6-8 (katas)

## Scratch
gh issue develop registers branch as "Development" in the sidebar — do not forget.
<!-- /not-flushed -->
```

## Restrictions

- **Idempotent:** multiple executions produce the same `.plans/{N}.md` for the same Issue body state.
- **Does not flush:** this kata is one-way (Issue → cache). To write back, use `kata-flush-plan-to-issue`.
- **Preserves local blocks:** existing `<!-- not-flushed -->` ... `<!-- /not-flushed -->` blocks in `.plans/{N}.md` are preserved; only the canonical content is re-synced.
- **MCP > CLI:** prefer MCP `get_issue` when the server is listed and active; CLI `gh issue view` is the documented fallback per `lex-mcp` rule 4.
- **Does not create an Issue:** if Issue `{N}` does not exist, the kata fails with a clear message. To create an Issue, use `kata-plan-task` (Eunomia top-level) or `kata-create-subtasks` (Eunomia subtask).

## References

- `lex-agent-planning` — 3-layer model and load/flush cadence
- `lex-mcp` — MCP preference + CLI fallback
- `codex-agent-planning` — operational manual
- ADR-002 — architecture decision
- `kata-flush-plan-to-issue` — inverse operation (cache → Issue)
- `kata-plan-task` — initial plan creation (populates the Issue body)
