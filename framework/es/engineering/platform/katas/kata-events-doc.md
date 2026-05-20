# Kata: Documentación de Eventos CloudEvents

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — documentación de eventos CloudEvents para una feature o módulo

## Objetivo

Este Kata define el procedimiento para **producir documentación en Markdown** de los eventos CloudEvents de una feature o módulo: consultar `lex-cloudevents`, `codex-cloudevents` y `codex-feature-design-docs`, identificar los tipos de evento (formato `event.guardia.{domain}.{entity_name}.{event_name}`), estructurar el contenido por entidad con `stateDiagram-v2` del ciclo de vida y payload CloudEvents por evento, y delegar la persistencia a `kata-feature-design-docs` en `docs/{context}/events/events.md`.

## Cuándo Usar

- Cuando una feature o módulo publica o consume eventos y es necesario catalogar y documentar esos eventos
- Cuando se invoca por el Warrior especialista en Event Storm (ej.: Kronos) o por el cry-event-storm
- Cuando es necesario generar o actualizar la doc de eventos en `docs/{context}/events/events.md`

## Inputs

| Entrada | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Nombre del Bounded Context | Sí | Nombre del Bounded Context en PascalCase (ej.: `ScheduledPayments`) |
| Contexto de la feature o módulo | Sí | Nombre del módulo, entidades involucradas y operaciones que emiten eventos (ej.: transaction.created, transaction.updated) o lista explícita de tipos de evento |
| Base path / source | No | Base de la URI `source` (ej.: `https://tenant.guardia.finance/platform/api/v1`). Si se omite, el agente propone conforme codex-cloudevents |
| Documento existente | No | Si existe doc de eventos en `docs/{context}/events/events.md`, actualizar en vez de crear desde cero |

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

1. Leer `.ahrena/.directives` para obtener `language.default`. El destino es fijo: `docs/{context}/events/events.md` por `lex-feature-design-docs`. Confirmar con el usuario el nombre del Bounded Context en PascalCase y el segmento `{module}` del CloudEvents
2. Cargar entidades existentes en `docs/{context}/entities/` para alinear payloads y ciclo de vida
3. Confirmar el contexto de la feature/módulo (entidades, operaciones que emiten eventos). Si es insuficiente, hacer preguntas al usuario (¿qué eventos? ¿created/updated/deleted? ¿entidades involucradas?) y esperar respuestas
4. Verificar si ya existe `docs/{context}/events/events.md` para actualizar en vez de crear nuevo

### Paso 2: Consultar Lexis y Codex CloudEvents

