# Kata: Python Bug Diagnosis

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Backend: systematic debugging of Python applications

## Objective

This Kata defines the procedure to diagnose and fix bugs in Python backend applications: reproduce the issue with a failing test, isolate the root cause, apply the fix, and add a regression test. No guessing — every fix is proven by a test that failed before and passes after.

## When to Use

- When a bug is reported in a Python backend service
- When invoked by the Apollo Warrior for debugging tasks
- When a test is failing and the cause is not immediately obvious
- When production behavior diverges from expected behavior

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Bug description | Yes | What is happening vs. what is expected |
| Reproduction steps | No | How to trigger the bug (API call, input data, sequence of events) |
| Error output | No | Stack trace, log entries, error messages |
| Environment | No | Where the bug occurs (local, staging, production) |

## Workflow

```
Progress:
- [ ] 1. Reproduce with a failing test
- [ ] 2. Isolate the root cause
- [ ] 3. Apply the fix
- [ ] 4. Verify the fix
- [ ] 5. Check for related issues
```

### Step 1: Reproduce with a Failing Test

1. Read the bug description, stack trace, and any provided context
2. Identify the **entry point**: which endpoint, function, or event triggers the bug?
3. Write a test that exercises the exact scenario and **asserts the expected behavior**
4. Run the test — it MUST fail. If it passes, the reproduction is wrong; refine it
5. If reproduction is unclear, **ask the user** for more details: exact input, sequence, environment

**Rules:**
- A bug without a failing test is not yet understood
- The test should be minimal — the smallest input that triggers the bug
- Mark the test clearly: `test_<description>_regression`

### Step 2: Isolate the Root Cause

1. Read the stack trace to identify the failure point
2. Trace the data flow from the entry point to the failure:
   - What value is wrong?
   - Where was it produced or transformed?
   - What condition was not met?
3. Narrow down: can a **unit test** reproduce it? (faster iteration)
   - If yes, write a focused unit test
   - If no (infrastructure-dependent), keep the integration test
4. Identify the root cause: is it a logic error, a missing validation, a race condition, a data mapping issue, or an infrastructure problem?

### Step 3: Apply the Fix

1. Fix the root cause — not a symptom
2. The fix should be **minimal**: change only what is necessary to make the failing test pass
3. Do not refactor surrounding code in the same commit (kata-python-refactor is separate)
4. Ensure the fix follows all applicable Lexis:
   - Type hints complete (lex-python-typing)
   - Error handling specific (lex-python-error-handling)
   - No security regressions (lex-python-security)

### Step 4: Verify the Fix

1. Run the regression test — it MUST now pass
2. Run the **full test suite** — no existing tests should break
3. Run `ruff check .` and `mypy .` — no new issues
4. Verify that the fix addresses the original bug description, not just the test

### Step 5: Check for Related Issues

1. Is the same pattern present elsewhere in the codebase? (same bug in similar code)
2. If yes, fix all instances or create a follow-up task
3. Could this bug have been prevented by a missing validation, a stricter type, or a better test? Consider adding a guardrail

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Fix | Python source changes | Affected files |
| Regression test | Python test file | `tests/unit/` or `tests/integration/` |
| Root cause analysis | Brief text explanation | Commit message or conversation |

## Execution Example

### Example Input

```
Bug: POST /v1/transactions returns 500 when currency is lowercase ("brl" instead of "BRL").
Stack trace: ValidationError in Pydantic model — currency pattern ^[A-Z]{3}$ rejects lowercase.
Expected: 422 with descriptive error, not 500.
```

### Example Output (summary)

1. **Reproduction test:** `test_create_transaction_lowercase_currency_returns_422` — sends `{"amount": 1000, "currency": "brl"}`, asserts 422 with error code `VALIDATION_ERROR`
2. **Root cause:** Pydantic `ValidationError` is not caught by the exception handler; FastAPI returns generic 500 instead of the structured 422 response
3. **Fix:** Added `RequestValidationError` handler in `register_exception_handlers()` that maps Pydantic validation errors to the standard 422 error response format
4. **Verification:** regression test passes; all 47 existing tests pass; Ruff and mypy clean
5. **Related:** same missing handler would affect all endpoints — fix is global (one change, full coverage)

## Constraints

- Never guess at the fix without reproducing first — write the failing test
- Never fix symptoms — find and fix the root cause
- Never change unrelated code in the fix commit
- Escalate to human if the bug involves data corruption, security breach, or cross-service issues

## References

- codex-python-testing (engineering/backend)
- lex-python-error-handling, lex-python-testing (engineering/backend)
