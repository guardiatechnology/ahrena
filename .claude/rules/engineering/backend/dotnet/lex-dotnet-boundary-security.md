---
paths:
  - '**/*.cs'
  - '**/*.csproj'
  - '**/appsettings*.json'
---

# Lexis: Secure .NET Boundaries

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Inputs, authorization, secrets, and integrations in .NET applications

## Law

> **Every .NET boundary MUST validate input and server-side authorization, obtain secrets from secure providers, parameterize data access, and prevent logs, errors, or telemetry from exposing sensitive information.**

## Verifiable Rules

1. Authentication proves identity; authorization validates the action and resource for every protected operation.
2. Client data, claims, and headers do not replace server-side ownership lookup or policy.
3. SQL uses parameters or translatable LINQ; input concatenation into commands is forbidden.
4. User-controlled external URLs require an allowlist and SSRF mitigation.
5. Secrets do not live in code, versioned `appsettings*.json`, error messages, snapshots, or logs.
6. Logs use structured fields and redaction; tokens, PAN, CVV, passwords, and unnecessary PII are not emitted.

## Violation Consequences

1. **Block:** the change cannot ship.
2. **Response:** stop propagation, rotate exposed secrets where applicable, and trigger incident handling.
3. **Remediation:** validate at the boundary, move secrets to a provider, parameterize queries, and add a negative test.

## Examples

### Correct

```csharp
var card = await db.Cards.SingleOrDefaultAsync(
    item => item.Id == cardId && item.AccountId == subject.AccountId,
    cancellationToken);
```

### Incorrect

```csharp
logger.LogInformation("Authorization {Token} for card {Pan}", token, pan);
```

## Automated Validation

- **Tool:** secret scanning, SAST, NuGet vulnerability audit, analyzers, and authorization tests
- **Moment:** pre-commit, CI, and dependency review
- **Metric:** 0 secrets or sensitive data; 0 concatenated SQL; every changed protected operation has a denial test
