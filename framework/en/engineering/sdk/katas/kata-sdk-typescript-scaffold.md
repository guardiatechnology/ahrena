# Kata: Scaffold a Guardia TypeScript/Node.js SDK

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — SDK: end-to-end procedure to scaffold (or bring into compliance) a TypeScript/Node.js SDK that consumes the Guardia REST API, per `lex-sdk-typescript` and `codex-sdk-typescript`

## Objective

This Kata produces a TypeScript/Node.js SDK skeleton that is, on day one, conformant with `lex-sdk-typescript`: strict types, declared `exports`, transport with auth + idempotency + trace, error envelope mapping, telemetry hooks, tests, and a release flow via changesets. The same procedure applies to bringing an existing SDK into compliance (existing files are diffed against the target skeleton).

## When to Use

- When a new bounded context exposes a stable REST API and a public SDK is required.
- When an internal team needs a typed client against an existing Guardia API context.
- When `cry-new-sdk-typescript` is invoked.
- When a legacy SDK fails Gate 2 and must be brought into conformance with the Lexis.

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| SDK name | Yes | Package name, e.g., `@guardia/sdk-scheduled-payments` or `sdk-internal-billing`. |
| Bounded context | Yes | The Guardia bounded context the SDK targets, e.g., `scheduled-payments`. Used to locate `docs/{context}/oas/openapi.yaml`. |
| Distribution target | Yes | `npm-public` (`@guardia/*`), `npm-internal` (GitHub Packages), or `both`. |
| OpenAPI source | No | Path to `docs/{context}/oas/openapi.yaml`. When absent, the SDK ships without generated types and the catalog is hand-written. |
| Repository target | No | `monorepo` (default) or `standalone`. Affects CI and changesets configuration. |
| Existing SDK path | No | When run in "bring into compliance" mode, the path to the existing SDK root. |

## Workflow

```
Progress:
- [ ] 1. Clarify inputs and resolve distribution target
- [ ] 2. Initialize package skeleton
- [ ] 3. Configure tooling (tsconfig, tsup, biome, vitest)
- [ ] 4. Generate types from OpenAPI (when available)
- [ ] 5. Implement transport (auth, retry, idempotency, trace, telemetry)
- [ ] 6. Implement error model and Result helper
- [ ] 7. Implement first domain module + tests
- [ ] 8. Wire changesets and release flow
- [ ] 9. Run validation suite and produce conformance report
```

### Step 1: Clarify Inputs and Resolve Distribution Target

1. Confirm the SDK name follows the `@guardia/sdk-{context}` (public) or `@guardia-internal/sdk-{context}` (internal) convention.
2. Confirm the bounded context exists under `docs/{context}/` and locate `oas/openapi.yaml`. When missing, ask the user whether to proceed without generated types or to wait until the OpenAPI is published.
3. Resolve distribution:
   - `npm-public` → `publishConfig.access: "public"`, `provenance: true`, registry npmjs.
   - `npm-internal` → `publishConfig.registry: "https://npm.pkg.github.com"`.
   - `both` → publish-time matrix in CI; same artifact.
4. Confirm repository target (monorepo vs standalone) — affects changesets root and CI workflow location.

### Step 2: Initialize Package Skeleton

1. Create the directory tree from `codex-sdk-typescript` (`src/`, `test/`, `.changeset/`, top-level config files).
2. Write `package.json` with:
   - `name`, `version: "0.1.0"`, `type: "module"`, `engines.node: ">=20"`.
   - `exports` map with at minimum `"."` resolving to `dist/index.{js,cjs,d.ts}`.
   - `files: ["dist", "README.md", "DEPENDENCIES.md"]`.
   - `sideEffects: false`.
   - `publishConfig` per distribution target.
3. Create `DEPENDENCIES.md` listing every runtime dependency with: name, purpose, license, last audit date.
4. Create `README.md` with installation, quickstart, and a link to `codex-sdk-typescript`.

