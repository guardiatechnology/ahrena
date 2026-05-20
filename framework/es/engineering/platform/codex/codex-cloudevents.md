# Codex: CloudEvents en la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — eventos

## Visión General

Este Codex describe el uso de la especificación CloudEvents para representar eventos en la plataforma Guardia. Cubre estructura del evento, propiedades obligatorias, formato, cuándo usar y cuándo no usar, y consideraciones de seguridad. El shape de los datos en `data` sigue codex-entities cuando la entidad sea persistente.

## Contexto

- **Dominio:** eventos en sistemas distribuidos en la plataforma Guardia (publicación y consumo).
- **Público objetivo:** implementadores de publicadores y consumidores de eventos.
- **Actualización:** cuando la especificación CloudEvents en el Hub sea alterada.

## Contenido

### Estructura del evento

| Propiedad | Tipo | Default | Obligatorio | Descripción |
|-----------|------|---------|-------------|-------------|
| id | UUID v7 | — | Sí | Identificador único de la emisión del evento. UUID v7 conforme RFC 9562. DEBE ser único por evento — la misma entidad puede emitir varios eventos (ej.: `created`, `approved`, `executed`), cada uno con un `id` distinto. NO es igual al `entity_id`. Inmutable. |
| source | URI | — | Sí | Origen del evento. Formato: `https://api.guardia.technology/{context}/{entity_type}/{entity_id}` |
| specversion | string | 1.0 | Sí | Versión de la spec CloudEvents; valor fijo "1.0". |
| type | string | — | Sí | Formato `event.{provider}.{domain}.{entity_name}.{event_name}`; todos los tokens en snake_case en minúsculas; catalogado en el Hub. |
| time | datetime | — | Sí | Timestamp de la ocurrencia (RFC 3339). |
| datacontenttype | string | application/json | Sí | Valor fijo "application/json". |
| dataschema | URI | — | Opcional | URI del schema JSON en el Hub. |
| subject | string | — | Sí | Formato `{entity_type}/{entity_id}`. `entity_type` en UPPER_SNAKE_CASE. |
| idempotencykey | UUID | — | Sí | Clave de idempotencia; conforme codex-idempotency. |
| data | object | — | Sí | Datos de la entidad; campos comunes: entity_id, entity_type, external_entity_id, created_at, updated_at, discarded_at, version, metadata. **El historial de la entidad DEBE omitirse de los eventos.** Ver codex-entities. |

Notas de las propiedades:
- **type:** DEBE ser un tipo catalogado en el catálogo de eventos del proyecto (schemas).
- **dataschema:** cuando esté presente, DEBE apuntar al schema JSON del proyecto.
- **data.entity_type:** DEBE usar UPPER_SNAKE_CASE (ej.: `TRANSACTION`, `SCHEDULED_TRANSFER`), conforme `lex-entity-naming`.
- **data.entity_id:** DEBE usar el formato `{entity_id_prefix}:{uuid_v7}`.

### Formato del tipo CloudEvents

El formato canónico para eventos internos de Guardia es:

```
event.{provider}.{domain}.{entity_name}.{event_name}
```

| Token | Descripción | Ejemplo |
|-------|-------------|---------|
| `provider` | Siempre `guardia` para eventos internos; nombre del proveedor externo para eventos externos mapeados | `guardia` |
| `domain` | Bounded context / dominio del servicio emisor | `platform`, `reconciliation`, `fiscal` |
| `entity_name` | Forma en minúsculas del `entity_type` en UPPER_SNAKE_CASE | `TRANSACTION` → `transaction` |
| `event_name` | Verbo en pasado describiendo lo que ocurrió | `created`, `approved`, `executed`, `failed` |

El segmento `{entity_name}` es la excepción declarada a la regla UPPER_SNAKE_CASE para `entity_type`: el estándar de notación dot-notation reverso del DNS de CloudEvents requiere minúsculas, por lo que `entity_name` se deriva convirtiendo `entity_type` a minúsculas.

### entity_id_prefix

Toda entidad tiene un prefijo corto (2–5 caracteres alfanuméricos en minúsculas) definido antes del inicio del desarrollo. El prefijo se combina con un UUID v7 para formar el identificador de la entidad:

```
{entity_id_prefix}:{uuid_v7}
```

Ejemplos: `txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`, `rec:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

El prefijo aparece donde sea que se referencie un `entity_id`: `data.entity_id`, `subject`, `source` y en cualquier campo de referencia cruzada de entidad en `data`. El `id` de CloudEvents NO es un `entity_id` — es un UUID v7 nuevo en cada emisión de evento y no lleva prefijo.

### Ejemplo de evento (JSON)

```json
{
  "id": "019b9f12-9999-7c8d-9e0f-aaaaaaaaaaaa",
  "source": "https://api.guardia.technology/platform/TRANSACTION/txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "specversion": "1.0",
  "type": "event.guardia.platform.transaction.created",
  "time": "2026-03-08T12:00:00Z",
  "datacontenttype": "application/json",
  "dataschema": "https://<schema-base>/schemas/transaction.v1.json",
  "subject": "TRANSACTION/txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "idempotencykey": "019b9f12-0000-7000-8000-000000000002",
  "data": {
    "entity_id": "txn:019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
    "entity_type": "TRANSACTION",
    "external_entity_id": "ext-123",
    "created_at": "2026-03-08T12:00:00Z",
    "updated_at": "2026-03-08T12:00:00Z",
    "discarded_at": null,
    "version": 1,
    "metadata": {}
  }
}
```

### Formato y serialización

- Serialización: JSON; encoding UTF-8.
- Timestamps: RFC 3339.
- Tamaño máximo del evento: inferior a 12KB.

### Comportamientos esperados

- Eventos inmutables tras la publicación.
- Publicación en tópicos distintos por tipo: estándar `event.guardia.{domain}.{entity_name}.{event_name}` (todos los tokens en snake_case en minúsculas).
- Los consumidores DEBEN implementar idempotencia.
- Orden de entrega preservada para consistencia temporal y causal.
- Eventos auto-descriptivos; validación contra schema cuando esté definido.

### Eventos externos

- Los eventos externos que no sigan CloudEvents DEBEN ser mapeados a este estándar.
- Publicación en tópicos con nomenclatura `event.{provider}.{domain}.{entity_name}.{event_name}` (todos los tokens en snake_case en minúsculas).

### Cuándo usar

- Sistemas distribuidos que intercambian eventos; arquitecturas basadas en eventos; integración entre servicios; consumo y propagación de eventos externos; mensajería asíncrona.

### Cuándo no usar

- Comunicación síncrona; transferencia de archivos grandes; streaming continuo; comunicación en tiempo real de baja latencia.

### Seguridad

- Transmisión por canales seguros (TLS); datos sensibles cifrados u ofuscados; acceso controlado por autenticación y autorización (conforme spec Auth).

### Notas

- Retry para entrega; consumidores idempotentes; dead letter queue para eventos no procesados.

## Referencias

- codex-entities, codex-idempotency
- Cloud Events Specification; RFC 3339; RFC 9562
