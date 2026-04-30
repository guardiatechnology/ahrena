# Lexis: BDD Coverage Through Test Mapping

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Coverage relationship between BDD scenarios in the GitHub issue and the test suite

## Law

> **Every business BDD scenario published in the GitHub issue (in the `bdd:scenarios` block) MUST be covered by at least one test of any level (unit, integration, E2E). The mapping MUST be discoverable from the test alone, by canonical `@bdd_scenario` marker (Python decorator, JSDoc/JS-TS tag, Go comment) carrying the scenario slug, or by fallback (`BDD: <title-or-slug>` in the test name or docstring). The framework does NOT mandate a Gherkin runner — scenarios remain documentation, tests remain the executable artifact. Scenarios without a covering test are gaps; markers pointing to scenarios absent from the issue are drift; both are violations.**

## Coverage

- **Applies to:** features that have BDD scenarios authored via `/cry-bdd-create-scenarios` (or otherwise present in the issue under the `bdd:scenarios` markers).
- **Bound agents:** `warrior-hera`, `kata-bdd-validate-scenarios`, code reviewers.
- **Exceptions:** features without BDD scenarios remain governed by their own quality rules (Issue-Driven AC↔test traceability, Gate 2). This Lexis is dormant for them.

## Rules

### 1. One scenario, at least one covering test

For each `Scenario: <title>` in the issue body, at least one test references it explicitly.

### 2. Mapping is discoverable from the test

Mapping mechanics, in order of preference:

| Stack | Canonical marker | Fallback |
|---|---|---|
| Python (pytest) | `@bdd_scenario("scenario-slug")` decorator on the test function | docstring contains `BDD: <scenario-title>` |
| JS/TS (Jest, Vitest) | `// @bdd_scenario scenario-slug` JSDoc tag immediately above the test, or a `bddScenario("scenario-slug", () => { ... })` wrapper | test name contains `BDD: <scenario-title>` |
| Go | `// bdd_scenario: scenario-slug` comment immediately above `func TestXxx` | function name contains the slug in CamelCase |
| Other | test name or docstring matching `BDD:\s*<title-or-slug>` | — |

`<scenario-slug>` is the kebab-case derivation of `Scenario: <title>` (lowercase, non-alphanumerics replaced with `-`, repeated `-` collapsed, trailing `-` removed). Example: `Customer requests a refund` → `customer-requests-a-refund`.

The `bdd_scenario` identifier is the canonical token across stacks. The framework does not ship the Python decorator or the JS/TS wrapper; projects that adopt BDD define a thin local helper (`bdd_scenario` / `bddScenario`) so the marker is grep-stable. The validation kata recognizes the canonical token regardless of the underlying implementation, as long as it carries the scenario slug.

### 3. Test level is open

The covering test may live at any level (unit, integration, E2E). Scenarios are level-agnostic. Level decisions follow `lex-test-pyramid` and `codex-test-strategy`.

### 4. No Gherkin runner is required

The framework does not mandate or recommend a Gherkin runner (Behave, Cucumber, SpecFlow). Scenarios are documentation; tests are the executable artifact. Projects that elect to adopt a runner may do so, but runner-generated tests still surface the mapping per Rule 2.

### 5. Bidirectional integrity

A test marker pointing to a scenario absent from the issue is drift. Cause is one of: scenario was renamed (rename the marker), scenario was removed (remove the test or update its scope), scenario never existed (correct the test). Drift is a violation, not a warning.

### 6. Renaming is a breaking change to the mapping

When a scenario is renamed in the issue, the slug changes; markers must be updated in the same change. Rename without marker update produces drift on the next validation run.

## Examples

### Correct

```python
# Issue body has: Scenario: Customer requests a refund for an eligible payment
@bdd_scenario("customer-requests-a-refund-for-an-eligible-payment")
def test_creates_pending_refund_and_audit_entry():
    """BDD: Customer requests a refund for an eligible payment."""
    ...
```

```typescript
// Issue body has: Scenario: Concurrent refunds deduplicate by idempotency key
// @bdd_scenario concurrent-refunds-deduplicate-by-idempotency-key
test("only one refund persists when two requests share an idempotency key", () => { ... });
```

### Incorrect

```python
# Scenario exists in the issue but no test references it (Rule 1 violation)
def test_creates_refund(): ...
```

```python
# Marker references a scenario absent from the issue (Rule 5 violation)
@bdd_scenario("legacy-scenario-removed-2-sprints-ago")
def test_legacy(): ...
```

## Automated Validation

- **Tool:** `kata-bdd-validate-scenarios` parses the `bdd:scenarios` block from the issue, scans the test suite for canonical markers and fallbacks per stack, and emits a bidirectional coverage report (covered, gaps, drift).
- **Timing:** on demand (`/cry-bdd-validate-scenarios <issue>`); recommended on PR review for any feature with BDD scenarios.
- **Metric:** 100% of scenarios have ≥1 covering test; 0 markers pointing to scenarios absent from the issue.
