Full Design — API and Events. Single process that combines REST API design and CloudEvents documentation for a new feature

# Cry: Full Design — API and Events

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Single process that combines REST API design and CloudEvents documentation for a new feature

## Usage

```
/cry-full-design <feature description> [base path] [events context]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature description` | Yes | Description of domain, entities, API operations, and business rules; used as the base for both the API and the event storm | "Scheduled transfers module: create, list, update, cancel; paginated listing; idempotent mutations; events created, updated, cancelled" |
| `base path` | No | URL prefix for the API (e.g., /v1/scheduled-transfers). If omitted, Daedalus proposes one | `/v1/scheduled-transfers` |
| `events context` | No | Specific complement for events (e.g., module, entity type, source base). If omitted, Kronos infers from the feature context or asks | "Module platform, entity type scheduled_transfer" |

## What the Command Does

1. **Phase 1 — API:** Assumes the role of the Daedalus Warrior; executes **kata-api-design-oas** and **kata-api-design-doc**; produces OpenAPI specification and API document in **`docs/{context}/oas/`**
2. **Phase 2 — Events:** Assumes the role of the Kronos Warrior; executes **kata-events-doc**; produces events documentation in **`docs/{context}/events/`**
3. Uses the same feature description as input for both phases; in phase 2, may use the explicit events context or infer from the designed API
4. Delivers a summary of produced artifacts: OAS and API doc in `docs/{context}/oas/`; events doc in `docs/{context}/events/`

## Prompt Template

```
Context:
- Feature description: {{feature description}}
- Base path (optional): {{base path}}
- Events context (optional): {{events context}}

Task:
Execute the **full design** process in sequence:

1) **API phase (Daedalus):** Act as the Daedalus Warrior. Execute **kata-api-design-oas** and **kata-api-design-doc** based on the feature description. Ask clarifying questions if needed (scope, authentication, pagination, base path). Produce OpenAPI specification and API document in **`docs/{context}/oas/`**.

2) **Event Storm phase (Kronos):** Act as the Kronos Warrior. Based on the same feature (and events context, if provided), execute **kata-events-doc**. Identify relevant events (e.g., created, updated, cancelled for the API operations), ask clarifying questions if needed, and produce the events documentation in **`docs/{context}/events/`**.

Deliver a final summary: artifacts in `docs/{context}/oas/` (OAS + API doc) and in `docs/{context}/events/` (events doc).
```

## Invocation Example

**Input:**

```
/cry-full-design "Scheduled transfers module: create, list, update, cancel; paginated sortable listing; idempotent mutations; events created, updated, cancelled" /v1/scheduled-transfers
```

**Expected output:**

- **Phase 1:** Resources and endpoints (POST, GET, GET/:id, PATCH, DELETE); OpenAPI specification and API document created/updated in **`docs/{context}/oas/`**
- **Phase 2:** Event catalog (event.guardia.platform.scheduled_transfer.created, .updated, .cancelled); events document created/updated in **`docs/{context}/events/`**
- Summary: three artifacts — OAS and API doc in `docs/scheduled-payments/oas/`; events doc in `docs/scheduled-payments/events/`

## Constraints

- The Cry does not implement code; it only orchestrates the two Warriors
- The feature description must support both API design and event identification; if information for events is missing, Kronos will ask questions in phase 2
- Exceptions to Lexis must be documented in an ADR

## Associated Cries and Warriors

- **cry-api-design** — API design only (Daedalus)
- **cry-event-storm** — Event documentation only (Kronos)
- **warrior-daedalus** — API Design Specialist
- **warrior-kronos** — Event Storm Specialist
