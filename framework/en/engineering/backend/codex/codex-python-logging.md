# Codex: Python Logging with Loguru and Decorator

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: logging pattern in Python applications

## Overview

This manual defines how Python backend applications produce, format, and correlate logs. It is the Python specialization of `lex-logging-decorator` (the language-agnostic rule). The pattern combines two pieces that live together: (1) `loguru` configured once at application boot (sinks, JSON format, level, OpenTelemetry integration); (2) a `@logged` decorator that wraps functions and methods and automatically emits enter, exit, duration, and exception events. Calls to `logger.info` and equivalents do not appear in function bodies.

## Context

- **Domain:** operational logging for Python services — APIs, workers, jobs, and CLIs.
- **Target audience:** implementers and AI agents that write or maintain Python code (warrior-apollo).
- **Update trigger:** when the log format evolves, when new correlation fields are adopted, when the decorator gains new capabilities (sampling, additional redaction, domain events).

## Content

### Principles

1. **Centralized configuration:** `loguru` is configured once at application boot. No other file redefines sinks, format, or level.
2. **Decorator-driven logging:** instrumentation lives at the function boundary. The function body is business logic, not an audit trail.
3. **JSON structure:** logs are consumed by machines (CloudWatch, Datadog, ELK). Free text is a complement, not a key.
4. **Mandatory correlation:** `trace_id`, `span_id`, and `correlation_id` are propagated via `loguru.contextualize` and injected into each record.
5. **Boundary redaction:** the decorator applies a field allowlist/denylist before serializing arguments; PII and secrets never reach the sink.
6. **Success is an event, not silence:** every decorated function execution emits at least `enter` and `exit` (or `error`); failures are logged with `exception` and re-raised.

### Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Logger | `loguru` | Single logging API; sinks, formatting, exception capture |
| Decorator | `app.shared.logging.decorator` (internal) | Enter/exit/error instrumentation with redaction |
| Correlation | `loguru.contextualize` + `opentelemetry-instrumentation-logging` | Propagates `trace_id`, `span_id`, `correlation_id` |
| Serialization | `orjson` (optional) | Fast JSON sink for production |

`logging` (stdlib), `structlog`, and `print` are not part of the allowed stack in application code.

### Boot Configuration

```python
# app/shared/logging/setup.py
import sys
from loguru import logger

from app.shared.logging.serializer import json_sink


def setup_logging(service_name: str, level: str = "INFO") -> None:
    logger.remove()
    logger.configure(extra={"service": service_name})
    logger.add(
        sys.stdout,
        level=level,
        serialize=False,
        backtrace=False,
        diagnose=False,
        format=(
            "<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green> "
            "<level>{level: <8}</level> "
            "trace_id={extra[trace_id]} "
            "{message}"
        ),
        filter=lambda record: record["extra"].setdefault("trace_id", "-") or True,
    )
    logger.add(json_sink, level=level)
```

**Rules:**

- `setup_logging` is called once in the entrypoint (`main.py`, `app.py`, `lambda_handler.py`).
- `backtrace=False` and `diagnose=False` in production: `loguru` tracebacks may expose variables with PII.
- The stdout sink serves local dev; the JSON sink (`json_sink`) is the real channel in production.
- Default level `INFO`; `DEBUG` only via environment variable in non-prod environments.

### JSON Sink

```python
# app/shared/logging/serializer.py
import orjson

REDACTED = "[REDACTED]"
DENY = {"password", "token", "secret", "api_key", "authorization", "cookie", "cpf", "ssn"}


def _redact(payload: dict) -> dict:
    return {k: (REDACTED if k.lower() in DENY else v) for k, v in payload.items()}


def json_sink(message) -> None:
    record = message.record
    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "service": record["extra"].get("service", "unknown"),
        "logger": record["name"],
        "message": record["message"],
        "trace_id": record["extra"].get("trace_id"),
        "span_id": record["extra"].get("span_id"),
        "correlation_id": record["extra"].get("correlation_id"),
        "operation": record["extra"].get("operation"),
        "outcome": record["extra"].get("outcome"),
        "duration_ms": record["extra"].get("duration_ms"),
        "args": _redact(record["extra"].get("args", {})),
    }
    if record["exception"] is not None:
        payload["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
        }
    print(orjson.dumps(payload).decode())
```

