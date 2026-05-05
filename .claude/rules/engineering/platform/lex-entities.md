---
paths:
  - "**/entities/**"
  - "**/*entity*.py"
  - "docs/**/entities/**"
---

# Lexis: Base Entity Structure

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — entity model

## Law

> **Every persistent, traceable entity on the Guardia platform MUST follow the base structure defined in the Hub Entities specification and referenced in the entities Codex (entity_id, entity_type, version, history, created_at, updated_at, discarded_at, and other required properties).**

## Examples

### Correct

Entity with entity_id (UUID v7), entity_type, created_at, updated_at, version, and other spec properties; history omitted in temporal responses; history endpoint available when applicable.

### Incorrect

API resource or event representing a persistent entity without entity_id, without version, or without timestamps (created_at/updated_at) as per the Entities specification.

## Automated Validation

- **Tool:** design and code review against codex-entities; contract validation (OpenAPI/schema) when available.
- **When:** PR review and design of new resources.
- **Metric:** 0 persistent entities outside the base structure, except exceptions documented in a PDR.
