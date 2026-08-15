# Codex: Observabilidad en Python

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: traces y métricas en aplicaciones Python vía OpenTelemetry y decorators

## Overview

Traces y métricas en backend Python. Los logs viven en `codex-python-logging`. Mismo principio: instrumentación por decorator, nunca inline. OpenTelemetry es la abstracción — el código de producto no conoce el backend (Prometheus, Datadog, OTLP). Un único decorator `@observe` combina log + métrica + span cuando tiene sentido.

## Context

- **Domain:** telemetría (traces + métricas) en servicios Python — APIs, workers, jobs.
- **Target audience:** implementadores y agentes (warrior-apollo).
- **Update trigger:** evolución del stack OpenTelemetry, cambio de backend, nuevas convenciones semánticas.

## Content

### Principios

1. Instrumentación por decorator — `tracer.start_as_current_span`, `counter.add`, `histogram.record`, `span.set_attribute` no aparecen en cuerpos de funciones de aplicación.
2. OpenTelemetry como abstracción — backend intercambiable (Prometheus, Datadog, OTLP) sin alterar el código de producto; vendor lock-in restringido al bootstrap.
3. Result Pattern como ciudadano de primera clase — cuando la función retorna `Result[T, E]`, el decorator inspecciona `Ok`/`Err` y clasifica `outcome`.
4. Métricas globales centralizadas — `fn_calls_total` y `fn_duration_seconds` cubren cualquier función decorada; las métricas de dominio son adicionales.
5. Métricas en endpoint dedicado — `/metrics` montado una sola vez, nunca acoplado a rutas de negocio.

### Stack

| Componente | Biblioteca | Propósito |
|------------|-----------|-----------|
| Tracing | `opentelemetry-api`, `opentelemetry-sdk` | Traces distribuidos |
| Métricas | `opentelemetry-sdk` + `opentelemetry-exporter-prometheus` | Portables (Prometheus, OTLP, Datadog) |
| Result Pattern | `result` (rustedpy/result) | `Ok`/`Err` para clasificación de outcome |
| Exposición | `prometheus-client` | Endpoint `/metrics` ASGI |
| Auto-instrumentación | `opentelemetry-instrumentation-fastapi/asyncpg/logging` | Spans HTTP, BD y correlación |

### Bootstrap

```python
# app/shared/observability/setup.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import Resource


def setup_observability(service_name: str) -> None:
    resource = Resource.create({"service.name": service_name})
    tp = TracerProvider(resource=resource)
    tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tp)
    metrics.set_meter_provider(MeterProvider(metric_readers=[PrometheusMetricReader()]))
```

```python
# app/shared/observability/auto_instrument.py
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor


def instrument(app) -> None:
    FastAPIInstrumentor.instrument_app(app)
    AsyncPGInstrumentor().instrument()
    LoggingInstrumentor().instrument(set_logging_format=True)
```

`BatchSpanProcessor` en producción; `SimpleSpanProcessor` en tests. Endpoint OTLP vía `OTEL_EXPORTER_OTLP_ENDPOINT`. Para Datadog, solo cambia el reader/exporter — la instrumentación se mantiene.

### Tipos de métricas

| Tipo | Cuándo usar | Ejemplo |
|------|-------------|---------|
| `Counter` | Solo crece | `transactions_created_total` |
| `UpDownCounter` | Sube y baja | `active_connections` |
| `Histogram` | Distribución | `transaction_duration_seconds` |
| `ObservableGauge` | Muestreado periódicamente | `queue_depth` |

`Summary` (percentiles del lado cliente) se evita: histogramas con buckets bien elegidos sirven al mismo caso y agregan entre instancias.

### Métricas globales

```python
# app/shared/observability/metrics.py
from opentelemetry import metrics

meter = metrics.get_meter("app.shared.observability")
calls_total = meter.create_counter("fn_calls_total", description="Llamadas a funciones decoradas")
call_duration = meter.create_histogram("fn_duration_seconds", description="Duración", unit="s")
```

Definidas una vez; importadas por los decorators. `fn` y `status` son labels Prometheus — mantener cardinalidad baja (sin UUIDs).

### Decorators

