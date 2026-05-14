# Kata: Save Session Checkpoint

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Save on demand + end of session, per `lex-checkpoint`

## Objective

Collect Session focus, Active plans, Open threads, and Notes from the current session context and write `.checkpoint` at the workspace root, respecting the canonical schema (4 sections). Silently overwrites any old schema.

## When to Use

- When the user invokes `cry-checkpoint` (explicit trigger)
- When ending the session IF context changed (new Session focus, new Active plan, new Open thread, new Notes)
- When the agent detects it is about to close the window and there is unpersisted context

DO NOT use:
- After every automatic activity (granularity lives in the plan)
- To record content already present in the plan (would duplicate `lex-agent-planning`)
- In purely operational sessions without parallel threads (no context to preserve outside the plan)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Session focus | Yes | 1-3 sentences describing the overall focus of the working window |
| Active plans | No | List of `(plan-id, 1-line context)` for plans active in the session; may be empty |
| Open threads | No | List of pending parallel threads; may be empty |
| Notes | No | Free text — links, reminders, snippets; may be empty |
| Workspace root | Yes | Directory in which to write `.checkpoint` (default: `pwd`) |

At least one of Session focus, Active plans, Open threads, or Notes must have content. An empty checkpoint is not written — `kata-checkpoint-save` returns `nothing-to-save`.

## Workflow

```
Progress:
- [ ] 1. Collect session context
- [ ] 2. Validate content (do not duplicate the plan)
- [ ] 3. Render the canonical schema
- [ ] 4. Write .checkpoint
- [ ] 5. Confirm to the user
```

### Step 1: Collect session context

1. Capture **Session focus** from the active context or ask the user in 1-3 sentences.
2. List **Active plans** — for each plan in use in the session, generate an entry `\`plan-{M}-{slug}\` — 1-line context ≤ 80 chars`. Infer from context or consult active `plan-*.md` files (status `in-progress`) in the provider cache (`.claude/plans/` for Claude Code; `.cursor/plans/` for Cursor).
3. Collect **Open threads** — ask the user or extract from recent conversation history pending decisions that did not become a plan.
4. Collect **Notes** — additional free text. May be empty.

### Step 2: Validate content (do not duplicate the plan)

Before writing, verify:

- **Session focus** does NOT contain `## Steps`, `## Closed decisions`, `## Risks` (those live in the plan)
- **Active plans** entries follow the canonical format (\`plan-{M}-{slug}\` — description) and ≤ 80 chars
- **Open threads** does NOT contain detailed task steps (if it does, move to the corresponding plan before writing)
- **Notes** does NOT contain artifacts produced (list of modified files — `git diff` covers this)

If validation detects duplication, present to the user and offer:
- Move duplicated content to the appropriate plan before writing
- Ignore and write as is (with explicit warning)

### Step 3: Render the canonical schema

Build the file content:

```markdown
# Session checkpoint

- **Last update:** {YYYY-MM-DDTHH:MM:SSZ — UTC ISO 8601}
- **Session id:** {session_id or HEAD commit short SHA}

## Session focus

{content collected in Step 1}

## Active plans

{list; if empty, omit bullets and leave the section with the text "No active plan recorded."}

## Open threads

{list; if empty, omit bullets and leave the section with the text "No open thread."}

## Notes

{free text; if empty, omit and leave the section with the text "—"}
```

Empty sections are preserved (heading kept) with a textual placeholder — the schema is canonical, not optional.

### Step 4: Write `.checkpoint`

1. Final path: `{workspace_root}/.checkpoint`
2. Atomic write: write to `.checkpoint.tmp` and `mv` to `.checkpoint` (avoids corruption on interruption)
3. Encoding UTF-8, LF line endings
4. Silent overwrite of any old schema present
5. Validate that `.gitignore` contains `.checkpoint` (per `lex-checkpoint` rule 4); if not, alert the user (but write anyway)

### Step 5: Confirm to the user

```
✅ Checkpoint saved at `.checkpoint`:
   - Session focus: {first sentence, max 100 chars}
   - Active plans: {N}
   - Open threads: {N}
   - Notes: {present | empty}
```

### Step 6: Final Validation

- [ ] `.checkpoint` exists at the workspace root
- [ ] First line is `# Session checkpoint` (not `# Checkpoint`)
- [ ] The 4 sections (Session focus, Active plans, Open threads, Notes) are present
- [ ] No forbidden sections (Activity, Status, Progress, Decisions made, Next steps, Artifacts produced)
- [ ] `.gitignore` covers `.checkpoint`
- [ ] Confirmation was shown to the user

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `.checkpoint` | UTF-8 Markdown with canonical schema | Workspace root |
| Status (`saved`, `nothing-to-save`, `validation-warning`, `gitignore-missing`) | Internal enum | Session context |
| Confirmation to the user | Markdown text | Terminal/IDE |

## Example Execution

### Input

```
Session focus: "Repositioning lex-checkpoint in parallel with plan-026 review."
Active plans:
  - plan-026 (commit-readiness-observer; awaiting adjustment)
  - plan-040 (.checkpoint repositioning; drafting)
Open threads:
  - Evaluate absorption of "Session risks" in lex-agent-planning
  - Decide the clade for Brand-related cries
Notes: "kata-quality-gate discussion link: https://..."
Workspace: /Users/dev/workspace/guardia/tooling/ahrena
```

### Output (`.checkpoint`)

```markdown
# Session checkpoint

- **Last update:** 2026-05-10T01:55:00Z
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

kata-quality-gate discussion link: https://...
```

### Confirmation

```
✅ Checkpoint saved at `.checkpoint`:
   - Session focus: Repositioning lex-checkpoint in parallel with plan-026 review.
   - Active plans: 2
   - Open threads: 2
   - Notes: present
```

## Restrictions

- DOES NOT write content that duplicates the plan (Activity, Steps, Artifacts produced)
- DOES NOT handle the old schema — overwrites silently
- DOES NOT emit empty save — a checkpoint without content returns `nothing-to-save`
- DOES NOT write if the workspace is read-only or permissions prevent it (alerts the user)
- Write is atomic (tmp + mv) — interruption mid-save does not corrupt
- DOES NOT commit `.checkpoint` — remains gitignored per `lex-checkpoint` rule 4
