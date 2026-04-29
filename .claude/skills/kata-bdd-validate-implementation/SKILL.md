---
name: kata-bdd-validate-implementation
description: "BDD Validation Report — Issue #{n}. Engineering — Quality. Second half of Phase 8 of the Issue-Driven flow. Maps each Gherkin scenario in 07-bdd-scenarios.md to existing tests in the repository and reports gaps."
---

# Kata: BDD Implementation Validation

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Quality. Second half of Phase 8 of the Issue-Driven flow. Maps each Gherkin scenario in `07-bdd-scenarios.md` to existing tests in the repository and reports gaps.

## Workflow

```
Progress:
- [ ] 1. Verify preconditions (Phase 8.1 complete and no BLOCKED ACs)
- [ ] 2. Parse 07-bdd-scenarios.md
- [ ] 3. Index repository tests (read-only)
- [ ] 4. Classify each scenario (covered | partial | missing)
- [ ] 5. Check BDD framework coupling
- [ ] 6. Compose 08-bdd-validation-report.md
- [ ] 7. Emit go | no-go decision
- [ ] 8. Update checkpoint
- [ ] 9. Final validation
```

### Step 1: Verify preconditions

1. Confirm `docs/issues/issue-{n}/07-bdd-scenarios.md` is present.
2. Confirm well-formed frontmatter: `sources`, `ac_coverage`, `generated_by: warrior-themis`.
3. Verify no AC has `status: BLOCKED` in `ac_coverage`. If any does, stop and route back to Phase 8.1 (the Issue must be amended before Gate 3 can pass).
4. Verify `sources` declares only allowed paths (no `src/`, `tests/`, etc.). Violation → fail and require Phase 8.1 regeneration.

### Step 2: Parse 07-bdd-scenarios.md

1. Extract the scenario list: for each, record `id (SCN-{N})`, AC tags (`@AC-{N}`), type tag (`@happy-path` etc.), title.
2. Build map `SCN → AC[]` and reverse map `AC → SCN[]`.
3. Validate `SCN-{N}` uniqueness in the file. Conflict = precondition failure (regenerate Phase 8.1).

### Step 3: Index repository tests

This step **may** open files under `tests/`, `__tests__/`, `spec/`, etc. No test execution — only static discovery.

1. Determine stack-conventional test directories:
   - Python: `tests/`, `tests/unit/`, `tests/integration/`, `tests/e2e/`
   - JS/TS: `__tests__/`, `tests/`, `e2e/`, `cypress/`, `playwright/`
   - Go: `*_test.go` files
   - Java: `src/test/java/`
2. For each test file, scan:
   - Function/`it`/`describe` names for `SCN-{N}` (regex `SCN[-_ ]?\d+`).
   - Docstrings/JSDoc/comments immediately above the function for the same reference.
3. Build map `SCN → [test_path:line, ...]`.
4. For each discovered test path, record the level inferred by directory (unit | integration | e2e).

### Step 4: Classify each scenario

For each `SCN-{N}` from Phase 8.1:

| Classification | Criterion |
|---|---|
| **covered** | ≥ 1 test references `SCN-{N}` **and** the level is compatible with the type tag |
| **partial** | A test references `SCN-{N}` **but** the level is insufficient for the scenario type (see table below), or only part of `Then` is asserted |
| **missing** | No test references `SCN-{N}` |

**Level ↔ type compatibility:**

| Type tag | Compatible level |
|---|---|
| `@happy-path` | unit OR integration OR e2e (any, per `lex-test-pyramid`) |
| `@alternative` | unit OR integration |
| `@edge` | unit OR integration |
| `@error` | unit OR integration |
| `@nfr` (latency, idempotency, availability) | integration OR e2e (pure unit cannot observe real NFR) |

If an `@nfr` scenario is covered only by a unit test → `partial` with recommendation to raise the level.

### Step 5: Check BDD framework coupling

1. Scan manifests against the forbidden list from `lex-bdd-no-framework-coupling` Rule 4:
   - Python: `pyproject.toml`, `requirements*.txt`, `Pipfile`, `setup.py` → look for `behave`, `pytest-bdd`, `lettuce`, `radish-bdd`.
   - JS/TS: `package.json` (deps + devDeps) → look for `cucumber`, `cucumber-js`, `@cucumber/cucumber`, `jest-cucumber`, `cypress-cucumber-preprocessor`.
   - Go: `go.mod` → look for `godog`.
   - Java: `pom.xml`, `build.gradle` → look for `cucumber-jvm`.
   - .NET: `*.csproj` → look for `specflow`, `reqnroll`.
2. Scan directory structure:
   - `features/` or `tests/features/` consumed by a runner.
   - `step_definitions/`, `steps/`, `support/world.js` bound to scenarios.
   - `@given`/`@when`/`@then`/`@step` decorators/annotations in test files.
3. Record result: `clean` (no violations) or `violations: [...]` (list of occurrences).

Additionally, if a test validates a scenario without a `SCN-{N}` reference (even when correct), record as a **traceability violation** — does not block go, but goes as a note in the gaps section.

### Step 6: Compose 08-bdd-validation-report.md

