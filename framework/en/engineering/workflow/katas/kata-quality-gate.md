# Kata: Quality Gate (Gate 2)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Phase 6 of the Issue-Driven flow — final implementation validation with 7 checks including AC↔test traceability, scope creep, best practices, tests, coverage, types, and performance budget

## Objective

Run Gate 2 of the Issue-Driven flow: 7 stack-aware verifications on the implementation completed in Phase 4 (and reviewed in Phase 5). Produces a `go`/`no-go`/`unverifiable` report at `.ahrena/issues/{n}/06-quality-report.md`. Any failure returns to Phase 4 with detailed context; only `go` allows advancing to Phase 7 (PR creation). Individual checks that cannot be executed in the current environment (tool missing, no applicable files) report `unverifiable` and surface that to the human rather than silently passing.

This kata is the **quality guardian** of the flow — it ensures the implementation covers every AC, did not exceed scope, applied the best practices defined by the framework's Lexis, and did not regress performance beyond declared budgets.

## When to Use

- Phase 6 of the flow orchestrated by `warrior-athena`, after `kata-security-review` results in `approved`
- Whenever an implementation must be rigorously validated before opening a PR

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Phase 2 requirements | Yes | `.ahrena/issues/{n}/02-requirements.md` (numbered ACs) |
| Phase 3 architecture | Yes | `.ahrena/issues/{n}/03-architecture.md` (component table — scope) |
| Phase 4 implementation | Yes | Code + tests in the working tree |
| Phase 5 review | Yes | `.ahrena/issues/{n}/05-security-review.md` (must be `approved`) |
| Coverage threshold | No | `quality.coverage_threshold` in `.directives` (default: 80) |
| Stack | Yes | Code language (detected from touched files) |

## Workflow

```
Progress:
- [ ] 1. Collect context (ACs, scope, diff, stack)
- [ ] 2. Check 1 — Bidirectional AC ↔ test traceability
- [ ] 3. Check 2 — Scope creep
- [ ] 4. Check 3 — Best practices (applicable Lexis per stack)
- [ ] 5. Check 4 — Tests executed
- [ ] 6. Check 5 — Coverage
- [ ] 7. Check 6 — Types
- [ ] 8. Check 7 — Performance budget
- [ ] 9. Consolidate go/no-go/unverifiable result
- [ ] 10. Persist to .ahrena/issues/{n}/06-quality-report.md
- [ ] 11. Update checkpoint
```

### Step 1: Collect context

1. Read ACs from `02-requirements.md` (extract `AC-1`, `AC-2`, ...).
2. Read the component table from `03-architecture.md` (extract the list of planned files).
3. Run `git diff --name-only {base}...HEAD` for the list of modified files.
4. Detect stack (`*.py` → Python; `*.ts` → Node/TS; etc.).
5. Read `quality.coverage_threshold` from `.ahrena/.directives` (default: `80`).
6. **Detect execution mode** by reading the front-matter of `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - If `stack.approved: true` is present, the mode is **per layer** (see dedicated section below); identify the current layer (`stack.decomposition[i].status: in-progress`) and filter `covers_acs` + `components`.
   - Otherwise, the mode is **single PR** (default behavior; steps 2-8 run over the full set of ACs and components).

### Per-layer (Stacked PRs) Mode

When the checkpoint contains `stack.approved: true`, this kata is invoked **once per layer** before the layer submits its PR. Each execution operates on subsets, not on the full set:

| Check | Scope in per-layer mode |
|---|---|
| Check 1 — AC ↔ test | Filter by the `stack.decomposition[i].covers_acs` subset. ACs outside the layer are **not** evaluated in this run; they will appear in a later layer |
| Check 2 — Scope creep | Compare files modified since the previous layer against `stack.decomposition[i].components` (not the full Phase 3 table) |
| Check 3 — Best practices | Apply Lexis to files modified in the current layer (same rules; smaller scope) |
| Check 4 — Tests | Run the full suite (tests cannot be safely partitioned by layer) |
| Check 5 — Coverage | Evaluate against the threshold over the cumulative diff up to the current layer (base→layer N) |
| Check 6 — Types | Same rule; scope = layer files |
| Check 7 — Performance budget | Same rule; apply when the layer touches performance-sensitive code |

**Status transitions:**
- The layer starts as `pending`; Athena promotes it to `in-progress` when starting Phase 4 for that layer.
- When the 7 checks return ✅ for the layer, this kata updates `stack.decomposition[i].status: submitted` in the checkpoint.
- After the layer's PR merges, Athena (or `kata-stacked-pr-merge`) updates it to `merged`.

**Final aggregate validation:** triggered automatically at the **end of the last layer's run** — i.e., on the same `kata-quality-gate` invocation that flips the final `pending` layer to `submitted`. After the 7 layer-scoped checks return ✅, the kata performs an additional aggregate pass that confirms:
1. Every numbered AC from Phase 2 was covered by **some** layer (no orphan AC).
2. Every component declared in Phase 3 was touched by **some** layer (no orphan component).

If aggregate validation fails, the layer's overall result is downgraded to `no-go` and the report points out the orphan elements. In single-PR flows (no `stack`), aggregate validation is trivially equivalent to Check 1 over the full set and adds no extra pass.

### Step 2: Check 1 — Bidirectional AC ↔ test traceability

**AC → Test:**

Use the **canonical form per stack** (deterministic parsing); fall back to regex only if canonical form is absent.

| Stack | Canonical marker | How to collect |
|---|---|---|
| Python / pytest | `@pytest.mark.ac("AC-N")` | `pytest --collect-only -q -m "ac"` + parse marker args |
| JS/TS / Jest, Vitest | `@ac` tag in docblock or `test.meta({ac: "AC-N"})` | parse via AST or filename regex |
| Go | `// ac: AC-N` comment above `func TestXxx` | `go list` + comment scan |
| Other | filename/docstring regex `AC[-_]?\d+` | fallback only |

