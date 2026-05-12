---
name: kata-pov-feedback-attach
description: "Attach Feedback Loop to PoV. Engineering — Agents (pre-operational stage): define lightweight HITL OR 1 objective metric as the PoV's feedback loop"
---

# Kata: Attach Feedback Loop to PoV

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): define lightweight HITL OR 1 objective metric as the PoV's feedback loop

## Workflow

```
Progress:
- [ ] 1. Decide between lightweight HITL or objective metric (or both)
- [ ] 2. Specify the chosen mechanism
- [ ] 3. Define capture cadence
- [ ] 4. Declare pivot trigger (when feedback changes the PoV)
- [ ] 5. Persist feedback.md
```

### Step 1: Decide between lightweight HITL or objective metric

Selection criterion:

| Scenario | Mechanism |
|---|---|
| Output is a consequential decision (writes to external system, sends a communication) | Lightweight HITL required |
| Output is an advisory suggestion (human validates before applying) | Objective metric suffices |
| Tier-1/2 declared | Lightweight HITL + objective metric (both) |
| Tier-3/4 (default PoV) | At least 1 of the two |

If the primary use case involves a **consequential decision**, the kata forces lightweight HITL even at tier-3/4.

### Step 2: Specify the chosen mechanism

**Lightweight HITL:**

- Where the human approves: PoV UI ("approve/reject" button), PR comment, or a dedicated channel (Slack thread)
- What gets captured: agent input, agent output, human decision (approve/reject/edit), reason (optional free text)
- Acceptable latency: ≤ 24h by default

**Objective metric:**

- Binary environment signal indicating hit/miss (e.g., "was the suggested entry effected in the ERP within 7 days?")
- How to capture: webhook, DB polling, human-action log
- Attribution window: declared (default 7 days)

### Step 3: Define capture cadence

- Lightweight HITL: daily aggregation + weekly review
- Objective metric: continuous aggregation + weekly read in `value-proof.md`
- The aggregation result is input for `kata-pov-value-track`

### Step 4: Declare pivot trigger

Declared condition that, when met, forces a PoV review (re-execution of `kata-pov-scope-define`):

- Default: "Human approval < 50% for 2 consecutive weeks" (lightweight HITL)
- Default: "Objective metric < 30% of the threshold for 2 consecutive weeks"

The pivot trigger is **different** from the discontinuation criterion (`pov.md::Discontinuation criterion`): pivot asks for review; discontinuation closes.

### Step 5: Persist feedback.md

Write `docs/{context}/agents-pov/{agent}/feedback.md` with sections: Chosen mechanism, Technical specification, Cadence, Pivot trigger, Cross-reference to `observability/value-metrics.md`.

### Final Validation

- [ ] At least 1 mechanism declared (lightweight HITL OR objective metric)
- [ ] If tier-1/2: both declared
- [ ] Pivot trigger has a quantified condition (window + threshold)
- [ ] Cadence declared explicitly
- [ ] Cross-link to `value-metrics.md` active

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `feedback.md` | Markdown | `docs/{context}/agents-pov/{agent}/feedback.md` |

## Execution Example

### Input (pov.md, excerpt)

```
Use case: suggest bank-statement-to-ledger-entry pairing. Advisory suggestion (human confirms before saving).
Tier: 3 (default PoV).
```

### Output (feedback.md, excerpt)

```markdown
## Mechanism

Objective metric (PoV is advisory, tier-3).

## Technical specification

- Signal: "did the operator approve or adjust the suggestion within 7 days?"
- Capture: log of the "Apply suggestion" button on the PoV front-end
- Window: 7 days per suggestion

## Cadence

- Continuous aggregation in observability/value-metrics.md::reconciliation_auto_rate
- Weekly review in value-proof.md

## Pivot trigger

reconciliation_auto_rate < 30% for 2 consecutive weeks → re-scope via kata-pov-scope-define.
```

## Restrictions

- **Never** a PoV without declared feedback. Without feedback, value-proof becomes a fake document.
- **Never** latent HITL (> 7 days for human capture) — it invalidates the short cycle that justifies the PoV.
- **Never** a qualitative pivot trigger ("if it goes bad"). Always window + threshold.

---

**Model:** This Kata applies Directive 04 (`lex-agent-construction-directives`) at pre-operational rigor. The critic agent is optional — it stays for Mêtis when the agent is promoted.
