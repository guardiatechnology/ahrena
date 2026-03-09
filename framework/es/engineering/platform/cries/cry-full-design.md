# Cry: Diseño Completo — API y Eventos

> **Prefijo:** `cry-` | **Tipo:** Comando Recorrente | **Alcance:** Proceso único que combina diseño de API REST y documentación de eventos CloudEvents para una nueva feature

## Descripción

Este comando ejecuta el **diseño completo** de la superficie de la feature: en una sola secuencia, invoca al Warrior Daedalus para diseñar la API (OpenAPI + documento de la API en **paths.oas**) y luego al Warrior Kronos para documentar los eventos (Markdown en **paths.events**). El agente ejecuta las dos fases en secuencia, usando la misma descripción de la feature como base. Equivale a combinar **cry-api-design** y **cry-event-storm** en un único flujo.

## Uso

```
/cry-full-design <descripción de la feature> [base path] [contexto de eventos]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `descripción de la feature` | Sí | Descripción del dominio, entidades, operaciones de API y reglas de negocio; sirve de base tanto para la API como para el event storm | "Módulo de agendamiento de transferencias: crear, listar, actualizar y cancelar; listado paginado; mutaciones idempotentes; eventos created, updated, cancelled" |
| `base path` | No | Prefijo de URL para la API (ej.: /v1/scheduled-transfers). Si se omite, Daedalus propone | `/v1/scheduled-transfers` |
| `contexto de eventos` | No | Complemento específico para eventos (ej.: módulo, entity type, source base). Si se omite, Kronos infiere del contexto de la feature o pregunta | "Módulo platform, entity type scheduled_transfer" |

## Qué Hace el Comando

1. **Fase 1 — API:** Asume el rol del Warrior Daedalus; ejecuta **kata-api-design-oas** y **kata-api-design-doc**; produce especificación OpenAPI y documento de la API en **paths.oas** (docs/oas)
2. **Fase 2 — Eventos:** Asume el rol del Warrior Kronos; ejecuta **kata-events-doc**; produce documentación de eventos en **paths.events** (docs/events)
3. Usa la misma descripción de la feature como input para ambas fases; en la fase 2, puede usar el contexto de eventos explícito o inferir a partir de la API diseñada
4. Entrega resumen de los artefactos producidos: OAS y doc de la API en paths.oas; doc de eventos en paths.events

## Prompt Template

```
Contexto:
- Descripción de la feature: {{descripción de la feature}}
- Base path (opcional): {{base path}}
- Contexto de eventos (opcional): {{contexto de eventos}}

Tarea:
Ejecute el proceso de **diseño completo** en secuencia:

1) **Fase API (Daedalus):** Actúe como el Warrior Daedalus. Ejecute **kata-api-design-oas** y **kata-api-design-doc** con base en la descripción de la feature. Haga preguntas de clarificación si es necesario (alcance, autenticación, paginación, base path). Produzca especificación OpenAPI y documento de la API en **paths.oas**.

2) **Fase Event Storm (Kronos):** Actúe como el Warrior Kronos. Con base en la misma feature (y en el contexto de eventos, si se informa), ejecute **kata-events-doc**. Identifique los eventos relevantes (ej.: created, updated, cancelled para las operaciones de la API), haga preguntas de clarificación si es necesario, y produzca la documentación de eventos en **paths.events**.

Entregue un resumen final: artefactos en paths.oas (OAS + doc de la API) y en paths.events (doc de eventos).
```

## Ejemplo de Invocación

**Input:**

```
/cry-full-design "Módulo de transferencias agendadas: crear, listar, actualizar y cancelar; listado paginado y ordenable; mutaciones idempotentes; eventos created, updated y cancelled" /v1/scheduled-transfers
```

**Output esperado:**

- **Fase 1:** Recursos y endpoints (POST, GET, GET/:id, PATCH, DELETE); especificación OpenAPI y doc de la API creados/actualizados en **paths.oas**
- **Fase 2:** Catálogo de eventos (event.guardia.platform.scheduled_transfer.created, .updated, .cancelled); doc de eventos creado/actualizado en **paths.events**
- Resumen: tres artefactos — OAS y doc de la API en docs/oas; doc de eventos en docs/events

## Restricciones

- El Cry no implementa código; solo orquesta los dos Warriors
- La descripción de la feature debe permitir tanto el diseño de la API como la identificación de los eventos; si falta información para eventos, Kronos hará preguntas en la fase 2
- Excepciones a las Lexis deben documentarse en ADR

## Cries y Warriors Asociados

- **cry-api-design** — Solo diseño de API (Daedalus)
- **cry-event-storm** — Solo documentación de eventos (Kronos)
- **warrior-daedalus** — Especialista en Diseño de API
- **warrior-kronos** — Especialista en Event Storm

## Referencias

- lex-restful-apis, lex-cloudevents, lex-entities, lex-idempotency
- codex-restful-apis, codex-cloudevents, codex-entities, codex-idempotency
