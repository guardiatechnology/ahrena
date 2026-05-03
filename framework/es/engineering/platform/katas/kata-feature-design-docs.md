# Kata: Crear y Actualizar Documentos de Diseño de Feature

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — producción de los documentos `entities/`, `oas/` y `events/` en `docs/{context}/` durante el ciclo de diseño de feature

## Objetivo

Producir o actualizar los documentos de diseño de una feature en la estructura canónica `docs/{context}/{categoria}/` definida por `lex-feature-design-docs` y detallada en `codex-feature-design-docs`. Este Kata es el procedimiento operacional consumido por `warrior-theseus` (entidades), `warrior-daedalus` (OAS) y `warrior-kronos` (eventos), invocado directa o indirectamente por `warrior-prometheus` en cada fase del ciclo de diseño.

## Cuándo Usar

- En cualquier fase del ciclo de diseño de feature orquestado por `warrior-prometheus` en la que un artefacto de diseño (entidades, OAS o eventos) deba persistirse
- Cuando `warrior-theseus`, `warrior-daedalus` o `warrior-kronos` necesite grabar o actualizar su output
- Cuando una feature en mantenimiento requiere revisión de la estructura de documentos
- Cuando se inicia un nuevo Bounded Context y la estructura de carpetas debe crearse desde cero

## Inputs

