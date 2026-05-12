# Kata: Track PoV Value (value-proof.md)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): structured data capture during PoV operation to support the go/no-go decision to promote to `operational-concrete`

## Objective

Produce and maintain `docs/{context}/agents-pov/{agent}/value-proof.md` — a **living** document throughout the PoV's operation. Define the canonical schema (mandatory fields + telemetry SHA), the go/no-go promotion criterion (direct input to DoOC), and the review cadence (`tier-1/2 weekly`; `tier-3/4 fortnightly`). Without a consistent `value-proof.md`, Mêtis cannot run `kata-dooc-validate` items 2 (leading proven) and 5 (observability ≥ 7 days).

## When to Use

- Immediately after `kata-pov-feedback-attach` (initial template)
- In every review cycle (weekly or fortnightly, per tier) — update
- When the pivot trigger in `feedback.md` is reached
- Before Mêtis invokes `cry-agent-design --from-pov`

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `docs/{context}/agents-pov/{agent}/pov.md` | Yes | Leading value metric + discontinuation criterion |
| `docs/{context}/agents-pov/{agent}/observability/value-metrics.md` | Yes | Definitions and thresholds |
| `docs/{context}/agents-pov/{agent}/feedback.md` | Yes | Capture mechanism + pivot trigger |
| `--tier <1\|2\|3\|4>` | No | Default 3. Determines cadence |
| `--cycle <N>` | No | Review round number (1, 2, 3, ...) |

## Workflow

```
Progress:
- [ ] 1. Initialize value-proof.md with canonical schema (first run)
- [ ] 2. Each cycle, record the primary metric reading with telemetry SHA
- [ ] 3. Record qualitative observations of the cycle
- [ ] 4. Evaluate discontinuation criterion and pivot trigger
- [ ] 5. Update PoV status (continue / pivot / discontinue / promote)
- [ ] 6. Persist the updated document
```

### Step 1: Initialize value-proof.md (first run)

Canonical schema (mandatory fields):

```markdown
# value-proof.md — PoV {context}

> Cadence: {weekly | fortnightly} (tier-{N})
> Stage: pre-operational

## Identification

- context: {context}
- started on: {ISO date}
- responsible: {person / team}
- primary metric: {name} (reference: observability/value-metrics.md)
- leading threshold: {value + window}
- discontinuation criterion: {literal from pov.md}
- pivot trigger: {literal from feedback.md}

## Cycle log

(living section — one entry per cycle)

### Cycle 1 — {ISO date}

- observed period: {start} → {end}
- primary metric value: {number}
- source telemetry SHA: {hash of the observability snapshot}
- qualitative observations: {free text, 3-5 sentences}
- cycle decision: continue | pivot | discontinue | promote
- justification: {free text}

## Current decision

- status: active | pivoting | closed | ready_for_dooc
- updated on: {ISO date}
- next cycle scheduled for: {ISO date}
```

### Step 2: Record the metric reading with SHA

In every kata execution within a cycle:

1. Read the telemetry snapshot (export of aggregated `observability/value-metrics.md`).
2. Compute SHA256 of the snapshot (traceability — Risk 5 of plan-031 mitigates "fake value-proof").
3. Append to the cycle record: metric value + SHA + observed period.

### Step 3: Record qualitative observations

3-5 short sentences per cycle:

- What worked (concrete case, no inventing)
- What failed (observed anti-pattern, link to context-pack if applicable)
- Surprises (case outside the expected)

No PII. If a case depends on sensitive detail, anonymize or refer by opaque ID.

### Step 4: Evaluate discontinuation criterion and pivot trigger

1. **Discontinuation criterion** (from `pov.md`): if reached, status → `closed`.
2. **Pivot trigger** (from `feedback.md`): if reached, status → `pivoting` and recommend re-running `kata-pov-scope-define`.
3. **Sustained success** (metric ≥ threshold for ≥ 7 days and scope stable for 2 weeks): status can advance to `ready_for_dooc` — Mêtis can run `cry-agent-design --from-pov`.

#### Mandatory precondition — PII boundary before `ready_for_dooc`

Before transitioning status to `ready_for_dooc` (and therefore before enabling the `cry-agent-design --from-pov` handoff to Mêtis), the kata **MUST** run a PII boundary check against the `docs/{context}/agents-pov/{agent}/` directory:

1. For each `.md` file (and files under `observability/`) of the PoV, grep against the patterns declared in `lex-data-retention` (CPF, CNPJ, email, phone, bank account, token, secret, etc.).
2. If there is **any** match, the kata **REFUSES** the transition and returns to the user the list of hit files and lines, recommending re-running `kata-pov-context-curate` for re-anonymization (`pov.md::Anonymization notes`).
3. Only when the grep returns zero matches may the status flip to `ready_for_dooc`.

Rationale: the `pov.md` document (and the context-pack) is delivered as direct input to `warrior-mêtis` via `--from-pov` for the `operational-concrete` cycle. PII leaked in the PoV package would propagate to the production design without a new review. The gate executes in this kata because it is the only point at which the handoff transition is decided.

### Step 5: Update PoV status

Update the "Current decision" block with:

- status (closed vocabulary: `active`, `pivoting`, `closed`, `ready_for_dooc`)
- timestamp
- next cycle scheduled (cadence: weekly for tier-1/2, fortnightly for tier-3/4)

### Step 6: Persist the document

1. Write `docs/{context}/agents-pov/{agent}/value-proof.md` with the current cycle added.
2. Record the commit in the PoV history (responsible + cycle number).
3. If status = `ready_for_dooc`, emit a log saying "Ready for Mêtis to consume via `cry-agent-design --from-pov docs/{context}/agents-pov/{agent}/`".

### Final Validation

- [ ] All mandatory schema fields present
- [ ] At least 1 cycle recorded (in the initial run this is cycle zero — bootstrap)
- [ ] Telemetry SHA present in every cycle (traceability)
- [ ] No PII
- [ ] Current status coherent with the metric reading

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `value-proof.md` | Markdown (living) | `docs/{context}/agents-pov/{agent}/value-proof.md` |

## Cadence (quick reference)

| PoV tier | Review cadence | Critical when |
|---|---|---|
| 1, 2 | Weekly | PoV impacts revenue or compliance |
| 3, 4 (default) | Fortnightly | Advisory / internal PoV |

## Restrictions

- **Never** a metric value without telemetry SHA — value-proof without evidence is a facade.
- **Never** a cycle without an explicit decision (`continue | pivot | discontinue | promote`).
- **Never** PII in observations.
- **Never** a status outside the closed vocabulary.
- **Always** the document is living: each cycle **adds** an entry; history is preserved.

---

**Model:** This Kata is the direct input of DoOC (`lex-agent-construction-directives`). The schema is the contract consumed by `kata-dooc-validate` (plan-032).
