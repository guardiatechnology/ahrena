# Kata: Revisión de CloudEvents

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — revisión de conformidad de documentación, publishers y consumers de CloudEvents contra Lexis y Codex Guardia

## Objetivo

Este Kata define el procedimiento para **revisar cambios relacionados con CloudEvents** (documentación en `docs/{context}/events/events.md`, código de publisher y consumer, definiciones de schema y payload) contra Lexis y Codex de CloudEvents de Guardia, identificando violaciones de conformidad, lagunas, breaking changes, y produciendo un reporte de revisión estructurado con findings clasificados por severidad. Es el par simétrico de `kata-api-design-review` para la superficie de eventos.

## Cuándo Usar

- Cuando un PR modifica `events.md` o cualquier archivo bajo `docs/{context}/events/`
- Cuando un PR modifica código que publica o consume CloudEvents (publishers, handlers de consumer, definiciones de event schema)
- Cuando es invocado por `warrior-argos` durante una revisión de Pull Request multi-eje
- Cuando `cry-review-pr` es disparado y el diff toca superficies de eventos

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Diff o ruta del events.md | Sí | Ruta del archivo `events.md` modificado o diff unificado conteniendo cambios en la superficie de eventos |
| Versión antigua del events.md (para verificación de breaking change) | No | Si se omite, el kata obtiene `git show HEAD~1:<path>` de la branch base al revisar un PR |
| Nombre del Bounded Context | No | Si se omite, infiere desde la ruta `docs/{context}/events/events.md` |
| Modo de corrección | No | `report` (por defecto) — solo findings; `fix` — propone correcciones inline junto con findings |

## Workflow

```
Progreso:
- [ ] 1. Leer directives y localizar la superficie de eventos
- [ ] 2. Consultar Lexis y Codex
- [ ] 3. Validar formato del type y nomenclatura
- [ ] 4. Validar presencia de idempotencykey
- [ ] 5. Validar payload (data) contra catálogo de entidades
- [ ] 6. Validar tamaño y serialización
- [ ] 7. Detectar breaking changes contra la versión base
- [ ] 8. Validar publishers y consumers (cuando estén en el diff)
- [ ] 9. Producir reporte de revisión
```

### Paso 1: Leer Directives y Localizar la Superficie de Eventos

1. Leer `.ahrena/.directives` para obtener `language.default`
2. Identificar la superficie de eventos en el diff:
   - Documentación: archivos que coincidan con `docs/*/events/events.md`
   - Código: archivos que importan o emiten CloudEvents (heurística: grep por `event.guardia.`, `idempotencykey`, `cloudevents`)
3. Si ni documentación ni código tocan la superficie de eventos, salir temprano con `not applicable: no event surface in diff`
4. Registrar el Bounded Context inferido desde la ruta

### Paso 2: Consultar Lexis y Codex

