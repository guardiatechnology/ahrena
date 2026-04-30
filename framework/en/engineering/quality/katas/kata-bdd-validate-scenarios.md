# Kata: Validate BDD Coverage Across the Test Suite

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Standalone — confirms that every business BDD scenario in a GitHub issue is covered by at least one test, by canonical marker or fallback

## Objective

Read the `bdd:scenarios` block from a GitHub issue, scan the test suite for canonical BDD markers and fallback patterns, and produce a bidirectional coverage report (scenarios → tests, tests → scenarios) classified as `complete`, `gaps`, `drift`, or `gaps+drift`. The kata does not run tests; it inspects mappings.

## When to Use

- After implementation begins, to confirm that scenarios are being covered as tests land.
- On PR review, to confirm that a change matches the BDD intent recorded in the issue.
- Invoked through `/cry-bdd-validate-scenarios <issue>`.
- Standalone — independent of `kata-quality-gate`. Both can run on the same change without coupling.

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Issue number | Yes | GitHub issue containing the `bdd:scenarios` block |
| Repository | Yes | `owner/repo` (default: detected via git remote) |
| Test root | No | Path(s) to scan; defaults to common roots per stack |
| Stack | No | Detected from file extensions in the working tree |

## Workflow

```
Progress:
- [ ] 1. Verify MCP and directives
- [ ] 2. Read the issue and extract the bdd:scenarios block
- [ ] 3. Parse scenarios into (title, slug) pairs
- [ ] 4. Detect stack(s) and scan tests
- [ ] 5. Build scenario → test map
- [ ] 6. Build test → scenario map
- [ ] 7. Classify gaps and drift
- [ ] 8. Emit coverage report
```

### Step 1: Verify MCP and directives

Same as `kata-bdd-create-scenarios` Step 1. `github` MCP is required; Notion is not used here.

### Step 2: Read the issue

Use `kata-mcp-github-read` to fetch the issue body. Locate the `<!-- bdd:scenarios:start -->` ... `<!-- bdd:scenarios:end -->` block. If absent, report "no BDD scenarios authored in this issue" and stop. The kata is a no-op when there is nothing to validate; it never invents an absence-of-block as a finding.

### Step 3: Parse scenarios

For each `Scenario: <title>` line in the block:

1. Extract the title (verbatim, trimmed).
2. Compute the slug: lowercase, replace runs of non-alphanumerics with `-`, collapse repeated `-`, trim leading and trailing `-`.

Yield a list `[(title, slug)]`.

### Step 4: Detect stack and scan tests

Detect stacks from the working tree:

- `*.py` → Python
- `*.ts|*.tsx|*.js|*.jsx` → JS/TS
- `*.go` → Go

Default test roots when not specified:

- Python: `tests/`, `**/test_*.py`, `**/*_test.py`
- JS/TS: `tests/`, `__tests__/`, `**/*.test.{ts,tsx,js,jsx}`, `**/*.spec.{ts,tsx,js,jsx}`
- Go: `**/*_test.go`

For each test, collect:

- `markers`: list of slugs claimed via canonical marker
  - Python: `@bdd_scenario("...")` decorator above the test function (regex; tolerate either the bare helper or `@pytest.mark.bdd_scenario("...")` when the helper wraps a pytest mark)
  - JS/TS: `// @bdd_scenario <slug>` JSDoc tag immediately above the test, or `bddScenario("<slug>", ...)` call wrapping the test
  - Go: `// bdd_scenario: <slug>` comment immediately above `func TestXxx`
- `fallbacks`: list of slugs/titles found via test name or docstring matching `BDD:\s*<title-or-slug>`

A single test may map to multiple scenarios.

### Step 5: scenario → test map

For each scenario `(title, slug)`:

1. List tests with canonical marker matching `slug`.
2. List tests with fallback matching `title` or `slug` (case-insensitive on title; exact on slug).
3. Status: `covered` if ≥1 test in either group; `gap` otherwise.

### Step 6: test → scenario map

For each test that has at least one BDD marker or fallback:

1. Resolve the slug to a scenario in the parsed list.
2. If no matching scenario exists in the issue → `drift` (orphan marker).

### Step 7: Classify

- **`complete`**: every scenario covered, no orphan markers.
- **`gaps`**: at least one uncovered scenario.
- **`drift`**: at least one test claims a scenario absent from the issue.
- A run can be both (`gaps+drift`).

### Step 8: Emit coverage report

Markdown table to the user:

```markdown
# BDD Coverage — Issue #{n}

- **Result:** {complete | gaps | drift | gaps+drift}
- **Scenarios in issue:** {count}
- **Covered:** {count}  | **Uncovered:** {count}  | **Orphan markers:** {count}

## Scenario → Test

| Scenario | Slug | Tests | Status |
|---|---|---|:-:|
| Customer requests a refund for an eligible payment | customer-requests-a-refund-for-an-eligible-payment | tests/refunds/test_create.py::test_pending_refund | ✅ |
| Concurrent refunds deduplicate by idempotency key | concurrent-refunds-deduplicate-by-idempotency-key | — | ❌ |

## Drift (markers without scenarios)

- tests/legacy/test_old.py::test_a — claims `legacy-scenario-removed`
```

When `result != complete`, recommend explicit fixes per finding:

- **Gaps:** add a covering test (any level) marked with the scenario slug or `BDD: <title>` in the docstring; alternatively, remove the scenario from the issue if the rule is no longer in scope.
- **Drift:** remove the marker, rename it to a valid slug, or restore the scenario in the issue.

If the user explicitly asks, save the report to `docs/bdd-coverage/{issue-n}.md`. Otherwise, emit only inline.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Coverage report | Markdown response | User-facing |
| Optional saved report | Markdown file | `docs/bdd-coverage/{issue-n}.md` (only when the user asks) |

## Restrictions

- **Read-only.** Does not modify the issue, tests, or any other file.
- **Does not execute tests.** Coverage here is structural (mapping), not behavioral.
- **Does not infer scenarios from tests.** A test without a marker is not coverage.
- **No silent passes.** When the issue has no `bdd:scenarios` block, the kata says so explicitly.

## References

- `lex-bdd-coverage` — coverage law
- `codex-bdd` — methodology and marker conventions
- `kata-bdd-create-scenarios` — predecessor procedure
- `lex-test-pyramid`, `codex-test-strategy` — level decisions for the covering tests
