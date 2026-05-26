# Kata: Consultar proyectos y código en GitHub vía MCP

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Lectura de repositorios, issues, pull requests, commits y código en GitHub vía servidor MCP

## Objetivo

Obtener y leer información de repositorios GitHub (código, issues, PRs, commits, branches) vía servidor MCP, trayendo los datos al contexto de la sesión para referencia, análisis o revisión. Esta kata es estrictamente **solo lectura** — ningún archivo, issue, PR o branch es creado o modificado.

## Cuándo Usar

- Cuando el usuario necesita inspeccionar código de un repositorio GitHub sin clonarlo localmente
- Cuando se necesitan consultar issues o PRs abiertos para contexto de una tarea
- Cuando se quiere revisar el historial de commits o la estructura de branches de un repositorio
- Cuando es necesario buscar código en repositorios para referencia o comparación

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Repositorio | Sí | `owner/repo` (ej.: `guardiatechnology/ahrena`) |
| Objeto | Sí | Qué consultar: `code`, `issues`, `prs`, `commits`, `branches`, `file` |
| Consulta o ruta | Depende | Término de búsqueda (para `code`), ruta (para `file`), filtros (para `issues`/`prs`) |
| Branch | No | Branch de referencia; por defecto: branch principal del repositorio |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y directivas
- [ ] 2. Identificar repositorio y objeto de consulta
- [ ] 3. Obtener y leer el contenido
- [ ] 4. Presentar resultado al usuario
```

### Paso 1: Verificar precondiciones MCP y directivas

1. Consultar `.ahrena/.directives` según `lex-directives`.
2. Verificar que `github` esté listado en `mcp.servers` (según `lex-mcp`). Si no, informar al usuario y detener.
3. Confirmar que la variable de entorno `GH_TOKEN` está definida. Si no, informar al usuario qué variable configurar y detener.
4. Consultar `codex-mcp-github` para identificar las herramientas y parámetros correctos.

### Paso 2: Identificar repositorio y objeto de consulta

1. Confirmar el repositorio (`owner/repo`) con el usuario — solicitarlo si no fue informado.
2. Identificar el objeto de consulta:
   - **`file`** — contenido de un archivo o listado de directorio
   - **`code`** — búsqueda de código por término o patrón
   - **`issues`** — lista o detalles de issues
   - **`prs`** — lista o detalles de pull requests
   - **`commits`** — historial de commits de un branch
   - **`branches`** — branches disponibles en el repositorio
3. Si el objeto no fue especificado, preguntar al usuario qué aspecto del repositorio desea consultar.

### Paso 3: Obtener y leer el contenido

**Objeto `file`:**
1. Llamar `get_file_contents(owner, repo, path, branch)`.
2. Si `path` es un directorio, listar los elementos retornados y preguntar al usuario cuál archivo expandir.
3. Si `path` es un archivo, presentar el contenido completo con resaltado de lenguaje.

**Objeto `code`:**
1. Llamar `search_code(query="{término} repo:{owner}/{repo}")`.
2. Presentar los archivos correspondientes con fragmentos relevantes.
3. Para los archivos de interés, llamar `get_file_contents` para obtener el contenido completo si el usuario lo solicita.

**Objeto `issues`:**
1. Llamar `list_issues(owner, repo, state, labels, assignee)` con los filtros proporcionados por el usuario.
2. Presentar la lista (número, título, estado, labels, assignee, fecha de apertura).
3. Si el usuario desea detalles de una issue específica, llamar `get_issue(owner, repo, issue_number)`.

**Objeto `prs`:**
1. Llamar `list_pull_requests(owner, repo, state, head, base)` con los filtros proporcionados.
2. Presentar la lista (número, título, estado, branch de origen/destino, autor, fecha).
3. Si el usuario desea detalles de un PR específico, llamar `get_pull_request(owner, repo, pull_number)`.

**Objeto `commits`:**
1. Llamar `list_commits(owner, repo, branch)`.
2. Presentar el historial (hash abreviado, mensaje, autor, fecha).
3. Limitar la presentación a los 20 commits más recientes por defecto; preguntar al usuario si desea más.

### Paso 4: Presentar resultado al usuario

1. Presentar el contenido recuperado de forma estructurada y legible.
2. Para listas (issues, PRs, commits): usar formato de tabla con los campos más relevantes.
3. Para archivos y código: preservar el formato original con bloque de código y lenguaje identificado.
4. Incluir el enlace directo al elemento en GitHub (URL) cuando esté disponible en la respuesta de la herramienta.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Contenido de archivo | Bloque de código con lenguaje identificado | Respuesta al usuario |
| Resultados de búsqueda de código | Lista de archivos con fragmentos relevantes | Respuesta al usuario |
| Lista de issues / PRs | Tabla con campos relevantes | Respuesta al usuario |
| Historial de commits | Tabla (hash, mensaje, autor, fecha) | Respuesta al usuario |

## Restricciones

- **Solo lectura:** esta kata nunca crea branches, issues, PRs, comentarios ni hace push de archivos.
- **Usar solo MCP:** nunca usar el CLI `gh` ni la API REST de GitHub directamente cuando el servidor MCP esté activo (según `lex-mcp`).
- **Sin credenciales hardcodeadas:** autenticación exclusivamente mediante variable de entorno `GH_TOKEN`.
- **Confirmar repositorio:** siempre confirmar `owner/repo` con el usuario antes de iniciar la consulta.

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `codex-mcp-github` — Referencia de herramientas y parámetros del GitHub MCP
- `lex-directives` — Cómo leer `.ahrena/.directives`
