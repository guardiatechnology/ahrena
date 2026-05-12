# Kata: Context Pack Design (with `--from-pov` Bridge)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents: design of the agent's context pack (`context-pack.md`) in `operational-concrete`, including the canonical bridge that consumes `warrior-claudionor` output (PoV → Operational Concrete)

## Objective

Produce the agent's context pack — positive few-shot (minimum 5 in production, > than in the PoV), curated negative examples (minimum 10), 30-90 day observed history when applicable. Strictly covers **Directive 06 — Rich Context** of `lex-agent-construction-directives`.

This Kata implements the **canonical `--from-pov` bridge**: when the agent arrives with `entry_mode: with-pov`, it reads `docs/{context}/agents-pov/{pov-agent}/` (output of `warrior-claudionor`) and enriches the context pack with:

- Positive few-shot derived from real inputs experimented in the PoV
- Negative examples curated from failures observed in the PoV (real anti-patterns, not invented)
- PoV telemetry snippets (typical traces, observed edge cases)

## When to Use

- After `kata-agent-feedback-design` (the context pack references metrics and thresholds)
- When the agent receives new training material (periodic re-curation)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `context` | Yes | Bounded Context |
| `agent` | Yes | Agent slug |
| `overview_path` | Yes | `docs/{context}/agents/{agent}/overview.md` |
| `--from-pov <path>` | No | `docs/{context}/agents-pov/{pov-agent}/` (output of `warrior-claudionor`) |
| `--retrain-cadence` | No | `weekly` \| `monthly` \| `quarterly` (default: `quarterly`) |

## `--from-pov` input contract

When the `--from-pov` flag is provided, the Kata expects the following files at the given path (all produced by `warrior-claudionor` PoV katas):

| File | Produced by | Content consumed |
|------|-------------|------------------|
| `pov.md` | `kata-pov-scope-define` | Primary use case (to confirm alignment) |
| `scope.md` | `kata-pov-scope-define` | Out-of-scope (to validate negatives) |
| `system-prompt.md` | `kata-pov-system-prompt` | Pre-operational identity (reference) |
| `tools.md` | `kata-pov-tools-select` | Tools used in the PoV |
| `context-pack.md` | `kata-pov-context-curate` | **Positive few-shot + anti-patterns — primary enrichment source** |
| `feedback.md` | `kata-pov-feedback-attach` | Value metric + pivot trigger |
| `value-proof.md` | `kata-pov-value-track` | Proven leading metric, `ready_for_dooc` decision (canonical machine-readable, language-invariant token) |
| `observability/value-metrics.md` | `kata-pov-observability-instrument` | Observed operational metrics |
| `observability/prompts-log.md` | `kata-pov-observability-instrument` | Edge cases identified in production (references, no PII) |
| `observability/tool-calls-log.md` | `kata-pov-observability-instrument` | Tool usage patterns |
| `observability/traces-spec.md` | `kata-pov-observability-instrument` | Typical trace snippets |
| `implementation/skill.md` or `subagent.md` | `kata-skill-implement` or `kata-agent-author` | Reference of the PoV implementation |

**PII redaction assumption:** the Kata trusts that `kata-pov-value-track::Step 4` applied the PII grep gate before marking `ready_for_dooc` (recorded in `value-proof.md`). It does not revalidate PII on input; it documents the trust boundary in the `Boundary input validation` section.

If the PoV is **not** yet `ready_for_dooc` in `value-proof.md`, the Kata aborts with a clear error — a context pack based on an immature PoV violates the spirit of the DoOC.

## Workflow

```
Progress:
- [ ] 1. Validate --from-pov input (when applicable)
- [ ] 2. Curate ≥ 5 positive few-shot
- [ ] 3. Curate ≥ 10 negative examples
- [ ] 4. Select telemetry snippets (30-90 days)
- [ ] 5. Declare re-curation policy
- [ ] 6. Final validation
```

### Step 1: Validate `--from-pov` input (when applicable)

1. If `--from-pov` provided:
   - Verify `pov_path/value-proof.md::status == ready_for_dooc`. Fail if different
   - Verify `pov_path/context-pack.md` exists (it is the primary source)
   - Verify `pov_path/observability/` contains the 4 expected files
2. If `--from-pov` absent:
   - In `entry_mode: direct-entry`, record `cold-start` mode: few-shot must be synthesized from the domain (without real inputs); mark obligation of re-curation after the first 7 days of production via automated runbook

### Step 2: Curate ≥ 5 positive few-shot

Priority sources (in order):

1. **PoV `context-pack.md`** (when `with-pov`) — copy/refine the examples that proved consistent success
2. **PoV `observability/prompts-log.md`** (real sample of pre-operational usage, anonymized)
3. **Domain** (when `direct-entry`/`cold-start`) — synthesize from `docs/{context}/entities/` + `docs/{context}/features/`

Each few-shot MUST contain:

```markdown
### Positive example #{N}: {short name}

**Scenario:** {1-2 sentences about context}

**Input (sanitized):**
```
{user input, with PII redacted}
```

**Expected thought:**
```
{thought process — for react/reflexion patterns}
```

**Tools invoked:**
- `{tool-name}` with input `{}`

**Expected output:**
```
{canonical output, per schema declared in system-prompt.md::Block 4}
```

**Origin:** PoV {agent-pov-slug} | synthetic derived from {entity}
```

