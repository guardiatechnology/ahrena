# Cry: Feature Design — Domain, API, and Events

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Complete feature design cycle: domain modeling, REST API design, and CloudEvents documentation in sequence

## Description

This command activates the **Prometheus Warrior** (Technical Product Manager) to orchestrate the complete feature design cycle in three sequential phases: domain modeling (warrior-theseus), API design (warrior-daedalus), and event documentation (warrior-kronos). Each phase uses the output of the previous phase as its authoritative input. The user confirms each phase before the next one begins.

## Usage

```
/cry-feature-design <feature description> [module] [constraints]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature description` | Yes | Description of the feature scope, business goal, and any known rules or actors | "Scheduled transfers: accountants create, supervisors approve, executed on the scheduled date" |
| `module` | No | CloudEvents module identifier. If omitted, Prometheus will ask | `platform` |
| `constraints` | No | Known constraints: security, compliance, existing integrations, breaking-change restrictions | "No breaking changes to existing /v1/transfers endpoints" |

## What the Command Does

1. **Assumes the role of warrior-prometheus** and reads `language.default` from `.ahrena/.directives`
2. **Asks clarifying questions** if the feature description, module, or constraints are insufficient
3. **Phase 1 — Domain Modeling (warrior-theseus):** models the domain iteratively; resolves P1 hotspots; confirms the domain model with the user before proceeding
4. **Phase 2 — API Design (warrior-daedalus):** designs the API using the domain model as authoritative input; confirms the API design with the user before proceeding
5. **Phase 3 — Event Documentation (warrior-kronos):** documents CloudEvents using the domain model and integration events from Phase 1; skips discovery (already done); confirms event documentation with the user
6. **Consistency check:** verifies that entity names, entity_type values, and CloudEvents type segments match the domain model across all outputs
7. **Delivers the final artifact package** with paths to all produced files

## Prompt Template

```
Context:
- Feature description: {{feature description}}
- Module (optional): {{module}}
- Constraints (optional): {{constraints}}

Task:
Act as the Prometheus Warrior (Technical Product Manager). Design artifacts are
persisted in the canonical structure `docs/{context}/{category}/` per
`lex-feature-design-docs`.

If the feature description, module, or constraints are insufficient, ask clarifying questions before starting.

Orchestrate the complete feature design cycle in sequence:

1) **Phase 1 — Domain Modeling (warrior-theseus):** Delegate to warrior-theseus with the feature description and module. Monitor P1 hotspots — do not advance until resolved. Present the domain model summary (entity catalog, use cases, integration events) and ask: "Does the domain model look correct? Should I proceed to API design?"

2) **Phase 2 — API Design (warrior-daedalus):** After explicit user confirmation, delegate to warrior-daedalus using the domain model document as primary input. Instruct Daedalus to use entity_type values and field names from the domain model (lex-entity-naming). Present the API design summary and ask: "Does the API design look correct? Should I proceed to event documentation?"

3) **Phase 3 — Event Documentation (warrior-kronos):** After explicit user confirmation, delegate to warrior-kronos with the domain model and integration events list. Instruct Kronos to skip discovery (events were identified in Phase 1) and go directly to documentation. Verify that CloudEvents type segments match entity_type values from the domain model. Present the events summary.

After all phases, verify consistency: entity names in APIs and events must match the domain model. Flag any divergence with a clear resolution path.

Deliver the final artifact package:
- Entities: `docs/{context}/entities/{entity}.md` (1 file per entity)
- API specification: `docs/{context}/oas/openapi.yaml` and `docs/{context}/oas/{slug}-api.md`
- Events document: `docs/{context}/events/events.md`
```

## Invocation Example

**Input:**

```
/cry-feature-design "Scheduled transfers: accountants schedule a transfer for a future date, supervisors approve transfers above BRL 10,000, the system executes on the scheduled date, failures trigger one retry after 30 minutes" platform
```

**Expected output:**

- **Phase 1 confirmation:** Entity catalog (`ScheduledTransfer`, entity_type `scheduled_transfer`), lifecycle, use cases, integration events — user confirms before Phase 2
- **Phase 2 confirmation:** Endpoints (POST /v1/scheduled-transfers, GET, GET/:id, PATCH, DELETE), Idempotency-Key, payloads — user confirms before Phase 3
- **Phase 3 confirmation:** CloudEvents catalog (`event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`) — final summary
- **Artifact package:**
  - `docs/scheduled-payments/entities/scheduled-transfer.md`
  - `docs/scheduled-payments/oas/openapi.yaml`
  - `docs/scheduled-payments/events/events.md`

## When to Use This Cry vs Others

| Cry | When to use |
|-----|-------------|
| **cry-feature-design** | Domain is unknown or must be modeled; need a consistent domain → API → events package |
| **cry-full-design** | Domain is already modeled; need only API + events from a feature description |
| **cry-api-design** | Domain is modeled and events are out of scope; need only the API |
| **cry-event-storm** | Need event discovery or documentation only (domain and API already exist) |

## Constraints

- Does not implement code — orchestrates design only
- Does not advance to the next phase without explicit user confirmation
- Does not skip Phase 1 (domain modeling) when the domain is genuinely unknown — a poorly modeled domain produces incorrect APIs and events
- Exceptions to Lexis must be documented in an ADR; Prometheus will signal when a decision requires one

## Associated Warriors and Katas

| Artifact | Role |
|----------|------|
| `warrior-prometheus` | Orchestrator — invoked by this Cry |
| `warrior-theseus` | Phase 1 — Domain Modeling |
| `warrior-daedalus` | Phase 2 — API Design |
| `warrior-kronos` | Phase 3 — Event Documentation |
| `kata-domain-model` | Executed by warrior-theseus |
| `kata-api-design-oas` | Executed by warrior-daedalus |
| `kata-api-design-doc` | Executed by warrior-daedalus |
| `kata-events-doc` | Executed by warrior-kronos |

## References

- `warrior-prometheus` — Technical Product Manager and feature design cycle orchestrator
- `lex-feature-design-docs` — canonical structure `docs/{context}/{category}/`
- `lex-entity-naming` — snake_case/PascalCase rules applied across all phases
- `lex-entities` — base entity structure (entity_id, entity_type, version, timestamps) consulted during domain modeling
- `lex-cloudevents` — CloudEvents type format consulted during event documentation
