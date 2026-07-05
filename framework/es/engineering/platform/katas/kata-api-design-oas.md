# Kata: Design de API RESTful para Nueva Feature — Especificación OpenAPI (OAS)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — design de APIs REST y producción de especificación OpenAPI 3.x

## Objetivo

Este Kata define el procedimiento para diseñar la API REST de una nueva feature y **producir especificación en formato OpenAPI 3.x** (YAML o JSON): consultar Lexis y Codex, identificar recursos y operaciones, definir endpoints y persistir el contrato en **docs/{context}/oas/openapi.yaml** en conformidad con las reglas de la Guardia.

## Cuándo Usar

- Cuando el formato de salida deseado es **OpenAPI 3.x** (YAML o JSON)
- Cuando una nueva feature exige exposición vía API HTTP y aún no existe contrato definido
- Cuando se invoca por el `cry-api-design` o por el Warrior Daedalus con output OAS
- Cuando es necesario generar o actualizar un archivo OAS en `docs/{context}/oas/openapi.yaml`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Descripción de la feature | Sí | Descripción textual del dominio, entidades, operaciones y reglas de negocio relevantes para la API |
| Contexto o alcance | No | Restricciones (ej.: solo lectura, solo un recurso), base path deseado o convención existente |
| Base path | No | Prefijo de URL (ej.: `/v1/transactions`). Si se omite, el agente propone con base en la feature |
| Formato OAS | No | YAML o JSON. Si se omite, se usa YAML como predeterminado |

## Workflow

```
Progreso:
- [ ] 1. Leer directivas y contexto
- [ ] 2. Consultar Lexis y Codex RESTful
- [ ] 3. Identificar recursos y operaciones
- [ ] 4. Diseñar endpoints (paths, métodos, status, headers, payloads)
- [ ] 5. Documentar errores e idempotencia
- [ ] 6. Producir especificación OpenAPI 3.x
- [ ] 7. Validación final
```

### Paso 1: Leer Directivas y Contexto

1. Leer `.ahrena/.directives` para obtener `language.default`. El destino es fijo: `docs/{context}/oas/openapi.yaml`, conforme a `lex-feature-design-docs`. Confirmar con el usuario el nombre del Bounded Context en PascalCase (se convertirá a kebab-case en la carpeta)
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
8. Consultar **codex-oas-structure** — orden de las operaciones en paths (POST, GET, PUT, PATCH, DELETE)

### Paso 3: Identificar Recursos y Operaciones

1. Extraer **recursos** (sustantivos) de la descripción de la feature — ej.: transacción, usuario, contrato
2. Para cada recurso, listar **operaciones** necesarias: crear, leer, actualizar, excluir (soft delete cuando aplique), listar (con paginación)
3. Identificar operaciones que **modifican estado** (POST, PATCH) y marcar como obligatorio Idempotency-Key
4. Identificar listados que exigen **paginación** (page_size, page_token) y **ordenación** (order_by, sort)
5. Mapear entidades persistentes que deben seguir la estructura base (entity_id, entity_type, version, timestamps)

### Paso 4: Diseñar Endpoints (paths, métodos, status, headers, payloads)

1. Definir **paths** en formato RESTful: recurso en plural o singular conforme convención del proyecto; identificador por path (ej.: `/v1/transactions/{entity_id}`)
2. Atribuir **métodos HTTP**: GET (lectura), POST (creación), PATCH o PUT (actualización), DELETE (exclusión lógica cuando aplique). Ordenar métodos HTTP por path conforme **codex-oas-structure**: POST, GET, PUT, PATCH, DELETE (omitir los no utilizados en el path, manteniendo el orden)
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

### Paso 6: Producir Especificación OpenAPI 3.x

1. Generar **documento OpenAPI 3.x** en YAML, conteniendo:
   - `openapi: 3.x`
   - `paths` con cada endpoint; en cada path, listar las operaciones en el orden **codex-oas-structure**: post, get, put, patch, delete; en cada operación: `parameters` (path, query, header), `requestBody` cuando aplique, `responses` (200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500)
   - Componentes de headers globales (Idempotency-Key, X-Grd-Trace-Id, Content-Type, Authorization) conforme codex-restful-headers
   - Schemas de request/response alineados a codex-restful-payload y codex-entities; reflejar el catálogo de campos de las entidades persistidas en `docs/{context}/entities/`
2. **Persistir vía `kata-feature-design-docs`** con:
   - `Bounded Context` = nombre en PascalCase
   - `Categoría` = `oas`
   - `Contenido` = YAML generado
   - `Operación` = `create` o `update`
   - El kata escribe en `docs/{context}/oas/openapi.yaml` y crea el directorio si es necesario
3. Si el usuario solicita entrega inline además del archivo, entregar también en el chat

### Paso 7: Validación Final

Antes de entregar el output, verificar:

- [ ] Todos los endpoints siguen lex-restful-apis (status, payload, headers, paginación, ordenación conforme spec)
- [ ] Operaciones de mutación exigen Idempotency-Key (lex-idempotency)
- [ ] Entidades persistentes siguen estructura base (lex-entities)
- [ ] Errores siguen estructura estandarizada y códigos conocidos (lex-error-handling)
- [ ] Autenticación/autorización documentadas conforme lex-auth cuando la API sea protegida
- [ ] Listados paginados tienen page_size, page_token y estructura pagination en la respuesta
- [ ] Archivo OpenAPI 3.x está completo (paths, methods, parameters, responses) y sin contradicción con las Lexis
- [ ] Orden de las operaciones en cada path sigue codex-oas-structure (POST, GET, PUT, PATCH, DELETE)
- [ ] Persistencia delegada a `kata-feature-design-docs` con categoría `oas` (path canónico `docs/{context}/oas/openapi.yaml`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Especificación OpenAPI 3.x | YAML | `docs/{context}/oas/openapi.yaml` (persistido vía `kata-feature-design-docs`) |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Feature: Módulo de agendamiento de transferencias. Crear, listar, actualizar y cancelar; listado paginado y ordenable por fecha; mutaciones idempotentes.
Base path: /v1/scheduled-transfers
Formato: YAML
```

### Output de Ejemplo (resumido)

Archivo `openapi.yaml` (o similar) en **docs/{context}/oas/openapi.yaml** con `paths` incluyendo:
- `POST /v1/scheduled-transfers` — 201, Idempotency-Key obligatorio
- `GET /v1/scheduled-transfers` — 200, query page_size, page_token, order_by, sort; response con data y pagination
- `GET /v1/scheduled-transfers/{entity_id}` — 200, 404
- `PATCH /v1/scheduled-transfers/{entity_id}` — 200, 409 (Idempotency-Key)
- `DELETE /v1/scheduled-transfers/{entity_id}` — 204, 404

Payloads y errores conforme codex-restful-payload y codex-entities.

## Restricciones

- Este Kata produce solo especificación OpenAPI 3.x; no implementa código
- No altera contratos OAS ya publicados sin justificación y ADR
- Excepciones a las Lexis deben documentarse en ADR y reflejarse en el OAS
- El agente debe escalar a humano cuando haya conflicto entre Lexis y requisito de negocio o cuando la feature involucre múltiples bounded contexts con fronteras de API no claras

## Referencias

- lex-directives, lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting, codex-entities, codex-idempotency, codex-error-handling, codex-auth, codex-oas-structure
- [OpenAPI Specification 3.x](https://spec.openapis.org/oas/v3.0.3)
