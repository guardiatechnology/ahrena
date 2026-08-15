# Codex: Python Logging with Loguru and Decorator

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: logging pattern in Python applications

## Overview

Python specialization of `lex-logging-decorator`. Applications use `loguru` configured once at boot and a `@logged` decorator that wraps functions and automatically emits enter, exit, duration, and exception events. Calls to `logger.info` and equivalents do not appear in function bodies.

## Context

- **Domain:** operational logging in Python services — APIs, workers, jobs, CLIs.
- **Target audience:** implementers and AI agents that write or maintain Python code (warrior-apollo).
- **Update trigger:** format evolution, new correlation fields, new decorator capabilities.

## Content

### Principles

1. Centralized configuration — `loguru` configured once at boot.
2. Decorator-driven logging — instrumentation at the boundary; function body is business logic.
3. JSON structure — logs consumed by machines (CloudWatch, Datadog, ELK).
4. Mandatory correlation — `trace_id`, `span_id`, `correlation_id` via `loguru.contextualize`.
5. Boundary redaction — allowlist/denylist applied before serialization.
6. Success is an event — every decorated execution emits `enter`+`exit` (or `error`); failures are re-raised.

### Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Logger | `loguru` | Single API; sinks, formatting, exception capture |
| Decorator | `app.shared.logging.decorator` | Enter/exit/error instrumentation with redaction |
| Correlation | `loguru.contextualize` + `opentelemetry-instrumentation-logging` | `trace_id`, `span_id`, `correlation_id` |
| Serialization | `orjson` | Fast JSON sink for production |

`logging` (stdlib), `structlog`, and `print` are not allowed in application code.

### Boot

```python
# app/shared/logging/setup.py
import sys
from loguru import logger
from app.shared.logging.serializer import json_sink


def setup_logging(service_name: str, level: str = "INFO") -> None:
    logger.remove()
    logger.configure(extra={"service": service_name})
    logger.add(sys.stdout, level=level, backtrace=False, diagnose=False,
               format="<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green> "
                      "<level>{level: <8}</level> trace_id={extra[trace_id]} {message}",
               filter=lambda r: r["extra"].setdefault("trace_id", "-") or True)
    logger.add(json_sink, level=level)
```

`backtrace=False` and `diagnose=False` in production (`loguru` tracebacks may expose variables with PII). `setup_logging` is called once in the entrypoint.

### JSON Sink

```python
# app/shared/logging/serializer.py
import orjson

DENY = {"password", "token", "secret", "api_key", "authorization", "cookie", "cpf", "ssn"}


def _redact(d: dict) -> dict:
    return {k: ("[REDACTED]" if k.lower() in DENY else v) for k, v in d.items()}


def json_sink(message) -> None:
    r = message.record
    payload = {
        "timestamp": r["time"].isoformat(),
        "level": r["level"].name,
        "service": r["extra"].get("service", "unknown"),
        "logger": r["name"],
        "message": r["message"],
        "trace_id": r["extra"].get("trace_id"),
        "span_id": r["extra"].get("span_id"),
        "correlation_id": r["extra"].get("correlation_id"),
        "operation": r["extra"].get("operation"),
        "outcome": r["extra"].get("outcome"),
        "duration_ms": r["extra"].get("duration_ms"),
        "args": _redact(r["extra"].get("args", {})),
    }
    if r["exception"] is not None:
        payload["exception"] = {"type": r["exception"].type.__name__, "value": str(r["exception"].value)}
    print(orjson.dumps(payload).decode())
```

Only exception type + value; the full traceback goes to the trace via `span.record_exception`. `print` here is the logger's output boundary, not application logging.

### Decorator

