# Codex: Error Handling on the Guardia Platform

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — error handling

## Overview

This Codex describes the standard for representing, categorizing, and handling errors on the Guardia platform. It aims for consistency, clarity, and traceability in failure communication between services, API consumers, and interfaces.

## Context

- **Domain:** error payload structure, codes, retry, and security.
- **Target audience:** API implementers and developers who handle errors.
- **Update trigger:** when the Hub Error Handling specification changes or when new errors are registered.

## Content

### Error payload structure

All errors MUST be encapsulated in the `errors` field, which MUST be an array of objects (even with a single error). Each object MUST contain:

| Property | Type | Description |
|----------|------|-------------|
| code | string | Semantic code in UPPER_SNAKE_CASE, unique in the domain; prefix ERR + HTTP code (e.g., ERR400_, ERR409_). |
| reason | string | Semantic category for programmatic handling; MUST be listed in Known Errors on the Hub. |
| message | string | Developer-oriented description; MUST NEVER expose sensitive data or stack trace. |

### General rules

- **code:** unique, UPPER_SNAKE_CASE, consistent with HTTP status.
- **reason:** indicates specific cause; multiple reason values may exist for the same code; MUST NOT contain sensitive data.
- **message:** informative for the developer; may be internationalized via Accept-Language; MUST NEVER expose sensitive internal information.

### Retry

- Conditions for retry MUST be documented in Known Errors.
- When applicable, include `Retry-After` header with recommended delay.
- Clients MUST apply exponential backoff base 2 when delay is not provided, up to a maximum of 4 attempts.
- After the 4th attempt, adopt circuit breaker pattern; half-open state may be tested every 60 seconds.
- Number of attempts and intervals configurable by the client, subject to platform limits.

### Creating new errors

- MUST follow the standardized structure.
- MUST be registered in Known Errors on the Hub.
- New reason groups MUST be justified by new business contexts.

### Security

- Authentication errors MUST NEVER indicate whether a user exists.
- No message MUST contain stack trace or sensitive internal identifiers.

### Monitoring

- ALL errors MUST be logged for audit.
- 4xx and 5xx errors MUST be monitored continuously.
- 5xx errors MUST trigger alerts.

### When to use

This specification MUST be applied to: public and internal REST APIs; inter-service communication; partner integrations; UIs that consume platform APIs.

## References

- [Error Handling Specification — Guardia Hub](https://hub.guardia.finance/docs/specifications/error-handling/)
- Known Errors (Hub)
