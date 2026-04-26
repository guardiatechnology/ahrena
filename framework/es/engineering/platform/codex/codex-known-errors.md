# Codex: Errores Conocidos de la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — catálogo de errores estandarizados

## Visión general

Este Codex cataloga los errores estandarizados utilizados por las APIs y eventos de la plataforma Guardia. Cada error se identifica por su `code` (UPPER_SNAKE_CASE con prefijo `ERR{HTTP}_`) y se detalla mediante sus posibles `reason`, con un mensaje orientado al desarrollador, elegibilidad de reintento y tratamiento sugerido.

> **Importante:** Todo error DEBE seguir la estructura definida en [codex-error-handling](codex-error-handling.md). Los nuevos `reason` DEBEN justificarse y agregarse a este catálogo.

## Contexto

- **Dominio:** catálogo de errores emitidos por endpoints HTTP y consumidores/procesadores de eventos.
- **Público objetivo:** implementadores de APIs/eventos, integradores y clientes que tratan respuestas de error.
- **Actualización:** siempre que se acuñe un nuevo `reason` en una especificación del Hub o se cree en un endpoint específico.

## Contenido

### Estructura del catálogo

Cada entrada del catálogo sigue este patrón:

- **`reason`** — cadena en UPPER_SNAKE_CASE, única por `code`.
- **Mensaje** — descripción orientada al desarrollador (no expuesta al usuario final).
- **Reintento** — elegibilidad de reintento (✅ tras corrección, ❌ no reintentar, ⏳ con backoff).
- **Tratamiento sugerido** — pasos para que el cliente resuelva el error.

### ERR400_MISSING_OR_MALFORMED_HEADER

Header obligatorio ausente o mal formado.

| reason | Reintento | Mensaje | Tratamiento sugerido |
|--------|:---------:|---------|----------------------|
| `IDEMPOTENCY_KEY_REQUIRED` | ✅ tras corrección | El recurso solicitado exige un `Idempotency-Key` válido. | Enviar el header `Idempotency-Key` formateado conforme a [codex-idempotency](codex-idempotency.md). |
| `MALFORMED_CORRELATION_ID` | ✅ tras corrección | El header `X-Grd-Correlation-Id` no está correctamente formateado. | Enviar UUID válido conforme a [codex-restful-headers](codex-restful-headers.md). |
| `INVALID_DEBUG_HEADER_VALUE` | ✅ tras corrección | El header `X-Grd-Debug` solo acepta `true` o `false`. | Corregir el valor del header `X-Grd-Debug`. |
| `INVALID_CONTENT_DIGEST` | ✅ tras corrección | El header `Content-Digest` es inválido o no coincide con el payload. | Recalcular SHA-256 sobre el JSON normalizado conforme a [codex-restful-headers](codex-restful-headers.md). |

### ERR400_INVALID_PAYLOAD

Body de la solicitud con formato o estructura inválida. Se añadirán códigos específicos a medida que nuevos endpoints registren `reason`.

### ERR400_INVALID_PARAMETER

Parámetros (path, query) con formato o valor inválido.

| reason | Reintento | Mensaje | Tratamiento sugerido |
|--------|:---------:|---------|----------------------|
| `INVALID_LEDGER_NAME_LENGTH` | ✅ tras corrección | Nombre del ledger fuera de los límites permitidos. | Ajustar el tamaño del nombre conforme al contrato del endpoint. |
| `INVALID_LEDGER_DESCRIPTION_LENGTH` | ✅ tras corrección | Descripción del ledger excede el límite. | Reducir el tamaño de la descripción. |
| `INVALID_PARAMETER_FORMAT` | ✅ tras corrección | Formato del body o de los parámetros inválido. | Verificar el contrato (OAS) y corregir la solicitud. |
| `INVALID_METADATA_FORMAT` | ✅ tras corrección | Metadatos inválidos. | Garantizar JSON válido y la estructura prevista en [codex-entities](codex-entities.md). |
| `INVALID_METADATA_LENGTH` | ✅ tras corrección | Los metadatos exceden el límite (10KB). | Reducir el tamaño de los metadatos. |
| `INVALID_EXTERNAL_ENTITY_ID_FORMAT` | ✅ tras corrección | `external_entity_id` con formato inválido. | Ajustar conforme a [codex-entities](codex-entities.md) (máx. 36 caracteres). |
| `PAGE_TOKEN_INVALID` | ✅ tras corrección | `page_token` inválido. | Usar el token devuelto en una respuesta anterior; ver [codex-restful-pagination](codex-restful-pagination.md). |
| `PAGE_TOKEN_EXPIRED` | ✅ tras corrección | `page_token` expirado. | Reiniciar la paginación desde `first_page_token` o desde la primera página. |
| `PAGE_SIZE_INVALID` | ✅ tras corrección | `page_size` inválido. | Enviar un entero positivo conforme al contrato. |
| `PAGE_SIZE_TOO_LARGE` | ✅ tras corrección | `page_size` por encima del límite (100). | Reducir `page_size` al máximo permitido. |
| `ORDER_BY_INVALID` | ✅ tras corrección | `order_by` inválido. | Usar `created_at`, `updated_at` o `reference_at`. |
| `SORT_INVALID` | ✅ tras corrección | `sort` inválido. | Usar `asc` o `desc` (case insensitive). |

