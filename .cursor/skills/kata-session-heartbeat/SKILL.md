---
name: kata-session-heartbeat
description: "Update Claude Code Session Heartbeat. Recording/updating the heartbeat of the current Claude Code session for an active plan"
---

# Kata: Update Claude Code Session Heartbeat

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Recording/updating the heartbeat of the current Claude Code session for an active plan

## Workflow

```
Progress:
- [ ] 1. Read env vars; if SESSION_ID/ENTRYPOINT absent, skip silently
- [ ] 2. Resolve heartbeat_dir from .ahrena/.directives (default .ahrena/workflow/sessions/)
- [ ] 3. Create directory if missing
- [ ] 4. Compose JSON per codex-session-tracking §2 schema
- [ ] 5. If heartbeat file already exists with same session_id, preserve started_at; otherwise started_at = now
- [ ] 6. Update last_heartbeat = now and last_activity from input
- [ ] 7. Write atomically (write + rename)
```

### Step 1 — Read environment variables

```bash
SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
ENTRYPOINT="${CLAUDE_CODE_ENTRYPOINT:-}"
AGENT_VERSION="${AI_AGENT:-}"

if [[ -z "$SESSION_ID" || -z "$ENTRYPOINT" ]]; then
  # Running outside Claude Code; heartbeat is a no-op
  exit 0
fi
```

### Step 2 — Resolve heartbeat_dir

Read `session_tracking.heartbeat_dir` from `.ahrena/.directives` (default `.ahrena/workflow/sessions/`). If `session_tracking.enabled == false`, skip silently.

### Step 3 — Ensure directory

```bash
mkdir -p .ahrena/workflow/sessions
```

(The directory is gitignored by `.gitignore` — see `codex-session-tracking` §6.)

### Step 4 — Compose JSON

```json
{
  "session_id": "<SESSION_ID>",
  "entrypoint": "<ENTRYPOINT>",
  "agent_version": "<AGENT_VERSION>",
  "plan_id": "<plan_id input>",
  "branch": "<git rev-parse --abbrev-ref HEAD>",
  "cwd": "<pwd>",
  "started_at": "<preserved from existing file OR now>",
  "last_heartbeat": "<now in ISO 8601>",
  "last_activity": "<last_activity input>",
  "role": "<role input>",
  "previous_session": "<previous_session input or null>"
}
```

### Step 5 — Preserve `started_at` on rewrite

If `.ahrena/workflow/sessions/<SESSION_ID>.json` already exists, read `started_at` from the existing file and preserve it; only `last_heartbeat` and `last_activity` change.

### Step 6+7 — Atomic write

```bash
TMP=$(mktemp)
echo "$JSON" > "$TMP"
mv "$TMP" ".ahrena/workflow/sessions/${SESSION_ID}.json"
```

Move (`mv`) is atomic on the same filesystem — avoids race when two concurrent calls happen.

## Outputs

| Output | Format | Destination |
|---|---|---|
| Heartbeat file | JSON per schema | `.ahrena/workflow/sessions/<session-id>.json` |

No mandatory stdout. The kata is silent on success. On failure (I/O error), report to stderr and propagate; the invoking agent decides whether to abort or proceed.

## Restrictions

- **No side effect beyond the heartbeat file.** Does not modify the plan, Issue, PR, or git.
- **No credentials or sensitive data in the JSON** per `codex-session-tracking`.
- **Idempotent.** Multiple rapid successive calls produce the same final file.
- **No-op outside Claude Code.** Without `CLAUDE_CODE_SESSION_ID`, the kata exits with code 0 with no error.

## Tags support

The kata accepts an optional `tags` input (or the equivalent CLI form `--set-tags <kind> [topic1] [topic2]`) governed by `lex-session-tags`.

**Invocation forms:**

```bash
# Positional (CLI ergonomics): kind first, then 0-2 topics
kata-session-heartbeat --set-tags tech-task reconciliation api

# Programmatic (kata invocation by another kata or warrior):
kata-session-heartbeat tags='{"kind":"tech-task","topics":["reconciliation","api"]}'
```

**Merge semantics:**

- When `tags` is provided: validate against `session_tracking.tags.*` in `.directives` (kind is in `kinds`; topics ≤ 2; total slots ≤ 3); replace the heartbeat's `tags` object atomically.
- When `tags` is omitted: preserve the existing `tags` object from the heartbeat on disk (along with `started_at`).
- To clear tags: pass an explicit empty object `tags={}` (rendered in the JSON as `"tags": {}` — or remove the key with `tags=null`).

**Atomic merge:**

The Step 6+7 atomic write (`mktemp` → `mv`) already preserves the rest of the JSON. The tags branch follows the same path:

```bash
EXISTING=$(cat ".ahrena/workflow/sessions/${SESSION_ID}.json" 2>/dev/null || echo '{}')
NEW=$(echo "$EXISTING" | jq --argjson tags "$TAGS_JSON" '.tags = $tags')
TMP=$(mktemp)
echo "$NEW" > "$TMP"
mv "$TMP" ".ahrena/workflow/sessions/${SESSION_ID}.json"
```

**Validation errors:**

When the validation in `lex-session-tags` fails (kind out of vocabulary, > 2 topics, malformed shape), the kata exits with code 2 and prints to stderr a one-line error listing the configured vocabulary. The heartbeat file is left untouched.

**Auto-suggest interplay:**

`kata-session-tag-suggest` is the upstream kata that produces a valid `tags` object from the first user prompt. This kata does NOT call it — it only writes what it receives. The orchestration (call-suggest-then-call-heartbeat) lives in Plan B's hook or in the user-invoked `cry-tags --auto-suggest`.
