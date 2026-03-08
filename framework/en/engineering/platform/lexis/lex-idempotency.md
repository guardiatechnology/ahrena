# Lexis: Idempotency for State-Modifying Operations

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — APIs and events

## Purpose

Ensure that operations that modify state (APIs and events) on the Guardia platform are idempotent, preserving data consistency and reliability in environments with network failures, timeouts, or retries. Avoid duplicate transactions, state inconsistencies, and unintended side effects.

## Law

> **Operations that modify state (APIs and events) on the Guardia platform MUST be idempotent per the Hub Idempotency specification; endpoints that modify state (POST, PATCH, etc.) MUST require and validate the Idempotency-Key header; published events MUST include idempotencykey and consumers MUST register and deduplicate by key and hash.**

## Scope

- **Applies to:** HTTP mutation endpoints (POST, PATCH, PUT) and event publication/consumption on the Guardia platform.
- **Bound agents:** all API implementers and event processors.
- **Exceptions:** None for state-modifying operations; purely read-only operations (GET, query events) are not in scope.

## Consequences of Violation

1. **Duplication:** transactions or effects applied more than once.
2. **Inconsistency:** divergent state between consumers and providers.
3. **Remediation:** implement idempotency per spec and reprocess or correct affected data.

## Examples

### Correct

POST endpoint with mandatory Idempotency-Key; return 400 when missing; 409 when same key with different payload; event with idempotencykey in payload; consumer ignores already-processed event and returns ACK.

### Incorrect

Mutation endpoint without Idempotency-Key requirement; event without idempotencykey; consumer re-executing logic for the same key and hash.

## Automated Validation

- **Tool:** contract (OpenAPI) and code review; retry tests with same key.
- **When:** PR review and integration tests.
- **Metric:** 0 mutation endpoints without Idempotency-Key; 0 events without idempotencykey when the spec applies.

## References

- codex-idempotency (engineering/platform) (engineering/platform)
- RFC 9562 (UUID); Draft RFC Idempotency-Key Header
