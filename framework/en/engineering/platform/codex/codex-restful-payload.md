# Codex: Response Payload in RESTful APIs

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — REST APIs — payload

## Overview

Unified structure for success and error responses in HTTP requests on the Guardia platform. Applies to all HTTP requests on the platform.

## Context

- **Domain:** response body structure (data, pagination, errors, debug).
- **Target audience:** API implementers and consumers.
- **Update trigger:** when the Hub payload specification changes.

## Content

### Standard structure

| Property | Type | Description |
|----------|------|-------------|
| data | object \| array | Data on 2xx; object for single entity, array for list; absent on 4xx/5xx |
| pagination | object | Present only for paginated resource (2xx); structure below; absent on error |
| errors | array | Error list on 4xx/5xx; each item: code, reason, message (per codex-error-handling); absent on 2xx |
| debug | object | Only if header X-Grd-Debug: true; trace_id, correlation_id, instance, timestamp, duration, memory, query, params, internal_ip, external_ip; never sensitive data |

### Success

- `data` with entity(ies); include entity_id, external_entity_id, entity_type per codex-entities when entity.
- With pagination: `data` array + `pagination` (page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token).

### Error

- `errors`: array of { code, reason, message }; code per Error Handling spec; **message** is for the **developer**, never the end user (avoid exposing to UI without handling).
- On 4xx/5xx responses, `data` and `pagination` are absent; only `errors` (and `debug` if X-Grd-Debug: true).

### Debug

- Include **only** when request header `X-Grd-Debug: true`; never in production by default.
- The `debug` object MUST contain: `trace_id`, `correlation_id`, `instance`, `timestamp`, `duration`, `memory`, `query`, `params`, `internal_ip`, `external_ip`.
- MUST NOT include sensitive data (secrets, PII, tokens).
- Example error payload with debug (when X-Grd-Debug: true):

```json
{
  "errors": [
    {
      "code": "ERR404_NOT_FOUND",
      "reason": "RESOURCE_NOT_FOUND",
      "message": "Resource not found for the given identifier."
    }
  ],
  "debug": {
    "trace_id": "019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
    "correlation_id": "019b9f12-0000-7000-8000-000000000001",
    "instance": "api-gateway-01",
    "timestamp": "2026-03-08T12:00:00Z",
    "duration": 15,
    "memory": 128,
    "query": "entity_id=abc",
    "params": {},
    "internal_ip": "10.0.1.5",
    "external_ip": "203.0.113.42"
  }
}
```

## References

- codex-entities, codex-error-handling; RFC 7807
- [codex-restful-apis](codex-restful-apis.md) (index)
