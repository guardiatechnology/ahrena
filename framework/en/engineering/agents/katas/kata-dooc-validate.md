# Kata: Definition of Operational Concrete (DoOC) Validation

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents: gate-keeping the promotion from `pre-operational` to `operational-concrete` per `lex-agent-construction-directives`

## Objective

Verify the 9 canonical items of the Definition of Operational Concrete (DoOC) before allowing an agent's promotion from `pre-operational` to `operational-concrete`. The Kata is the executable tool of the HARD-GATE in `lex-agent-construction-directives`: it produces an auditable `go`/`no-go` report, persisted at `docs/{context}/dooc/{agent}.md`. It is not a new HARD-GATE — it is the verifier of the existing one.

## When to Use

- Before any transition of `stage: pre-operational` → `stage: operational-concrete` in an agent's system prompt
- Whenever `warrior-metis` receives `cry-agent-design --from-pov docs/{context}/agents-pov/{agent}/`
- At Gate 2 of the Issue-Driven flow when the feature touches `docs/{context}/agents/`
- In periodic audit of `legacy-pov` agents (90 days after `lex-agent-construction-directives` merge)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `context` | Yes | Bounded Context of the agent (kebab-case) |
| `agent` | Yes | Agent slug (kebab-case) |
| `--from-pov <path>` | No | Path to `docs/{context}/agents-pov/{agent}/` when a PoV exists. If absent, `direct-entry` mode requires ADR/PDR |
| `--entry-mode` | No | `with-pov` (default when `--from-pov` is present) \| `direct-entry` \| `legacy-pov` |
| `--tier` | Yes | `tier-1` \| `tier-2` \| `tier-3` \| `tier-4` (tier-1/2 triggers SLO obligation per `lex-slo-required`) |
| `--owner` | Yes | Stakeholder owner name + role of the agent + escalation channel |

## Workflow

```
Progress:
- [ ] 1. Resolve paths and entry mode
- [ ] 2. Verify item (a) — PoV origin declared
- [ ] 3. Verify item (b) — Leading metric proven
- [ ] 4. Verify item (c) — Lagging metric declared
- [ ] 5. Verify item (d) — Scope stabilized ≥ 2 weeks
- [ ] 6. Verify item (e) — Observability data ≥ 7 days
- [ ] 7. Verify item (f) — Stakeholder owner identified
- [ ] 8. Verify item (g) — Implementation capacity confirmed
- [ ] 9. Verify item (h) — Tier declared (tier-1/2 → SLO mandatory)
- [ ] 10. Verify item (i) — Stage explicit in PoV system prompt
- [ ] 11. Apply exception clause when applicable (legacy-pov, direct-entry, user-override)
- [ ] 12. Produce `dooc/{agent}.md` report + `go`/`no-go` decision
```

### Step 1: Resolve paths and entry mode

1. Resolve `pov_path = docs/{context}/agents-pov/{agent}/` if `--from-pov` provided; otherwise record `pov_path: N/A`
2. Define `entry_mode` per precedence rule: explicit argument → `with-pov` when `pov_path` exists → `direct-entry` when not
3. In `entry_mode: direct-entry`, require a path to an ADR/PDR in `docs/adr/` declaring: reason for bypassing `pre-operational`, target leading metric + post-deploy window, observability plan instrumented from day 0. Without ADR/PDR, fail immediately with a clear message
4. In `entry_mode: legacy-pov`, verify that the original PoV date predates the `lex-agent-construction-directives` merge AND falls within the 90-day window after the merge. Outside the window, fail immediately

### Step 2: Verify item (a) — PoV origin declared

| `entry_mode` | Criterion |
|--------------|-----------|
| `with-pov` | `pov_path/pov.md` exists and is valid (contains `stage: pre-operational` in the header) → ✅ |
| `direct-entry` | Mark `N/A — direct-entry (ADR: {path})` referencing the ADR/PDR from Step 1 → ✅ |
| `legacy-pov` | An identifiable historical PoV exists (commit ref or archive path) → ✅ |

Fail if no criterion is satisfied.

### Step 3: Verify item (b) — Leading metric proven

The leading metric is the operational evidence that the agent delivers value before aggregate impact. Criterion:

1. Read `pov_path/value-proof.md` (output of `kata-pov-value-track`) when `with-pov`
2. Look for: metric name + declared threshold + observation window ≥ 7 days + observed value ≥ threshold for ≥ 2 consecutive cycles
3. In `direct-entry`, mark `N/A — direct-entry` referencing the ADR; the ADR MUST declare the target leading metric and post-deploy window (fill in later)

Fail if:
- `with-pov` without valid `value-proof.md`
- threshold or window not declared
- observed value below threshold

### Step 4: Verify item (c) — Lagging metric declared

The lagging metric is the business metric impacted (e.g., monthly close time, reconciliation rework rate). Criterion:

