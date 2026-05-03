# Kata: Design de API RESTful para Nueva Feature — Documento Estructurado (Markdown)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — design de APIs REST y producción de documento Markdown estructurado

> **Estado:** complementario. El artefacto canónico de API es `docs/{context}/oas/openapi.yaml` producido por `kata-api-design-oas` y persistido por `kata-feature-design-docs`. Este Kata permanece para generar documentación humana adicional bajo demanda; cuando se utiliza, el output complementa (no sustituye) al `openapi.yaml`.

## Objetivo

Este Kata define el procedimiento para diseñar la API REST de una nueva feature y **producir documentación en formato Markdown estructurado** (tablas de endpoints, métodos, status, request/response, errores): consultar Lexis y Codex, identificar recursos y operaciones, definir endpoints y persistir el documento como complemento legible al `openapi.yaml` canónico en `docs/{context}/oas/`.

## Cuándo Usar

- Cuando el formato de salida deseado es **documento Markdown** (no OpenAPI)
- Cuando una nueva feature exige exposición vía API HTTP y aún no existe contrato documentado
- Cuando se invoca por el `cry-api-design` o por el Warrior Daedalus con output en Markdown
- Cuando es necesario generar o actualizar un documento de API en `docs/{context}/oas/` para lectura humana o revisión

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Descripción de la feature | Sí | Descripción textual del dominio, entidades, operaciones y reglas de negocio relevantes para la API |
| Contexto o alcance | No | Restricciones (ej.: solo lectura, solo un recurso), base path deseado o convención existente |
| Base path | No | Prefijo de URL (ej.: `/v1/transactions`). Si se omite, el agente propone con base en la feature |

## Workflow

```
Progreso:
- [ ] 1. Leer directivas y contexto
- [ ] 2. Consultar Lexis y Codex RESTful
- [ ] 3. Identificar recursos y operaciones
- [ ] 4. Diseñar endpoints (paths, métodos, status, headers, payloads)
- [ ] 5. Documentar errores e idempotencia
- [ ] 6. Producir documento Markdown estructurado
- [ ] 7. Validación final
```

### Paso 1: Leer Directivas y Contexto

1. Identificar `language.default` en `.ahrena/.directives`; el destino canónico del documento es **`docs/{context}/oas/`** conforme a `lex-feature-design-docs`
2. Confirmar que la descripción de la feature fue proporcionada. **Trabajar de forma iterativa:** si es incompleta o ambigua, **hacer preguntas al usuario** (ej.: ¿API pública o privada? ¿Paginación y ordenación? ¿Base path? ¿Soft delete o discarded_at? ¿Filtros?) y esperar respuestas; repetir hasta que los criterios queden claros
3. Registrar el base path informado o proponer uno (ej.: `/v1/<recurso-principal>`) en kebab-case y versión en la URL cuando aplique
4. Identificar si la API es pública (Client Credentials, FAPI 2.0) o privada (JWT, RBAC) para alinear con lex-auth

### Paso 2: Consultar Lexis y Codex RESTful

1. Consultar **lex-directives** (obligatorio)
2. Consultar **lex-restful-apis** — conformidad general en endpoints HTTP
3. Consultar **codex-restful-apis** y módulos referenciados: codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting
4. Consultar **lex-entities** y **codex-entities** — estructura base de entidades (entity_id, entity_type, version, created_at, updated_at, discarded_at)
5. Consultar **lex-idempotency** y **codex-idempotency** — Idempotency-Key en mutaciones
6. Consultar **lex-error-handling** y **codex-error-handling** — estructura de errores (code, reason, message)
7. Consultar **lex-auth** y **codex-auth** — autenticación y autorización (OAuth 2.0, JWT, RBAC)

### Paso 3: Identificar Recursos y Operaciones

1. Extraer **recursos** (sustantivos) de la descripción de la feature — ej.: transacción, usuario, contrato
2. Para cada recurso, listar **operaciones** necesarias: crear, leer, actualizar, excluir (soft delete cuando aplique), listar (con paginación)
3. Identificar operaciones que **modifican estado** (POST, PATCH, PUT) y marcar como obligatorio Idempotency-Key
4. Identificar listados que exigen **paginación** (page_size, page_token) y **ordenación** (order_by, sort)
5. Mapear entidades persistentes que deben seguir la estructura base (entity_id, entity_type, version, timestamps)

### Paso 4: Diseñar Endpoints (paths, métodos, status, headers, payloads)

