# Lexis: .NET Correctness and Memory Safety

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** C# async code, nullability, and resource ownership

## Purpose

Prevent deadlocks, orphaned operations, predictable `NullReferenceException`s, resource leaks, invalid states, and needless garbage collector pressure in .NET services.

## Law

> **All production C# code MUST remain memory-safe by default, make ownership and invalid states explicit, keep nullable reference types enabled, propagate cancellation, avoid sync-over-async, and meet measured allocation budgets on hot paths.**

## Scope

- **Applies to:** production C# projects, workers, APIs, libraries, and adapters
- **Bound agents:** Apollo-.NET and every agent changing C# code
- **Exceptions:** None. Lexis admit no exceptions.

## Verifiable Rules

1. New projects use `<Nullable>enable</Nullable>`; nullability warnings are not suppressed without a locally verifiable rationale.
2. Cancelable async methods receive and propagate `CancellationToken`, including HTTP, database, queue, and delay calls.
3. `.Result`, `.Wait()`, and `.GetAwaiter().GetResult()` are forbidden in application async flows.
4. The creator of an `IDisposable`/`IAsyncDisposable` resource owns its disposal; consumers do not dispose injected resources.
5. `async void` is restricted to framework-required event handlers.
6. Domain and application code does not use `unsafe`, pointers, or unchecked memory access. Unavoidable interop is isolated in a minimal adapter with a rationale, bounds/lifetime tests, and explicit review.
7. Hot paths have an allocation budget and profiler/benchmark evidence. Per-item loops do not create collections, strings, closures, boxing, or disposable tasks without measured need.
8. `Span<T>`, `Memory<T>`, `stackalloc`, and `ArrayPool<T>` are used only for measured allocation reduction with demonstrably correct lifetimes; rented sensitive buffers are cleared before return.
9. Small immutable Value Objects may use `readonly record struct`; large or mutable structs are avoided because of copying and unclear aliasing.
10. Arithmetic where overflow changes money, versions, sequences, or limits uses `checked` or a validated domain type. Domain states are closed and handled exhaustively where the language permits.

## Violation Consequences

1. **Block:** build, analysis, or quality gate fails.
2. **Diagnosis:** identify the symbol, broken cancellation flow, or resource without ownership.
3. **Remediation:** fix the signature and propagation, replace synchronous blocking, or define lifetime.

## Examples

### Correct

```csharp
public Task<Card?> FindAsync(Guid id, CancellationToken cancellationToken) =>
    db.Cards.SingleOrDefaultAsync(card => card.Id == id, cancellationToken);
```

### Incorrect

```csharp
public Card Find(Guid id) => FindAsync(id, CancellationToken.None).Result!;
```

## Automated Validation

- **Tool:** `dotnet build`, .NET/Roslyn analyzers, and tests
- **Moment:** pre-commit and CI
- **Metric:** 0 new nullability/analyzer warnings; 0 sync-over-async; 100% of changed cancelable calls propagate the token; 0 `unsafe` in domain/application; no allocation-budget regression on changed hot paths

## References

- `.references/topicos/01-csharp-runtime-e-biblioteca-padrao.md`
- Official sources cataloged in `.references/fontes/dotnet-oficial.md`
