# Codex: Feature Design Documents — Structure and Templates

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — templates and conventions for documents produced in the feature design cycle

## Canonical Structure

```
docs/
└── {context}/                  # Bounded Context in kebab-case
    ├── entities/
    │   └── {entity-name}.md
    ├── oas/
    │   └── openapi.yaml
    ├── events/
    │   └── events.md
    ├── agents/                 # reserved
    └── metrics/                # reserved
```

### Conventions

| Item | Rule |
|------|------|
| `{context}` | Bounded Context in kebab-case. e.g. `ScheduledPayments` → `scheduled-payments` |
| Files in `entities/` | kebab-case derived from PascalCase. e.g. `ScheduledTransfer` → `scheduled-transfer.md` |
| File in `oas/` | `openapi.yaml`; when multiple APIs: `openapi-{slug}.yaml` |
| File in `events/` | `events.md` |
| Language | per `language.default` in `.ahrena/.directives` |

## Templates

### 1. `entities/{entity-name}.md`

Each entity in the Bounded Context has a **dedicated file** under `docs/{context}/entities/`. Template:

````markdown
# Entity: {EntityName}

> **DDD Classification:** Entity | Aggregate Root | Value Object
> **Bounded Context:** {context}
> **entity_type:** `{snake_case}`

## Why it exists

{Describe in 2 to 4 sentences why the entity exists in the domain. Focus on the business problem it solves, not the technical schema. Example: "Represents a bank transfer ordered by an accountant for execution on a future date. Exists to separate intent (scheduling) from execution (processing) and to allow the mandatory supervisor approval cycle."}

## Fields

| Field | Type | Size | Required | Description |
|-------|------|------|:--------:|-------------|
| `entity_id` | UUID v7 | 36 | Yes | Unique entity identifier (lex-entities) |
| `entity_type` | string | — | Yes | Fixed value: `{snake_case}` |
| `version` | integer | — | Yes | Optimistic version |
| `created_at` | datetime (ISO 8601) | — | Yes | Created |
| `updated_at` | datetime (ISO 8601) | — | Yes | Last update |
| `discarded_at` | datetime (ISO 8601) | — | No | Soft delete (lex-entities) |
| `{business_field}` | {type} | {size} | Yes/No | {Functional description} |

> **Type:** use canonical types: `string`, `integer`, `decimal`, `boolean`, `datetime`, `date`, `enum<...>`, `UUID v7`, `Money`, `array<...>`, `object<...>`, or reference to another Entity/VO.
> **Size:** maximum length (string), precision (decimal), or `—` when not applicable.
> **Required:** Yes when the field is required to create the entity; No when optional.

## Business Rules

List numerically the business rules that govern the entity in domain language (not SQL/code).

1. **{BR-1 — short name}:** {full rule in one sentence. e.g.: "A transfer can only be scheduled for business days up to 90 days in the future."}
2. **{BR-2}:** {...}
3. **{BR-3}:** {...}

## Invariants

Invariants are conditions that **always hold** for the entity or aggregate. They differ from business rules in that they admit no exception in any state.

- **{INV-1}:** {e.g.: "`amount` is always strictly positive."}
- **{INV-2}:** {e.g.: "`status` only transitions through the states defined in the diagram."}
- **{INV-3}:** {e.g.: "An `executed` transfer can never go back to `requested`."}

## Relationships

| Relation | Cardinality | Type | Target Entity | Note |
|----------|-------------|------|---------------|------|
| owns | 1..N | composition | `{OtherEntity}` | {e.g.: "ScheduledTransfer owns 1..N TransferApproval"} |
| references | N..1 | reference | `{OtherEntity}` | {e.g.: "References Account by entity_id; does not compose."} |

> Use `composition` when the target entity only exists via the root; `reference` when the target has an independent lifecycle.

## Errors

Errors emitted by use cases that touch this entity. Each error MUST follow `lex-error-handling` (code, reason, message).

| Code | Reason | Message | When it occurs |
|------|--------|---------|----------------|
| `ERR400_INVALID_PARAMETER` | `INVALID_SCHEDULED_DATE` | "scheduled_date must be a future business day" | {BR-1 violated} |
| `ERR409_CONFLICT` | `INVALID_STATE_TRANSITION` | "transfer cannot move from {from} to {to}" | Invalid transition attempt |

