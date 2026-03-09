# Kata: Documentación de Eventos CloudEvents

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — documentación de eventos CloudEvents para una feature o módulo

## Objetivo

Este Kata define el procedimiento para **producir documentación en Markdown** de los eventos CloudEvents de una feature o módulo: consultar lex-cloudevents y codex-cloudevents, identificar los tipos de evento (formato `event.guardia.{module}.{entity_type}.{event_name}`), documentar estructura, payload (data), idempotencia y persistir el documento en **paths.events** en conformidad con las reglas de la Guardia.

## Cuándo Usar

- Cuando una feature o módulo publica o consume eventos y es necesario catalogar y documentar esos eventos
- Cuando se invoca por el Warrior especialista en Event Storm (ej.: Kronos) o por el cry-event-storm
- Cuando es necesario generar o actualizar la doc de eventos en paths.events (ej.: `events.md`, `cloudevents.md`)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Contexto de la feature o módulo | Sí | Nombre del módulo, entidades involucradas y operaciones que emiten eventos (ej.: transaction.created, transaction.updated) o lista explícita de tipos de evento |
| Base path / source | No | Base de la URI `source` (ej.: `https://tenant.guardia.finance/platform/api/v1`). Si se omite, el agente propone conforme codex-cloudevents |
| Documento existente | No | Si existe doc de eventos en paths.events, actualizar en vez de crear desde cero |

## Workflow

```
Progreso:
- [ ] 1. Leer directivas y contexto
- [ ] 2. Consultar Lexis y Codex CloudEvents
- [ ] 3. Identificar tipos de evento y payloads
- [ ] 4. Documentar cada evento (type, source, subject, data, idempotencykey)
- [ ] 5. Producir documento Markdown de eventos
- [ ] 6. Validación final
```

### Paso 1: Leer Directivas y Contexto

1. Leer `.ahrena/.directives` para obtener **paths.events** (destino de la doc de eventos; predeterminado `docs/events`)
2. Confirmar el contexto de la feature/módulo (entidades, operaciones que emiten eventos). Si es insuficiente, hacer preguntas al usuario (¿qué eventos? ¿created/updated/deleted? ¿entidades involucradas?) y esperar respuestas
3. Verificar si ya existe documento de eventos en paths.events (ej.: `events.md`, `cloudevents.md`) para actualizar o crear nuevo

### Paso 2: Consultar Lexis y Codex CloudEvents

1. Consultar **lex-directives** (obligatorio)
2. Consultar **lex-cloudevents** — los eventos deben seguir CloudEvents (estructura, propiedades obligatorias, idempotencykey, JSON, tamaño < 12KB)
3. Consultar **codex-cloudevents** — estructura del evento (id, source, specversion, type, time, datacontenttype, subject, idempotencykey, data); formato de type `event.guardia.{module}.{entity_type}.{event_name}`; shape de `data` conforme codex-entities
4. Consultar **lex-entities** y **codex-entities** — campos de entidad en `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitido)
5. Consultar **lex-idempotency** y **codex-idempotency** — idempotencykey obligatorio; consumidores deben deduplicar

### Paso 3: Identificar Tipos de Evento y Payloads

1. Listar **tipos de evento** en el formato `event.guardia.{module}.{entity_type}.{event_name}` (ej.: `event.guardia.platform.transaction.created`, `event.guardia.platform.scheduled_transfer.cancelled`)
2. Para cada tipo, definir: **source** (URI base + entity_type + entity_id cuando aplique), **subject** (`{entity_type}/{entity_id}`), **data** (campos conforme codex-entities; sin history)
3. Garantizar que cada evento tenga **idempotencykey** documentado y que el tamaño del evento sea inferior a 12KB
4. Mapear entidades referenciadas en `data` a los campos obligatorios de codex-entities

### Paso 4: Documentar Cada Evento (type, source, subject, data, idempotencykey)

Para cada evento catalogado, documentar:

1. **type** — nombre completo del tipo (event.guardia.{module}.{entity_type}.{event_name})
2. **Descripción** — cuándo se emite el evento (ej.: tras creación de transferencia agendada)
3. **source** — patrón de la URI de origen (conforme codex-cloudevents)
4. **subject** — formato `{entity_type}/{entity_id}`
5. **idempotencykey** — obligatorio; consumidores deben registrar y deduplicar por clave y hash
6. **data** — estructura del payload (entity_id, entity_type, y demás campos conforme codex-entities); indicar que history debe omitirse
7. **Ejemplo** (opcional) — snippet JSON del evento conforme codex-cloudevents

### Paso 5: Producir Documento Markdown de Eventos

1. Obtener **paths.events** en `.ahrena/.directives`. Garantizar que el directorio exista; si no existe, crearlo
2. Generar o actualizar **documento Markdown** (ej.: `events.md`, `cloudevents.md`) en paths.events conteniendo:
   - Título y resumen (módulo/feature)
   - Tabla de eventos (type, descripción, cuándo se emite)
   - Para cada evento: type, descripción, source, subject, idempotencykey, estructura de `data`, ejemplo cuando sea útil
   - Notas: serialización JSON UTF-8, tamaño < 12KB, consumidores idempotentes (conforme lex-idempotency)
3. Si ya existe doc de eventos en el path, **fusionar** los nuevos eventos en la estructura existente (por módulo o por entity_type) en vez de sobrescribir
4. Guardar en **paths.events**. Si el usuario solicita entrega inline, entregar también en el chat

### Paso 6: Validación Final

Antes de entregar el output, verificar:

- [ ] Todos los eventos siguen lex-cloudevents (estructura, type catalogado, idempotencykey, data conforme codex-entities)
- [ ] Tipo en formato event.guardia.{module}.{entity_type}.{event_name}
- [ ] data sin history; campos obligatorios de entidad documentados
- [ ] Documento está completo (tabla de eventos, detalles por tipo) y sin contradicción con las Lexis
- [ ] Documento fue guardado en el path **paths.events** (directorio creado si no existía)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Documento de eventos CloudEvents | Markdown (.md) | Directorio **paths.events** en `.ahrena/.directives` (predeterminado `docs/events`; crear directorio si no existe; crear o actualizar el archivo, ej.: events.md) |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Módulo: platform. Entidades: scheduled_transfer. Eventos: created (tras POST), updated (tras PATCH), cancelled (tras DELETE).
```

### Output de Ejemplo (resumido)

Archivo `events.md` (o `cloudevents.md`) en **paths.events** con:
- event.guardia.platform.scheduled_transfer.created — tras creación; source, subject, idempotencykey; data con entity_id, entity_type, created_at, updated_at, version, etc.
- event.guardia.platform.scheduled_transfer.updated
- event.guardia.platform.scheduled_transfer.cancelled

Cada uno con descripción, source, subject, data y ejemplo JSON conforme codex-cloudevents.

## Restricciones

- Este Kata produce solo documentación de eventos; no implementa publicadores ni consumidores
- No altera documentación ya publicada sin justificación y ADR
- Excepciones a las Lexis deben documentarse en ADR
- El agente debe escalar a humano cuando haya duda sobre fronteras de módulo o tipos de evento no catalogados

## Referencias

- lex-directives, lex-cloudevents, lex-entities, lex-idempotency
- codex-cloudevents, codex-entities, codex-idempotency
- [CloudEvents Specification](https://cloudevents.io/)
