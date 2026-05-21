# Lexis: Entity Naming and Identifier Conventions

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — entity types, identifiers, field names, CloudEvents type segments, and database column names

## Purpose

Naming inconsistency between domain model, APIs, events, and databases is a persistent source of integration bugs, confusion in code review, and broken interoperability between services. Enforcing canonical conventions across all system boundaries eliminates an entire class of mapping errors.

## Law

> **Every `entity_type` value MUST use UPPER_SNAKE_CASE (e.g., `TRANSACTION`, `SCHEDULED_TRANSFER`). Every JSON field name and database column name MUST use snake_case. Every `entity_id` MUST be formatted as `{entity_id_prefix}:{uuid_v7}`, where the prefix is a 2–5 character lowercase alphanumeric string defined before development starts. Entity identifier fields in external JSON payloads MUST follow the convention `{entity_name}_id` — the suffix `_entity_id` is FORBIDDEN. In CloudEvents `type` segments, `{entity_name}` MUST be the lowercase form of the UPPER_SNAKE_CASE `entity_type`. Using camelCase or PascalCase for `entity_type` values, JSON property names, or CloudEvents type segments is FORBIDDEN.**

## Rules

### 1. entity_type values — UPPER_SNAKE_CASE

`entity_type` is the canonical discriminator for the entity class. It MUST:
- Use UPPER_SNAKE_CASE: `TRANSACTION`, `SCHEDULED_TRANSFER`, `LEDGER_ENTRY`
- Be singular (not plural): `TRANSACTION`, not `TRANSACTIONS`
- Be stable: changing `entity_type` is a breaking change and requires an ADR

The only contexts where `entity_type` appears in lowercase are:
- URL path segments (e.g., `/v1/scheduled-transfers` in kebab-case per `lex-restful-apis`)
- The CloudEvents `type` field `{entity_name}` segment (e.g., `SCHEDULED_TRANSFER` → `scheduled_transfer`), as a declared exception justified by the CloudEvents reverse-DNS dot-notation standard

### 2. entity_id format — {entity_id_prefix}:{uuid_v7}

Every entity identifier MUST be formatted as:

```
{entity_id_prefix}:{uuid_v7}
```

