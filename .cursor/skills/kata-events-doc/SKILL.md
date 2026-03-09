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
- [ ] 5. Produce events Markdown document
- [ ] 6. Final validation
```

### Step 1: Read Directives and Context

1. Read `.ahrena/.directives` to obtain **paths.events** (destination for events doc; default `docs/events`)
2. Confirm the feature/module context (entities, operations that emit events). If insufficient, ask the user (which events? created/updated/deleted? entities involved?) and wait for answers
3. Check whether an events document already exists in paths.events (e.g., `events.md`, `cloudevents.md`) to update or create new

### Step 2: Consult Lexis and Codex CloudEvents

1. Consult **lex-directives** (required)
2. Consult **lex-cloudevents** — events must follow CloudEvents (structure, required properties, idempotencykey, JSON, size < 12KB)
3. Consult **codex-cloudevents** — event structure (id, source, specversion, type, time, datacontenttype, subject, idempotencykey, data); type format `event.guardia.{module}.{entity_type}.{event_name}`; `data` shape per codex-entities
4. Consult **lex-entities** and **codex-entities** — entity fields in `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitted)
5. Consult **lex-idempotency** and **codex-idempotency** — idempotencykey required; consumers must deduplicate

### Step 3: Identify Event Types and Payloads

1. List **event types** in format `event.guardia.{module}.{entity_type}.{event_name}` (e.g., `event.guardia.platform.transaction.created`, `event.guardia.platform.scheduled_transfer.cancelled`)
2. For each type, define: **source** (base URI + entity_type + entity_id when applicable), **subject** (`{entity_type}/{entity_id}`), **data** (fields per codex-entities; no history)
3. Ensure each event has **idempotencykey** documented and event size is under 12KB
4. Map entities referenced in `data` to required fields from codex-entities

### Step 4: Document Each Event (type, source, subject, data, idempotencykey)

For each cataloged event, document:

1. **type** — full type name (event.guardia.{module}.{entity_type}.{event_name})
2. **Description** — when the event is emitted (e.g., after creation of scheduled transfer)
3. **source** — origin URI pattern (per codex-cloudevents)
4. **subject** — format `{entity_type}/{entity_id}`
5. **idempotencykey** — required; consumers must register and deduplicate by key and hash
6. **data** — payload structure (entity_id, entity_type, and other fields per codex-entities); state that history must be omitted
7. **Example** (optional) — JSON snippet of the event per codex-cloudevents

### Step 5: Produce Events Markdown Document

1. Obtain **paths.events** from `.ahrena/.directives`. Ensure the directory exists; create it if it does not
2. Generate or update **Markdown document** (e.g., `events.md`, `cloudevents.md`) in paths.events containing:
   - Title and summary (module/feature)
   - Events table (type, description, when emitted)
   - For each event: type, description, source, subject, idempotencykey, `data` structure, example when useful
   - Notes: JSON UTF-8 serialization, size < 12KB, idempotent consumers (per lex-idempotency)
3. If an events doc already exists in the path, **merge** the new events into the existing structure (by module or entity_type) instead of overwriting
4. Save in **paths.events**. If the user requests inline delivery, also deliver in chat

### Step 6: Final Validation

Before delivering the output, verify:

- [ ] All events follow lex-cloudevents (structure, cataloged type, idempotencykey, data per codex-entities)
- [ ] Type in format event.guardia.{module}.{entity_type}.{event_name}
- [ ] data without history; required entity fields documented
- [ ] Document is complete (events table, details per type) and consistent with the Lexis
- [ ] Document was saved to path **paths.events** (directory created if it did not exist)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| CloudEvents documentation | Markdown (.md) | Directory **paths.events** in `.ahrena/.directives` (default `docs/events`; create directory if it does not exist; create or update the file, e.g., events.md) |

## Example Execution

### Example Input

```
Module: platform. Entities: scheduled_transfer. Events: created (after POST), updated (after PATCH), cancelled (after DELETE).
```

### Example Output (summary)

File `events.md` (or `cloudevents.md`) in **paths.events** with:
- event.guardia.platform.scheduled_transfer.created — after creation; source, subject, idempotencykey; data with entity_id, entity_type, created_at, updated_at, version, etc.
- event.guardia.platform.scheduled_transfer.updated
- event.guardia.platform.scheduled_transfer.cancelled

Each with description, source, subject, data, and JSON example per codex-cloudevents.

## Restrictions

- This Kata produces only event documentation; it does not implement publishers or consumers
- Do not change already-published documentation without justification and ADR
- Exceptions to the Lexis must be documented in an ADR
- The agent must escalate to a human when there is doubt about module boundaries or uncataloged event types