## Catalog

| entity_type | event_name | full type | Publisher | Consumers |
|-------------|------------|-----------|-----------|-----------|
| `scheduled_transfer` | `requested` | `event.guardia.platform.scheduled_transfer.requested` | ScheduledPayments | Approval, Audit |
| `scheduled_transfer` | `approved` | `event.guardia.platform.scheduled_transfer.approved` | Approval | ScheduledPayments, Audit |
| `scheduled_transfer` | `executed` | `event.guardia.platform.scheduled_transfer.executed` | BankingIntegration | ScheduledPayments, Ledger |

---

## {EntityNameInPascalCase}

> `entity_type`: `{snake_case}`

### Lifecycle

```mermaid
stateDiagram-v2
    [*] --> requested
    requested --> approved: ApproveScheduledTransfer
    requested --> cancelled: CancelScheduledTransfer
    approved --> executed: scheduler trigger
    approved --> failed: execution error
    approved --> cancelled: CancelScheduledTransfer
    failed --> [*]
    executed --> [*]
    cancelled --> [*]
```

### Events

#### `event.guardia.{module}.{entity_type}.requested`

> Emitted when the user creates the entity.

```json
{
  "specversion": "1.0",
  "id": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "source": "/guardia/platform/scheduled-payments",
  "type": "event.guardia.platform.scheduled_transfer.requested",
  "subject": "scheduled_transfer/{entity_id}",
  "time": "2026-04-26T10:00:00Z",
  "datacontenttype": "application/json",
  "idempotencykey": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "data": {
    "entity_id": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
    "entity_type": "scheduled_transfer",
    "version": 1,
    "created_at": "2026-04-26T10:00:00Z",
    "updated_at": "2026-04-26T10:00:00Z",
    "scheduled_date": "2026-04-30",
    "amount": 100000,
    "currency": "BRL",
    "source_account_id": "...",
    "target_account_id": "..."
  }
}
```

| `data` field | Type | Required | Description |
|--------------|------|:--------:|-------------|
| `entity_id` | UUID v7 | Yes | Entity identifier |
| `entity_type` | string | Yes | Always `{snake_case}` |
| `scheduled_date` | date | Yes | Scheduled execution date |
| `amount` | integer (cents) | Yes | Value in the currency's smallest unit |
| `currency` | string (ISO 4217) | Yes | Currency code |

**Idempotency:** `idempotencykey` equal to the `entity_id` of the originating request.
**Trigger:** Use Case `RequestScheduledTransfer`.

---

#### `event.guardia.{module}.{entity_type}.approved`

> Emitted when supervisor approves.

```json
{ ... full payload ... }
```

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|

**Trigger:** Use Case `ApproveScheduledTransfer`.

---

(repeat for each event of the entity)

---

## {OtherEntity}

(repeats the structure: lifecycle → events with payload)

## Cross-References

The three document types reference each other:

| From → To | Reference |
|-----------|-----------|
| `entities/{e}.md` → `events/events.md` | Lists the events emitted by the entity in *References* |
| `entities/{e}.md` → `oas/openapi.yaml` | Lists the REST endpoints that expose the entity |
| `events/events.md` → `entities/` | Each entity section in events.md references the entity file |
| `oas/openapi.yaml` → `entities/` | Schemas mirror the entity field catalog |

Cross-consistency is verified by `warrior-prometheus` at the end of the cycle (Phase 4 — Consistency Verification).

## Restrictions

- **Do not invert the hierarchy:** always `docs/{context}/{category}/`. Category as the top level (`docs/entities/{context}/...`) is FORBIDDEN.
- **Do not duplicate entity field in event payload:** the payload references the entity catalog; only fields relevant to the event are reproduced.
- **Do not create a single "domain" file:** the domain model is distributed across `entities/` (tables and rules), `events/` (lifecycle) and `oas/` (exposed contract). The monolithic `domain-model.md` is deprecated.
- **Do not use configurable paths:** `paths.domain`, `paths.oas`, `paths.events` were removed from `.ahrena/.directives`. The structure is fixed and codified in this Lexis/Codex.