1. Consultar **lex-directives** (obligatorio)
2. Consultar **lex-cloudevents** — los eventos deben seguir CloudEvents (estructura, propiedades obligatorias, idempotencykey, JSON, tamaño < 12KB)
3. Consultar **codex-cloudevents** — estructura del evento (id, source, specversion, type, time, datacontenttype, subject, idempotencykey, data); formato de type `event.guardia.{domain}.{entity_name}.{event_name}`; shape de `data` conforme codex-entities
4. Consultar **lex-entities** y **codex-entities** — campos de entidad en `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitido)
5. Consultar **lex-idempotency** y **codex-idempotency** — idempotencykey obligatorio; consumidores deben deduplicar

### Paso 3: Identificar Tipos de Evento y Payloads

1. Listar **tipos de evento** en el formato `event.guardia.{domain}.{entity_name}.{event_name}` (ej.: `event.guardia.financial.record.created`, `event.guardia.financial.scheduled_transfer.cancelled`)
2. Para cada tipo, definir: **source** (URI base + entity_type + entity_id cuando aplique), **subject** (`{entity_type}/{entity_id}`), **data** (campos conforme codex-entities; sin history)
3. Garantizar que cada evento tenga **idempotencykey** documentado y que el tamaño del evento sea inferior a 12KB
4. Mapear entidades referenciadas en `data` a los campos obligatorios de codex-entities

### Paso 4: Documentar Cada Evento (type, source, subject, data, idempotencykey)

Para cada evento catalogado, documentar:

1. **type** — nombre completo del tipo (event.guardia.{domain}.{entity_name}.{event_name})
2. **Descripción** — cuándo se emite el evento (ej.: tras creación de transferencia agendada)
3. **source** — patrón de la URI de origen (conforme codex-cloudevents)
4. **subject** — formato `{entity_type}/{entity_id}`
5. **idempotencykey** — obligatorio; consumidores deben registrar y deduplicar por clave y hash
6. **data** — estructura del payload (entity_id, entity_type, y demás campos conforme codex-entities); indicar que history debe omitirse
7. **Ejemplo** (opcional) — snippet JSON del evento conforme codex-cloudevents

### Paso 5: Producir Contenido del `events.md` en la Estructura Canónica

Estructurar el contenido conforme al template de `codex-feature-design-docs`:

1. **Encabezado** con Bounded Context y el segmento `{module}`
2. **Visión General** en 2-4 frases
3. **Catálogo** — tabla `entity_type | event_name | type completo | Publicador | Consumidores`
4. **Una sección por entidad que emite eventos**:
   - Subsección **Ciclo de Vida** con bloque `mermaid` `stateDiagram-v2` cubriendo todos los estados y transiciones
   - Subsección **Eventos**: para cada evento, bloque JSON con payload CloudEvents completo (`specversion`, `id`, `source`, `type`, `subject`, `time`, `datacontenttype`, `idempotencykey`, `data`), tabla `Campo | Tipo | Obligatorio | Descripción` para `data`, y líneas finales **Idempotencia** + **Trigger** (Use Case)
5. **Referencias** a `lex-cloudevents`, `codex-cloudevents`, `lex-entity-naming`, `lex-idempotency`, y los archivos en `docs/{context}/entities/`

Persistencia: invocar **`kata-feature-design-docs`** con `Bounded Context`, `Categoría` = `events`, `Contenido` = Markdown generado, `Operación` = `create` o `update`. El kata escribe en `docs/{context}/events/events.md`.

### Paso 6: Validación Final

Antes de entregar el output, verificar:

- [ ] Todos los eventos siguen lex-cloudevents (estructura, type catalogado, idempotencykey, data conforme codex-entities)
- [ ] Tipo en formato event.guardia.{domain}.{entity_name}.{event_name}
- [ ] data sin history; campos obligatorios de entidad documentados
- [ ] Documento está completo (tabla de eventos, detalles por tipo) y sin contradicción con las Lexis
- [ ] `stateDiagram-v2` presente para cada entidad que emite eventos
- [ ] Persistencia delegada a `kata-feature-design-docs` con categoría `events` (path canónico `docs/{context}/events/events.md`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Documento de eventos CloudEvents | Markdown (.md) | `docs/{context}/events/events.md` (persistido vía `kata-feature-design-docs`) |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Módulo: platform. Entidades: scheduled_transfer. Eventos: created (tras POST), updated (tras PATCH), cancelled (tras DELETE).
```

### Output de Ejemplo (resumido)

Archivo `docs/{context}/events/events.md` con:
- event.guardia.financial.scheduled_transfer.created — tras creación; source, subject, idempotencykey; data con entity_id, entity_type, created_at, updated_at, version, etc.
- event.guardia.financial.scheduled_transfer.updated
- event.guardia.financial.scheduled_transfer.cancelled

Cada uno con descripción, source, subject, data y ejemplo JSON conforme codex-cloudevents.

## Restricciones

- Este Kata produce solo documentación de eventos; no implementa publicadores ni consumidores
- No altera documentación ya publicada sin justificación y ADR
- Excepciones a las Lexis deben documentarse en ADR
- El agente debe escalar a humano cuando haya duda sobre fronteras de módulo o tipos de evento no catalogados

## Referencias

- `lex-feature-design-docs` — estructura `docs/{context}/events/`
- `codex-feature-design-docs` — template del `events.md`
- `kata-feature-design-docs` — persistencia canónica
- `kata-events-review` — contraparte de revisión para CloudEvents en momento de PR
- `lex-directives`, `lex-cloudevents`, `lex-entities`, `lex-entity-naming`, `lex-idempotency`
- `codex-cloudevents`, `codex-entities`, `codex-idempotency`
- [CloudEvents Specification](https://cloudevents.io/)
