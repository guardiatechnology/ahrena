# Lexis: Authentication and Authorization for Guardia APIs

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Guardia platform — API access

## Purpose

Ensure security, traceability, and regulatory compliance for access to Guardia platform APIs. Access without standardized authentication and authorization (OAuth 2.0, AAA model) compromises isolation, audit, and adherence to LGPD and PCI DSS.

## Law

> **Access to Guardia platform APIs MUST be controlled by authentication and authorization per the Hub Authentication and Authorization specification: OAuth 2.0 as standard; public APIs with Client Credentials and FAPI 2.0 extensions; private APIs with JWT tokens from a trusted IdP and role-based access control (RBAC).**

## Scope

- **Applies to:** all HTTP APIs on the Guardia platform (public and private).
- **Bound agents:** API implementers and consumers that authenticate.
- **Exceptions:** None for APIs exposing protected resources; documented public endpoints (e.g. health) may be excepted when justified in an ADR.

## Consequences of Violation

1. **Security:** unauthorized or untraceable access.
2. **Compliance:** gaps in LGPD, PCI DSS, and audit.
3. **Remediation:** implement OAuth 2.0 and AAA per spec; review access.

## Examples

### Correct

Public API: Client Credentials, FAPI 2.0, RBAC/ABAC, traceability; private API: JWT from trusted IdP, RBAC, isolation (e.g. VPC).

### Incorrect

API without authentication mechanism; use of API keys without OAuth 2.0 when spec requires it; private APIs without JWT or without RBAC.

## Automated Validation

- **Tool:** design and code review; authentication and authorization tests.
- **When:** PR review and security audit.
- **Metric:** 0 protected APIs without compliance with Auth spec.

## References

- codex-auth (engineering/platform) (engineering/platform)
- RFC 6749 (OAuth 2.0); FAPI 2.0 Security Profile
