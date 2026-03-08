# Codex: Guardia Platform RESTful APIs

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — REST APIs

## Overview

This Codex consolidates guidelines for building, consuming, and documenting RESTful APIs on the Guardia platform. Rules are organized in specific modules; each has its own artifact for detailed reference. Exceptions to the spec must be documented in an ADR.

## Context

- **Domain:** HTTP APIs on the Guardia platform (responses, headers, pagination, sorting).
- **Target audience:** API implementers and consumers.
- **Update trigger:** when Hub RESTful specifications change.

## Modules

| Module | Artifact | Content |
|--------|----------|---------|
| Status Codes | [codex-restful-status-codes](codex-restful-status-codes.md) | Allowed HTTP codes (2xx, 3xx, 4xx, 5xx) and when to use/not use |
| Response Payload | [codex-restful-payload](codex-restful-payload.md) | Structure data, pagination, errors, debug |
| Headers | [codex-restful-headers](codex-restful-headers.md) | Standard and custom headers (X-Grd-*), Content-Digest, Idempotency-Key |
| Pagination | [codex-restful-pagination](codex-restful-pagination.md) | Parameters, response, tokens, known errors |
| Sorting | [codex-restful-sorting](codex-restful-sorting.md) | order_by, sort, indexes, partitioning |

## General references

- codex-entities, codex-idempotency, codex-error-handling
- RFC 9110 (HTTP Semantics), RFC 9111 (Caching), RFC 7232 (Conditional Requests), RFC 7807 (Problem Details)
