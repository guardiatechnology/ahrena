# Codex: Payload de Respuesta en APIs RESTful

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — APIs REST — payload

## Visión General

Estructura unificada para respuestas de éxito y error en peticiones HTTP de la plataforma Guardia. Aplicable a todas las peticiones HTTP de la plataforma.

## Contexto

- **Dominio:** estructura del cuerpo de respuesta (data, pagination, errors, debug).
- **Público objetivo:** implementadores y consumidores de APIs.
- **Actualización:** cuando la especificación de payload en el Hub sea alterada.

## Contenido

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

- `errors`: array de { code, reason, message }; code conforme Tratamiento de Errores; **message** orientada al **desarrollador**, nunca al usuario final (evitar exponer a la UI sin tratamiento).
- En respuestas 4xx/5xx, `data` y `pagination` ausentes; solo `errors` (y `debug` si X-Grd-Debug: true).

### Debug

- Incluir **solo** cuando el header de petición `X-Grd-Debug: true`; nunca en producción por defecto.
- El objeto `debug` DEBE contener: `trace_id`, `correlation_id`, `instance`, `timestamp`, `duration`, `memory`, `query`, `params`, `internal_ip`, `external_ip`.
- NUNCA incluir datos sensibles (secretos, PII, tokens).
- Ejemplo de payload de error con debug (cuando X-Grd-Debug: true):

```json
{
  "errors": [
    {
      "code": "ERR404_NOT_FOUND",
      "reason": "RESOURCE_NOT_FOUND",
      "message": "Recurso no encontrado para el identificador informado."
    }
  ],
  "debug": {
    "trace_id": "019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
    "correlation_id": "019b9f12-0000-7000-8000-000000000001",
    "instance": "api-gateway-01",
    "timestamp": "2026-03-08T12:00:00Z",
    "duration": 15,
    "memory": 128,
    "query": "entity_id=abc",
    "params": {},
    "internal_ip": "10.0.1.5",
    "external_ip": "203.0.113.42"
  }
}
```

## Referencias

- codex-entities, codex-error-handling; RFC 7807
- [codex-restful-apis](codex-restful-apis.md) (índice)
