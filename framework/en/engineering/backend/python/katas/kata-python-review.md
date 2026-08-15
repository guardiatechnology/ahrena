# Kata: Python Code Review

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Backend: systematic code review for Python PRs

## Objective

This Kata defines the procedure to review Python code changes: verify correctness, type safety, test coverage, security, error handling, and adherence to project Lexis. The goal is to catch bugs, enforce standards, and share knowledge — not to gatekeep or nitpick style (Ruff handles that).

## When to Use

- When reviewing a pull request or code change in a Python backend service
- When invoked by `cry-python-review` or by the Apollo Warrior
- When the user asks for a code review or quality assessment

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Code to review | Yes | Diff, file paths, or PR reference containing the changes |
| Context | No | Feature description, related issue, or design document |

## Workflow

```
Progress:
- [ ] 1. Understand the change
- [ ] 2. Verify correctness
- [ ] 3. Check type safety
- [ ] 4. Assess test coverage
- [ ] 5. Review security
- [ ] 6. Review error handling
- [ ] 7. Check architecture compliance
- [ ] 8. Deliver review
```

### Step 1: Understand the Change

1. Read the PR description, commit messages, and related issue/spec
2. Understand the **intent** — what problem does this solve?
3. Identify the scope: which layers are affected (domain, infrastructure, HTTP)?

### Step 2: Verify Correctness

1. Does the code do what the description says?
2. Are edge cases handled? (null values, empty lists, boundary values, concurrent access)
3. Is the logic correct for all code paths?
4. Are there off-by-one errors, race conditions, or resource leaks?

### Step 3: Check Type Safety

1. Are all functions, parameters, and return values typed? (lex-python-typing)
2. Are types accurate? (not `Any` without justification, not overly broad)
3. Would mypy strict pass on the changes?
4. Are Pydantic models used for validation at boundaries?

### Step 4: Assess Test Coverage

1. Does every new behavior have a test? (lex-python-testing)
2. Are tests at the right level? (unit for logic, integration for DB, HTTP for endpoints)
3. Are mocks used only at system boundaries? (not mocking internal collaborators)
4. Are edge cases and error paths tested?
5. Are assertions meaningful? (testing behavior, not implementation)
6. For domain invariants: would Hypothesis property-based tests add value?

### Step 5: Review Security

1. No hardcoded secrets? (lex-python-security)
2. Input validated at boundaries? (Pydantic models with constraints)
3. SQL uses parameterized queries? (no string interpolation)
4. Error messages don't expose sensitive data?
5. New dependencies audited for vulnerabilities?

### Step 6: Review Error Handling

1. No bare `except:` or generic `except Exception:` without context? (lex-python-error-handling)
2. Exceptions are specific to the failure mode?
3. Errors are logged with sufficient context for debugging?
4. Error responses don't leak internal details?

### Step 7: Check Architecture Compliance

1. Domain layer free of framework imports? (codex-python-architecture)
2. Dependencies point inward? (infrastructure → domain, never reverse)
3. Dataclasses are frozen? (lex-python-immutability)
4. No premature abstractions? (no interface for a single implementation without testing need)
5. Follows existing codebase patterns?

### Step 8: Deliver Review

Structure the review as:

1. **Summary:** one-sentence assessment (approve, request changes, or comment)
2. **Critical issues:** bugs, security vulnerabilities, missing tests (must fix)
3. **Suggestions:** improvements that would strengthen the code (optional)
4. **Positive notes:** what was done well (acknowledge good patterns)

**Rules:**
- Be specific — reference file, line, and the issue
- Explain **why**, not just what — cite the relevant Lexis or Codex
- Suggest a fix when possible, don't just point out problems
- Don't comment on style — Ruff handles formatting
- Don't request changes for personal preference — only for Lexis violations, bugs, or missing tests

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Review | Structured feedback (summary, critical, suggestions, positives) | Inline in conversation or as PR review comments |

## Constraints

- This Kata reviews code — it does not implement fixes (kata-python-implement handles that)
- Focus on substance (correctness, security, tests) over style (Ruff handles style)
- Do not block PRs for non-critical suggestions
- Escalate to human when the change has architectural implications beyond the reviewer's scope

## References

- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-tooling (engineering/backend)
