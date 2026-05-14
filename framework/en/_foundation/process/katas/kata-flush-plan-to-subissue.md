# Kata: Flush Plan to Sub-issue

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Synchronization of the provider-specific local cache (`.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`) to the canonical Plan sub-issue body, per the hierarchical model of `lex-agent-planning`

## Objective

Persist the content of the provider-specific local cache (AI working memory) into the body of Plan sub-issue `{M}` on GitHub (canonical), filtering local blocks marked `<!-- not-flushed -->` ... `<!-- /not-flushed -->`. The operation is idempotent. It is triggered on the 4 canonical triggers of `lex-agent-planning`: each `status:` label transition on the sub-issue/PR, each completed Step (`[ ]` → `[x]`), end of session (heartbeat completes or owner exits), and handoff between agents.

## When to Use

- `status:` label transition on the Plan sub-issue or the linked PR (`todo → development`, `development → to review`, `to review → review`, etc.).
- Plan Step marked as completed (`[ ]` → `[x]`) in the local cache.
- End of a Claude Code or Cursor session (heartbeat finishes or Athena/Argos/Janus exits).
- Handoff between agents (deliver before the next agent enters).
- Explicit user request ("flush plan", "update the sub-issue").

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `subissue_number` | Yes | Number `{M}` of the Plan sub-issue |
| `owner/repo` | No | Repo where the Plan sub-issue lives. Default: current repo of the worktree |
| `source_path` | No | Path of the local cache file. Default: resolved by provider detection (`.claude/plans/plan-{M}-{slug}.md` or `.cursor/plans/plan-{M}-{slug}.md`) |
| `force` | No | `true` forces a write even if a remote edit is detected. Default: `false` (alerts + offers manual merge) |

## Workflow

```
Progress:
- [ ] 1. Resolve provider + source path
- [ ] 2. Read the local cache
- [ ] 3. Filter `<!-- not-flushed -->` blocks
- [ ] 4. Detect remote drift (preflight)
- [ ] 5. Write via MCP `update_issue` (preferred)
- [ ] 6. Fallback `gh issue edit --body-file`
- [ ] 7. Validate idempotency
```

### Step 1: Resolve provider + source path

1. If `source_path` was passed, use it.
2. Otherwise, detect the agent runtime:
   - Claude Code → `.claude/plans/plan-{M}-{slug}.md`
   - Cursor → `.cursor/plans/plan-{M}-{slug}.md`
3. If the file does not exist or is empty, abort with a message directing the user to run `kata-load-plan-from-subissue` first.

### Step 2: Read the local cache

```bash
cat {source_path}
```

Validate that the content carries the minimum canonical schema (Summary, Plan section). If the structure is missing, abort and direct the user to synchronize first via `kata-load-plan-from-subissue`.

### Step 3: Filter `<!-- not-flushed -->` blocks

Remove all delimited blocks from the content:

```
<!-- not-flushed -->
...any content...
<!-- /not-flushed -->
```

The result is the **candidate body** to write to the sub-issue. Canonical implementation in Python:

```python
import re
filtered = re.sub(
    r"<!-- not-flushed -->.*?<!-- /not-flushed -->",
    "",
    raw_content,
    flags=re.DOTALL,
)
# collapse only triple+ blank-line sequences to double; preserve indentation
filtered = re.sub(r"\n\n\n+", "\n\n", filtered).strip() + "\n"
```

The filter is silent by design — the candidate body does not leak in session logs.

### Step 4: Detect remote drift (preflight)

Before writing, **read the current sub-issue body** and compare with the last locally known state:

1. `gh issue view {M} --repo {owner}/{repo} --json body --jq .body` → `remote_body_now`.
2. Compare `remote_body_now` with `remote_body_at_last_load` (state saved locally at `.claude/plans/.{M}.remote.last` or similar — optional; if absent, read on the fly).
3. If different, there was an **unknown remote edit** (another session flushed in parallel or the body was edited via the GitHub UI).

Behavior on drift detection:

| Scenario | Default (`force=false`) | With `force=true` |
|---|---|---|
| No drift | Write directly | Write directly |
| With drift | **Alert** (no write); offer: (a) show diff and abort, (b) manual merge, (c) overwrite | Write directly (overwrites remote changes) |

The default `force=false` is more conservative — it protects against losing simultaneous edits.

### Step 5: Write via MCP `update_issue` (preferred)

Per `lex-mcp` rule 1, if the GitHub MCP server is listed in `mcp.servers` and active:

