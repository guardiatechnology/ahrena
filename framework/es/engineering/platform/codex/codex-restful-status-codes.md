# Codex: Códigos de Estado HTTP en APIs RESTful

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — APIs REST — códigos de estado

## Visión General

Códigos de estado permitidos y reglas de uso para endpoints HTTP de la plataforma Guardia. Los códigos utilizados en cada endpoint DEBEN constar en el contrato OAS. Estándar mínimo para cualquier API RESTful de la Guardia.

## Contexto

- **Dominio:** códigos de estado HTTP en respuestas de API.
- **Público objetivo:** implementadores y consumidores de APIs.
- **Actualización:** cuando la especificación de códigos de estado en el Hub sea alterada.

## Contenido

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
| 408 | Request Timeout | El cliente tardó en completar la petición | Timeout entre servidores (use 504) |
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

## Referencias

- RFC 9110; MDN
- [codex-restful-apis](codex-restful-apis.md) (índice)
