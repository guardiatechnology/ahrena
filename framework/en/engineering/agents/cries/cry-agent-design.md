# Cry: Canonical Design of an Agent in Operational Concrete

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Engineering — Agents: entry point to lead the promotion from PoV → `operational-concrete` or `direct-entry` in production, under orchestration of `warrior-metis`

## Description

`cry-agent-design` is the canonical entry point for designing an agent at `operational-concrete` stage. It invokes `warrior-metis`, who applies the DoOC gate (`kata-dooc-validate`), orchestrates the 8 design katas, and delivers the 13-file package at `docs/{context}/agents/{agent}/`.

When `--from-pov` is provided, the cycle consumes the `warrior-claudionor` output (pre-operational PoV) and enriches the context pack with real material (few-shot, negative examples, telemetry). When absent, it operates in `direct-entry` (requires explicit ADR/PDR) or `legacy-pov` (retrofit).

## Usage

```
/cry-agent-design --context <name> --agent <slug> [--from-pov <path>] --tier <1|2|3|4> [--owner "..."] [--entry-mode <with-pov|direct-entry|legacy-pov>] [--adr <path>]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `--context` | Yes | Bounded Context (kebab-case) — `docs/{context}/agents/{agent}/` | `reconciliation` |
| `--agent` | Yes | Agent slug (kebab-case) | `rec-classifier` |
| `--from-pov` | No | Origin PoV path produced by `warrior-claudionor` | `docs/reconciliation/agents-pov/rec-pov-classifier/` |
| `--tier` | Yes | Criticality tier; tier-1/2 triggers required SLO per `lex-slo-required` | `tier-2` |
| `--owner` | No (suggested) | Name + role + escalation channel of the owner | `"Marta Souza, Lead Reconciliation, #rec-oncall"` |
| `--entry-mode` | No | Entry mode; default = `with-pov` when `--from-pov` present, `direct-entry` when absent | `with-pov` \| `direct-entry` \| `legacy-pov` |
| `--adr` | Conditional | ADR/PDR path; required in `direct-entry` and in `legacy-pov` outside the 90-day window | `docs/adr/ADR-029-rec-classifier-direct-entry.md` |

## What the Command Does

1. Invokes `warrior-metis` with the received parameters
2. Mêtis runs the full cycle:
   - Step 0 — `kata-dooc-validate` (canonical gate)
   - Steps 1-8 — 8 design katas in order
   - Step 9 — Feature ↔ Agent reciprocity
   - Step 10 — DoOC snapshot
   - Step 11 — handoff to `warrior-apollo-agents`
3. Reports the final tree of produced files
4. Declares the package ready for implementation by `warrior-apollo-agents`

## Prompt Template

```
Assume the role of warrior-metis. Lead the promotion of agent
{{agent}} in {{context}} to stage `operational-concrete`.

Canonical inputs:
- context: {{context}}
- agent: {{agent}}
- tier: {{tier}}
- owner: {{owner}}
- entry-mode: {{entry_mode}}
- from-pov: {{from_pov_path}} (when applicable)
- adr: {{adr_path}} (when direct-entry or legacy-pov outside the window)

Execute the main flow of warrior-metis:
  Step 0 — kata-dooc-validate (gate)
  Steps 1-8 — 8 design katas in deterministic order
  Step 9 — Feature ↔ Agent reciprocity
  Step 10 — DoOC snapshot
  Step 11 — handoff to warrior-apollo-agents

Constraints:
- DO NOT promote the agent without kata-dooc-validate returning `go`
- DO NOT write code (Python, TS); the package is design, not implementation
- Apply tone per lex-brand-voice (direct, strategic, affirmative, clear;
  prohibited: innovative, disruptive, transformative, revolutionary, fintech)
- Use language per language.default in .ahrena/.directives

Output format:
- Final tree under docs/{{context}}/agents/{{agent}}/
- DoOC sidecar at docs/{{context}}/dooc/{{agent}}.md
- Update in docs/{{context}}/feature-agent-map.md
- Summary with DoOC decision + produced paths + next step (handoff to Apollo-Agents)
```

## Example Invocation

**Input:**

```
/cry-agent-design \
  --context reconciliation \
  --agent rec-classifier \
  --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/ \
  --tier tier-2 \
  --owner "Marta Souza, Lead Reconciliation, #rec-oncall"
```

**Expected output (summary):**

```
🛡️  warrior-metis — APM Operational Concrete
   context: reconciliation | agent: rec-classifier | tier: tier-2 | entry-mode: with-pov

✅ DoOC gate: go (9/9 items)
✅ 13 files produced at docs/reconciliation/agents/rec-classifier/
✅ DoOC sidecar at docs/reconciliation/dooc/rec-classifier.md
✅ Feature ↔ Agent reciprocity updated at docs/reconciliation/feature-agent-map.md

Package ready for warrior-apollo-agents to implement (plan-013).
```

## Constraints

- The Cry does NOT invoke Lexis or Codex directly (per `lex-pilars`); it invokes only `warrior-metis`
- `warrior-metis` orchestrates all 9 katas internally; the Cry remains the single entry point
- In `direct-entry` without `--adr`, Mêtis aborts before orchestrating the 9 katas (argument pre-check inside `kata-dooc-validate` Step 1)
- In `legacy-pov` outside the 90-day window without `--adr`, idem
- The Cry does NOT modify `.ahrena/.directives` or `framework/`

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation (1 entry point) | Structured procedure |
| **Who orchestrates** | `warrior-metis` | Mêtis invokes the 9 katas |
| **Configures agent?** | No (it is the invoker) | Yes |
| **Example** | `/cry-agent-design ...` | `kata-dooc-validate`, `kata-agent-overview-design`, ... |

## Cross-references

- `warrior-metis` — orchestrator invoked by the Cry
- `kata-dooc-validate` — first Kata invoked by Mêtis
- `warrior-claudionor` — upstream producer of the PoV consumed via `--from-pov`
- `warrior-apollo-agents` — downstream consumer after design (per plan-013)
- `lex-agent-construction-directives`, `lex-agent-design-docs` — foundation of the applied rules

---

**Model:** The Cry is the single entry point of the Operational Concrete stage. It invokes `warrior-metis`. Mêtis applies the DoOC gate, orchestrates 8 design katas, and delivers 13 canonical files. Apollo-Agents implements downstream.