1. Read `pov_path/value-proof.md` field `lagging_metric` or `docs/{context}/features/{feature}.md` when the agent serves existing features
2. The metric MUST be declared with unit and expected improvement direction (e.g., "reduce mean monthly close time from 5d to 3d")

Even in `direct-entry`, this item is mandatory. Fail without an explicit exception ADR via the `user-override` clause.

### Step 5: Verify item (d) — Scope stabilized ≥ 2 weeks

Criterion: the agent's scope (primary use case + declared out-of-scope) has not changed in the last 2 weeks. Verification:

1. Read `pov_path/scope.md` (output of `kata-pov-scope-define`) and check the file's commit history via `git log --since="2 weeks ago" -- {scope.md}`
2. Accept: 0 changes in 14 days OR only typographic changes (no alteration of `primary use case` or `out-of-scope` sections)
3. In `direct-entry`, mark `N/A — direct-entry`; scope is declared again during design by Mêtis

Fail if there is recent structural change.

### Step 6: Verify item (e) — Observability data ≥ 7 days

Criterion: minimum 7-day telemetry of the PoV in operation, aligned with `lex-observability-required` (1 trace + 1 metric + structured log with correlation_id).

1. Read `pov_path/observability/` (output of `kata-pov-observability-instrument`)
2. Verify that `traces-spec.md`, `prompts-log.md`, `tool-calls-log.md`, and `value-metrics.md` exist
3. Request confirmation that external dashboards / aggregators have ≥ 7 days of collection (human confirms or provides snapshot path)

In `direct-entry`, mark `N/A — direct-entry`; observability will be instrumented by `warrior-apollo-agents` from day 0 per the ADR.

### Step 7: Verify item (f) — Stakeholder owner identified

Criterion: owner name + role + escalation channel documented. Verification:

1. `--owner` argument provided OR `pov_path/value-proof.md::owner` populated
2. Escalation channel MUST be concrete (Slack `#channel`, email, on-call) — not "TBD" or "to be defined"

Mandatory in all `entry_mode`. Fail without declared exception.

### Step 8: Verify item (g) — Implementation capacity confirmed

Criterion:

1. `warrior-apollo-agents` is available (plan-013 merged — verify via existence of `framework/{lang}/engineering/backend/warriors/warrior-apollo-agents.md`) → ✅
2. OR alternative path declared in an ADR (`docs/adr/ADR-{N}-{slug}.md`)

Without either, fail.

### Step 9: Verify item (h) — Tier declared

Criterion:

1. `--tier` argument in {`tier-1`, `tier-2`, `tier-3`, `tier-4`}
2. When `tier-1` or `tier-2`, record obligation to produce `docs/{context}/agents/{agent}/metrics.md` with SLO section per `lex-slo-required` (declared as precondition for design completion, not for DoOC passing)
3. `tier-3` / `tier-4` does not trigger SLO obligation

Fail if `--tier` is missing or out of the enum.

### Step 10: Verify item (i) — Stage explicit in PoV system prompt

Criterion: `pov_path/system-prompt.md` contains the literal string `stage: pre-operational` (per `lex-system-prompt`).

1. In `with-pov`, read the file and search for the literal string
2. In `direct-entry`, mark `N/A — direct-entry`; Mêtis will declare `stage: operational-concrete` in the produced system prompt
3. In `legacy-pov`, require manual migration via `kata-pov-system-prompt --retrofit` before proceeding; without retrofit, fail

### Step 11: Apply exception clause when applicable

In `entry_mode: direct-entry`, items (a), (b), (d), and (e) MAY appear as `N/A — direct-entry` if the ADR/PDR from Step 1 declares (i) reason for bypass, (ii) target leading metric + post-deploy window, (iii) day-0 observability plan. Items (c) and (f)-(i) remain mandatory.

In `entry_mode: user-override` (CEO or designated Brand owner promotes with partial evidence), require an ADR/PDR declaring (i) which items are overridden, (ii) `Promoted by: {name}` in `dooc/{agent}.md`, (iii) retroactive compensation window (suggested 30 days). Overridden items become `N/A — user-override`.

### Step 12: Produce `dooc/{agent}.md` report + decision

Persist at `docs/{context}/dooc/{agent}.md` in the format:

```markdown
# DoOC — {agent}

> **Bounded Context:** {context}
> **Entry mode:** with-pov | direct-entry | legacy-pov
> **Tier:** tier-1 | tier-2 | tier-3 | tier-4
> **Promoted by:** {name, role} (in user-override)
> **PR ref:** {owner/repo#NNN}
> **Validation date:** {ISO 8601}
> **Validator:** warrior-metis via kata-dooc-validate

## Items (9)

| # | Item | Status | Evidence |
|---|------|:------:|----------|
| a | PoV origin declared | ✅ \| ❌ \| N/A | path or ADR ref |
| b | Leading metric proven | ✅ \| ❌ \| N/A | path or ADR ref |
| c | Lagging metric declared | ✅ \| ❌ | path or ADR ref |
| d | Scope stabilized ≥ 2 weeks | ✅ \| ❌ \| N/A | git log evidence |
| e | Observability data ≥ 7 days | ✅ \| ❌ \| N/A | path |
| f | Stakeholder owner identified | ✅ \| ❌ | name + channel |
| g | Implementation capacity confirmed | ✅ \| ❌ | warrior path or ADR |
| h | Tier declared (SLO if tier-1/2) | ✅ \| ❌ | tier value |
| i | Stage explicit in PoV system prompt | ✅ \| ❌ \| N/A | path |

## Decision

`go` when all items are ✅ or `N/A` justified by a valid ADR/PDR.
`no-go` in any other case.

## ADRs / PDRs referenced

- {path/name}

## Next steps when `go`

Proceed with `warrior-metis` orchestrating the remaining 8 design katas.

## Next steps when `no-go`

Report missing items to the user; suggest resuming the PoV (`/cry-pov`) or opening an exception ADR when applicable.
```

### Final Validation

Before declaring `go`, verify:

- [ ] All 9 items with status ✅ or `N/A` justified by an existing ADR/PDR
- [ ] `dooc/{agent}.md` persisted at the canonical path
- [ ] When `tier-1` or `tier-2`, record pending SLO obligation in `metrics.md` (to be produced by `kata-agent-feedback-design`)
- [ ] Owner + escalation channel concrete (not placeholders)
- [ ] PR ref populated when the Kata runs inside an Issue-Driven flow

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `dooc/{agent}.md` | Markdown | `docs/{context}/dooc/{agent}.md` |
| Decision | `go` \| `no-go` | return to the orchestrator (`warrior-metis`) |
| Missing items list | Text list | in case of `no-go`, returned to the caller |

## Example Execution

### Input

```
kata-dooc-validate \
  --context reconciliation \
  --agent rec-classifier \
  --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/ \
  --tier tier-2 \
  --owner "Marta Souza, Lead Reconciliation, #rec-oncall"
```

### Output (excerpt)

```markdown
# DoOC — rec-classifier

> **Bounded Context:** reconciliation
> **Entry mode:** with-pov
> **Tier:** tier-2
> **PR ref:** guardiatechnology/ahrena#543
> **Validation date:** 2026-05-12T15:30:00Z
> **Validator:** warrior-metis via kata-dooc-validate

## Items (9)

| # | Item | Status | Evidence |
|---|------|:------:|----------|
| a | PoV origin declared | ✅ | docs/reconciliation/agents-pov/rec-pov-classifier/pov.md |
| b | Leading metric proven | ✅ | reconciliation_auto_rate = 62% (threshold 60%) over 21 days |
| c | Lagging metric declared | ✅ | docs/reconciliation/features/transaction-classification.md::lagging_metric |
| d | Scope stabilized ≥ 2 weeks | ✅ | git log scope.md: 0 changes in 18 days |
| e | Observability data ≥ 7 days | ✅ | docs/reconciliation/agents-pov/rec-pov-classifier/observability/ (21 days) |
| f | Stakeholder owner identified | ✅ | Marta Souza, Lead Reconciliation, #rec-oncall |
| g | Implementation capacity confirmed | ✅ | framework/.../warriors/warrior-apollo-agents.md (plan-013 merged) |
| h | Tier declared | ✅ | tier-2 (SLO mandatory in metrics.md) |
| i | Stage explicit in PoV system prompt | ✅ | pov-path/system-prompt.md::stage: pre-operational |

## Decision

`go` — all 9 items ✅. Proceed with design of the 13 files.
```

## Constraints

- The Kata is the **verifier** of the HARD-GATE in `lex-agent-construction-directives`; it does not create a new HARD-GATE
- `no-go` is the Kata's final decision; deciding to resume PoV or open an exception ADR rests with the human user
- In `direct-entry` mode, the ADR/PDR MUST exist before Step 1; creating a retroactive ADR solely to pass the Kata is prohibited (violates the gate's spirit)
- Do not persist `dooc/{agent}.md` when the output is `no-go` — only report; the snapshot goes to the canonical destination only after `go`
- Do not modify `lex-agent-construction-directives` or `lex-agent-design-docs`
- PR ref is required when the Kata runs inside an Issue-Driven flow; in periodic audit or manual round, fill with `manual-audit`

---

**Model:** Canonical gate-keeper Kata for promotion to `operational-concrete`. Programmatically executes the 9 DoOC items, applies the 3 exception clauses declared in `lex-agent-construction-directives` (legacy-pov, direct-entry, user-override), and persists the snapshot at `docs/{context}/dooc/{agent}.md` on `go`. Always invoked first by `warrior-metis` before any other design kata.
