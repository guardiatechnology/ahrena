# Kata: Redactar Escenarios BDD de Negocio desde Issue y Notion

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Independiente — produce escenarios BDD orientados al negocio a partir de un issue de GitHub y Notion, y luego los escribe de regreso en el cuerpo del issue

## Objetivo

Leer un issue de GitHub (y páginas de Notion relacionadas cuando MCP esté configurado), producir una lista de escenarios Gherkin orientados al negocio, y persistirlos en el cuerpo del issue dentro de los marcadores `<!-- bdd:scenarios:start -->` / `<!-- bdd:scenarios:end -->`. La kata nunca lee código fuente ni código de prueba; los escenarios codifican intención de negocio, no una descripción de lo que la implementación ya hace.

## Cuándo Usar

- Antes de que comience la implementación, en una feature donde BDD agrega valor (tier-1, dominio regulado, reglas de negocio complejas).
- Invocada a través de `/cry-bdd-create-scenarios <issue>`.
- Opcional e independiente — independiente de `/cry-implement-issue` y del Gate 2.

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Número de issue | Sí | Número del issue de GitHub (ej.: `42`) |
| Repositorio | Sí | `owner/repo` (por defecto: detectado vía git remote) |
| Notion root | No | Página raíz de contexto en Notion; por defecto: `knowledge.notion.root_page` en `.directives` |
| Confirmación del usuario | Sí | Confirmación explícita antes de que la kata escriba en el issue vía MCP |

## Workflow

```
Progreso:
- [ ] 1. Verificar MCP y directivas
- [ ] 2. Leer el issue (título, cuerpo, comentarios)
- [ ] 3. Traer contexto de Notion si está disponible
- [ ] 4. Detectar escenarios API/UI existentes en el cuerpo del issue
- [ ] 5. Redactar escenarios orientados al negocio (duplicar, no reemplazar)
- [ ] 6. Ejecutar validación de lenguaje (sin verbos HTTP, códigos de estado, formas de payload)
- [ ] 7. Presentar al usuario el bloque bdd:scenarios propuesto
- [ ] 8. Tras la confirmación, actualizar el cuerpo del issue vía GitHub MCP
- [ ] 9. Reportar al usuario los títulos y slugs de los escenarios
```

### Paso 1: Verificar MCP y directivas

1. Leer `.ahrena/.directives` según `lex-directives`.
2. Confirmar que `github` esté en `mcp.servers` (según `lex-mcp`); sin él, detenerse e informar al usuario.
3. Confirmar que `notion` esté en `mcp.servers` (opcional). Si está ausente, continuar sin enriquecimiento de Notion e informar al usuario que el contexto vendrá solo del issue.
4. Confirmar variables de entorno: `GITHUB_PAT` (obligatoria); `NOTION_API_KEY` (cuando Notion esté en alcance).

### Paso 2: Leer el issue

1. Usar `kata-mcp-github-read` para obtener el issue: título, cuerpo, labels, asignados, comentarios.
2. Detenerse si el issue no existe o tiene cuerpo vacío.
3. Si el cuerpo ya contiene un bloque `<!-- bdd:scenarios:start -->`, capturar el contenido actual para fines de diff (las re-ejecuciones son merges, no sobreescrituras a ciegas).
4. **El código fuente está prohibido.** Sin `git show`, sin Read sobre `src/`, `tests/`, `app/`, `domain/`, etc. La perspectiva de la kata es lo que el negocio quiere; el código responde otra pregunta.

### Paso 3: Traer contexto de Notion (opcional)

Cuando `notion` esté activo:

1. Extraer términos de dominio del título y del cuerpo del issue (nombres de entidad, operaciones, roles).
2. Usar `kata-mcp-notion-read` en modo `search` para 3-5 términos de alta señal (evitar costo excesivo).
3. Para los hits relevantes, obtener en modo `page` con profundidad `full`.
4. Filtrar por estrategia de producto, reglas de negocio y decisiones de producto previas. Saltar páginas irrelevantes.
5. Registrar: título de la página, URL, fragmento relevante.

### Paso 4: Detectar escenarios API/UI existentes

