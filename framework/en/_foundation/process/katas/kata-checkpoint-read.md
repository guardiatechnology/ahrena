# Kata: Read Session Checkpoint

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Start of session with an AI agent, per `lex-checkpoint`

## Objective

Locate `.checkpoint` at the workspace root, validate the schema, present a summary to the user, and ask whether to resume the saved context. When the schema is old, emit a deprecation warning and proceed as if no checkpoint were present.

## When to Use

- At the start of every session with an AI agent, before any other activity (automatic trigger per `lex-checkpoint` rule 1)
- When the user explicitly invokes it to review the saved context
- After a `git pull` that may have brought workspace changes (rare — `.checkpoint` is gitignored, but configured paths may change)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Workspace root | Yes | Directory in which to look for `.checkpoint` (default: `pwd` at session start) |
| Presentation mode | No | `summary` (default — short summary) or `full` (full checkpoint content) |

## Workflow

```
Progress:
- [ ] 1. Locate .checkpoint
- [ ] 2. Detect schema (new, old, missing)
- [ ] 3. Present to the user (summary or warning)
- [ ] 4. Capture decision (resume, discard, ignore)
- [ ] 5. Apply decision in session context
```

### Step 1: Locate `.checkpoint`

1. Look for `.checkpoint` at the workspace root (workspace = `pwd` or directory passed as input).
2. If it does not exist: status `absent` → proceed to Step 5 without reading.
3. If it exists: status `present` → proceed to Step 2.

### Step 2: Detect schema

1. Read the first line of the file:
   - `# Session checkpoint` → new schema
   - `# Checkpoint` (without "Session") → old schema
   - Other content → unknown schema (treat as old: warning + ignore)
2. For new schema: validate the presence of at least one of `## Session focus`, `## Active plans`, `## Open threads`, or `## Notes`. If none of the 4 sections exists, downgrade to unknown schema.
3. For old or unknown schema: DO NOT parse the content. Only record status for Step 3.

### Step 3: Present to the user

**Case new schema:**

```
I found a `.checkpoint` (current schema):
  - Session focus: {first line of Session focus, max 100 chars}
  - Active plans: {compact list of plan-IDs}
  - Open threads: {N items}
  - Last update: {timestamp in relative format, e.g.: "2h ago"}

Do you want to resume this context or start a new window?
```

In `full` mode, present the full content of the 4 sections.

**Case old schema:**

```
⚠️  I found a `.checkpoint` in old schema (pre-issue #73).
   The content will be ignored and overwritten on the next invocation of
   `cry-checkpoint` or when ending the session.

   To discard now: `rm .checkpoint`
   To preserve as Notes: copy the content manually before saving.

Proceeding as if no checkpoint were present.
```

DO NOT offer the resume option — the old schema is not safely parseable.

**Case missing:**

Emit nothing. Proceed silently. The absence of `.checkpoint` is a valid scenario (per `lex-checkpoint` rule 1.5).

### Step 4: Capture decision (only for new schema)

Wait for the user's response:

- **"resume" / "yes" / "r"** → status `resume`; the agent loads context into session memory and makes it available for further decisions.
- **"new" / "discard" / "n"** → status `discard`; the agent marks `.checkpoint` for overwrite on the next save invocation (does not delete yet — the user may change their mind).
- **"ignore" / silence on timeout** → status `ignore`; the agent proceeds without applying context, but does NOT mark for overwrite; the current checkpoint remains intact.

### Step 5: Apply decision

- `resume`: place Active plans, Open threads, Session focus into the active session context. Notes remain available on demand but are not automatically presented.
- `discard`: clear the session context, mark `.checkpoint` for overwrite.
- `ignore`: proceed without applying.
- `absent` / `old schema`: proceed without applying.

### Step 6: Final Validation

- [ ] User decision was captured (or inferred via timeout)
- [ ] Session context reflects the decision (resume = applied; others = no application)
- [ ] Old schema emitted a visible warning to the user
- [ ] Missing checkpoint did NOT emit a warning (silent is correct)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Checkpoint summary presented to the user | Markdown text | Terminal/IDE |
| Operation status (`resume`, `discard`, `ignore`, `absent`, `deprecated_schema`) | Internal enum | Session context |
| Loaded context (only if `resume`) | Structured (Session focus, Active plans, Open threads, Notes) | Session memory |

## Example Execution

### Input

Workspace root: `/Users/dev/workspace/guardia/tooling/ahrena`
Mode: `summary` (default)

### `.checkpoint` content

```markdown
# Session checkpoint

- **Last update:** 2026-05-09T22:30:00Z
- **Session id:** abc1234

## Session focus

Repositioning lex-checkpoint in parallel with plan-026 review.

## Active plans

- `plan-026` — commit-readiness-observer; awaiting adjustment
- `plan-040` — `.checkpoint` repositioning; drafting

## Open threads

- Evaluate absorption of "Session risks" in lex-agent-planning
- Decide the clade for Brand-related cries

## Notes

Discussion link about kata-quality-gate: https://...
```

### Output

```
I found a `.checkpoint` (current schema):
  - Session focus: Repositioning lex-checkpoint in parallel with plan-026 review
  - Active plans: plan-026, plan-040
  - Open threads: 2 items
  - Last update: 2h ago

Do you want to resume this context or start a new window?
```

## Restrictions

- DOES NOT modify `.checkpoint` under any scenario (read-only operation)
- DOES NOT attempt to parse the old schema — only detects and emits warning
- DOES NOT fail if `.checkpoint` is missing — absence is a valid scenario
- DOES NOT write verbose log details of the content (Notes may contain sensitive personal info)
- Presentation mode respects the declared preference — does not flood the terminal with full content if mode is `summary`
