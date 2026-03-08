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
| id | UUID v7 | — | Sí | Identificador único del evento; inmutable; RFC 9562. |
| source | URI | — | Sí | Origen del evento (ej.: https://&lt;tenant_id&gt;.guardia.finance/&lt;module&gt;/api/v1/&lt;entity_type&gt;/&lt;entity_id&gt;) |
| specversion | string | 1.0 | Sí | Versión de la spec CloudEvents; valor fijo "1.0". |
| type | string | — | Sí | Formato event.{provider}.{module}.{entity_type}.{event_name}; catalogado en el Hub. |
| time | datetime | — | Sí | Timestamp de la ocurrencia (RFC 3339). |
| datacontenttype | string | application/json | Sí | Valor fijo "application/json". |
| dataschema | URI | — | Opcional | URI del schema JSON en el Hub. |
| subject | string | — | Sí | Formato {entity_type}/{entity_id}. |
| idempotencykey | UUID | — | Sí | Clave de idempotencia; conforme codex-idempotency. |
| data | object | — | Sí | Datos de la entidad; campos comunes: entity_id, entity_type, external_entity_id, created_at, updated_at, discarded_at, version, metadata. **El historial de la entidad DEBE omitirse de los eventos.** Ver codex-entities. |

- **type:** DEBE ser un tipo catalogado en el catálogo de eventos del proyecto (schemas).
- **dataschema:** cuando esté presente, DEBE apuntar al schema JSON del proyecto.

### Ejemplo de evento (JSON)

```json
{
  "id": "019b9f12-3a4b-7c8d-9e0f-1a2b3c4d5e6f",
  "source": "https://tenant.guardia.finance/platform/api/v1/transactions/019b9f12-0000-7000-8000-000000000001",
  "specversion": "1.0",
  "type": "event.guardia.platform.transaction.created",
  "time": "2026-03-08T12:00:00Z",
  "datacontenttype": "application/json",
  "dataschema": "https://<schema-base>/schemas/transaction.v1.json",
  "subject": "transaction/019b9f12-0000-7000-8000-000000000001",
  "idempotencykey": "019b9f12-0000-7000-8000-000000000002",
  "data": {
    "entity_id": "019b9f12-0000-7000-8000-000000000001",
    "entity_type": "transaction",
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
- Publicación en tópicos distintos por tipo: estándar event.guardia.{module}.{entity_type}.{event_name}.
- Los consumidores DEBEN implementar idempotencia.
- Orden de entrega preservada para consistencia temporal y causal.
- Eventos auto-descriptivos; validación contra schema cuando esté definido.

### Eventos externos

- Los eventos externos que no sigan CloudEvents DEBEN ser mapeados a este estándar.
- Publicación en tópicos con nomenclatura event.{provider}.{module}.{entity_type}.{event_name}.

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
- Cloud Events Specification; RFC 3339
