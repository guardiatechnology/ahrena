# Cry: Validate BDD Scenario Coverage in the Test Suite

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Standalone — confirms that every business BDD scenario in a GitHub issue has at least one covering test (by canonical marker or fallback)

## Description

Standalone shortcut to invoke `kata-bdd-validate-scenarios`. Reads the `bdd:scenarios` block from a GitHub issue, scans the test suite for canonical `@bdd_scenario` markers (and per-stack equivalents) plus fallback patterns, and emits a bidirectional coverage report. Does not run tests, does not modify the issue or any source file. Independent of the Issue-Driven flow.

## Usage

```
/cry-bdd-validate-scenarios <issue-number> [<owner>/<repo>]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `issue-number` | Yes | Issue containing the `bdd:scenarios` block | `42` |
| `<owner>/<repo>` | No | Default: current repo via git remote | `guardiafinance/ahrena` |

## Prerequisites

- `github` listed in `mcp.servers` in `.ahrena/.directives`
- Env: `GITHUB_PAT` (required)
- Existing issue with a `bdd:scenarios` block (otherwise the kata reports "nothing to validate" and stops)

## What the Command Does

1. Invokes `kata-bdd-validate-scenarios`.
2. The kata reads the issue body and extracts scenarios with their slugs.
3. The kata scans the working tree for canonical `bdd_scenario` markers per stack (`@bdd_scenario("slug")` Python decorator, `// @bdd_scenario slug` JSDoc tag or `bddScenario("slug", ...)` wrapper in JS/TS, `// bdd_scenario: slug` comment in Go) and fallback patterns (`BDD: <title-or-slug>` in test name or docstring).
4. The kata emits a coverage report listing covered scenarios, gaps, and drift, with concrete file/line evidence and a recommendation per finding.

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Run kata-bdd-validate-scenarios for issue #{{issue-number}}. Read the bdd:scenarios block from the issue body. Scan the test suite for canonical `bdd_scenario` markers per stack (`@bdd_scenario("slug")` in Python, `// @bdd_scenario slug` or `bddScenario(...)` in JS/TS, `// bdd_scenario: slug` in Go) and fallback patterns (`BDD: <title-or-slug>` in test name or docstring). Build the bidirectional map. Report `complete`, `gaps`, `drift`, or `gaps+drift` with concrete file/line evidence and a recommendation per finding.

Do not run tests. Do not modify any file. Do not infer scenarios from test code.

Strictly respect lex-bdd-coverage and lex-mcp.
```

## Invocation Example

**Input:**

```
/cry-bdd-validate-scenarios 42
```

**Expected output:**

```
BDD Coverage — Issue #42 — Result: gaps

Scenarios in issue: 3
Covered: 2 | Uncovered: 1 | Orphan markers: 0

| Scenario | Slug | Tests | Status |
|---|---|---|:-:|
| Customer requests a refund for an eligible payment | customer-requests-a-refund-for-an-eligible-payment | tests/refunds/test_create.py::test_pending_refund | ✅ |
| Customer cannot refund after 30 days | customer-cannot-refund-after-30-days | tests/refunds/test_eligibility.py::test_30d_window | ✅ |
| Concurrent refunds deduplicate by idempotency key | concurrent-refunds-deduplicate-by-idempotency-key | — | ❌ |

Recommendation:
- `concurrent-refunds-deduplicate-by-idempotency-key` is uncovered. Add a test (any level) marked `@bdd_scenario("concurrent-refunds-deduplicate-by-idempotency-key")` or with `BDD: Concurrent refunds deduplicate by idempotency key` in its docstring.
```

## Restrictions

- **Read-only.** Does not modify the issue, tests, or any other file.
- **Does not run tests.** This is a structural mapping check, not a behavioral one.
- **Standalone.** Does not block or modify any other flow (Issue-Driven, Gate 2). Run it whenever useful.
- **No silent passes.** When the issue has no `bdd:scenarios` block, the command says so explicitly.

## Cry vs Kata

| Aspect | Cry | Kata |
|---|---|---|
| Nature | Quick invocation by issue number | Full procedure (parse, scan, classify, report) |
| Complexity | Low | High (8 steps incl. multi-stack scanning) |

## Associated Cries and Katas

- `kata-bdd-validate-scenarios` — invoked by this cry
- `cry-bdd-create-scenarios` — predecessor cry (authors scenarios)
- `kata-quality-gate` — orthogonal; can run together with this cry for a fuller coverage picture, but is not coupled

## References

- `lex-bdd-coverage` — coverage law
- `codex-bdd` — methodology and marker conventions
- `kata-bdd-validate-scenarios` — procedure
- `lex-test-pyramid`, `codex-test-strategy` — test-level decisions for the covering tests
