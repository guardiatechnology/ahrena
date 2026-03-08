# Codex: APIs RESTful de la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — APIs REST

## Visión General

Este Codex consolida las directrices para construcción, consumo y documentación de APIs RESTful en la plataforma Guardia. Cubre códigos de estado, payloads de respuesta, headers, paginación y ordenación. Las excepciones a la spec deben documentarse en ADR.

**Referencias Hub:** [RESTful](https://hub.guardia.finance/docs/specifications/restful/) | [Status Codes](https://hub.guardia.finance/docs/specifications/restful/http-status-code/) | [Payload](https://hub.guardia.finance/docs/specifications/restful/http-response-payloads/) | [Headers](https://hub.guardia.finance/docs/specifications/restful/http-headers/) | [Paginación](https://hub.guardia.finance/docs/specifications/restful/http-pagination/) | [Ordenación](https://hub.guardia.finance/docs/specifications/restful/http-sorting/)

## Contexto

- **Dominio:** APIs HTTP de la plataforma Guardia (respuestas, headers, paginación, ordenación).
- **Público objetivo:** implementadores y consumidores de APIs.
- **Actualización:** cuando las especificaciones RESTful en el Hub sean alteradas.

---

## Módulo 1: Status Codes

Códigos de estado permitidos y reglas de uso. Los códigos utilizados en cada endpoint DEBEN constar en el contrato OAS. Estándar mínimo para cualquier API RESTful de la Guardia.

### 2xx — Éxito

| Código | Status | Métodos | Cuándo usar | Cuándo no usar |
|--------|--------|---------|-------------|----------------|
| 200 | OK | GET, POST, PUT, PATCH | Operación exitosa con datos; listado vacío procesado con éxito | Recurso nuevo creado (use 201); procesamiento pendiente (use 202); sin contenido (use 204) |
| 201 | Created | POST, PUT | Recurso nuevo creado | Recurso ya existía/actualizado; creación aún no concluida (use 202) |
| 202 | Accepted | POST, PUT, PATCH | Aceptado; procesamiento asíncrono | Resultado ya disponible |
| 204 | No Content | DELETE, PUT, PATCH | Éxito sin cuerpo | Cuando hay contenido a retornar |

### 3xx — Redirección

| Código | Status | Cuándo usar | Cuándo no usar |
|--------|--------|-------------|----------------|
| 301 | Moved Permanently | Recurso movido permanentemente; descontinuación de ruta | Cambio temporal (use 307) |
| 304 | Not Modified | Recurso sin cambios (caché, If-Modified-Since/ETag) | Contenido alterado (use 200) |
| 307 | Temporary Redirect | Recurso temporalmente en otra URL; método y cuerpo preservados | Cambio permanente (use 301); nunca convertir método a GET |

### 4xx — Error del cliente

| Código | Status | Cuándo usar | Cuándo no usar |
|--------|--------|-------------|----------------|
| 400 | Bad Request | Petición malformada o inválida | Datos correctos pero semántica inválida (use 422) |
| 401 | Unauthorized | Autenticación ausente o token inválido | Autenticado sin permiso (use 403) |
| 402 | Payment Required | Acceso condicionado a pago/suscripción | Problema de permiso (use 403) |
| 403 | Forbidden | Autenticado pero sin autorización para el recurso | No autenticado (use 401) |
| 404 | Not Found | Recurso inexistente | Recurso existe pero acceso restringido (use 403) |
| 408 | Request Timeout | Cliente tardó en completar la petición | Timeout entre servidores (use 504) |
| 409 | Conflict | Conflicto con estado actual (duplicidad, versión) | Error de validación (use 400/422) |
| 422 | Unprocessable Entity | Datos sintácticamente correctos, semánticamente inválidos | Formato o propiedades faltantes (use 400) |
| 429 | Too Many Requests | Límite de peticiones excedido | Error no relacionado con rate limit |

### 5xx — Error del servidor

| Código | Status | Cuándo usar | Cuándo no usar |
|--------|--------|-------------|----------------|
| 500 | Internal Server Error | Fallo inesperado o excepción no tratada | Error previsible/tratable por el cliente |
| 501 | Not Implemented | Método válido no soportado; funcionalidad no implementada | Fallo al procesar (use 500) |
| 502 | Bad Gateway | Respuesta inválida de otro servidor | Error en el propio servicio (use 500) |
| 503 | Service Unavailable | Servicio temporalmente no disponible | Servicio activo con fallo interno (use 500) |
| 504 | Gateway Timeout | Sin respuesta a tiempo de otro servidor | Timeout cliente→servidor (use 408) |

**Referencias:** RFC 9110; MDN.

---

## Módulo 2: Payload de Respuesta

Estructura unificada para éxito y error. Aplicable a todas las peticiones HTTP de la plataforma.

### Estructura estándar

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| data | object \| array | Datos cuando 2xx; objeto para entidad única, array para lista; ausente en 4xx/5xx |
| pagination | object | Presente solo en recurso paginado (2xx); estructura abajo; ausente en error |
| errors | array | Lista de errores cuando 4xx/5xx; cada ítem: code, reason, message (conforme codex-error-handling); ausente en 2xx |
| debug | object | Solo si header X-Grd-Debug: true; trace_id, correlation_id, instance, timestamp, duration, memory, query, params, internal_ip, external_ip; nunca datos sensibles |

### Éxito

- `data` con entidad(es); incluir entity_id, external_entity_id, entity_type conforme codex-entities cuando sea entidad.
- Con paginación: `data` array + `pagination` (page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token).

### Error

- `errors`: array de { code, reason, message }; code conforme Tratamiento de Errores; message orientada al desarrollador, no al usuario final.

### Debug

- Incluir solo con X-Grd-Debug: true; campos de rastreo (trace_id, correlation_id, instance, timestamp, duration, memory, etc.).

**Referencias:** codex-entities, codex-error-handling; RFC 7807.

---

## Módulo 3: Headers

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
| Content-Digest | Response | En respuestas idempotentes | sha-256=&lt;hash&gt; 64 chars hex; conforme idempotencia |
| Last-Modified | Response | En idempotencia | Fecha última modificación (RFC 7232) |
| Retry-After | Response | En 429 | Segundos para reintentar |

### Headers personalizados (X-Grd-*)

| Header | Dirección | Obligatoriedad | Descripción |
|--------|-----------|----------------|-------------|
| X-Grd-Debug | Request | Opcional | true/false; habilita objeto debug en la respuesta; validación: 400 ERR400_MISSING_OR_MALFORMED_HEADER, INVALID_DEBUG_HEADER_VALUE si valor inválido; en producción: alcance, 10 min, 10 req/min, intervalo 1 min, auditoría |
| X-Grd-Trace-Id | Response | Obligatorio | UUID v7; en todas las respuestas; rastreo en todas las capas |
| X-Grd-Correlation-Id | Request/Response | Opcional | UUID; propagar si presente en la petición |

**Seguridad:** headers de rastreo sin PII/secretos; validar por tenant y rate limit; sanitizar y limitar cantidad.

**Referencias:** RFC 9110, 9111, 7232; codex-idempotency.

---

## Módulo 4: Paginación

### Petición

| Parámetro | Tipo | Default | Máximo | Regla |
|-----------|------|---------|--------|-------|
| page_size | uint32 | 20 | 100 | Rechazar por encima del límite con 400 ERR400_INVALID_PARAMETER (PAGE_SIZE_TOO_LARGE, etc.) |
| page_token | string | — | — | Token opaco; retornado en llamadas anteriores |
| order_by | string | created_at | — | created_at, updated_at, reference_at; otro valor → 400 ORDER_BY_INVALID |
| sort | string | asc | — | asc, desc (case insensitive); otro → 400 SORT_INVALID |

### Respuesta

- `data`: array de la página actual.
- `pagination`: page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token (todos presentes, nulos cuando no aplique).
- Headers: Cache-Control (ej.: max-age=900), Link con rel first, previous, next, last.

### Comportamientos

- Primera página: sin page_token, page_size=20.
- Soporte a paginación reversa (previous_page_token, first_page_token).
- Ordenación estable y determinística.
- Tokens opacos (criptografiados/firmados); expiración (ej.: 10 min); log con X-Grd-Trace-Id.
- Sin resultados: 200 OK, lista vacía, total_count=0.

### Errores conocidos

| Escenario | HTTP | code | reason |
|-----------|------|------|--------|
| page_token inválido/expirado | 400 | ERR400_INVALID_PARAMETER | PAGE_TOKEN_INVALID, PAGE_TOKEN_EXPIRED |
| page_size inválido/por encima del límite | 400 | ERR400_INVALID_PARAMETER | PAGE_SIZE_INVALID, PAGE_SIZE_TOO_LARGE |
| order_by/sort inválido | 400 | ERR400_INVALID_PARAMETER | ORDER_BY_INVALID, SORT_INVALID |

**Referencias:** Hub Paginación; HATEOAS.

---

## Módulo 5: Ordenación

- Ordenación limitada a propiedades temporales: created_at, updated_at, reference_at.
- Uso de índices; ordenación estable (criterio secundario ej.: entity_id).
- Parámetros: order_by (default created_at), sort (default asc). Ausencia → created_at asc.
- Valores no permitidos en order_by o sort → 400 Bad Request (ERR400_INVALID_PARAMETER, ORDER_BY_INVALID, SORT_INVALID).
- Excepción: ordenación fija por regla de negocio puede omitir order_by si registrado en PDR.

**Referencias:** Hub Ordenación; OAS.

---

## Referencias generales

- [RESTful APIs — Hub Guardia](https://hub.guardia.finance/docs/specifications/restful/)
- codex-entities, codex-idempotency, codex-error-handling
- RFC 9110 (HTTP Semantics), RFC 9111 (Caching), RFC 7232 (Conditional Requests), RFC 7807 (Problem Details)
