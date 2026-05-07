# Lexis: Product Discovery Flow — Insight to Idea

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Product Discovery — production of insights, status transitions, and promotion of an approved insight to an Idea in Ahrena

## Purpose

Ensure that every Idea in Ahrena has traceable origin in human-approved insights, and that the status evolution of an insight occurs exclusively by explicit human decision. Without this law, Ideas are born without evidence and insights slide from `proposed` to terminal states without review, breaking Discovery auditability.

## Law

> **Every Idea in Ahrena (`docs/discovery/{topic}/ideas/{NNN}-{slug}.md`) MUST have been created by `warrior-phanes` exclusively from one or more insights whose `status` is `approved`, with the 5 mandatory content fields (`problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate`) filled, and the source insight MUST be updated to `status: promoted` with `idea_ref` pointing to the created Idea. Every change of an insight `status` to any value other than `proposed` MUST be driven by an explicit, recorded human decision (session message, PR comment, or literal instruction); `warrior-pitia` MUST NOT change status on its own initiative, except for the initial creation in `proposed`.**

## Coverage

- **Applies to:** all insights and ideas produced in the Ahrena context, in any project that adopts the framework
- **Bound agents:** `warrior-pitia`, `warrior-phanes`, and any other agent that creates or modifies files under `docs/discovery/`
- **Exceptions:** None. Lexis admit no exceptions. (The HARD-GATEs below declare *precondition carve-outs* — not Law exceptions. The HG2 carve-out — initial creation in `proposed` — is integral to the rule, not derogation.)

<HARD-GATE>
warrior-phanes MUST NOT promote an insight to an Idea without ALL
preconditions below being met:

  (a) insight.status == approved (recorded human decision)
  (b) Idea references ≥1 insight in linked_insights[]
  (c) Idea fills the 5 mandatory schema fields:
      problem, hypothesis, target_user, success_metric, effort_estimate
  (d) Idea.topic matches insight.topic in ALL linked_insights[]
  (e) Phanes updates the source insight to status: promoted +
      fills idea_ref pointing to the created Idea

This rule applies to EVERY Idea creation in Ahrena, regardless of:
  - perceived size ("it is just an experiment")
  - verbal validation ("the stakeholder already approved on the call")
  - perceived obviousness ("the insight is trivial")
  - declared urgency ("we need the Idea for the sprint that starts tomorrow")

Single exception: none.
</HARD-GATE>

<HARD-GATE>
warrior-pitia MUST NOT change the status of an insight to any
value other than "proposed" without explicit human direction.

Mandatory preconditions for any status transition other than
`[*] → proposed`:

  (a) An explicit human instruction exists, identifying the insight by
      its `id` or canonical path
  (b) The target transition is valid in the state machine defined in
      codex-discovery-artifacts (transition table)
  (c) For under_review → refining: the human provided actionable
      written feedback
  (d) For refining → under_review: insight v2 has been effectively
      written, with `updated_at` updated

This rule applies to ALL insights produced by warrior-pitia,
regardless of:
  - obviousness of the feedback ("the adjustment is trivial")
  - history of similar cases ("Pitia has seen this before")
  - declared urgency
  - team confidence

Single exception: the initial creation of the insight (`[*] → proposed`)
belongs to warrior-pitia and does not require human direction — only
the existence of at least one reference in `source_refs[]`.
</HARD-GATE>

## Violation Consequences

1. **Automatic block:** PR rejected when the reviewer detects (a) an Idea without a valid `linked_insights[]`, (b) an Idea with any of the 5 mandatory fields empty or null, (c) an insight whose status changed without corresponding human evidence, or (d) divergent `topic` between the Idea and its source insights.
2. **Alert:** notifies the stakeholder responsible for the `topic` and the human author who was driving the evaluation.
3. **Remediation:** the PR author chooses between (a) fixing the Idea/insight to satisfy all preconditions of the applicable HARD-GATE, or (b) reverting the invalid transition and reopening the cycle from the prior valid state.

## Examples

### Correct

```yaml
# docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
---
id: "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
topic: "scheduled-payments-research"
status: approved          # <- human approved explicitly in PR review
source_refs:
  - "docs/transcripts/interview-2026-05-04-accountant-X.md"
created_at: "2026-05-04T10:00:00Z"
updated_at: "2026-05-08T14:30:00Z"
---

# warrior-phanes reads the approved insight and produces the Idea:
# docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md
---
id: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
topic: "scheduled-payments-research"          # <- matches the insight topic
problem: "Accountants lose 4h/week reconciling ERP and bank statements."
hypothesis: "An automatic suggestion with ≥90% confidence will be accepted in ≥70% of cases, reducing manual time by ≥60%."
target_user: "Operational accountant in firms with 50-500 clients"
success_metric: "Average reconciliation time: baseline 4h/client/month → target 1.5h in 90 days"
effort_estimate: "M (2-4 sprints)"
linked_insights:
  - "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
created_at: "2026-05-10T15:00:00Z"
updated_at: "2026-05-10T15:00:00Z"
---

# Phanes updates the source insight:
# status: promoted
# idea_ref: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
```

### Incorrect

```yaml
# Idea without linked_insights[] — VIOLATES HARD-GATE 1, precondition (b)
---
id: "scheduled-payments-research/ideas/002-mobile-receipt-capture"
topic: "scheduled-payments-research"
problem: "We think mobile capture would be useful"
hypothesis: ""              # <- VIOLATES HARD-GATE 1, precondition (c) — empty field
target_user: "Users"        # <- inadequate, but present
success_metric: ""          # <- VIOLATES HARD-GATE 1, precondition (c)
effort_estimate: "M"
linked_insights: []         # <- VIOLATES HARD-GATE 1, precondition (b) — empty array
---
```

```yaml
# warrior-pitia changes status without human direction — VIOLATES HARD-GATE 2
# Before: status: proposed
# After (without human instruction): status: approved
# ❌ Even if Pitia "finds it obvious", the transition is invalid without a human record.
```

```yaml
# Idea with topic divergent from the insight — VIOLATES HARD-GATE 1, precondition (d)
---
id: "billing/ideas/001-auto-invoice"
topic: "billing"
linked_insights:
  - "scheduled-payments-research/insights/003-erp-divergence"  # divergent topic
---
```

## Automated Validation

- **Tool:** human PR review while a dedicated linter does not exist; in the future `kata-design-validation` parameterized for type `discovery-artifacts` MUST validate (i) presence and type of mandatory fields, (ii) `topic` coherence between the Idea and `linked_insights[]`, (iii) `status` coherence with conditional fields (`merged_into`, `idea_ref`, `rejected_reason`, `awaiting_evidence_reason`), (iv) transition history in the file's git log (each status change accompanied by a commit or human comment).
- **When:** PR review on every PR that touches `docs/discovery/`; auto-check by `warrior-phanes` itself before writing the Idea.
- **Metric:** 0 Ideas with empty `linked_insights[]` on `main`; 0 Ideas with any of the 5 mandatory fields empty; 0 insight status transitions executed by `warrior-pitia` without evidence of corresponding human instruction; 100% of Idea `topic` values matching their source insights.

## References

- `codex-discovery-artifacts` — full schema of insights and ideas, state machine, addressing conventions
- `lex-hard-gate-pattern` — canonical pattern of the HARD-GATE block
- `kata-discovery-synthesis` — procedure for producing insights
- `kata-ideation-from-insight` — procedure for promoting to an Idea
- `warrior-pitia`, `warrior-phanes` — bound agents