1. For each AC identified in Step 1, collect covering tests via canonical markers.
2. If canonical marker absent, **fall back to regex** (name or docstring containing `AC-{N}` / `AC_{N}`) and emit a warning that canonical form is preferred.
3. Each AC must have at least 1 corresponding test.
4. ACs without a test → ❌ `Check 1 — AC→Test`.

**Test → AC:**

1. For each new/modified test in the diff, verify it references at least one AC (canonical or fallback).
2. Tests without referenced AC → ❌ `Check 1 — Test→AC` (indicates scope creep).

Check 1 result: ✅ if both directions are complete; ❌ otherwise. If no tests exist at all in the stack (edge case) → `unverifiable`.

### Step 3: Check 2 — Scope creep

1. Compare the list of modified files (Step 1) with the Phase 3 component table.
2. Files outside the table → scope creep candidates.
3. **Legitimate exceptions** (do not flag):
   - Test files corresponding to declared components (e.g., if `service.py` is in the table, `test_service.py` is implicit).
   - Automatic configuration files (e.g., `requirements.lock`, `yarn.lock`).
   - Documentation generated by the flow itself (e.g., `.ahrena/issues/{n}/*`).
4. New public functions/classes in touched files that do not map to any AC → flag.

Check 2 result: ✅ if only declared files + exceptions were modified; ❌ if there is unjustified scope creep.

If ❌: **options presented to the user**:
- (a) Expand ACs (return to Phase 2/3 and re-run Gate 1).
- (b) Revert out-of-scope code and open a new issue for it.

### Step 4: Check 3 — Best practices (applicable Lexis per stack)

Select Lexis applicable to the detected stack(s) and run each verification. Each Lexis either `✅`, `❌`, or `unverifiable` (tool missing / inapplicable). Unverifiable does not block but is surfaced in the report.

**Python (`*.py` in the diff):**

| Lexis | Verification | Command / Heuristic |
|---|---|---|
| `lex-python-typing` | No type errors | `mypy --strict {touched-files}` |
| `lex-python-testing` | Public functions tested | For each new/modified public function, search for a test that calls it |
| `lex-python-security` | No hardcoded credentials | Regex for credential patterns |
| `lex-python-immutability` | No mutation of shared structures | Static (AST) analysis: mutation of parameters or globals |
| `lex-python-error-handling` | No `except: pass` or swallowing | Regex for `except` without re-raise and without log |

**Frontend (`*.ts|*.tsx|*.vue|*.svelte` in the diff):**

