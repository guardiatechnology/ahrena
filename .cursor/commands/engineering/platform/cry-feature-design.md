---
description: "Feature Design — Domain, API, and Events. Complete feature design cycle: domain modeling, REST API design, and CloudEvents documentation in sequence"
---

# Cry: Feature Design — Domain, API, and Events

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Complete feature design cycle: domain modeling, REST API design, and CloudEvents documentation in sequence

## Description

This command orchestrates the complete feature design cycle by invoking the Prometheus Warrior, who coordinates in sequence: (1) domain modeling (warrior-theseus), (2) REST API design (warrior-daedalus), and (3) events documentation (warrior-kronos). Artifacts are produced in **`docs/{context}/entities/`**, **`docs/{context}/oas/`**, and **`docs/{context}/events/`** respectively.

## Usage

```
/cry-feature-design <feature description> [base path] [events context]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature description` | Yes | Description of domain, entities, operations, and business rules; used as the base for the complete cycle | "Scheduled transfers module: create, list, update, and cancel; paginated listing; idempotent mutations; events emitted on each state transition" |
| `base path` | No | URL prefix for the API (e.g.: /v1/scheduled-transfers). If omitted, Daedalus proposes one | `/v1/scheduled-transfers` |
| `events context` | No | Specific complement for events (e.g.: module, entity type). If omitted, Kronos infers from context | "Module platform, entity scheduled_transfer" |

## What the Command Does

1. Invokes the Prometheus Warrior to orchestrate the complete design cycle
2. **Phase 1 — Domain:** Prometheus delegates to warrior-theseus; produces entities and domain model in **`docs/{context}/entities/`**
3. **Phase 2 — API:** Prometheus delegates to warrior-daedalus; produces OpenAPI specification and API document in **`docs/{context}/oas/`**
4. **Phase 3 — Events:** Prometheus delegates to warrior-kronos; produces events documentation in **`docs/{context}/events/`**
5. Prometheus verifies consistency across the three artifacts and delivers a design package summary

## Prompt Template

```
Context:
- Feature description: {{feature description}}
- Base path (optional): {{base path}}
- Events context (optional): {{events context}}

Task:
Act as the Prometheus Warrior (Technical Product Manager) and execute the complete feature design cycle in sequence:

1) **Domain Phase (Theseus):** Delegate to warrior-theseus. Execute kata-domain-model to model entities, aggregates, business rules, and invariants. Ask clarifying questions when necessary. Produce entity artifacts in **`docs/{context}/entities/`**.

2) **API Phase (Daedalus):** Delegate to warrior-daedalus. Execute kata-api-design-oas and kata-api-design-doc based on the designed entities. Ask clarifying questions when necessary. Produce OpenAPI specification and API document in **`docs/{context}/oas/`**.

3) **Events Phase (Kronos):** Delegate to warrior-kronos. Execute kata-events-doc based on the entities and API operations. Ask clarifying questions when necessary. Produce events documentation in **`docs/{context}/events/`**.

4) **Consistency Verification:** Verify that entities, API, and events are consistent with each other. Deliver a complete design package summary.
```

## Invocation Example

**Input:**

```
/cry-feature-design "Scheduled transfers module: create, list, update, and cancel; paginated and sortable listing by date; idempotent mutations; events emitted on each state transition" /v1/scheduled-transfers "module platform, entity scheduled_transfer"
```

**Expected output:**

Complete design package produced by Prometheus with:
- **Entities:** `docs/scheduled-payments/entities/scheduled-transfer.md` — domain model with fields, business rules, and invariants
- **API:** `docs/scheduled-payments/oas/openapi.yaml` + Markdown document — POST/GET/PATCH/DELETE endpoints with pagination and idempotency
- **Events:** `docs/scheduled-payments/events/events.md` — catalog with `requested`, `approved`, `executed`, `failed`, `cancelled`
- Consistency verification across the three artifacts

## Constraints

- The Cry does not implement code; it only orchestrates the complete design cycle
- The feature description must be sufficient for all three phases; if incomplete, each specialist Warrior will ask its own questions
- Exceptions to Lexis must be documented in an ADR

## Cry vs Individual Katas

| Aspect | Cry | Individual Katas |
|--------|-----|-----------------|
| **Nature** | Orchestration of the complete cycle in one command | Execution of a specific phase |
| **Complexity** | Medium (3 phases coordinated by Prometheus) | High per phase (each Kata has multiple steps) |
| **Configures agent?** | Yes (Prometheus + the three Warriors) | Yes (the specific Warrior or agent for the phase) |
| **Example** | "/cry-feature-design complete scheduled transfers domain" | "/cry-api-design only the transfers API" |

## Associated Warriors

- **warrior-prometheus** — Orchestrator of the complete design cycle
- **warrior-theseus** — Domain modeling; produces `docs/{context}/entities/`
- **warrior-daedalus** — REST API design; produces `docs/{context}/oas/`
- **warrior-kronos** — Events documentation; produces `docs/{context}/events/`

## References

- `lex-feature-design-docs` — canonical structure `docs/{context}/{category}/`
- `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, `warrior-kronos` — Warriors invoked by this Cry
