# Codex: APIs RESTful de la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — APIs REST

## Visión General

Este Codex consolida las directrices para construcción, consumo y documentación de APIs RESTful en la plataforma Guardia. Las reglas están organizadas en módulos específicos; cada uno posee su propio artefato para consulta detallada. Las excepciones a la spec deben documentarse en ADR.

## Contexto

- **Dominio:** APIs HTTP de la plataforma Guardia (respuestas, headers, paginación, ordenación).
- **Público objetivo:** implementadores y consumidores de APIs.
- **Actualización:** cuando las especificaciones RESTful en el Hub sean alteradas.

## Módulos

| Módulo | Artefato | Contenido |
|--------|----------|-----------|
| Status Codes | [codex-restful-status-codes](codex-restful-status-codes.md) | Códigos HTTP permitidos (2xx, 3xx, 4xx, 5xx) y cuándo usar/no usar |
| Payload de Respuesta | [codex-restful-payload](codex-restful-payload.md) | Estructura data, pagination, errors, debug |
| Headers | [codex-restful-headers](codex-restful-headers.md) | Headers estándar y personalizados (X-Grd-*), Content-Digest, Idempotency-Key |
| Paginación | [codex-restful-pagination](codex-restful-pagination.md) | Parámetros, respuesta, tokens, errores conocidos |
| Ordenación | [codex-restful-sorting](codex-restful-sorting.md) | order_by, sort, índices, particionamiento |

## Referencias generales

- codex-entities, codex-idempotency, codex-error-handling
- RFC 9110 (HTTP Semantics), RFC 9111 (Caching), RFC 7232 (Conditional Requests), RFC 7807 (Problem Details)