1. Buscar en el cuerpo del issue bloques cercados ```gherkin y marcadores `Scenario:`.
2. Capturarlos como **escenarios API/UI** (la salida de las plantillas originales). Mantenerlos.
3. Se vuelven la semilla para la duplicación a forma de negocio (Paso 5).
4. El agente no modifica ni elimina los originales.

### Paso 5: Redactar escenarios de negocio

Para cada comportamiento implícito en el issue y en el contexto de Notion:

1. Identificar al actor en términos de dominio (cliente, operador, sistema actuando por sí mismo — nunca "la API" o "el user agent").
2. Identificar la acción en términos de dominio (solicitar un reembolso, programar una transferencia, aprobar una liberación — nunca un verbo HTTP).
3. Identificar el resultado observable (se crea un registro, se despacha una notificación, ocurre una transición de estado — nunca un código de estado o forma de payload).
4. Escribir el escenario en Gherkin:

```gherkin
Scenario: <Title in product language>
  Given <precondition stated in domain terms>
  When <action stated in domain terms>
  Then <observable business outcome>
  And <additional outcome, if any>
```

5. Cubrir happy path, casos clave de error/borde e idempotencia o replay cuando sea relevante.
6. No inventar reglas ausentes del issue o de Notion; en su lugar, listarlas bajo una sub-sección `## Pending Questions` dentro del mismo bloque.

### Paso 6: Validación de lenguaje

Rechazar cualquier línea redactada que contenga:

- Verbos HTTP en mayúsculas (`POST`, `GET`, `PUT`, `PATCH`, `DELETE`).
- Códigos de estado cuando estén adyacentes a "status", "code" o "returns" (regex `\b[1-5]\d{2}\b`).
- Tokens de forma de payload (`{` / `}` que encierren claves tipo campo; `Content-Type`, `Accept`, `Idempotency-Key`).
- Selectores DOM/UI (`#`, `.`, `[data-`).
- Nombres de framework de implementación (`fastapi`, `react`, `redis`, `kafka` cuando se usen como elemento `Then`).

Para cada rechazo: reescribir la línea en términos de negocio, o escalar el conflicto al usuario.

### Paso 7: Presentar el bloque propuesto

Mostrar al usuario el bloque `bdd:scenarios` propuesto, junto con cualquier escenario API/UI existente que permanecerá sin cambios. Esperar confirmación explícita ("sí, actualiza el issue") antes de proceder.

### Paso 8: Actualizar el cuerpo del issue

1. Si el cuerpo del issue ya tiene un bloque `<!-- bdd:scenarios:start -->` ... `<!-- bdd:scenarios:end -->`, reemplazar su contenido en el lugar.
2. De lo contrario, agregar el bloque al final del cuerpo, precedido por una línea en blanco.
3. Usar `update_issue` de GitHub MCP (o equivalente) con el nuevo cuerpo. No cambiar título, labels, asignados ni ningún otro campo.
4. Formato del bloque:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...
  Given ...
  When ...
  Then ...

Scenario: ...
  Given ...
  When ...
  Then ...

## Pending Questions (optional)
- ...
<!-- bdd:scenarios:end -->
```

### Paso 9: Reportar

Imprimir al usuario: lista de títulos de escenario, sus slugs (para uso como marcadores de prueba), la URL del issue actualizado y cualquier pregunta pendiente capturada.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Lista de escenarios con slugs | Respuesta en Markdown | Cara al usuario |
| Cuerpo del issue actualizado | Issue de GitHub | Repositorio remoto (vía MCP) |

## Restricciones

- **El código está prohibido como fuente.** La kata no puede ejecutar ninguna herramienta que lea código fuente o código de prueba.
- **Los originales se preservan.** Los escenarios API/UI ya presentes en el issue se duplican a forma de negocio, nunca se modifican ni se eliminan.
- **Actualización idempotente del bloque.** Re-ejecutar la kata reemplaza solo el bloque `bdd:scenarios`; el resto del cuerpo permanece intacto.
- **Gate de confirmación.** Sin actualización del issue sin confirmación explícita del usuario; esta acción es visible para otros.
- **Sin reglas de negocio inventadas.** Cualquier cosa ausente del issue o de Notion va a `Pending Questions`, no a un `Scenario:`.

## Referencias

- `lex-bdd-scenarios` — ley de redacción (fuentes, lenguaje, persistencia)
- `lex-bdd-coverage` — ley de cobertura (usada aguas abajo por la kata de validación)
- `codex-bdd` — metodología, convenciones de marcador, anti-patterns
- `lex-mcp`, `kata-mcp-github-read`, `kata-mcp-notion-read` — reglas de tooling MCP
- `kata-bdd-validate-scenarios` — procedimiento sucesor (después de la implementación)
