# Lexis: Entity Naming Conventions — snake_case

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — entity identifiers, field names, CloudEvents type segments, and database column names

## Purpose

Naming inconsistency between domain model, APIs, events, and databases is a persistent source of integration bugs, confusion in code review, and broken interoperability between services. Enforcing a single casing convention across all system boundaries eliminates an entire class of mapping errors.

## Law

> **Every `entity_type` value, JSON field name, database column name, and variable segment in the CloudEvents type format (`{module}`, `{entity_type}`, `{event_name}`) MUST use snake_case. In domain model documents (DDD artifacts), aggregate and entity names used as conceptual identifiers MUST use PascalCase. Using camelCase, PascalCase, or kebab-case for `entity_type` values, JSON property names, or CloudEvents type segments is FORBIDDEN.**

## Rules

### 1. entity_type values

`entity_type` is a string identifier for the entity class. It MUST:
- Use snake_case: `scheduled_transfer`, `ledger_entry`, `reconciliation_run`
- Be singular (not plural): `scheduled_transfer`, not `scheduled_transfers`
- Be stable: changing `entity_type` is a breaking change and requires an ADR

### 2. JSON field names (APIs and events)

All field names in JSON request bodies, response payloads, and CloudEvents `data` objects MUST use snake_case:
- Correct: `entity_id`, `created_at`, `idempotency_key`, `scheduled_date`, `failure_reason`
- Incorrect: `entityId`, `createdAt`, `idempotencyKey`, `scheduledDate`, `failureReason`

### 3. CloudEvents type segments

The CloudEvents type format `event.guardia.{module}.{entity_type}.{event_name}` requires all variable segments in snake_case:
- `{module}`: `platform`, `reconciliation`, `fiscal`
- `{entity_type}`: `scheduled_transfer`, `ledger_entry`
- `{event_name}`: `created`, `approved`, `executed`, `failed`, `cancelled`
- Full example: `event.guardia.platform.scheduled_transfer.approved`

### 4. Database column names

Database column names MUST use snake_case:
- Correct: `entity_id`, `entity_type`, `created_at`, `scheduled_date`
- Incorrect: `entityId`, `EntityType`, `created-at`

### 5. Domain model documents — exception for PascalCase

In DDD artifacts (domain model documents, bounded context diagrams, aggregate definitions), **aggregate and entity names used as conceptual identifiers** MUST use PascalCase. This is the sole exception to snake_case:
- Aggregate in DDD doc: `ScheduledTransfer`, `LedgerEntry`, `ReconciliationRun`
- The same entity in APIs and events: `entity_type: "scheduled_transfer"`, `event.guardia.platform.scheduled_transfer.created`

PascalCase in DDD documents reflects domain language; snake_case at system boundaries enforces technical consistency.

### 6. URL path segments — kebab-case (not entity naming)

API resource URL path segments follow kebab-case (`/v1/scheduled-transfers`) per RESTful conventions (`lex-restful-apis`). This is API routing, not entity naming — `entity_type` in the payload remains snake_case even when the URL uses kebab-case.

## Scope

- **Applies to:** entity modeling, API contracts (OpenAPI/JSON), CloudEvents payloads, database schemas, domain model documents, event documentation.
- **Bound agents:** all agents that create or review entities, APIs, events, or domain models (warrior-theseus, warrior-daedalus, warrior-kronos, warrior-apollo, warrior-hera).
- **Exceptions:** third-party integration field names that arrive in camelCase from external systems — map at the anti-corruption layer boundary; do not propagate camelCase internally.

## Examples

### Correct

```json
{
  "entity_id": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entity_type": "scheduled_transfer",
  "scheduled_date": "2026-04-30",
  "failure_reason": null,
  "created_at": "2026-04-26T10:00:00Z",
  "updated_at": "2026-04-26T10:00:00Z",
  "version": 1
}
```

CloudEvents type: `event.guardia.platform.scheduled_transfer.approved`

Domain model doc aggregate: `ScheduledTransfer`

### Incorrect

```json
{
  "entityId": "01957f3e-...",
  "entityType": "ScheduledTransfer",
  "scheduledDate": "2026-04-30",
  "failureReason": null,
  "createdAt": "2026-04-26T10:00:00Z"
}
```

CloudEvents type (invalid): `event.guardia.platform.scheduledTransfer.Approved`

## Automated Validation

- **Tool:** JSON Schema / OpenAPI linter with property name pattern `^[a-z][a-z0-9_]*$`; CloudEvents type regex `^event\.guardia\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`; database migration linter (squawk) checking column name casing.
- **When:** pre-commit, CI (OpenAPI validation), PR review for domain model documents.
- **Metric:** 0 camelCase or PascalCase field names in JSON schemas; 0 CloudEvents types with non-snake_case segments; 0 database columns outside snake_case.

## References

- `lex-entities` — base entity structure (entity_id, entity_type, version, timestamps)
- `lex-cloudevents` — CloudEvents type format and structure
- `lex-restful-apis` — API URL conventions (kebab-case for path segments)
- `codex-entities` — entity model reference