1. Consultar **lex-cloudevents** — los eventos DEBEN seguir CloudEvents (estructura, propiedades obligatorias, idempotencykey, JSON, tamaño < 12KB)
2. Consultar **codex-cloudevents** — estructura del evento, formato del type `event.guardia.{module}.{entity_type}.{event_name}`, formato de `data` por codex-entities
3. Consultar **lex-entities** y **codex-entities** — campos de la entidad en `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitido)
4. Consultar **lex-entity-naming** — `entity_type`, nombres de campo JSON y segmentos del type CloudEvents DEBEN estar en snake_case
5. Consultar **lex-idempotency** y **codex-idempotency** — idempotencykey obligatorio en todo evento publicado; los consumers DEBEN deduplicar
6. Consultar **lex-feature-design-docs** — estructura canónica bajo `docs/{context}/events/events.md`

### Paso 3: Validar Formato del Type y Nomenclatura

Para cada evento documentado o emitido en el diff:

1. **Regex del type** — DEBE coincidir con `^event\.guardia\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`. Marcar cualquier desvío como 🔴 BLOCKER.
2. **Segmento module** — declarado y estable; renombrar un module existente es breaking change
3. **Segmento entity_type** — snake_case singular (e.g., `scheduled_transfer`, no `scheduledTransfer` ni `scheduled_transfers`)
4. **Segmento event_name** — verbo en snake_case en participio pasado (e.g., `created`, `approved`, `executed`, `cancelled`)
5. **Presencia en el catálogo** — todo type documentado DEBE aparecer en la tabla del catálogo de eventos en la parte superior de `events.md`

### Paso 4: Validar Presencia de idempotencykey

Para cada evento documentado o emitido:

1. **En la documentación** — todo ejemplo JSON en `events.md` DEBE incluir `idempotencykey` a nivel del envelope
2. **En el código publisher** — todo call site que construye un CloudEvent DEBE definir `idempotencykey` (típicamente igual al `entity_id` del request originador)
3. **En el código consumer** — los handlers DEBEN persistir `(type, idempotencykey)` y cortocircuitar en duplicado
4. Marcar cualquier evento sin `idempotencykey` como 🔴 BLOCKER citando `lex-idempotency`

### Paso 5: Validar Payload (data) Contra Catálogo de Entidades

Para cada evento cuyo `data` representa una entidad persistente:

1. **entity_id** — presente, tipado como UUID v7
2. **entity_type** — presente, snake_case, coincide con el segmento del type
3. **created_at, updated_at** — presentes como timestamps ISO 8601
4. **version** — presente cuando optimistic locking está documentado para la entidad
5. **history** — DEBE ser omitido de `data` (por lex-entities)
6. **Nomenclatura de campos** — todos los campos de `data` DEBEN ser snake_case (por lex-entity-naming)
7. **Cross-referencia** — los campos en `data` DEBEN existir en el catálogo `docs/{context}/entities/{entity}.md` correspondiente. Marcar cualquier campo presente en `data` pero ausente del catálogo de la entidad como 🟡 WARNING (catálogo desactualizado) o 🔴 BLOCKER (filtración silenciosa de campo interno)

### Paso 6: Validar Tamaño y Serialización

1. **Serialización** — JSON UTF-8 (por lex-cloudevents)
2. **Tamaño** — payload < 12KB. Cuando el diff incluye un ejemplo representativo, calcular el tamaño en bytes y marcar si ≥ 12KB
3. **Content-Type** — `datacontenttype: application/json` declarado

### Paso 7: Detectar Breaking Changes Contra la Versión Base

Para cada evento presente en **ambas** versiones (base y nueva) del `events.md` (o schema):

| Cambio | Severidad | Razón |
|--------|-----------|-------|
| `type` renombrado (cualquier segmento alterado) | 🔴 BLOCKER | Consumers suscritos al type antiguo silenciosamente dejan de recibir |
| Campo obligatorio removido de `data` | 🔴 BLOCKER | Consumers que leen el campo se rompen |
| Tipo de campo restringido (e.g., `string` → `enum<a,b>`) | 🔴 BLOCKER | Valores existentes se vuelven inválidos |
| Campo obligatorio agregado sin plan de backfill | 🔴 BLOCKER | Consumers antiguos lo desconocen; emisores publicando sin él rompen el contrato |
| Campo renombrado | 🔴 BLOCKER | Equivalente a remover + agregar |
| Campo opcional agregado con default | 🟡 WARNING | Los consumers DEBERÍAN ignorar campos desconocidos, pero marcar para conciencia |
| Segmento `module` de una entidad existente alterado | 🔴 BLOCKER | El ruteo de tópicos se rompe |

Método de detección: comparar la tabla del catálogo de eventos (entity_type × event_name × type) y la lista de campos `data` por evento. Usar git: `git show <base-sha>:<path>` versus actual.

Para eventos **solo en la versión nueva** (agregados): ningún breaking change — registrar como 🟡 WARNING solo cuando la entidad correspondiente existe en la base pero el diagrama de lifecycle no incluye el nuevo estado.

### Paso 8: Validar Publishers y Consumers (cuando estén en el diff)

Cuando código de publisher o consumer está en el diff:

1. **Publisher** — confirmar que el call site:
   - define el segmento `type` conforme el catálogo
   - incluye `idempotencykey`
   - serializa `data` con campos en snake_case
   - propaga el trace context conforme `lex-observability-required`
2. **Consumer** — confirmar que el handler:
   - se suscribe al `type` catalogado (sin typos)
   - verifica idempotencia antes de procesar
   - retorna ACK después de la persistencia (no antes)
   - registra fallas con correlation_id sin exponer PII

### Paso 9: Producir Reporte de Revisión

Generar un reporte de revisión Markdown estructurado:

1. **Encabezado** — superficie de eventos revisada (rutas, total de eventos, total de publishers/consumers en el diff), veredicto general:
   - ✅ **Conforme** — cero BLOCKERs y cero WARNINGs
   - 🟡 **Warnings** — cero BLOCKERs, uno o más WARNINGs
   - 🔴 **Violaciones** — uno o más BLOCKERs
2. **Tabla de findings** — una fila por finding:

   | Severidad | Evento / Archivo | Lexis / Codex | Finding | Sugerencia |
   |-----------|------------------|---------------|---------|------------|

   Niveles de severidad:
   - `🔴 BLOCKER` — violación de Lexis o breaking change; DEBE ser corregido antes del merge
   - `🟡 WARNING` — desvío de Codex o punto no bloqueante; DEBERÍA ser corregido en este PR o en un follow-up

3. **Resumen de conteos** — total BLOCKER / WARNING
4. **Matriz de breaking change** — cuando el Paso 7 encuentre algo, listar antiguo → nuevo con el tipo de cambio
5. **Próximos pasos** — en modo `fix`, anexar corrección inline para cada BLOCKER y WARNING; en modo `report`, listar los eventos que requieren atención

Si no hay findings, declarar: "Superficie de eventos totalmente conforme con Lexis y Codex Guardia; ningún breaking change detectado."

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Reporte de revisión | Markdown | Retornado al llamador (típicamente `warrior-argos`) para inclusión en el review-comment consolidado del PR |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Ruta del diff: docs/scheduled-payments/events/events.md
SHA base: 12bf878 (main)
Modo de corrección: report
```

