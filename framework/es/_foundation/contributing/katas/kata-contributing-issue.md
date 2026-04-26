# Kata: Abrir issue en el repositorio (plantilla por tipo)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de issue en el repositorio origin vía MCP de GitHub

## Objetivo

Este Kata define el procedimiento estandarizado para abrir una issue en el repositorio origin del proyecto usando una de las 5 plantillas de issue (feature-request, epic, user-story-for-api, user-story-for-frontend, simple-task). El agente resuelve la plantilla en `.ahrena/contributing_templates/`, rellena las secciones con el usuario, aplica las etiquetas obligatorias según `lex-issue-quality`, y crea la issue **vía MCP de GitHub** (respaldo con `gh` CLI cuando no esté disponible). Sigue el flujo del `codex-contributing`.

## Cuándo Usar

- Cuando el usuario solicita abrir una feature request, epic, user story (API o frontend) o tarea simple
- Cuando se invoca por uno de los cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-simple-task
- Cuando se invoca por cry-contribute con acción issue (y tipo indicado o inferido)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Tipo | Sí* | `feature-request` \| `epic` \| `user-story-for-api` \| `user-story-for-frontend` \| `simple-task`. *Inferido por el cry que invocó si no se indica.* |
| Título (resumen) | No | Resumen breve de la issue. Si se omite, el agente compone a partir del contexto. |
| Contexto del usuario | No | Información adicional para rellenar placeholders de la plantilla. |

### Tabla: tipo → plantilla → etiquetas obligatorias

| Tipo | Archivo de plantilla | Etiquetas obligatorias |
|------|----------------------|------------------------|
| feature-request | `feature-request.md` | `feature request ➕` |
| epic | `epic.md` | `epic` |
| user-story-for-api | `user-story-for-api.md` | `api`, `user story 🎯` |
| user-story-for-frontend | `user-story-for-frontend.md` | `frontend`, `user story 🎯` |
| simple-task | `simple-task.md` | Al menos una de: `documentation 📃`, `ci 🏗️`, `enhancement 🔝`, `evolvability ♻️` |

## Workflow

```
Progreso:
- [ ] 1. Resolver tipo de la issue
- [ ] 2. Cargar plantilla .md
- [ ] 3. Rellenar secciones/placeholders con el usuario
- [ ] 4. Crear issue vía MCP de GitHub (o gh)
- [ ] 5. Verificación final
```

### Paso 1: Resolver tipo de la issue

1. Si el tipo se pasó de forma explícita (p. ej. por el cry), usarlo.
2. En caso contrario, preguntar al usuario qué tipo desea: feature request, epic, user story (API), user story (frontend) o tarea simple.
3. Mapear al nombre del archivo y las etiquetas obligatorias según la tabla anterior.

### Paso 2: Cargar plantilla .md

1. Ruta canónica: `.ahrena/contributing_templates/<archivo>.md` (p. ej. `feature-request.md`).
2. Si no existe en `.ahrena/`, usar respaldo: `framework/templates/contributing_templates/<archivo>.md` o `.github/ISSUE_TEMPLATE/` cuando aplique.
3. Leer el contenido e identificar secciones y placeholders (p. ej. `{user_role}`, `{specific_objective}`).

### Paso 3: Rellenar secciones/placeholders con el usuario

1. Para cada sección obligatoria de la plantilla, obtener del usuario o del contexto la información necesaria.
2. Sustituir placeholders y marcar checkboxes cuando aplique.
3. Componer el título de la issue (p. ej. "feat/ resumen" para feature request; resumen breve para epic/user story).
4. Montar el body en Markdown con la plantilla rellenada.

### Paso 4: Crear issue vía MCP de GitHub (o gh)

1. Determinar las etiquetas obligatorias según la tabla anterior. Para `simple-task`, preguntar al usuario qué etiqueta aplica si no queda claro por el contexto.
2. **Preferencia:** usar MCP de GitHub (servidor que exponga creación de issue). Ej.: servidor `project-0-ahrena-github`, herramienta `issue_write` con `method`: `create`; `owner`; `repo`; `title`; `body`; `labels` — **obligatorio**, según `lex-issue-quality`.
3. **Respaldo:** si el MCP no está disponible, usar `gh issue create --title "..." --body "..." --label "nombre-etiqueta"` (o body vía archivo temporal).

### Paso 5: Verificación final

- [ ] La issue se creó correctamente
- [ ] El título y el body reflejan la plantilla rellenada
- [ ] Las etiquetas obligatorias fueron aplicadas según `lex-issue-quality`
- [ ] Se presentó al usuario el enlace de la issue

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Issue | GitHub Issue | Repositorio origin |
| URL de la issue | Enlace | Presentado al usuario |

## Restricciones

- Usar siempre uno de los 5 tipos y la plantilla correspondiente; no crear issue sin plantilla ni sin las etiquetas obligatorias.
- Si no existen ni `.ahrena/contributing_templates/` ni el respaldo, informar al usuario y sugerir ejecutar el install de Ahrena o crear la plantilla manualmente.
- En caso de fallo del MCP, presentar el error y sugerir creación manual vía `gh issue create` o la UI de GitHub.

## Referencias

- `lex-issue-quality` — Ley que rige plantillas, etiquetas y contenido Por qué/Qué/Cómo
- `codex-contributing` — Flujo de contribución Guardia
- `.ahrena/contributing_templates/` — Plantillas de issue (feature-request.md, epic.md, user-story-for-api.md, user-story-for-frontend.md, simple-task.md)
- MCP de GitHub (p. ej. issue_write para creación de issue)
- Cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend, cry-new-simple-task