```python
mcp.github.update_issue(
    owner=owner,
    repo=repo,
    issue_number=M,
    body=filtered_body,
)
```

On success, update `.claude/plans/.{M}.remote.last` (or the Cursor equivalent) with the body just written, and skip to Step 7.

### Step 6: Fallback `gh issue edit --body-file`

Per `lex-mcp` rule 4 (MCP unavailable):

```bash
# Write the candidate body to a temporary file
echo "$filtered_body" > /tmp/subissue-{M}-body.md

# Write to the sub-issue via gh
gh issue edit {M} --repo {owner}/{repo} --body-file /tmp/subissue-{M}-body.md

# Clean up
rm /tmp/subissue-{M}-body.md
```

If `gh` fails:

1. Single retry after a 5-second backoff.
2. If it persists, offer the user (per `lex-mcp` rule 4 steps 3-4): (a) retry, (b) pause, (c) abort.

### Step 7: Validate idempotency

After writing, run `gh issue view {M} --json body --jq .body` and compare with `filtered_body`. Expected result: equal.

If there is a difference, the flush silently failed — abort and investigate (typically: encoding, special-character escaping, or rate-limit silenced by GitHub).

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Updated body | Markdown (no `<!-- not-flushed -->` blocks) | Sub-issue `{M}` on GitHub |
| `.claude/plans/.{M}.remote.last` (optional) | Markdown | Local cache of the last known remote state (preflight for the next flush) |

## Execution Example

### Input

```
subissue_number: 201
owner/repo: guardiatechnology/example-repo
source_path: (default; provider Claude Code) .claude/plans/plan-201.md
force: false
```

### `.claude/plans/plan-201.md` before the flush

```markdown
## Summary

Refactor the Ledger aggregate to event sourcing, separating commands
(write-side) from reads (read-side projection).

Parent: #200

## Plan
### Steps
- [x] Step 1 — Model LedgerEvent base class
- [x] Step 2 — Rewrite Ledger.apply() as event projection (just completed)
- [ ] Step 3 — Repository persisting events instead of state
...

<!-- not-flushed -->
## Working notes
- 15:10 — finished Step 2; cache here is newer than the sub-issue body.

## Scratch
discriminated union vs class hierarchy: class hierarchy turned out more readable.
<!-- /not-flushed -->
```

### Body written to the sub-issue after the flush

```markdown
## Summary

Refactor the Ledger aggregate to event sourcing, separating commands
(write-side) from reads (read-side projection).

Parent: #200

## Plan
### Steps
- [x] Step 1 — Model LedgerEvent base class
- [x] Step 2 — Rewrite Ledger.apply() as event projection (just completed)
- [ ] Step 3 — Repository persisting events instead of state
...
```

`<!-- not-flushed -->` blocks stay only in the local cache. When another session runs `kata-load-plan-from-subissue`, it receives the body without the blocks — preserving the property that canonical = sub-issue body.

## Restrictions

- **Idempotent:** multiple runs produce the same body if the local cache did not change.
- **Mandatory preflight (default):** without `force=true`, remote drift blocks the flush and requires a human decision.
- **MCP > CLI:** prefer MCP `update_issue`; CLI `gh issue edit --body-file` is the fallback per `lex-mcp` rule 4.
- **Does not create the sub-issue:** if `{M}` does not exist, fail immediately. To create it, use `kata-plan-task` or `kata-decompose-issue-into-plans`.
- **Does not touch labels or assignees:** the flush operates only on the body. Labels (including `status:*`) are the responsibility of the transition owner (per `lex-agent-planning` and `lex-issue-status`).
- **Does not log filtered content:** the candidate body does not appear in session logs.
- **Preserves indentation:** the blank-line collapse regex operates only on `\n\n\n+` sequences; never on horizontal spaces (which would destroy Markdown indentation of lists and code blocks).

## References

- `lex-agent-planning` — hierarchical Issue → Plan → PR model; flush cadence (4 canonical triggers)
- `lex-mcp` — MCP preference + CLI fallback
- `lex-issue-status` — canonical labels; flush is triggered on each transition
- `codex-agent-planning` — operational manual
- `kata-load-plan-from-subissue` — inverse operation (sub-issue → cache)
- `kata-plan-task` — Plan sub-issue creation (precondition)
- `kata-decompose-issue-into-plans` — decomposition of the parent Issue into N Plan sub-issues
- `kata-pr-prepare` — invokes this kata before opening the PR
- `warrior-athena`, `warrior-argos`, `warrior-janus` — agents that trigger flushes on transitions
