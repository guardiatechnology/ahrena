# Cry: Event Storm — CloudEvents Discovery and Documentation

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to discover and document CloudEvents for a feature or module per Guardia Lexis and Codex

## Description

This command triggers the Kronos Warrior (Event Storm specialist) to discover and document CloudEvents for a feature or module in two phases. When the event landscape is unknown, Kronos first executes **kata-event-storm** (Discovery) to map domain events, commands, aggregates, policies, hotspots, and bounded contexts, then proceeds to **kata-events-doc** (Documentation). When events are already identified, Kronos goes directly to Documentation.

## Usage

```
/cry-event-storm <feature or module context> [source base]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature or module context` | Yes | Module name and domain description (for Discovery) or explicit list of event types (for Documentation only) | `"Platform module, scheduled transfers — unknown events"` or `"event.guardia.financial.scheduled_transfer.created, .updated, .cancelled"` |
| `source base` | No | Base URI for `source` (e.g., `https://tenant.guardia.finance/platform/api/v1`). If omitted, the agent proposes per codex-cloudevents | `https://tenant.guardia.finance/platform/api/v1` |

## What the Command Does

1. Assumes the role of the Kronos Warrior and **determines the entry point**:
   - Context describes a domain without known events → **Phase 1: Discovery** (kata-event-storm) then **Phase 2: Documentation** (kata-events-doc)
   - Context provides an explicit list of event types → **Phase 2: Documentation only** (kata-events-doc)
2. **Phase 1 — Discovery** (when applicable): executes kata-event-storm iteratively — maps domain events (timeline), commands, actors, aggregates, policies, external systems, read models, hotspots, and bounded contexts; produces CloudEvents catalog; presents it to the user for confirmation; resolves P1 hotspots before advancing
3. **Phase 2 — Documentation**: executes kata-events-doc — documents event structure, payload (data), idempotency; generates or updates the formal events document in **`docs/{context}/events/`**
4. Persists both artifacts (discovery document when Phase 1 ran; events document always) in **`docs/{context}/events/`**; creates the directory if it does not exist

## Prompt Template

```
Context:
- Feature/module context: {{feature or module context}}
- Source base (optional): {{source base}}

Task:
Act as the Kronos Warrior (Event Storm Specialist) and determine the entry point:
- If the event landscape is unknown or the domain has not been mapped →
  execute kata-event-storm first (Phase 1 — Discovery), then kata-events-doc
  (Phase 2 — Documentation).
- If an explicit list of event types is provided → execute kata-events-doc
  directly (Phase 2 — Documentation only).

Work iteratively: ask clarifying questions when needed and wait for answers
before advancing. Do not proceed from Phase 1 to Phase 2 if P1 hotspots
remain unresolved.

Output format:
- Save in `docs/{context}/events/` per `lex-feature-design-docs`
- Create the directory if it does not exist
- Phase 1 (when executed): save event storm discovery document (e.g., event-storm-{module}.md)
- Phase 2: create or update the formal events document (events.md)
- Confirm paths of all persisted artifacts
```

## Invocation Examples

**Scenario A — Unknown event landscape (Phase 1 → Phase 2):**

```
/cry-event-storm "Platform module, scheduled transfers — accountants schedule bank transfers for future execution; mandatory supervisor approval before execution"
```

Expected output:
- Kronos executes kata-event-storm: maps timeline, commands, actors, aggregates, hotspots
- Presents CloudEvents catalog for confirmation; resolves P1 hotspots
- Executes kata-events-doc and produces formal events document
- Both artifacts saved in `docs/{context}/events/`

**Scenario B — Events already known (Phase 2 only):**

```
/cry-event-storm "event.guardia.financial.scheduled_transfer.created, .updated, .cancelled"
```

Expected output:
- Kronos executes kata-events-doc directly
- Asks about source base and payload if needed
- Events document created or updated in `docs/{context}/events/`

## Constraints

- The Cry does not implement code (publishers or consumers); it only triggers discovery and documentation
- P1 hotspots identified in Phase 1 block the transition to Phase 2 — they must be resolved before documentation
- Context must be sufficient to identify the module and domain or event types; if vague, Kronos asks for clarification
- Exceptions to Lexis must be documented in an ADR

## Associated Katas and Warrior

| Artifact | Phase | Description |
|----------|-------|-------------|
| `kata-event-storm` | 1 — Discovery | Domain events, commands, aggregates, policies, bounded contexts, CloudEvents catalog |
| `kata-events-doc` | 2 — Documentation | Formal CloudEvents document (Markdown) in `docs/{context}/events/` |
| `warrior-kronos` | Orchestrator | Determines entry point and orchestrates both phases |

## References

- `warrior-kronos` — Event Storm Specialist; routes between Discovery and Documentation based on context
- `kata-event-storm` — Discovery procedure (Phase 1)
- `kata-events-doc` — Documentation procedure (Phase 2)
