---
paths:
  - "**/*.py"
---

# Lexis: Python Error Handling

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: error handling standards for Python code, complementary to `lex-python-result-type` and `lex-python-error-object`

## Law

> **Bare `except:` and `except Exception:` are FORBIDDEN unless paired with logging via `logger.exception(...)` and either re-raise or translation into a typed `Error` (per `lex-python-error-object`). Custom exceptions raised in the permitted cases (per `lex-python-result-type`) MUST be specific to the failure mode and MUST inherit from a project base exception. Exception messages MUST NOT expose sensitive data (credentials, tokens, PII). Top-level boundary handlers (FastAPI exception handlers, CLI entry points, message-consumer entry points) MUST log the original exception with full context and translate it into an `Error` before producing the response payload.**

## Examples

### Correct

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import Error, InternalError

logger = logging.getLogger(__name__)
app = FastAPI()

# Top-level boundary handler — logs original, translates into Error
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    error = InternalError(message="An unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content={"errors": [{"code": error.code, "reason": error.reason, "message": error.message}]},
    )

# Specific exception, narrow except, no PII leakage
async def load_external_payload(url: str) -> bytes:
    try:
        return await http_client.get_bytes(url)
    except TimeoutError:
        logger.warning("External call timed out", extra={"url": url})
        raise  # propagate to boundary; will be logged + translated
```

### Incorrect

```python
# Bare except — swallows everything
try:
    await process_payment()
except:
    pass  # ❌

# Generic catch without logging or translation
try:
    result = await repository.save(entity)
except Exception:
    return None  # ❌ caller has no idea save failed

# Leaking sensitive data
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail=f"Auth failed for token {e.token}")  # ❌ token in message
```

## Automated Validation

- **Tool:** Ruff rules (E722 bare except, BLE001 blind exception); code review enforcing logging + `Error` translation at boundary handlers.
- **When:** every commit (pre-commit) and every PR (CI).
- **Metric:** 0 bare exceptions; 0 generic catches without logging; 0 boundary handlers returning a payload that is not built from an `Error` instance.
