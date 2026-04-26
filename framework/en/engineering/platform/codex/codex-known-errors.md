# Codex: Guardia Platform Known Errors

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — standardized error catalog

## Overview

This Codex catalogs the standardized errors used by the Guardia platform's APIs and events. Each error is identified by its `code` (UPPER_SNAKE_CASE with the prefix `ERR{HTTP}_`) and detailed by its possible `reason` values, with a developer-oriented message, retry eligibility, and suggested handling.

> **Important:** Every error MUST follow the structure defined in [codex-error-handling](codex-error-handling.md). New `reason` values MUST be justified and added to this catalog.

## Context

- **Domain:** catalog of errors emitted by HTTP endpoints and event consumers/processors.
- **Target audience:** API/event implementers, integrators, and clients that handle error responses.
- **Update trigger:** whenever a new `reason` is coined in a Hub specification or created in a specific endpoint.

## Content

### Catalog structure

Each catalog entry follows this pattern:

- **`reason`** — UPPER_SNAKE_CASE string, unique per `code`.
- **Message** — developer-oriented description (not exposed to the end user).
- **Retry** — retry eligibility (✅ after correction, ❌ do not retry, ⏳ with backoff).
- **Suggested handling** — steps for the client to resolve the error.

### ERR400_MISSING_OR_MALFORMED_HEADER

Required header missing or malformed.

| reason | Retry | Message | Suggested handling |
|--------|:-----:|---------|--------------------|
| `IDEMPOTENCY_KEY_REQUIRED` | ✅ after fix | The requested resource requires a valid `Idempotency-Key`. | Send the `Idempotency-Key` header formatted per [codex-idempotency](codex-idempotency.md). |
| `MALFORMED_CORRELATION_ID` | ✅ after fix | The `X-Grd-Correlation-Id` header is not properly formatted. | Send a valid UUID per [codex-restful-headers](codex-restful-headers.md). |
| `INVALID_DEBUG_HEADER_VALUE` | ✅ after fix | The `X-Grd-Debug` header accepts only `true` or `false`. | Correct the `X-Grd-Debug` header value. |
| `INVALID_CONTENT_DIGEST` | ✅ after fix | The `Content-Digest` header is invalid or does not match the payload. | Recompute SHA-256 over the normalized JSON per [codex-restful-headers](codex-restful-headers.md). |

### ERR400_INVALID_PAYLOAD

Request body with invalid format or structure. Specific codes will be added as new endpoints register `reason` values.

### ERR400_INVALID_PARAMETER

Parameters (path, query) with invalid format or value.

| reason | Retry | Message | Suggested handling |
|--------|:-----:|---------|--------------------|
| `INVALID_LEDGER_NAME_LENGTH` | ✅ after fix | Ledger name out of allowed bounds. | Adjust the name length per the endpoint contract. |
| `INVALID_LEDGER_DESCRIPTION_LENGTH` | ✅ after fix | Ledger description exceeds the limit. | Reduce the description length. |
| `INVALID_PARAMETER_FORMAT` | ✅ after fix | Body or parameter format is invalid. | Check the contract (OAS) and correct the request. |
| `INVALID_METADATA_FORMAT` | ✅ after fix | Invalid metadata. | Ensure valid JSON and the structure defined in [codex-entities](codex-entities.md). |
| `INVALID_METADATA_LENGTH` | ✅ after fix | Metadata exceeds the limit (10KB). | Reduce metadata size. |
| `INVALID_EXTERNAL_ENTITY_ID_FORMAT` | ✅ after fix | `external_entity_id` in invalid format. | Adjust per [codex-entities](codex-entities.md) (max. 36 characters). |
| `PAGE_TOKEN_INVALID` | ✅ after fix | `page_token` is invalid. | Use a token returned in a previous response; see [codex-restful-pagination](codex-restful-pagination.md). |
| `PAGE_TOKEN_EXPIRED` | ✅ after fix | `page_token` expired. | Restart pagination from `first_page_token` or the first page. |
| `PAGE_SIZE_INVALID` | ✅ after fix | `page_size` is invalid. | Send a positive integer per the contract. |
| `PAGE_SIZE_TOO_LARGE` | ✅ after fix | `page_size` above the limit (100). | Reduce `page_size` to the maximum allowed. |
| `ORDER_BY_INVALID` | ✅ after fix | `order_by` is invalid. | Use `created_at`, `updated_at`, or `reference_at`. |
| `SORT_INVALID` | ✅ after fix | `sort` is invalid. | Use `asc` or `desc` (case insensitive). |

