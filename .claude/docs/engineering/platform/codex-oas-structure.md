# Codex: Order of Operations in OpenAPI Paths

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — path structure in OpenAPI 3.x specifications

## Content

### Mandatory order of operations

In each `paths` entry in the OpenAPI specification (YAML or JSON), operations (HTTP methods) **MUST** be listed in the following order:

| Order | HTTP Method | Typical use |
|:-----:|-------------|-------------|
| 1 | POST | Resource creation |
| 2 | GET | Read (single or list) |
| 3 | PUT | Full replacement |
| 4 | PATCH | Partial update |
| 5 | DELETE | Deletion (logical or physical) |

When documenting a path (e.g. `/v1/transactions`), include only the operations that the endpoint exposes, **keeping this sequence**. Example: if the path has only POST, GET and PATCH, they must appear in that order in the YAML/JSON.

### Technical constraints

- When generating or editing an OpenAPI specification, the agent **MUST** order the operations of each path per the table above.
- Methods not used on the path may be omitted; those that are documented **MUST** follow the sequence POST → GET → PUT → PATCH → DELETE.
- The order applies to the OAS document (keys `post`, `get`, `put`, `patch`, `delete` in each path), not to the order in which paths are defined.
