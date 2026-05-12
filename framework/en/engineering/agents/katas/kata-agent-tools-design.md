# Kata: Tripartite Tool Catalog Design

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents: design of the agent's tool catalog (`tools.md`) in `operational-concrete`

## Objective

Produce the agent's canonical tool catalog, split into **three categories** per `lex-agent-construction-directives::Directive 03 — Concrete Tools`:

1. **Deterministic** — deterministic functions (key lookup, validations, controlled parsing)
2. **ML** — trained models or specific inference (classification, embeddings, OCR)
3. **MCP** — tools exposed via an MCP server (per `lex-mcp` and `codex-mcp-common`)

The catalog declares the contract (input, output, idempotency, typical latency, lateral effects) of each tool. Strictly covers **Directive 03**.

## When to Use

- After `kata-agent-orchestrator-design` and (when applicable) `kata-agent-specialists-design`
- When the agent needs a catalog revision (new tool added, tool deprecated via ADR)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `context` | Yes | Bounded Context |
| `agent` | Yes | Agent slug |
| `orchestrator_path` | Yes | `docs/{context}/agents/{agent}/orchestrator.md` |
| `specialists_paths` | No | List of `docs/{context}/agents/{agent}/specialists/{name}.md` |
| `--from-pov <path>` | No | PoV path; inherits the subset of tools proven and disambiguates the production catalog |

## Workflow

```
Progress:
- [ ] 1. Extract tools mentioned in orchestrator + specialists
- [ ] 2. Classify each tool (deterministic | ML | MCP)
- [ ] 3. Declare each tool's contract (I/O, idempotency, lateral effects)
- [ ] 4. Verify idempotency where writes are involved
- [ ] 5. Input validation at the boundary
- [ ] 6. Final validation
```

### Step 1: Extract mentioned tools

Read `orchestrator.md::Workflow (with tools and dependencies)` and each `specialists/{name}.md::Tools consumed`. Consolidate into a single list.

### Step 2: Classify each tool

| Signal | Category |
|--------|----------|
| Pure function without external call, 100% deterministic output for fixed input | **Deterministic** |
| Inference via model (classifier, embeddings, regressor, OCR, ASR) | **ML** |
| Call via MCP server listed in `mcp.servers` in `.ahrena/.directives` | **MCP** |
| External HTTP call without MCP | **MCP** (MUST be exposed via MCP per `lex-mcp` when feasible) or justification in ADR |

Each tool appears in **exactly one** category. Duplication is prohibited.

### Step 3: Declare each tool's contract

Canonical template for `tools.md`:

```markdown
# Tools — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **Source of truth:** this file. Tools used at runtime MUST be present in this catalog; tools outside the catalog are blocked by guardrail (cross-link `guardrails.md::Tool injection`).

## Deterministic

### `{tool-name}`

- **Description:** {1-2 sentences}
- **When to use:** {concrete trigger}
- **Input schema:** {JSON schema or Pydantic model reference}
- **Output schema:** {JSON schema}
- **Idempotency:** yes (pure function)
- **Lateral effects:** none
- **Typical latency:** < {N}ms
- **Possible errors:** {codes per lex-error-handling}

(repeat for each deterministic tool)

## ML

### `{tool-name}`

- **Description:** {model + version + training dataset}
- **When to use:** {trigger}
- **Input schema:** {}
- **Output schema:** {with confidence score}
- **Idempotency:** partial (same model + same version → deterministic output modulo random seed)
- **Lateral effects:** paid inference usage (cost declared in model ADR)
- **Typical latency:** ~ {N}ms p99
- **Confidence threshold:** {value} (below → escalate via `escalation.md`)
- **Model version:** {tag/SHA}
- **Retrain trigger:** {when the model is retrained}

(repeat for each ML tool)

## MCP

### `{tool-name}`

- **MCP server:** `{server-name}` (declared in `mcp.servers` in `.ahrena/.directives`)
- **Description:** {1-2 sentences}
- **When to use:** {trigger}
- **Input schema:** {}
- **Output schema:** {}
- **Idempotency:** yes/no — when "no", MUST receive `Idempotency-Key` on input per `lex-idempotency`
- **Lateral effects:** {writes to external system: ERP, bank, email, S3}
- **Typical latency:** ~ {N}ms p99
- **Retry policy:** {exponential backoff, max retries, circuit breaker}
- **Possible errors:** {codes per lex-error-handling}
- **Auth:** credentials via environment variable per `lex-mcp` (never in code)

(repeat for each MCP tool)

## Idempotency

Tools that produce lateral effects (MCP category, mostly) MUST be idempotent per `lex-idempotency`. Implementation:

- Endpoint receives `Idempotency-Key` in header or input
- The MCP server deduplicates by key + payload hash
- Retry with the same key + same payload returns the same result (no duplicate effect)

Tools that fail this requirement MUST be deprecated and replaced.

## Input validation at the boundary

Every tool MUST validate input before executing:

- Schema validation via Pydantic or Zod
- Strict type checking
- Bounds checking (e.g., `amount > 0` per aggregate invariant)
- `org_id`/`client_id` checking — the tool never crosses tenant boundary

Cross-link `guardrails.md::Tool injection` for OWASP controls.

## References

- `lex-agent-construction-directives::Directive 03`
- `lex-mcp`, `codex-mcp-common`
- `lex-idempotency`
- `lex-error-handling`, `codex-known-errors`
- `guardrails.md` — OWASP controls applied to tools
- `orchestrator.md`, `specialists/` — who invokes what
```

### Step 4: Verify idempotency where writes are involved

For each tool in `MCP` with `lateral effects ≠ none`:

1. Confirm that it accepts `Idempotency-Key`
2. Confirm that the MCP server deduplicates
3. Confirm that the retry policy does not duplicate the effect

When it fails, record the tool as `pending idempotency review` in the promotion PR; block the merge until resolved.

### Step 5: Input validation at the boundary

For each tool:

- A schema exists (Pydantic, Zod, or equivalent)
- The schema validates `org_id`/`client_id` when applicable
- Validation errors return `ERR400_INVALID_PARAMETER` per `lex-error-handling`

### Final Validation

- [ ] Every tool appears in exactly one category
- [ ] Tools with lateral effects have verified idempotency
- [ ] ML tools declare model version + confidence threshold
- [ ] MCP tools reference a server declared in `mcp.servers`
- [ ] Schemas declared (input + output) — no placeholders
- [ ] Cross-references with `guardrails.md` for applied OWASP controls

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `tools.md` | Markdown | `docs/{context}/agents/{agent}/tools.md` |

## Constraints

- Every tool MUST belong to one of the 3 categories; a fourth category is prohibited without ADR
- Tools with lateral effects without idempotency are prohibited in `operational-concrete`
- A tool exposed directly without an MCP server is prohibited when MCP is feasible (per `lex-mcp`); justification requires an ADR
- Do not duplicate tools across categories

---

**Model:** The Kata produces a tripartite catalog (deterministic | ML | MCP) with clear contracts. Every tool used at runtime MUST be present in this file; guardrails block tools outside the catalog.
