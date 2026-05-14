Save Session Checkpoint. User shortcut to write .checkpoint on demand, per lex-checkpoint

# Cry: Save Session Checkpoint

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** User shortcut to write `.checkpoint` on demand, per `lex-checkpoint`

## Usage

```
/cry-checkpoint
```

No arguments by default. The agent collects session context and writes.

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `--focus "<sentence>"` | No | Overrides the Session focus inferred by the agent | `--focus "Reviewing plan-026"` |
| `--add-thread "<line>"` | No | Adds an Open thread to the current checkpoint | `--add-thread "Evaluate X"` |
| `--note "<text>"` | No | Appends text to Notes | `--note "Link: https://..."` |
| `--dry-run` | No | Shows the content that would be written without persisting | — |

Without flags, the agent infers all fields from the session context.

## What the Command Does

1. Invokes `kata-checkpoint-save`
2. The kata collects Session focus, Active plans, Open threads, and Notes from the session context
3. Validates that the content does not duplicate the plan
4. Writes `.checkpoint` at the workspace root with the canonical schema
5. Presents confirmation to the user

## Prompt Template

```
Invoke kata-checkpoint-save with:

- Workspace root: {{pwd}}
- Session focus: {{--focus if provided, otherwise infer from session context}}
- Active plans: {{infer from plans with status: in-progress in the provider cache (.claude/plans/ for Claude Code; .cursor/plans/ for Cursor)}}
- Open threads: {{collect from context + add --add-thread if provided}}
- Notes: {{collect from context + append --note if provided}}
- Dry-run: {{--dry-run flag}}

After writing, present confirmation to the user in the format:

✅ Checkpoint saved at `.checkpoint`:
   - Session focus: {first sentence, max 100 chars}
   - Active plans: {N}
   - Open threads: {N}
   - Notes: {present | empty}
```

## Invocation Example

**Input:**

```
/cry-checkpoint
```

**Expected output:**

```
Collecting session context...

Session focus: Repositioning lex-checkpoint in parallel with plan-026 review.
Active plans: plan-026, plan-040
Open threads:
  - Evaluate absorption of "Session risks" in lex-agent-planning
  - Decide the clade for Brand-related cries
Notes: kata-quality-gate discussion link: https://...

✅ Checkpoint saved at `.checkpoint`:
   - Session focus: Repositioning lex-checkpoint in parallel with plan-026 review.
   - Active plans: 2
   - Open threads: 2
   - Notes: present
```

**Input with flags:**

```
/cry-checkpoint --add-thread "Validate with PM before PR" --note "Slack: #ahrena"
```

**Output:**

```
Adding 1 thread and 1 note to the context.

✅ Checkpoint saved at `.checkpoint`:
   - Session focus: {inferred}
   - Active plans: 2
   - Open threads: 3 (1 new)
   - Notes: present
```

## Restrictions

- DOES NOT modify plans (`plan-*.md` in the provider cache `.claude/plans/` or `.cursor/plans/`) — `cry-checkpoint` covers only `.checkpoint`
- DOES NOT write content that duplicates the plan — kata-checkpoint-save validates and blocks
- Output respects the Guardia tone (`lex-tone`, `lex-brand-voice`) — direct, no buzzwords
- Does not commit `.checkpoint` — follows gitignore per `lex-checkpoint` rule 4
- `--dry-run` shows but does not write

## Difference from Kata

| Aspect | `cry-checkpoint` | `kata-checkpoint-save` |
|---------|------------------|------------------------|
| **Nature** | User shortcut | Full procedure |
| **Invocation** | `/cry-checkpoint` (1 line) | Called by `cry-checkpoint` or by other warriors |
| **Configures the agent?** | No | Yes — defines triggers, validation, format |
| **Output** | Write + confirmation | Write + status + confirmation |
