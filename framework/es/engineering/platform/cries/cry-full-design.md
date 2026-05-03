# Cry: Diseño Completo — API y Eventos

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Proceso único que combina diseño de API REST y documentación de eventos CloudEvents para una nueva feature

## Descripción

Este comando ejecuta el **diseño completo** de la superficie de la feature: en una sola secuencia, dispara al Warrior Daedalus para diseñar la API (OpenAPI + documento de API en **`docs/{context}/oas/`**) y luego al Warrior Kronos para documentar los eventos (Markdown en **`docs/{context}/events/`**). El agente ejecuta ambas fases en secuencia usando la misma descripción de feature como base. Equivale a combinar **cry-api-design** y **cry-event-storm** en un único flujo.

## Uso

```
/cry-full-design <descripción de la feature> [base path] [contexto de eventos]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `descripción de la feature` | Sí | Descripción del dominio, entidades, operaciones de API y reglas de negocio; usada como base para la API y el event storm | "Módulo de transferencias programadas: crear, listar, actualizar, cancelar; listado paginado; mutaciones idempotentes; eventos created, updated, cancelled" |
| `base path` | No | Prefijo de URL para la API (ej.: /v1/scheduled-transfers). Si se omite, Daedalus propone uno | `/v1/scheduled-transfers` |
| `contexto de eventos` | No | Complemento específico para eventos (ej.: módulo, tipo de entidad, base de source). Si se omite, Kronos infiere del contexto de la feature o hace preguntas | "Módulo platform, tipo de entidad scheduled_transfer" |

## Qué Hace el Comando

1. **Fase 1 — API:** Asume el rol del Warrior Daedalus; ejecuta **kata-api-design-oas** y **kata-api-design-doc**; produce especificación OpenAPI y documento de API en **`docs/{context}/oas/`**
2. **Fase 2 — Eventos:** Asume el rol del Warrior Kronos; ejecuta **kata-events-doc**; produce documentación de eventos en **`docs/{context}/events/`**
3. Usa la misma descripción de feature como input para ambas fases; en la fase 2, puede usar el contexto de eventos explícito o inferir de la API diseñada
4. Entrega un resumen de los artefactos producidos: OAS y documento de API en `docs/{context}/oas/`; doc de eventos en `docs/{context}/events/`

## Template de Prompt

```
Contexto:
- Descripción de la feature: {{descripción de la feature}}
- Base path (opcional): {{base path}}
- Contexto de eventos (opcional): {{contexto de eventos}}

Tarea:
Ejecuta el proceso de **diseño completo** en secuencia:

1) **Fase API (Daedalus):** Actúa como el Warrior Daedalus. Ejecuta **kata-api-design-oas** y **kata-api-design-doc** basándote en la descripción de la feature. Haz preguntas de clarificación cuando sea necesario (alcance, autenticación, paginación, base path). Produce especificación OpenAPI y documento de API en **`docs/{context}/oas/`**.

2) **Fase Event Storm (Kronos):** Actúa como el Warrior Kronos. Basándote en la misma feature (y contexto de eventos, si se proporcionó), ejecuta **kata-events-doc**. Identifica los eventos relevantes (ej.: created, updated, cancelled para las operaciones de API), haz preguntas de clarificación cuando sea necesario, y produce la documentación de eventos en **`docs/{context}/events/`**.

Entrega un resumen final: artefactos en `docs/{context}/oas/` (OAS + doc de API) y en `docs/{context}/events/` (doc de eventos).
```

## Ejemplo de Invocación

**Input:**

```
/cry-full-design "Módulo de transferencias programadas: crear, listar, actualizar, cancelar; listado paginado y ordenable; mutaciones idempotentes; eventos created, updated, cancelled" /v1/scheduled-transfers
```

**Output esperado:**

- **Fase 1:** Recursos y endpoints (POST, GET, GET/:id, PATCH, DELETE); especificación OpenAPI y documento de API creados/actualizados en **`docs/{context}/oas/`**
- **Fase 2:** Catálogo de eventos (event.guardia.platform.scheduled_transfer.created, .updated, .cancelled); documento de eventos creado/actualizado en **`docs/{context}/events/`**
- Resumen: tres artefactos — OAS y doc de API en `docs/scheduled-payments/oas/`; doc de eventos en `docs/scheduled-payments/events/`

## Restricciones

- El Cry no implementa código; solo orquesta los dos Warriors
- La descripción de la feature debe soportar tanto el diseño de API como la identificación de eventos; si falta información para eventos, Kronos hará preguntas en la fase 2
- Las excepciones a las Lexis deben documentarse en un ADR

## Cries y Warriors Asociados

- **cry-api-design** — Solo diseño de API (Daedalus)
- **cry-event-storm** — Solo documentación de eventos (Kronos)
- **warrior-daedalus** — Especialista en Diseño de API
- **warrior-kronos** — Especialista en Event Storm

## Referencias

- `lex-feature-design-docs` — estructura canónica `docs/{context}/{category}/`
- `cry-api-design`, `cry-event-storm` — Cries invocados (los Katas que ejecutan consultan las Lexis y Codex aplicables; ver documentación de Cry/Kata)
