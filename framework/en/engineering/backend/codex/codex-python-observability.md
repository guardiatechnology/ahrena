# Codex: Python Observability

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: observability patterns with OpenTelemetry, structured logging, and metrics

## Overview

This manual defines the observability patterns for Python backend applications. Observability is the ability to understand the internal state of a system from its external outputs: logs, traces, and metrics. Every service MUST be instrumented to enable debugging, performance analysis, and alerting in production.

## Context

- **Domain:** observability for Python applications using OpenTelemetry stack.
- **Target audience:** implementers and AI agents that instrument or maintain Python services.
- **Update trigger:** when OpenTelemetry patterns evolve or new instrumentation is adopted.

## Content

### Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Tracing | `opentelemetry-api`, `opentelemetry-sdk` | Distributed tracing |
| Auto-instrumentation | `opentelemetry-instrumentation-fastapi` | HTTP span creation |
| DB instrumentation | `opentelemetry-instrumentation-asyncpg` | Database span creation |
| Log instrumentation | `opentelemetry-instrumentation-logging` | Trace-log correlation |
| Export | `opentelemetry-exporter-otlp` | Export traces/metrics via OTLP |
| Structured logging | `structlog` or `logging` with JSON formatter | Machine-readable logs |

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

**Rules:**
- Set up tracing at application startup (`main.py` or app factory)
- Use `BatchSpanProcessor` for production; `SimpleSpanProcessor` for testing
- Service name from environment or configuration
- OTLP endpoint from environment variable (`OTEL_EXPORTER_OTLP_ENDPOINT`)

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

**Rules:**
- Instrument FastAPI for automatic HTTP span creation
- Instrument asyncpg for database query spans
- Instrument logging for trace-log correlation (trace_id in log records)

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

**Rules:**
- Add custom spans for business-critical operations
- Use semantic attributes (noun.property format)
- Set span status on errors
- Never include PII or secrets in span attributes

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

**Rules:**
- JSON format in production for machine parsing
- Include `trace_id` and `span_id` for log-trace correlation
- Log levels: DEBUG (development only), INFO (operational events), WARNING (recoverable issues), ERROR (failures requiring attention)
- Never log secrets, tokens, passwords, or PII
- Log at boundaries: incoming requests, outgoing calls, errors, business events

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

**Rules:**
- Use counters for events (requests, errors, transactions created)
- Use histograms for durations and sizes
- Metric names: `noun.verb` or `noun.property` in snake_case
- Export via OTLP alongside traces

## Glossary

| Term | Definition |
|------|------------|
| Span | A unit of work within a trace, with start/end time and attributes |
| Trace | End-to-end request path across services, composed of spans |
| OTLP | OpenTelemetry Protocol for exporting telemetry data |
| Correlation | Linking logs to traces via trace_id/span_id |

## References

- [OpenTelemetry Python documentation](https://opentelemetry.io/docs/languages/python/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- codex-python-architecture (engineering/backend)
