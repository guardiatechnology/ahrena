# Codex: Figma MCP Server

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Herramientas y autenticación del servidor MCP de Figma para Cursor y Claude Code

## Resumen General

Este Codex es la referencia para usar el **servidor MCP de Figma** en proyectos Ahrena. Ver `codex-mcp-common` para patrones MCP compartidos (autenticación, configuración, fallback). Este documento se enfoca en herramientas, parámetros y casos de uso específicos de Figma: extraer tokens de diseño, leer specs de componentes, obtener dimensiones de frames para implementación.

## Contexto

- **Dominio:** Lectura de archivos Figma vía MCP — componentes, frames, variables (design tokens), estilos y metadatos de nodos.
- **Público objetivo:** Agentes IA que extraen especificaciones de diseño de Figma para implementación o documentación en proyectos Ahrena.
- **Actualización:** Cuando se agreguen nuevas herramientas al servidor MCP de Figma o cuando cambie la estructura de variables/tokens.

## Contenido

### Configuración por plataforma

**Cursor (`.cursor/mcp.json`):**
```json
"figma": {
  "command": "npx",
  "args": ["-y", "figma-developer-mcp", "--stdio"],
  "env": { "FIGMA_API_KEY": "${env:FIGMA_API_KEY}" }
}
```

**Claude Code (`.mcp.json`):**
```json
"figma": {
  "command": "npx",
  "args": ["-y", "figma-developer-mcp", "--stdio"],
  "env": { "FIGMA_API_KEY": "${FIGMA_API_KEY}" }
}
```

> Figma queda en el nivel 3 (npx) de la preferencia de transporte (`lex-mcp` §5) porque Figma no publica hoy un endpoint HTTP remoto oficial ni un binario standalone. Node.js es entonces dependencia lazy: instalada bajo demanda por `make mcp-enable SERVER=figma PLATFORM=...` vía preflight.
>
> La variable `FIGMA_API_KEY` debe estar definida en el entorno. Generar un Personal Access Token en Figma → Settings → Account → Personal access tokens. El token necesita acceso de lectura al archivo objetivo. Nunca escribir tokens en archivos rastreados (ver `lex-mcp`).

#### Alternativa local: Figma Dev Mode MCP server

Cuando la app Figma desktop está corriendo con el panel Dev Mode activo, expone un servidor MCP local en `http://127.0.0.1:3845/sse`. No es un endpoint hospedado (sigue exigiendo la app desktop en ejecución), pero elimina npx/Node y expone algunas herramientas extra de Dev Mode (componente seleccionado en el canvas, code suggestions). Configuración:

```json
{
  "_comment": "Override: usando el servidor local Figma Dev Mode MCP. Exige la app Figma desktop corriendo con Dev Mode activo.",
  "cursor": { "url": "http://127.0.0.1:3845/sse" },
  "claude-code": { "type": "http", "url": "http://127.0.0.1:3845/sse" }
}
```

Guarde como `.ahrena/mcp/figma.json` para sobrescribir la configuración por defecto (npx). El override exige Figma desktop abierto en la máquina; no funciona en CI ni en servidores headless.

### Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `get_file` | Obtiene el documento completo del archivo Figma (árbol de nodos) |
| `get_node` | Obtiene un nodo específico por ID (frame, componente, grupo, etc.) |
| `get_component` | Obtiene metadatos de un componente por ID |
| `get_component_set` | Obtiene un conjunto de variantes de componente |
| `get_team_components` | Lista componentes publicados de un equipo |
| `get_file_components` | Lista todos los componentes de un archivo |
| `get_local_variables` | Obtiene todas las variables locales del archivo (design tokens) |
| `get_published_variables` | Obtiene variables publicadas de una biblioteca |
| `export_node` | Exporta un nodo como imagen (PNG, SVG, PDF, JPEG) |
| `get_file_styles` | Obtiene estilos definidos en el archivo (colores, tipografía, efectos) |
| `get_comments` | Lista comentarios de un archivo |

### Casos de uso típicos

| Caso | Herramientas |
|---|---|
| Extraer design tokens (colores, espaciados, tipografía) | `get_local_variables` |
| Leer spec de un componente específico | `get_component` o `get_node` |
| Obtener todas las variantes de un botón | `get_component_set` |
| Exportar ícono como SVG | `export_node` con `format="SVG"` |
| Inspeccionar estructura de un frame | `get_node` + `get_file` con `depth` limitado |
| Listar estilos de color del archivo | `get_file_styles` |

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `kata-mcp-figma-extract` — Kata para extracción de tokens y specs de Figma
- [figma-developer-mcp — repositorio del servidor](https://github.com/figma/figma-developer-mcp)
- [Figma API — Variables](https://www.figma.com/developers/api#variables)
