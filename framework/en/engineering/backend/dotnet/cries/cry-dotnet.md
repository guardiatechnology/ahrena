# Cry: .NET Work

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Single entry point for .NET implementation, review, refactoring, and debugging

## Description

Invokes Apollo-.NET and `kata-dotnet-delivery` in the requested mode, using the repository's actual technical contract.

## Usage

```
/cry-dotnet <implement|review|refactor|debug> <objective> [evidence]
```

## Parameters

| Parameter | Required | Description |
|---|:---:|---|
| `mode` | Yes | Operation to perform |
| `objective` | Yes | Feature, diff, component, or failure |
| `evidence` | No | Issue, logs, stack trace, contract, or constraints |

## What the Command Does

1. Invokes `warrior-apollo-dotnet` with the supplied context.
2. The Warrior runs `kata-dotnet-delivery` in the requested mode.
3. Returns a validated change, prioritized findings, or an evidence-backed diagnosis.

## Prompt Template

```
Context:
- Mode: {{mode}}
- Objective: {{objective}}
- Evidence: {{evidence}}

Task:
Act as `warrior-apollo-dotnet` and execute `kata-dotnet-delivery`. Discover repository SDK/TFM and commands first. Apply .NET Lexis, `codex-dotnet-engineering`, `codex-code-design`, and `codex-domain-driven-design` when domain work is involved.

Output:
- Primary result
- Checks run and results
- Residual risks or blockers
```

## Invocation Example

`/cry-dotnet implement "Add idempotent authorization" "OAS contract under docs/cards/oas"`

## Cry vs Kata

| Aspect | Cry | Kata |
|---|---|---|
| Role | Fast entry point | Complete verifiable procedure |
| Inputs | Mode, objective, evidence | Discovery, baseline, execution, validation |
| Logic | Delegates | Defines steps |

## Constraints

- The Cry does not run tools directly; it delegates through the Warrior to the Kata.
- Request a correction before proceeding with an invalid mode.

## References

- `warrior-apollo-dotnet`, `kata-dotnet-delivery`