| Lexis | Verification | Command / Heuristic |
|---|---|---|
| `lex-frontend-typing` | No type errors | `tsc --noEmit`; zero `any` without justification comment |
| `lex-frontend-testing` | Components with logic/interaction tested | Cross-reference component files vs. test files |
| `lex-frontend-accessibility` | WCAG 2.1 AA | `eslint-plugin-jsx-a11y` report; `jest-axe` results; Lighthouse a11y ≥ 95 |
| `lex-frontend-security` | No unsanitized `dangerouslySetInnerHTML`; no bundled secrets | AST scan + bundle string scan |

**Infrastructure (`*.tf|*.ts (CDK)|*.yaml` in the diff):**

| Lexis | Verification | Command |
|---|---|---|
| `lex-aws-security` | IAM least privilege; encryption; secrets | `tfsec`, `checkov`, or `cdk-nag` — 0 critical/high |
| `lex-aws-iac` | Tagging; state remote; no inline secrets | Linter + repo policy |
| `lex-aws-cost` | Cost allocation tags present; expected cost estimated | `infracost` diff |

**Cross-stack (all diffs):**

| Lexis | Verification |
|---|---|
| `lex-conventional-commits` | `git log {base}..HEAD --format=%s` + regex `^(feat\|fix\|chore\|docs\|refactor\|test\|build\|ci)(\(.+\))?: .+` |
| `lex-observability-required` | New HTTP endpoint / event consumer emits trace + metric + structured log (AST scan for instrumentation call patterns per stack) |

Record violations with file/line. Any violation → ❌ `Check 3 — {lex-name}`. Lexis not applicable to stacks present in the diff is omitted (neither pass nor fail).

### Step 5: Check 4 — Tests executed

1. Run test command detected by stack:
   - Python: `pytest`
   - Node/TS: `yarn test` (or `npm test` per `.directives`)
2. Capture exit code and output.
3. Any failure → ❌ `Check 4 — Tests`.

### Step 6: Check 5 — Coverage

1. Run test with coverage:
   - Python: `pytest --cov={package} --cov-report=term-missing`
2. Extract total coverage percentage.
3. Compare with `quality.coverage_threshold` (default: 80).
4. `% < threshold` → ❌ `Check 5 — Coverage ({%}% < {threshold}%)`.

### Step 7: Check 6 — Types

1. Run stack-specific type checker:
   - Python: `mypy --strict` over modified packages
   - TS: `tsc --noEmit`
2. Capture errors.
3. New errors (in files modified in this PR) → ❌ `Check 6 — Types`.
4. Pre-existing errors in unmodified files → do not block (record as a note).

### Step 8: Check 7 — Performance budget

Read `quality.performance` from `.ahrena/.directives`. If absent, this check reports `unverifiable` (not a failure) and emits a recommendation to configure budgets. Example:

```yaml
quality:
  coverage_threshold: 80
  performance:
    lighthouse_min: 80            # Frontend only
    bundle_kb_max: 250            # Frontend only (main bundle)
    api_p99_ms_max: 300           # Backend only (changed endpoints)
    benchmark_regression_pct: 10  # Backend; max allowed regression vs. baseline
```

Run checks applicable to the stack:

**Frontend:**
1. Build production bundle (`yarn build` or equivalent).
2. Measure size of primary chunks; compare to `bundle_kb_max`.
3. Run Lighthouse in headless mode on a representative page; compare `performance` score to `lighthouse_min`.

**Backend (API changes):**
1. For each modified endpoint, run a smoke benchmark (`pytest-benchmark` for Python, `k6` or similar for others).
2. Compare p99 to `api_p99_ms_max` (absolute) and to last baseline on main (regression %).

**Infrastructure:**
1. Run `infracost diff`; flag if expected cost delta exceeds budget declared in Phase 3 by more than 20%.

Any budget breach → ❌ `Check 7 — Performance`. Tools missing or no applicable change → `unverifiable`.

### Step 9: Consolidate go/no-go/unverifiable result

1. If all 7 checks are ✅ (or `unverifiable` where a ❌ would not apply) → result `go`.
2. If any check is ❌ → result `no-go`.
3. If more than 2 checks are `unverifiable` → report `go-with-caveats` and present to the human: proceed, or address the gaps first. The human decides; no automatic override to `go`.

For each ❌ or `unverifiable`, record:
- Which check
- Details (files, lines, commands, output) or reason (missing tool, no applicable files)
- Correction or configuration recommendation