### Output de Ejemplo (resumen)

```markdown
## Revisión de CloudEvents — docs/scheduled-payments/events/events.md

**Eventos revisados:** 6 | **Veredicto:** 🔴 1 BLOCKER, 2 WARNINGs

| Severidad | Evento / Archivo | Regla | Finding | Sugerencia |
|-----------|------------------|-------|---------|------------|
| 🔴 BLOCKER | event.guardia.platform.scheduledTransfer.approved | lex-entity-naming | Segmento entity_type en camelCase | Renombrar a `scheduled_transfer` (snake_case) |
| 🟡 WARNING | event.guardia.platform.scheduled_transfer.executed | lex-cloudevents | data.failure_reason marcado opcional pero ausente del catálogo de la entidad | Agregar `failure_reason` en docs/scheduled-payments/entities/scheduled-transfer.md |
| 🟡 WARNING | tabla del catálogo events.md | codex-feature-design-docs | Columna Consumers ausente | Llenar la columna Consumers para todas las filas |

**Matriz de breaking change:** ninguna.

**Próximos pasos:** corregir 1 BLOCKER antes del merge; tratar 2 WARNINGs en este PR o abrir Issue de follow-up.
```

## Restricciones

- Este Kata produce solo un reporte de revisión; no modifica documentación ni código a menos que el modo `fix` se solicite explícitamente
- Toda divergencia DEBE ser clasificada como 🔴 BLOCKER (violación de Lexis o breaking change) o 🟡 WARNING (desvío de Codex o no bloqueante) — nunca aceptar silenciosamente
- Escalar al humano cuando una divergencia pueda ser una excepción intencional que requiera un ADR
- No marcar divergencias en eventos explícitamente excluidos del alcance de la revisión
- La verificación de breaking change requiere versión base; si no está disponible, omitir el Paso 7 y reportar `breaking-change check skipped: base version unavailable` como 🟡 WARNING

## Referencias

- `lex-cloudevents`, `codex-cloudevents`
- `lex-entities`, `codex-entities`, `lex-entity-naming`
- `lex-idempotency`, `codex-idempotency`
- `lex-feature-design-docs`, `codex-feature-design-docs`
- `lex-observability-required`
- `kata-api-design-review` — par simétrico para contratos de API HTTP
- `kata-events-doc` — contraparte de autoría
- [CloudEvents Specification](https://cloudevents.io/)
