# Lexis: Python Error Handling

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: error handling standards for Python code

## Purpose

Ensure that Python code handles errors explicitly, specifically, and traceably. Bare exceptions swallow bugs. Generic catches mask root causes. Silent failures corrupt data. Every error must be either handled with intent or propagated with context.

## Law

> **NEVER use bare `except:` or `except Exception:` without re-raising or logging with full context. All exceptions MUST be specific to the failure mode. Custom domain exceptions MUST inherit from a project base exception. Error messages MUST NOT expose sensitive data (credentials, tokens, PII).**

## Scope

- **Applies to:** all Python source files — application code, infrastructure code, scripts.
- **Bound agents:** all agents and implementers that write or modify Python code.
- **Exceptions:** top-level error handlers (FastAPI exception handlers, CLI entry points) may catch broad exceptions for graceful degradation, but MUST log the original exception.

## Consequences of Violation

1. **Silent corruption:** swallowed exceptions allow invalid state to propagate.
2. **Debugging cost:** generic catches without context make root cause analysis impossible.
3. **Security leak:** error messages containing credentials or PII are an information disclosure vulnerability.
4. **Remediation:** bare exceptions must be replaced with specific handlers before merge.

## Examples

### Correct

```python
from app.exceptions import TransactionNotFoundError, InsufficientFundsError

# Specific exception with context
async def transfer(source_id: UUID, target_id: UUID, amount: int) -> Transfer:
    source = await repository.get_by_id(source_id)
    if source is None:
        raise TransactionNotFoundError(entity_id=source_id)
    if source.balance < amount:
        raise InsufficientFundsError(
            available=source.balance, requested=amount
        )
    ...

# Top-level handler — catches broad, logs original
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"errors": [{"code": "INTERNAL_ERROR"}]})
```

### Incorrect

```python
# Bare except — swallows everything
try:
    await process_payment()
except:
    pass

# Generic catch without re-raise or logging
try:
    result = await repository.save(entity)
except Exception:
    return None  # silently returns None, caller has no idea save failed

# Leaking sensitive data
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail=f"Auth failed for token {e.token}")
```

## Automated Validation

- **Tool:** Ruff rules (E722 bare except, BLE001 blind exception); code review.
- **When:** every commit (pre-commit) and every PR (CI).
- **Metric:** 0 bare exceptions; 0 generic catches without logging/re-raise.

## References

- [PEP 8 — Programming Recommendations (exceptions)](https://peps.python.org/pep-0008/#programming-recommendations)
- [Ruff E722](https://docs.astral.sh/ruff/rules/bare-except/)
- codex-python-architecture (engineering/backend)
