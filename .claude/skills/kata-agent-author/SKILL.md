---
name: kata-agent-author
description: "Scaffold Isolated Anthropic Subagent. Engineering — Agents (pre-operational stage): create a standalone Claude Code subagent with correct Anthropic frontmatter"
---

# Kata: Scaffold Isolated Anthropic Subagent

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): create a standalone Claude Code subagent with correct Anthropic frontmatter

## Workflow

```
Progress:
- [ ] 1. Validate slug and destination path
- [ ] 2. Compose Anthropic frontmatter
- [ ] 3. Compose the subagent body
- [ ] 4. Persist the file
- [ ] 5. Verify minimum conformance
```

### Step 1: Validate slug and destination path

- `--slug` must be kebab-case, 1-64 chars, `[a-z0-9-]`, no consecutive `--`, no leading or trailing hyphen.
- Resolve `--target`. Default: `.claude/agents/<slug>.md`. If a different path is passed (e.g., `<plugin-root>/agents/<slug>.md`), ensure the directory exists.
- If a file already exists at the destination, require `--force`.

### Step 2: Compose Anthropic frontmatter

Minimum frontmatter per the Claude Code subagents spec:

```yaml
---
name: <slug>
description: <literal description from --description>
---
```

If `--from-pov` was passed, read `docs/{context}/agents-pov/overview.md` and populate `description` with the persona declared there (1 sentence).

### Step 3: Compose the subagent body

Minimum body structure (the user can expand later):

```markdown
# <Readable name derived from the slug>

## Identity

stage: pre-operational

<persona content; if --from-pov, copies the persona block from overview.md; if --persona, imports identity from the referenced warrior>

## Capabilities

- <capability 1>
- <capability 2>

## Restrictions

- Does not persist data beyond the current context window
- Does not execute outside the scope declared in `description`

## Notes

- Created by kata-agent-author on <ISO date>
- Origin: <`--from-pov path` | standalone | warrior reference>
```

If `--from-pov` was passed, copy the `Identity`, `Capabilities`, `Restrictions` blocks literally from the corresponding `system-prompt.md`.

### Step 4: Persist the file

1. Write to `--target`.
2. Verify the file was written with correct permissions.
3. If the destination is `<plugin>/agents/`, **do not** register in the plugin's `manifest.skill.subagents` (plan-034's responsibility).

### Step 5: Verify minimum conformance

- [ ] Frontmatter has `name` and `description`
- [ ] The `stage: pre-operational` line appears literally in the body
- [ ] Frontmatter slug == file name (without `.md`)
- [ ] Description is a concrete sentence (not a placeholder)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `<slug>.md` | Markdown with YAML frontmatter | `.claude/agents/<slug>.md` (default) or `<plugin>/agents/<slug>.md` |

## Execution Example

### Input

```
cry-agent --slug reconciliation-assistant \
          --description "Suggests bank-statement-to-ledger-entry pairings at pre-operational stage"
```

### Output (`.claude/agents/reconciliation-assistant.md`)

```markdown
---
name: reconciliation-assistant
description: Suggests bank-statement-to-ledger-entry pairings at pre-operational stage
---

# Reconciliation Assistant

## Identity

stage: pre-operational

Assistant specialized in suggesting pairings between bank statement transactions
and ERP ledger entries from the same time window.

## Capabilities

- Suggest the most likely pairing by value + date + similar description
- Indicate confidence level (high / medium / low) per suggestion

## Restrictions

- Does not persist data beyond the current context window
- Does not execute outside the scope declared in `description`
- Does not create ERP entries (suggest only)

## Notes

- Created by kata-agent-author on 2026-05-12
- Origin: standalone
```

## Restrictions

- **Never** scaffold without `stage: pre-operational` literal — blocks conformance with `lex-agent-construction-directives`.
- **Never** a remaining placeholder (`<...>`) in the final file.
- **Never** the kata invokes Hephaestus or Apollo — the Anthropic subagent is pure markdown; there is no code to delegate.
- **Always** when the destination is inside a plugin, **plan-034** is responsible for registering it in the plugin manifest; this kata only creates the file.

---

**Model:** This Kata is the shortcut for trivial scaffolding. For structured PoVs, prefer `cry-pov` (full cycle). When the subagent is part of a plugin, plan-034 takes the relay.