### Step 3: Configure Tooling

1. **`tsconfig.json`** — extend `@guardia/tsconfig-sdk` when it exists, otherwise inline the baseline from `codex-sdk-typescript`. Confirm `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, target `ES2022`, module `ESNext`.
2. **`tsup.config.ts`** — entry `src/index.ts`, formats `["esm", "cjs"]`, `dts: true`, `clean: true`, `treeshake: true`, `splitting: false`. Add additional entries for every sub-path declared in `exports`.
3. **`biome.json`** (or `eslint.config.js`) — enable `noExplicitAny` as error in publishable files, ban `console.*` in `src/`, ban relative imports crossing into `src/generated/` from outside transport layer.
4. **`vitest.config.ts`** — coverage thresholds at 80/80/80/80; environment `node` for transport tests, `happy-dom` only when DOM polyfills are needed.

### Step 4: Generate Types from OpenAPI

1. When `docs/{context}/oas/openapi.yaml` exists:
   ```
   pnpm dlx openapi-typescript docs/{context}/oas/openapi.yaml -o src/generated/openapi.ts
   ```
2. Add an npm script `"types:generate": "openapi-typescript ..."` to keep the command discoverable.
3. Decide commit vs gitignore for `src/generated/`. Default: commit, to simplify consumer install. Document the choice in `README.md`.
4. When OpenAPI is absent, hand-write minimal types under `src/types/` and note in `README.md` that the SDK will be regenerated when the spec lands.

### Step 5: Implement Transport

1. Create `src/transport/http.ts` with the `HttpTransport` class:
   - Reads `config.baseUrl`, `config.token` (string or async resolver), `config.fetch` (default `globalThis.fetch`).
   - Builds `Authorization: Bearer <token>`.
   - For `POST`/`PUT`/`PATCH`/`DELETE`, sets `Idempotency-Key` from caller or generates UUID v7.
   - Reads trace id from `config.tracer` (default no-op) and sets `X-Grd-Trace-Id`.
   - Wraps `fetch` with `AbortController` for timeout.
2. Create `src/transport/retry.ts`:
   - Exponential backoff with jitter on `429`, `502`, `503`, `504`, network errors.
   - Defaults: 3 retries, base 100 ms, cap 2 s.
   - Honors `Retry-After` when present.
3. Create `src/transport/telemetry.ts`:
   - `TelemetryHook` interface (`onRequest`, `onResponse`, `onError`, `onRetry`).
   - No-op default.

### Step 6: Implement Error Model and Result Helper

1. Create `src/errors.ts` with `GuardiaError` class and the canonical `GuardiaErrorCode` union (mirroring `codex-known-errors`).
2. Create `src/result.ts` with `Result<T, E>` = `Ok<T> | Err<E>` plus `ok`, `err`, `isOk`, `isErr`, `map`, `mapErr` helpers.
3. The transport translates every non-2xx response and every transport-level failure into `Err(GuardiaError)`. Public methods return `Promise<Result<T, GuardiaError>>`.
4. Expose error codes from `./errors` sub-path in `exports` so consumers can pattern-match.

### Step 7: Implement First Domain Module + Tests

1. Pick one resource from the OpenAPI (e.g., `scheduled-transfers`) and implement `src/domains/scheduled-transfers.ts` exposing the canonical CRUD methods (`create`, `list`, `get`, `update`, `delete`) per `codex-restful-payload`.
2. Wire the methods through `HttpTransport`; map request/response shapes through decoders.
3. Write **unit tests** for each method using MSW to assert:
   - The request URL, method, body, and headers (`Authorization`, `Idempotency-Key` on mutating verbs, `X-Grd-Trace-Id`).
   - Decoding of the success response.
   - Error envelope mapping for `400`, `401`, `404`, `409`, `429`, `500`, `503`.
   - Retry on `503` with backoff (use fake timers).
4. Write **integration tests** that exercise the transport against a recorded server (MSW HTTP server) and assert the public surface end-to-end.

### Step 8: Wire Changesets and Release Flow

1. Run `pnpm dlx @changesets/cli init`.
2. Configure `.changeset/config.json` with `access: "public"` (for `@guardia/*`) or `restricted` (internal), `baseBranch: "main"`, `commit: false`.
3. Add the changesets GitHub Action at `.github/workflows/release.yml`:
   - On push to `main`, run `pnpm validate`, then `changeset version` (opens a PR) or `changeset publish` (when the version PR is merged).
   - On `@guardia/*` packages, enable `--provenance` and require `id-token: write` permission.
4. Add a `.github/workflows/ci.yml` that runs on every PR: `pnpm install`, `pnpm validate`, upload coverage.

### Step 9: Validation and Conformance Report

1. Run `pnpm validate` locally:
   - `tsc --noEmit` clean.
   - `biome check` clean.
   - `vitest run` with coverage ≥ 80%.
   - `publint` clean.
   - `attw --pack .` clean (no false-CJS, no false-ESM).
2. Produce a conformance report mapping each clause of `lex-sdk-typescript` to its verification artifact:

| Clause | Verification |
|--------|--------------|
| 1. Strict TS | `tsc --noEmit` output |
| 2. `exports` map | `publint`/`attw` output |
| 3. Semver | `.changeset/` directory + CI workflow |
| 4. Canonical headers | Integration test assertions |
| 5. Error envelope | Unit tests for `400`/`401`/`409`/`500` |
| 6. Public `.d.ts` | `attw --pack .` |
| 7. Dependencies justified | `DEPENDENCIES.md` |
| 8. Tests + coverage | Vitest coverage report |
| 9. Telemetry hooks | `src/transport/telemetry.ts` + tests |
| 10. `engines.node` | `package.json` |

3. Hand the report to the PR reviewer and to `warrior-athena` for Gate 2.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| SDK skeleton | TypeScript project | `sdk-{context}/` (monorepo) or repo root (standalone) |
| Conformance report | Markdown | PR body or `docs/sdks/{context}/conformance.md` |
| Initial changeset | Markdown | `.changeset/initial.md` describing the 0.1.0 surface |

## Execution Example

### Example Input

```
SDK name: @guardia/sdk-scheduled-payments
Bounded context: scheduled-payments
Distribution: npm-public
OpenAPI: docs/scheduled-payments/oas/openapi.yaml
Repository: monorepo
```

### Example Output

```
sdks/scheduled-payments/
├── package.json          (@guardia/sdk-scheduled-payments@0.1.0, exports map, engines, provenance)
├── tsconfig.json         (strict + noUncheckedIndexedAccess)
├── tsup.config.ts        (esm + cjs + dts)
├── biome.json
├── vitest.config.ts
├── src/
│   ├── index.ts
│   ├── client.ts
│   ├── config.ts
│   ├── errors.ts
│   ├── result.ts
│   ├── transport/{http,retry,telemetry}.ts
│   ├── generated/openapi.ts        (from openapi-typescript)
│   └── domains/scheduled-transfers.ts
├── test/{unit,integration}/...
├── DEPENDENCIES.md
├── README.md
└── .changeset/initial.md
```

Validation: `pnpm validate` passes, coverage 87% lines, `publint` and `attw` clean, conformance report attached to the PR.

## Constraints

- Never weaken `tsconfig.json` from the baseline (no opt-out of `strict`, `noUncheckedIndexedAccess`, or `exactOptionalPropertyTypes`).
- Never publish a `0.x.y` release that introduces a public-surface change without a `BREAKING CHANGES.md` entry.
- Never add a runtime dependency without an entry in `DEPENDENCIES.md` justifying it.
- Never write to `console.*` from `src/`; route every signal through the telemetry hook.
- When `docs/{context}/oas/openapi.yaml` is missing, do not invent endpoints — pause and request the OAS or hand-write a minimal stub under `src/types/` with the user's explicit approval.
