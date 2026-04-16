# Codex: Observabilidad en Python

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: patrones de observabilidad con OpenTelemetry, logging estructurado y métricas

## Visión General

Este manual define los patrones de observabilidad para aplicaciones Python de backend. La observabilidad es la capacidad de entender el estado interno de un sistema a partir de sus salidas externas: logs, trazas y métricas. Todo servicio DEBE estar instrumentado para permitir depuración, análisis de rendimiento y alertas en producción.

## Contexto

- **Dominio:** observabilidad para aplicaciones Python usando el stack OpenTelemetry.
- **Audiencia objetivo:** implementadores y agentes de IA que instrumentan o mantienen servicios Python.
- **Disparador de actualización:** cuando los patrones OpenTelemetry evolucionan o se adopta nueva instrumentación.

## Contenido

### Stack

| Componente | Librería | Propósito |
|------------|---------|---------|
| Trazabilidad | `opentelemetry-api`, `opentelemetry-sdk` | Trazabilidad distribuida |
| Auto-instrumentación | `opentelemetry-instrumentation-fastapi` | Creación de spans HTTP |
| Instrumentación de BD | `opentelemetry-instrumentation-asyncpg` | Creación de spans de base de datos |
| Instrumentación de logs | `opentelemetry-instrumentation-logging` | Correlación traza-log |
| Exportación | `opentelemetry-exporter-otlp` | Exportar trazas/métricas vía OTLP |
| Logging estructurado | `structlog` o `logging` con formateador JSON | Logs legibles por máquina |

### Configuración de Trazabilidad

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

**Reglas:**
- Configurar la trazabilidad al inicio de la aplicación (`main.py` o fábrica de app)
- Usar `BatchSpanProcessor` para producción; `SimpleSpanProcessor` para testing
- Nombre del servicio desde entorno o configuración
- Endpoint OTLP desde variable de entorno (`OTEL_EXPORTER_OTLP_ENDPOINT`)

### Auto-Instrumentación

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor


def setup_instrumentation(app: FastAPI) -> None:
    FastAPIInstrumentor.instrument_app(app)
    AsyncPGInstrumentor().instrument()
    LoggingInstrumentor().instrument(set_logging_format=True)
```

**Reglas:**
- Instrumentar FastAPI para creación automática de spans HTTP
- Instrumentar asyncpg para spans de consultas a la base de datos
- Instrumentar logging para correlación traza-log (trace_id en registros de log)

### Spans Personalizados

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

**Reglas:**
- Agregar spans personalizados para operaciones críticas del negocio
- Usar atributos semánticos (formato sustantivo.propiedad)
- Establecer el estado del span en caso de errores
- Nunca incluir PII ni secretos en los atributos de span

### Logging Estructurado

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

**Reglas:**
- Formato JSON en producción para parsing por máquina
- Incluir `trace_id` y `span_id` para correlación log-traza
- Niveles de log: DEBUG (solo desarrollo), INFO (eventos operacionales), WARNING (problemas recuperables), ERROR (fallos que requieren atención)
- Nunca registrar secretos, tokens, contraseñas ni PII
- Registrar en los límites: requests entrantes, llamadas salientes, errores, eventos de negocio

### Métricas

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

**Reglas:**
- Usar contadores para eventos (requests, errores, transacciones creadas)
- Usar histogramas para duraciones y tamaños
- Nombres de métricas: `sustantivo.verbo` o `sustantivo.propiedad` en snake_case
- Exportar vía OTLP junto con las trazas

## Glosario

| Término | Definición |
|---------|------------|
| Span | Unidad de trabajo dentro de una traza, con tiempo de inicio/fin y atributos |
| Trace | Camino de un request de extremo a extremo entre servicios, compuesto de spans |
| OTLP | Protocolo OpenTelemetry para exportar datos de telemetría |
| Correlation | Vinculación de logs con trazas mediante trace_id/span_id |

## Referencias

- [Documentación de OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [Convenciones Semánticas de OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/)
- codex-python-architecture (engineering/backend)
