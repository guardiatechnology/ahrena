Promote an Approved Insight to an Idea. Product Discovery — shortcut to invoke warrior-phanes with one or more approved insight_path

# Cry: Promote an Approved Insight to an Idea

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Product Discovery — shortcut to invoke `warrior-phanes` with one or more approved `insight_path`

## Usage

```
/cry-ideation
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `insight_path` | Yes | Canonical path of the insight to promote (string or array when multiple insights form a single Idea) | `docs/discovery/scheduled-payments-research/insights/001-...` |
| `additional_context` | No | Extra context provided by the human (telemetry data, refined hypothesis, available pilot) that helps Phanes assemble `success_metric` or `effort_estimate` | "Pilot client available: firm Y" |

## What the Command Does

1. Invokes `warrior-phanes` with the provided parameters
2. Phanes reads `.ahrena/.directives` and internalizes `lex-discovery-flow` and `codex-discovery-artifacts`
3. Phanes validates HARD-GATE 1 at **three moments** (per `kata-ideation-from-insight`): input preflight (a, d) before any read, output preflight (b, c) on the synthesized Idea before writing, and post-write (e) with transactional rollback if any partial source-insight update fails
4. If preflight passes, Phanes executes `kata-ideation-from-insight`, generating the Idea file with the 5 mandatory content fields filled
5. Phanes updates the source insight(s) to `status: promoted` with `idea_ref` pointing to the Idea (rollback automatic on failure)
6. Phanes reports the created Idea and the promoted insights, flagging gaps that need additional validation

## Prompt Template

```
Take the role of warrior-phanes (Product Ideation).

Received parameters:
- insight_path:
{{insight_path}}
- additional_context:
{{additional_context}}

Task:
Execute kata-ideation-from-insight with the parameters above.
Before any write, read .ahrena/.directives, lex-discovery-flow, and codex-discovery-artifacts.
Validate HARD-GATE 1 at three moments, per the kata:
  - Input preflight (a, d) before any read
  - Output preflight (b, c) on the synthesized Idea, BEFORE writing
  - Post-write (e) with transactional rollback if any partial source-insight update fails
If any preflight fails, interrupt and inform the human which action unblocks.
If it passes, generate the Idea in docs/discovery/{topic}/ideas/{NNN}-{slug}.md
with the 5 mandatory content fields (problem, hypothesis, target_user, success_metric, effort_estimate)
and linked_insights[] referencing the source insights.
Update the source insight(s) to status: promoted + idea_ref + updated_at.
Do not change an insight status to approved (HARD-GATE 2; human prerogative).

Output format:
- Confirmation of the created Idea with canonical path
- List of promoted insights
- Summary of each of the 5 mandatory content fields
- Gaps that need additional validation before the design cycle
```

## Invocation Example

**Input:**

```
/cry-ideation
insight_path: docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
additional_context: |
  Pilot client available: firm Y with 80 active accountants
```

**Expected output:**

```
warrior-phanes validated HARD-GATE 1 ✅ and executed kata-ideation-from-insight.

Idea created: docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md

Promoted insights:
- scheduled-payments-research/insights/001-manual-reconciliation-bottleneck → status: promoted

Idea summary:
- Problem: 4h/week of manual reconciliation, with no perception of value
- Hypothesis: automatic suggestion with ≥90% confidence will be accepted in ≥70% of cases
- Target user: operational accountant in firms with 50-500 clients integrated with ERP X
- Success metric: reconciliation time per month per client — baseline 4h → target 1.5h in 90 days
- Effort estimate: M (2-4 sprints; depends on the matching model and ERP X webhooks)

Gaps that need validation:
- Baseline 4h comes from 1 interview — I recommend confirming with 3 additional interviews
- ERP X webhooks were not validated against the product documentation

Idea ready for warrior-prometheus consumption.
```

**Failure scenario:**

```
/cry-ideation
insight_path: docs/discovery/scheduled-payments-research/insights/005-payment-method-confusion.md
```

```
warrior-phanes interrupted. HARD-GATE 1 failed:
- (a) status: under_review ❌ (expected: approved)

To unblock:
1. Evaluate the insight in PR review
2. If approved, update status: approved in the front-matter (your decision per HARD-GATE 2)
3. Reinvoke /cry-ideation with the same insight_path
```

## Restrictions

- Does not create an Idea if HARD-GATE 1 fails — interrupts and informs the human
- Does not change an insight status to `approved` — human prerogative per HARD-GATE 2 of `lex-discovery-flow`
- Does not modify source insight fields beyond `status`, `idea_ref`, and `updated_at`
- Does not mix distinct `topics` in a single Idea
- Output always in the language defined in `language.default` of `.directives` (default: pt-BR)

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Shortcut to invoke Phanes | Procedure that Phanes executes |
| **Who invokes** | Human user | Warrior (Phanes) |
| **What it does** | Triggers the warrior with parameters | Validates HARD-GATE 1 and promotes insight to Idea |
| **Example** | `/cry-ideation` | `kata-ideation-from-insight` |
