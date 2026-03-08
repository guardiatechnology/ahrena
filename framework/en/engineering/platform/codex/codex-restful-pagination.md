# Codex: Pagination in RESTful APIs

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — REST APIs — pagination

## Overview

Parameters, response structure, and behaviors for paginated listings on the Guardia platform. Opaque tokens, stable ordering, and standardized errors.

## Context

- **Domain:** pagination of resources in Guardia platform HTTP APIs.
- **Target audience:** API implementers and consumers.
- **Update trigger:** when the Hub pagination specification changes.

## Content

### Request

| Parameter | Type | Default | Max | Rule |
|-----------|------|---------|-----|------|
| page_size | uint32 | 20 | 100 | Reject above limit with 400 ERR400_INVALID_PARAMETER (PAGE_SIZE_TOO_LARGE, etc.) |
| page_token | string | — | — | Opaque token; returned in previous calls |
| order_by | string | created_at | — | created_at, updated_at, reference_at; other value → 400 ORDER_BY_INVALID |
| sort | string | asc | — | asc, desc (case insensitive); other → 400 SORT_INVALID |

### Response

- `data`: array of current page.
- `pagination`: page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token (all present; null when not applicable). **total_count** MAY be omitted when the cost of computing it is prohibitive (e.g. exact count on very large bases); when omitted, document in the contract.
- Headers: Cache-Control (e.g. max-age=900), Link with rel first, previous, next, last.
- **Compliance by Design:** opaque tokens and limited expiration; access logs with X-Grd-Trace-Id; no data leakage across tenants; parameters validated and rejected with standardized code/reason.

### Behaviors

- First page: no page_token, page_size=20.
- Reverse pagination support (previous_page_token, first_page_token).
- Stable, deterministic ordering.
- Opaque tokens (encrypted/signed); expiration (e.g. 10 min); log with X-Grd-Trace-Id.
- No results: 200 OK, empty list, total_count=0.

### Known errors

| Scenario | HTTP | code | reason |
|----------|------|------|--------|
| page_token invalid/expired | 400 | ERR400_INVALID_PARAMETER | PAGE_TOKEN_INVALID, PAGE_TOKEN_EXPIRED |
| page_size invalid/over limit | 400 | ERR400_INVALID_PARAMETER | PAGE_SIZE_INVALID, PAGE_SIZE_TOO_LARGE |
| order_by/sort invalid | 400 | ERR400_INVALID_PARAMETER | ORDER_BY_INVALID, SORT_INVALID |

Example error response (invalid page_token):

```json
{
  "errors": [
    {
      "code": "ERR400_INVALID_PARAMETER",
      "reason": "PAGE_TOKEN_INVALID",
      "message": "The provided pagination token is invalid or has expired."
    }
  ]
}
```

## References

- HATEOAS
- [codex-restful-apis](codex-restful-apis.md) (index); [codex-restful-sorting](codex-restful-sorting.md)