| Entrada | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Bounded Context | Sí | Nombre del contexto en PascalCase (será convertido a kebab-case). Ej.: `ScheduledPayments` |
| Categoría | Sí | Una de: `entities`, `oas`, `events` (categorías `agents`, `metrics` reservadas) |
| Contenido | Sí | Modelo de dominio, especificación OpenAPI o catálogo de eventos a documentar |
| Module CloudEvents | Sí cuando categoría = `events` | Segmento `{module}` del tipo CloudEvents (ej.: `platform`) |
| Operación | Sí | `create` (nuevo archivo) o `update` (fusionar con existente preservando secciones estables) |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Leer Lexis y Codex aplicables
- [ ] 2. Resolver path canónico
- [ ] 3. Garantizar estructura de carpetas
- [ ] 4. Aplicar template de la categoría
- [ ] 5. Verificar conformidad
- [ ] 6. Grabar o actualizar archivo
- [ ] 7. Actualizar referencias cruzadas
- [ ] 8. Validación final
```

### Paso 1: Leer Lexis y Codex Aplicables

1. Consultar **`lex-feature-design-docs`** — la estructura `docs/{context}/{categoria}/` es obligatoria; las categorías son fijas
2. Consultar **`codex-feature-design-docs`** — template específico de la categoría que se producirá
3. Para `entities/`: consultar adicionalmente `lex-entities`, `lex-entity-naming`, `codex-entities`
4. Para `oas/`: consultar adicionalmente `codex-oas-structure`, `codex-restful-payload`, `codex-restful-headers`, `codex-restful-pagination`, `codex-restful-status-codes`
5. Para `events/`: consultar adicionalmente `lex-cloudevents`, `codex-cloudevents`, `lex-idempotency`, `lex-entity-naming`

### Paso 2: Resolver Path Canónico

1. Convertir el Bounded Context a kebab-case:
   - `ScheduledPayments` → `scheduled-payments`
   - `BankingIntegration` → `banking-integration`
2. Componer el directorio base: `docs/{context-kebab}/`
3. Componer el path final por categoría:
   - `entities`: `docs/{context}/entities/{entity-name-kebab}.md` (1 archivo por entidad)
   - `oas`: `docs/{context}/oas/openapi.yaml` (o `openapi-{slug}.yaml` si hay múltiples APIs)
   - `events`: `docs/{context}/events/events.md` (1 archivo por contexto)

### Paso 3: Garantizar Estructura de Carpetas

1. Verificar si `docs/{context}/` existe; crearlo si no existe
2. Verificar si la subcarpeta de la categoría existe; crearla si no existe
3. **No crear** subcarpetas de categorías reservadas (`agents/`, `metrics/`) sin instrucción explícita
4. **No crear** categorías fuera del conjunto canónico — hacerlo es violación de `lex-feature-design-docs`

### Paso 4: Aplicar Template de la Categoría

Cargar el template correspondiente del `codex-feature-design-docs` y completar:

#### Categoría `entities`

1. Encabezado con **Clasificación DDD**: Entity, Aggregate Root o Value Object
2. **Bounded Context** y **entity_type** (snake_case) en el encabezado
3. Sección **Por qué existe** — 2 a 4 frases sobre el motivo de negocio
4. Sección **Campos** — tabla con columnas `Campo | Tipo | Tamaño | Obligatorio | Descripción`. Incluir siempre los campos de la estructura base (`entity_id`, `entity_type`, `version`, `created_at`, `updated_at`, `discarded_at`) y a continuación los campos de negocio
5. Sección **Reglas de Negocio** — lista numerada (RN-1, RN-2, ...) en lenguaje de dominio
6. Sección **Invariantes** — condiciones siempre verdaderas
7. Sección **Relaciones** — tabla `Relación | Cardinalidad | Tipo | Entidad Objetivo | Observación`
8. Sección **Errores** — tabla con `code`, `reason`, `message`, cuándo ocurre, conforme a `lex-error-handling`
9. Sección **Referencias** — enlaces a `events/events.md`, `oas/openapi.yaml` y Lexis aplicables

#### Categoría `oas`

1. Estructurar OpenAPI 3.x conforme a `codex-oas-structure`
2. `info.title`, `info.version`, `info.description` apuntando al Bounded Context
3. `tags` por entidad
4. `paths` ordenados por recurso, con operaciones en el orden `POST → GET (list) → GET (item) → PATCH → DELETE`
5. `components.schemas` reutilizables derivados de las entidades en `docs/{context}/entities/`
6. `components.parameters` para paginación canónica (`page_size`, `page_token`)
7. `components.securitySchemes` (Bearer JWT) conforme a `lex-auth`
8. Cabeceras obligatorias (`Idempotency-Key`, `X-Grd-Trace-Id`) declaradas en parámetros reutilizables

#### Categoría `events`

1. Encabezado con Bounded Context y segmento `{module}` del CloudEvents
2. Sección **Visión General**
3. Sección **Catálogo** — tabla `entity_type | event_name | type completo | Publicador | Consumidores`
4. **Una sección por entidad** que emite eventos:
   - Subsección **Ciclo de Vida** con `mermaid` `stateDiagram-v2` cubriendo todos los estados posibles y transiciones
   - Subsección **Eventos** — para cada evento:
     - Bloque JSON con payload completo conforme a `codex-cloudevents` (`specversion`, `id`, `source`, `type`, `subject`, `time`, `datacontenttype`, `idempotencykey`, `data`)
     - Tabla de campos del `data`: `Campo | Tipo | Obligatorio | Descripción`
     - Líneas finales con **Idempotencia** y **Trigger** (Use Case que dispara)
5. Sección **Referencias**

### Paso 5: Verificar Conformidad

Antes de grabar:

- [ ] ¿El path está exactamente en `docs/{context}/{categoria}/...`?
- [ ] ¿El nombre del archivo respeta las convenciones (`{entity-name}.md`, `openapi.yaml`, `events.md`)?
- [ ] ¿La categoría pertenece al conjunto canónico (`entities`, `oas`, `events`)?
- [ ] ¿El contenido sigue el template correspondiente de `codex-feature-design-docs`?
- [ ] Para `entities`: ¿están presentes las 7 secciones obligatorias (Clasificación DDD, Por qué existe, Campos, Reglas de Negocio, Invariantes, Relaciones, Errores, Referencias)?
- [ ] Para `entities`: ¿la tabla de Campos incluye la estructura base de `lex-entities`?
- [ ] Para `oas`: ¿el archivo es YAML válido y sigue `codex-oas-structure`?
- [ ] Para `events`: ¿cada entidad tiene `stateDiagram-v2` y cada evento tiene payload CloudEvents completo?
- [ ] Para `events`: ¿todos los tipos siguen `event.guardia.{module}.{entity_type}.{event_name}` en snake_case (lex-entity-naming)?

### Paso 6: Grabar o Actualizar Archivo

1. En **`create`**: grabar el archivo en el path resuelto
2. En **`update`**:
   - Leer el archivo existente
   - Identificar secciones que cambiaron (nuevos campos, nuevos eventos, nuevos endpoints) y secciones estables (descripciones, referencias cruzadas)
   - Fusionar preservando comentarios humanos cuando sea posible; sustituir tablas y bloques canónicos por las versiones nuevas
   - No remover silenciosamente una sección que existía — señalar el cambio al usuario si la remoción es intencional
3. No grabar archivo vacío o con placeholders `{...}` no completados

### Paso 7: Actualizar Referencias Cruzadas

Cuando la categoría afecta a otra:

| Cambio | Actualizar |
|--------|------------|
| Nuevo evento de una entidad | `entities/{entity}.md` (sección Referencias) y `events/events.md` (catálogo) |
| Nuevo campo en entidad | `oas/openapi.yaml` (schema) y `events/events.md` (payload si es relevante) |
| Nuevo endpoint REST | `entities/{entity}.md` (sección Referencias) |
| Renombrado de entidad | nombre del archivo, `entity_type`, schemas OAS, segmento `{entity_type}` en todos los tipos CloudEvents |

### Paso 8: Validación Final

- [ ] Archivo grabado en path canónico (`docs/{context}/{categoria}/...`)
- [ ] Conformidad con template de `codex-feature-design-docs` confirmada
- [ ] Referencias cruzadas actualizadas donde aplique
- [ ] Lexis aplicables (`lex-feature-design-docs`, `lex-entities`, `lex-entity-naming`, `lex-cloudevents`, `lex-idempotency`, `lex-error-handling`) respetadas
- [ ] El idioma coincide con `language.default` en `.ahrena/.directives`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Archivo de entidad | Markdown | `docs/{context}/entities/{entity-name}.md` |
| Especificación OpenAPI | YAML | `docs/{context}/oas/openapi.yaml` |
| Documento de eventos | Markdown | `docs/{context}/events/events.md` |

## Ejemplo de Ejecución

### Input

```
Bounded Context: ScheduledPayments
Categoría: entities
Operación: create
Contenido:
  Entidad: ScheduledTransfer (Aggregate Root)
  entity_type: scheduled_transfer
  Por qué existe: separa intención de ejecución de transferencias bancarias con aprobación obligatoria
  Campos de negocio: scheduled_date (date), amount (integer cents), currency (ISO 4217), source_account_id (UUID), target_account_id (UUID), status (enum), approver_id (UUID, nullable)
  Reglas: programación hasta 90 días hábiles en el futuro; solo admin aprueba; no permite ejecución sin approval
