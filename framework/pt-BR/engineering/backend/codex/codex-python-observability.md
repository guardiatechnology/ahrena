# Codex: Observabilidade Python

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: traces e métricas em aplicações Python via OpenTelemetry e decorators

## Overview

Traces e métricas em backend Python. Logs ficam em `codex-python-logging`. Mesmo princípio: instrumentação por decorator, nunca inline. OpenTelemetry é a abstração — o código de produto não conhece o backend (Prometheus, Datadog, OTLP). Um único decorator `@observe` combina log + métrica + span quando faz sentido.

## Context

- **Domain:** telemetria (traces + metrics) em serviços Python — APIs, workers, jobs.
- **Target audience:** implementadores e agentes (warrior-apollo).
- **Update trigger:** evolução do stack OpenTelemetry, mudança de backend, novas convenções semânticas.

## Content

### Princípios

1. Instrumentação por decorator — `tracer.start_as_current_span`, `counter.add`, `histogram.record`, `span.set_attribute` não aparecem em corpos de funções de aplicação.
2. OpenTelemetry como abstração — backend trocável (Prometheus, Datadog, OTLP) sem alterar o código de produto; vendor lock-in restrito ao bootstrap.
3. Result Pattern como cidadão de primeira classe — quando a função retorna `Result[T, E]`, o decorator inspeciona `Ok`/`Err` e classifica `outcome`.
4. Métricas globais centralizadas — `fn_calls_total` e `fn_duration_seconds` cobrem qualquer função decorada; métricas de domínio são adicionais.
5. Métricas em endpoint dedicado — `/metrics` montado uma única vez, nunca acoplado a rotas de negócio.

### Stack

| Componente | Biblioteca | Propósito |
|------------|-----------|-----------|
| Tracing | `opentelemetry-api`, `opentelemetry-sdk` | Traces distribuídos |
| Métricas | `opentelemetry-sdk` + `opentelemetry-exporter-prometheus` | Portáveis (Prometheus, OTLP, Datadog) |
| Result Pattern | `result` (rustedpy/result) | `Ok`/`Err` para classificação de outcome |
| Exposição | `prometheus-client` | Endpoint `/metrics` ASGI |
| Auto-instrumentação | `opentelemetry-instrumentation-fastapi/asyncpg/logging` | Spans HTTP, BD e correlação |

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

`BatchSpanProcessor` em produção; `SimpleSpanProcessor` em testes. Endpoint OTLP via `OTEL_EXPORTER_OTLP_ENDPOINT`. Para Datadog, basta trocar reader/exporter — instrumentação não muda.

### Tipos de métricas

| Tipo | Quando usar | Exemplo |
|------|-------------|---------|
| `Counter` | Só cresce | `transactions_created_total` |
| `UpDownCounter` | Sobe e desce | `active_connections` |
| `Histogram` | Distribuição | `transaction_duration_seconds` |
| `ObservableGauge` | Amostrado periodicamente | `queue_depth` |

`Summary` (percentis no cliente) é evitado: histogramas com buckets bem escolhidos servem ao mesmo caso e agregam entre instâncias.

### Métricas globais

```python
# app/shared/observability/metrics.py
from opentelemetry import metrics

meter = metrics.get_meter("app.shared.observability")
calls_total = meter.create_counter("fn_calls_total", description="Chamadas a funções decoradas")
call_duration = meter.create_histogram("fn_duration_seconds", description="Duração", unit="s")
```

Definidas uma vez; importadas pelos decorators. `fn` e `status` são labels Prometheus — manter cardinalidade baixa (sem UUIDs).

### Decorators

Três decorators atendem a maioria dos casos. `@observe` é o default; os outros são especialização quando uma das três facetas (log, métrica, span) não se aplica.

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
    """Span + métrica + log no mesmo ponto. Default para casos de uso."""
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
    """Apenas métricas. Inspeciona Result quando presente; senão classifica por exceção."""
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
    return w  # versão async análoga; omitida por brevidade


