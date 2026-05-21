# Lexis: Mandatory Structure of Agent Design Documents

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — Agent Design axis (documents produced by `warrior-metis` to promote and operate agents)

## Purpose

Building agents on the Guardia platform demands rigor of form so the result is reviewable, comparable across agents, and governable in production. Without a single structure for design files, each agent ends up described in a different place, with different sections, and the promotion from `pre-operational` to `operational-concrete` becomes subjective. This Lexis fixes the physical location of the artifacts, the governance snapshot of the DoOC, and the mandatory reciprocity with the Feature Design axis.

This Lexis complements — but does not replace — `lex-agent-construction-directives`: that one governs **what** an agent MUST have (6 Directives + 9 DoOC items); this one governs **where** and **in what form** that MUST be documented so that promotion and operation are auditable.

## Law

> **Every agent in the `operational-concrete` state on the Guardia platform MUST have (a) the 13 canonical files in `docs/{context}/agents/{agent}/` per `codex-agent-design-docs` (Hub & Spoke), (b) `docs/{context}/dooc/{agent}.md` filled in per `lex-agent-construction-directives` HARD-GATE, (c) `overview.md` with the `serves_features` field populated, (d) reciprocity in `docs/{context}/feature-agent-map.md` (forward and reverse mapping consistent between features and agents), (e) `warrior-metis` declared as author (PR ref, session-id, or `authored_by: warrior-metis` signature in the header of `overview.md`).**

