# Lexis: Test Pyramid

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Test distribution across levels (unit, integration, E2E) in any stack to ensure fast feedback, adequate coverage, and sustainable cost

## Purpose

Pipelines dominated by slow E2E tests kill the dev cycle (feedback in minutes instead of seconds); suites dominated by unit mocks give false security (tests pass, integration blows up in prod). The test pyramid distributes rigor across the levels where each type works best — unit tests fast and cheap at the base, E2E expensive but essential at the top.

This Lexis exists to ensure that **every project has a test distribution proportional to the pyramid**, that **E2E tests are restricted to critical journeys**, and that **integration tests cover real boundaries (DB, queue, external API)**.

## Law

> **Every test suite MUST respect the approximate proportion of 70% unit / 20% integration / 10% E2E. E2E tests MUST cover only declared critical journeys (login, checkout, onboarding) — never exhaustive CRUD. Integration tests MUST use real boundaries (real database, real queues in container) and mocks MUST be limited to non-free or non-deterministic external services.**

## Rules

### 1. 70/20/10 Proportion

Measured by **number of tests** (not by time). Tolerance: ±10 percentage points in small projects (<50 total tests).

If the proportion is inverted (e.g.: 30% unit / 60% E2E) → **suite is unbalanced**; refactor before adding more tests.

### 2. E2E only for critical journeys

An E2E journey:
- Represents a transaction of real value to the end user (pay, book, send).
- Crosses multiple bounded contexts or UI + backend + data.
- Has real cost of failure (lost revenue, corrupted data).

Cases that **DO NOT** deserve E2E:
- Form validation (unit component test is enough).
- Standard CRUD (integration test on the endpoint + unit on the domain).
- Aesthetic or layout variations.

### 3. Integration uses real boundaries

The agent **MUST**:

- Use **real database** in container (PostgreSQL, MySQL) — not SQLite in-memory in projects that run PostgreSQL in prod.
- Use **real queues** in container (Redis, RabbitMQ, Kafka) — not library mocks.
- Use **containers with the same version as production** (`postgres:16` not `postgres:latest`).

The agent **MAY** mock:
- Paid external APIs (Stripe, SMS providers).
- Services that do not have a public sandbox.
- Time/clock for deterministic tests.

### 4. Isolation between tests

Tests at the same level **MUST NOT** share mutable state. Each test:
- Starts from a known state (fixtures, truncate, isolated transaction).
- Does not depend on execution order.
- Can run in parallel without race conditions.

Flaky tests = bug: either in the test or in the system. Never tolerate retry as a solution.

### 5. Pyramid adapted by context

Exceptions to 70/20/10 allowed with documented justification:

- **Pure integration projects** (ETL, glue code): naturally inverted pyramid (more integration); document it.
- **Pure libraries** (no I/O): 90%+ unit is acceptable.
- **Mobile apps**: UI tests (Espresso/XCUITest) partially replace E2E; proportion adjusted.

Document deviation in ADR when structural.

## Applicability

- **Applies to:** every test suite in all Ahrena projects.
- **Linked agents:** `warrior-hera`, `warrior-apollo`, `warrior-hephaestus`.
- **Exceptions:** None. Lexis do not admit exceptions (documented deviations are contextual, not violations).

## Consequences of Violation

1. **Slow pipeline:** 80% E2E = 30+ min build; dev turns off local CI, regressions escape.
2. **False security:** 90% unit with mocks = prod breaks in production on untested integrations.
3. **Tolerated flaky tests:** team learns to ignore red builds; coverage becomes theater.
4. **Remediation:** audit distribution; migrate tests from the wrong level (E2E → integration when possible); explicitly declare legitimate E2E journeys.

## Automated Validation

- **Tool:** test count by conventional directory (`tests/unit`, `tests/integration`, `tests/e2e`); lint that flags E2E tests outside the declared directory.
- **Timing:** monthly in CI as a report; at Gate 2 (via `kata-quality-gate` Check 3) for new features.
- **Metric:** distribution ≈ 70/20/10 ±10pp; 0 active flaky tests; unit suite time < 60s.

## References

- `lex-frontend-testing`, `lex-python-testing` — rules per stack
- `codex-test-strategy` — detailed strategy (levels, scopes)
- `warrior-hera` — QA/Test Strategy specialist
- [Test Pyramid — Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)
