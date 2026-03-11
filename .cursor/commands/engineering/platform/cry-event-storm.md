---
description: "Event Storm — CloudEvents Documentation. Shortcut to document CloudEvents for a feature or module per Guardia Lexis and Codex"
---

# Cry: Event Storm — CloudEvents Documentation

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to document CloudEvents for a feature or module per Guardia Lexis and Codex

## Usage

```
/cry-event-storm <feature or module context> [source base]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature or module context` | Yes | Module name, entities involved, and operations that emit events (e.g., created, updated, cancelled) or explicit list of event types | "Platform module, scheduled_transfer entity: events created (after POST), updated (after PATCH), cancelled (after DELETE)" |
| `source base` | No | Base URI for `source` (e.g., https://tenant.guardia.finance/platform/api/v1). If omitted, the agent proposes per codex-cloudevents | `https://tenant.guardia.finance/platform/api/v1` |

## What the Command Does

1. Interprets the feature/module context and source base (if provided)
2. Assumes the role of the Kronos Warrior (Event Storm specialist) or delegates to the agent that executes **kata-events-doc**
3. The Warrior Kronos (via kata-events-doc) consults lex-directives, lex-cloudevents, codex-cloudevents, lex-entities, codex-entities, lex-idempotency, and codex-idempotency
4. Identifies event types (format event.guardia.{module}.{entity_type}.{event_name}), source, subject, data, and idempotencykey
5. Produces events Markdown document (e.g., events.md, cloudevents.md) with catalog and details per type
6. Persists in **paths.events** (`.ahrena/.directives`; default `docs/events`) and delivers summary or inline

## Prompt Template

```
Context:
- Feature/module context: {{feature or module context}}
- Source base (optional): {{source base}}

Task:
Act as the Kronos Warrior (Event Storm Specialist) and execute **kata-events-doc** iteratively (the Kata consults lex-cloudevents, codex-cloudevents, and related Lexis/Codex per its documentation). Based on the context above, ask clarifying questions when needed and refine the catalog based on answers. Produce the events documentation in paths.events.

Output format:
- Consult **paths.events** in `.ahrena/.directives` for the destination (default docs/events)
- Create the directory (paths.events) if it does not exist in the project
- Create or update the events document (e.g., events.md) in that path
- Events table (type, description, when emitted); for each event: type, source, subject, idempotencykey, data structure per codex-entities
```

## Invocation Example

**Input:**

```
/cry-event-storm "Platform module, scheduled_transfer entity: events created, updated, and cancelled"
```

**Expected output:**

Structured response from the Kronos Warrior with:
- Event type catalog (e.g., event.guardia.platform.scheduled_transfer.created, .updated, .cancelled)
- For each type: description, source, subject, idempotencykey, data structure
- Document created or updated in **paths.events** (`.ahrena/.directives`; directory created if it did not exist)

## Restrictions

- The Cry does not implement code; it only triggers event documentation
- Context must allow identifying module, entities, and events; if vague, the agent may ask for more detail
- Exceptions to the Lexis must be documented in an ADR

## Associated Kata and Warrior

- **kata-events-doc** — CloudEvents documentation (Markdown) in paths.events
- **warrior-kronos** — Event Storm specialist; executes kata-events-doc
