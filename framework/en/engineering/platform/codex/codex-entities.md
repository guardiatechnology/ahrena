# Codex: Guardia Platform Entity Model

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — base entity structure

## Overview

This specification defines the minimum structural model that all entities on the Guardia platform MUST follow. The goal is to ensure consistency across services, interoperability across domains, and adherence to security, traceability, and compliance requirements from the outset.

This base structure applies to any persistent, traceable object on the platform, including APIs, databases, domain events, external integrations, and other entity representation mechanisms.

By adopting this standard, every entity:

- Has a unique, global identifier;
- Is versioned with explicit change control;
- Maintains a complete, auditable history;
- Can be integrated and eventually discarded without losing traceability.

Applying this structure reduces inconsistencies, eases integrations, and removes audit gaps that could compromise compliance with norms such as **LGPD**, **SOC 2**, and **ISO 27001**.

The model also reinforces **Compliance by Design** principles, ensuring:

- Unique identification (`entity_id`);
- Temporal traceability (`created_at`, `updated_at`, `discarded_at`);
- Integrity and concurrency control (`version`);
- History preservation and reversibility (`history`);
- Integration and interoperability with external systems (`external_entity_id`, `metadata`).

## Context

- **Domain:** model of persistent, traceable entities on the Guardia platform.
- **Target audience:** implementers, architects, and AI agents that model or consume entities.
- **Update trigger:** when the Entities specification changes or when a PDR approves an exception.

## Content

### Base structure

The base structure of an entity in Guardia MUST contain the following properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| entity_id | UUID v7 | Yes | Unique identifier of the entity. |
| entity_type | string | Yes | Entity type. |
| external_entity_id | string | No | Unique identifier of the entity in an external system. |
| created_at | datetime | Yes | Entity creation date and time. |
| updated_at | datetime | Yes | Entity last update date and time. |
| discarded_at | datetime | No | Entity discard date and time. |
| metadata | JSON Object | No | Entity metadata. |
| version | integer | Yes | Entity version. |
| history | array | No | Entity version history. |

### Detailed properties

#### entity_id

- MUST implement UUID v7 per [RFC 9562](https://datatracker.ietf.org/doc/html/rfc9562#name-uuid-version-7) ensuring temporal ordering.
- MUST be unique, immutable, and system-generated.

#### entity_type

- MUST belong to a controlled list of entity types known to the system.

#### external_entity_id

- MAY be null.
- MUST have at most 36 characters.
- WHEN present, MUST be unique within `entity_type`.
- Ideal for cross-references with legacy or external systems.

#### created_at

- MUST be a datetime in UTC formatted per [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339).
- MUST be set automatically on creation.
- MUST NOT be changed after creation.

#### updated_at

- MUST be a datetime in UTC formatted per [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339).
- MUST be updated on every persistent modification.
- On creation, MUST match `created_at`.
- On discard, MUST match `discarded_at`.
- Used for concurrency control and synchronization.

#### discarded_at

- MUST be a datetime in UTC formatted per [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339).
- MAY be null.
- When set, indicates soft delete. The entity remains in the system for traceability.

#### metadata

- MUST be a JSON Object.
- Key and value MUST be strings.
- SHOULD stay within 4KB when possible and MUST NOT exceed 10KB.
- Updates MUST be done via JSON Merge Patch [RFC 7386](https://datatracker.ietf.org/doc/html/rfc7386).
- MUST NOT contain sensitive or personal data without legal provision.
- Values MAY be stored encrypted, with performance impact.

#### version

- Starts at 1 and is incremented automatically with `updated_at`.
- Is NEVER reset, even after restoring a discarded entity.
- On version conflict, the latest version is kept and the conflicting one is discarded.

#### history

- Stores snapshots of previous versions.
- Used for audit, rollback, and investigation.
- By default, stores the last 10 most recent versions for up to 365 days.
- History MUST be omitted from temporal responses (create, update, delete, get).
- MUST be omitted from domain events.
- History MUST be provided in read responses (get) when requested by the client at the endpoint `api/v1/<entity_type>/<entity_id>/history`.
- The history endpoint returns a list of up to 10 historical records for the same entity.
- Values MAY be stored encrypted, with performance impact.

### When to apply

This model MUST be adopted whenever:

- A new domain resource is modeled;
- APIs are exposed internally or externally;
- Domain events are produced;
- Data requires uniqueness, traceability, reversibility, or interoperability.

**IMPORTANT:** Exceptions MUST be justified and approved by the Steering Committee and recorded in a Product Decision Record (PDR).

## Glossary

| Term | Definition |
|------|------------|
| entity_id | Global unique identifier of the entity (UUID v7). |
| entity_type | Cataloged type of the entity in the system. |
| soft delete | Logical discard via discarded_at; entity retained for traceability. |
| history | Array of snapshots of previous versions for audit. |

## References

- [RFC 3339: Date and Time on the Internet: Timestamps](https://datatracker.ietf.org/doc/html/rfc3339)
- [RFC 7386: JSON Merge Patch](https://datatracker.ietf.org/doc/html/rfc7386)
- [RFC 9562: UUID Version 7](https://datatracker.ietf.org/doc/html/rfc9562)
