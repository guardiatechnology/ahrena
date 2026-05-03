# Cry: Feature Design — Dominio, API y Eventos

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ciclo completo de diseño de feature: modelado de dominio, diseño de API REST y documentación de CloudEvents en secuencia

## Descripción

Este comando orquesta el ciclo completo de diseño de una feature invocando al Warrior Prometheus, quien coordina en secuencia: (1) modelado de dominio (warrior-theseus), (2) diseño de API REST (warrior-daedalus) y (3) documentación de eventos (warrior-kronos). Los artefactos se producen en **`docs/{context}/entities/`**, **`docs/{context}/oas/`** y **`docs/{context}/events/`** respectivamente.

## Uso

```
/cry-feature-design <descripción de la feature> [base path] [contexto de eventos]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `descripción de la feature` | Sí | Descripción del dominio, entidades, operaciones y reglas de negocio; usada como base para el ciclo completo | "Módulo de transferencias programadas: crear, listar, actualizar y cancelar; listado paginado; mutaciones idempotentes; eventos emitidos en cada transición de estado" |
| `base path` | No | Prefijo de URL para la API (ej.: /v1/scheduled-transfers). Si se omite, Daedalus propone uno | `/v1/scheduled-transfers` |
| `contexto de eventos` | No | Complemento específico para eventos (ej.: módulo, tipo de entidad). Si se omite, Kronos infiere del contexto | "Módulo platform, entidad scheduled_transfer" |

## Qué Hace el Comando

1. Invoca al Warrior Prometheus para orquestar el ciclo completo de diseño
2. **Fase 1 — Dominio:** Prometheus delega a warrior-theseus; produce entidades y modelo de dominio en **`docs/{context}/entities/`**
3. **Fase 2 — API:** Prometheus delega a warrior-daedalus; produce especificación OpenAPI y documento de API en **`docs/{context}/oas/`**
4. **Fase 3 — Eventos:** Prometheus delega a warrior-kronos; produce documentación de eventos en **`docs/{context}/events/`**
5. Prometheus verifica la consistencia entre los tres artefactos y entrega un resumen del paquete de diseño

## Template de Prompt

```
Contexto:
- Descripción de la feature: {{descripción de la feature}}
- Base path (opcional): {{base path}}
- Contexto de eventos (opcional): {{contexto de eventos}}

Tarea:
Actúa como el Warrior Prometheus (Gestor Técnico de Producto) y ejecuta el ciclo completo de diseño de la feature en secuencia:

1) **Fase de Dominio (Theseus):** Delega a warrior-theseus. Ejecuta kata-domain-model para modelar entidades, agregados, reglas de negocio e invariantes. Haz preguntas de clarificación cuando sea necesario. Produce artefactos de entidades en **`docs/{context}/entities/`**.

2) **Fase de API (Daedalus):** Delega a warrior-daedalus. Ejecuta kata-api-design-oas y kata-api-design-doc basándote en las entidades diseñadas. Haz preguntas de clarificación cuando sea necesario. Produce especificación OpenAPI y documento de API en **`docs/{context}/oas/`**.

3) **Fase de Eventos (Kronos):** Delega a warrior-kronos. Ejecuta kata-events-doc basándote en las entidades y operaciones de API. Haz preguntas de clarificación cuando sea necesario. Produce documentación de eventos en **`docs/{context}/events/`**.

4) **Verificación de Consistencia:** Verifica que entidades, API y eventos sean consistentes entre sí. Entrega un resumen del paquete de diseño completo.
```

## Ejemplo de Invocación

**Input:**

```
/cry-feature-design "Módulo de transferencias programadas: crear, listar, actualizar y cancelar; listado paginado y ordenable por fecha; mutaciones idempotentes; eventos emitidos en cada transición de estado" /v1/scheduled-transfers "módulo platform, entidad scheduled_transfer"
```

**Output esperado:**

Paquete de diseño completo producido por Prometheus con:
- **Entidades:** `docs/scheduled-payments/entities/scheduled-transfer.md` — modelo de dominio con campos, reglas de negocio e invariantes
- **API:** `docs/scheduled-payments/oas/openapi.yaml` + documento Markdown — endpoints POST/GET/PATCH/DELETE con paginación e idempotencia
- **Eventos:** `docs/scheduled-payments/events/events.md` — catálogo con `requested`, `approved`, `executed`, `failed`, `cancelled`
- Verificación de consistencia entre los tres artefactos

## Restricciones

- El Cry no implementa código; solo orquesta el ciclo de diseño completo
- La descripción de la feature debe ser suficiente para las tres fases; si está incompleta, cada Warrior especialista hará sus propias preguntas
- Las excepciones a las Lexis deben documentarse en un ADR

## Cry vs Kata

| Aspecto | Cry | Katas individuales |
|---------|-----|--------------------|
| **Naturaleza** | Orquestación del ciclo completo en un comando | Ejecución de una fase específica |
| **Complejidad** | Media (3 fases coordinadas por Prometheus) | Alta por fase (cada Kata tiene múltiples pasos) |
| **¿Configura agente?** | Sí (Prometheus + los tres Warriors) | Sí (el Warrior o agente específico de la fase) |
| **Ejemplo** | "/cry-feature-design dominio completo de transferencias programadas" | "/cry-api-design solo la API de transferencias" |

## Warriors Asociados

- **warrior-prometheus** — Orquestador del ciclo de diseño completo
- **warrior-theseus** — Modelado de dominio; produce `docs/{context}/entities/`
- **warrior-daedalus** — Diseño de API REST; produce `docs/{context}/oas/`
- **warrior-kronos** — Documentación de eventos; produce `docs/{context}/events/`

## Referencias

- `lex-feature-design-docs` — estructura canónica `docs/{context}/{category}/`
- `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, `warrior-kronos` — Warriors invocados por este Cry
