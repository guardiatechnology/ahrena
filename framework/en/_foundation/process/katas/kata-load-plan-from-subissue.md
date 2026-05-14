# Kata: Load Plan from Sub-issue

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Materialization of the provider-specific local cache (`.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`) from the canonical Plan sub-issue body, per the hierarchical model of `lex-agent-planning`

## Objective

Synchronize the body of Plan sub-issue `{M}` (canonical per `lex-agent-planning`) into the provider-specific local cache. The operation is idempotent: it can run as many times as needed and the result is deterministic. It runs at the start of every session that will operate on a Plan, on every handoff between agents, and on a fresh clone of the repo.

This kata materializes the local cache from a Plan sub-issue that **already exists** on GitHub. When the sub-issue does not exist (orphan plan-file with `status: draft` in front-matter, `issue: TBD`, or plan-first scenario), this kata does NOT apply directly — the agent MUST first trigger the **plan-first promotion** defined in `lex-agent-planning` (create the parent Issue via `kata-contributing-issue`, create the Plan sub-issue via `kata-decompose-issue-into-plans` or `kata-plan-task`) and only then invoke this kata with the newly-created sub-issue number `{M}` to materialize the cache.

## When to Use

- Start of a Claude Code or Cursor session (any agent: Athena, Argos, Janus, etc.) before any edit to `.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`.
- Handoff between agents (e.g., Athena hands off to Argos at `to review → review`).
- Fresh clone of the repo (the local cache does not exist).
- Suspected drift between the local cache and the Plan sub-issue body (e.g., another session edited the body via the GitHub UI or another agent flushed in parallel).

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `subissue_number` | Yes | Number `{M}` of the Plan sub-issue |
| `owner/repo` | No | Repo where the Plan sub-issue lives. Default: current repo of the worktree |
| `dest_path` | No | Path of the cache file. Default: resolved by provider detection (see Step 1) |

## Workflow

```
Progress:
- [ ] 1. Resolve owner/repo + provider + destination path
- [ ] 2. Confirm the Plan sub-issue exists (plan-first guardrail)
- [ ] 3. Read the sub-issue body via MCP `get_issue` (preferred)
- [ ] 4. Fallback `gh issue view --json body`
- [ ] 5. Write the body to `.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`
- [ ] 6. Validate idempotency
```

### Step 1: Resolve owner/repo + provider + destination path

1. If `owner/repo` was passed, use it. Otherwise, derive from the worktree via `gh repo view --json owner,name`.
2. Detect the agent runtime:
   - Claude Code (CLI, VSCode, Desktop, claude.ai/code) → `.claude/plans/`
   - Cursor → `.cursor/plans/`
   - Other → consult `.ahrena/.directives` and ask the user if ambiguous.
3. Resolve the destination path:
   - If `dest_path` was passed, use it.
   - Otherwise, final path: `<provider-dir>/plan-{M}-{slug}.md`.
4. Ensure the destination directory exists (`mkdir -p`).

### Step 2: Confirm the Plan sub-issue exists

This kata assumes that the Plan sub-issue `{M}` already exists on GitHub. Verify:

```bash
# Preferred — via MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=M)

# CLI fallback
gh issue view {M} --repo {owner}/{repo} --json number,state,labels
```

If the sub-issue does NOT exist (HTTP 404), **do not fail as a fatal error**. The scenario is valid (orphan plan-file, plan-first path). The kata MUST return status `PROMOTION_REQUIRED` with the message:

> "Plan sub-issue #{M} not found in {owner}/{repo}, or the plan-file carries `status: draft`/`issue: TBD`. Valid plan-first scenario. Trigger the promotion per `lex-agent-planning`: `kata-contributing-issue` to create the parent Issue (if it does not yet exist), then `kata-decompose-issue-into-plans` or `kata-plan-task` to create the Plan sub-issue. After promotion, return to this kata with the sub-issue number to materialize the cache."

The invoking agent MUST treat `PROMOTION_REQUIRED` as a flow signal (trigger plan-first promotion), not a fatal failure.

If the sub-issue exists, proceed.

### Step 3: Read the sub-issue body via MCP `get_issue` (preferred)

