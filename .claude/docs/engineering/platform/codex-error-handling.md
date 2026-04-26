# Codex: Error Handling on the Guardia Platform

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — error handling

## Content

### Error payload structure

All errors MUST be encapsulated in the `errors` field, which MUST be an array of objects (even with a single error). Each object MUST contain:

| Property | Type | Description |
|----------|------|-------------|
| code | string | Semantic code in UPPER_SNAKE_CASE, unique in the domain; prefix ERR + HTTP code (e.g., ERR400_, ERR409_). |
| reason | string | Semantic category for programmatic handling; MUST be listed in Known Errors on the Hub. |
| message | string | Developer-oriented description; MUST NEVER expose sensitive data or stack trace. |

### Example payload

```json
{
  "errors": [
    {
      "code": "ERR402_INSUFFICIENT_FUNDS",
      "reason": "PAYMENT_IS_REQUIRED",
      "message": "Insufficient balance for the requested operation."
    }
  ]
}
```

### General rules

- **code:** unique, UPPER_SNAKE_CASE, consistent with HTTP status.
- **reason:** indicates specific cause; multiple reason values may exist for the same code; MUST NOT contain sensitive data.
- **message:** informative for the developer; may be internationalized via Accept-Language; MUST NEVER expose sensitive internal information.
- **Documentation:** for each operation, document the possible code/reason pairs in the contract (OpenAPI) and in the project Known Errors catalog.

### Retry

- Conditions for retry MUST be documented in Known Errors.
- When applicable, include `Retry-After` header with recommended delay.
- Clients MUST apply exponential backoff base 2 when delay is not provided, up to a maximum of 4 attempts.
- After the 4th attempt, adopt circuit breaker pattern; half-open state may be tested every 60 seconds.
- Number of attempts and intervals configurable by the client, subject to platform limits.

### Creating new errors

- MUST follow the standardized structure (code, reason, message).
- MUST be registered in the project Known Errors catalog.
- New reason groups MUST be justified by new business contexts.
- **Security considerations:** avoid messages that enable enumeration (e.g., user exists/does not exist); do not include internal data or stack trace.
- **Monitoring:** ensure new errors are included in metrics and alerts per platform policy.

### Security

- Authentication errors MUST NEVER indicate whether a user exists.
- No message MUST contain stack trace or sensitive internal identifiers.

### Monitoring

- ALL errors MUST be logged for audit.
- 4xx and 5xx errors MUST be monitored continuously.
- 5xx errors MUST trigger alerts.

### When to use

This specification MUST be applied to: public and internal REST APIs; inter-service communication; partner integrations; UIs that consume platform APIs.
