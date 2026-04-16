# Lexis: La Observabilidad es Obligatoria

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todo nuevo endpoint HTTP, consumidor de eventos, job agendado o worker de larga ejecución en cualquier stack

## Propósito

El código sin observabilidad falla en silencio. Cuando un endpoint se vuelve lento, un consumidor de eventos pierde mensajes, o un job en background entra en loop, los ingenieros sin traces, métricas y logs estructurados quedan ciegos — los incidentes demoran horas en diagnosticarse, los post-mortems se vuelven conjeturas y el impacto al usuario se estima en vez de medirse. Esto ocurre incluso cuando `codex-python-observability` existe, porque la instrumentación se trata como opcional.

Esta Lexis existe para garantizar que **toda nueva superficie de runtime (endpoint, consumer, job) emita traces, métricas y logs estructurados desde el día uno**, que **los identificadores de correlación propaguen a través de fronteras de servicio** y que **el Gate 2 rechace implementaciones sin esos señales**.

## Ley

> **Todo nuevo endpoint HTTP, consumidor de eventos, job agendado o worker de larga ejecución DEBE emitir un trace distribuido (span), al menos una métrica de latencia y logs estructurados con correlation ID en los caminos de éxito y falla. Los servicios que se comunican vía HTTP o event bus DEBEN propagar el correlation ID (W3C Trace Context o equivalente). Los logs NO PUEDEN contener datos sensibles (PII, secretos, números de tarjeta completos).**

## Reglas

### 1. Tres señales por nueva superficie de runtime

Para cada nuevo endpoint, consumer o job, el agente **DEBE** instrumentar:

1. **Trace:** un span envolviendo la unidad de trabajo, con atributos (entity id, nombre de operación, outcome).
2. **Métrica:** al menos un histograma de latencia; contadores para errores/retries cuando aplica.
3. **Log:** estructurado (JSON) con `correlation_id`, `entity_type`, `entity_id`, `operation`, `outcome`.

Base neutra preferida: **OpenTelemetry SDK** (exporter OTLP); fallbacks específicos de plataforma (CloudWatch EMF, Datadog APM) aceptables cuando OTel no está disponible en el ambiente.

### 2. Propagación del correlation ID

El agente **DEBE**:

1. Aceptar header `traceparent` (W3C Trace Context) en HTTP inbound; generar si está ausente.
2. Propagar ese trace context en llamadas outbound (otros HTTP, publicación de eventos) vía header `traceparent` o metadata del envelope del evento.
3. Incluir `correlation_id` (trace id en minúsculas) en toda línea de log producida durante la unidad de trabajo.

### 3. Datos sensibles en logs

El agente **NO PUEDE** loguear:

- Números de tarjeta completos, CVVs, PINs.
- Contraseñas, tokens de API, cookies de sesión.
- IDs nacionales completos (RUT, DNI, CPF) — enmascarar o hashear (últimos 4 dígitos aceptables cuando se necesita identificador auditable).
- Cuerpos de email o contenido de mensajes cuando los datos del usuario no son esenciales para debug.

Las bibliotecas de logging DEBERÍAN aplicar filtros de redaction; los agentes DEBEN revisar los statements de log generados por fugas.

### 4. Los caminos de error también son observados

El agente **DEBE** garantizar:

1. Las excepciones no manejadas se propagan en el trace como status de error + excepción registrada.
2. Los outcomes de error esperados (fallas de validación, errores de negocio conocidos) emiten contadores y se loguean en `WARN` con `outcome=error` y código de error.
3. Los bloques `except: ...` que tragan errores sin al menos un log + métrica están prohibidos (refuerza `lex-python-error-handling`).

### 5. Enforcement en el Gate 2

`kata-quality-gate` Check 3 **DEBE** verificar que la instrumentación está presente para cada nueva superficie de runtime declarada en la tabla de componentes de la Fase 3. Heurística (dependiente del stack):

- Python: buscar `@trace`, `tracer.start_as_current_span`, `metric.observe`, uso de logger estructurado.
- Frontend (rutas de servidor): buscar middleware de tracing, inicialización de `sendBeacon`/APM SDK.
- Infraestructura: X-Ray / OTel integration configurada donde los servicios corren.

Ausencia = ❌ `Check 3 — lex-observability-required`.

## Alcance

- **Se aplica a:** todo componente listado como nuevo endpoint/consumer/job en `docs/issues/issue-{n}/03-architecture.md`.
- **Agentes vinculados:** todos los warriors que implementan código de runtime (Apollo, Hephaestus, Hera cuando ejecuta pruebas, etc.); verificado por `warrior-athena` en el Gate 2.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Incidentes a ciegas:** la mediana de tiempo-hasta-diagnóstico se infla de minutos a horas; el impacto al cliente escala antes de la detección.
2. **Ficción en el post-mortem:** sin logs y traces, las narrativas de causa raíz se infieren — frecuentemente equivocadas, llevando a incidentes recurrentes.
3. **Falla de compliance:** SOC 2 CC7 / ISO 27001 A.12.4 exigen explícitamente logging de actividad; las auditorías fallan.
4. **Remediación:** PR rechazado por el Gate 2 hasta agregar instrumentación; backport de instrumentación antes de la release.

## Validación Automatizada

- **Herramienta:**
  - Regla de lint / análisis estático escaneando llamadas de instrumentación en las superficies nuevas declaradas.
  - Request sintético en staging — verificar que el trace aparece en el backend de tracing.
  - Checks de redaction de log (regex para patrones de credencial en líneas de log muestreadas).
- **Momento:** Gate 2 (pre-PR); continuo en producción vía pipelines de log/métrica.
- **Métrica:** 100% de los nuevos endpoints/consumers con span + métrica + log estructurado; 0 eventos de fuga de datos sensibles.

## Referencias

- `codex-python-observability` — patrones OpenTelemetry para Python
- `kata-quality-gate` — enforce de esta Lexis en el Check 3
- `lex-python-error-handling` — los caminos de error también deben observarse
- `lex-mcp` — al usar MCP para auditoría, aplica el mismo correlation id
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