### ERR401_UNAUTHORIZED

Autenticación ausente o inválida. Reservado para fallas de OAuth 2.0/JWT. Los mensajes NUNCA DEBEN indicar si un usuario existe.

### ERR402_INSUFFICIENT_FUNDS

| reason | Reintento | Mensaje | Tratamiento sugerido |
|--------|:---------:|---------|----------------------|
| `PAYMENT_IS_REQUIRED` | ❌ | Saldo insuficiente para la operación solicitada. | Regularizar saldo/pago antes de reintentar. |

### ERR403_FORBIDDEN

Cliente autenticado, sin autorización para el recurso. Los `reason` específicos por alcance se registrarán según necesidad.

### ERR404_NOT_FOUND

| reason | Reintento | Mensaje | Tratamiento sugerido |
|--------|:---------:|---------|----------------------|
| `LEDGER_NOT_FOUND` | ⏳ si el ledger se crea | Ledger especificado no encontrado. | Verificar `entity_id` o crear el ledger. |

### ERR405_INVALID_OPERATION

Operación no permitida en el estado actual del recurso. Los `reason` específicos se registrarán por dominio.

### ERR408_REQUEST_TIMEOUT

El cliente no completó la solicitud dentro del tiempo límite. Generalmente reintentable tras estabilización de red.

### ERR409_SERVER_STATE_CONFLICT

Conflicto con el estado actual del recurso.

| reason | Reintento | Mensaje | Tratamiento sugerido |
|--------|:---------:|---------|----------------------|
| `CONFLICTING_IDEMPOTENT_REQUEST` | ✅ tras corrección | Misma `Idempotency-Key` con payload distinto al de la ejecución previa. | Usar una nueva clave para una nueva operación O reenviar el payload original. |
| `EXTERNAL_ENTITY_ID_ALREADY_IN_USE` | ✅ tras corrección | `external_entity_id` ya utilizado por otro recurso. | Elegir otro identificador externo. |
| `LEDGER_NAME_ALREADY_IN_USE` | ✅ tras corrección | Nombre del ledger ya en uso. | Elegir otro nombre. |

### ERR422_BUSINESS_ERROR

Datos sintácticamente válidos, pero con error semántico/regla de negocio. Los `reason` específicos se registrarán por dominio.

### ERR429_RATE_LIMITED

El cliente excedió el límite de solicitudes. La respuesta DEBE incluir el header `Retry-After`.

### ERR500_INTERNAL_ERROR

Falla interna inesperada. El cliente NO DEBE reintentar inmediatamente; aplicar backoff exponencial y circuit breaker conforme a [codex-error-handling](codex-error-handling.md).

### ERR501_FEATURE_NOT_IMPLEMENTED

Funcionalidad no implementada. NO reintentar.

### ERR503_SERVICE_UNAVAILABLE

Servicio temporalmente no disponible. Reintentar con backoff, respetando `Retry-After` cuando esté presente.

### ERR504_GATEWAY_TIMEOUT

Timeout de gateway upstream. Reintentar con backoff.

### Creación de nuevos `reason`

Al añadir un nuevo `reason` al catálogo:

1. Confirmar que el `code` HTTP correcto ya existe en esta lista; si no, abrir una nueva sección `ERR{HTTP}_*`.
2. Garantizar UPPER_SNAKE_CASE y unicidad dentro del `code`.
3. Documentar el mensaje (sin datos sensibles), la elegibilidad de reintento y el tratamiento sugerido.
4. Registrar el error en el contrato OAS del endpoint que lo emite.
5. Actualizar este Codex y la página **Known Errors** en Notion.

## Referencias

- [codex-error-handling](codex-error-handling.md) — estructura estandarizada de errores
- [codex-idempotency](codex-idempotency.md) — `Idempotency-Key` y `Content-Digest`
- [codex-restful-headers](codex-restful-headers.md) — headers estándar y personalizados
- [codex-restful-pagination](codex-restful-pagination.md) — errores de paginación
- [codex-restful-status-codes](codex-restful-status-codes.md) — uso correcto de códigos HTTP
- Hub Guardia — página Known Errors (Notion)
