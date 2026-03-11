# Cry: Event Storm — Documentación de Eventos CloudEvents

> **Prefijo:** `cry-` | **Tipo:** Comando Recorrente | **Alcance:** Atajo para documentar eventos CloudEvents de una feature o módulo conforme a Lexis y Codex de Guardia

## Descripción

Este comando invoca al Warrior Kronos (o al agente asumiendo su rol) para realizar event storm y documentar los eventos CloudEvents de una feature o módulo: consultar lex-cloudevents y codex-cloudevents, catalogar tipos de evento y producir documentación en Markdown en **paths.events** (docs/events).

## Uso

```
/cry-event-storm <contexto de la feature o módulo> [source base]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `contexto de la feature o módulo` | Sí | Nombre del módulo, entidades involucradas y operaciones que emiten eventos (ej.: created, updated, cancelled) o lista explícita de tipos de evento | "Módulo platform, entidad scheduled_transfer: eventos created (tras POST), updated (tras PATCH), cancelled (tras DELETE)" |
| `source base` | No | Base de la URI `source` (ej.: https://tenant.guardia.finance/platform/api/v1). Si se omite, el agente propone conforme codex-cloudevents | `https://tenant.guardia.finance/platform/api/v1` |

## Qué Hace el Comando

1. Interpreta el contexto de la feature/módulo y el source base (si se informa)
2. Asume el rol del Warrior Kronos (especialista en Event Storm) o delega al agente que ejecuta **kata-events-doc**
3. El Warrior Kronos (vía kata-events-doc) consulta lex-directives, lex-cloudevents, codex-cloudevents, lex-entities, codex-entities, lex-idempotency y codex-idempotency
4. Identifica tipos de evento (formato event.guardia.{module}.{entity_type}.{event_name}), source, subject, data e idempotencykey
5. Produce documento Markdown de eventos (ej.: events.md, cloudevents.md) con catálogo y detalles por tipo
6. Persiste en **paths.events** (`.ahrena/.directives`; predeterminado `docs/events`) y entrega resumen o inline

## Prompt Template

```
Contexto:
- Contexto de la feature/módulo: {{contexto de la feature o módulo}}
- Source base (opcional): {{source base}}

Tarea:
Actúe como el Warrior Kronos (Especialista en Event Storm) y ejecute de forma iterativa el **kata-events-doc** (el Kata consulta lex-cloudevents, codex-cloudevents y demás Lexis/Codex conforme su documentación). Con base en el contexto anterior, haga preguntas de clarificación cuando sea necesario y refine el catálogo con base en las respuestas. Produzca la documentación de eventos en paths.events.

Formato de salida:
- Consultar **paths.events** en `.ahrena/.directives` para el destino (predeterminado docs/events)
- Crear el directorio (paths.events) si no existe en el proyecto
- Crear o actualizar el documento de eventos (ej.: events.md) en ese path
- Tabla de eventos (type, descripción, cuándo se emite); para cada evento: type, source, subject, idempotencykey, estructura de data conforme codex-entities
```

## Ejemplo de Invocación

**Input:**

```
/cry-event-storm "Módulo platform, entidad scheduled_transfer: eventos created, updated y cancelled"
```

**Output esperado:**

Respuesta estructurada del Warrior Kronos con:
- Catálogo de tipos (ej.: event.guardia.platform.scheduled_transfer.created, .updated, .cancelled)
- Para cada tipo: descripción, source, subject, idempotencykey, estructura de data
- Documento creado o actualizado en el path **paths.events** (`.ahrena/.directives`; directorio creado si no existía)

## Restricciones

- El Cry no implementa código; solo dispara la documentación de eventos
- El contexto debe permitir identificar módulo, entidades y eventos; si es vago, el agente puede pedir complemento
- Excepciones a las Lexis deben documentarse en ADR

## Kata y Warrior Asociados

- **kata-events-doc** — Documentación de eventos CloudEvents (Markdown) en paths.events
- **warrior-kronos** — Especialista en Event Storm; ejecuta kata-events-doc

## Referencias

- `kata-events-doc` — Procedimiento ejecutado por el Warrior Kronos (el Kata consulta las Lexis y Codex de eventos, entidades e idempotencia; ver documentación del Kata)
