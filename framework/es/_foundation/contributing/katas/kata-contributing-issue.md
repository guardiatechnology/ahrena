# Kata: Abrir issue en el repositorio (template por tipo)

> **Prefix:** `kata-` | **Type:** Skill Repetible | **Scope:** Crear issue en el repositorio de origen mediante GitHub MCP

## Objetivo

Esta Kata define el procedimiento estandarizado para abrir un issue en el repositorio de origen del proyecto usando uno de los 5 templates de issue (feature-request, epic, user-story-for-api, user-story-for-frontend, tech-task). El agente resuelve el template en `.ahrena/contributing_templates/`, completa las secciones con el usuario, aplica los labels obligatorios según `lex-issue-quality`, define el GitHub Issue Type, se auto-asigna el issue y lo crea **mediante GitHub MCP** (fallback al CLI `gh` cuando no está disponible). Sigue el flujo definido en `codex-contributing`.

## Cuándo Usar

- Cuando el usuario solicita abrir un feature request, epic, user story (API o frontend) o simple task
- Cuando es invocada por uno de los cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-tech-task
- Cuando es invocada por cry-contribute con acción de issue (y tipo indicado o inferido)

## Entradas

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| Tipo | Sí* | `feature-request` \| `epic` \| `user-story-for-api` \| `user-story-for-frontend` \| `tech-task`. *Inferido del cry invocante si no se proporciona.* |
| Título (resumen) | No | Resumen breve del issue. Si se omite, el agente lo compone a partir del contexto. |
| Contexto del usuario | No | Información adicional para completar los placeholders del template. |

### Tabla: tipo → template → labels obligatorios → Issue Type

| Tipo | Archivo de template | Labels obligatorios | GitHub Issue Type |
|------|---------------------|---------------------|-------------------|
| feature-request | `feature-request.md` | `feature request ➕` | Feature |
| epic | `epic.md` | `epic` | Feature |
| user-story-for-api | `user-story-for-api.md` | `api`, `user story 🎯` | Feature |
| user-story-for-frontend | `user-story-for-frontend.md` | `frontend`, `user story 🎯` | Feature |
| tech-task | `tech-task.md` | Al menos uno de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` | Task |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Resolver el tipo del issue
- [ ] 2. Cargar template .md
- [ ] 3. Completar secciones/placeholders con el usuario
- [ ] 4. Crear issue mediante GitHub MCP (o gh)
- [ ] 5. Definir GitHub Issue Type mediante GraphQL
- [ ] 6. Verificación final
```

### Paso 1: Resolver el tipo del issue

1. Si el tipo fue pasado explícitamente (por ejemplo, por el cry), utilizarlo.
2. En caso contrario, preguntar al usuario qué tipo desea: feature request, epic, user story (API), user story (frontend) o simple task.
3. Mapear al nombre del archivo de template, labels obligatorios y GitHub Issue Type según la tabla anterior.

### Paso 2: Cargar template .md

1. Ruta canónica: `.ahrena/contributing_templates/<archivo>.md` (por ejemplo, `feature-request.md`).
2. Si no existe en `.ahrena/`, usar fallback: `framework/templates/contributing_templates/<archivo>.md` o `.github/ISSUE_TEMPLATE/` cuando corresponda.
3. Leer el contenido e identificar secciones y placeholders (por ejemplo, `{user_role}`, `{specific_objective}`).

### Paso 3: Completar secciones/placeholders con el usuario

1. Para cada sección obligatoria del template, obtener la información necesaria del usuario o del contexto.
2. Reemplazar placeholders y completar checkboxes cuando corresponda.
3. Componer el título del issue (por ejemplo, "feat/ resumen" para feature request; resumen breve para epic/user story).
4. Construir el cuerpo en Markdown con el template completado.

### Paso 4: Crear issue mediante GitHub MCP (o gh)

1. Determinar los labels obligatorios según la tabla anterior. Para `tech-task`, preguntar al usuario qué label aplica si no queda claro por el contexto.
2. **Preferido:** Usar GitHub MCP (servidor que expone la creación de issues). Por ejemplo, servidor `project-0-ahrena-github`, herramienta `issue_write` con: `method`: `create`; `owner`; `repo`; `title`; `body`; `labels` — **obligatorio**, según `lex-issue-quality`; `assignees`: `["@me"]`.
3. **Fallback:** Si el MCP no está disponible, usar:
   ```bash
   gh issue create \
     --title "..." \
     --body "..." \
     --label "nombre-del-label" \
     --assignee "@me"
   ```
4. Registrar el número del issue y el node ID devueltos por la API — necesarios para el Paso 5.

### Paso 5: Definir GitHub Issue Type mediante GraphQL

El CLI `gh issue create` no soporta `--type`. Se debe definir el Issue Type inmediatamente después de la creación mediante la API GraphQL.

```bash
# Obtener el node ID del issue (si no fue devuelto en el Paso 4)
ISSUE_ID=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json id -q .id)

# Definir Issue Type (reemplazar ISSUE_TYPE_ID con el valor de la tabla a continuación)
gh api graphql -f query="
  mutation {
    updateIssue(input: {id: \"$ISSUE_ID\", issueTypeId: \"$ISSUE_TYPE_ID\"}) {
      issue { number }
    }
  }
"
```

**IDs de Issue Type** (específicos del repositorio — verificar mediante `codex-labels`):

| GitHub Issue Type | ID |
|-------------------|----|
| Task | `IT_kwDOED9Qy84B7pBh` |
| Bug | `IT_kwDOED9Qy84B7pBi` |
| Feature | `IT_kwDOED9Qy84B7pBj` |

### Paso 6: Verificación final

- [ ] El issue fue creado correctamente
- [ ] El título y el cuerpo reflejan el template completado
- [ ] Los labels obligatorios fueron aplicados según `lex-issue-quality`
- [ ] El issue está asignado al usuario actual (`@me`)
- [ ] El GitHub Issue Type está definido (Task o Feature según el template)
- [ ] El enlace del issue fue presentado al usuario

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Issue | GitHub Issue | Repositorio de origen |
| URL del issue | Enlace | Presentado al usuario |

## Restricciones

- Siempre usar uno de los 5 tipos y el template correspondiente; no crear un issue sin el template o sin los labels obligatorios.
- Siempre auto-asignarse el issue (`--assignee "@me"`), a menos que el usuario especifique explícitamente un assignee diferente.
- Siempre definir el GitHub Issue Type en el Paso 5 inmediatamente después de la creación.
- Si ni `.ahrena/contributing_templates/` ni el fallback existen, informar al usuario y sugerir ejecutar el install de Ahrena o crear el template manualmente.
- En caso de fallo del MCP, presentar el error y sugerir la creación manual mediante `gh issue create` o la UI de GitHub.

## Referencias

- `lex-issue-quality` — Ley que rige templates, labels y contenido Why/What/How
- `codex-labels` — Taxonomía completa de labels y definiciones de GitHub Issue Type
- `codex-contributing` — Flujo de contribución Guardia
- `.ahrena/contributing_templates/` — Templates de issue (feature-request.md, epic.md, user-story-for-api.md, user-story-for-frontend.md, tech-task.md)
- GitHub MCP (por ejemplo, issue_write para la creación de issues)
- Cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-tech-task
