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

Ambas plataformas consumen el **servidor remoto oficial hospedado por GitHub** en `https://api.githubcopilot.com/mcp/` (nivel 1 de la preferencia de transporte declarada en `lex-mcp` §5 — cero dependencia local).

**Cursor (`.cursor/mcp.json`):**
```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${env:GH_TOKEN}" }
}
```

**Claude Code (`.mcp.json`):**
```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${GH_TOKEN}" }
}
```

> La variable `GH_TOKEN` debe estar definida en el entorno (token clásico o fine-grained). El nombre coincide con la convención del CLI `gh` y con la variable documentada del servidor MCP de GitHub. Nunca escribir tokens en archivos rastreados (ver `lex-mcp`).
>
> Diferencia sintáctica intencional: Cursor usa `${env:VAR}` para interpolar variables de entorno; Claude Code usa `${VAR}`. Ambas formas resuelven al mismo valor en runtime.

#### Scopes OAuth requeridos

Un PAT clásico utilizado con el MCP de GitHub DEBE conceder los siguientes scopes para la superficie completa de herramientas (issues, PRs, ramas, workflows, búsquedas de usuario):

| Scope | Por qué |
|---|---|
| `repo` | Lectura/escritura en issues, PRs, ramas, archivos, commits |
| `read:org` | Listar equipos, miembros y code owners de la organización |
| `workflow` | Leer ejecuciones de workflow, disparar reruns (usado por katas de release/CI) |
| `read:user` | Resolver `@me` e identidades de assignees |

El `scripts/install.py` verifica estos scopes en el momento del install cuando `GH_TOKEN` está definida y emite una línea de aviso (solo warn, nunca bloquea) por scope faltante, con la sugerencia lista para pegar: `gh auth refresh -s <scope>`. Fallas de red o PATs fine-grained (que no exponen el header `X-OAuth-Scopes`) caen a una única línea consultiva.

#### Override para el camino npx legacy

El paquete npx (`@modelcontextprotocol/server-github`) está deprecated pero sigue funcional. Los equipos que lo necesitan (entornos air-gapped, herramientas no cubiertas aún por el endpoint hospedado) pueden sobrescribir el JSON del servidor en `.ahrena/mcp/github.json` con una desviación justificada por `_comment`, conforme `lex-mcp` §5:

```json
{
  "_comment": "Override: usando el paquete npx @modelcontextprotocol/server-github por <razón>. Decisión registrada en ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GH_TOKEN}" }
  },
  "claude-code": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GH_TOKEN}" }
  }
}
```

El override exige Node.js en el host; ejecute `make mcp-enable SERVER=github PLATFORM=...` y el preflight ofrecerá instalarlo cuando falte.

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

### Ejemplo de uso: crear PR con body estructurado

```
create_pull_request(
  owner="acme",
  repo="mi-proyecto",
  title="feat(auth): implementar OAuth2",
  head="feat/oauth2",
  base="main",
  body="## Resumen\n\n- Agrega flujo OAuth2 con PKCE\n- Integra con el proveedor configurado en `.env`\n\n## Cómo probar\n\n1. Definir `OAUTH_CLIENT_ID` y `OAUTH_CLIENT_SECRET`\n2. Ejecutar `make dev` y acceder a `/auth/login`",
  draft=False
)
```

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `codex-mcp-notion` — Referencia del Notion MCP (patrón análogo)
- [GitHub MCP Server — repositorio oficial en Go](https://github.com/github/github-mcp-server) (binario/HTTP mantenido por GitHub)
- [Claude Code — documentación MCP](https://code.claude.com/docs/en/mcp)