def count(metric, attrs_fn):
    """Conta uma métrica de domínio com atributos derivados do retorno."""
    def deco(fn):
        @functools.wraps(fn)
        def w(*args, **kwargs):
            result = fn(*args, **kwargs); metric.add(1, attrs_fn(result)); return result
        return w
    return deco
```

Regras:
- `@observe` é default para casos de uso e operações de domínio. `Err` é registrado como `ERROR` no span — o trace reflete a falha mesmo sem exceção.
- Não combinar `@observe` com `@logged` ou `@track_metrics` na mesma função (eventos duplicados).
- `operation` segue `domain.action` (ex.: `transfer.create`).

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

`Ok` → `status=ok`; `Err` → `status=failure`; exceção → `status=error`. Corpo sem chamadas a `logger.*`, `counter.add`, `tracer.start_as_current_span`.

### Métricas de domínio

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

### Exposição no FastAPI

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

`/metrics` montado uma vez no app factory; protegido por rede (security group, ingress) — nunca exposto publicamente sem auth.

### Recomendação por cenário

| Decisão | Escolha |
|---------|---------|
| Instrumentação | `opentelemetry-sdk` (sempre — abstração trocável) |
| Self-hosted | Prometheus + Grafana |
| Stack já tem Datadog | Exporter Datadog OTLP ou SDK direto |
| Trocar backend no futuro | OpenTelemetry com OTLP exporter |
| Função pequena, custo de span alto | `@logged` + `@track_metrics` separados |

OpenTelemetry com Prometheus é o caminho mais portável em produto novo. Se o stack já tem Datadog, vai direto — não compensa a camada extra.

### Onde aparecem chamadas diretas

A mesma regra de `lex-logging-decorator` se aplica a métricas e spans:

| Módulo | Papel |
|--------|-------|
| `app/shared/observability/setup.py` | Bootstrap |
| `app/shared/observability/metrics.py` | Métricas globais |
| `app/shared/observability/decorators.py` | `@observe`, `@track_metrics`, `@count` |
| `app/shared/observability/auto_instrument.py` | Auto-instrumentação |
| `app/domain/<bc>/metrics.py` | Métricas do bounded context (apenas declaração) |
| Handlers globais de exceção | `span.record_exception` em handler top-level |

Qualquer outro arquivo chamando `tracer.start_as_current_span`, `counter.add`, `histogram.record`, `span.set_attribute` é violação.

### Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| `operation` | `domain.action` em snake_case | `transfer.create` |
| Nomes de métrica | `<substantivo>_<verbo_passado>_<unidade>` | `transfers_created_total`, `request_duration_seconds` |
| Labels | Cardinalidade baixa, sem PII, sem ID único | `currency`, `status` ✓ ; `entity_id` ✗ |
| Histogramas | Buckets explícitos quando default não cobre | latência `[0.005, 0.01, 0.025, ...]` |
| Result Pattern | Erros esperados como `Err`; exceções para invariantes violados | `return Err(TransferError.INVALID_AMOUNT)` |

## Glossary

| Termo | Definição |
|-------|-----------|
| Span | Unidade de trabalho dentro de um trace |
| Trace | Caminho ponta a ponta de um request, composto de spans |
| OTLP | Protocolo OpenTelemetry para exportar telemetria |
| Result | Tipo `Ok[T] | Err[E]` — substitui exceção por retorno |
| Outcome | `ok` (Ok), `failure` (Err), `error` (exceção) |
| Cardinalidade | Número de valores distintos de um label; alto = caro |

## References

- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) — [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [prometheus-client](https://github.com/prometheus/client_python) — [rustedpy/result](https://github.com/rustedpy/result)
- codex-python-logging (engineering/backend) — `@logged` + loguru
- lex-logging-decorator, lex-observability-required (_foundation/quality)
- codex-python-architecture (engineering/backend)
