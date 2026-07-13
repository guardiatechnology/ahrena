# Cry: New Guardia TypeScript/Node.js SDK

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to scaffold (or bring into compliance) a Guardia TypeScript/Node.js SDK per `lex-sdk-typescript` and `codex-sdk-typescript`

## Description

This command invokes `kata-sdk-typescript-scaffold` to produce a TypeScript/Node.js SDK that consumes the Guardia REST API and conforms to `lex-sdk-typescript` from day one. The same command brings a legacy SDK into compliance when the `--from` flag points to an existing directory.

## Usage

```
/cry-new-sdk-typescript <sdk-name> <bounded-context> [--target=npm-public|npm-internal|both] [--from=<path>]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `sdk-name` | Yes | Package name following the canonical convention. | `@guardia/sdk-scheduled-payments` |
| `bounded-context` | Yes | Guardia bounded context the SDK targets. Used to locate `docs/{context}/oas/openapi.yaml`. | `scheduled-payments` |
| `--target` | No | Distribution target. Default: `npm-public`. | `--target=both` |
| `--from` | No | Path to an existing SDK to bring into compliance instead of scaffolding from scratch. | `--from=sdks/legacy-billing` |

## What the Command Does

1. Parses the inputs and validates the SDK name and bounded context.
2. Executes `kata-sdk-typescript-scaffold` step by step, asking the user for any missing input.
3. Generates the project skeleton, transport, error model, first domain module, and the changesets release flow.
4. Runs `pnpm validate` and produces the conformance report mapping each clause of `lex-sdk-typescript` to its verification artifact.
5. Surfaces the conformance report and the next-step checklist in the PR description.

## Prompt Template

```
Context:
- SDK name: {{sdk-name}}
- Bounded context: {{bounded-context}}
- Distribution target: {{target}}
- Existing SDK path (when bringing into compliance): {{from}}

Task:
Execute `kata-sdk-typescript-scaffold` end to end. Consult `lex-sdk-typescript`
and `codex-sdk-typescript` for every decision. Ask clarifying questions before
scaffolding when the bounded context lacks an OpenAPI spec at
docs/{{bounded-context}}/oas/openapi.yaml or when `--from` points to a path
that does not exist. After scaffolding, run the validation suite and produce
the conformance report.

Output:
- SDK skeleton at sdks/{{bounded-context}}/ (monorepo) or repository root
  (standalone), with src/, test/, tsconfig, tsup, biome, vitest, changesets,
  CI workflows.
- Conformance report covering the 10 clauses of `lex-sdk-typescript`.
- An initial changeset documenting the 0.1.0 public surface.
```

## Invocation Example

**Input:**

```
/cry-new-sdk-typescript @guardia/sdk-scheduled-payments scheduled-payments --target=both
```

**Expected output:**

The Kata scaffolds `sdks/scheduled-payments/`, generates types from `docs/scheduled-payments/oas/openapi.yaml`, implements the transport with `Authorization`, `Idempotency-Key`, and `X-Grd-Trace-Id`, ships the first domain module (`scheduled-transfers`), wires changesets and the release workflow for both npm public and GitHub Packages, runs `pnpm validate`, and attaches the conformance report to the resulting PR.

## Constraints

- Never publish during the scaffolding (no `npm publish`); the Cry only prepares the package and validates it locally.
- Never weaken the `tsconfig.json` baseline from `codex-sdk-typescript`.
- When the bounded context has no OpenAPI specification, pause and surface the missing artifact instead of inventing endpoints.

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Single shortcut with two required arguments. | Nine-step procedure with validation and report. |
| **Complexity** | Low (one command). | High (scaffold, transport, error model, tests, release flow). |
| **Configures agent?** | Yes (assumes the SDK author role and invokes the Kata). | Yes (defines every step). |
| **Example** | `/cry-new-sdk-typescript @guardia/sdk-x x` | Execute `kata-sdk-typescript-scaffold` with explicit inputs. |

## Associated Kata and Lexis

- **kata-sdk-typescript-scaffold** — end-to-end scaffolding procedure.
- **lex-sdk-typescript** — unbreakable laws for any Guardia TS/Node SDK.
- **codex-sdk-typescript** — reference manual.

## References

- `kata-sdk-typescript-scaffold`
- `lex-sdk-typescript`
- `codex-sdk-typescript`
- `lex-restful-headers`, `lex-idempotency`, `lex-error-handling` — contract the SDK enforces on every call.
- `codex-semantic-version` — versioning rules consumed by the release flow.
