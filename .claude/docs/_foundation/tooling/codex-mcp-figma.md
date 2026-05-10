# Codex: Figma MCP Server

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Tools and authentication for the Figma MCP server on Cursor and Claude Code

## Content

### Platform configuration

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

> Figma sits at tier 3 (npx) of the transport preference (`lex-mcp` §5) because Figma does not currently publish an official remote HTTP endpoint nor a standalone binary. Node.js is therefore a lazy dependency: installed on demand by `make mcp-enable SERVER=figma PLATFORM=...` via the preflight.
>
> The `FIGMA_API_KEY` variable must be defined in the environment. Generate a Personal Access Token in Figma → Settings → Account → Personal access tokens. The token needs read access to the target file. Never hardcode tokens in tracked files (see `lex-mcp`).

#### Local alternative: Figma Dev Mode MCP server

When the Figma desktop app is running with the Dev Mode panel active, it exposes a local MCP server at `http://127.0.0.1:3845/sse`. This is not a hosted endpoint (it still requires the desktop app running), but it eliminates npx/Node and surfaces some additional Dev Mode tools (selected component on canvas, code suggestions). Configuration:

```json
{
  "_comment": "Override: using the local Figma Dev Mode MCP server. Requires the Figma desktop app running with Dev Mode active.",
  "cursor": { "url": "http://127.0.0.1:3845/sse" },
  "claude-code": { "type": "http", "url": "http://127.0.0.1:3845/sse" }
}
```

Save as `.ahrena/mcp/figma.json` to override the default (npx) config. The override requires Figma desktop open on the machine; it does not work in CI or headless servers.

### How to get the Figma File ID

The File ID is the alphanumeric string in the Figma file URL:
```
https://www.figma.com/file/{FILE_ID}/File-Name
```

The Node ID is the identifier of a specific frame, component, or node, visible when inspecting the element in Figma.

### Available tools

| Tool | Description |
|---|---|
| `get_file` | Gets the complete Figma file document (node tree) |
| `get_node` | Gets a specific node by ID (frame, component, group, etc.) |
| `get_component` | Gets metadata for a component by ID |
| `get_component_set` | Gets a component variant set |
| `get_team_components` | Lists published components of a team |
| `get_file_components` | Lists all components in a file |
| `get_local_variables` | Gets all local variables of the file (design tokens) |
| `get_published_variables` | Gets published variables from a library |
| `export_node` | Exports a node as an image (PNG, SVG, PDF, JPEG) |
| `get_file_styles` | Gets styles defined in the file (colors, typography, effects) |
| `get_comments` | Lists comments on a file |

### Parameters for most-used tools

**`get_file`**
```
file_key      (string, required)  — Figma File ID
depth         (integer, optional) — node tree depth (default: full depth)
```

**`get_node`**
```
file_key      (string, required) — Figma File ID
node_id       (string, required) — node ID (e.g., "1:23")
```

**`get_local_variables`**
```
file_key      (string, required) — Figma File ID
```
Returns: variable collections with types (`COLOR`, `FLOAT`, `STRING`, `BOOLEAN`), modes, and values.

**`export_node`**
```
file_key      (string, required)  — Figma File ID
node_id       (string, required)  — node ID to export
format        (string, optional)  — "PNG" | "SVG" | "PDF" | "JPEG" (default: "PNG")
scale         (float, optional)   — export scale (default: 1)
```

### Variable to design token mapping

The `get_local_variables` response follows this structure:
```json
{
  "variables": {
    "{variable_id}": {
      "name": "Color/Primary/500",
      "resolvedType": "COLOR",
      "valuesByMode": {
        "{mode_id}": { "r": 0.2, "g": 0.5, "b": 1.0, "a": 1.0 }
      }
    }
  },
  "variableCollections": {
    "{collection_id}": {
      "name": "Design Tokens",
      "modes": [{ "modeId": "{mode_id}", "name": "Light" }]
    }
  }
}
```

Convert `r/g/b` (0–1) to hex: `#RRGGBB` = `round(r*255)`, `round(g*255)`, `round(b*255)`.

### Typical use cases

| Use case | Tools |
|---|---|
| Extract design tokens (colors, spacing, typography) | `get_local_variables` |
| Read specs for a specific component | `get_component` or `get_node` |
| Get all variants of a button | `get_component_set` |
| Export icon as SVG | `export_node` with `format="SVG"` |
| Inspect a frame structure | `get_node` + `get_file` with limited `depth` |
| List color styles of the file | `get_file_styles` |

### Usage example: extract color tokens

```
# 1. Get file variables
vars = get_local_variables(file_key="ABC123XYZ")

# 2. Filter by type COLOR and collection "Design Tokens"
# 3. Convert rgba values to hex and generate tokens.json:
{
  "color": {
    "primary": { "500": { "value": "#3380FF", "type": "color" } },
    "neutral": { "900": { "value": "#1A1A1A", "type": "color" } }
  }
}
# 4. Save to docs/design/tokens.json (see kata-mcp-figma-extract)
```