### Step 10: Persist to `.ahrena/issues/{n}/06-quality-report.md`

Structure:

```markdown
# Quality Gate — Issue #{n}: {title}

- **References:** [Requirements](./02-requirements.md) · [Architecture](./03-architecture.md) · [Security](./05-security-review.md)
- **Date:** {YYYY-MM-DD}
- **Result:** {✅ go | ❌ no-go | ⚠️ go-with-caveats}
- **Stack detected:** {Python | Frontend (TS) | IaC (Terraform) | mixed}

## AC ↔ Test Traceability Matrix

| AC | Description | Covering tests | Status |
|---|---|---|:-:|
| AC-1 | ... | `test_foo_AC_1`, `test_bar_AC_1` | ✅ |
| AC-2 | ... | `test_baz_AC_2` | ✅ |
| AC-3 | ... | — | ❌ |

### Tests without referenced AC (scope creep candidates)

- `test_helper_utility` in `tests/test_utils.py:42` — {recommendation}

## Result per Check

| # | Check | Status | Details |
|:-:|---|:-:|---|
| 1 | AC ↔ Test Traceability | {✅/❌/⚠️} | {summary} |
| 2 | Scope Creep | {✅/❌} | {summary} |
| 3 | Best Practices | {✅/❌/⚠️} | {summary} |
| 4 | Tests Executed | {✅/❌/⚠️} | {summary} |
| 5 | Coverage | {✅/❌/⚠️} | {current}% / {threshold}% |
| 6 | Types | {✅/❌/⚠️} | {summary} |
| 7 | Performance Budget | {✅/❌/⚠️} | {summary of metrics vs. budget} |

## Failure Details

### Check {n}: {name}

{detailed description, files, lines, command output}

**Recommendation:** {how to fix}

## Conclusion

- If `go`: proceed to Phase 7 (`kata-pr-prepare`).
- If `no-go`: return to Phase 4 with the corrections above.
```

### Step 11: Update checkpoint

1. Update `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - completed phase: 6
   - result: `go` or `no-go`
   - If `go`: next phase = 7
   - If `no-go`: next phase = 4 (return for corrections)
   - **Per-layer mode:** additionally update `stack.decomposition[i].status` for the current layer — `submitted` when `go`; keep `in-progress` when `no-go`. `phase_next` stays at 4 while any layer is pending.
2. Inform `warrior-athena`:
   - If `go` (single PR): advance to `kata-contributing-pr` (per `lex-issue-driven` Rule 12).
   - If `go` (per-layer mode): release the layer for submission via `kata-stacked-pr-create`; if any layer is still pending, return to Phase 4 for the next.
   - If `no-go`: present the report to the human and await direction (fix or expand ACs).

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Gate report | Markdown with 6 checks + traceability matrix | `.ahrena/issues/{n}/06-quality-report.md` |
| Result | `go` / `no-go` | Return to orchestrator |
| Updated checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrictions

- **Checks are executed, not simulated:** `pytest`, `mypy`, coverage, and scans are real commands; the kata cannot "mark as passed" without actual execution.
- **Check ordering is mandatory:** checks 1-3 (static analysis) before 4-6 (execution); if static analysis fails, still run the rest to report the complete picture.
- **Threshold configurable but not optional:** `quality.coverage_threshold` may be adjusted in `.directives`, but Check 5 is always executed.
- **No override for `no-go`:** the only legitimate way out of `no-go` is to fix the implementation or renegotiate ACs (via Gate 1). No human or agent can manually flip to `go`.
- **Fixed destination:** `.ahrena/issues/{n}/06-quality-report.md` (per `lex-issue-driven`). In per-layer mode, the report accumulates one section per layer plus a final aggregate section.
- **Per-layer subset does not relax criteria:** the AC/component filter only narrows the execution scope; thresholds (coverage, performance) and check strictness remain identical.

## References

- `lex-issue-driven` — laws of the flow, in particular traceability, scope creep, and Rule 11 (per-layer Gate 2 when a stack is approved)
- `codex-issue-workflow` — full detail of the 7 checks
- `codex-stacked-prs` — conceptual model and Decision Checklist for stacked PRs
- `kata-stacked-pr-create` — invoked by Phase 7 when a stack is approved
- `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-immutability`, `lex-python-error-handling`, `lex-conventional-commits` — Lexis verified in Check 3
