# Codex: Observabilidade Python

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: padrões de observabilidade com OpenTelemetry, logging estruturado e métricas

## Overview

Este manual define os padrões de observabilidade para aplicações Python backend. Observabilidade é a capacidade de entender o estado interno de um sistema a partir de suas saídas externas: logs, traces e métricas. Todo serviço DEVE ser instrumentado para possibilitar debugging, análise de performance e alertas em produção.

## Context

- **Domain:** observabilidade para aplicações Python usando o stack OpenTelemetry.
- **Target audience:** implementadores e agentes de IA que instrumentam ou mantêm serviços Python.
- **Update trigger:** quando os padrões OpenTelemetry evoluem ou nova instrumentação é adotada.

## Content

### Stack

| Componente | Biblioteca | Propósito |
|------------|-----------|-----------|
| Tracing | `opentelemetry-api`, `opentelemetry-sdk` | Tracing distribuído |
| Auto-instrumentação | `opentelemetry-instrumentation-fastapi` | Criação de spans HTTP |
| Instrumentação de BD | `opentelemetry-instrumentation-asyncpg` | Criação de spans de banco de dados |
| Instrumentação de log | `opentelemetry-instrumentation-logging` | Correlação trace-log |
| Exportação | `opentelemetry-exporter-otlp` | Exportar traces/métricas via OTLP |
| Logging estruturado | `structlog` ou `logging` com JSON formatter | Logs legíveis por máquina |

### Tracing Setup

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource


def setup_tracing(service_name: str) -> None:
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
```

**Regras:**
- Configurar tracing na inicialização da aplicação (`main.py` ou app factory)
- Usar `BatchSpanProcessor` para produção; `SimpleSpanProcessor` para testes
- Nome do serviço a partir de variável de ambiente ou configuração
- Endpoint OTLP a partir de variável de ambiente (`OTEL_EXPORTER_OTLP_ENDPOINT`)

### Auto-Instrumentation

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor


def setup_instrumentation(app: FastAPI) -> None:
    FastAPIInstrumentor.instrument_app(app)
    AsyncPGInstrumentor().instrument()
    LoggingInstrumentor().instrument(set_logging_format=True)
```

**Regras:**
- Instrumentar FastAPI para criação automática de spans HTTP
- Instrumentar asyncpg para spans de queries de banco de dados
- Instrumentar logging para correlação trace-log (trace_id nos registros de log)

### Custom Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


async def process_payment(payment_id: UUID) -> PaymentResult:
    with tracer.start_as_current_span(
        "process_payment",
        attributes={"payment.id": str(payment_id)},
    ) as span:
        result = await gateway.charge(payment_id)
        span.set_attribute("payment.status", result.status.value)
        if result.failed:
            span.set_status(trace.StatusCode.ERROR, result.error_message)
        return result
```

**Regras:**
- Adicionar spans customizados para operações críticas do negócio
- Usar atributos semânticos (formato substantivo.propriedade)
- Definir status do span em erros
- Nunca incluir PII ou segredos em atributos de span

### Structured Logging

```python
import logging
import json


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "otelTraceID", ""),
            "span_id": getattr(record, "otelSpanID", ""),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)
```

**Regras:**
- Formato JSON em produção para parsing por máquina
- Incluir `trace_id` e `span_id` para correlação log-trace
- Níveis de log: DEBUG (somente desenvolvimento), INFO (eventos operacionais), WARNING (problemas recuperáveis), ERROR (falhas que requerem atenção)
- Nunca logar segredos, tokens, senhas ou PII
- Logar nas fronteiras: requests recebidos, chamadas externas, erros, eventos de negócio

### Metrics

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

transaction_counter = meter.create_counter(
    "transactions.created",
    description="Number of transactions created",
)

processing_duration = meter.create_histogram(
    "transactions.processing_duration_ms",
    description="Transaction processing duration in milliseconds",
)
```

**Regras:**
- Usar contadores para eventos (requests, erros, transações criadas)
- Usar histogramas para durações e tamanhos
- Nomes de métricas: `substantivo.verbo` ou `substantivo.propriedade` em snake_case
- Exportar via OTLP junto com traces

## Glossary

| Termo | Definição |
|-------|-----------|
| Span | Uma unidade de trabalho dentro de um trace, com tempo de início/fim e atributos |
| Trace | Caminho de request de ponta a ponta entre serviços, composto de spans |
| OTLP | Protocolo OpenTelemetry para exportar dados de telemetria |
| Correlation | Vinculação de logs a traces via trace_id/span_id |

## References

- [OpenTelemetry Python documentation](https://opentelemetry.io/docs/languages/python/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- codex-python-architecture (engineering/backend)
