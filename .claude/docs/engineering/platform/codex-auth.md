# Codex: Authentication and Authorization on the Guardia Platform

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guardia platform — API access

## Content

### AAA model (Triple A)

1. **Authentication:** verification of user or system identity via credentials (passwords, certificates, tokens).
2. **Authorization:** definition of permissions for the authenticated identity based on policies and scopes.
3. **Accounting:** recording of actions (access, resource usage) for audit and accountability.

The model supports security and governance and guides authentication flows.

### OAuth 2.0

Protocol adopted as standard for authentication and authorization between systems. Tokens issued by Authorization Server; distinct flows depending on API type.

### Public APIs

- **Definition:** APIs exposed to external systems (partners, integrations, third-party applications).
- **Client Credentials** flow (RFC 6749) with **FAPI 2.0 Security Profile** extensions.
- Guarantees: granular authorization (RBAC and ABAC), operation traceability, fraud protection, mutual authentication between client and server.

### Private APIs

- **Definition:** APIs consumed only by internal platform components (microservices, jobs, gateways).
- OAuth 2.0 with **JWT tokens from a trusted IdP (Identity Provider)**.
- Guarantees: secure communication between internal modules, role-based access control (RBAC), network isolation when applicable (e.g. **VPC — Virtual Private Cloud**).

### Interoperability and compliance

- Unified approach enables interoperability across components, compatibility with regulations (LGPD, PCI DSS), and adherence to OpenID and FAPI.
