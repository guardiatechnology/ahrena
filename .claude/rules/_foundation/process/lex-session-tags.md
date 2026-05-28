# Lexis: Session Tags

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Semantic tags attached to each Claude Code session, surfaced to humans in the statusline, the VSCode extension sidebar, and the Eunomia plans digest

## Law

> **Every Claude Code session that opts into `session_tracking.tags.enabled` MUST carry at most 3 tags in its heartbeat file: exactly one `kind` (the 1st slot, drawn from the controlled vocabulary in `session_tracking.tags.kinds`) and 0–2 `topics` (free-form, lowercase, kebab-case, ≤ 20 characters each). Tags MUST live under the `tags` object of `.ahrena/workflow/sessions/<session-id>.json` per `codex-session-tracking` §9. Inventing a `kind` outside the configured vocabulary, exceeding 3 slots, or persisting tags in any location other than the heartbeat JSON is FORBIDDEN.**

## Coverage

- **Applies to:** every Claude Code session running in a repository with `session_tracking.enabled: true` and `session_tracking.tags.enabled: true` in `.ahrena/.directives`.
- **Bound agents:** every agent that writes a heartbeat (`kata-session-heartbeat`), suggests tags (`kata-session-tag-suggest`), or accepts user overrides (`cry-tags`). Surface consumers (statusline script, ahrena-vscode extension, Eunomia digest) read but do not author.
- **Exceptions:** sessions running outside Claude Code (no `CLAUDE_CODE_SESSION_ID`) skip tags silently along with the heartbeat. Sessions in repositories without the `tags` block in `.directives` keep heartbeats without `tags` — backward-compatible.

## Rules

### 1. Slot model

The `tags` object has exactly two keys:

```json
"tags": {
  "kind": "tech-task",
  "topics": ["reconciliation", "api"]
}
```

- `kind` (slot 1): single string, mandatory when `tags` is present, drawn from `session_tracking.tags.kinds` in `.directives`.
- `topics` (slots 2–3): array of 0 to 2 strings, free-form, recommended lowercase kebab-case, each ≤ 20 characters.

Flat arrays (`"tags": ["tech-task", "reconciliation", "api"]`), nested structures, or extra keys are FORBIDDEN.

### 2. Controlled vocabulary for `kind`

`kind` MUST exactly match one of the values in `session_tracking.tags.kinds`. The default vocabulary covers the common intents of the Issue-Driven flow: `tech-task`, `bug`, `spike`, `user-story`, `epic`, `chore`, `design`, `review`, `exploration`, `release`.

A project MAY extend the list in its own `.ahrena/.directives`, but additions are PR-gated to keep the vocabulary small and aggregatable in the Eunomia digest.

### 3. Free-form `topics`

`topics` are not validated against any list. Recommended shape: lowercase, kebab-case (`reconciliation-engine`, `pix-integration`). The agent SHOULD warn when a topic is uppercase, contains spaces, or exceeds 20 characters, but MUST NOT reject — correction stays with the user via `cry-tags set`.

### 4. Heartbeat as the only source of truth

Tags MUST be persisted only in the heartbeat JSON at `.ahrena/workflow/sessions/<session-id>.json`. Duplicating tags into plan front-matter, Issue body, PR body, commit messages, or any other location is FORBIDDEN — every reader (statusline, extension, digest) reads the heartbeat directly. The PR "Session Trace" section (built by `kata-pr-prepare`) MAY include tags as derived information from the heartbeats it aggregates, but the heartbeat remains canonical.

### 5. Auto-suggestion is silent with visibility note

When `session_tracking.tags.auto_suggest: true` and the heartbeat for the current session has no `tags` object, the agent invokes `kata-session-tag-suggest` on the first user turn, writes the inferred tags via `kata-session-heartbeat`, and emits a one-line visibility note in the same response (format: `tagged: [kind] [topic1] [topic2]`). The user keeps full control via `/cry-tags set`, `/cry-tags clear`, or `/cry-tags --auto-suggest` to re-infer.

Re-running auto-suggest when `tags` is already present is FORBIDDEN — tags are session-scoped and only the user clears them.

### 6. Backward compatibility

Heartbeats written before tags existed (no `tags` key) remain valid. Every reader MUST treat the `tags` field as optional and render gracefully when absent (e.g., the statusline shows `main ahrena` with no chip; the digest line omits the tag column for that session).

```
<HARD-GATE>
Every agent MUST NOT write a session heartbeat containing `tags`
without satisfying ALL preconditions:

  (a) `session_tracking.tags.enabled: true` in `.ahrena/.directives`
  (b) `tags.kind` is a string drawn from `session_tracking.tags.kinds`
  (c) `tags.topics` is an array of 0 to 2 strings
  (d) Total slots used ≤ 3 (1 kind + up to 2 topics)
  (e) The shape is the object form `{kind, topics: [...]}` —
      flat arrays or extra keys are rejected
  (f) The destination path is `.ahrena/workflow/sessions/<id>.json`
      (no duplication to plan front-matter, Issue/PR body, or
      commit messages)

This rule applies to EVERY Claude Code session, regardless of:
  - perceived size ("it is just one tag")
  - urgency ("the user wants to see it now")
  - team confidence ("we already validated the kind")
  - inference confidence ("I am sure this is a bug")

Single declared exception: sessions running outside Claude Code
(no `CLAUDE_CODE_SESSION_ID`) skip the heartbeat and tags
silently, with no error and no fallback persistence.
</HARD-GATE>
```

## Examples

### Correct

```json
{
  "session_id": "85846253-4edf-443d-b294-187ef287d1bb",
  "plan_id": "321",
  "branch": "feat/321-session-tags-foundation",
  "tags": {
    "kind": "tech-task",
    "topics": ["session-tracking", "framework"]
  },
  "last_heartbeat": "2026-05-28T04:10:00Z"
}
```

```
User: /cry-tags set bug reconciliation api
Agent: tags updated → [bug] [reconciliation] [api]
```

### Incorrect

```json
"tags": ["tech-task", "reconciliation", "api"]
```
Flat array — violates rule 1.

```json
"tags": {"kind": "documentation", "topics": []}
```
`documentation` is not in the default `kinds` list; either add it to the project `.directives` (PR-gated) or pick from the controlled vocabulary.

```json
"tags": {"kind": "tech-task", "topics": ["a","b","c"]}
```
Three topics — exceeds the 2-slot cap. Total would be 4 (1 kind + 3 topics).

## Automated Validation

- **Tool:** JSON schema validator on heartbeat write (`kata-session-heartbeat`); `cry-tags` rejects out-of-vocabulary `kind` with a one-line error listing the configured vocabulary; Eunomia digest reads `tags` defensively and skips malformed entries.
- **Timing:** every heartbeat write; every `/cry-tags set` invocation; Eunomia PM loop tick.
- **Metric:** 0 heartbeats with `tags.kind` outside `session_tracking.tags.kinds`; 0 heartbeats with > 3 tag slots; 0 tags persisted outside the heartbeat JSON.
