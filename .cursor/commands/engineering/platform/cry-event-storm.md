---
description: "Event Storm — CloudEvents Discovery and Documentation. Shortcut to discover and document CloudEvents for a feature or module per Guardia Lexis and Codex"
---

# Cry: Event Storm — CloudEvents Discovery and Documentation

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to discover and document CloudEvents for a feature or module per Guardia Lexis and Codex

## Description

This command invokes the Kronos Warrior (or the agent assuming its role) to execute the discovery and documentation of CloudEvents for a new feature: consult the CloudEvents Lexis and Codex and produce the **events documentation in Markdown** (kata-events-doc), in **`docs/{context}/events/`**.

## Usage

```
/cry-event-storm <feature description> [events context]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature description` | Yes | Description of domain, entities, operations, and business rules relevant to the events | "Scheduled transfers module: create, list, update, and cancel; events emitted on each state transition" |
| `events context` | No | Specific complement for events (e.g.: module, entity type, source base). If omitted, the agent infers from the feature context or asks | "Module platform, entity type scheduled_transfer" |

## What the Command Does

1. Interprets the feature description and events context (if provided)
2. Assumes the role of the Kronos Warrior (events specialist) or delegates to the agent executing kata-events-doc
3. The Kronos Warrior (or the agent in its role) consults lex-cloudevents, lex-idempotency, and the CloudEvents Codex
4. Identifies entities, state transitions, and events relevant to the feature
5. Produces events documentation in Markdown with catalog, lifecycle diagrams (Mermaid), and CloudEvents payloads
6. Delivers the artifact in **`docs/{context}/events/`**

## Prompt Template

```
Context:
- Feature description: {{feature description}}
- Events context (optional): {{events context}}

Task:
Act as the Kronos Warrior (Event Storm Specialist) and execute **kata-events-doc** (the Kata consults the CloudEvents Lexis and Codex per its documentation). Based on the feature description, ask clarifying questions when necessary (e.g.: module, entity types, state transitions, consumers) and refine the design based on the answers. Produce the events documentation in `docs/{context}/events/`. Use the provided events context or propose a suitable one.

Output format:
- Save to `docs/{context}/events/` per `lex-feature-design-docs`
- Create the directory if it does not exist in the project
- Create or update the events Markdown document at that path
- Event catalog (entity_type, event_name, full type, publishers, consumers); for each event: Mermaid lifecycle diagram, full CloudEvents payload with all `data` attribute fields, fields table
```

## Invocation Example

**Input:**

```
/cry-event-storm "Scheduled transfers module: create, update, and cancel; events emitted in requested, approved, executed, failed, cancelled" "module platform, entity scheduled_transfer"
```

**Expected output:**

Structured response from the Kronos Warrior with:
- Identified events: `event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`
- Mermaid lifecycle diagram for `scheduled_transfer`
- Full CloudEvents payload for each event (specversion, id, source, type, subject, time, idempotencykey, data)
- Documentation created or updated in `docs/{context}/events/` (directory created if it did not exist)

## Constraints

- The Cry does not implement code; it only triggers the events discovery and documentation
- The feature description must be sufficient to identify entities and state transitions; if vague, the agent may ask for clarification
- Exceptions to Lexis must be documented in an ADR; the agent may flag when a decision requires an ADR

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation with feature description | Complete procedure in multiple steps |
| **Complexity** | Low (1 command) | High (steps: directives, consult Lexis/Codex, entities, events, payloads, documentation, validation) |
| **Configures agent?** | Yes (assumes the Kronos Warrior role) | Yes (defines all discovery steps) |
| **Example** | "/cry-event-storm create/list/cancel scheduled transfers" | Execute kata-events-doc with explicit inputs |

## Associated Kata and Warrior

- **kata-events-doc** — Event discovery and production of Markdown documentation in `docs/{context}/events/`
- **warrior-kronos** — Event Storm Specialist; executes kata-events-doc

## References

- `kata-events-doc` — Procedure executed by the Kronos Warrior (the Kata consults the CloudEvents Lexis and Codex; see Kata documentation)
- `lex-feature-design-docs` — canonical structure `docs/{context}/{category}/`
