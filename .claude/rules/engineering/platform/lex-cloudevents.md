---
paths:
  - "**/events/**"
  - "**/*event*.py"
  - "**/*event*.ts"
---

# Lexis: CloudEvents on the Guardia Platform

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — distributed systems and events

## Law

> **Events published or consumed by the Guardia platform in distributed systems MUST follow the CloudEvents specification (structure, required properties, idempotencykey, JSON serialization, size under 12KB); external events that do not follow the standard MUST be mapped to this format before being published or processed.**

## Examples

### Correct

Event with id, source, specversion, type, time, idempotencykey, subject, data; type in format event.guardia.{module}.{entity_type}.{event_name}; data with entity fields per codex-entities; JSON UTF-8 serialization; size < 12KB.

### Incorrect

Event without idempotencykey; without cataloged type; data without entity_id/entity_type when entity; size over 12KB; format other than JSON.

## Automated Validation

- **Tool:** validation against CloudEvents schema; review of publishers and consumers.
- **When:** PR review and event integration tests.
- **Metric:** 0 events published outside the CloudEvents standard when the spec applies.