**Rules:**

- Redaction applied before serialization. The team defines a safe-field allowlist; anything not in the allowlist is treated as sensitive by default for fields whose names appear in `DENY`.
- No full tracebacks in JSON: only type and message; the full traceback goes to the trace via `span.record_exception`.
- `print` appears **only** inside this sink — it is the logger's output boundary, not application logging.

### Decorator

```python
# app/shared/logging/decorator.py
import asyncio
import functools
import time
from typing import Any, Callable, ParamSpec, TypeVar

from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")


def logged(
    operation: str,
    *,
    level: str = "INFO",
    capture_args: bool = True,
    redact: tuple[str, ...] = (),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                bound = _bound_args(fn, args, kwargs, capture_args, redact)
                start = time.perf_counter()
                with logger.contextualize(operation=operation, args=bound, outcome="enter"):
                    logger.log(level, "{} enter", operation)
                try:
                    result = await fn(*args, **kwargs)
                except Exception:
                    duration_ms = (time.perf_counter() - start) * 1000
                    with logger.contextualize(
                        operation=operation, args=bound, outcome="error", duration_ms=duration_ms
                    ):
                        logger.opt(exception=True).error("{} error", operation)
                    raise
                duration_ms = (time.perf_counter() - start) * 1000
                with logger.contextualize(
                    operation=operation, args=bound, outcome="exit", duration_ms=duration_ms
                ):
                    logger.log(level, "{} exit", operation)
                return result

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = _bound_args(fn, args, kwargs, capture_args, redact)
            start = time.perf_counter()
            with logger.contextualize(operation=operation, args=bound, outcome="enter"):
                logger.log(level, "{} enter", operation)
            try:
                result = fn(*args, **kwargs)
            except Exception:
                duration_ms = (time.perf_counter() - start) * 1000
                with logger.contextualize(
                    operation=operation, args=bound, outcome="error", duration_ms=duration_ms
                ):
                    logger.opt(exception=True).error("{} error", operation)
                raise
            duration_ms = (time.perf_counter() - start) * 1000
            with logger.contextualize(
                operation=operation, args=bound, outcome="exit", duration_ms=duration_ms
            ):
                logger.log(level, "{} exit", operation)
            return result

        return sync_wrapper

    return decorator


def _bound_args(fn: Callable[..., Any], args: tuple, kwargs: dict, capture: bool, redact: tuple[str, ...]) -> dict:
    if not capture:
        return {}
    import inspect

    sig = inspect.signature(fn)
    try:
        bound = sig.bind_partial(*args, **kwargs)
    except TypeError:
        return {}
    raw = dict(bound.arguments)
    raw.pop("self", None)
    raw.pop("cls", None)
    return {k: ("[REDACTED]" if k in redact else _safe(v)) for k, v in raw.items()}


def _safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return repr(value)[:200]
```

**Rules:**

- The decorator supports sync and async functions. Never two manual versions — `@logged` decides.
- `operation` is mandatory and uses the `domain.action` format (e.g., `transfer.create`, `reconciliation.run`).
- `capture_args=True` by default; `False` at boundaries with untrusted input (e.g., webhook payload).
- `redact=("password", "card_number", ...)` applies redaction by argument name, complementing the sink's global denylist.
- The decorator does NOT swallow exceptions: it logs `error` and re-raises. Error handling is the global handler's responsibility (lex-python-error-handling).

### Usage

```python
# app/application/transfers/use_cases.py
from uuid import UUID

from app.application.transfers.ports import TransferRepository
from app.shared.logging import logged


class CreateTransferUseCase:
    def __init__(self, repository: TransferRepository) -> None:
        self._repository = repository

    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

```python
# app/infrastructure/http/routers/transfers.py
from fastapi import APIRouter, Depends

