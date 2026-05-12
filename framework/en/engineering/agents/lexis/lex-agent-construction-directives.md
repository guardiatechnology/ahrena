# Lexis: Agent Construction Directives

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Construction of AI agents on the Guardia platform — system prompt, memory, tools, feedback, scope, context, and cognitive-stage promotion cycle

## Purpose

Guardia builds AI agents as products (Isac, reconciliation, fiscal classification, closing). Without a shared foundation, PoVs become product without maturing, production is tolerated as PoV, and Claudionor and Mêtis talk about "agent" with different expectations. This Law codifies the objective promotion criterion (DoOC) and the shared vocabulary (cognitive stages) that make the question "is this PoV ready for scale?" verifiable rather than subjective.

## Law

> **Every AI agent built on the Guardia platform MUST explicitly declare its cognitive stage (`stage: pre-operational | operational-concrete | legacy-pov`) in the system prompt. Agents in `operational-concrete` MUST satisfy all 6 Construction Directives (Clear Identity, Layered Memory, Concrete Tools, Explicit Feedback Loop, Restricted Scope, Rich Context) at production rigor, per `codex-agent-construction-directives` and the canonical manual "Diretrizes para Construção de Agentes" maintained in Notion. Agents in `pre-operational` MAY operate with a minimum viable version of each Directive, provided the stage is declared and the gaps are recorded in the PoV. Promoting an agent from `pre-operational` to `operational-concrete` without a Definition of Operational Concrete (DoOC) validated on the 9 canonical items is FORBIDDEN.**

## Coverage

- **Applies to:** every AI agent built on the Guardia platform — Isac, reconciliation agents, fiscal classification agents, closing agents, internal automation agents, customer-facing agents, support agents. Applies to the agent prompt, the tooling layer, the memory layer, and the promotion cycle between stages.
- **Bound agents:** `warrior-claudionor` (PoV Factory — plan-031), `warrior-metis` (APM Operational Concrete — plan-032), `warrior-apollo-agents` (implementation — plan-013), `warrior-athena` (Gate 2 of the Issue-Driven Flow when the feature touches `docs/{context}/agents/`).
- **Exceptions:** Lexis admit no exceptions. The 3 clauses declared in the HARD-GATE are `legacy-pov`, `direct-entry`, and `user-override`; each requires compensation documented in an ADR or PDR and a corresponding marker in `dooc/{agent}.md` per `codex-agent-design-docs`. Without a valid ADR/PDR, the exceptions are non-compliant.

## Cognitive stages

The Piaget analogy detailed in `codex-agent-construction-directives` is the conceptual framework; the differential rigor expressed here is its operational translation.

| Tag | When to use | Rigor required of the 6 Directives |
|-----|-------------|------------------------------------|
| `pre-operational` | Active PoV, proving value before scale | Minimum viable version of each Directive; gaps declared in PoV doc/PDR |
| `operational-concrete` | Production; scope proven; value measured | All 6 Directives at production rigor |
| `legacy-pov` | Agent created before this Lex's merge | Treated as `pre-operational`; migration required within 90 days |

## Definition of Operational Concrete (DoOC)

The DoOC is the canonical promotion checklist. Per-criterion detail (evidence format, expected links) lives in `codex-agent-construction-directives`. The 9 items are:

1. **Declared PoV origin** — path under `docs/{context}/agents-pov/` referencing the original PoV
2. **Proven leading value metric** — number, threshold, and observation window (minimum 7 days)
3. **Declared lagging value metric** — business metric the agent is expected to move
4. **Stabilized scope** — no scope change in the last 2 weeks
5. **Available observability data** — minimum 7 days of telemetry from the PoV in operation
6. **Identified stakeholder owner** — name and role; escalation channel documented
7. **Confirmed implementation capacity** — `warrior-apollo-agents` available OR alternative path declared
8. **Declared criticality tier** — tier-1/2 triggers mandatory SLO per `lex-slo-required`
9. **Explicit stage in the system prompt** — `stage: pre-operational` declared in the PoV prompt before promotion

## HARD-GATE

Per [`lex-hard-gate-pattern`](framework/en/_foundation/quality/lexis/lex-hard-gate-pattern.md), the textual block of this Lex is canonically expressed as:

```
<HARD-GATE>
warrior-claudionor, warrior-metis, warrior-apollo-agents and any
other agent MUST NOT promote an agent from `pre-operational` to
`operational-concrete` without ALL 9 items of the Definition of
Operational Concrete (DoOC) ✅:

  (a) Declared PoV origin (path under docs/{context}/agents-pov/)
  (b) Proven leading value metric (number, threshold, window
      ≥ 7 days)
  (c) Declared lagging value metric
  (d) Stabilized scope (no change in the last 2 weeks)
  (e) Available PoV observability data (≥ 7 days)
  (f) Identified stakeholder owner
  (g) Confirmed implementation capacity (warrior-apollo-agents
      OR alternative path declared)
  (h) Declared criticality tier (tier-1/2 triggers mandatory SLO)
  (i) Explicit stage in the PoV system prompt
      (`stage: pre-operational`)

This rule applies to EVERY agent built on the Guardia platform,
regardless of:
  - perceived size ("it's just a simple agent")
  - urgency ("the customer needs it today")
  - who requested ("the CEO asked")
  - team confidence ("we already tested a lot")

Declared exceptions (3):

(1) `legacy-pov` — agents created before this Lex's merge are
    treated as `stage: legacy-pov`. Promotion to `operational-concrete`
    requires a retroactive DoOC + ADR recording the historical gap.
    The tag is NOT permanent: agents in `legacy-pov` MUST migrate to
    `pre-operational` or `operational-concrete` within 90 days after
    this Lex's merge; beyond that deadline they are considered
    non-compliant.

(2) `direct-entry` — Mêtis invoked to design an agent directly into
    `operational-concrete` without a prior PoV (Claudionor was not
    invoked). Permitted only with an ADR or PDR declaring:
      (i) the reason for bypassing the `pre-operational` stage;
      (ii) target leading metric + post-deploy validation window;
      (iii) observability plan instrumented from day 0.
    DoOC items (a), (b), (d) and (e) may be filled as `N/A — direct-entry` in
    `dooc/{agent}.md`, always referencing the ADR/PDR; items (c) and (f)-(i)
    remain mandatory.

(3) `user-override` — the user (CEO or designated Brand owner) promotes
    an agent with partial DoOC evidence. Permitted only with an ADR
    or PDR declaring:
      (i) which DoOC items are being overridden and why;
      (ii) explicit user accountability (`Promoted by` filled in
           `dooc/{agent}.md`);
      (iii) retroactive compensation in a declared window
            (suggested: 30 days).
    Overridden items appear as `N/A — user-override` in `dooc/{agent}.md`.

In all exceptions, the Lex stays inviolate — exceptions are canonical
fillings of `dooc/{agent}.md` with auditable justification in an ADR
or PDR, NOT a bypass of the gate. Without a valid ADR/PDR, the
declared exceptions are non-compliant.
</HARD-GATE>
```

## Violation Consequences

1. **Automatic block:** `kata-dooc-validate` (delivered in plan-032) fails the checklist whenever any DoOC item is missing; `warrior-athena` at Gate 2 of the Issue-Driven Flow blocks the PR when the feature touches `docs/{context}/agents/` without a declared `stage:` or without a DoOC attached to the promotion. A commit that changes `stage:` from `pre-operational` to `operational-concrete` without a promotion ADR referencing the DoOC is rejected.
2. **Alert:** notifies the agent owner (declared in DoOC item (f)) and the `#agents-governance` channel; agents in `legacy-pov` beyond the deadline declared in the HARD-GATE enter an automatic weekly report until they are regularized or decommissioned.
3. **Remediation:** (a) revert the promotion (back to `pre-operational`) and open an issue to complete the missing DoOC items; OR (b) open an ADR recording the alternative path per DoOC item (g); OR (c) decommission the agent when the PoV does not justify production.

## Examples

### Correct

PoV system prompt declaring its stage:

```
# Agent: rec-pov-classifier
# stage: pre-operational
# DoOC gaps: leading metric still being collected; observability < 7 days
# Identity: transaction classifier for reconciliation
# Memory: short-term (session window)
# Tools: search over classification history + simple execution
# Feedback: light HITL (analyst validates every classification)
# Scope: 1 use case — Itaú PJ bank statements
# Context: 12 few-shot + 4 curated negative examples
```

System prompt for a production agent:

```
# Agent: rec-classifier
# stage: operational-concrete
# DoOC: ✅ (validated on 2026-04-12, ADR-018)
# tier: tier-2
# SLO: docs/reconciliation/metrics/slo-rec-classifier.yaml
# Identity: per docs/reconciliation/agents/rec-classifier/identity.md (full manual)
# Memory: short + medium (session + customer history) + long (classification rules)
# Tools: tripartite catalog — deterministic + ML + MCP
# Feedback: HITL + critic LLM + 3 objective metrics in CloudWatch
# Scope: transaction classification for bank reconciliation
# Context: curated few-shot + docs + observed history of the last 90 days
```

### Incorrect

Agent without a declared stage:

```
# Agent: rec-classifier
# Identity: classifier
# (no stage:, no DoOC, no tier, no manual reference)
```

Outcome: `warrior-athena` blocks the PR at Gate 2; `warrior-metis` refuses to promote the PoV; the agent reaches production as a black box.

Promotion without DoOC:

```
# Before: stage: pre-operational
# After:  stage: operational-concrete
# (without the 9 DoOC items validated, without a promotion ADR)
```

Outcome: `warrior-metis` rejects the promotion; a commit that changes `stage:` without an attached DoOC checklist is blocked at Gate 2.

## Automated Validation

- **Tool:** `kata-dooc-validate` (delivered in plan-032 alongside `warrior-metis`) executes the 9-item DoOC checklist programmatically; a lint in the pipeline detects system prompts under `docs/{context}/agents/` without a declared `stage:`; `warrior-athena` applies this Gate when the feature touches agent artifacts.
- **When:** at agent promotion (`pre-operational` → `operational-concrete` transition); at Gate 2 of the Issue-Driven Flow when the feature touches `docs/{context}/agents/`; in periodic audits of `legacy-pov` agents (90 days after merge).
- **Metric:** 0 agents in `operational-concrete` without DoOC ✅; 100% of platform system prompts with `stage:` declared; 0 agents in `legacy-pov` beyond 90 days after this Lex's merge.
