# Kata: 3-Layer Memory Design

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents: design of the agent's memory in `operational-concrete`, producing `memory.md` with 3 mandatory layers

## Objective

Produce the agent's canonical memory file, with **3 mandatory layers** per `lex-agent-construction-directives::Directive 02 — Layered Memory`:

1. **Short** — current session context window
2. **Medium** — client history (by `org_id`/`client_id`), TTL of weeks to months
3. **Long** — stable knowledge (business rules, taxonomies, catalog embeddings) — indefinite TTL with retraining

Each layer MUST declare schema, TTL, retention (per `lex-data-retention`), and PII handling. Strictly covers **Directive 02**.

## When to Use

- After `kata-agent-tools-design` (tools consume memory; order matters)
- When the agent needs a memory-architecture revision (retention change, long-layer expansion)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `context` | Yes | Bounded Context |
| `agent` | Yes | Agent slug |
| `overview_path` | Yes | `docs/{context}/agents/{agent}/overview.md` (for tier + use case) |
| `tools_path` | Yes | `docs/{context}/agents/{agent}/tools.md` |
| `--from-pov <path>` | No | PoV path; in pre-operational there was only the short layer — Mêtis expands to 3 |

## Workflow

```
Progress:
- [ ] 1. Read overview + tools
- [ ] 2. Declare short layer (session)
- [ ] 3. Declare medium layer (client history)
- [ ] 4. Declare long layer (stable knowledge)
- [ ] 5. Declare retention policy (per lex-data-retention)
- [ ] 6. Declare PII handling (redaction, anonymization, right-to-be-forgotten)
- [ ] 7. Final validation
```

### Step 1: Read overview + tools

1. Read `overview.md` to extract tier, primary use case, and `serves_features`
2. Read `tools.md` to identify which tools consume each layer
3. In `with-pov`, read `pov-path/system-prompt.md` and any notes about memory — usually only the short layer (session window)

### Step 2: Declare short layer

Short layer = current session context window. Always present. Typical schema:

```yaml
short_layer:
  scope: "session"
  storage: "in-process (LLM context window)"
  ttl: "session lifetime"
  size_limit: "tokens (per model)"
  schema:
    - turn_history: list of turns (user, assistant, tool_call, tool_result)
    - working_memory: variables accumulated in the reasoning loop
  pii_handling: "PII from user input stays in the window during the session; persists in redacted form only in medium/long layers"
  retention: "closed at session end"
```

### Step 3: Declare medium layer

Medium layer = client history, indexed by `org_id`/`client_id`. Returns context between sessions. Typical schema:

```yaml
medium_layer:
  scope: "per-tenant (org_id + client_id)"
  storage: "Postgres or DynamoDB (declare)"
  ttl: "{30 to 180 days, per retention policy}"
  size_limit: "{N} events per client"
  schema:
    - event_id: UUID v7
    - org_id: UUID
    - client_id: UUID
    - agent_id: slug
    - event_type: enum
    - payload: JSON
    - created_at: timestamp
    - pii_redacted: boolean
  pii_handling: "PII redacted by default; sensitive fields (national ID, email, phone) replaced by hash + last 4 digits when audit-relevant"
  retention: "per docs/data-retention.yaml; default 90 days after client's last activity"
  right_to_be_forgotten: "DELETE by client_id within ≤ 15 days of request (LGPD Art. 18 / GDPR Art. 17)"
```

### Step 4: Declare long layer

Long layer = stable knowledge shared across tenants. Contains no PII. Typical schema:

```yaml
long_layer:
  scope: "shared (no org_id/client_id)"
  storage: "S3 + index (Pinecone, OpenSearch, or pgvector — declare)"
  ttl: "indefinite (with retraining)"
  size_limit: "{N} documents / embeddings"
  schema:
    - doc_id: UUID v7
    - doc_type: enum (rule | taxonomy | example | embedding)
    - content: text or vector
    - version: semver
    - created_at: timestamp
    - source: path/URL
  pii_handling: "ZERO PII — content is generic (rules, taxonomies). Client-derived content MUST be anonymized before ingestion"
  retention: "indefinite; retraining/update recorded via version"
  versioning: "semver; breaking changes require an ADR + re-embedding"
```

### Step 5: Declare retention policy (per `lex-data-retention`)

```yaml
retention_policy:
  reference: "docs/data-retention.yaml"
  classes:
    - name: "agent-{agent}-medium-memory"
      retention: "90 days after last activity"
      legal_basis: "LGPD Art. 16 — operational, minimum necessary"
      storage: "Postgres + S3 archive after 30d"
      enforcement: "cron job + retention column"
    - name: "agent-{agent}-long-memory"
      retention: "indefinite (with retraining)"
      pii: "none"
      storage: "S3 + vector index"
```

### Step 6: Declare PII handling

Per `lex-data-retention` and `lex-frontend-security` (PII handling):

1. **Redaction at boundary:** PII detected in input (regex for national ID, email, etc.) is redacted before persisting in medium/long layers
2. **Anonymization for the long layer:** any data derived from a client enters only after anonymization; identifiers hashed
3. **Right to be forgotten:** API `DELETE /agents/{agent}/memory?client_id={id}` deletes the client's medium/long layers; the short layer closes at the session end
4. **Audit log:** every PII read/write operation logged via structured log (per `lex-observability-required`)

### Final Validation

- [ ] All 3 layers declared (short, medium, long) — none omitted
- [ ] Each layer declares schema, TTL, retention, PII handling
- [ ] Long layer contains no PII
- [ ] Medium layer references `lex-data-retention` and `docs/data-retention.yaml`
- [ ] Right to be forgotten implemented (DELETE path declared)
- [ ] Tools that consume each layer listed (cross-link `tools.md`)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `memory.md` | Markdown | `docs/{context}/agents/{agent}/memory.md` |
| Update in `docs/data-retention.yaml` | YAML | add agent classes (when they do not yet exist) |

## Structure of `memory.md`

```markdown
# Memory — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **3 mandatory layers per `lex-agent-construction-directives::Directive 02`.**

## Layers

### Short

(YAML from Step 2)

### Medium

(YAML from Step 3)

### Long

(YAML from Step 4)

## Right to be forgotten

- **API endpoint:** {path}
- **SLA:** ≤ 15 days from request (LGPD Art. 18 / GDPR Art. 17)
- **Affected layers:** medium + long (retroactive anonymization when applicable)
- **Audit log:** recorded in {observability backend}

## References

- `lex-agent-construction-directives::Directive 02`
- `lex-data-retention`
- `docs/data-retention.yaml`
- `tools.md` — which tools consume each layer
- `metrics.md` — operational metrics for the layer (cache hit, query latency)
```

## Constraints

- The short layer is always present (not a decision)
- The long layer MAY be empty in a simple agent — declaring `not used` is accepted; OMITTING the section is prohibited
- PII in the long layer is prohibited per LGPD/GDPR
- Indefinite retention in layers with PII is prohibited
- Sharing memory across tenants (`org_id` cross) is prohibited in medium/short layers

---

**Model:** The Kata produces the 3-layer catalog. Every layer declared with schema, TTL, PII handling. Right to be forgotten implemented. Strict cross-link with `lex-data-retention`.