1. Definir **paths** en formato RESTful: recurso en plural o singular conforme convención del proyecto; identificador por path (ej.: `/v1/transactions/{entity_id}`)
2. Atribuir **métodos HTTP**: GET (lectura), POST (creación), PATCH o PUT (actualización), DELETE (exclusión lógica cuando aplique)
3. Para cada endpoint, definir **códigos de status** conforme codex-restful-status-codes (ej.: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
4. Definir **headers** obligatorios: Idempotency-Key en mutaciones; X-Grd-Trace-Id cuando aplique; Content-Type, Accept
5. Definir **payload de request**: cuerpo para POST/PATCH/PUT; parámetros de query para listado (page_size, page_token, order_by, sort)
6. Definir **payload de response**: estructura `data` (objeto o array), `pagination` cuando listado paginado, conforme codex-restful-payload
7. Garantizar que entidades en respuesta incluyan campos obligatorios de codex-entities (entity_id, entity_type, created_at, updated_at, version cuando aplique)

### Paso 5: Documentar Errores e Idempotencia

1. Para cada endpoint de mutación, documentar que **Idempotency-Key** es obligatorio; respuestas 400 (ausente), 409 (misma clave, payload distinto)
2. Listar **errores conocidos** por endpoint: códigos ERR4xx/ERR5xx, reason (conforme codex-error-handling), message orientada al desarrollador
3. Garantizar que respuestas de error usen solo la estructura `errors` (array de code, reason, message); sin exponer datos sensibles en mensajes de autenticación (lex-error-handling)
4. Documentar **paginación** en listados: parámetros de request (page_size, page_token), estructura de respuesta (pagination con first_page_token, next_page_token, etc.)

### Paso 6: Producir Documento Markdown Estructurado

1. El path canónico es **`docs/{context}/oas/`** conforme a `lex-feature-design-docs`. Garantizar que el directorio exista en la raíz del proyecto; si no existe, crearlo
2. Generar **documento Markdown** (.md) conteniendo:
   - Título y resumen de la API
   - Tabla de endpoints (path, método, resumen)
   - Para cada endpoint: parámetros (path, query, header), cuerpo de request cuando aplique, respuestas (200/201/204, 400, 401, 403, 404, 409, 422, 429, 500) con estructura de payload conforme codex-restful-payload
   - Sección de **headers globales** (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization) conforme codex-restful-headers
   - Sección de errores conocidos por endpoint (códigos, reason, message)
   - Ejemplos de request/response cuando sea útil
3. Nombrar el archivo de forma consistente (ej.: `api-scheduled-transfers.md`, `api.md`). Guardar en **docs/{context}/oas/** (crear o actualizar). Si el usuario solicita entrega inline además del archivo, entregar también en el chat

### Paso 7: Validación Final

Antes de entregar el output, verificar:

- [ ] Todos los endpoints siguen lex-restful-apis (status, payload, headers, paginación, ordenación conforme spec)
- [ ] Operaciones de mutación exigen Idempotency-Key (lex-idempotency)
- [ ] Entidades persistentes siguen estructura base (lex-entities)
- [ ] Errores siguen estructura estandarizada y códigos conocidos (lex-error-handling)
- [ ] Autenticación/autorización documentadas conforme lex-auth cuando la API sea protegida
- [ ] Listados paginados tienen page_size, page_token y estructura pagination en la respuesta
- [ ] Documento está completo (tabla de endpoints, detalles por endpoint, headers globales, errores) y sin contradicción con las Lexis
- [ ] Documento fue guardado en el path **docs/{context}/oas/** (directorio creado si no existía)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Documento de API | Markdown (.md) | Directorio **docs/{context}/oas/** (crear directorio si no existe; crear o actualizar el archivo) |
| Tabla de endpoints | Markdown | Incluida en el documento |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Feature: Módulo de agendamiento de transferencias. Crear, listar, actualizar y cancelar; listado paginado y ordenable por fecha; mutaciones idempotentes.
Base path: /v1/scheduled-transfers
```

### Output de Ejemplo (resumido)

Archivo `.md` en **docs/{context}/oas/** con:
- Tabla: `POST /v1/scheduled-transfers` (crear), `GET /v1/scheduled-transfers` (listar), `GET /v1/scheduled-transfers/{entity_id}`, `PATCH ...`, `DELETE ...`
- Para cada endpoint: parámetros, headers, request/response, status 200/201/204/400/404/409/422 etc.
- Headers globales (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization)
- Errores conocidos y payloads conforme codex-restful-payload y codex-entities

## Restricciones

- Este Kata produce solo documento Markdown; no implementa código ni genera OpenAPI
- No altera documentos ya publicados sin justificación y ADR
- Excepciones a las Lexis deben documentarse en ADR y reflejarse en el documento
- El agente debe escalar a humano cuando haya conflicto entre Lexis y requisito de negocio o cuando la feature involucre múltiples bounded contexts con fronteras de API no claras

## Referencias

- lex-directives, lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting, codex-entities, codex-idempotency, codex-error-handling, codex-auth
