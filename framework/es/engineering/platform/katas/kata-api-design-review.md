# Kata: Revisión de Diseño de API RESTful

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — revisión de contratos de API HTTP existentes contra las Lexis y Codex de Guardia

## Objetivo

Este Kata define el procedimiento para **revisar un contrato de API existente** (especificación OpenAPI 3.x o documento Markdown) contra las Lexis y Codex RESTful de Guardia, identificando violaciones de conformidad, brechas y mejoras, y produciendo un informe de revisión estructurado con hallazgos clasificados por severidad.

## Cuándo Usar

- Cuando un archivo OAS o documento Markdown de API existente necesita validación contra las reglas de Guardia antes o después de la implementación
- Cuando un PR incluye cambios en un contrato de API que debe pasar el Gate 2 (kata-quality-gate)
- Cuando es invocado por el Warrior Daedalus como parte de un ciclo de diseño-revisión
- Cuando `cry-api-review` es activado por el usuario

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Ruta del contrato | Sí | Ruta al archivo OAS (YAML/JSON) o documento Markdown de API a revisar |
| Alcance de la revisión | No | Endpoints o reglas específicas en las que enfocarse. Si se omite, revisa el contrato completo |
| Modo | No | `report` (por defecto) — solo hallazgos; `fix` — propone correcciones inline junto con los hallazgos |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Leer directivas y localizar contrato
- [ ] 2. Consultar Lexis y Codex
- [ ] 3. Validar endpoints (paths, métodos, status codes)
- [ ] 4. Validar estructura de entidades
- [ ] 5. Validar idempotencia
- [ ] 6. Validar estructura de errores
- [ ] 7. Validar autenticación
- [ ] 8. Validar paginación y ordenamiento
- [ ] 9. Producir informe de revisión
```

### Paso 1: Leer Directivas y Localizar Contrato

1. Leer `.ahrena/.directives` para obtener `paths.oas` y `language.default`
2. Localizar el contrato en la ruta proporcionada. Si la ruta no existe o no puede parsearse, alertar al usuario y detener la ejecución
3. Identificar si el contrato es OpenAPI 3.x (YAML/JSON) o Markdown. Si no está claro, preguntar al usuario
4. Registrar el alcance de la revisión: todos los endpoints o un subconjunto específico

### Paso 2: Consultar Lexis y Codex

1. Consultar **lex-restful-apis** — conformidad general para endpoints HTTP
2. Consultar **codex-restful-apis**, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting
3. Consultar **lex-entities** y **codex-entities** — estructura base de entidad (entity_id, entity_type, version, timestamps)
4. Consultar **lex-idempotency** y **codex-idempotency** — Idempotency-Key para mutaciones
5. Consultar **lex-error-handling** y **codex-error-handling** — estructura de error (code, reason, message)
6. Consultar **lex-auth** y **codex-auth** — autenticación y autorización
7. Consultar **codex-oas-structure** — orden de operaciones dentro de paths (POST, GET, PUT, PATCH, DELETE)

### Paso 3: Validar Endpoints (paths, métodos, status codes)

Para cada endpoint del contrato:

1. **Formato del path** — nomenclatura RESTful: sustantivos en plural, kebab-case, prefijo de versión `/v1/`; identificador en el path (ej: `/{entity_id}`)
2. **Métodos HTTP** — semántica correcta: POST = crear, GET = leer, PATCH o PUT = actualizar, DELETE = eliminar
3. **Status codes** — solo códigos permitidos por codex-restful-status-codes: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500; señalar cualquier código fuera del conjunto permitido
4. **Orden de operaciones** (solo OAS) — POST, GET, PUT, PATCH, DELETE por path según codex-oas-structure; señalar desviaciones
5. **Headers obligatorios** — X-Grd-Trace-Id cuando corresponda; Content-Type, Accept

### Paso 4: Validar Estructura de Entidades

Para cada payload de respuesta que representa una entidad persistente:

1. **entity_id** — presente y tipado como UUID
2. **entity_type** — presente y string no vacío
3. **created_at**, **updated_at** — presentes como timestamps ISO 8601
4. **discarded_at** — presente cuando el endpoint soporta soft delete; señalar ausencia solo cuando DELETE está implementado
5. **version** — presente cuando el locking optimista está documentado
6. Señalar cualquier entidad con campos obligatorios ausentes según lex-entities

### Paso 5: Validar Idempotencia

Para cada operación que modifica estado (POST, PATCH, PUT):

1. **Header Idempotency-Key** — declarado como obligatorio en la definición del endpoint
2. **Respuesta 400** — documentada para Idempotency-Key ausente (`ERR400_MISSING_IDEMPOTENCY_KEY`)
3. **Respuesta 409** — documentada para la misma clave con payload diferente
4. Señalar cualquier endpoint de mutación sin Idempotency-Key según lex-idempotency

### Paso 6: Validar Estructura de Errores

Para cada respuesta de error:

1. **Array `errors`** — el body usa `{ "errors": [{ "code": "...", "reason": "...", "message": "..." }] }`
2. **Formato del `code`** — sigue el patrón `ERR{HTTP_CODE}_{NOMBRE}` (ej: `ERR400_MISSING_FIELD`, `ERR404_NOT_FOUND`)
3. **`reason`** — debe ser un valor catalogado según codex-known-errors
4. **Mensajes de autenticación** — las respuestas 401/403 no deben revelar si el usuario o recurso existe según lex-error-handling
5. Señalar cualquier respuesta de error que se desvíe de la estructura estándar

### Paso 7: Validar Autenticación

1. **Endpoints protegidos** — esquema de autenticación declarado (OAuth 2.0 / Bearer JWT)
2. **APIs públicas** — Client Credentials + extensiones FAPI 2.0 documentadas cuando corresponda
3. **APIs privadas** — JWT de IdP confiable + alcance RBAC documentado
4. Señalar cualquier endpoint protegido sin documentación de autenticación según lex-auth

### Paso 8: Validar Paginación y Ordenamiento

Para cada endpoint de listado (GET que retorna una colección):

1. **Parámetros de request** — `page_size` y `page_token` declarados como query parameters
2. **Estructura de respuesta** — objeto `pagination` con `first_page_token`, `next_page_token`, `prev_page_token`, `page_size` según codex-restful-pagination
3. **Ordenamiento** — parámetros `order_by` y `sort` declarados cuando el ordenamiento es soportado
4. Señalar cualquier endpoint de colección sin paginación según codex-restful-pagination

### Paso 9: Producir Informe de Revisión

Generar un informe Markdown estructurado:

1. **Encabezado** — contrato revisado (ruta, formato, total de endpoints), veredicto general:
   - ✅ **Conforme** — cero ERRORs y cero WARNINGs
   - ⚠️ **Advertencias** — cero ERRORs, uno o más WARNINGs
   - ❌ **Violaciones** — uno o más ERRORs
2. **Tabla de hallazgos** — una fila por hallazgo:

   | Severidad | Endpoint | Lexis / Codex | Hallazgo | Sugerencia |
   |-----------|----------|---------------|----------|------------|

   Niveles de severidad:
   - `ERROR` — violación de Lexis; DEBE corregirse antes del merge
   - `WARNING` — desviación de Codex; DEBERÍA corregirse
   - `INFO` — oportunidad de mejora; PUEDE abordarse

3. **Conteo resumido** — total ERROR / WARNING / INFO
4. **Próximos pasos** — en modo `fix`, agregar corrección inline para cada ERROR y WARNING; en modo `report`, listar los endpoints que requieren atención

Si no hay hallazgos, indicar: "Contrato totalmente conforme con las Lexis y Codex de Guardia."

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Informe de revisión | Markdown | Entregado en el chat; opcionalmente guardado en `docs/reviews/api-review-{nombre-contrato}.md` |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Ruta del contrato: docs/oas/openapi.yaml
Alcance de la revisión: todos los endpoints
Modo: report
```

