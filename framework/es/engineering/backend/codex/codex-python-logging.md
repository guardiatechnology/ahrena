# Codex: Logging Python con Loguru y Decorator

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: patrón de logging en aplicaciones Python

## Overview

Este manual define cómo las aplicaciones Python backend producen, formatean y correlacionan logs. Es la especialización Python de `lex-logging-decorator` (la regla agnóstica al lenguaje). El patrón consta de dos piezas que viven juntas: (1) `loguru` configurado una sola vez en el boot de la aplicación (sinks, formato JSON, nivel, integración con OpenTelemetry); (2) un decorator `@logged` que envuelve funciones y métodos y emite, automáticamente, eventos de entrada, salida, duración y excepción. Las llamadas `logger.info` y equivalentes no aparecen en el cuerpo de las funciones.

## Context

- **Domain:** logging operativo de servicios Python — APIs, workers, jobs y CLIs.
- **Target audience:** implementadores y agentes de IA que escriben o mantienen código Python (warrior-apollo).
- **Update trigger:** cuando el formato de log evoluciona, cuando se adoptan nuevos campos de correlación, cuando el decorator gana capacidades nuevas (sampling, redacción extra, eventos de dominio).

## Content

### Principios

1. **Configuración centralizada:** `loguru` se configura una sola vez en el boot de la aplicación. Ningún otro archivo redefine sinks, formato o nivel.
2. **Logging por decorator:** la instrumentación vive en la frontera de la función. El cuerpo de la función es regla de negocio, no traza de auditoría.
3. **Estructura JSON:** los logs son consumidos por máquinas (CloudWatch, Datadog, ELK). El texto libre es complemento, no clave.
4. **Correlación obligatoria:** `trace_id`, `span_id` y `correlation_id` se propagan vía `loguru.contextualize` y se inyectan en cada registro.
5. **Redacción en la frontera:** el decorator aplica allowlist/denylist de campos antes de serializar argumentos; PII y secretos nunca llegan al sink.
6. **El éxito es evento, no silencio:** toda ejecución de función decorada emite al menos `enter` y `exit` (o `error`); las fallas se loguean con `exception` y se relanzan.

### Stack

| Componente | Biblioteca | Propósito |
|------------|-----------|-----------|
| Logger | `loguru` | API única de logging; sinks, formateo, captura de excepción |
| Decorator | `app.shared.logging.decorator` (interno) | Instrumentación de entrada/salida/error con redacción |
| Correlación | `loguru.contextualize` + `opentelemetry-instrumentation-logging` | Propaga `trace_id`, `span_id`, `correlation_id` |
| Serialización | `orjson` (opcional) | Sink JSON rápido para producción |

`logging` (stdlib), `structlog` y `print` no forman parte del stack permitido en código de aplicación.

### Configuración de Boot

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

**Reglas:**

- `setup_logging` se llama una vez en el entrypoint (`main.py`, `app.py`, `lambda_handler.py`).
- `backtrace=False` y `diagnose=False` en producción: los tracebacks de `loguru` pueden exponer variables con PII.
- El sink stdout sirve para dev local; el sink JSON (`json_sink`) es el canal real en producción.
- Nivel default `INFO`; `DEBUG` solo vía variable de entorno en ambientes no-prod.

### Sink JSON

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

**Reglas:**

- Redacción aplicada antes de la serialización. El equipo define un allowlist de campos seguros; lo que no esté en el allowlist se trata como sensible por defecto para campos cuyos nombres aparezcan en `DENY`.
- Nada de tracebacks completos en JSON: solo tipo y mensaje; el traceback completo va al trace vía `span.record_exception`.
- `print` aparece **solo** dentro de este sink — es la frontera de salida del logger, no logging de aplicación.

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

**Reglas:**

- El decorator soporta funciones sync y async. Nunca dos versiones manuales — `@logged` decide.
- `operation` es obligatorio y usa el formato `domain.action` (ej.: `transfer.create`, `reconciliation.run`).
- `capture_args=True` por defecto; `False` en fronteras con input no confiable (ej.: webhook payload).
- `redact=("password", "card_number", ...)` aplica redacción por nombre de argumento, complementando el denylist global del sink.
- El decorator NO engulle excepciones: loguea `error` y relanza. El manejo de error es responsabilidad del handler global (lex-python-error-handling).

### Uso

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

### Correlación trace ↔ log

`opentelemetry-instrumentation-logging` inyecta `otelTraceID` y `otelSpanID` en cada record. Un middleware de FastAPI propaga el `correlation_id` por request:

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

Cada record lleva `correlation_id` automáticamente — el decorator no necesita propagarlo a mano.

### Niveles y cuándo usar

| Nivel | Cuándo emitir | Quién emite |
|-------|---------------|-------------|
| `DEBUG` | Solo en desarrollo; instrumentación detallada de algoritmos | Decorator con `level="DEBUG"` |
| `INFO` | Eventos operativos relevantes (entrada/salida de caso de uso, request HTTP atendido) | Decorator (default) |
| `WARNING` | Comportamiento degradado recuperable (retry, fallback, circuito abierto) | Decorator con `level="WARNING"` en fronteras de retry |
| `ERROR` | Excepción no tratada que aborta la operación | Decorator (automático en `except`) |
| `CRITICAL` | Falla que afecta al servicio entero (BD inalcanzable, dependencia crítica caída) | Handler global en el entrypoint |

`SUCCESS` y `TRACE` (de loguru) no se usan.

### Dónde aparece `logger` directamente (excepciones permitidas)

La regla inviolable (lex-logging-decorator) lista tres casos. Viven físicamente en tres módulos predecibles:

| Módulo | Rol |
|--------|-----|
| `app/shared/logging/setup.py` | Configura el `loguru` en el boot |
| `app/shared/logging/decorator.py` | Implementa `@logged` |
| `app/infrastructure/http/exception_handlers.py` (o equivalente en workers/Lambda) | Loguea excepciones no capturadas en el tope |

Cualquier otro archivo que importe `from loguru import logger` para llamar `logger.<level>` es una violación.

### Patrones y convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| Formato de `operation` | `domain.action` en snake_case | `transfer.create`, `ledger.post_entry` |
| Estructura JSON | snake_case en todas las claves | `trace_id`, `correlation_id`, `duration_ms` |
| Captura de argumentos | Habilitada por defecto; deshabilitada en fronteras con payload libre | `capture_args=False` en el router HTTP |
| Redacción | Por nombre de campo (sink global) y por argumento (decorator) | `redact=("password", "card_number")` |
| Re-lanzamiento de excepciones | Siempre | El decorator nunca engulle |

## Glossary

| Término | Definición |
|---------|------------|
| Sink | Destino del log en `loguru` (stdout, archivo, función custom) |
| Operation | Identificador estable del evento de log; clave para búsqueda y dashboards |
| Outcome | Estado del evento: `enter`, `exit`, `error` |
| Redacción | Sustitución de valores sensibles por `[REDACTED]` antes de la serialización |
| Correlation ID | UUID por request, propagado en logs y en response headers |

## References

- [Loguru documentation](https://loguru.readthedocs.io/)
- [orjson](https://github.com/ijl/orjson) — serializador JSON usado en el sink
- lex-logging-decorator (_foundation/quality) — ley agnóstica al lenguaje que hace el patrón obligatorio
- kata-python-logging-setup (engineering/backend) — procedimiento de configuración
- codex-python-observability (engineering/backend) — traces y métricas vía OpenTelemetry
- lex-python-security (engineering/backend) — prohibición de loguear secretos y PII
- lex-python-error-handling (engineering/backend) — excepciones y re-raise
