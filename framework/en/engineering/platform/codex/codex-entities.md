# Codex: Guardia Platform Entity Model

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — base entity structure

## Overview

This Codex describes the minimum structural model that all entities on the Guardia platform must follow. It aims for consistency across services, interoperability across domains, and adherence to security, traceability, and compliance requirements (Compliance by Design). It applies to APIs, databases, domain events, and external integrations.

## Context

- **Domain:** model of persistent, traceable entities on the Guardia platform.
- **Target audience:** implementers, architects, and AI agents that model or consume entities.
- **Update trigger:** when the Hub Entities specification changes or when a PDR approves an exception.

## Content

### Mandatory base structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| entity_id | UUID v7 | Yes | Unique identifier of the entity, immutable, system-generated. RFC 9562 (temporal ordering). |
| entity_type | string | Yes | Entity type; must belong to a controlled list known to the system. |
| external_entity_id | string | No | Identifier in external system; max 36 characters; unique per entity_type when present. |
| created_at | datetime | Yes | Creation date and time in UTC (RFC 3339); set on creation; not alterable. |
| updated_at | datetime | Yes | Last update date and time in UTC; updated on each modification; on creation = created_at; on discard = discarded_at. |
| discarded_at | datetime | No | Soft delete; when set, entity is retained for traceability. |
| metadata | JSON Object | No | Keys and values string; ideal ≤ 4KB, max 10KB; updates via JSON Merge Patch (RFC 7386); must not contain sensitive data without legal provision. |
| version | integer | Yes | Starts at 1; incremented with updated_at; never reset (even after restore). Version conflict: latest wins. |
| history | array | No | Snapshots of previous versions; last 10 versions, up to 365 days; audit and rollback. Omitted from temporal responses and events; available at endpoint api/v1/<entity_type>/<entity_id>/history. |

### Principles

1. **Unique identification:** entity_id UUID v7 ensures global uniqueness and temporal ordering.
2. **Temporal traceability:** created_at, updated_at, and discarded_at enable audit and synchronization.
3. **Integrity and concurrency:** version enables concurrency control and conflict detection.
4. **History and reversibility:** history preserves latest versions for audit and rollback.
5. **Interoperability:** external_entity_id and metadata enable integration with external systems.

### When to apply

This model MUST be adopted whenever:

- A new domain resource is modeled;
- APIs are exposed internally or externally;
- Domain events are produced;
- Data requires uniqueness, traceability, reversibility, or interoperability.

Exceptions MUST be justified and approved by the Steering Committee and recorded in a PDR.

### Technical constraints

- entity_id: UUID v7 (RFC 9562).
- Timestamps: UTC, RFC 3339.
- metadata: key and value string only; update via JSON Merge Patch (RFC 7386).
- history: omitted from create/update/delete/get by default; provided only at the history endpoint.

## Glossary

| Term | Definition |
|------|------------|
| entity_id | Global unique identifier of the entity (UUID v7). |
| entity_type | Cataloged type of the entity in the system. |
| soft delete | Logical discard via discarded_at; entity retained for traceability. |
| history | Array of snapshots of previous versions for audit. |

## References

- [Entities Specification — Guardia Hub](https://hub.guardia.finance/docs/specifications/entities/)
- RFC 9562: UUID Version 7
- RFC 7386: JSON Merge Patch
- RFC 3339: Date and Time on the Internet: Timestamps
