# Codex: Python Observability

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: traces and metrics in Python applications via OpenTelemetry and decorators

## Content

### Principles

1. Decorator-driven instrumentation — `tracer.start_as_current_span`, `counter.add`, `histogram.record`, `span.set_attribute` do not appear in application function bodies.
2. OpenTelemetry as abstraction — swappable backend (Prometheus, Datadog, OTLP) without touching product code; vendor lock-in restricted to the bootstrap.
3. Result Pattern as a first-class citizen — when the function returns `Result[T, E]`, the decorator inspects `Ok`/`Err` and classifies `outcome`.
4. Centralized global metrics — `fn_calls_total` and `fn_duration_seconds` cover any decorated function; domain metrics are additional.
5. Metrics on a dedicated endpoint — `/metrics` mounted once, never coupled to business routes.

### Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Tracing | `opentelemetry-api`, `opentelemetry-sdk` | Distributed traces |
| Metrics | `opentelemetry-sdk` + `opentelemetry-exporter-prometheus` | Portable (Prometheus, OTLP, Datadog) |
| Result Pattern | `result` (rustedpy/result) | `Ok`/`Err` for outcome classification |
| Exposure | `prometheus-client` | ASGI `/metrics` endpoint |
| Auto-instrumentation | `opentelemetry-instrumentation-fastapi/asyncpg/logging` | HTTP, DB, log correlation |

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

`BatchSpanProcessor` in production; `SimpleSpanProcessor` in tests. OTLP endpoint via `OTEL_EXPORTER_OTLP_ENDPOINT`. For Datadog, only the reader/exporter changes — instrumentation stays the same.

### Metric types

| Type | When to use | Example |
|------|-------------|---------|
| `Counter` | Only grows | `transactions_created_total` |
| `UpDownCounter` | Goes up and down | `active_connections` |
| `Histogram` | Distribution | `transaction_duration_seconds` |
| `ObservableGauge` | Periodically sampled | `queue_depth` |

`Summary` (client-side percentiles) is avoided: histograms with well-chosen buckets serve the same case and aggregate across instances.

### Global metrics

```python
# app/shared/observability/metrics.py
from opentelemetry import metrics

meter = metrics.get_meter("app.shared.observability")
calls_total = meter.create_counter("fn_calls_total", description="Calls to decorated functions")
call_duration = meter.create_histogram("fn_duration_seconds", description="Duration", unit="s")
```

Defined once; imported by decorators. `fn` and `status` are Prometheus labels — keep cardinality low (no UUIDs).

### Decorators

Three decorators cover most cases. `@observe` is the default; the others are specializations when one of the three facets (log, metric, span) does not apply.

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
    """Span + metric + log at one place. Default for use cases."""
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
    """Metrics only. Inspects Result when present; otherwise classifies by exception."""
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
    return w  # async version is analogous; omitted for brevity

def count(metric, attrs_fn):
    """Counts a domain metric with attributes derived from the return value."""
    def deco(fn):
        @functools.wraps(fn)
        def w(*args, **kwargs):
            result = fn(*args, **kwargs); metric.add(1, attrs_fn(result)); return result
        return w
    return deco
```

Rules:
- `@observe` is the default for use cases and domain operations. `Err` is recorded as `ERROR` on the span — the trace reflects the failure even without an exception.
- Do not combine `@observe` with `@logged` or `@track_metrics` on the same function (events would be duplicated).
- `operation` follows `domain.action` (e.g., `transfer.create`).

### Usage

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

`Ok` → `status=ok`; `Err` → `status=failure`; exception → `status=error`. Body free of `logger.*`, `counter.add`, `tracer.start_as_current_span`.

### Domain metrics

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

### Exposure on FastAPI

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

`/metrics` mounted once in the app factory; protected at network level (security group, ingress) — never publicly exposed without auth.

### Recommendation by scenario

| Decision | Choice |
|----------|--------|
| Instrumentation | `opentelemetry-sdk` (always — swappable abstraction) |
| Self-hosted | Prometheus + Grafana |
| Stack already has Datadog | Datadog OTLP exporter or SDK directly |
| Backend change in the future | OpenTelemetry with OTLP exporter |
| Small function, high span cost | `@logged` + `@track_metrics` separately |

OpenTelemetry with Prometheus is the most portable path in a new product. If the stack already has Datadog, go directly — the extra layer is not worth it.

### Where direct calls appear

The same rule from `lex-logging-decorator` applies to metrics and spans:

| Module | Role |
|--------|------|
| `app/shared/observability/setup.py` | Bootstrap |
| `app/shared/observability/metrics.py` | Global metrics |
| `app/shared/observability/decorators.py` | `@observe`, `@track_metrics`, `@count` |
| `app/shared/observability/auto_instrument.py` | Auto-instrumentation |
| `app/domain/<bc>/metrics.py` | Bounded-context metrics (declaration only) |
| Global exception handlers | `span.record_exception` in top-level handler |

Any other file calling `tracer.start_as_current_span`, `counter.add`, `histogram.record`, `span.set_attribute` is a violation.

### Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| `operation` | `domain.action` in snake_case | `transfer.create` |
| Metric names | `<noun>_<past_verb>_<unit>` | `transfers_created_total`, `request_duration_seconds` |
| Labels | Low cardinality, no PII, no unique IDs | `currency`, `status` ✓ ; `entity_id` ✗ |
| Histograms | Explicit buckets when default does not cover the case | latency `[0.005, 0.01, 0.025, ...]` |
| Result Pattern | Expected errors as `Err`; exceptions for invariant violations | `return Err(TransferError.INVALID_AMOUNT)` |
