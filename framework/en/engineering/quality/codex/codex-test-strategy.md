# Codex: Test Strategy

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Test strategy applied in the Ahrena framework — levels, scopes, tools, when to use each, anti-patterns

## Overview

This Codex is the operational reference for **test strategy decisions** in Ahrena projects. Consulted by `warrior-hera` when designing a test plan for a feature, by `warrior-apollo` and `warrior-hephaestus` during implementation when there is doubt about at what level to test something, and by code reviewers at Gate 2.

## Context

- **Domain:** test strategy (what to test, where to test, how to test, when NOT to test)
- **Target audience:** `warrior-hera`, agents that implement production code, reviewers
- **Update:** when new test frameworks emerge, when architectural patterns change (e.g.: microservices alter what "integration" means)

## Content

### The 4 levels

| Level | Scope | Tools | Target time per test |
|---|---|---|---|
| **Unit** | Pure function, isolated class, component without I/O | pytest, Jest, Vitest, Go testing | < 100ms |
| **Integration** | Multiple components + real infra (DB, queue) | pytest + testcontainers, Jest + MSW + Postgres | < 10s |
| **E2E (API)** | Real HTTP request → system → response | pytest + httpx, Supertest, Pact | < 30s |
| **E2E (UI)** | Real browser → UI → backend → UI | Playwright, Cypress | < 2min |

### When to use each level

**Unit**: domain logic, utilities, pure functions, presentation components without I/O.
- Rule: if writing the test requires mocking more than 1 collaborator, it's probably integration, not unit.

**Integration**: any path that touches persistence, queue, cache, external API (even in container).
- Rule: test what production really uses (Postgres 16, not SQLite; real Redis, not in-memory).

**E2E (API)**: external contract visible to the consumer; flows between multiple endpoints.
- Rule: one per main endpoint; plus one per multi-endpoint flow (e.g.: create + list + delete).

**E2E (UI)**: critical business journeys; behaviors that only manifest in the browser (routing, end-to-end authentication, DOM events).
- Rule: ≤ 1 E2E UI per journey (login, checkout, onboarding); NOT one per screen.

### Decision tree

```
Something new to test?
│
├── Is it a pure function / domain logic?
│   → Unit test
│
├── Involves DB, queue, cache, or real integration?
│   ├── Cross-service or requires full deploy?
│   │   → E2E (API)
│   └── Isolable with container?
│       → Integration
│
├── Is it a critical and visual user journey?
│   → E2E (UI), 1 per journey
│
└── Is it aesthetic variation or CSS?
    → Visual regression test (or manual inspection)
```

### Tools per stack

**Python (Apollo):**
- Unit: `pytest` + `pytest-mock`
- Property-based: `hypothesis`
- Integration: `pytest` + `testcontainers-python` + real Postgres
- E2E API: `pytest` + `httpx` or `requests-mock` for externals
- Benchmarks: `pytest-benchmark`
- Coverage: `pytest-cov`

**Frontend (Hephaestus):**
- Unit/Component: `vitest` or `jest` + `@testing-library/react`
- Integration: `vitest` + `msw` (API mock)
- E2E: `playwright` (preferred) or `cypress`
- Visual regression: `chromatic` (Storybook) or `playwright-visual`
- Accessibility: `jest-axe`, `@axe-core/playwright`

**Backend infra (IaC):**
- Unit: Terraform module validation (`terraform validate`, `terraform test`)
- Integration: apply in sandbox account + assert via AWS SDK
- Policy: `opa test`, `conftest`

### Strategies for boundaries

**Paid external APIs (Stripe, Twilio):**
- Unit: full mock.
- Integration: provider sandbox when available + contract test (Pact).
- Production: canary smoke test post-deploy.

**Received webhooks:**
- Integration: send real provider payload (captured in VCR) to the endpoint.
- Validate idempotency: send 2x, expect 1 effect.

**Asynchronous events:**
- Integration: publish event, wait for consumer to process (controlled timeout).
- Validate side effects (DB updated, downstream event published).

### Anti-patterns to avoid

| Anti-pattern | Why it's bad |
|---|---|
| Mocking DB in repository test | Masks query/migration bugs; test proves nothing real |
| Giant snapshot without review | Diff blindly accepted; snapshot becomes noise |
| One E2E per endpoint | Suite explodes; CI becomes a marathon; ROI drops |
| Retry on flaky test | Doesn't cure; masks; teaches to ignore signals |
| `test.only` committed | We run only 1 test in CI without noticing; coverage drops without warning |
| Assert on implementation (`expect(foo.state).toBe(...)`)| Breaks with each refactor without real regression |

### Coverage

- **Coverage ≥ threshold** (80% default) is a necessary condition, not sufficient.
- 100% line coverage does **not** mean tested: it can be "was executed but without assertion".
- Prefer `branch coverage` over `line coverage` when available.
- Coverage is a **signal**, not a target metric. Critical features (payment, auth) must have coverage for real (mutation testing with `mutmut`, `stryker` to validate the quality of asserts).

### When NOT to test

- **Trivial code without logic** (pure getter/setter, `return x + 1`): test adds noise without value.
- **Thin library wrappers** (`def create_uuid(): return uuid.uuid4()`): tests the library, not the code.
- **Static configuration** (constants, labels): test only if it changes frequently.
- **Generated code**: trust the generator (OpenAPI client, Prisma schema).

Record the "do not test" decision in local comment or in review — documentation > silent absence.

## References

- `lex-test-pyramid` — 70/20/10 distribution
- `lex-test-isolation` — determinism and parallelism
- `lex-python-testing`, `lex-frontend-testing` — rules per stack
- `warrior-hera` — executes strategy
- `kata-test-plan-design` — design procedure
- `kata-quality-gate` — validates at Gate 2
- [Growing Object-Oriented Software, Guided by Tests (GOOS)](http://www.growing-object-oriented-software.com/)