```

### Output Resumido

Archivo `docs/scheduled-payments/entities/scheduled-transfer.md`:

```markdown
# Entity: ScheduledTransfer

> **Clasificación DDD:** Aggregate Root
> **Bounded Context:** scheduled-payments
> **entity_type:** `scheduled_transfer`

## Por qué existe

Representa una transferencia bancaria ordenada por un contador para ejecución en fecha futura. Existe para separar la intención (programación) de la ejecución (procesamiento) y permitir el ciclo de aprobación obligatoria por supervisor antes de que los valores se muevan.

## Campos

| Campo | Tipo | Tamaño | Obligatorio | Descripción |
|-------|------|--------|:-----------:|-------------|
| `entity_id` | UUID v7 | 36 | Sí | Identificador único |
| `entity_type` | string | — | Sí | Siempre `scheduled_transfer` |
| `version` | integer | — | Sí | Versión optimista |
| `created_at` | datetime | — | Sí | Creación |
| `updated_at` | datetime | — | Sí | Última actualización |
| `discarded_at` | datetime | — | No | Soft delete |
| `scheduled_date` | date | — | Sí | Fecha programada (≤ 90 días hábiles en el futuro) |
| `amount` | integer | — | Sí | Valor en centavos |
| `currency` | string | 3 | Sí | ISO 4217 |
| `source_account_id` | UUID v7 | 36 | Sí | Cuenta de origen |
| `target_account_id` | UUID v7 | 36 | Sí | Cuenta de destino |
| `status` | enum<requested,approved,executed,failed,cancelled> | — | Sí | Estado actual |
| `approver_id` | UUID v7 | 36 | No | Supervisor que aprobó |

