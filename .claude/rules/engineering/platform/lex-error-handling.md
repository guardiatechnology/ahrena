---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/api/**"
  - "**/handlers/**"
---

# Lexis: Standardized Error Structure in Responses

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — error handling

## Law

> **Errors returned by the Guardia platform MUST follow the standardized structure (errors array with code, reason, and message properties); codes MUST be prefixed with ERR and the HTTP code (e.g., ERR400_); reason MUST be listed in Known Errors; retry and circuit breaker per specification; authentication errors MUST NEVER indicate whether a user exists.**

## Examples

### Correct

Payload with `errors: [{ "code": "ERR402_INSUFFICIENT_FUNDS", "reason": "PAYMENT_IS_REQUIRED", "message": "..." }]`; reason in Known Errors; 401 without indicating whether the user exists.

### Incorrect

Error without errors array; code without ERR + HTTP prefix; reason not cataloged without justification; login message distinguishing "user not found" and "wrong password".

## Automated Validation

- **Tool:** contract (OpenAPI) and code review; error tests.
- **When:** PR review and integration tests.
- **Metric:** 0 error responses outside the structure; 0 authentication messages that indicate user existence.
