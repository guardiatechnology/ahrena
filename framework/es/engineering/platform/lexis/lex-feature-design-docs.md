# Lexis: Estructura Obligatoria de los Documentos de Diseño de Feature

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — documentos producidos durante el ciclo de diseño de feature orquestado por warrior-prometheus

## Propósito

El modelado de dominio, el diseño de API y la documentación de eventos producen artefactos que deben encontrarse rápidamente, leerse por humanos y por agentes, y actualizarse sin ambigüedad entre fases. Sin una estructura única y nominal, cada feature termina guardando documentos en lugares diferentes, con nombres diferentes, y la consistencia cruzada entre dominio, API y eventos se pierde. Esta Lexis fija el lugar, el nombre y la forma de organización de esos documentos.

## Ley

> **Todo documento producido en las fases de diseño de feature (modelado de dominio, diseño de API, documentación de eventos, agentes y métricas) DEBE ser persistido en `docs/{context}/{categoria}/`, donde `{context}` es el Bounded Context en kebab-case y `{categoria}` es una de las categorías canónicas: `entities`, `oas`, `events`, `agents`, `metrics`. Cada categoría DEBE seguir el template definido en `codex-feature-design-docs`. Guardar documentos de diseño fuera de esa estructura, en paths configurables (`paths.oas`, `paths.events`, `paths.domain`) o en cualquier otro lugar FUERA de `docs/{context}/{categoria}/` está PROHIBIDO.**

## Cobertura

- **Se aplica a:** todos los documentos producidos por los warriors de diseño (`warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, `warrior-kronos`) y por cualquier agente que cree o actualice artefactos de diseño de feature en la plataforma Guardia.
- **Agentes vinculados:** `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, `warrior-kronos`, `warrior-athena` cuando orquesta diseño, y cualquier Kata invocado por ellos (`kata-domain-model`, `kata-api-design-oas`, `kata-api-design-doc`, `kata-event-storm`, `kata-events-doc`, `kata-feature-design-docs`).
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones. Documentos transitorios de orquestación (checkpoints, scratchpads de fase) no son objetivo de esta Lexis y permanecen en `.ahrena/workflow/`.

## Estructura Canónica

```
docs/
└── {context}/                  # Bounded Context en kebab-case (ej.: scheduled-payments)
    ├── entities/
    │   └── {entity-name}.md    # 1 archivo por entidad (kebab-case)
    ├── oas/
    │   └── openapi.yaml        # OpenAPI 3.x de la API del contexto
    ├── events/
    │   └── events.md           # Eventos del contexto, organizados por entidad
    ├── agents/                 # (reservado — definición posterior)
    └── metrics/                # (reservado — definición posterior)
```

### Reglas de nomenclatura

| Ítem | Regla |
|------|-------|
| `{context}` | kebab-case del nombre del Bounded Context. Ej.: `ScheduledPayments` → `scheduled-payments` |
| Archivos de `entities/` | `{entity-name}.md` en kebab-case del nombre en PascalCase. Ej.: `ScheduledTransfer` → `scheduled-transfer.md` |
| Archivo de `oas/` | `openapi.yaml`. Cuando exista más de una API en el mismo contexto, sufijar: `openapi-{slug}.yaml` |
| Archivo de `events/` | `events.md` |
| Categorías reservadas | `entities`, `oas`, `events`, `agents`, `metrics`. Crear otra categoría sin ADR aprobado está PROHIBIDO |

### Conformidad de contenido

Cada categoría DEBE seguir el template definido en `codex-feature-design-docs`:

- `entities/{entity}.md` — encabezado con **Clasificación DDD** (Entity, Aggregate Root o Value Object), sección **Por qué existe**, tabla **Campos** (Campo, Tipo, Tamaño, Obligatorio, Descripción), y secciones **Reglas de Negocio**, **Invariantes**, **Relaciones**, **Errores** y **Referencias**.
- `oas/openapi.yaml` — OpenAPI 3.x en YAML legible, conforme a `codex-oas-structure`.
- `events/events.md` — agrupado por entidad, con `stateDiagram-v2` Mermaid del ciclo de vida, y para cada evento el payload en CloudEvents conforme a `codex-cloudevents`.

## Consecuencias de Violación

1. **Bloqueo automático:** los PR con documentos de diseño fuera de `docs/{context}/{categoria}/` son rechazados.
2. **Inconsistencia cruzada:** Prometheus no concluye el paquete final cuando algún artefacto está fuera de la estructura.
3. **Remediación:** mover el documento al path canónico, actualizar referencias y actualizar el resumen final del warrior-prometheus.

## Ejemplos

### Correcto

```
docs/
└── scheduled-payments/
    ├── entities/
    │   ├── scheduled-transfer.md
    │   └── transfer-approval.md
    ├── oas/
    │   └── openapi.yaml
    └── events/
        └── events.md
```

### Incorrecto

```
docs/
├── domain/platform-domain-model.md     # ❌ no existe paths.domain
├── oas/scheduled-transfers-api.yaml    # ❌ fuera de docs/{context}/oas/
└── events/scheduled-transfers.md       # ❌ fuera de docs/{context}/events/
```

```
docs/
└── scheduled-payments/
    └── domain-model.md                 # ❌ la categoría "domain-model" no existe; el modelo de dominio se distribuye entre entities/, events/ y oas/
```

## Validación Automatizada

- **Herramienta:** verificación por agente al persistir; lint de PR que valida el regex `^docs/[a-z][a-z0-9-]*/(entities|oas|events|agents|metrics)/[^/]+$` para todo archivo nuevo en `docs/`.
- **Momento:** al final de cada fase del diseño, en el Gate 1 del flujo Issue-Driven (alcance) y en el PR.
- **Métrica:** 0 documentos de diseño fuera de la estructura canónica en `main`; 100% de las features con Bounded Contexts identificados producen subdirectorios coherentes en `docs/`.

## Referencias

- `codex-feature-design-docs` — manual con templates de cada categoría
- `kata-feature-design-docs` — procedimiento para crear y actualizar los documentos
- `lex-entities`, `lex-entity-naming` — estructura y nomenclatura de entidades
- `lex-cloudevents`, `codex-cloudevents` — formato de eventos
- `codex-oas-structure` — estructura del OpenAPI
- `warrior-prometheus` — orquestador del ciclo de diseño que aplica esta Lexis
