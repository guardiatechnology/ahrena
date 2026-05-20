# Lexis: Convenciones de Nomenclatura de Entidades e Identificadores

> **Prefijo:** `lex-` | **Tipo:** Ley Inviolable | **Alcance:** Plataforma Guardia — tipos de entidad, identificadores, nombres de campo, segmentos del tipo CloudEvents y nombres de columnas de base de datos

## Propósito

Las inconsistencias de nomenclatura entre el modelo de dominio, APIs, eventos y bases de datos son una fuente persistente de bugs de integración, confusión en code review y ruptura de interoperabilidad entre servicios. Imponer convenciones canónicas en todos los límites del sistema elimina toda una clase de errores de mapeo.

## Ley

> **Todo valor de `entity_type` DEBE usar UPPER_SNAKE_CASE (ej.: `TRANSACTION`, `SCHEDULED_TRANSFER`). Todo nombre de campo JSON y nombre de columna de base de datos DEBE usar snake_case. Todo `entity_id` DEBE formatearse como `{entity_id_prefix}:{uuid_v7}`, donde el prefijo es una cadena alfanumérica en minúsculas de 2 a 5 caracteres definida antes del inicio del desarrollo. Los campos de identificador de entidad en payloads JSON externos DEBEN seguir la convención `{entity_name}_id` — el sufijo `_entity_id` está PROHIBIDO. En segmentos del tipo CloudEvents, `{entity_name}` DEBE ser la forma en minúsculas del `entity_type` en UPPER_SNAKE_CASE. Usar camelCase o PascalCase para valores de `entity_type`, nombres de propiedades JSON o segmentos del tipo CloudEvents está PROHIBIDO.**

## Reglas

### 1. Valores de entity_type — UPPER_SNAKE_CASE

`entity_type` es el discriminador canónico para la clase de la entidad. DEBE:
- Usar UPPER_SNAKE_CASE: `TRANSACTION`, `SCHEDULED_TRANSFER`, `LEDGER_ENTRY`
- Ser en singular (no plural): `TRANSACTION`, no `TRANSACTIONS`
- Ser estable: cambiar `entity_type` es un cambio breaking y requiere ADR

Los únicos contextos donde `entity_type` aparece en minúsculas son:
- Segmentos de path de URL (ej.: `/v1/scheduled-transfers` en kebab-case conforme `lex-restful-apis`)
- El segmento `{entity_name}` del campo `type` de CloudEvents (ej.: `SCHEDULED_TRANSFER` → `scheduled_transfer`), como excepción declarada justificada por el estándar de notación dot-notation reverso del DNS de CloudEvents

### 2. Formato de entity_id — {entity_id_prefix}:{uuid_v7}

Todo identificador de entidad DEBE formatearse como:

```
{entity_id_prefix}:{uuid_v7}
```