```python
# app/shared/logging/decorator.py
import asyncio, functools, inspect, time
from typing import Any, Callable, ParamSpec, TypeVar
from loguru import logger

P = ParamSpec("P"); R = TypeVar("R")


def logged(operation: str, *, level: str = "INFO",
           capture_args: bool = True, redact: tuple[str, ...] = ()) -> Callable:
    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        is_async = asyncio.iscoroutinefunction(fn)

        def _bound(args, kwargs) -> dict:
            if not capture_args:
                return {}
            try:
                b = inspect.signature(fn).bind_partial(*args, **kwargs)
            except TypeError:
                return {}
            raw = dict(b.arguments); raw.pop("self", None); raw.pop("cls", None)
            return {k: ("[REDACTED]" if k in redact else _safe(v)) for k, v in raw.items()}

        def _emit(outcome: str, args_dict: dict, duration_ms: float | None, exc: bool = False) -> None:
            ctx = {"operation": operation, "args": args_dict, "outcome": outcome}
            if duration_ms is not None:
                ctx["duration_ms"] = duration_ms
            with logger.contextualize(**ctx):
                if exc:
                    logger.opt(exception=True).error("{} error", operation)
                else:
                    logger.log(level if outcome != "error" else "ERROR", "{} {}", operation, outcome)

        @functools.wraps(fn)
        async def aw(*args: P.args, **kwargs: P.kwargs) -> R:
            bound, t0 = _bound(args, kwargs), time.perf_counter()
            _emit("enter", bound, None)
            try:
                result = await fn(*args, **kwargs)
            except Exception:
                _emit("error", bound, (time.perf_counter() - t0) * 1000, exc=True); raise
            _emit("exit", bound, (time.perf_counter() - t0) * 1000); return result

        @functools.wraps(fn)
        def sw(*args: P.args, **kwargs: P.kwargs) -> R:
            bound, t0 = _bound(args, kwargs), time.perf_counter()
            _emit("enter", bound, None)
            try:
                result = fn(*args, **kwargs)
            except Exception:
                _emit("error", bound, (time.perf_counter() - t0) * 1000, exc=True); raise
            _emit("exit", bound, (time.perf_counter() - t0) * 1000); return result

        return aw if is_async else sw  # type: ignore[return-value]
    return deco


def _safe(v: Any) -> Any:
    return v if isinstance(v, (str, int, float, bool, type(None))) else repr(v)[:200]
```

Supports sync and async; `operation` is mandatory in `domain.action` format; `capture_args=False` at boundaries with free payload; `redact` complements the sink's global denylist. The decorator does not swallow exceptions — it logs `error` and re-raises.

### Usage

```python
from app.shared.logging import logged


class CreateTransferUseCase:
    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

In HTTP routers, use `capture_args=False` when the payload may contain unfiltered free data.

### Trace ↔ log correlation

`opentelemetry-instrumentation-logging` injects `otelTraceID` and `otelSpanID` into each record. A FastAPI middleware propagates `correlation_id` per request:

```python
from uuid import uuid4
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cid = request.headers.get("x-correlation-id") or str(uuid4())
        with logger.contextualize(correlation_id=cid):
            response = await call_next(request)
        response.headers["x-correlation-id"] = cid
        return response
```

### Levels

| Level | When | Who emits |
|-------|------|-----------|
| `DEBUG` | Dev only; detailed instrumentation | Decorator with `level="DEBUG"` |
| `INFO` | Operational events (default) | Decorator |
| `WARNING` | Recoverable degraded behavior (retry, fallback) | Decorator with `level="WARNING"` |
| `ERROR` | Untreated exception aborting the operation | Decorator (automatic in `except`) |
| `CRITICAL` | Failure affecting the entire service | Global handler |

`SUCCESS` and `TRACE` (loguru-specific) are not used.

### Where `logger` appears directly

The unbreakable rule (`lex-logging-decorator`) lists three cases. They live in three predictable modules:

| Module | Role |
|--------|------|
| `app/shared/logging/setup.py` | Configures `loguru` at boot |
| `app/shared/logging/decorator.py` | Implements `@logged` |
| `app/infrastructure/http/exception_handlers.py` (or worker/Lambda) | Logs uncaptured top-level exceptions |

Any other file importing `from loguru import logger` to call `logger.<level>` is a violation.

### Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| `operation` | `domain.action` in snake_case | `transfer.create`, `ledger.post_entry` |
| JSON keys | snake_case | `trace_id`, `correlation_id`, `duration_ms` |
| Argument capture | Default `True`; `False` at boundaries with free payload | `capture_args=False` in HTTP router |
| Redaction | By field name (sink) and by argument (decorator) | `redact=("password", "card_number")` |
| Re-raise | Always | The decorator never swallows |

## Glossary

| Term | Definition |
|------|------------|
| Sink | Log destination in `loguru` |
| Operation | Stable event identifier; key for search and dashboards |
| Outcome | Event status: `enter`, `exit`, `error` |
| Redaction | Replacement of sensitive values with `[REDACTED]` |
| Correlation ID | Per-request UUID propagated in logs and response headers |

## References

- [Loguru](https://loguru.readthedocs.io/) — [orjson](https://github.com/ijl/orjson)
- lex-logging-decorator (_foundation/quality) — language-agnostic law
- kata-python-logging-setup (engineering/backend) — setup procedure
- codex-python-observability (engineering/backend) — traces and metrics
- lex-python-security, lex-python-error-handling (engineering/backend)
