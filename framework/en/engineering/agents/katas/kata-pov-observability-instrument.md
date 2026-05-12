# Kata: Instrument Observability in PoV

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): instrument native telemetry in the PoV — traces, prompts log, tool calls log, value metrics

## Objective

Produce `docs/{context}/agents-pov/{agent}/observability/` with 4 canonical files (`traces-spec.md`, `prompts-log.md`, `tool-calls-log.md`, `value-metrics.md`) declaring the PoV's observability **contract**: which spans, which log fields, which leading metrics. Observability is a **first-class citizen** in the PoV — without instrumentation, there is no base for Directive 06 (rich context for retrofit) nor for DoOC item 5 (observability data ≥ 7 days). Apply `lex-observability-required` at pre-operational rigor: 1 trace + 1 metric + structured log are enough.

## When to Use

- After `kata-pov-tools-select` (tools are input for `tool-calls-log.md`)
- In parallel with `kata-pov-feedback-attach` (value-metrics talk to the feedback criterion)
- When a PoV operation reveals a new leading metric to track

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `docs/{context}/agents-pov/{agent}/pov.md` | Yes | Defines the leading value metric |
| `docs/{context}/agents-pov/{agent}/tools.md` | Yes | Tools list for the logs |
| `lex-observability-required` | Yes | Minimum rigor (trace + metric + log) |
| `lex-data-retention` | Yes | PII restrictions in logs |

## Workflow

```
Progress:
- [ ] 1. Define spans (traces-spec.md)
- [ ] 2. Define prompts log schema (no PII)
- [ ] 3. Define tool calls log schema
- [ ] 4. Define leading metrics (value-metrics.md)
- [ ] 5. Cross-link with lex-observability-required (minimum rigor)
- [ ] 6. Persist observability/
```

### Step 1: Define spans (traces-spec.md)

Canonical structure (OpenTelemetry-compatible, **same schema Mêtis will adopt** — eases the bridge):

```yaml
# traces-spec.md (excerpt)

spans:
  - name: agent.turn
    attributes:
      - agent.name: <pov-name>
      - agent.stage: pre-operational
      - session_id: <opaque>
      - turn_index: <int>
      - input_tokens: <int>
      - output_tokens: <int>
      - latency_ms: <int>
      - outcome: success | error | refusal

  - name: agent.tool_call
    parent: agent.turn
    attributes:
      - tool.name: <web_search | code_execution | ...>
      - tool.duration_ms: <int>
      - tool.outcome: success | error | timeout
      - tool.error_class: <if outcome=error>
```

Each PoV explicitly declares which spans it emits. Minimum: `agent.turn`. Recommended when there are tools: `agent.turn` + `agent.tool_call`.

### Step 2: Define prompts log schema (no PII)

```yaml
# prompts-log.md (excerpt)

fields:
  - session_id: opaque, hashed
  - turn_index: int
  - prompt_hash: sha256(user_input)   # does NOT store raw text
  - prompt_token_count: int
  - context_size_tokens: int
  - timestamp: ISO 8601

excluded:
  - user_input (raw text)
  - PII (tax IDs, email, full name)

retention:
  - 30 days for active PoV
  - destroy at PoV closure
```

The schema lives in `lex-data-retention` by default; if the PoV justifies longer retention, record it in `value-proof.md` with the reason. Applying `lex-data-retention` is this kata's responsibility.

### Step 3: Define tool calls log schema

```yaml
# tool-calls-log.md (excerpt)

fields:
  - session_id: opaque, hashed
  - turn_index: int
  - tool_name: enum [web_search | code_execution | str_replace_editor | bash]
  - parameters_hash: sha256(parameters)   # does NOT store raw parameters
  - parameters_size_bytes: int
  - duration_ms: int
  - outcome: success | error | timeout
  - error_class: string | null
  - result_size_bytes: int   # NOT the content

excluded:
  - raw parameters (especially when they contain customer data)
  - result content

retention:
  - 30 days for active PoV
```

### Step 4: Define leading metrics (value-metrics.md)

**Operational** leading metrics the PoV must track continuously:

```markdown
# value-metrics.md (excerpt)

## Primary metric

- name: reconciliation_auto_rate
- definition: turns where the answer produced a pairing with confidence ≥ high / total turns
- frequency: per session and aggregated daily
- window: rolling 7 days
- discontinuation threshold: < 30% after 4 weeks

## Quality metrics

- name: refusal_rate
  - definition: turns with outcome=refusal / total turns
  - alarm: > 10% indicates a miscalibrated prompt
- name: avg_latency_ms
  - definition: p95 latency per turn
  - alarm: > 5000ms indicates a tool with timeout
```

### Step 5: Cross-link with lex-observability-required

At the end of `traces-spec.md`, add section `## Conformance with lex-observability-required`:

| Requirement | How the PoV meets it |
|---|---|
| 1 trace per work unit | `agent.turn` span emitted per turn |
| 1 leading metric | `reconciliation_auto_rate` (see value-metrics.md) |
| Structured logging with redacted PII | prompt_hash + parameters_hash (never raw) |
| Window ≥ 7 days for DoOC | retention 30 days declared |

### Step 6: Persist observability/

Create directory `docs/{context}/agents-pov/{agent}/observability/` with:

- `traces-spec.md`
- `prompts-log.md`
- `tool-calls-log.md`
- `value-metrics.md`

Add a short `README.md` listing the 4 files and the directory's purpose.

### Final Validation

- [ ] 4 files present in `observability/`
- [ ] `agent.stage: pre-operational` appears in `traces-spec.md`
- [ ] Logs declare a **hash** of prompt/parameters, never raw text
- [ ] `value-metrics.md` has 1 primary metric with a discontinuation threshold
- [ ] Cross-link `lex-observability-required` present

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `observability/traces-spec.md` | Markdown + YAML | `docs/{context}/agents-pov/{agent}/observability/` |
| `observability/prompts-log.md` | Markdown + YAML | same |
| `observability/tool-calls-log.md` | Markdown + YAML | same |
| `observability/value-metrics.md` | Markdown | same |
| `observability/README.md` | Markdown | same |

## Restrictions

- **Never** store raw prompt text or raw tool parameters — always a hash.
- **Never** the absence of a leading metric — without a metric, `kata-pov-value-track` cannot operate.
- **Never** indefinite retention in PoV — maximum is 90 days, and even that requires justification.
- **Always** the schema is the same one Mêtis (plan-032) will consume via `--from-pov`. Divergence here breaks the bridge.

---

**Model:** This Kata treats observability as a first-class citizen in PoV. The contract declared here is the bridge for `kata-dooc-validate` item 5.