## Reglas de Negocio

1. **RN-1 — Ventana de programación:** `scheduled_date` debe ser día hábil dentro de los 90 días futuros.
2. **RN-2 — Aprobación obligatoria:** La transición `requested → approved` exige `approver_id` con perfil supervisor.
3. **RN-3 — Ejecución condicionada:** La transición a `executed` solo ocurre desde `approved`.

## Invariantes

- **INV-1:** `amount > 0`.
- **INV-2:** `status` sigue exactamente las transiciones del diagrama en `events/events.md`.
- **INV-3:** Después de `executed`, la entidad es inmutable excepto `updated_at`.

## Relaciones

| Relación | Cardinalidad | Tipo | Entidad Objetivo | Observación |
|----------|--------------|------|------------------|-------------|
| references | N..1 | referencia | `Account` | source y target |
| owns | 1..N | composición | `TransferApproval` | rastro de aprobación |

## Errores

| Code | Reason | Mensaje | Cuándo ocurre |
|------|--------|---------|---------------|
| `ERR400_INVALID_PARAMETER` | `INVALID_SCHEDULED_DATE` | "scheduled_date must be a future business day within 90 days" | RN-1 |
| `ERR403_FORBIDDEN` | `APPROVER_NOT_AUTHORIZED` | "approver does not have supervisor role" | RN-2 |
| `ERR409_CONFLICT` | `INVALID_STATE_TRANSITION` | "transfer cannot move from {from} to {to}" | INV-2 |

## Referencias

- `lex-entities`, `lex-entity-naming`, `lex-error-handling`
- `docs/scheduled-payments/events/events.md`
- `docs/scheduled-payments/oas/openapi.yaml`
```

## Restricciones

- Este Kata **no** decide el contenido del diseño — entrega el documento conforme al input ya producido por el warrior responsable (Theseus, Daedalus, Kronos)
- **Nunca** guardar fuera de `docs/{context}/{categoria}/` — viola `lex-feature-design-docs`
- **Nunca** usar paths configurables como `paths.domain`, `paths.oas`, `paths.events` — esos paths ya no existen en `.ahrena/.directives`
- **Nunca** mezclar dos categorías en un mismo archivo (ej.: payload de evento dentro de `entities/{e}.md`)
- Cuando `update` borra una sección que existía, **señalar al usuario** antes de grabar
- El idioma del documento conforme a `language.default` en `.ahrena/.directives`

## Referencias

- `lex-feature-design-docs` — Ley
- `codex-feature-design-docs` — templates
- `lex-entities`, `lex-entity-naming`, `codex-entities`
- `lex-cloudevents`, `codex-cloudevents`
- `codex-oas-structure`, `codex-restful-payload`, `codex-restful-headers`, `codex-restful-pagination`, `codex-restful-status-codes`
- `lex-error-handling`, `codex-error-handling`, `codex-known-errors`
- `lex-idempotency`, `codex-idempotency`
- `lex-auth`, `codex-auth`
- `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus`, `warrior-kronos`
