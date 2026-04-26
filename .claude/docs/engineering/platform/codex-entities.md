# Codex: Guardia Platform Entity Model

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — base entity structure

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