- `entity_id_prefix`: 2–5 lowercase alphanumeric characters defined before development starts (e.g., `txn`, `rec`, `org`, `per`, `doc`)
- `uuid_v7`: UUID v7 per [RFC 9562](https://datatracker.ietf.org/doc/html/rfc9562), ensuring temporal ordering
- Example: `txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

The prefix MUST be declared in the entity's design document before coding begins. Changing a prefix is a breaking change requiring an ADR.

### 3. Identifier field naming — {entity_name}_id

When referencing an entity by its identifier in a JSON payload from another entity:
- The field MUST be named `{entity_name}_id`, where `{entity_name}` is the lowercase form of the `entity_type`
- Correct: `transaction_id`, `ledger_entry_id`, `scheduled_transfer_id`
- The suffix `_entity_id` is FORBIDDEN: never use `transaction_entity_id`, `ledger_entry_entity_id`

Exception: within the entity's own payload, the canonical identifier field is always `entity_id`.

### 4. JSON field names — snake_case

All field names in JSON request bodies, response payloads, and CloudEvents `data` objects MUST use snake_case:
- Correct: `entity_id`, `created_at`, `idempotency_key`, `scheduled_date`, `failure_reason`
- Incorrect: `entityId`, `createdAt`, `idempotencyKey`, `scheduledDate`, `failureReason`

### 5. CloudEvents type segments — lowercase

The CloudEvents type format `event.{provider}.{domain}.{entity_name}.{event_name}` requires all variable segments in lowercase snake_case:
- `{provider}`: `guardia` for internal events; external provider name for mapped external events
- `{domain}`: `platform`, `reconciliation`, `fiscal`
- `{entity_name}`: lowercase form of the UPPER_SNAKE_CASE `entity_type` (e.g., `SCHEDULED_TRANSFER` → `scheduled_transfer`)
- `{event_name}`: `created`, `approved`, `executed`, `failed`, `cancelled`
- Full example: `event.guardia.financial.scheduled_transfer.approved`

### 6. Database column names — snake_case

Database column names MUST use snake_case:
- Correct: `entity_id`, `entity_type`, `created_at`, `scheduled_date`
- Incorrect: `entityId`, `EntityType`, `created-at`

### 7. Domain model documents — exception for PascalCase

In DDD artifacts (domain model documents, bounded context diagrams, aggregate definitions), **aggregate and entity names used as conceptual identifiers** MUST use PascalCase. This is the sole exception:
- Aggregate in DDD doc: `ScheduledTransfer`, `LedgerEntry`, `Transaction`
- The same entity at system boundaries: `entity_type: "SCHEDULED_TRANSFER"`, `event.guardia.financial.scheduled_transfer.created`

PascalCase in DDD documents reflects domain language; UPPER_SNAKE_CASE at system boundaries enforces technical consistency.

### 8. URL path segments — plural kebab-case

API resource URL path segments follow **plural kebab-case** per RESTful conventions (`lex-restful-apis`). The plural form is derived from the singular UPPER_SNAKE_CASE `entity_type`:

| `entity_type` (data) | URL resource segment |
|----------------------|----------------------|
| `TRANSACTION` | `transactions` |
| `RECORD` | `records` |
| `SCHEDULED_TRANSFER` | `scheduled-transfers` |
| `LEDGER_ENTRY` | `ledger-entries` |

Example full path: `/v1/scheduled-transfers/txn:01957f3e-...`. The `entity_type` value in the JSON payload remains UPPER_SNAKE_CASE singular (`SCHEDULED_TRANSFER`) regardless of the URL form. CloudEvents `source` URIs follow the same convention — see `codex-cloudevents`.

## Scope

- **Applies to:** entity modeling, API contracts (OpenAPI/JSON), CloudEvents payloads, database schemas, domain model documents, event documentation.
- **Bound agents:** all agents that create or review entities, APIs, events, or domain models (warrior-theseus, warrior-daedalus, warrior-kronos, warrior-apollo, warrior-hera).
- **Exceptions:** third-party integration field names that arrive in camelCase from external systems — map at the anti-corruption layer boundary; do not propagate camelCase internally.

## Examples

### Correct

```json
{
  "entity_id": "txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entity_type": "SCHEDULED_TRANSFER",
  "scheduled_date": "2026-04-30",
  "failure_reason": null,
  "created_at": "2026-04-26T10:00:00Z",
  "updated_at": "2026-04-26T10:00:00Z",
  "version": 1
}
```

CloudEvents type: `event.guardia.financial.scheduled_transfer.approved`

CloudEvents subject: `SCHEDULED_TRANSFER/txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

Domain model doc aggregate: `ScheduledTransfer`

Cross-entity reference: `"transaction_id": "txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f"`

### Incorrect

```json
{
  "entityId": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entityType": "ScheduledTransfer",
  "transaction_entity_id": "txn:...",
  "scheduledDate": "2026-04-30",
  "createdAt": "2026-04-26T10:00:00Z"
}
```

CloudEvents type (invalid): `event.guardia.financial.ScheduledTransfer.Approved`

## Automated Validation

- **Tool:** JSON Schema / OpenAPI linter with `entity_type` pattern `^[A-Z][A-Z0-9_]*$`; JSON field name pattern `^[a-z][a-z0-9_]*$`; CloudEvents type regex `^event\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`; entity_id pattern `^[a-z0-9]{2,5}:[0-9a-f-]{36}$`; lint rule blocking the `_entity_id` suffix; database migration linter (squawk) checking column name casing.
- **When:** pre-commit, CI (OpenAPI validation), PR review for domain model documents.
- **Metric:** 0 lowercase `entity_type` values in JSON payloads; 0 `_entity_id` suffixes in field names; 0 entity_id values without prefix; 0 camelCase field names in JSON schemas; 0 CloudEvents types with non-lowercase segments; 0 database columns outside snake_case.

## References

- `lex-entities` — base entity structure (entity_id, entity_type, version, timestamps)
- `lex-cloudevents` — CloudEvents type format and structure
- `lex-restful-apis` — API URL conventions (kebab-case for path segments)
- `codex-entities` — entity model reference
