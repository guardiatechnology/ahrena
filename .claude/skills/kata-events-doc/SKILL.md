---
name: kata-events-doc
description: "CloudEvents Documentation. Guardia platform — CloudEvents documentation for a feature or module"
---

# Kata: CloudEvents Documentation

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Guardia platform — CloudEvents documentation for a feature or module

## Workflow

```
Progress:
- [ ] 1. Read directives and context
- [ ] 2. Consult Lexis and Codex CloudEvents
- [ ] 3. Identify event types and payloads
- [ ] 4. Document each event (type, source, subject, data, idempotencykey)
- [ ] 5. Produce events.md content in the canonical structure
- [ ] 6. Final validation
```

### Step 1: Read Directives and Context

1. Read `.ahrena/.directives` to obtain `language.default`. The destination is fixed: `docs/{context}/events/events.md` per `lex-feature-design-docs`. Confirm with the user the Bounded Context name in PascalCase and the CloudEvents `{module}` segment
2. Load existing entities at `docs/{context}/entities/` to align payloads and lifecycle
3. Confirm the feature/module context (entities, operations that emit events). If insufficient, ask the user (which events? created/updated/deleted? entities involved?) and wait for answers
4. Check whether `docs/{context}/events/events.md` already exists to update instead of creating new

### Step 2: Consult Lexis and Codex CloudEvents

1. Consult **lex-directives** (required)
2. Consult **lex-cloudevents** — events MUST follow CloudEvents (structure, required properties, idempotencykey, JSON, size < 12KB)
3. Consult **codex-cloudevents** — event structure (id, source, specversion, type, time, datacontenttype, subject, idempotencykey, data); type format `event.guardia.{domain}.{entity_name}.{event_name}`; `data` shape per codex-entities
4. Consult **lex-entities** and **codex-entities** — entity fields in `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitted)
5. Consult **lex-idempotency** and **codex-idempotency** — idempotencykey required; consumers MUST deduplicate

### Step 3: Identify Event Types and Payloads

1. List **event types** in format `event.guardia.{domain}.{entity_name}.{event_name}` (e.g., `event.guardia.financial.record.created`, `event.guardia.financial.scheduled_transfer.cancelled`)
2. For each type, define: **source** (base URI + entity_type + entity_id when applicable), **subject** (`{entity_type}/{entity_id}`), **data** (fields per codex-entities; no history)
3. Ensure each event has **idempotencykey** documented and the event size is under 12KB
4. Map entities referenced in `data` to required fields from codex-entities

### Step 4: Document Each Event (type, source, subject, data, idempotencykey)

For each cataloged event, document:

1. **type** — full type name (event.guardia.{domain}.{entity_name}.{event_name})
2. **Description** — when the event is emitted (e.g., after creation of a scheduled transfer)
3. **source** — origin URI pattern (per codex-cloudevents)
4. **subject** — format `{entity_type}/{entity_id}`
5. **idempotencykey** — required; consumers MUST register and deduplicate by key and hash
6. **data** — payload structure (entity_id, entity_type, and other fields per codex-entities); state that history MUST be omitted
7. **Example** (optional) — JSON snippet of the event per codex-cloudevents

### Step 5: Produce `events.md` Content in the Canonical Structure

Structure the content per the `codex-feature-design-docs` template:

1. **Header** with the Bounded Context and the `{module}` segment
2. **Overview** in 2-4 sentences
3. **Catalog** — table `entity_type | event_name | full type | Publisher | Consumers`
4. **One section per entity that emits events**:
   - **Lifecycle** subsection with a `mermaid` `stateDiagram-v2` block covering all states and transitions
   - **Events** subsection: for each event, a JSON block with the full CloudEvents payload (`specversion`, `id`, `source`, `type`, `subject`, `time`, `datacontenttype`, `idempotencykey`, `data`), a `Field | Type | Required | Description` table for `data`, and final lines **Idempotency** + **Trigger** (Use Case)
5. **References** to `lex-cloudevents`, `codex-cloudevents`, `lex-entity-naming`, `lex-idempotency`, and the files at `docs/{context}/entities/`

Persistence: invoke **`kata-feature-design-docs`** with `Bounded Context`, `Category` = `events`, `Content` = generated Markdown, `Operation` = `create` or `update`. The kata writes to `docs/{context}/events/events.md`.

### Step 6: Final Validation

Before delivering the output, verify:

- [ ] All events follow lex-cloudevents (structure, cataloged type, idempotencykey, data per codex-entities)
- [ ] Type in format event.guardia.{domain}.{entity_name}.{event_name}
- [ ] data without history; required entity fields documented
- [ ] Document is complete (events table, details per type) and consistent with the Lexis
- [ ] `stateDiagram-v2` present for each entity that emits events
- [ ] Persistence delegated to `kata-feature-design-docs` with category `events` (canonical path `docs/{context}/events/events.md`)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| CloudEvents documentation | Markdown (.md) | `docs/{context}/events/events.md` (persisted via `kata-feature-design-docs`) |

## Example Execution

### Example Input

```
Module: platform. Entities: scheduled_transfer. Events: created (after POST), updated (after PATCH), cancelled (after DELETE).
```

### Example Output (summary)

File `docs/{context}/events/events.md` with:
- event.guardia.financial.scheduled_transfer.created — after creation; source, subject, idempotencykey; data with entity_id, entity_type, created_at, updated_at, version, etc.
- event.guardia.financial.scheduled_transfer.updated
- event.guardia.financial.scheduled_transfer.cancelled

Each with description, source, subject, data, and JSON example per codex-cloudevents.

## Constraints

- This Kata produces only event documentation; it does not implement publishers or consumers
- Does not change already-published documentation without justification and ADR
- Exceptions to the Lexis must be documented in an ADR
- The agent MUST escalate to a human when there is doubt about module boundaries or uncataloged event types
