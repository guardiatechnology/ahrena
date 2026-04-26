# Codex: HTTP Headers in RESTful APIs

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — REST APIs — headers

## Content

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
| Content-Digest | Response | On idempotent responses | sha-256=&lt;hash&gt;; MUST be SHA-256 in hexadecimal with 64 characters; request body MUST be normalized to JSON before hashing; invalid value → 400 ERR400_MISSING_OR_MALFORMED_HEADER, reason INVALID_CONTENT_DIGEST |
| Last-Modified | Response | On idempotency | Last modification date (RFC 7232) |
| Retry-After | Response | On 429 | Seconds to retry |

### Custom headers (X-Grd-*)

| Header | Direction | Required | Description |
|--------|-----------|----------|-------------|
| X-Grd-Debug | Request | Optional | Allowed values: **true** or **false** (any other value → 400 ERR400_MISSING_OR_MALFORMED_HEADER, reason INVALID_DEBUG_HEADER_VALUE); enables debug object in response; in production: restrict by scope (e.g. user/tenant), max window 10 min, 10 req/min per client, minimum 1 min interval between activations, usage audited |
| X-Grd-Trace-Id | Response | Required | UUID v7; on all responses; tracing across all layers |
| X-Grd-Correlation-Id | Request/Response | Optional | UUID; propagate if present in request |

### Security

- Tracing headers must not contain PII/secrets; validate by tenant and rate limit; sanitize and limit count.
