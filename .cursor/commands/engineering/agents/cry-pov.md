---
description: "Agent PoV Cycle. Engineering — Agents (pre-operational stage): main entry point to create an agent PoV via the Anthropic stack with native observability"
---

# Cry: Agent PoV Cycle

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Engineering — Agents (pre-operational stage): main entry point to create an agent PoV via the Anthropic stack with native observability

## Invocation

```
/cry-pov --context <name> --kind <skill|subagent|plugin> --problem "..." --value-metric "..." [--tier N] [--dry-run]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `--context` | Yes | Bounded context in kebab-case | `reconciliation` |
| `--kind` | Yes | Anthropic artifact type | `skill`, `subagent`, `plugin` |
| `--problem` | Yes | Customer problem in 1 sentence | `"Accounting team spends 3h/day reconciling statements"` |
| `--value-metric` | Yes | Leading metric with window and threshold | `"% automatic reconciliation ≥ 60% in 4 weeks"` |
| `--tier` | No | Criticality tier (default: 3) | `3` |
| `--dry-run` | No | Lists artifacts to create without persisting | (flag) |
| `--force` | No | Overwrites an existing PoV in the same `--context` | (flag) |

## What the Command Does

1. Resolves `--context` and prepares `docs/{context}/agents-pov/`
2. Invokes `warrior-claudionor`, who triggers in sequence:
   - `kata-pov-scope-define` → `overview.md`
   - `kata-pov-system-prompt` → `system-prompt.md`
   - `kata-pov-tools-select` → `tools.md`
   - `kata-pov-context-curate` → `context-pack.md`
   - `kata-pov-observability-instrument` → `observability/`
   - `kata-pov-feedback-attach` → `feedback.md`
   - `kata-pov-value-track` → `value-proof.md` (initial template)
3. Dispatches implementation per `--kind`:
   - `skill` → `kata-skill-implement` (delegates widgets to Hephaestus, Python to Apollo)
   - `subagent` → `kata-agent-author --from-pov docs/{context}/agents-pov/`
   - `plugin` → delegates to plan-034 (orthogonal capability). If plan-034 is not merged, aborts with a clear message
4. Reports the final tree of `docs/{context}/agents-pov/` + paths of the implementation artifacts

## Prompt Template

```
You are starting an agent PoV. Take the warrior-claudionor role
(Pre-operational Agent Factory) and run the complete POV cycle.

Context: {{context}}
Kind: {{kind}}
Problem: {{problem}}
Value metric: {{value_metric}}
Tier: {{tier | default: 3}}

Execute the 7 POV katas in sequence, persisting each output to
docs/{{context}}/agents-pov/. Apply the 6 Construction Directives
(lex-agent-construction-directives) at pre-operational rigor. Ensure
that `stage: pre-operational` appears literally in system-prompt.md.

Then dispatch the implementation per --kind:
- skill: kata-skill-implement
- subagent: kata-agent-author --from-pov
- plugin: delegate to plan-034 (abort if unavailable)

At the end, report the full tree and status (ready to operate / pending
fields / blocked by dependency).
```

## Invocation Example

**Input:**

```
/cry-pov --context reconciliation \
         --kind skill \
         --problem "Accounting team spends 3h/day reconciling bank statements with ERP entries" \
         --value-metric "% automatic reconciliation ≥ 60% in 4 weeks"
```

**Expected output:**

```
🛠  warrior-claudionor — PoV cycle started
   context: reconciliation
   kind: skill
   tier: 3 (default)

Phase 1/8 — kata-pov-scope-define
   ✅ overview.md created (primary use case: statement↔entry pairing;
      discontinuation criterion: < 30% after 4 weeks)

Phase 2/8 — kata-pov-system-prompt
   ✅ system-prompt.md (stage: pre-operational declared)

Phase 3/8 — kata-pov-tools-select
   ✅ tools.md (str_replace_editor + code execution; no custom MCP)

Phase 4/8 — kata-pov-context-curate
   ✅ context-pack.md (4 positive few-shot + 2 anti-patterns; PII anonymized)

Phase 5/8 — kata-pov-observability-instrument
   ✅ observability/{traces-spec,prompts-log,tool-calls-log,value-metrics}.md

Phase 6/8 — kata-pov-feedback-attach
   ✅ feedback.md (objective metric: operator approval within 7 days)

Phase 7/8 — kata-pov-value-track
   ✅ value-proof.md (template; fortnightly cadence — tier-3)

Phase 8/8 — Implementation (--kind=skill)
   → kata-skill-implement
     ↳ warrior-hephaestus: no widget needed in this PoV (CLI/headless)
     ↳ warrior-apollo: similarity script in scripts/match_transactions.py
   ✅ skill in skills/reconciliation-pov-skill/

Next steps:
   - Operate the PoV for 4 weeks; run kata-pov-value-track fortnightly
   - When value-proof.md::status = ready-for-DoOC, invoke:
     /cry-agent-design --context reconciliation --from-pov docs/reconciliation/agents-pov/
```

## Restrictions

- `--problem` and `--value-metric` are required and must be concrete (no generalities like "automate stuff").
- `--kind=plugin` requires plan-034 merged; otherwise abort with a clear message.
- `--context` must be kebab-case and unique; if `docs/{context}/agents-pov/` already exists, require `--force` to overwrite.
- All 7 POV katas execute in sequence, no skip; failure in any one interrupts the cycle.
- The Cry **does not** invoke `lex-*` or `codex-*` directly (`lex-pilars`); the work is done by the katas via `warrior-claudionor`.

## Difference from Kata and other Cries

| Aspect | `cry-pov` | `cry-skill` | `cry-agent` |
|---|---|---|---|
| **Nature** | Full PoV cycle + implementation | Skill as distributable artifact | Standalone isolated subagent |
| **Output** | `docs/{context}/agents-pov/` + skill/subagent/plugin | `.dist/<slug>.skill/` | `.claude/agents/<slug>.md` |
| **When to use** | Prove the agent's value to the customer | Package an already mature skill | Trivial scaffold without the POV cycle |

---

**Model:** This Cry invokes `warrior-claudionor` for the full PoV cycle. For pure Skill packaging, use `cry-skill`. For trivial subagent scaffold, use `cry-agent`.
