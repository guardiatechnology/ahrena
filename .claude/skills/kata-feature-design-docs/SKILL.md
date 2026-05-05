---
name: kata-feature-design-docs
description: "ScheduledTransfer. Guardia platform — production of entities/, oas/ and events/ documents under docs/{context}/ during the feature design cycle"
---

# Kata: Create and Update Feature Design Documents

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — production of `entities/`, `oas/` and `events/` documents under `docs/{context}/` during the feature design cycle

## Workflow

```
Progress:
- [ ] 1. Read applicable Lexis and Codex
- [ ] 2. Resolve canonical path
- [ ] 3. Ensure folder structure
- [ ] 4. Apply category template
- [ ] 5. Verify conformance
- [ ] 6. Write or update file
- [ ] 7. Update cross-references
- [ ] 8. Final validation
```

### Step 1: Read Applicable Lexis and Codex

1. Consult **`lex-feature-design-docs`** — the structure `docs/{context}/{category}/` is mandatory; categories are fixed
2. Consult **`codex-feature-design-docs`** — specific template for the category to be produced
3. For `entities/`: also consult `lex-entities`, `lex-entity-naming`, `codex-entities`
4. For `oas/`: also consult `codex-oas-structure`, `codex-restful-payload`, `codex-restful-headers`, `codex-restful-pagination`, `codex-restful-status-codes`
5. For `events/`: also consult `lex-cloudevents`, `codex-cloudevents`, `lex-idempotency`, `lex-entity-naming`

### Step 2: Resolve Canonical Path

1. Convert the Bounded Context to kebab-case:
   - `ScheduledPayments` → `scheduled-payments`
   - `BankingIntegration` → `banking-integration`
2. Compose the base directory: `docs/{context-kebab}/`
3. Compose the final path per category:
   - `entities`: `docs/{context}/entities/{entity-name-kebab}.md` (1 file per entity)
   - `oas`: `docs/{context}/oas/openapi.yaml` (or `openapi-{slug}.yaml` if multiple APIs)
   - `events`: `docs/{context}/events/events.md` (1 file per context)

### Step 3: Ensure Folder Structure

1. Check whether `docs/{context}/` exists; create if missing
2. Check whether the category subfolder exists; create if missing
3. **Do not create** subfolders for reserved categories (`agents/`, `metrics/`) without explicit instruction
4. **Do not create** categories outside the canonical set — doing so violates `lex-feature-design-docs`

### Step 4: Apply the Category Template

Load the corresponding template from `codex-feature-design-docs` and fill in:

#### Category `entities`

1. Header with **DDD Classification**: Entity, Aggregate Root or Value Object
2. **Bounded Context** and **entity_type** (snake_case) in the header
3. **Why it exists** section — 2 to 4 sentences about the business reason
4. **Fields** section — table with columns `Field | Type | Size | Required | Description`. Always include base structure fields (`entity_id`, `entity_type`, `version`, `created_at`, `updated_at`, `discarded_at`) and then business fields
5. **Business Rules** section — numbered list (BR-1, BR-2, ...) in domain language
6. **Invariants** section — always-true conditions
7. **Relationships** section — table `Relation | Cardinality | Type | Target Entity | Note`
8. **Errors** section — table with `code`, `reason`, `message`, when it occurs, per `lex-error-handling`
9. **References** section — links to `events/events.md`, `oas/openapi.yaml` and applicable Lexis

#### Category `oas`

1. Structure OpenAPI 3.x per `codex-oas-structure`
2. `info.title`, `info.version`, `info.description` pointing to the Bounded Context
3. `tags` per entity
4. `paths` ordered by resource, operations in order `POST → GET (list) → GET (item) → PATCH → DELETE`
5. `components.schemas` reusable, derived from the entities in `docs/{context}/entities/`
6. `components.parameters` for canonical pagination (`page_size`, `page_token`)
7. `components.securitySchemes` (Bearer JWT) per `lex-auth`
8. Required headers (`Idempotency-Key`, `X-Grd-Trace-Id`) declared as reusable parameters

#### Category `events`

1. Header with Bounded Context and CloudEvents `{module}` segment
2. **Overview** section
3. **Catalog** section — table `entity_type | event_name | full type | Publisher | Consumers`
4. **One section per entity** that emits events:
   - **Lifecycle** subsection with `mermaid` `stateDiagram-v2` covering all possible states and transitions
   - **Events** subsection — for each event:
     - JSON block with full payload per `codex-cloudevents` (`specversion`, `id`, `source`, `type`, `subject`, `time`, `datacontenttype`, `idempotencykey`, `data`)
     - `data` fields table: `Field | Type | Required | Description`
     - Final lines with **Idempotency** and **Trigger** (Use Case that triggers it)
5. **References** section

### Step 5: Verify Conformance

Before writing:

- [ ] Path is exactly under `docs/{context}/{category}/...`?
- [ ] Filename respects conventions (`{entity-name}.md`, `openapi.yaml`, `events.md`)?
- [ ] Category belongs to the canonical set (`entities`, `oas`, `events`)?
- [ ] Content follows the corresponding template in `codex-feature-design-docs`?
- [ ] For `entities`: all 7 mandatory sections present (DDD Classification, Why it exists, Fields, Business Rules, Invariants, Relationships, Errors, References)?
- [ ] For `entities`: Fields table includes the base structure from `lex-entities`?
- [ ] For `oas`: file is valid YAML and follows `codex-oas-structure`?
- [ ] For `events`: each entity has `stateDiagram-v2` and each event has full CloudEvents payload?
- [ ] For `events`: all types follow `event.guardia.{module}.{entity_type}.{event_name}` in snake_case (lex-entity-naming)?

