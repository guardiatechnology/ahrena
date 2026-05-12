# Cry: Scaffold Isolated Anthropic Subagent

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Engineering — Agents (pre-operational stage): quickly create a standalone Anthropic subagent without the full POV cycle

## Description

Shortcut to invoke `kata-agent-author` directly and create an isolated Anthropic subagent at `.claude/agents/<slug>.md` (or inside a plugin, delegated to plan-034). For trivial cases where the full POV cycle (`cry-pov`) is overhead — just a `.md` file with Anthropic frontmatter and declared identity is enough. The generated subagent **always** declares `stage: pre-operational` by construction; if the PoV matures, promotion to `operational-concrete` goes through DoOC (`lex-agent-construction-directives`).

## Invocation

```
/cry-agent --slug <name> --description "..." [--persona <warrior>] [--target <path>] [--from-pov <path>]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `--slug` | Yes | Identifier in kebab-case (1-64 chars, `[a-z0-9-]`) | `reconciliation-assistant` |
| `--description` | Yes | Short description (1-2 sentences) — goes to the frontmatter | `"Suggests bank-statement-to-ledger pairings"` |
| `--persona` | No | Imports base identity from an existing warrior | `warrior-apollo` |
| `--target` | No | Destination path. Default `.claude/agents/<slug>.md` | `.claude/agents/`, `plugins/foo/agents/` |
| `--from-pov` | No | Imports from an existing PoV | `docs/reconciliation/agents-pov/rec-pov-classifier/` |
| `--force` | No | Overwrites existing file | (flag) |

## What the Command Does

1. Validates `--slug` (kebab-case, no consecutive `--`)
2. Resolves `--target` (default `.claude/agents/`)
3. Invokes `kata-agent-author` with the received parameters
4. Persists file `<slug>.md` with Anthropic frontmatter + minimum body (Identity + `stage: pre-operational` + Capabilities + Restrictions)
5. Reports the final path and applied validations

## Prompt Template

```
Create a standalone Anthropic subagent by invoking kata-agent-author.

Slug: {{slug}}
Description: {{description}}
{% if persona %}Base persona: {{persona}}{% endif %}
{% if from_pov %}PoV origin: {{from_pov}}{% endif %}
{% if target %}Destination: {{target}}{% endif %}

Ensure:
- Correct Anthropic frontmatter (`name`, `description`)
- Literal `stage: pre-operational` line in the body
- No remaining placeholders

Report the final path and the tree of the generated file.
```

## Invocation Example

**Input:**

```
/cry-agent --slug reconciliation-assistant \
           --description "Suggests bank-statement-to-ledger-entry pairings at pre-operational stage"
```

**Expected output:**

```
🛠  cry-agent — standalone scaffold
   slug: reconciliation-assistant
   target: .claude/agents/reconciliation-assistant.md

→ kata-agent-author
   ✅ frontmatter validated
   ✅ stage: pre-operational declared
   ✅ file created

Content (excerpt):
   ---
   name: reconciliation-assistant
   description: Suggests bank-statement-to-ledger-entry pairings at pre-operational stage
   ---
   # Reconciliation Assistant
   ## Identity
   stage: pre-operational
   ...

Next steps:
   - Iterate the subagent body as needed
   - When a structured PoV cycle is needed, consider /cry-pov --kind subagent
```

**Input (importing from an existing PoV):**

```
/cry-agent --slug reconciliation-assistant \
           --description "Suggests bank-statement-to-ledger pairings" \
           --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/
```

**Expected output:**

```
🛠  cry-agent — standalone scaffold (--from-pov)
   slug: reconciliation-assistant
   importing from: docs/reconciliation/agents-pov/rec-pov-classifier/

→ kata-agent-author
   ✅ persona imported from pov.md
   ✅ Capabilities and Restrictions copied from system-prompt.md
   ✅ stage: pre-operational preserved
   ✅ file created at .claude/agents/reconciliation-assistant.md
```

## Restrictions

- `--slug` must follow the Anthropic Agent Skills spec restrictions (kebab-case; no consecutive `--`; no leading/trailing hyphen).
- `--description` must be concrete (no placeholder).
- The generated subagent **always** has `stage: pre-operational` — promotion to `operational-concrete` requires DoOC.
- The Cry **does not** invoke `lex-*` or `codex-*` directly (`lex-pilars`); orchestration is the kata's responsibility.
- When `--target` points inside a plugin, **plan-034** is responsible for registering the subagent in the plugin manifest; this cry only creates the file.

## Difference from `cry-pov`

| Aspect | `cry-agent` | `cry-pov` |
|---|---|---|
| **Nature** | Trivial scaffold | Full POV cycle |
| **Output** | 1 `.md` file | `docs/{context}/agents-pov/{agent}/` + implementation |
| **When to use** | Scope and tooling are clear; just the file is needed | Start of a real PoV with a customer |
| **Directives** | Declared identity (minimum Directive 01) | The 6 Directives applied at pre-operational rigor |

---

**Model:** This Cry is the shortcut for trivial creation. For structured PoVs, prefer `cry-pov` (full cycle).