### Step 3: Curate ≥ 10 negative examples

Negative examples = anti-patterns. **Minimum 10** in production (vs. ≥ 2 in the PoV — differential rigor). Required categories:

| Category | Minimum | Source |
|----------|---------|--------|
| Out-of-scope (input outside the agent's scope) | 2 | PoV scope.md + synthesis |
| Unresolved ambiguity (asks for clarification, does not guess) | 2 | PoV observability |
| PII leakage (agent MUST NOT reveal PII in given context) | 2 | guardrails |
| Prompt injection (adversarial input attempts to override system prompt) | 2 | `kata-system-prompt-adversarial-validate` outputs |
| Tool injection (input requests tool outside catalog) | 1 | guardrails |
| Cross-tenant boundary (input requests data from another `org_id`) | 1 | guardrails |

Each negative example:

```markdown
### Negative example #{N}: {short name}

**Category:** out-of-scope | ambiguity | pii-leakage | prompt-injection | tool-injection | cross-tenant

**Input (adversarial or edge case):**
```
{input}
```

**INCORRECT behavior:**
```
{what the agent MUST NOT do — and why}
```

**CORRECT behavior:**
```
{structured refusal with error code per lex-error-handling | escalation via escalation.md | clarification request}
```

**Origin:** PoV observability | guardrails | adversarial suite
```

### Step 4: Select telemetry snippets

When `with-pov`, include:

1. Typical trace (`agent.turn` + `agent.tool_call` for an easy case) — sanitized
2. Edge-case trace (medium case with resolved ambiguity) — sanitized
3. Outcome distribution observed in the PoV (% success, % escalated, % rejected)

Snippets MUST be hash-only for any residual PII.

In `direct-entry`/`cold-start`, omit this section; mark obligation to add after 30 days of production (re-curation).

### Step 5: Declare re-curation policy

```markdown
## Re-curation policy

- **Cadence:** {weekly | monthly | quarterly} — default quarterly
- **Automatic trigger:** pivot trigger fired in `feedback.md`
- **Owner:** {agent owner declared in overview.md}
- **Process:** invoke `kata-agent-context-pack-design --refresh` with the latest telemetry snapshot
- **Versioning:** changes to `context-pack.md` recorded in `Appendix — Versions` with date + PR ref
```

### Final Validation

- [ ] ≥ 5 positive few-shot with complete schema
- [ ] ≥ 10 negative examples covering the 6 required categories (minimums per category)
- [ ] In `with-pov`, source of each example declared (PoV path or synthesis)
- [ ] Telemetry snippets sanitized when `with-pov`
- [ ] Re-curation policy declared with cadence + owner
- [ ] PII redaction confirmed on input (trust boundary documented for `with-pov`)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `context-pack.md` | Markdown | `docs/{context}/agents/{agent}/context-pack.md` |

## Structure of `context-pack.md`

```markdown
# Context Pack — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **Source:** {with-pov: docs/{context}/agents-pov/{pov-agent}/} | {direct-entry: synthesized from domain}
> **Re-curation cadence:** {cadence}
> **Last refresh:** {ISO 8601}

## Boundary input validation

- **PII trust boundary:** we trust the PII grep gate applied by `kata-pov-value-track::Step 4` on the origin PoV (when `with-pov`). This Kata does not revalidate PII; it assumes `pov_path/value-proof.md::status == ready_for_dooc` as proof of gate approval
- **Source attribution:** each example declares its origin (PoV path | synthetic)
- **Versioning:** changes pass through `kata-system-prompt-adversarial-validate` when they alter negatives related to prompt injection

## Positive few-shot (≥ 5)

(sections `### Positive example #{N}` per Step 2)

## Negative examples (≥ 10)

(sections `### Negative example #{N}` per Step 3)

## Observed telemetry (30-90 days)

(snippets from Step 4)

## Re-curation policy

(per Step 5)

## Appendix — Versions

- v1.0.0 — {date} — first version derived from PoV {pov-path} (PR ref)
- v1.1.0 — {date} — quarterly re-curation (PR ref)

## References

- `lex-agent-construction-directives::Directive 06`
- `system-prompt.md` — identity the context-pack reinforces
- `guardrails.md` — negative categories aligned with controls
- `feedback.md` — pivot trigger fires re-curation
- `kata-system-prompt-adversarial-validate` — suite invoked when negatives change
- `docs/{context}/agents-pov/{pov-agent}/` — primary source in `with-pov` mode
```

## Constraints

- < 5 positive few-shot violates Directive 06 at production rigor
- < 10 negative examples violates Directive 06 at production rigor
- Invented few-shot when a PoV is available is prohibited — prefer real sources
- Immature PoV (`value-proof.md::status != ready_for_dooc`) as a source is prohibited — Kata aborts
- Telemetry snippets with clear (un-sanitized) PII are prohibited

---

**Model:** The Kata is the canonical PoV → Operational Concrete bridge. Reads 12 files from the Claudionor output when `--from-pov`, enriches the context pack with real material (few-shot + negatives + telemetry). In `direct-entry`, operates in cold-start mode with post-deploy re-curation obligation. Trusts (does not revalidate) the PoV PII gate.
