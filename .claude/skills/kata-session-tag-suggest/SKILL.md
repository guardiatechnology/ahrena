---
name: kata-session-tag-suggest
description: "Suggest Session Tags from First Prompt. Inferring a valid tags object (1 kind + up to 2 topics) from the user's first prompt and the active plan context"
---

# Kata: Suggest Session Tags from First Prompt

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Inferring a valid `tags` object (1 kind + up to 2 topics) from the user's first prompt and the active plan context

## Workflow

```
Progress:
- [ ] 1. Read kinds_vocabulary from .ahrena/.directives
- [ ] 2. Derive kind from branch type + prompt verbs + plan slug
- [ ] 3. Derive topics from prompt nouns + plan slug + scope hints
- [ ] 4. Validate against lex-session-tags (kind in vocabulary, topics ≤ 2)
- [ ] 5. Emit the {kind, topics} object as structured output
```

### Step 1 — Read vocabulary

```bash
KINDS=$(yq '.session_tracking.tags.kinds' .ahrena/.directives)
```

If `session_tracking.tags.kinds` is missing or empty, exit with code 1 — the suggestion cannot be made without a vocabulary.

### Step 2 — Derive `kind`

The agent picks one value from `kinds_vocabulary` using this signal ladder (first match wins):

| Signal | Maps to `kind` |
|---|---|
| Branch prefix `feat/` + prompt mentions a new capability | `user-story` (when the parent Issue is a User Story) or `tech-task` (when it is a Tech Task) |
| Branch prefix `fix/` + prompt mentions a bug, error, regression | `bug` |
| Branch prefix `chore/`, `ci/`, `build/`, `docs/`, `style/`, `refactor/` | `chore` |
| Prompt mentions "design", "wireframe", "mockup", "API design" | `design` |
| Prompt mentions "review", "audit", "check", "approve" + a PR/Issue ref | `review` |
| Prompt mentions "explore", "investigate", "spike", "PoC", "research" | `spike` (or `exploration` when no time-boxed deliverable) |
| Prompt mentions "release", "tag", "publish", "version bump" | `release` |
| Prompt is a question or open-ended | `exploration` |
| No signal fires | `tech-task` (safe default for the framework) |

When multiple signals fire, the **branch prefix** wins — it reflects the committed scope, not the conversation.

### Step 3 — Derive `topics`

Pick up to 2 topics in this order of preference:

1. **Plan slug** stripped of leading number: `321-session-tags-foundation` → `session-tags-foundation` → `session-tags` (kept) + `foundation` (kept).
2. **Domain noun** from the prompt: identify the most concrete domain noun (e.g., "reconciliation", "pix", "fiscal", "auth"). Lowercase, kebab-case.
3. **Repo/component** from `cwd` when the prompt is generic.

Truncate to ≤ 20 characters each. Skip topics that are too generic (`feature`, `code`, `system`, `change`).

### Step 4 — Validate

Apply the precondition checks from `lex-session-tags` HARD-GATE:

- `kind` ∈ `kinds_vocabulary`
- `topics` is an array of 0 to 2 strings
- Total ≤ 3 slots
- Object shape `{kind, topics: [...]}` (no flat array, no extra keys)

When validation fails, fall back to `{"kind": "tech-task", "topics": []}` and emit a warning to stderr — the heartbeat write is non-blocking.

### Step 5 — Emit structured output

Print a single JSON line to stdout:

```json
{"kind":"tech-task","topics":["session-tags","foundation"]}
```

The caller pipes this directly into `kata-session-heartbeat --set-tags` or renders the visibility note `tagged: [tech-task] [session-tags] [foundation]` in the agent's response.

## Outputs

| Output | Format | Destination |
|---|---|---|
| Tag suggestion | Single JSON line | stdout |
| Warning (when fallback used) | One-line text | stderr |

## Restrictions

- **No persistence.** The kata never touches the heartbeat file. Writing is the caller's job.
- **No interactive prompt.** The inference is silent; user confirmation lives in the visibility note + `cry-tags set`.
- **No re-suggestion on a heartbeat with existing tags.** The caller MUST check `tags == null` before invoking; otherwise this kata is a no-op (exit code 0, empty stdout).
- **No invention of `kind`.** Falling back to a default value is acceptable; inventing a new vocabulary value is not.
