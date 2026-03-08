# Lexis: Conformidad RESTful en Endpoints HTTP

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — APIs REST

## Propósito

Garantizar estandarización en las respuestas y comportamientos de los endpoints HTTP de la plataforma Guardia, promoviendo interoperabilidad, rastreabilidad y claridad para consumidores internos y externos. La inconsistencia en códigos de estado, payloads, headers, paginación u ordenación rompe contratos e integraciones.

## Ley

> **Todo endpoint HTTP de la plataforma Guardia DEBE seguir las reglas de la especificación RESTful (códigos de estado, payloads de respuesta, headers, paginación y ordenación) definidas en el Hub y referenciadas en el Codex RESTful, salvo excepciones justificadas y documentadas en ADR.**

## Alcance

- **Se aplica a:** cualquier endpoint HTTP implementado en la plataforma Guardia (APIs públicas e internas).
- **Agentes vinculados:** todos los implementadores de APIs HTTP.
- **Excepciones:** solo cuando estén justificadas y documentadas en Architecture Decision Record (ADR).

## Consecuencias de Violación

1. **Interoperabilidad:** los consumidores no pueden asumir comportamiento estándar.
2. **Contrato:** la documentación (OAS) y la implementación divergen de la spec.
3. **Remediación:** alinear status, payload, headers y paginación a la spec o registrar ADR.

## Ejemplos

### Correcto

Endpoint que retorna 200/201/204/400/401/404/409/422/429/500 conforme a la tabla de status; payload con data/errors/pagination/debug conforme a la estructura estándar; headers Idempotency-Key, X-Grd-Trace-Id, etc. conforme a la spec; listados paginados con page_size, page_token, order_by, sort.

### Incorrecto

Uso de status fuera de la lista permitida; payload de éxito sin data o de error sin array errors; ausencia de X-Grd-Trace-Id; listado sin paginación cuando aplique.

## Validación Automatizada

- **Herramienta:** revisión de contrato OpenAPI y código; pruebas de contrato.
- **Momento:** revisión de PR y validación de API.
- **Métrica:** 0 endpoints fuera de la spec, salvo excepciones en ADR.

## Referencias

- codex-restful-apis (índice), codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting (engineering/platform)
