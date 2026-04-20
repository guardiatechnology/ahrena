# Kata: Consultar contenido de Notion vía MCP

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Lectura de páginas, databases y bloques de Notion vía servidor MCP para uso en el contexto local

## Objetivo

Obtener y leer contenido de Notion (páginas, databases, bloques) vía servidor MCP, trayendo la información al contexto de la sesión para referencia, análisis o procesamiento. Esta kata es estrictamente **solo lectura** — ninguna página ni bloque es creado o modificado.

## Cuándo Usar

- Cuando el usuario necesita consultar documentación, notas o decisiones registradas en Notion
- Cuando se necesitan entradas de un database de Notion (ej.: backlog, ADRs, tareas)
- Cuando el contenido de una página Notion debe ser analizado o referenciado durante la sesión

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Consulta o ID | Sí | Término de búsqueda textual, ID de página o URL de la página/database en Notion |
| Modo | No | `search` (búsqueda por texto), `page` (página específica por ID), `database` (entradas de database); por defecto: `search` |
| Filtro de database | No | Filtro de propiedades para `query_database` (ej.: estado, fecha, etiqueta) |
| Profundidad | No | `summary` (título + resumen) o `full` (contenido completo de los bloques); por defecto: `summary` |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y directivas
- [ ] 2. Identificar qué buscar
- [ ] 3. Obtener y leer el contenido
- [ ] 4. Presentar resultado al usuario
```

### Paso 1: Verificar precondiciones MCP y directivas

1. Consultar `.ahrena/.directives` según `lex-directives`.
2. Verificar que `notion` esté listado en `mcp.servers` (según `lex-mcp`). Si no, informar al usuario y detener.
3. Confirmar que la variable de entorno `NOTION_API_KEY` está definida. Si no, informar al usuario qué variable configurar y detener.
4. Consultar `codex-mcp-notion` para identificar las herramientas y parámetros correctos.

### Paso 2: Identificar qué buscar

1. Si el usuario proporcionó un ID o URL de página: usarlo en el Paso 3 con `get_page`.
2. Si el usuario proporcionó un ID de database: usarlo en el Paso 3 con `query_database`.
3. Si el usuario proporcionó un término de búsqueda: usarlo en el Paso 3 con `search`.
4. Si no se proporcionó ningún input, preguntar al usuario: "¿Qué página, database o término desea consultar en Notion?"

### Paso 3: Obtener y leer el contenido

**Modo `search`:**
1. Llamar `search(query="{término}")` para localizar páginas y databases correspondientes.
2. Presentar la lista de resultados (título, tipo, última edición) y confirmar con el usuario cuál elemento detallar.
3. Para el elemento seleccionado, llamar `get_page(page_id="{id}")`.
4. Si la profundidad es `full`: llamar `get_block_children(block_id="{id}")` para obtener el contenido completo.

**Modo `page`:**
1. Llamar `get_page(page_id="{id}")` para obtener metadatos y propiedades.
2. Si la profundidad es `full`: llamar `get_block_children(block_id="{id}")` para obtener los bloques de contenido.

**Modo `database`:**
1. Llamar `query_database(database_id="{id}", filter={...})` con los filtros opcionales informados por el usuario.
2. Para cada entrada retornada, registrar: título, propiedades relevantes, ID de página.
3. Si el usuario solicita detalles de una entrada específica, llamar `get_page` y `get_block_children` para esa entrada.

### Paso 4: Presentar resultado al usuario

1. Presentar el contenido recuperado de forma estructurada y legible.
2. Para databases: mostrar las entradas en formato de tabla con las propiedades más relevantes.
3. Para páginas: mostrar título, metadatos (última edición, creador) y contenido (resumen o completo según profundidad).
4. Indicar el ID y URL de cada elemento presentado para referencia futura.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Contenido de página | Texto estructurado (título, metadatos, bloques) | Respuesta al usuario |
| Entradas de database | Tabla con propiedades relevantes | Respuesta al usuario |
| Resultados de búsqueda | Lista de elementos correspondientes con título y tipo | Respuesta al usuario |

## Restricciones

- **Solo lectura:** esta kata nunca crea, modifica ni elimina páginas, bloques ni propiedades en Notion.
- **Usar solo MCP:** nunca usar la API REST de Notion directamente; siempre usar herramientas del servidor MCP (según `lex-mcp`).
- **Sin credenciales hardcodeadas:** autenticación exclusivamente mediante variable de entorno `NOTION_API_KEY`.
- **Confirmar antes de búsquedas amplias:** si la consulta puede retornar muchos resultados, presentar una muestra y confirmar con el usuario antes de continuar.

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `codex-mcp-notion` — Referencia de herramientas y parámetros del Notion MCP
- `lex-directives` — Cómo leer `.ahrena/.directives`
