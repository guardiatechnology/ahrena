# Lexis: Guardia SDK in TypeScript/Node.js

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — SDK: any TypeScript/Node.js client library that consumes the Guardia REST API, regardless of distribution (`@guardia/*` on npm or internal-only)

## Law

> **Every TypeScript/Node.js SDK that consumes the Guardia REST API MUST: (1) compile under `strict: true` with `noUncheckedIndexedAccess: true` and target ES2022 or newer; (2) declare every public symbol in the `exports` field of `package.json` — implicit barrel re-exports outside `exports` are FORBIDDEN; (3) version under Semantic Versioning 2.0.0, where any change visible in the public API surface (types, function signatures, exported error codes, runtime behavior of documented contracts) constitutes a major or minor bump as defined in `codex-semantic-version`; (4) propagate the canonical Guardia request headers on every HTTP call — `Authorization: Bearer <token>`, `Idempotency-Key` for mutating verbs, and `X-Grd-Trace-Id` — per `lex-restful-headers` and `lex-idempotency`; (5) translate error responses into the standardized error envelope defined in `lex-error-handling`, preserving `code`, `reason`, and `message`, without leaking transport-level shapes; (6) ship type declarations (`.d.ts`) generated from the source — `any` MUST NOT appear in the public surface, and `unknown` is permitted only at parse boundaries (response decoding) with a typed narrowing path; (7) declare each runtime dependency in `dependencies` with a justified entry in the SDK's `DEPENDENCIES.md` — adding a runtime dependency without justification is FORBIDDEN; (8) provide unit tests for every public function and integration tests against a recorded HTTP transport (nock/MSW or equivalent) with ≥ 80% line coverage in CI; (9) expose telemetry hooks (request lifecycle, error, retry) that consumers MAY wire to OpenTelemetry — internal `console.*` calls are FORBIDDEN; (10) declare `engines.node` with the minimum supported Node.js LTS version (currently `>=20`) and MUST NOT use APIs introduced after that floor without a runtime guard.**

## Scope

- **Applies to:** every Guardia-authored TypeScript or JavaScript SDK whose purpose is to consume the Guardia REST API, regardless of distribution channel (`@guardia/*` on npm, private GitHub Packages, monorepo internal package, vendored fork).
- **Out of scope:** application code that embeds an SDK (consumers), generated code emitted by `openapi-typescript`/`openapi-fetch` from `docs/{context}/oas/openapi.yaml` (the SDK wraps and re-exposes generated code through its own public surface, which is in scope).
- **Bound agents:** `warrior-apollo` (when authoring an SDK on behalf of an API context), `warrior-hephaestus` (when integrating an SDK into a frontend), `warrior-iris` (mobile consumers of Node-compatible SDKs), `warrior-athena` (Gate 2 of the Issue-Driven flow).
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **Automatic block:** Gate 2 (`kata-quality-gate`) rejects the PR when any clause of the Law is violated and not remediated.
2. **Public-surface breakage:** any drift from clauses (2), (3), or (6) is treated as a published-contract incident and triggers a coordinated deprecation cycle per `codex-semantic-version`.
3. **Security escalation:** auth-header leaks, missing `Idempotency-Key` on mutating verbs, or untyped `any` returns in the public surface are escalated to the platform owner of the consumed API context.
4. **Remediation:** the SDK MUST be brought into conformance before the next release; intermediate releases with known violations carry a documented `KNOWN_ISSUES.md` entry and a target version for the fix.

## Examples

### Correct

```typescript
// src/client.ts — public API
import type { paths } from "./generated/openapi";

export class GuardiaClient {
  constructor(private readonly config: GuardiaClientConfig) {}

  async createScheduledTransfer(
    input: CreateScheduledTransferInput,
    options: RequestOptions = {},
  ): Promise<Result<ScheduledTransfer, GuardiaError>> {
    return this.transport.request({
      method: "POST",
      path: "/v1/scheduled-transfers",
      body: input,
      headers: {
        "Idempotency-Key": options.idempotencyKey ?? randomUuidV7(),
        "X-Grd-Trace-Id": this.tracer.currentTraceId(),
      },
      decoder: ScheduledTransferDecoder,
    });
  }
}
```

```json
// package.json — explicit exports, engines, no implicit barrel
{
  "name": "@guardia/sdk-scheduled-payments",
  "version": "1.4.0",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    },
    "./errors": {
      "types": "./dist/errors.d.ts",
      "import": "./dist/errors.js",
      "require": "./dist/errors.cjs"
    }
  },
  "engines": { "node": ">=20" },
  "files": ["dist", "README.md", "DEPENDENCIES.md"]
}
```

### Incorrect

```typescript
// ❌ Untyped public surface
export async function createTransfer(input: any): Promise<any> {
  const res = await fetch("/v1/transfers", { method: "POST", body: JSON.stringify(input) });
  return res.json(); // no Idempotency-Key, no Authorization, no error envelope, returns any
}
```

```json
// ❌ Implicit barrel, no engines, no exports map
{
  "name": "guardia-sdk",
  "main": "src/index.ts",
  "dependencies": { "axios": "*", "lodash": "*", "moment": "*" }
}
```

## Automated Validation

- **Tooling:**
  - **Strict TS:** `tsc --noEmit` with the SDK's `tsconfig.json` extending `@guardia/tsconfig-sdk` (provides `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`).
  - **Public-surface drift:** `api-extractor` (or `arethetypeswrong`/`publint`) checking `exports` map, dual-emit consistency, and `.d.ts` coverage.
  - **Semver enforcement:** `changesets` with `--commit-mode=intent`; CI blocks merges that bump version without a corresponding changeset.
  - **HTTP contract:** integration suite recording requests against `nock` or MSW with assertions on `Authorization`, `Idempotency-Key`, `X-Grd-Trace-Id`.
  - **Dependency audit:** `npm audit --omit=dev` + `depcheck`; presence of `DEPENDENCIES.md` enforced by Gate 2.
  - **Linter:** `eslint-plugin-no-restricted-imports` blocking `console.*` in `src/`; `@typescript-eslint/no-explicit-any` set to `error` in publishable files.
- **Timing:** pre-commit (lint, types), CI on every PR (full suite, coverage, publint), pre-publish (`npm publish --dry-run` validation), Gate 2 of the Issue-Driven flow.
- **Metric:** 0 PRs merged with `any` in the public surface; 100% of mutating endpoints with `Idempotency-Key` assertion in integration tests; 100% of releases with a corresponding changeset entry; non-decreasing line coverage on `main`.
