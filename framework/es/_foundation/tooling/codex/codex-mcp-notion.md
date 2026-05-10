# Codex: Notion MCP Server

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Herramientas y autenticación del servidor MCP de Notion para Cursor y Claude Code

## Resumen General

Este Codex es la referencia para usar el **servidor MCP de Notion** en proyectos Ahrena. Ver `codex-mcp-common` para patrones MCP compartidos (autenticación, configuración, fallback). Este documento se enfoca en herramientas, parámetros y casos de uso específicos de Notion: lectura de documentación, creación de wikis, notas de reunión y páginas de proyecto.

## Contexto

- **Dominio:** Operaciones de creación, lectura y actualización de contenido en Notion vía MCP (páginas, bloques, databases, búsquedas).
- **Público objetivo:** Agentes IA que gestionan documentación o conocimiento en Notion en proyectos Ahrena con el servidor MCP activo.
- **Actualización:** Cuando se agreguen nuevas herramientas al servidor MCP de Notion o cuando cambie el schema de databases.

## Contenido

### Configuración por plataforma

Ambas plataformas consumen el **servidor remoto oficial hospedado por Notion** en `https://mcp.notion.com/mcp` (nivel 1 de la preferencia de transporte declarada en `lex-mcp` §5 — cero dependencia local). Auth es vía **OAuth-per-user**: en la primera llamada, cada usuario autentica vía browser; el token es gestionado por la plataforma.

**Cursor (`.cursor/mcp.json`):**
```json
"notion": {
  "url": "https://mcp.notion.com/mcp"
}
```

**Claude Code (`.mcp.json`):**
```json
"notion": {
  "type": "http",
  "url": "https://mcp.notion.com/mcp"
}
```

> Cambio de UX: la versión anterior (npx + `NOTION_API_KEY` compartido) fue reemplazada por el endpoint hospedado con OAuth-per-user. Cada miembro del equipo autentica individualmente; ya no hay variable de entorno que configurar.

#### Override para el camino npx legacy (NOTION_API_KEY compartido)

Equipos que dependen de la configuración compartida vía env var (CI sin browser, integrations con permisos finos) pueden sobrescribir el JSON del servidor en `.ahrena/mcp/notion.json` con una desviación justificada por `_comment`, conforme `lex-mcp` §5:

```json
{
  "_comment": "Override: usando NOTION_API_KEY compartido por <razón — ej.: CI headless>. Decisión registrada en ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "NOTION_API_KEY": "${env:NOTION_API_KEY}" }
  },
  "claude-code": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "NOTION_API_KEY": "${NOTION_API_KEY}" }
  }
}
```

Obtener una integration key en [notion.so/my-integrations](https://www.notion.so/my-integrations). La integration DEBE tener acceso a las páginas/databases objetivo (compartir explícitamente en Notion). El override exige Node.js en el host; ejecute `make mcp-enable SERVER=notion PLATFORM=...` y el preflight ofrecerá instalarlo cuando falte. Nunca escribir tokens en archivos rastreados (ver `lex-mcp`).

### Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `search` | Busca páginas y databases por título o contenido |
| `get_page` | Obtiene metadatos y propiedades de una página |
| `create_page` | Crea una nueva página en un parent (página o database) |
| `update_page` | Actualiza propiedades de una página existente |
| `get_block_children` | Lista los bloques hijos de una página o bloque |
| `append_block_children` | Agrega bloques al final de una página o bloque |
| `delete_block` | Elimina un bloque específico |
| `list_databases` | Lista databases accesibles por la integration |
| `query_database` | Consulta un database con filtros y ordenación |
| `get_database` | Obtiene metadatos y schema de un database |
| `create_database` | Crea un nuevo database en una página |

### Parámetros de las herramientas más usadas

**`create_page`**
```
parent        (object, obligatorio) — {"page_id": "..."} o {"database_id": "..."}
properties    (object, obligatorio) — propiedades de la página; para una página simple: {"title": [{"text": {"content": "Título"}}]}
children      (array, opcional)     — lista de bloques de contenido inicial
icon          (object, opcional)    — ícono de la página (emoji o archivo)
cover         (object, opcional)    — imagen de portada
```

**`append_block_children`**
```
block_id      (string, obligatorio) — ID de la página o bloque padre
children      (array, obligatorio)  — lista de bloques a anexar
```

Tipos de bloque comunes en `children`:
```json
{ "type": "paragraph", "paragraph": { "rich_text": [{"text": {"content": "Texto"}}] } }
{ "type": "heading_2", "heading_2": { "rich_text": [{"text": {"content": "Sección"}}] } }
{ "type": "bulleted_list_item", "bulleted_list_item": { "rich_text": [{"text": {"content": "Ítem"}}] } }
{ "type": "code", "code": { "language": "python", "rich_text": [{"text": {"content": "print('hello')"}}] } }
```

**`query_database`**
```
database_id   (string, obligatorio)  — ID del database
filter        (object, opcional)     — filtro por propiedad
sorts         (array, opcional)      — ordenación [{property, direction}]
page_size     (integer, opcional)    — máximo de resultados (default: 100)
```

**`search`**
```
query         (string, opcional) — texto a buscar (vacío retorna todo)
filter        (object, opcional) — {"property": "object", "value": "page"} o "database"
sort          (object, opcional) — {"direction": "descending", "timestamp": "last_edited_time"}
```

### Casos de uso típicos

| Caso | Herramientas |
|---|---|
| Sincronizar doc del framework a Notion | `search` → `create_page` o `update_page` + `append_block_children` |
| Crear nota de reunión estructurada | `create_page` con `children` pre-formateados |
| Actualizar wiki del proyecto | `search` → `get_page` → `append_block_children` |
| Consultar database de tareas | `query_database` con filtros de estado |
| Listar databases disponibles | `list_databases` |

### Ejemplo de uso: crear página de documentación

```
# 1. Verificar si la página ya existe
search(query="Lexis: Herramientas MCP", filter={"property": "object", "value": "page"})

# 2. Si no se encuentra, crear en el wiki del proyecto
create_page(
  parent={"page_id": "WIKI-PAGE-ID"},
  properties={"title": [{"text": {"content": "Lexis: Herramientas MCP"}}]},
  children=[
    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Propósito"}}]}},
    {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Esta Lexis define..."}}]}}
  ]
)
```

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `kata-mcp-notion-read` — Kata de consulta de contenido de Notion (solo lectura)
- [Notion MCP Server — repositorio oficial](https://github.com/makenotion/notion-mcp-server)
- [Notion API — Block types](https://developers.notion.com/reference/block)
