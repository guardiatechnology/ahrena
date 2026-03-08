# Codex: Guardia Platform RESTful APIs

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — REST APIs

## Overview

This Codex consolidates guidelines for building, consuming, and documenting RESTful APIs on the Guardia platform. It covers status codes, response payloads, headers, pagination, and sorting. Exceptions to the spec must be documented in an ADR.

**Hub references:** [RESTful](https://hub.guardia.finance/docs/specifications/restful/) | [Status Codes](https://hub.guardia.finance/docs/specifications/restful/http-status-code/) | [Payload](https://hub.guardia.finance/docs/specifications/restful/http-response-payloads/) | [Headers](https://hub.guardia.finance/docs/specifications/restful/http-headers/) | [Pagination](https://hub.guardia.finance/docs/specifications/restful/http-pagination/) | [Sorting](https://hub.guardia.finance/docs/specifications/restful/http-sorting/)

## Context

- **Domain:** HTTP APIs on the Guardia platform (responses, headers, pagination, sorting).
- **Target audience:** API implementers and consumers.
- **Update trigger:** when Hub RESTful specifications change.

---

## Module 1: Status Codes

Allowed status codes and usage rules. Codes used per endpoint MUST be documented in the OAS contract. Minimum standard for any Guardia RESTful API.

### 2xx — Success

| Code | Status | Methods | When to use | When not to use |
|------|--------|---------|-------------|-----------------|
| 200 | OK | GET, POST, PUT, PATCH | Successful operation with data; empty listing processed successfully | New resource created (use 201); processing pending (use 202); no content (use 204) |
| 201 | Created | POST, PUT | New resource created | Resource already existed/updated; creation not yet complete (use 202) |
| 202 | Accepted | POST, PUT, PATCH | Accepted; asynchronous processing | Result already available |
| 204 | No Content | DELETE, PUT, PATCH | Success with no body | When there is content to return |

### 3xx — Redirect

| Code | Status | When to use | When not to use |
|------|--------|-------------|-----------------|
| 301 | Moved Permanently | Resource permanently moved; route deprecation | Temporary change (use 307) |
| 304 | Not Modified | Resource unchanged (cache, If-Modified-Since/ETag) | Content changed (use 200) |
| 307 | Temporary Redirect | Resource temporarily at another URL; method and body preserved | Permanent change (use 301); never convert method to GET |

### 4xx — Client error

| Code | Status | When to use | When not to use |
|------|--------|-------------|-----------------|
| 400 | Bad Request | Malformed or invalid request | Correct data but invalid semantics (use 422) |
| 401 | Unauthorized | Authentication missing or invalid token | Authenticated without permission (use 403) |
| 402 | Payment Required | Access conditional on payment/subscription | Permission issue (use 403) |
| 403 | Forbidden | Authenticated but not authorized for resource | Not authenticated (use 401) |
| 404 | Not Found | Resource does not exist | Resource exists but access restricted (use 403) |
| 408 | Request Timeout | Client took too long to complete request | Timeout between servers (use 504) |
| 409 | Conflict | Conflict with current state (duplicate, version) | Validation error (use 400/422) |
| 422 | Unprocessable Entity | Syntactically correct, semantically invalid data | Format or missing properties (use 400) |
| 429 | Too Many Requests | Request limit exceeded | Error unrelated to rate limit |

### 5xx — Server error

| Code | Status | When to use | When not to use |
|------|--------|-------------|-----------------|
| 500 | Internal Server Error | Unexpected failure or unhandled exception | Predictable/client-handlable error |
| 501 | Not Implemented | Valid method not supported; feature not implemented | Processing failure (use 500) |
| 502 | Bad Gateway | Invalid response from another server | Error in own service (use 500) |
| 503 | Service Unavailable | Service temporarily unavailable | Service up with internal failure (use 500) |
| 504 | Gateway Timeout | No response in time from another server | Client→server timeout (use 408) |

**References:** RFC 9110; MDN.

---

## Module 2: Response Payload

Unified structure for success and error. Applies to all HTTP requests on the platform.

### Standard structure

| Property | Type | Description |
|----------|------|-------------|
| data | object \| array | Data when 2xx; object for single entity, array for list; absent in 4xx/5xx |
| pagination | object | Present only for paginated resource (2xx); structure below; absent on error |
| errors | array | Error list when 4xx/5xx; each item: code, reason, message (per codex-error-handling); absent in 2xx |
| debug | object | Only if header X-Grd-Debug: true; trace_id, correlation_id, instance, timestamp, duration, memory, query, params, internal_ip, external_ip; never sensitive data |

### Success

- `data` with entity(ies); include entity_id, external_entity_id, entity_type per codex-entities when entity.
- With pagination: `data` array + `pagination` (page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token).

### Error

- `errors`: array of { code, reason, message }; code per Error Handling spec; message developer-oriented, not end-user.

### Debug

- Include only with X-Grd-Debug: true; tracing fields (trace_id, correlation_id, instance, timestamp, duration, memory, etc.).

**References:** codex-entities, codex-error-handling; RFC 7807.

---

## Module 3: Headers

### Standard headers

| Header | Direction | Required | Description |
|--------|-----------|----------|-------------|
| Accept | Request | Optional | Accepted format (e.g. application/vnd.guardia.v1+json) |
| Accept-Language | Request | Optional | Preferred language |
| Content-Type | Request/Response | Optional | Content format |
| Content-Language | Response | Optional | Response language |
| Cache-Control | Response | Optional | Cache directives (public/private, max-age; no-store) |
| Link | Response | Optional | Navigation (pagination rel first/previous/next/last; HATEOAS) |
| Idempotency-Key | Request/Response | Required for mutations | UUID; per codex-idempotency |
| Content-Digest | Response | On idempotent responses | sha-256=&lt;hash&gt; 64 hex chars; per idempotency spec |
| Last-Modified | Response | On idempotency | Last modification date (RFC 7232) |
| Retry-After | Response | On 429 | Seconds to retry |

### Custom headers (X-Grd-*)

| Header | Direction | Required | Description |
|--------|-----------|----------|-------------|
| X-Grd-Debug | Request | Optional | true/false; enables debug object in response; validation: 400 ERR400_MISSING_OR_MALFORMED_HEADER, INVALID_DEBUG_HEADER_VALUE if invalid value; in production: scope, 10 min, 10 req/min, 1 min interval, audit |
| X-Grd-Trace-Id | Response | Required | UUID v7; on all responses; tracing across all layers |
| X-Grd-Correlation-Id | Request/Response | Optional | UUID; propagate if present in request |

**Security:** tracing headers must not contain PII/secrets; validate by tenant and rate limit; sanitize and limit count.

**References:** RFC 9110, 9111, 7232; codex-idempotency.

---

## Module 4: Pagination

### Request

| Parameter | Type | Default | Max | Rule |
|-----------|------|---------|-----|------|
| page_size | uint32 | 20 | 100 | Reject above limit with 400 ERR400_INVALID_PARAMETER (PAGE_SIZE_TOO_LARGE, etc.) |
| page_token | string | — | — | Opaque token; returned in previous calls |
| order_by | string | created_at | — | created_at, updated_at, reference_at; other value → 400 ORDER_BY_INVALID |
| sort | string | asc | — | asc, desc (case insensitive); other → 400 SORT_INVALID |

### Response

- `data`: array of current page.
- `pagination`: page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token (all present, null when not applicable).
- Headers: Cache-Control (e.g. max-age=900), Link with rel first, previous, next, last.

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

**References:** Hub Pagination; HATEOAS.

---

## Module 5: Sorting

- Sorting limited to temporal properties: created_at, updated_at, reference_at.
- Use indexes; stable ordering (secondary criterion e.g. entity_id).
- Parameters: order_by (default created_at), sort (default asc). Omission → created_at asc.
- Disallowed values for order_by or sort → 400 Bad Request (ERR400_INVALID_PARAMETER, ORDER_BY_INVALID, SORT_INVALID).
- Exception: fixed ordering by business rule may omit order_by if recorded in PDR.

**References:** Hub Sorting; OAS.

---

## General references

- [RESTful APIs — Guardia Hub](https://hub.guardia.finance/docs/specifications/restful/)
- codex-entities, codex-idempotency, codex-error-handling
- RFC 9110 (HTTP Semantics), RFC 9111 (Caching), RFC 7232 (Conditional Requests), RFC 7807 (Problem Details)
