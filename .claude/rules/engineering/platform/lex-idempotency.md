---
paths:
  - '**/api/**'
  - '**/*api*.py'
  - '**/*router*.py'
  - '**/events/**'
---

# Lexis: Idempotency for State-Modifying Operations

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — APIs and events

## Law

> **Operations that modify state (APIs and events) on the Guardia platform MUST be idempotent per the Hub Idempotency specification; endpoints that modify state (POST, PATCH, etc.) MUST require and validate the Idempotency-Key header; published events MUST include idempotencykey and consumers MUST register and deduplicate by key and hash.**

## Examples

### Correct

POST endpoint with mandatory Idempotency-Key; return 400 when missing; 409 when same key with different payload; event with idempotencykey in payload; consumer ignores already-processed event and returns ACK.

### Incorrect

Mutation endpoint without Idempotency-Key requirement; event without idempotencykey; consumer re-executing logic for the same key and hash.

## Automated Validation

- **Tool:** contract (OpenAPI) and code review; retry tests with same key.
- **When:** PR review and integration tests.
- **Metric:** 0 mutation endpoints without Idempotency-Key; 0 events without idempotencykey when the spec applies.
