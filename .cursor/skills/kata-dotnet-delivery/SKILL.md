---
name: kata-dotnet-delivery
description: ".NET Delivery. Implement, review, refactor, or diagnose .NET applications"
---

# Kata: .NET Delivery

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Implement, review, refactor, or diagnose .NET applications

## Workflow

```
Progress:
- [ ] 1. Discover the repository contract
- [ ] 2. Bound domain, risk, and boundaries
- [ ] 3. Build a reproducible baseline
- [ ] 4. Design or diagnose the smallest change
- [ ] 5. Implement or record findings
- [ ] 6. Validate quality, integration, and operations
- [ ] 7. Final validation
```

### Step 1: Discover the Repository Contract

Read instructions, `global.json`, solution/project files, central properties, packages, analyzers, CI, and local commands. Confirm SDK/TFM; do not change versions for convenience.

### Step 2: Bound Domain, Risk, and Boundaries

Identify domain language, invariants, consumers, public contracts, data, concurrency, authorization, and operational impact. Consult `codex-domain-driven-design` for domain decisions.

### Step 3: Build a Reproducible Baseline

Run repository restore/build/test and reproduce failures in `debug` mode. Record pre-existing failures separately. Add characterization protection before refactoring when needed.

### Step 4: Design or Diagnose the Smallest Change

Consult `codex-dotnet-engineering` and `codex-code-design`. List options, trade-offs, pattern `use_when`/`avoid_when`, and failure modes. Choose the smallest contract-preserving solution.

### Step 5: Implement or Record Findings

- `implement`: code and tests at the risk level.
- `refactor`: reversible steps without hidden behavior change.
- `debug`: fix only when authorized; otherwise deliver cause and evidence.
- `review`: prioritized findings with file/line, impact, and verifiable correction.

### Step 6: Validate Quality, Integration, and Operations

Run format/analyzers, build, and tests. When touched, validate negative authorization, real SQL, concurrency, migrations, idempotency, timeout, telemetry, health, containers, and rollback. For hot paths, compare throughput, bytes/op, Gen0/1/2 collections, and retained-memory baselines; review ownership of buffers and disposables.

### Step 7: Final Validation

- [ ] Reported SDK/TFM and commands belong to the repository
- [ ] `lex-clean-code` and all three `lex-dotnet-*` pass
- [ ] Build and test results are explicit
- [ ] Contracts, schema, and error semantics did not change silently
- [ ] Code remains memory-safe; `unsafe`/interop is isolated and justified
- [ ] Changed hot paths meet the allocation budget with evidence and no speculative pooling
- [ ] Overflow, invalid states, and expected outcomes have explicit representations and tests
- [ ] Residual risks, pre-existing failures, and skipped validations are declared

## Outputs

| Mode | Output |
|---|---|
| implement/refactor | Code, tests, and decision summary |
| review | Prioritized findings or explicit no-findings statement |
| debug | Reproduction, root cause, evidence, and fix if authorized |

## Execution Example

`implement`: add idempotent card authorization in ASP.NET Core with PostgreSQL. Output includes boundary validation, invariant, real-provider idempotency test, cancellation propagation, and telemetry without PAN.

## Constraints

- Do not install or migrate SDK/packages without project need.
- Do not replace relational semantics with EF Core InMemory.
- Do not automatically retry financial effects without idempotency and reconciliation.