from app.application.transfers.use_cases import CreateTransferUseCase
from app.infrastructure.http.schemas import CreateTransferRequest, TransferResponse
from app.shared.logging import logged

router = APIRouter()


@router.post("/transfers", response_model=TransferResponse)
@logged(operation="http.transfer.create", capture_args=False)
async def create_transfer(
    payload: CreateTransferRequest,
    use_case: CreateTransferUseCase = Depends(),
) -> TransferResponse:
    entity_id = await use_case.execute(payload.source_id, payload.target_id, payload.amount)
    return TransferResponse(entity_id=entity_id)
```

### Trace ↔ log correlation

`opentelemetry-instrumentation-logging` injects `otelTraceID` and `otelSpanID` into each record. A FastAPI middleware propagates `correlation_id` per request:

```python
# app/infrastructure/http/middleware/correlation.py
from uuid import uuid4

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("x-correlation-id") or str(uuid4())
        with logger.contextualize(correlation_id=correlation_id):
            response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        return response
```

Each record carries `correlation_id` automatically — the decorator does not need to propagate it manually.

### Levels and when to use them

| Level | When to emit | Who emits |
|-------|--------------|-----------|
| `DEBUG` | Development only; detailed algorithm instrumentation | Decorator with `level="DEBUG"` |
| `INFO` | Relevant operational events (use case enter/exit, HTTP request served) | Decorator (default) |
| `WARNING` | Recoverable degraded behavior (retry, fallback, open circuit) | Decorator with `level="WARNING"` at retry boundaries |
| `ERROR` | Untreated exception that aborts the operation | Decorator (automatic in `except`) |
| `CRITICAL` | Failure affecting the entire service (DB unreachable, critical dependency down) | Global handler at the entrypoint |

`SUCCESS` and `TRACE` (loguru-specific) are not used.

### Where `logger` appears directly (allowed exceptions)

The unbreakable law (lex-logging-decorator) lists three cases. They live physically in three predictable modules:

| Module | Role |
|--------|------|
| `app/shared/logging/setup.py` | Configures `loguru` at boot |
| `app/shared/logging/decorator.py` | Implements `@logged` |
| `app/infrastructure/http/exception_handlers.py` (or worker/Lambda equivalent) | Logs uncaptured top-level exceptions |

Any other file importing `from loguru import logger` to call `logger.<level>` is a violation.

### Patterns and conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| `operation` format | `domain.action` in snake_case | `transfer.create`, `ledger.post_entry` |
| JSON structure | snake_case in all keys | `trace_id`, `correlation_id`, `duration_ms` |
| Argument capture | Enabled by default; disabled at boundaries with free payload | `capture_args=False` in HTTP router |
| Redaction | By field name (global sink) and by argument (decorator) | `redact=("password", "card_number")` |
| Exception re-raise | Always | The decorator never swallows |

## Glossary

| Term | Definition |
|------|------------|
| Sink | Log destination in `loguru` (stdout, file, custom function) |
| Operation | Stable identifier of the log event; key for search and dashboards |
| Outcome | Event status: `enter`, `exit`, `error` |
| Redaction | Replacement of sensitive values with `[REDACTED]` before serialization |
| Correlation ID | Per-request UUID propagated in logs and response headers |

## References

- [Loguru documentation](https://loguru.readthedocs.io/)
- [orjson](https://github.com/ijl/orjson) — JSON serializer used in the sink
- lex-logging-decorator (_foundation/quality) — language-agnostic law that makes the pattern mandatory
- kata-python-logging-setup (engineering/backend) — setup procedure
- codex-python-observability (engineering/backend) — traces and metrics via OpenTelemetry
- lex-python-security (engineering/backend) — no secrets or PII in logs
- lex-python-error-handling (engineering/backend) — exceptions and re-raise
