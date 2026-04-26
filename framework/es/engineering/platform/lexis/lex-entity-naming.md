# Lexis: Convenciones de Nomenclatura de Entidades — snake_case

> **Prefijo:** `lex-` | **Tipo:** Ley Inviolable | **Alcance:** Plataforma Guardia — identificadores de entidad, nombres de campo, segmentos del tipo CloudEvents y nombres de columnas de base de datos

## Propósito

Las inconsistencias de nomenclatura entre el modelo de dominio, APIs, eventos y base de datos son una fuente persistente de bugs de integración, confusión en code review y ruptura de interoperabilidad entre servicios. Imponer una única convención de casing en todos los límites del sistema elimina toda una clase de errores de mapeo.

## Ley

> **Todo valor de `entity_type`, nombre de campo JSON, nombre de columna de base de datos y segmento variable en el formato de tipo CloudEvents (`{module}`, `{entity_type}`, `{event_name}`) DEBE usar snake_case. En documentos de modelo de dominio (artefactos DDD), los nombres de agregados y entidades usados como identificadores conceptuales DEBEN usar PascalCase. Usar camelCase, PascalCase o kebab-case para valores de `entity_type`, nombres de propiedades JSON o segmentos del tipo CloudEvents está PROHIBIDO.**

## Reglas

### 1. Valores de entity_type

`entity_type` es un identificador de cadena para la clase de la entidad. DEBE:
- Usar snake_case: `scheduled_transfer`, `ledger_entry`, `reconciliation_run`
- Ser en singular (no plural): `scheduled_transfer`, no `scheduled_transfers`
- Ser estable: cambiar `entity_type` es un cambio breaking y requiere ADR

### 2. Nombres de campos JSON (APIs y eventos)

Todos los nombres de campos en cuerpos de solicitud JSON, payloads de respuesta y objetos `data` de CloudEvents DEBEN usar snake_case:
- Correcto: `entity_id`, `created_at`, `idempotency_key`, `scheduled_date`, `failure_reason`
- Incorrecto: `entityId`, `createdAt`, `idempotencyKey`, `scheduledDate`, `failureReason`

### 3. Segmentos del tipo CloudEvents

El formato de tipo CloudEvents `event.guardia.{module}.{entity_type}.{event_name}` requiere todos los segmentos variables en snake_case:
- `{module}`: `platform`, `reconciliation`, `fiscal`
- `{entity_type}`: `scheduled_transfer`, `ledger_entry`
- `{event_name}`: `created`, `approved`, `executed`, `failed`, `cancelled`
- Ejemplo completo: `event.guardia.platform.scheduled_transfer.approved`

### 4. Nombres de columnas de base de datos

Los nombres de columnas de base de datos DEBEN usar snake_case:
- Correcto: `entity_id`, `entity_type`, `created_at`, `scheduled_date`
- Incorrecto: `entityId`, `EntityType`, `created-at`

### 5. Documentos de modelo de dominio — excepción para PascalCase

En artefactos DDD (documentos de modelo de dominio, diagramas de bounded context, definiciones de agregados), **los nombres de agregados y entidades usados como identificadores conceptuales** DEBEN usar PascalCase. Esta es la única excepción al snake_case:
- Agregado en documento DDD: `ScheduledTransfer`, `LedgerEntry`, `ReconciliationRun`
- La misma entidad en APIs y eventos: `entity_type: "scheduled_transfer"`, `event.guardia.platform.scheduled_transfer.created`

PascalCase en documentos DDD refleja el lenguaje del dominio; snake_case en los límites del sistema impone consistencia técnica.

### 6. Segmentos de path de URL — kebab-case (no es nomenclatura de entidad)

Los segmentos de path de URL de recursos de la API siguen kebab-case (`/v1/scheduled-transfers`) conforme a las convenciones RESTful (`lex-restful-apis`). Esto es enrutamiento de API, no nomenclatura de entidad — `entity_type` en el payload permanece en snake_case incluso cuando la URL usa kebab-case.

## Alcance

- **Aplica a:** modelado de entidades, contratos de API (OpenAPI/JSON), payloads de CloudEvents, esquemas de base de datos, documentos de modelo de dominio, documentación de eventos.
- **Agentes vinculados:** todos los agentes que crean o revisan entidades, APIs, eventos o modelos de dominio (warrior-theseus, warrior-daedalus, warrior-kronos, warrior-apollo, warrior-hera).
- **Excepciones:** nombres de campos de integraciones de terceros que llegan en camelCase de sistemas externos — mapear en la capa anti-corruption layer; no propagar camelCase internamente.

## Ejemplos

### Correcto

```json
{
  "entity_id": "01957f3e-a1b2-7c8d-9e0f-1a2b3c4d5e6f",
  "entity_type": "scheduled_transfer",
  "scheduled_date": "2026-04-30",
  "failure_reason": null,
  "created_at": "2026-04-26T10:00:00Z",
  "updated_at": "2026-04-26T10:00:00Z",
  "version": 1
}
```

Tipo CloudEvents: `event.guardia.platform.scheduled_transfer.approved`

Agregado en el documento de modelo de dominio: `ScheduledTransfer`

### Incorrecto

```json
{
  "entityId": "01957f3e-...",
  "entityType": "ScheduledTransfer",
  "scheduledDate": "2026-04-30",
  "failureReason": null,
  "createdAt": "2026-04-26T10:00:00Z"
}
```

Tipo CloudEvents (inválido): `event.guardia.platform.scheduledTransfer.Approved`

## Validación Automatizada

- **Herramienta:** JSON Schema / linter OpenAPI con patrón de nombre de propiedad `^[a-z][a-z0-9_]*$`; regex de tipo CloudEvents `^event\.guardia\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`; linter de migración de base de datos (squawk) verificando casing de nombres de columna.
- **Cuando:** pre-commit, CI (validación OpenAPI), PR review para documentos de modelo de dominio.
- **Métrica:** 0 nombres de campo en camelCase o PascalCase en esquemas JSON; 0 tipos CloudEvents con segmentos fuera de snake_case; 0 columnas de base de datos fuera de snake_case.

## Referencias

- `lex-entities` — estructura base de entidades (entity_id, entity_type, version, timestamps)
- `lex-cloudevents` — formato y estructura del tipo CloudEvents
- `lex-restful-apis` — convenciones de URL de API (kebab-case para segmentos de path)
- `codex-entities` — referencia del modelo de entidades