### ERR401_UNAUTHORIZED

Missing or invalid authentication. Reserved for OAuth 2.0/JWT failures. Messages MUST NEVER indicate whether a user exists.

### ERR402_INSUFFICIENT_FUNDS

| reason | Retry | Message | Suggested handling |
|--------|:-----:|---------|--------------------|
| `PAYMENT_IS_REQUIRED` | ❌ | Insufficient balance for the requested operation. | Regularize balance/payment before retrying. |

### ERR403_FORBIDDEN

Authenticated client without authorization for the resource. Specific `reason` values per scope will be registered as needed.

### ERR404_NOT_FOUND

| reason | Retry | Message | Suggested handling |
|--------|:-----:|---------|--------------------|
| `LEDGER_NOT_FOUND` | ⏳ if the ledger is created | Specified ledger was not found. | Verify `entity_id` or create the ledger. |

### ERR405_INVALID_OPERATION

Operation not allowed in the current state of the resource. Specific `reason` values registered per domain.

### ERR408_REQUEST_TIMEOUT

Client did not complete the request within the time limit. Generally retryable after network stabilization.

### ERR409_SERVER_STATE_CONFLICT

Conflict with the current state of the resource.

| reason | Retry | Message | Suggested handling |
|--------|:-----:|---------|--------------------|
| `CONFLICTING_IDEMPOTENT_REQUEST` | ✅ after fix | Same `Idempotency-Key` with a different payload from the prior execution. | Use a new key for a new operation OR resend the original payload. |
| `EXTERNAL_ENTITY_ID_ALREADY_IN_USE` | ✅ after fix | `external_entity_id` already used by another resource. | Choose a different external identifier. |
| `LEDGER_NAME_ALREADY_IN_USE` | ✅ after fix | Ledger name already in use. | Choose a different name. |

### ERR422_BUSINESS_ERROR

Syntactically valid data but with a semantic/business-rule error. Specific `reason` values per domain.

### ERR429_RATE_LIMITED

Client exceeded the request limit. Response MUST include the `Retry-After` header.

### ERR500_INTERNAL_ERROR

Unexpected internal failure. Client MUST NOT retry immediately; apply exponential backoff and circuit breaker per [codex-error-handling](codex-error-handling.md).

### ERR501_FEATURE_NOT_IMPLEMENTED

Feature not implemented. DO NOT retry.

### ERR503_SERVICE_UNAVAILABLE

Service temporarily unavailable. Retry with backoff, honoring `Retry-After` when present.

### ERR504_GATEWAY_TIMEOUT

Upstream gateway timeout. Retry with backoff.

### Creating new `reason` values

When adding a new `reason` to the catalog:

1. Confirm the correct HTTP `code` already exists in this list; if not, open a new `ERR{HTTP}_*` section.
2. Ensure UPPER_SNAKE_CASE and uniqueness within the `code`.
3. Document the message (no sensitive data), retry eligibility, and suggested handling.
4. Register the error in the OAS contract of the endpoint that emits it.
5. Update this Codex and the **Known Errors** page in Notion.

## References

- [codex-error-handling](codex-error-handling.md) — standardized error structure
- [codex-idempotency](codex-idempotency.md) — `Idempotency-Key` and `Content-Digest`
- [codex-restful-headers](codex-restful-headers.md) — standard and custom headers
- [codex-restful-pagination](codex-restful-pagination.md) — pagination errors
- [codex-restful-status-codes](codex-restful-status-codes.md) — correct HTTP status usage
- Guardia Hub — Known Errors page (Notion)
