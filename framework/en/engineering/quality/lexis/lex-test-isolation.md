# Lexis: Test Isolation

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Ensuring each test runs from a known state, independent of order and parallelizable without race conditions

## Purpose

Tests that depend on order, mutable global state, or real time become time bombs: they pass locally, fail in CI; they pass on one machine, fail on another. The team loses hours debugging the test instead of the code. Worse: tolerating retry as a solution teaches teams to ignore signals — the next real bug is buried in the noise.

This Lexis exists to ensure that **every test is deterministic, independent, and parallelizable**, and that **flaky tests are treated as critical bugs** — not as inconveniences.

## Law

> **Every test MUST start from a known state, MUST NOT depend on execution order, and MUST be able to run in parallel with others of the same type without race conditions. Non-deterministic external dependencies (clock, network, random, UUID) MUST be parameterized or mocked. Flaky tests MUST be fixed immediately or disabled — never ignored with retry.**

## Rules

### 1. Known initial state

Each test **MUST**:

- Start with explicit fixtures/factories — never rely on data from a previous test.
- Clean up state after execution (truncate tables, reset caches, unmount components).
- Use transactions + rollback when possible (test commits, framework reverts).

**Antipattern:** `test_create_user` trusts that `test_delete_user` has not yet run.

### 2. Order independence

Running the suite in **random** order (`pytest --randomly`, Jest `testSequencer: 'random'`) **MUST** produce the same result. Failures that appear only in a specific order indicate coupling via shared state.

### 3. Safe parallelism

Tests at the same level **MUST** be parallelizable (`pytest -n auto`, Jest default). If tests share a resource (database, port, file), they **MUST** use a unique identifier per worker (`pytest-xdist` worker id, schema per worker).

### 4. Mocks for non-determinism

| Source of non-determinism | Strategy |
|---|---|
| Clock (`datetime.now()`, `Date.now()`) | Inject clock; freeze in test with `freeze_time` |
| UUID / random | Fixed seed or injection |
| External network (paid APIs, services without sandbox) | VCR / MSW / fixture; validate contract separately |
| Shared filesystem | `tempfile` / container per test |
| Environment variables | Set/unset in fixture setup/teardown |

### 5. Flaky = critical bug

A flaky test:
- **MUST** be fixed in the sprint in which it was detected.
- While open, **MUST** be marked (`@pytest.mark.flaky` with reason + ticket) and have visibility.
- Never "handle with retry" (`pytest-rerunfailures`) without investigating root cause — retry is anesthesia, not cure.

Valid exceptions for retry:
- E2E test against an external service with real latency and known SLA agreement.
- Document the retry with a comment justifying it.

### 6. Monitored suite time

- **Unit**: each test < 1s; total suite < 60s on dev machine.
- **Integration**: each test < 10s; total suite < 5min in CI.
- **E2E**: each journey < 2min; total suite < 15min in CI.

Tests that exceed the level's budget **MUST** be moved to a higher level (unit → integration) or optimized.

## Applicability

- **Applies to:** every test suite in all projects.
- **Linked agents:** `warrior-hera`, `warrior-apollo`, `warrior-hephaestus`.
- **Exceptions:** None. Slow but stable tests are acceptable at the right level; flakiness never.

## Consequences of Violation

1. **Wasteful debug:** engineers spend hours finding why the test fails on Monday and passes on Tuesday.
2. **Loss of trust in CI:** red builds become noise; merges approved with red tests "because it's flaky".
3. **Prod incidents:** race conditions not caught in test (because tests masked them) blow up in production.
4. **Remediation:**
   - Identify flaky tests (historical report: failure rate).
   - Each flaky becomes a P1 ticket; fix or disable.
   - Reinforce parallelism + random order in CI.

## Automated Validation

- **Tool:**
  - `pytest --randomly-seed=random` (detects order dependency)
  - `pytest -n auto` / Jest parallelism (detects race conditions)
  - Historical tracking of flakes in CI (GitHub Actions, CircleCI insights).
- **Timing:** every CI execution; weekly flake report.
- **Metric:** 0 active flaky (without ticket); >99% determinism in the suite.

## References

- `lex-test-pyramid` — distribution per level
- `lex-frontend-testing`, `lex-python-testing`
- `warrior-hera` — leads test strategy
