# Codex: HTTP Status Codes in RESTful APIs

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — REST APIs — status codes

## Content

### 2xx — Success

| Code | Status | Methods | When to use | When not to use |
|------|--------|---------|-------------|-----------------|
| 200 | OK | GET, POST, PUT, PATCH | Successful operation with data; empty listing processed successfully | New resource created (use 201); processing pending (use 202); no content (use 204) |
| 201 | Created | POST, PUT | New resource created | Resource already existed/updated; creation not yet complete (use 202) |
| 202 | Accepted | POST, PUT, PATCH | Accepted; asynchronous processing | Result already available |
| 204 | No Content | DELETE, PUT, PATCH | Success with no body | When there is content to return |

### 3xx — Redirection

| Code | Status | When to use | When not to use |
|------|--------|-------------|-----------------|
| 301 | Moved Permanently | Resource permanently moved; route deprecation | Temporary change (use 307) |
| 304 | Not Modified | Resource unchanged (cache, If-Modified-Since/ETag) | Content changed (use 200) |
| 307 | Temporary Redirect | Resource temporarily at another URL; method and body preserved | Permanent change (use 301); never convert method to GET |

### 4xx — Client error

| Code | Status | When to use | When not to use |
|------|--------|-------------|-----------------|
| 400 | Bad Request | Malformed or invalid request | Correct data but invalid semantics (use 422) |
| 401 | Unauthorized | Authentication missing or invalid token | Authenticated but no permission (use 403) |
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