### Step 6: Write or Update File

1. On **`create`**: write the file at the resolved path
2. On **`update`**:
   - Read the existing file
   - Identify changed sections (new fields, new events, new endpoints) and stable sections (descriptions, cross-references)
   - Merge preserving human comments where possible; replace canonical tables and blocks with the new versions
   - Do not silently remove a section that existed — flag the change to the user if removal is intentional
3. Do not write empty files or files with unfilled placeholders `{...}`

### Step 7: Update Cross-References

When the category affects another:

| Change | Update |
|--------|--------|
| New event from an entity | `entities/{entity}.md` (References) and `events/events.md` (catalog) |
| New field in entity | `oas/openapi.yaml` (schema) and `events/events.md` (payload if relevant) |
| New REST endpoint | `entities/{entity}.md` (References) |
| Entity rename | filename, `entity_type`, OAS schemas, `{entity_type}` segment in all CloudEvents types |

### Step 8: Final Validation

- [ ] File written to canonical path (`docs/{context}/{category}/...`)
- [ ] Conformance with `codex-feature-design-docs` template confirmed
- [ ] Cross-references updated where applicable
- [ ] Applicable Lexis (`lex-feature-design-docs`, `lex-entities`, `lex-entity-naming`, `lex-cloudevents`, `lex-idempotency`, `lex-error-handling`) respected
- [ ] Language matches `language.default` in `.ahrena/.directives`

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Entity file | Markdown | `docs/{context}/entities/{entity-name}.md` |
| OpenAPI specification | YAML | `docs/{context}/oas/openapi.yaml` |
| Events document | Markdown | `docs/{context}/events/events.md` |

## Example Execution

### Input

```
Bounded Context: ScheduledPayments
Category: entities
Operation: create
Content:
  Entity: ScheduledTransfer (Aggregate Root)
  entity_type: scheduled_transfer
  Why it exists: separates intent from execution of bank transfers with required approval
  Business fields: scheduled_date (date), amount (integer cents), currency (ISO 4217), source_account_id (UUID), target_account_id (UUID), status (enum), approver_id (UUID, nullable)
  Rules: scheduling up to 90 business days in the future; only admin approves; no execution without approval
```

### Summarized Output

File `docs/scheduled-payments/entities/scheduled-transfer.md`:

```markdown
# Entity: ScheduledTransfer

> **DDD Classification:** Aggregate Root
> **Bounded Context:** scheduled-payments
> **entity_type:** `scheduled_transfer`

## Why it exists

Represents a bank transfer ordered by an accountant for execution on a future date. Exists to separate intent (scheduling) from execution (processing) and to allow the mandatory supervisor approval cycle before any value moves.

## Fields

| Field | Type | Size | Required | Description |
|-------|------|------|:--------:|-------------|
| `entity_id` | UUID v7 | 36 | Yes | Unique identifier |
| `entity_type` | string | — | Yes | Always `scheduled_transfer` |
| `version` | integer | — | Yes | Optimistic version |
| `created_at` | datetime | — | Yes | Created |
| `updated_at` | datetime | — | Yes | Last update |
| `discarded_at` | datetime | — | No | Soft delete |
| `scheduled_date` | date | — | Yes | Scheduled date (≤ 90 business days in the future) |
| `amount` | integer | — | Yes | Value in cents |
| `currency` | string | 3 | Yes | ISO 4217 |
| `source_account_id` | UUID v7 | 36 | Yes | Source account |
| `target_account_id` | UUID v7 | 36 | Yes | Target account |
| `status` | enum<requested,approved,executed,failed,cancelled> | — | Yes | Current state |
| `approver_id` | UUID v7 | 36 | No | Supervisor who approved |

## Business Rules

1. **BR-1 — Scheduling window:** `scheduled_date` must be a business day within 90 days in the future.
2. **BR-2 — Required approval:** Transition `requested → approved` requires `approver_id` with supervisor role.
3. **BR-3 — Conditional execution:** Transition to `executed` only happens from `approved`.

## Invariants

- **INV-1:** `amount > 0`.
- **INV-2:** `status` follows exactly the transitions in the diagram in `events/events.md`.
- **INV-3:** After `executed`, the entity is immutable except for `updated_at`.

## Relationships

| Relation | Cardinality | Type | Target Entity | Note |
|----------|-------------|------|---------------|------|
| references | N..1 | reference | `Account` | source and target |
| owns | 1..N | composition | `TransferApproval` | approval trail |

## Errors

| Code | Reason | Message | When it occurs |
|------|--------|---------|----------------|
| `ERR400_INVALID_PARAMETER` | `INVALID_SCHEDULED_DATE` | "scheduled_date must be a future business day within 90 days" | BR-1 |
| `ERR403_FORBIDDEN` | `APPROVER_NOT_AUTHORIZED` | "approver does not have supervisor role" | BR-2 |
| `ERR409_CONFLICT` | `INVALID_STATE_TRANSITION` | "transfer cannot move from {from} to {to}" | INV-2 |

## Restrictions

- This Kata **does not** decide design content — it persists the document with the input already produced by the responsible warrior (Theseus, Daedalus, Kronos)
- **Never** save outside `docs/{context}/{category}/` — violates `lex-feature-design-docs`
- **Never** use configurable paths like `paths.domain`, `paths.oas`, `paths.events` — these paths no longer exist in `.ahrena/.directives`
- **Never** mix two categories in the same file (e.g., event payload inside `entities/{e}.md`)
- When `update` removes a previously existing section, **flag the user** before writing
- Document language per `language.default` in `.ahrena/.directives`
