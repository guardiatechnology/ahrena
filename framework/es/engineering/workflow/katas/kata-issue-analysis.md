# Kata: Análisis de Issue

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 1 del flujo Issue-Driven — lectura de la issue de GitHub y búsqueda de contexto relacionado en Notion

## Objetivo

Leer una issue de GitHub (título, descripción, comentarios, labels, metadata) y buscar en Notion documentos de contexto relacionados (specs de producto, ADRs previos, reglas de negocio), produciendo un brief estructurado en `.ahrena/issues/{n}/01-brief.md`. Este brief es la base para las fases subsiguientes del flujo Issue-Driven.

## Cuándo Usar

- Fase 1 del flujo orquestado por `warrior-athena` tras la invocación de `/cry-implement-issue`
- Siempre que sea necesario consolidar el contexto de una issue antes de iniciar el diseño o la implementación

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Número de la issue | Sí | Número de la issue en GitHub (ej.: `42`) |
| Repositorio | Sí | `owner/repo` (ej.: `guardiatechnology/ahrena`) |
| Raíz Notion | No | Página/database de contexto; por defecto: `knowledge.notion.root_page` en `.ahrena/.directives` |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y directivas
- [ ] 2. Leer la issue de GitHub
- [ ] 3. Buscar contexto relacionado en Notion
- [ ] 4. Consolidar y estructurar el brief
- [ ] 5. Persistir en .ahrena/issues/{n}/01-brief.md
- [ ] 6. Actualizar checkpoint de handoff
```

### Paso 1: Verificar precondiciones MCP y directivas

1. Consultar `.ahrena/.directives` según `lex-directives`.
2. Confirmar que `github` está en `mcp.servers` (según `lex-mcp`). Si no, informar al usuario y detener.
3. Confirmar que `notion` está en `mcp.servers`. Si no, continuar sin contexto Notion (informar al usuario que el enriquecimiento será omitido).
4. Confirmar que `GITHUB_PAT` y `NOTION_API_KEY` (si aplica) estén definidas en el ambiente.

### Paso 2: Leer la issue de GitHub

1. Invocar `kata-mcp-github-read` con:
   - objeto: `issues`
   - `owner/repo` e `issue_number` recibidos como input
2. Registrar: título, body, labels, assignees, autor, fecha de creación, estado, milestone.
3. Invocar `kata-mcp-github-read` nuevamente para listar comentarios de la issue (usar `get_issue` si ya retorna comments; caso contrario buscar vía API de la issue).
4. Si la issue no existe o está vacía, informar al usuario y detener.

### Paso 3: Buscar contexto relacionado en Notion

Si `notion` está activo:

1. Extraer términos clave del título y body de la issue (nombres propios de features, entidades de dominio, áreas técnicas).
2. Invocar `kata-mcp-notion-read` en modo `search` para cada término relevante (límite de 3-5 búsquedas para evitar costo excesivo).
3. Para cada resultado prometedor, invocar `kata-mcp-notion-read` en modo `page` con profundidad `full` para obtener el contenido.
4. Filtrar resultados irrelevantes (desactualizados, tangenciales). Si `knowledge.notion.root_page` está configurada, priorizar resultados descendientes de esa página.
5. Registrar: título de la página, URL, fragmento relevante, relación con la issue.

### Paso 4: Consolidar y estructurar el brief

Producir el brief siguiendo la estructura:

```markdown
# Brief — Issue #{n}: {título}

- **Repositorio:** {owner/repo}
- **Autor:** @{autor}
- **Creada:** {YYYY-MM-DD}
- **Labels:** {lista}
- **Assignees:** {lista}
- **Link:** {URL de la issue}

## Problema

{resumen en 2-3 párrafos de lo que la issue describe — problema, motivación, síntomas}

## Contexto adicional

### De la issue (comentarios relevantes)

- {comentario 1, autor, fecha}
- {comentario 2, autor, fecha}

### De Notion

- **[{Título de la página}]({URL}):** {fragmento relevante, 1-3 líneas}
- **[{Título de la página}]({URL}):** {fragmento relevante, 1-3 líneas}

## Tipo de trabajo

{Feature | Bugfix | Refactor | Chore} — {breve justificación}

## Riesgos e incógnitas identificadas

- {Lista de puntos que requieren aclaración antes del diseño}

## Siguiente fase

Fase 2: elicitación de requisitos (`kata-requirements-brief`).
```

### Paso 5: Persistir en `.ahrena/issues/{n}/01-brief.md`

1. Crear el directorio `.ahrena/issues/{n}/` si no existe.
2. Guardar el brief en `.ahrena/issues/{n}/01-brief.md`.
3. Si el archivo ya existe, comparar con el nuevo contenido: si diverge, presentar diff al usuario antes de sobrescribir.

### Paso 6: Actualizar checkpoint de handoff

1. Crear/actualizar `.ahrena/workflow/issue-{n}/checkpoint.md` con:
   - fase completada: 1
   - siguiente fase: 2
   - referencia: `.ahrena/issues/{n}/01-brief.md`
   - timestamp
2. Informar a `warrior-athena` (o al usuario) que la Fase 1 fue concluida.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Brief estructurado | Markdown | `.ahrena/issues/{n}/01-brief.md` |
| Checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Resumen al usuario | Texto estructurado | Respuesta al orquestador |

## Restricciones

- **Solo lectura en GitHub:** este kata no crea ni modifica issues, comentarios o labels (según `kata-mcp-github-read`).
- **Solo lectura en Notion:** este kata no crea ni modifica páginas (según `kata-mcp-notion-read`).
- **Sin inferencia de alcance:** el kata consolida lo que está en la issue y en Notion; no añade información no documentada. Las incógnitas van a la sección "Riesgos e incógnitas".
- **Destino fijo:** el brief va en `.ahrena/issues/{n}/01-brief.md`; nunca en otra ruta (según `lex-issue-driven`).

## Referencias

- `lex-issue-driven` — leyes del flujo Issue-Driven
- `codex-issue-workflow` — estructura completa del flujo
- `kata-mcp-github-read` — lectura de issues vía MCP
- `kata-mcp-notion-read` — lectura de contenido Notion vía MCP
- `lex-mcp` — uso obligatorio de MCP
