# Lexis: CloudEvents on the Guardia Platform

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — distributed systems and events

## Purpose

Ensure interoperability, traceability, and consistency in event-based communication. Events that do not follow the CloudEvents standard with required properties and idempotencykey break deduplication and integration across services.

## Law

> **Events published or consumed by the Guardia platform in distributed systems MUST follow the CloudEvents specification (structure, required properties, idempotencykey, JSON serialization, size under 12KB); external events that do not follow the standard MUST be mapped to this format before being published or processed.**

## Scope

- **Applies to:** event publication and consumption in event-based architectures on the Guardia platform; integration with external events.
- **Bound agents:** event publishers and consumers.
- **Exceptions:** None for events representing significant occurrences in the system; synchronous communication, large file transfer, and continuous streaming are not in scope.

## Consequences of Violation

1. **Interoperability:** consumers cannot validate or deduplicate events.
2. **Traceability:** lack of essential metadata compromises audit.
3. **Remediation:** map events to CloudEvents or publish to compatible topics.

## Examples

### Correct

Event with id, source, specversion, type, time, idempotencykey, subject, data; type in format event.guardia.{module}.{entity_type}.{event_name}; data with entity fields per codex-entities; JSON UTF-8 serialization; size < 12KB.

### Incorrect

Event without idempotencykey; without cataloged type; data without entity_id/entity_type when entity; size over 12KB; format other than JSON.

## Automated Validation

- **Tool:** validation against CloudEvents schema; review of publishers and consumers; `kata-events-review` invoked by `warrior-argos` during multi-axis Pull Request review (catches type-format violations, missing `idempotencykey`, payload mismatches against the entity catalog, breaking changes against the base version).
- **When:** PR review (via `cry-review-pr` → `warrior-argos` → `kata-events-review`) and event integration tests.
- **Metric:** 0 events published outside the CloudEvents standard when the spec applies.

## References

- codex-cloudevents (engineering/platform), codex-entities, codex-idempotency
- CloudEvents Specification; RFC 3339
