# Codex: Order of Operations in OpenAPI Paths

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — path structure in OpenAPI 3.x specifications

## Overview

This Codex defines the order in which HTTP methods must appear in each path in the OpenAPI specification (OAS 3.x), for consistency and readability. Every artifact that generates or edits OAS specifications on the Guardia platform must respect this order when documenting a path's operations.

## Context

- **Domain:** Structure of paths and operations in OpenAPI 3.x specifications.
- **Target audience:** Agents and procedures that produce or maintain OAS specs (kata-api-design-oas, Warrior Daedalus).
- **Update trigger:** When the platform convention for method order changes.

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

## Glossary

| Term | Definition |
|------|------------|
| path | URL route in the OAS spec (e.g. `/v1/transactions`, `/v1/transactions/{entity_id}`) |
| operation | HTTP method (post, get, put, patch, delete) documented under a path |

## References

- codex-restful-apis — Guardia RESTful APIs index
- [OpenAPI Specification 3.x](https://spec.openapis.org/oas/v3.0.3)
