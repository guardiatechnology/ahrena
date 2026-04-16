# Codex: GitHub MCP Server

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Herramientas y autenticación del servidor MCP de GitHub para Cursor y Claude Code

## Resumen General

Este Codex es la referencia para usar el **servidor MCP de GitHub** en proyectos Ahrena. Ver `codex-mcp-common` para patrones MCP compartidos (autenticación, configuración, fallback). Este documento se enfoca en herramientas, parámetros y ejemplos específicos de GitHub. Consultado por Warriors y Katas que realizan operaciones de repositorio (issues, pull requests, branches, archivos, búsquedas).

## Contexto

- **Dominio:** Operaciones de repositorio GitHub vía MCP (issues, PRs, branches, commits, archivos, búsquedas, discussions).
- **Público objetivo:** Agentes IA que realizan operaciones GitHub en proyectos Ahrena con el servidor MCP activo.
- **Actualización:** Cuando se agreguen nuevas herramientas al servidor MCP de GitHub o cuando cambien los parámetros.

## Contenido

### Configuración por plataforma

**Cursor (`.cursor/mcp.json`):**
```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${env:GITHUB_PAT}" }
}
```

**Claude Code (`.claude/settings.json`):**
```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}" }
}
```

> La variable `GITHUB_PAT` debe estar definida en el entorno. Nunca escribir tokens en archivos rastreados (ver `lex-mcp`).

### Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `create_issue` | Crea una issue en el repositorio |
| `list_issues` | Lista issues con filtros (state, labels, assignee) |
| `get_issue` | Obtiene detalles de una issue específica |
| `add_issue_comment` | Agrega un comentario a una issue |
| `create_pull_request` | Crea un pull request |
| `list_pull_requests` | Lista PRs con filtros (state, head, base) |
| `get_pull_request` | Obtiene detalles de un PR específico |
| `merge_pull_request` | Hace merge de un PR |
| `create_branch` | Crea una nueva branch en el repositorio |
| `push_files` | Hace push de uno o más archivos a una branch |
| `get_file_contents` | Obtiene el contenido de un archivo o directorio |
| `list_commits` | Lista commits de una branch |
| `search_repositories` | Busca repositorios en GitHub |
| `search_code` | Busca código en repositorios |
| `fork_repository` | Hace fork de un repositorio |
| `create_repository` | Crea un nuevo repositorio |

### Parámetros de las herramientas más usadas

**`create_pull_request`**
```
owner         (string, obligatorio) — dueño del repositorio
repo          (string, obligatorio) — nombre del repositorio
title         (string, obligatorio) — título del PR
head          (string, obligatorio) — branch de origen
base          (string, obligatorio) — branch de destino (ej.: "main")
body          (string, opcional)    — descripción del PR (Markdown)
draft         (boolean, opcional)   — crear como borrador
```

**`create_issue`**
```
owner         (string, obligatorio) — dueño del repositorio
repo          (string, obligatorio) — nombre del repositorio
title         (string, obligatorio) — título de la issue
body          (string, opcional)    — descripción (Markdown)
labels        (array, opcional)     — lista de labels
assignees     (array, opcional)     — lista de assignees
```

**`push_files`**
```
owner         (string, obligatorio) — dueño del repositorio
repo          (string, obligatorio) — nombre del repositorio
branch        (string, obligatorio) — branch de destino
message       (string, obligatorio) — mensaje de commit
files         (array, obligatorio)  — [{path, content}] — contenido como string
```

### Cuándo usar MCP vs CLI `gh`

| Situación | Usar |
|---|---|
| Servidor MCP de GitHub listado en `mcp.servers` | **MCP** (siempre, según `lex-mcp`) |
| Servidor MCP no disponible o variable no definida | CLI `gh` como fallback (comunicar indisponibilidad) |
| Operación no cubierta por las herramientas MCP | CLI `gh` o API REST directamente |

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `codex-mcp-notion` — Referencia del Notion MCP (patrón análogo)
- [GitHub MCP Server — repositorio oficial](https://github.com/modelcontextprotocol/servers)