- `entity_id_prefix`: 2 a 5 caracteres alfanuméricos en minúsculas definidos antes del inicio del desarrollo (ej.: `txn`, `rec`, `org`, `per`, `doc`)
- `uuid_v7`: UUID v7 conforme a la [RFC 9562](https://datatracker.ietf.org/doc/html/rfc9562), asegurando ordenación temporal
- Ejemplo: `txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

El prefijo DEBE declararse en el documento de diseño de la entidad antes de comenzar la codificación. Cambiar un prefijo es un cambio breaking que requiere ADR.

### 3. Nomenclatura del campo de identificador — {entity_name}_id

Al referenciar una entidad por su identificador en un payload JSON de otra entidad:
- El campo DEBE denominarse `{entity_name}_id`, donde `{entity_name}` es la forma en minúsculas del `entity_type`
- Correcto: `transaction_id`, `ledger_entry_id`, `scheduled_transfer_id`
- El sufijo `_entity_id` está PROHIBIDO: nunca usar `transaction_entity_id`, `ledger_entry_entity_id`

Excepción: dentro del propio payload de la entidad, el campo de identificador canónico es siempre `entity_id`.

### 4. Nombres de campos JSON — snake_case

Todos los nombres de campos en cuerpos de solicitud JSON, payloads de respuesta y objetos `data` de CloudEvents DEBEN usar snake_case:
- Correcto: `entity_id`, `created_at`, `idempotency_key`, `scheduled_date`, `failure_reason`
- Incorrecto: `entityId`, `createdAt`, `idempotencyKey`, `scheduledDate`, `failureReason`

### 5. Segmentos del tipo CloudEvents — minúsculas

El formato de tipo CloudEvents `event.{provider}.{domain}.{entity_name}.{event_name}` requiere todos los segmentos variables en snake_case en minúsculas:
- `{provider}`: `guardia` para eventos internos; nombre del proveedor externo para eventos externos mapeados
- `{domain}`: `platform`, `reconciliation`, `fiscal`
- `{entity_name}`: forma en minúsculas del `entity_type` en UPPER_SNAKE_CASE (ej.: `SCHEDULED_TRANSFER` → `scheduled_transfer`)
- `{event_name}`: `created`, `approved`, `executed`, `failed`, `cancelled`
- Ejemplo completo: `event.guardia.platform.scheduled_transfer.approved`

### 6. Nombres de columnas de base de datos — snake_case

Los nombres de columnas de base de datos DEBEN usar snake_case:
- Correcto: `entity_id`, `entity_type`, `created_at`, `scheduled_date`
- Incorrecto: `entityId`, `EntityType`, `created-at`

### 7. Documentos de modelo de dominio — excepción para PascalCase

En artefactos DDD (documentos de modelo de dominio, diagramas de bounded context, definiciones de agregados), **los nombres de agregados y entidades usados como identificadores conceptuales** DEBEN usar PascalCase. Esta es la única excepción:
- Agregado en documento DDD: `ScheduledTransfer`, `LedgerEntry`, `Transaction`
- La misma entidad en los límites del sistema: `entity_type: "SCHEDULED_TRANSFER"`, `event.guardia.platform.scheduled_transfer.created`

PascalCase en documentos DDD refleja el lenguaje del dominio; UPPER_SNAKE_CASE en los límites del sistema impone consistencia técnica.

### 8. Segmentos de path de URL — kebab-case

Los segmentos de path de URL de recursos de la API siguen kebab-case (`/v1/scheduled-transfers`) conforme a las convenciones RESTful (`lex-restful-apis`). Esto es enrutamiento de API — `entity_type` en el payload permanece UPPER_SNAKE_CASE.

## Alcance

- **Aplica a:** modelado de entidades, contratos de API (OpenAPI/JSON), payloads de CloudEvents, esquemas de base de datos, documentos de modelo de dominio, documentación de eventos.
- **Agentes vinculados:** todos los agentes que crean o revisan entidades, APIs, eventos o modelos de dominio (warrior-theseus, warrior-daedalus, warrior-kronos, warrior-apollo, warrior-hera).
- **Excepciones:** nombres de campos de integraciones de terceros que llegan en camelCase de sistemas externos — mapear en la capa anti-corruption layer; no propagar camelCase internamente.

## Ejemplos

### Correcto

```json
{
  "entity_id": "txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entity_type": "SCHEDULED_TRANSFER",
  "scheduled_date": "2026-04-30",
  "failure_reason": null,
  "created_at": "2026-04-26T10:00:00Z",
  "updated_at": "2026-04-26T10:00:00Z",
  "version": 1
}
```

Tipo CloudEvents: `event.guardia.platform.scheduled_transfer.approved`

Subject CloudEvents: `SCHEDULED_TRANSFER/txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f`

Agregado en el documento de modelo de dominio: `ScheduledTransfer`

Referencia cruzada de entidad: `"transaction_id": "txn:01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f"`

### Incorrecto

```json
{
  "entityId": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entityType": "ScheduledTransfer",
  "transaction_entity_id": "txn:...",
  "scheduledDate": "2026-04-30",
  "createdAt": "2026-04-26T10:00:00Z"
}
```

Tipo CloudEvents (inválido): `event.guardia.platform.ScheduledTransfer.Approved`

## Validación Automatizada

- **Herramienta:** JSON Schema / linter OpenAPI con patrón `entity_type` `^[A-Z][A-Z0-9_]*$`; patrón de nombre de campo JSON `^[a-z][a-z0-9_]*$`; regex de tipo CloudEvents `^event\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`; patrón de entity_id `^[a-z0-9]{2,5}:[0-9a-f-]{36}$`; regla de lint bloqueando el sufijo `_entity_id`; linter de migración de base de datos (squawk) verificando casing de nombres de columna.
- **Cuando:** pre-commit, CI (validación OpenAPI), PR review para documentos de modelo de dominio.
- **Métrica:** 0 valores de `entity_type` en minúsculas en payloads JSON; 0 sufijos `_entity_id` en nombres de campo; 0 valores de entity_id sin prefijo; 0 nombres de campo en camelCase en esquemas JSON; 0 tipos CloudEvents con segmentos no en minúsculas; 0 columnas de base de datos fuera de snake_case.

## Referencias

- `lex-entities` — estructura base de entidades (entity_id, entity_type, version, timestamps)
- `lex-cloudevents` — formato y estructura del tipo CloudEvents
- `lex-restful-apis` — convenciones de URL de API (kebab-case para segmentos de path)
- `codex-entities` — referencia del modelo de entidades
