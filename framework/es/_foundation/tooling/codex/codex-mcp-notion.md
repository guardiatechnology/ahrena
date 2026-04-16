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

**Cursor (`.cursor/mcp.json`):**
```json
"notion": {
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": { "NOTION_API_KEY": "${env:NOTION_API_KEY}" }
}
```

**Claude Code (`.claude/settings.json`):**
```json
"notion": {
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": { "NOTION_API_KEY": "${NOTION_API_KEY}" }
}
```

> La variable `NOTION_API_KEY` debe estar definida en el entorno. Obtener una integration key en [notion.so/my-integrations](https://www.notion.so/my-integrations). La integration DEBE tener acceso a las páginas/databases objetivo (compartir explícitamente en Notion). Nunca escribir tokens en archivos rastreados (ver `lex-mcp`).

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

### Casos de uso típicos

| Caso | Herramientas |
|---|---|
| Sincronizar doc del framework a Notion | `search` → `create_page` o `update_page` + `append_block_children` |
| Crear nota de reunión estructurada | `create_page` con `children` pre-formateados |
| Actualizar wiki del proyecto | `search` → `get_page` → `append_block_children` |
| Consultar database de tareas | `query_database` con filtros de estado |
| Listar databases disponibles | `list_databases` |

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `kata-mcp-notion-read` — Kata de consulta de contenido de Notion (solo lectura)
- [Notion MCP Server — repositorio oficial](https://github.com/makenotion/notion-mcp-server)
- [Notion API — Block types](https://developers.notion.com/reference/block)
