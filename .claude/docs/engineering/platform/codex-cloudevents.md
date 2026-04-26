# Codex: CloudEvents on the Guardia Platform

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — events

## Content

### Event structure

| Property | Type | Default | Required | Description |
|----------|------|---------|----------|-------------|
| id | UUID v7 | — | Yes | Unique identifier of the event; immutable; RFC 9562. |
| source | URI | — | Yes | Origin of the event (e.g. https://&lt;tenant_id&gt;.guardia.finance/&lt;module&gt;/api/v1/&lt;entity_type&gt;/&lt;entity_id&gt;) |
| specversion | string | 1.0 | Yes | CloudEvents spec version; fixed value "1.0". |
| type | string | — | Yes | Format event.{provider}.{module}.{entity_type}.{event_name}; cataloged on the Hub. |
| time | datetime | — | Yes | Timestamp of occurrence (RFC 3339). |
| datacontenttype | string | application/json | Yes | Fixed value "application/json". |
| dataschema | URI | — | Optional | URI of JSON schema on the Hub. |
| subject | string | — | Yes | Format {entity_type}/{entity_id}. |
| idempotencykey | UUID | — | Yes | Idempotency key; per codex-idempotency. |
| data | object | — | Yes | Entity data; common fields: entity_id, entity_type, external_entity_id, created_at, updated_at, discarded_at, version, metadata. **Entity history MUST be omitted from events.** See codex-entities. |

- **type:** MUST be a type cataloged in the project event catalog (schemas).
- **dataschema:** when present, MUST point to the project JSON schema.

### Example event (JSON)

```json
{
  "id": "019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "source": "https://tenant.guardia.finance/platform/api/v1/transactions/019b9f12-0000-7000-8000-000000000001",
  "specversion": "1.0",
  "type": "event.guardia.platform.transaction.created",
  "time": "2026-03-08T12:00:00Z",
  "datacontenttype": "application/json",
  "dataschema": "https://<schema-base>/schemas/transaction.v1.json",
  "subject": "transaction/019b9f12-0000-7000-8000-000000000001",
  "idempotencykey": "019b9f12-0000-7000-8000-000000000002",
  "data": {
    "entity_id": "019b9f12-0000-7000-8000-000000000001",
    "entity_type": "transaction",
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
- Publication in distinct topics per type: pattern event.guardia.{module}.{entity_type}.{event_name}.
- Consumers MUST implement idempotency.
- Delivery order preserved for temporal and causal consistency.
- Self-describing events; validation against schema when defined.

### External events

- External events that do not follow CloudEvents MUST be mapped to this standard.
- Publication in topics with naming event.{provider}.{module}.{entity_type}.{event_name}.

### When to use

- Distributed systems exchanging events; event-based architectures; service integration; consuming and propagating external events; asynchronous messaging.

### When not to use

- Synchronous communication; large file transfer; continuous streaming; low-latency real-time communication.

### Security

- Transmission over secure channels (TLS); sensitive data encrypted or obfuscated; access controlled by authentication and authorization (per Auth spec).

### Notes

- Retry for delivery; idempotent consumers; dead letter queue for unprocessed events.
