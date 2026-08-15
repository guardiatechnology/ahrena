---
paths:
  - '**/*.cs'
  - '**/*.py'
  - '**/*.ts'
  - '**/*.tsx'
  - '**/*.js'
  - '**/*.go'
  - '**/*.rs'
---

# Lexis: Intentional and Verifiable Code

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Application code, tests, and automations maintained in the repository

## Law

> **All versioned code MUST express active behavior using domain names, contain no dead or commented-out code or comments that merely restate the implementation, and remain within the project's configured complexity limits.**

## Verifiable Rules

1. Comments explain a decision, constraint, risk, or non-obvious behavior; they do not narrate the next line.
2. Commented-out code and unused imports, parameters, variables, and private members must not be versioned.
3. Names must be searchable and reflect the bounded context language; undocumented local abbreviations are forbidden.
4. Complexity, function-size, parameter, and nesting limits must be declared in the project's analyzer configuration. Without configuration, CI adopts the stack baseline and prevents regression.
5. A complexity warning requires investigation and either protected refactoring or a recorded decision; it does not authorize mechanical extraction that reduces cohesion.

<HARD-GATE>
Subject: code change before commit or delivery
Action: block delivery when there is commented-out code, dead symbols, comments that merely restate code, or regression against configured complexity limits
Preconditions: stack analyzers ran on changed files; the diff was reviewed for names and comments
Scope: versioned application code, tests, and scripts
Counter-pretexts: short deadline, manually generated code, temporary compatibility, locally disabled lint
Exceptions: none
</HARD-GATE>

## Violation Consequences

1. **Block:** the change does not pass the quality gate.
2. **Diagnosis:** output identifies the file, rule, and exceeded limit.
3. **Remediation:** remove noise, simplify behind a protective test, or record the technical decision if the project limit must change.

## Examples

### Correct

```csharp
// The provider may confirm after a timeout; the key preserves deduplication during reconciliation.
await gateway.AuthorizeAsync(request, idempotencyKey, cancellationToken);
```

### Incorrect

```csharp
// Authorizes the payment.
await gateway.AuthorizeAsync(request, key, CancellationToken.None);
// await legacyGateway.AuthorizeAsync(request);
```

## Automated Validation

- **Tool:** native stack analyzers (for example Roslyn/.NET analyzers, Ruff, ESLint), dead-code detection, and `kata-quality-gate`
- **Moment:** pre-commit and pull request CI
- **Metric:** 0 commented-out or dead code; 0 regressions against configured limits; 0 purely narrative comments in the diff
