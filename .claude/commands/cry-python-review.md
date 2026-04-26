Python Code Review. Shortcut to review Python code per backend Lexis and Codex

# Cry: Python Code Review

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to review Python code per backend Lexis and Codex

## Usage

```
/cry-python-review <target> [context]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `target` | Yes | What to review: file paths, diff, PR number, or "last commit" | "src/transactions/", "PR #42", "last commit" |
| `context` | No | What the change is about, related issue or spec | "Implements transaction cancellation per issue #15" |

## What the Command Does

1. Reads the target code or diff
2. Assumes the role of the Apollo Warrior (Senior Python Engineer)
3. Executes **kata-python-review** systematically:
   - Understands the change intent
   - Checks correctness, types, tests, security, error handling, architecture
4. Delivers structured review: summary, critical issues, suggestions, positive notes

## Prompt Template

```
Context:
- Review target: {{target}}
- Additional context: {{context}}

Task:
Act as the Apollo Warrior (Senior Python Engineer) and execute **kata-python-review**. Review the code against all applicable Lexis (lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability) and Codex (codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing). Focus on correctness, security, and test coverage — not style (Ruff handles that).

Output format:
1. **Summary:** one-sentence assessment (approve / request changes / comment)
2. **Critical issues:** bugs, security vulnerabilities, missing tests (must fix)
3. **Suggestions:** improvements that would strengthen the code (optional)
4. **Positive notes:** what was done well
```

## Invocation Example

**Input:**

```
/cry-python-review "src/transactions/" "New transaction cancellation feature per issue #15"
```

**Expected output:**

Apollo reviews the code and delivers:

**Summary:** Request changes — missing test for concurrent cancellation race condition.

**Critical:**
- `repository.soft_delete()` at `src/transactions/infrastructure/database/repositories/transaction_repo.py:45` does not check `version` for optimistic locking — concurrent cancellations could corrupt state (lex-python-error-handling)
- No test for the 409 conflict case when cancelling an already-cancelled transaction (lex-python-testing)

**Suggestions:**
- Consider adding a Hypothesis property test for the invariant "a cancelled transaction cannot be cancelled again" (codex-python-testing)

**Positive:**
- Clean separation between domain and infrastructure (codex-python-architecture)
- Pydantic response model with `from_domain()` pattern is well implemented

## Constraints

- The Cry triggers a review — it does not implement fixes (cry-python-implement handles that)
- Focus on substance over style — Ruff handles formatting
- Do not block for non-critical suggestions

## Associated Kata and Warrior

- **kata-python-review** — Full code review procedure
- **warrior-apollo** — Senior Python Engineer; executes kata-python-review
