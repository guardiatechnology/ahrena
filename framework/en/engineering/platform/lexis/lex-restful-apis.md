# Lexis: RESTful Compliance for HTTP Endpoints

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — REST APIs

## Purpose

Ensure standardized responses and behavior for HTTP endpoints on the Guardia platform, promoting interoperability, traceability, and clarity for internal and external consumers. Inconsistency in status codes, payloads, headers, pagination, or sorting breaks contracts and integrations.

## Law

> **Every HTTP endpoint on the Guardia platform MUST follow the RESTful specification rules (status codes, response payloads, headers, pagination, and sorting) defined in the Hub and referenced in the RESTful Codex, except when justified and documented in an ADR.**

## Scope

- **Applies to:** any HTTP endpoint implemented on the Guardia platform (public and internal APIs).
- **Bound agents:** all HTTP API implementers.
- **Exceptions:** only when justified and documented in an Architecture Decision Record (ADR).

## Consequences of Violation

1. **Interoperability:** consumers cannot assume standard behavior.
2. **Contract:** documentation (OAS) and implementation diverge from the spec.
3. **Remediation:** align status, payload, headers, and pagination to the spec or record an ADR.

## Examples

### Correct

Endpoint returning 200/201/204/400/401/404/409/422/429/500 per status table; payload with data/errors/pagination/debug per standard structure; headers Idempotency-Key, X-Grd-Trace-Id, etc. per spec; paginated listings with page_size, page_token, order_by, sort.

### Incorrect

Use of status outside the allowed list; success payload without data or error without errors array; missing X-Grd-Trace-Id; listing without pagination when applicable.

## Automated Validation

- **Tool:** OpenAPI contract and code review; contract tests.
- **When:** PR review and API validation.
- **Metric:** 0 endpoints outside the spec, except exceptions in ADR.

## References

- codex-restful-apis (index), codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting (engineering/platform)
