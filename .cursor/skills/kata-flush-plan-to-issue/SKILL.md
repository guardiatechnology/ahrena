---
name: kata-flush-plan-to-issue
description: "Flush Plan to Issue. Synchronizing the local cache .plans/{N}.md to the canonical GitHub Issue body, per the 3-layer storage model in ADR-002"
---

# Kata: Flush Plan to Issue

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Synchronizing the local cache `.plans/{N}.md` to the canonical GitHub Issue body, per the 3-layer storage model in ADR-002

## Workflow

```
Progress:
- [ ] 1. Read `.plans/{N}.md`
- [ ] 2. Filter `<!-- not-flushed -->` blocks
- [ ] 3. Detect remote drift (preflight)
- [ ] 4. Write via MCP `update_issue` (preferred)
- [ ] 5. Fallback `gh issue edit --body-file`
- [ ] 6. Validate idempotence
```

### Step 1: Read `.plans/{N}.md`

Load the content of the local cache:

```bash
cat .plans/{N}.md
```

If the file does not exist or is empty, abort with a message instructing to run `kata-load-plan-from-issue` first.

### Step 2: Filter `<!-- not-flushed -->` blocks

Remove from the content all delimited blocks:

```
<!-- not-flushed -->
...any content...
<!-- /not-flushed -->
```

The result is the **candidate body** to write to the Issue. Canonical implementation via Python:

```python
import re
filtered = re.sub(
    r"<!-- not-flushed -->.*?<!-- /not-flushed -->",
    "",
    raw_content,
    flags=re.DOTALL,
)
# remove duplicated blank lines left over after filtering
filtered = re.sub(r"\n{3,}", "\n\n", filtered).strip() + "\n"
```

### Step 3: Detect remote drift (preflight)

Before writing, **read the current Issue body** and compare it with the last locally known state:

1. `gh issue view {N} --json body --jq .body` → `remote_body_now`.
2. Compare `remote_body_now` with `remote_body_at_last_load` (state saved locally in `.plans/.{N}.remote.last` or similar — optional; if missing, read at runtime).
3. If different, an **unknown remote edit** occurred (another session or an edit via the GitHub UI).

Behavior on drift detection:

| Scenario | Default | With `force=true` |
|---|---|---|
| No drift | Writes directly | Writes directly |
| With drift | **Alert** (does not write); offers: (a) show diff and abort, (b) manual merge, (c) overwrite | Writes directly (overwrites remote changes) |

The default `force=false` is more conservative — it protects against losing concurrent edits.

### Step 4: Write via MCP `update_issue` (preferred)

Per `lex-mcp` rule 1, if the GitHub MCP server is listed in `mcp.servers` and active:

```python
mcp.github.update_issue(
    owner=owner,
    repo=repo,
    issue_number=N,
    body=filtered_body,
)
```

On success, update `.plans/.{N}.remote.last` with the body just written, and skip to Step 6.

### Step 5: Fallback `gh issue edit --body-file`

Per `lex-mcp` rule 4 (MCP unavailable):

```bash
# Write candidate body to temporary file
echo "$filtered_body" > /tmp/issue-{N}-body.md

# Write to the Issue via gh
gh issue edit {N} --repo {owner}/{repo} --body-file /tmp/issue-{N}-body.md

# Clean up
rm /tmp/issue-{N}-body.md
```

If `gh` fails:

1. Single retry after 5 seconds of backoff.
2. If it persists, offer the user (per `lex-mcp` rule 4 steps 3-4): (a) try again, (b) pause, (c) abort.

### Step 6: Validate idempotence

After writing, execute `gh issue view {N} --json body --jq .body` and compare with `filtered_body`. Expected result: equal.

If there is a difference, the flush silently failed — abort and investigate (typically: encoding, escaping of special characters, or rate-limit silently dropped by GitHub).

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Updated body | Markdown (no `<!-- not-flushed -->` blocks) | Issue `{N}` on GitHub |
| `.plans/.{N}.remote.last` (optional) | Markdown | Local cache of the last known remote state (preflight for the next flush) |

## Execution Example

### Example Input

```
issue_number: 96
owner/repo: guardiatechnology/ahrena
source_path: (default) .plans/96.md
force: false
```

### `.plans/96.md` before flush

```markdown
## Summary
...

## Plan
### Steps
- [x] Step 1
- [x] Step 2
- [x] Step 3 — Rewrite lex-agent-planning (Just completed)
- [ ] Step 4
...

<!-- not-flushed -->
## Working notes
- 23:55 — finished Step 3; cache here is newer than the Issue body.

## Scratch
testing whether update_issue MCP supports body >50KB. Yes, it does (limit ~65KB).
<!-- /not-flushed -->
```

### Body written to the Issue after flush

```markdown
## Summary
...

## Plan
### Steps
- [x] Step 1
- [x] Step 2
- [x] Step 3 — Rewrite lex-agent-planning (Just completed)
- [ ] Step 4
...
```

`<!-- not-flushed -->` blocks stay only in the local cache. When another session runs `kata-load-plan-from-issue`, it receives the body without the blocks — preserving the property that canonical = Issue body.

## Restrictions

- **Idempotent:** multiple executions produce the same body if `.plans/{N}.md` has not changed.
- **Mandatory preflight (default):** without `force=true`, remote drift blocks the flush and requires human decision.
- **MCP > CLI:** prefer MCP `update_issue`; CLI `gh issue edit --body-file` is fallback per `lex-mcp` rule 4.
- **Does not create an Issue:** if `{N}` does not exist, fail immediately. To create, use `kata-plan-task`.
- **Does not touch labels nor assignees:** flush operates only on the body. Labels (including `status:*`) are the transition owner's responsibility (per `lex-agent-planning` and `lex-issue-status`).
- **Does not log content:** `<!-- not-flushed -->` filtering is silent by design — the candidate body does not leak into session logs.