Tres decorators atienden la mayoría de los casos. `@observe` es el default; los otros son especialización cuando una de las tres facetas (log, métrica, span) no aplica.

```python
# app/shared/observability/decorators.py
import asyncio, functools, time
from typing import Any, Callable, ParamSpec, TypeVar
from loguru import logger
from opentelemetry import trace
from result import Result, Ok
from app.shared.observability.metrics import calls_total, call_duration

P = ParamSpec("P"); R = TypeVar("R")
tracer = trace.get_tracer("app.shared.observability")


def _classify(result: Any, exc: BaseException | None) -> str:
    if exc is not None:
        return "error"
    if isinstance(result, Result) and not isinstance(result, Ok):
        return "failure"
    return "ok"


def _record(operation, span, t0, result, exc):
    dur = (time.perf_counter() - t0) * 1000
    attrs = {"fn": operation}
    if exc is not None:
        span.set_status(trace.StatusCode.ERROR, str(exc)); span.record_exception(exc)
        status = "error"
    else:
        status = _classify(result, None)
        if status == "failure":
            span.set_status(trace.StatusCode.ERROR, "result.err")
    calls_total.add(1, {**attrs, "status": status})
    call_duration.record(dur / 1000, attrs)
    with logger.contextualize(operation=operation, outcome=status, duration_ms=dur):
        if exc is not None:
            logger.opt(exception=True).error("{} error", operation)
        else:
            logger.info("{} {}", operation, status)


def observe(operation: str) -> Callable:
    """Span + métrica + log en el mismo punto. Default para casos de uso."""
    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        async def aw(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = time.perf_counter()
            with tracer.start_as_current_span(operation) as span, \
                 logger.contextualize(operation=operation, outcome="enter"):
                logger.info("{} enter", operation)
                try:
                    result = await fn(*args, **kwargs)
                except Exception as exc:
                    _record(operation, span, t0, None, exc); raise
                _record(operation, span, t0, result, None); return result

        @functools.wraps(fn)
        def sw(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = time.perf_counter()
            with tracer.start_as_current_span(operation) as span, \
                 logger.contextualize(operation=operation, outcome="enter"):
                logger.info("{} enter", operation)
                try:
                    result = fn(*args, **kwargs)
                except Exception as exc:
                    _record(operation, span, t0, None, exc); raise
                _record(operation, span, t0, result, None); return result

        return aw if asyncio.iscoroutinefunction(fn) else sw  # type: ignore[return-value]
    return deco


def track_metrics(fn: Callable[P, R]) -> Callable[P, R]:
    """Solo métricas. Inspecciona Result cuando está presente; si no, clasifica por excepción."""
    @functools.wraps(fn)
    def w(*args, **kwargs):
        t0 = time.perf_counter(); attrs = {"fn": fn.__name__}
        try:
            result = fn(*args, **kwargs)
        except Exception:
            calls_total.add(1, {**attrs, "status": "error"})
            call_duration.record(time.perf_counter() - t0, attrs); raise
        status = _classify(result, None)
        calls_total.add(1, {**attrs, "status": status})
        call_duration.record(time.perf_counter() - t0, attrs)
        return result
    return w  # versión async análoga; omitida por brevedad


def count(metric, attrs_fn):
    """Cuenta una métrica de dominio con atributos derivados del retorno."""
    def deco(fn):
        @functools.wraps(fn)
        def w(*args, **kwargs):
            result = fn(*args, **kwargs); metric.add(1, attrs_fn(result)); return result
        return w
    return deco
```

Reglas:
- `@observe` es el default para casos de uso y operaciones de dominio. `Err` se registra como `ERROR` en el span — el trace refleja la falla incluso sin excepción.
- No combinar `@observe` con `@logged` o `@track_metrics` en la misma función (eventos duplicados).
- `operation` sigue `domain.action` (ej.: `transfer.create`).

### Uso

```python
from result import Ok, Err, Result
from app.shared.observability import observe


class CreateTransferUseCase:
    @observe(operation="transfer.create")
    async def execute(self, source_id, target_id, amount) -> Result[Transfer, TransferError]:
        if amount <= 0:
            return Err(TransferError.INVALID_AMOUNT)
        transfer = await self._repository.create(source_id, target_id, amount)
        return Ok(transfer)
```

