# Codex: .NET Engineering

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Development, data, operations, and delivery of .NET applications

## Overview

This Codex is Apollo-.NET's primary reference. It covers C#, ASP.NET Core, EF Core, testing, resilience, observability, and delivery while treating Clean Code and DDD as decision criteria rather than imposed structures.

## Context

- **Domain:** modern .NET applications and libraries
- **Audience:** Apollo-.NET, backend developers, and reviewers
- **Update:** whenever the supported SDK, target framework, analyzers, operational contracts, or architecture ADR changes
- **Observed local baseline:** SDK 10.0.400 and runtime 10.0.11 on 2026-08-14; each project declares its own `global.json`/TFM and must not inherit this version accidentally

## Content

### 1. Discovery Before Implementation

Inspect `global.json`, `*.sln`/`*.slnx`, `*.csproj`, `Directory.Build.*`, `Directory.Packages.props`, lock files, analyzers, and CI. Record the confirmed version, repository commands, and local/pipeline differences.

### 2. C# and Runtime

| Decision | Guidance |
|---|---|
| Nullability | Enable and model absence; do not spread `!` |
| Async | Async end-to-end, propagate cancellation, no sync-over-async |
| Resources | Explicit ownership; `await using` for async resources |
| Exceptions | Exceptions for exceptional failures; typed results for expected outcomes when they clarify the contract |
| LINQ | Account for deferred execution, repeated enumeration, and provider translation |
| Time/IDs | Inject `TimeProvider` and generators when determinism matters |

### 2.1. Rust-Inspired Discipline

The goal is not to simulate a borrow checker in C#, but to import properties that improve correctness:

| Property | Idiomatic .NET application |
|---|---|
| Memory safety | Stay in safe code; isolate interop; never expose pointers/lifetimes to the domain |
| Ownership | Creators dispose; DI lifetimes are explicit; rented buffers return in `finally` |
| Immutability | `record`, `readonly`, and immutable/read-only collections at domain boundaries |
| Valid states | Factories/constructors protect invariants; closed hierarchies and exhaustive pattern matching |
| Expected errors | Typed Result/union when callers decide; exceptions remain for exceptional failures |
| Arithmetic correctness | `checked`, money/domain types, and boundary/overflow tests |
| Zero-cost when proven | `Span<T>`, `Memory<T>`, structs, and pooling only with benchmarks and simple lifetimes |

#### Allocation Strategy

1. Measure with `dotnet-counters`, `dotnet-trace`, a profiler, and BenchmarkDotNet before optimizing.
2. First remove avoidable work: materialization, repeated enumeration, closures, boxing, intermediate strings, and per-item buffers.
3. Prefer streaming and caller-provided buffers on hot paths; keep ordinary APIs where allocation does not affect SLO or cost.
4. Use pooling last: it trades GC for manual ownership, memory retention, and residual-data risk.
5. Record throughput, bytes/op, Gen0/1/2, and retained memory; fewer allocations without measurable impact do not justify complexity.

### 3. Architecture, Clean Code, and DDD

Dependencies point toward stable policies; domain code does not import ASP.NET Core, EF Core, or provider SDKs. This does not require a fixed project count. Separate along real change, test, deploy, or ownership boundaries. Consult `codex-code-design` and `codex-domain-driven-design`.

### 4. ASP.NET Core

| Topic | Guidance |
|---|---|
| Pipeline | Middleware order is behavior; test auth, authorization, errors, and observability |
| Contracts | Validate at the boundary and keep domain models out of wire formats |
| DI/options | Explicit lifetimes; validate options on startup; avoid service locator |
| HTTP clients | Use `IHttpClientFactory`, timeout budget, cancellation, and dependency-specific policy |
| Health | Liveness checks process; readiness checks serving capability without cascades |
| Tests | Use `WebApplicationFactory` for real pipeline behavior where applicable |

### 5. EF Core and Consistency

- `DbContext` is short-lived, represents a unit of work, and is not thread-safe.
- Inspect SQL/translation for critical queries; avoid N+1, needless tracking, and early materialization.
- Database constraints protect persisted invariants; application validation improves feedback but does not replace them.
- Optimistic concurrency needs a token, conflict response, and deliberate retry policy.
- Local transactions do not cover HTTP/queues. Evaluate outbox/inbox and idempotent consumers for reliable publication.
- Migrations use expand/contract when versions coexist; define backup, duration, locking, rollback, and compatibility.
- A timed-out commit may have succeeded: reconcile before repeating a financial effect.

### 6. Resilience and Observability

Define a timeout budget per dependency. Retry only transient failures and idempotent operations, with bounds and jitter. Circuit breakers and bulkheads protect resources but do not fix poor contracts. Correlate logs, metrics, and traces without sensitive data or uncontrolled cardinality. Alerts point to impact/SLO and a runbook.

### 7. Testing

Choose level by risk: unit for rules, integration for adapters/providers, contract for boundaries, and few end-to-end tests for critical flows. Use the repository's xUnit/NUnit choice. Use Testcontainers or isolated infrastructure when external semantics matter. Coverage reveals gaps; it does not prove quality.

### 8. Build, Dependencies, and Delivery

| Topic | Guidance |
|---|---|
| SDK/TFM | Pin policy with `global.json`; declare supported TFMs |
| Packages | Central management when adopted; lock and audit vulnerabilities |
| Build | Relevant warnings as errors; versioned analyzers; reproducible artifact |
| Publish | Choose framework-dependent/self-contained deliberately |
| Trimming/AOT | Only after testing reflection, serialization, compatibility, and startup |
| Container | Minimal supported image, non-root user, health, graceful shutdown |
| Deploy | Promote the same artifact; compatible schema; explicit rollback/reconciliation |

### Current Decisions

| Decision | Status | Consequence |
|---|---|---|
| Version-independent reference with a recorded baseline | Confirmed | Version-dependent rules require project and official-doc verification |
| Architecture follows boundaries, not a fixed template | Confirmed | Small projects may remain simple |
| Patterns declare when to use and avoid | Ahrena v2 proposal | Apollo-.NET justifies a pattern before adding structure |

### Technical Constraints

- Do not assume the installed SDK is the repository-supported SDK.
- Do not retry non-idempotent operations or uncertain commits without reconciliation.
- Do not use `DbContext` concurrently or hide its lifetime in a singleton.
- Do not put PII, tokens, PAN, or secrets in logs/traces.
- Do not use `unsafe` in domain/application or introduce pooling/`stackalloc` without benchmarks, clear bounds, and lifetime tests.
- Do not adopt Native AOT, CQRS, Event Sourcing, or microservices without evidence and an operational plan.

## Glossary

| Term | Definition |
|---|---|
| TFM | Project Target Framework Moniker |
| Timeout budget | Total time apportioned across calls and attempts |
| Expand/contract | Staged compatible migration for coexisting versions |
| Uncertain commit | Communication failure where transaction outcome is unknown |

## References

- `lex-dotnet-runtime-safety`, `lex-dotnet-boundary-security`, `lex-dotnet-testing`
- `codex-code-design`, `codex-domain-driven-design`, `codex-test-strategy`
- `.references/TRILHA-DOTNET.md`, `.references/topicos/01-10`, and `.references/fontes/dotnet-oficial.md`
