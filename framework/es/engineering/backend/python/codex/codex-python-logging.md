# Codex: Logging Python con Loguru y Decorator

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: patrón de logging en aplicaciones Python

## Overview

Especialización Python de `lex-logging-decorator`. Las aplicaciones usan `loguru` configurado una sola vez en el boot y un decorator `@logged` que envuelve funciones y emite, automáticamente, eventos de entrada, salida, duración y excepción. Las llamadas `logger.info` y equivalentes no aparecen en el cuerpo de las funciones.

## Context

- **Domain:** logging operativo en servicios Python — APIs, workers, jobs y CLIs.
- **Target audience:** implementadores y agentes de IA que escriben o mantienen código Python (warrior-apollo).
- **Update trigger:** evolución del formato, nuevos campos de correlación, nuevas capacidades en el decorator.

## Content

### Principios

1. Configuración centralizada — `loguru` configurado una sola vez en el boot.
2. Logging por decorator — instrumentación en la frontera; el cuerpo de la función es regla de negocio.
3. Estructura JSON — logs consumidos por máquinas (CloudWatch, Datadog, ELK).
4. Correlación obligatoria — `trace_id`, `span_id`, `correlation_id` vía `loguru.contextualize`.
5. Redacción en la frontera — allowlist/denylist aplicada antes de la serialización.
6. Éxito es evento — toda ejecución decorada emite `enter`+`exit` (o `error`); las fallas se relanzan.

### Stack

| Componente | Biblioteca | Propósito |
|------------|-----------|-----------|
| Logger | `loguru` | API única; sinks, formateo, captura de excepción |
| Decorator | `app.shared.logging.decorator` | Instrumentación de entrada/salida/error con redacción |
| Correlación | `loguru.contextualize` + `opentelemetry-instrumentation-logging` | `trace_id`, `span_id`, `correlation_id` |
| Serialización | `orjson` | Sink JSON rápido para producción |

`logging` (stdlib), `structlog` y `print` no están permitidos en código de aplicación.

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

`backtrace=False` y `diagnose=False` en producción (los tracebacks de `loguru` pueden exponer variables con PII). `setup_logging` se llama una vez en el entrypoint.

### Sink JSON

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

Solo tipo + valor de la excepción; el traceback completo va al trace vía `span.record_exception`. `print` aquí es la frontera de salida del logger, no logging de aplicación.

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

Soporta sync y async; `operation` es obligatorio en formato `domain.action`; `capture_args=False` en fronteras con payload libre; `redact` complementa el denylist global del sink. El decorator no engulle excepciones — loguea `error` y relanza.

### Uso

```python
from app.shared.logging import logged


class CreateTransferUseCase:
    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

En router HTTP, usar `capture_args=False` cuando el payload pueda contener datos libres no filtrados.

### Correlación trace ↔ log

`opentelemetry-instrumentation-logging` inyecta `otelTraceID` y `otelSpanID` en cada record. Un middleware FastAPI propaga `correlation_id` por request:

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

### Niveles

| Nivel | Cuándo | Quién emite |
|-------|--------|-------------|
| `DEBUG` | Solo dev; instrumentación detallada | Decorator con `level="DEBUG"` |
| `INFO` | Eventos operativos (default) | Decorator |
| `WARNING` | Comportamiento degradado recuperable (retry, fallback) | Decorator con `level="WARNING"` |
| `ERROR` | Excepción no tratada que aborta la operación | Decorator (automático en `except`) |
| `CRITICAL` | Falla que afecta al servicio entero | Handler global |

`SUCCESS` y `TRACE` (de loguru) no se usan.

### Dónde aparece `logger` directamente

La regla inviolable (`lex-logging-decorator`) lista tres casos. Viven en tres módulos predecibles:

| Módulo | Rol |
|--------|-----|
| `app/shared/logging/setup.py` | Configura `loguru` en el boot |
| `app/shared/logging/decorator.py` | Implementa `@logged` |
| `app/infrastructure/http/exception_handlers.py` (o worker/Lambda) | Loguea excepciones no capturadas en el tope |

Cualquier otro archivo que importe `from loguru import logger` para llamar `logger.<level>` es violación.

### Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| `operation` | `domain.action` en snake_case | `transfer.create`, `ledger.post_entry` |
| Claves JSON | snake_case | `trace_id`, `correlation_id`, `duration_ms` |
| Captura de args | Default `True`; `False` en fronteras con payload libre | `capture_args=False` en router HTTP |
| Redacción | Por nombre de campo (sink) y por argumento (decorator) | `redact=("password", "card_number")` |
| Re-raise | Siempre | El decorator nunca engulle |

## Glossary

| Término | Definición |
|---------|------------|
| Sink | Destino del log en `loguru` |
| Operation | Identificador estable del evento; clave para búsqueda y dashboards |
| Outcome | Estado del evento: `enter`, `exit`, `error` |
| Redacción | Sustitución de valores sensibles por `[REDACTED]` |
| Correlation ID | UUID por request, propagado en logs y response headers |

## References

- [Loguru](https://loguru.readthedocs.io/) — [orjson](https://github.com/ijl/orjson)
- lex-logging-decorator (_foundation/quality) — ley agnóstica al lenguaje
- kata-python-logging-setup (engineering/backend) — procedimiento de configuración
- codex-python-observability (engineering/backend) — traces y métricas
- lex-python-security, lex-python-error-handling (engineering/backend)