`Ok` → `status=ok`; `Err` → `status=failure`; excepción → `status=error`. Cuerpo sin llamadas a `logger.*`, `counter.add`, `tracer.start_as_current_span`.

### Métricas de dominio

```python
# app/domain/transfers/metrics.py
from opentelemetry import metrics
_meter = metrics.get_meter("app.domain.transfers")
transfers_created_total = _meter.create_counter("transfers_created_total")
```

```python
@observe(operation="transfer.create")
@count(transfers_created_total, lambda r: {"currency": r.unwrap().currency} if r.is_ok() else {})
async def execute(...): ...
```

### Exposición en FastAPI

```python
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from app.shared.logging import setup_logging
from app.shared.observability import setup_observability, instrument


def create_app() -> FastAPI:
    setup_logging("transfer-api")
    setup_observability("transfer-api")
    app = FastAPI()
    instrument(app)
    app.mount("/metrics", make_asgi_app())
    return app
```

`/metrics` se monta una sola vez en el app factory; protegido a nivel de red (security group, ingress) — nunca expuesto públicamente sin auth.

### Recomendación por escenario

| Decisión | Elección |
|----------|----------|
| Instrumentación | `opentelemetry-sdk` (siempre — abstracción intercambiable) |
| Self-hosted | Prometheus + Grafana |
| Stack ya tiene Datadog | Exporter Datadog OTLP o SDK directo |
| Cambiar backend en el futuro | OpenTelemetry con OTLP exporter |
| Función pequeña, costo de span alto | `@logged` + `@track_metrics` por separado |

OpenTelemetry con Prometheus es el camino más portable en producto nuevo. Si el stack ya tiene Datadog, ir directo — la capa extra no compensa.

### Dónde aparecen llamadas directas

La misma regla de `lex-logging-decorator` aplica a métricas y spans:

| Módulo | Rol |
|--------|-----|
| `app/shared/observability/setup.py` | Bootstrap |
| `app/shared/observability/metrics.py` | Métricas globales |
| `app/shared/observability/decorators.py` | `@observe`, `@track_metrics`, `@count` |
| `app/shared/observability/auto_instrument.py` | Auto-instrumentación |
| `app/domain/<bc>/metrics.py` | Métricas del bounded context (solo declaración) |
| Handlers globales de excepción | `span.record_exception` en handler top-level |

Cualquier otro archivo que llame `tracer.start_as_current_span`, `counter.add`, `histogram.record`, `span.set_attribute` es violación.

### Convenciones

| Aspecto | Estándar | Ejemplo |
|---------|----------|---------|
| `operation` | `domain.action` en snake_case | `transfer.create` |
| Nombres de métrica | `<sustantivo>_<verbo_pasado>_<unidad>` | `transfers_created_total`, `request_duration_seconds` |
| Labels | Cardinalidad baja, sin PII, sin ID único | `currency`, `status` ✓ ; `entity_id` ✗ |
| Histogramas | Buckets explícitos cuando el default no cubre | latencia `[0.005, 0.01, 0.025, ...]` |
| Result Pattern | Errores esperados como `Err`; excepciones para invariantes violados | `return Err(TransferError.INVALID_AMOUNT)` |

## Glossary

| Término | Definición |
|---------|------------|
| Span | Unidad de trabajo dentro de un trace |
| Trace | Camino punta a punta de un request, compuesto por spans |
| OTLP | Protocolo OpenTelemetry para exportar telemetría |
| Result | Tipo `Ok[T] | Err[E]` — sustituye excepción por retorno |
| Outcome | `ok` (Ok), `failure` (Err), `error` (excepción) |
| Cardinalidad | Número de valores distintos para un label; alto = costoso |

## References

- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) — [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [prometheus-client](https://github.com/prometheus/client_python) — [rustedpy/result](https://github.com/rustedpy/result)
- codex-python-logging (engineering/backend) — `@logged` + loguru
- lex-logging-decorator, lex-observability-required (_foundation/quality)
- codex-python-architecture (engineering/backend)