Structure:

```yaml
---
issue: {n}
repo: {owner/repo}
generated_at: "{ISO-8601}"
generated_by: warrior-themis
scenarios_total: 12
covered_count: 9
partial_count: 2
missing_count: 1
framework_coupling: clean   # or: violations
gate_3_decision: go | no-go
---
```

Body:

```markdown
# BDD Validation Report — Issue #{n}

## Summary

- Total scenarios: 12
- Covered: 9
- Partial: 2
- Missing: 1
- BDD framework coupling: clean

## Scenario ↔ Test Mapping

| SCN | AC | Type | Status | Tests |
|---|---|---|---|---|
| SCN-1 | AC-1 | @happy-path | covered | tests/integration/test_transfer_scheduling.py:23 |
| SCN-2 | AC-2 | @alternative | covered | tests/integration/test_transfer_scheduling.py:48 |
| SCN-3 | AC-3 | @error | covered | tests/integration/test_transfer_scheduling.py:71 |
| SCN-4 | AC-3 | @edge | partial | tests/unit/test_transfer_rules.py:15 (lower bound only) |
| SCN-5 | AC-4 | @nfr | partial | tests/unit/test_balance_query.py:8 (logic only, no observable latency) |
| SCN-6 | AC-5 | @nfr | missing | — |

## Gaps (no-go items)

### SCN-4 — partial (partial coverage)
- **AC:** AC-3
- **Currently covers:** lower bound (balance equal to amount)
- **Missing:** upper bound (balance equal to amount + fee)
- **Recommended level:** integration
- **Suggested owner:** warrior-apollo

### SCN-5 — partial (insufficient level)
- **AC:** AC-4 (@nfr — latency)
- **Currently covers:** unit logic of the query
- **Missing:** observable latency assertion
- **Recommended level:** integration with measurement
- **Suggested owner:** warrior-apollo

### SCN-6 — missing
- **AC:** AC-5 (@nfr — idempotency)
- **Recommended level:** integration
- **Suggested owner:** warrior-apollo

## Framework Coupling Check

- pyproject.toml: ✓ no step-runner
- package.json: ✓ no step-runner
- features/: ✓ absent
- step_definitions/: ✓ absent

## Gate 3 Decision

**no-go**

Reason: 1 missing scenario (SCN-6) + 2 partials (SCN-4, SCN-5).

## Next Actions

| Gap | Action | Owner | Level | Iteration |
|---|---|---|---|---|
| SCN-6 | Create integration test validating operation idempotency | warrior-apollo | integration | next |
| SCN-5 | Add integration test measuring observable latency | warrior-apollo | integration | next |
| SCN-4 | Extend existing test to cover upper bound | warrior-apollo | integration | next |
```

### Step 7: Emit go | no-go decision

- **go**: `missing_count == 0`, `partial_count == 0`, `framework_coupling == clean`.
- **no-go**: any other combination. List next actions with owner (warrior) and level (per `codex-test-strategy`).

### Step 8: Update checkpoint

Update `.ahrena/workflow/issue-{n}/checkpoint.md` with:

```yaml
phase_completed: 8.2
phase_next: 6.b   # if go: return to Quality Gate (Check 8)
                  # if no-go: awaiting warrior-apollo/hephaestus/iris to implement gaps
artifacts:
  bdd_validation_report: docs/issues/issue-{n}/08-bdd-validation-report.md
gate_3:
  status: go | no-go
  last_run_at: "{ISO-8601}"
updated_at: "{ISO-8601}"
```

### Step 9: Final validation

Before returning control:

- [ ] All `SCN-{N}` from Phase 8.1 appear in the mapping.
- [ ] Every `partial` or `missing` scenario has a recommended action with owner and level.
- [ ] Framework coupling check is complete (every manifest scanned).
- [ ] `go | no-go` decision is consistent with the report content.
- [ ] Checkpoint updated.

## Outputs

| Output | Format | Destination |
|-------|---------|-------------|
| Validation report | Markdown YAML + tables | `docs/issues/issue-{n}/08-bdd-validation-report.md` |
| Gate 3 decision | `go` or `no-go` | Response to orchestrator + checkpoint |
| Next actions list | Table | Report section |
| Updated checkpoint | Markdown YAML | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Constraints

- **MAY read code:** static test discovery is part of this Kata's purpose. The "blind to code" restriction only applies to `kata-bdd-scenarios-design` (Phase 8.1).
- **MUST NOT execute tests:** discovery is static (name/docstring parsing); execution validation belongs to `kata-quality-gate` Check 1.
- **MUST NOT modify tests:** when a gap exists, the Kata reports. Implementation of missing tests is delegated to `warrior-apollo`/`warrior-hephaestus`/`warrior-iris` in a follow-up iteration.
- **MUST NOT infer coverage without `SCN-{N}` reference:** if a test validates the behavior without referencing the scenario, it is a violation of `lex-bdd-no-framework-coupling` Rule 3 — recorded as a note, but does not count as coverage.
- **MUST block the gate** when a manifest declares a BDD step-runner or a runner-consumed `features/` directory is found.
