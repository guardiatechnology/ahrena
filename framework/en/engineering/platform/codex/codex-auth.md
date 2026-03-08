# Codex: Authentication and Authorization on the Guardia Platform

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — API access

## Overview

This Codex describes the authentication and authorization models adopted by the Guardia platform to ensure security, traceability, and compliance for API access. Based on OAuth 2.0 and the AAA model (Authentication, Authorization, Accounting).

## Context

- **Domain:** authentication and authorization for HTTP APIs on the Guardia platform.
- **Target audience:** API implementers and integrators.
- **Update trigger:** when the Hub Auth specification changes.

## Content

### AAA model (Triple A)

1. **Authentication:** verification of user or system identity via credentials (passwords, certificates, tokens).
2. **Authorization:** definition of permissions for the authenticated identity based on policies and scopes.
3. **Accounting:** recording of actions (access, resource usage) for audit and accountability.

The model supports security and governance and guides authentication flows.

### OAuth 2.0

Protocol adopted as standard for authentication and authorization between systems. Tokens issued by Authorization Server; distinct flows depending on API type.

### Public APIs

- **Client Credentials** flow with **FAPI 2.0 Security Profile** extensions.
- Guarantees: granular authorization (RBAC and ABAC), operation traceability, fraud protection, mutual authentication between client and server.

### Private APIs

- OAuth 2.0 with **JWT tokens from a trusted IdP**.
- Guarantees: secure communication between internal modules, role-based access control (RBAC), network isolation (e.g. Virtual Private Cloud — VPC).

### Interoperability and compliance

- Unified approach enables interoperability across components, compatibility with regulations (LGPD, PCI DSS), and adherence to OpenID and FAPI.

## References

- [Authentication and Authorization — Guardia Hub](https://hub.guardia.finance/docs/specifications/auth/)
- FAPI 2.0 Security Profile
- RFC 2906 (AAA Authorization Requirements); RFC 6749 (OAuth 2.0 Authorization Framework)
