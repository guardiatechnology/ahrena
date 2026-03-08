# Lexis: Base Entity Structure

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — entity model

## Purpose

Ensure that every persistent, traceable entity on the Guardia platform follows a minimum structural model, ensuring consistency across services, interoperability across domains, and adherence to security, traceability, and compliance requirements (LGPD, SOC 2, ISO 27001). Exceptions without this standard create audit gaps and break interoperability.

## Law

> **Every persistent, traceable entity on the Guardia platform MUST follow the base structure defined in the Hub Entities specification and referenced in the entities Codex (entity_id, entity_type, version, history, created_at, updated_at, discarded_at, and other required properties).**

## Scope

- **Applies to:** modeling and exposure of entities in APIs, databases, domain events, and integrations of the Guardia platform.
- **Bound agents:** all agents and implementers that create or modify entities on the platform.
- **Exceptions:** Only when justified and approved by the Steering Committee and recorded in a Product Decision Record (PDR).

## Consequences of Violation

1. **Inconsistency:** services and consumers cannot assume the minimum structure of entities.
2. **Audit:** gaps in traceability and history compromise compliance.
3. **Remediation:** entities outside the standard must be migrated or documented in a PDR before being accepted.

## Examples

### Correct

Entity with entity_id (UUID v7), entity_type, created_at, updated_at, version, and other spec properties; history omitted in temporal responses; history endpoint available when applicable.

### Incorrect

API resource or event representing a persistent entity without entity_id, without version, or without timestamps (created_at/updated_at) as per the Entities specification.

## Automated Validation

- **Tool:** design and code review against codex-entities; contract validation (OpenAPI/schema) when available.
- **When:** PR review and design of new resources.
- **Metric:** 0 persistent entities outside the base structure, except exceptions documented in a PDR.

## References

- codex-entities (engineering/platform) (engineering/platform)
- RFC 9562 (UUID v7), RFC 7386 (JSON Merge Patch), RFC 3339 (timestamps)
