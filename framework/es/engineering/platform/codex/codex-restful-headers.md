# Codex: Headers HTTP en APIs RESTful

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — APIs REST — headers

## Visión General

Headers estándar y personalizados (X-Grd-*) para peticiones y respuestas HTTP de la plataforma Guardia. Incluye reglas para Idempotency-Key, Content-Digest, X-Grd-Debug y rastreo.

## Contexto

- **Dominio:** headers HTTP en APIs de la plataforma Guardia.
- **Público objetivo:** implementadores y consumidores de APIs.
- **Actualización:** cuando la especificación de headers en el Hub sea alterada.

## Contenido

### Headers estándar

| Header | Dirección | Obligatoriedad | Descripción |
|--------|-----------|----------------|-------------|
| Accept | Request | Opcional | Formato aceptado (ej.: application/vnd.guardia.v1+json) |
| Accept-Language | Request | Opcional | Idioma preferido |
| Content-Type | Request/Response | Opcional | Formato del contenido |
| Content-Language | Response | Opcional | Idioma de la respuesta |
| Cache-Control | Response | Opcional | Directivas de caché (public/private, max-age; no-store) |
| Link | Response | Opcional | Navegación (paginación rel first/previous/next/last; HATEOAS) |
| Idempotency-Key | Request/Response | Obligatorio en mutaciones | UUID; conforme codex-idempotency |
| Content-Digest | Response | En respuestas idempotentes | sha-256=&lt;hash&gt;; DEBE ser SHA-256 en hexadecimal con 64 caracteres; cuerpo de la petición DEBE normalizarse en JSON antes del cálculo; valor inválido → 400 ERR400_MISSING_OR_MALFORMED_HEADER, reason INVALID_CONTENT_DIGEST |
| Last-Modified | Response | En idempotencia | Fecha última modificación (RFC 7232) |
| Retry-After | Response | En 429 | Segundos para reintentar |

### Headers personalizados (X-Grd-*)

| Header | Dirección | Obligatoriedad | Descripción |
|--------|-----------|----------------|-------------|
| X-Grd-Debug | Request | Opcional | Valores permitidos: **true** o **false** (cualquier otro valor → 400 ERR400_MISSING_OR_MALFORMED_HEADER, reason INVALID_DEBUG_HEADER_VALUE); habilita objeto debug en la respuesta; en producción: restringir por alcance (ej.: usuario/tenant), ventana máx. 10 min, 10 req/min por cliente, intervalo mínimo 1 min entre activaciones, uso auditado |
| X-Grd-Trace-Id | Response | Obligatorio | UUID v7; en todas las respuestas; rastreo en todas las capas |
| X-Grd-Correlation-Id | Request/Response | Opcional | UUID; propagar si presente en la petición |

### Seguridad

- Headers de rastreo sin PII/secretos; validar por tenant y rate limit; sanitizar y limitar cantidad.

## Referencias

- RFC 9110, 9111, 7232; codex-idempotency
- [codex-restful-apis](codex-restful-apis.md) (índice)