```
<HARD-GATE>
warrior-metis, warrior-apollo-agents, and any other agent MUST NOT promote an agent to `operational-concrete` (merge into main, deploy to production) without ALL 5 preconditions:

  (a) 13 files present in `docs/{context}/agents/{agent}/`: `overview.md`, `orchestrator.md`, `specialists/{name}.md` (≥1), `tools.md`, `memory.md`, `reasoning-loop.md`, `feedback.md`, `context-pack.md`, `system-prompt.md`, `metrics.md`, `guardrails.md`, `authorization.md`, `escalation.md`
  (b) `docs/{context}/dooc/{agent}.md` exists and satisfies `lex-agent-construction-directives` HARD-GATE (9 DoOC items with evidence or N/A justified by ADR/PDR when `entry_mode` ≠ `with-pov`)
  (c) `agents/{agent}/overview.md` field `serves_features` populated with a valid list of features existing in `docs/{context}/features/`
  (d) `docs/{context}/feature-agent-map.md` reflects the relationship: forward (feature → agents) and reverse (agent → features) consistent; no agent listed in a feature without reciprocity in the agent's `serves_features`, and no feature listed in `serves_features` without reciprocity in `served_by_agents`
  (e) `warrior-metis` declared as author — PR ref in the header of `overview.md` (field `PR ref: {owner/repo#NNN}`) OR `authored_by: warrior-metis` in the header OR canonical session-id in the commit message

This rule applies to EVERY agent being promoted to `operational-concrete`, regardless of:
  - perceived size ("it's just a simple agent")
  - declared urgency ("the client needs it today")
  - who requested ("the CEO asked")
  - team confidence ("we already tested a lot")

Declared exceptions:
  - Agents in `pre-operational` (PoV produced by `warrior-claudionor`) are OUTSIDE this HARD-GATE — their minimum viable structure is defined in `codex-agent-construction-directives` (differential rigor per stage).
  - Agents in `legacy-pov` (prior to the merge of this Lexis) MAY be promoted with retroactive DoOC + ADR per the transition clause of `lex-agent-construction-directives` (90 days after merge). Reciprocity in `feature-agent-map.md` remains mandatory.
</HARD-GATE>
```

## Coverage

- **Applies to:** every agent that serves production features on the Guardia platform (Isac, reconciliation agents, fiscal/accounting classification, close, future agents). Includes agents that cover only one use case (1..1) and agents that cover multiple features (1..N).
- **Bound agents:** `warrior-metis` (author of the 13 files + `dooc/{agent}.md`), `warrior-apollo-agents` (consumer during implementation), `warrior-athena` (Gate 2 when the feature touches `docs/**/agents/**`), `warrior-prometheus` (coordinates Feature ↔ Agent reciprocity).
- **Exceptions:** only the two declared in the `<HARD-GATE>` (agents in `pre-operational` and `legacy-pov`).

## Violation Consequences

1. **Automatic block:** Gate 2 (`kata-quality-gate`) rejects promotion PRs that do not satisfy the 5 preconditions. PRs with `serves_features` inconsistent with `served_by_agents` (broken reciprocity) are blocked.
2. **Alert:** notifies `warrior-metis`, `warrior-prometheus` (Feature axis), and the agent's owner (`Owner` field in `overview.md`).
3. **Remediation:** complete the 13 files, fill in `dooc/{agent}.md`, update `feature-agent-map.md` to reflect reciprocity, and republish the promotion PR. In emergency deploys, rollback is mandatory until remediation.

## Examples

### Correct

Agent `rec-classifier` in capability `reconciliation` promoted in PR #543:

```
docs/
└── reconciliation/
    ├── agents/
    │   └── rec-classifier/
    │       ├── overview.md            # authored_by: warrior-metis; PR ref: guardiatechnology/ahrena#543
    │       │                          # serves_features: [transaction-classification, monthly-close-acceleration]
    │       ├── orchestrator.md
    │       ├── specialists/
    │       │   ├── statement-parser.md
    │       │   └── category-matcher.md
    │       ├── tools.md
    │       ├── memory.md
    │       ├── reasoning-loop.md
    │       ├── feedback.md
    │       ├── context-pack.md
    │       ├── system-prompt.md
    │       ├── metrics.md
    │       ├── guardrails.md
    │       ├── authorization.md
    │       └── escalation.md
    ├── dooc/
    │   └── rec-classifier.md          # 9 items with evidence; entry_mode: with-pov
    ├── features/
    │   ├── transaction-classification.md   # served_by_agents: [rec-classifier]
    │   └── monthly-close-acceleration.md   # served_by_agents: [rec-classifier]
    └── feature-agent-map.md           # forward: transaction-classification → rec-classifier
                                       # reverse: rec-classifier → transaction-classification, monthly-close-acceleration
```

Reciprocity verified: `serves_features` in `rec-classifier/overview.md` lists both features, and each feature lists the agent in `served_by_agents`. Promotion approved at Gate 2.

### Incorrect

```
docs/
└── reconciliation/
    ├── agents/
    │   └── rec-classifier/
    │       ├── overview.md            # serves_features: [transaction-classification, refund-detection]
    │       └── ... (13 files)
    ├── features/
    │   └── transaction-classification.md   # served_by_agents: [rec-classifier]
    │                                       # ❌ refund-detection does not exist
    └── feature-agent-map.md           # ❌ forward does not include refund-detection
```

Broken reciprocity: `serves_features` points to a nonexistent feature (`refund-detection`) and `feature-agent-map.md` does not reflect it. **Gate 2 rejects** — preconditions (c) and (d) violated.

Another incorrect case: agent promoted without `dooc/{agent}.md` ("we'll fill it in later"). Without a validated snapshot per `lex-agent-construction-directives`, precondition (b) is violated; promotion blocked.

## Automated Validation

- **Tool:** verification by the agent itself (`warrior-metis`) before promotion + lint at Gate 2 (`kata-quality-gate`) detecting: absence of the 13 files, missing `dooc/{agent}.md`, empty `serves_features` field in `operational-concrete`, desync between `serves_features` ↔ `served_by_agents` (reciprocity), absence of `authored_by` or PR ref in the header of `overview.md`. In the future: `kata-agent-design-validate` formalizing the 5 checks.
- **Timing:** Gate 2 of the Issue-Driven flow; PR review of the promotion; pre-deploy of any agent in `operational-concrete`; periodic audit of agents in production.
- **Metric:** 0 agents in `operational-concrete` without the 5 preconditions ✅; 0 features with `served_by_agents` pointing to a nonexistent agent; 0 agents with `serves_features` pointing to a nonexistent feature; 100% of promotions with `warrior-metis` tracked as author.

## References

- `codex-agent-design-docs` — manual with the 15 templates (13 agent files + dooc + feature-agent-map)
- `lex-agent-construction-directives` — master Law (6 Directives + DoOC HARD-GATE)
- `codex-agent-construction-directives` — conceptual foundation (Piaget, stage tags, differential rigor, evidence format)
- `lex-feature-design-docs`, `codex-feature-design-docs` — parallel Feature Design axis (reciprocity `serves_features` ↔ `served_by_agents`)
- `lex-hard-gate-pattern` — format of the `<HARD-GATE>` block used in this Lexis
- `warrior-metis` — author of the Agent axis artifacts
- `warrior-apollo-agents` — implementation consumer
- `warrior-athena` — orchestrates Gate 2 when a feature touches `docs/**/agents/**`
- `warrior-prometheus` — coordinates Feature ↔ Agent reciprocity
