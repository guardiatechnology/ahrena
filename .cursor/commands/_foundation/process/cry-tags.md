---
description: "Manage Session Tags. User shortcut to read, set, clear, or re-infer the tags of the current Claude Code session, per lex-session-tags"
---

# Cry: Manage Session Tags

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** User shortcut to read, set, clear, or re-infer the tags of the current Claude Code session, per `lex-session-tags`

## Usage

```
/cry-tags <subcommand> [args]
```

## Subcommands

| Subcommand | Effect |
|---|---|
| `set <kind> [topic1] [topic2]` | Replaces the current tags object with the given values. `kind` MUST be in `session_tracking.tags.kinds`; topics are optional. |
| `show` | Prints the current tags object to the user without modifying anything. |
| `clear` | Removes the `tags` key from the heartbeat (resets to "no tags"). |
| `--auto-suggest` | Forces a fresh inference via `kata-session-tag-suggest` even if `tags` is already present, then writes the suggestion via `kata-session-heartbeat`. |

## What the Command Does

1. Reads `session_tracking.tags.*` from `.ahrena/.directives`.
2. Reads the current heartbeat at `.ahrena/workflow/sessions/<session_id>.json` (when present).
3. Dispatches by subcommand:
   - `set`: validates `kind` against the configured vocabulary; rejects with a one-line error listing the vocabulary when invalid. Invokes `kata-session-heartbeat` with the merged `tags` object.
   - `show`: prints the current `tags` object (or `"(no tags)"` when absent).
   - `clear`: invokes `kata-session-heartbeat` passing `tags=null` to remove the field.
   - `--auto-suggest`: invokes `kata-session-tag-suggest` with the user's first prompt (read from the session) + plan front-matter + branch name; pipes the JSON output into `kata-session-heartbeat --set-tags`.
4. Emits a one-line confirmation in the format `tagged: [kind] [topic1] [topic2]` (or `tags cleared` / `(no tags)`).

## Prompt Template

```
Invoke the relevant kata for the {subcommand}:

- For `set`: validate the kind against session_tracking.tags.kinds, then call
  kata-session-heartbeat with tags={kind, topics: [...]}.

- For `show`: read .ahrena/workflow/sessions/<session_id>.json and print the
  tags object or "(no tags)" when absent.

- For `clear`: call kata-session-heartbeat with tags=null.

- For `--auto-suggest`: call kata-session-tag-suggest with the first user
  prompt of the session, then pipe the JSON output into
  kata-session-heartbeat --set-tags.

After any write, emit the one-line confirmation:
  tagged: [kind] [topic1] [topic2]
or:
  tags cleared
```

## Restrictions

- DOES NOT persist tags anywhere other than the heartbeat JSON — duplication into plan front-matter, Issue body, or commit message is forbidden by `lex-session-tags` rule 4.
- DOES NOT invent `kind` values outside `session_tracking.tags.kinds`. Project additions go through PR review on `.ahrena/.directives`.
- DOES NOT operate when `session_tracking.enabled: false` or `session_tracking.tags.enabled: false` — exits silently with a one-line note.
- DOES NOT operate outside Claude Code (no `CLAUDE_CODE_SESSION_ID`) — exits silently per `lex-session-tags` exception clause.
- Output respects the Guardia tone (`lex-tone`, `lex-brand-voice`) — direct, no buzzwords.

## Difference from Kata

| Aspect | `cry-tags` | `kata-session-heartbeat` / `kata-session-tag-suggest` |
|---|---|---|
| **Nature** | User shortcut | Full procedures |
| **Invocation** | `/cry-tags <subcommand>` (1 line) | Called by `cry-tags` or by warriors |
| **Knows the vocabulary?** | Reads from `.directives`, validates user input | The kata also validates, but does not present the error message to the human |
| **Output** | Single-line user-facing confirmation | Structured JSON + exit code |