Per `lex-mcp` rule 1, if the GitHub MCP server is listed in `mcp.servers` and active:

```python
issue = mcp.github.get_issue(owner=owner, repo=repo, issue_number=M)
body = issue["body"]
```

On success, skip to Step 5.

### Step 4: Fallback `gh issue view --json body`

Per `lex-mcp` rule 4 (MCP unavailable), execute the documented CLI fallback:

```bash
gh issue view {M} --repo {owner}/{repo} --json body --jq .body > {dest_path}
```

If `gh` also fails:

1. Single retry after a 5-second backoff.
2. If it persists, offer the user: (a) retry with another command, (b) pause for investigation, (c) abort.

### Step 5: Write the body to `.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`

1. If the local cache already exists and has content, **preserve existing `<!-- not-flushed -->` ... `<!-- /not-flushed -->` blocks**:
   - Extract all `<!-- not-flushed -->` blocks from the current file.
   - Replace the main body with the new sub-issue body.
   - Append the `<!-- not-flushed -->` blocks at the end.
2. If the local cache does not exist, write the body directly (no `<!-- not-flushed -->` blocks yet).

Preserving local blocks allows reload without losing AI scratch — reload only re-synchronizes the canonical content.

### Step 6: Validate idempotency

After writing, perform a second (read-only) call and compare:

```bash
# Canonical comparison (after stripping not-flushed blocks on both sides)
diff <(strip-not-flushed {dest_path}) <(gh issue view {M} --json body --jq .body)
```

Expected result: no difference.

If there is any difference outside `<!-- not-flushed -->` blocks, the reload silently failed — abort and investigate.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Local cache | Markdown (superset of the sub-issue body + preserved `<!-- not-flushed -->` blocks) | `.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md` |

## Execution Example

### Input

```
subissue_number: 201
owner/repo: guardiatechnology/example-repo
dest_path: (default; detected provider: Claude Code) .claude/plans/plan-201.md
```

### Output

`.claude/plans/plan-201.md` (right after the first load, no not-flushed blocks yet):

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

After some AI edits to the local cache, the file carries not-flushed blocks:

```markdown
## Summary
...
(body content — mirrored)
...

<!-- not-flushed -->
## Working notes
- 14:32 — started Step 1; LedgerEvent will inherit from DomainEvent base.

## Next actions
1. Step 2 — apply() takes LedgerEvent, returns a new immutable state.
2. Step 3 — repository.save() calls event_store.append().

## Scratch
considering discriminated union instead of class hierarchy.
<!-- /not-flushed -->
```

## Restrictions

- **Idempotent:** multiple runs produce the same local cache for the same sub-issue body state.
- **Does not flush:** this kata is one-way (sub-issue → cache). To write back, use `kata-flush-plan-to-subissue`.
- **Preserves local blocks:** existing `<!-- not-flushed -->` ... `<!-- /not-flushed -->` blocks in the local cache are preserved; only canonical content is re-synchronized.
- **Plan-first promotion:** if the Plan sub-issue `{M}` does not exist, the kata returns `PROMOTION_REQUIRED` (not a fatal error), directing the invoking agent to trigger `kata-contributing-issue` + `kata-decompose-issue-into-plans` (or `kata-plan-task`) before returning.
- **MCP > CLI:** prefer MCP `get_issue` when the server is listed and active; CLI `gh issue view` is the documented fallback per `lex-mcp` rule 4.
- **Does not create the sub-issue:** if sub-issue `{M}` does not exist, the kata fails; creation is the responsibility of `kata-plan-task` or `kata-decompose-issue-into-plans`.
- **Provider-specific:** Claude Code → `.claude/plans/`; Cursor → `.cursor/plans/`. There is no shared cache across providers.

## References

- `lex-agent-planning` — hierarchical Issue → Plan → PR model; load/flush cadence; plan-first guardrail
- `lex-mcp` — MCP preference + CLI fallback
- `codex-agent-planning` — operational manual
- `kata-flush-plan-to-subissue` — inverse operation (cache → sub-issue)
- `kata-plan-task` — initial creation of the Plan sub-issue (precondition of this kata)
- `kata-decompose-issue-into-plans` — decomposition of the parent Issue into N Plan sub-issues
