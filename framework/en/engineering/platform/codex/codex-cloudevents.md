# Codex: CloudEvents on the Guardia Platform

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — events

## Overview

This Codex describes the use of the CloudEvents specification to represent events on the Guardia platform. It covers event structure, required properties, format, when to use and when not to use, and security considerations. The shape of data in `data` follows codex-entities when the entity is persistent.

## Context

- **Domain:** events in distributed systems on the Guardia platform (publish and consume).
- **Target audience:** implementers of event publishers and consumers.
- **Update trigger:** when the Hub CloudEvents specification changes.

## Content

### Event structure

| Property | Type | Default | Required | Description |
|----------|------|---------|----------|-------------|
| id | {entity_id_prefix}:{uuid_v7} | — | Yes | Event identifier; equals the entity's `entity_id`. Prefix is 2–5 chars defined pre-development (e.g., `txn:01957f3e-...`). Immutable; RFC 9562. |
| source | URI | — | Yes | Origin of the event. Format: `https://api.guardia.technology/{context}/{entity_type}/{entity_id_prefix}:{entity_id}` |
| specversion | string | 1.0 | Yes | CloudEvents spec version; fixed value "1.0". |
| type | string | — | Yes | Format `event.{provider}.{domain}.{entity_name}.{event_name}`; all tokens lowercase snake_case; cataloged on the Hub. |
| time | datetime | — | Yes | Timestamp of occurrence (RFC 3339). |
| datacontenttype | string | application/json | Yes | Fixed value "application/json". |
| dataschema | URI | — | Optional | URI of JSON schema on the Hub. |
| subject | string | — | Yes | Format `{entity_type}/{entity_id_prefix}:{entity_id}`. `entity_type` in UPPER_SNAKE_CASE. |
| idempotencykey | UUID | — | Yes | Idempotency key; per codex-idempotency. |
| data | object | — | Yes | Entity data; common fields: entity_id, entity_type, external_entity_id, created_at, updated_at, discarded_at, version, metadata. **Entity history MUST be omitted from events.** See codex-entities. |

Property notes:
- **type:** MUST be a type cataloged in the project event catalog (schemas).
- **dataschema:** when present, MUST point to the project JSON schema.
- **data.entity_type:** MUST use UPPER_SNAKE_CASE (e.g., `TRANSACTION`, `SCHEDULED_TRANSFER`), per `lex-entity-naming`.
- **data.entity_id:** MUST use the `{entity_id_prefix}:{uuid_v7}` format.

### CloudEvents type format

The canonical format for internal Guardia events is:

```
event.{provider}.{domain}.{entity_name}.{event_name}
```

| Token | Description | Example |
|-------|-------------|---------|
| `provider` | Always `guardia` for internal events; external provider name for mapped external events | `guardia` |
| `domain` | Bounded context / domain of the emitting service | `platform`, `reconciliation`, `fiscal` |
| `entity_name` | Lowercase form of the UPPER_SNAKE_CASE `entity_type` | `TRANSACTION` → `transaction` |
| `event_name` | Past-tense verb describing what happened | `created`, `approved`, `executed`, `failed` |

The `{entity_name}` segment is the declared exception to the UPPER_SNAKE_CASE rule for `entity_type`: the CloudEvents reverse-DNS dot-notation standard requires lowercase, so `entity_name` is derived by lowercasing `entity_type`.

### entity_id_prefix

Every entity has a short prefix (2–5 lowercase alphanumeric characters) defined before development starts. The prefix is combined with a UUID v7 to form the entity's identifier:

```
{entity_id_prefix}:{uuid_v7}
```

Examples: `txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`, `rec:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

The prefix appears in `id`, `subject`, `source`, `data.entity_id`, and any cross-entity reference field in `data`.

### Example event (JSON)

```json
{
  "id": "txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "source": "https://api.guardia.technology/platform/TRANSACTION/txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "specversion": "1.0",
  "type": "event.guardia.platform.transaction.created",
  "time": "2026-03-08T12:00:00Z",
  "datacontenttype": "application/json",
  "dataschema": "https://<schema-base>/schemas/transaction.v1.json",
  "subject": "TRANSACTION/txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "idempotencykey": "019b9f12-0000-7000-8000-000000000002",
  "data": {
    "entity_id": "txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
    "entity_type": "TRANSACTION",
    "external_entity_id": "ext-123",
    "created_at": "2026-03-08T12:00:00Z",
    "updated_at": "2026-03-08T12:00:00Z",
    "discarded_at": null,
    "version": 1,
    "metadata": {}
  }
}
```

### Format and serialization

- Serialization: JSON; UTF-8 encoding.
- Timestamps: RFC 3339.
- Maximum event size: under 12KB.

### Expected behaviors

- Events immutable after publication.
- Publication in distinct topics per type: pattern `event.guardia.{domain}.{entity_name}.{event_name}` (all tokens lowercase snake_case).
- Consumers MUST implement idempotency.
- Delivery order preserved for temporal and causal consistency.
- Self-describing events; validation against schema when defined.

### External events

- External events that do not follow CloudEvents MUST be mapped to this standard.
- Publication in topics with naming `event.{provider}.{domain}.{entity_name}.{event_name}` (all tokens lowercase snake_case).

### When to use

- Distributed systems exchanging events; event-based architectures; service integration; consuming and propagating external events; asynchronous messaging.

### When not to use

- Synchronous communication; large file transfer; continuous streaming; low-latency real-time communication.

### Security

- Transmission over secure channels (TLS); sensitive data encrypted or obfuscated; access controlled by authentication and authorization (per Auth spec).

### Notes

- Retry for delivery; idempotent consumers; dead letter queue for unprocessed events.

## References

- codex-entities, codex-idempotency
- Cloud Events Specification; RFC 3339; RFC 9562