### Output de Ejemplo (resumen)

```markdown
## Revisión de Diseño de API — openapi.yaml

**Endpoints revisados:** 5 | **Veredicto:** ❌ 2 ERRORs, 3 WARNINGs

| Severidad | Endpoint | Regla | Hallazgo | Sugerencia |
|-----------|----------|-------|----------|------------|
| ERROR | POST /v1/transfers | lex-idempotency | Header Idempotency-Key no declarado | Agregar header obligatorio Idempotency-Key; documentar respuestas 400 y 409 |
| ERROR | GET /v1/transfers/{entity_id} | lex-entities | entity_type ausente del schema de respuesta | Agregar entity_type: string (no vacío) al schema TransferResponse |
| WARNING | DELETE /v1/transfers/{entity_id} | codex-restful-status-codes | Status 200 usado en lugar de 204 para respuesta sin body | Cambiar a 204 No Content |
| WARNING | GET /v1/transfers | codex-restful-pagination | page_token ausente del objeto pagination en la respuesta | Agregar page_token al schema de pagination |
| WARNING | POST /v1/transfers | codex-oas-structure | GET declarado antes de POST en la definición del path | Reordenar: POST, luego GET |

**Próximos pasos:** corregir 2 ERRORs antes del merge; 3 WARNINGs deben abordarse en el mismo PR.
```

## Restricciones

- Este Kata produce solo un informe de revisión; no modifica el contrato a menos que el modo `fix` sea explícitamente solicitado
- Toda desviación DEBE clasificarse como ERROR (Lexis) o WARNING (Codex) — nunca aceptar violaciones silenciosamente
- Escalar a un humano cuando una desviación puede ser una excepción intencional que requiere un ADR
- No señalar desviaciones en endpoints explícitamente excluidos del alcance de la revisión

## Referencias

- lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting, codex-entities, codex-idempotency, codex-error-handling, codex-auth, codex-oas-structure
