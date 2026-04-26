# Kata: Escribir contenido en Notion via MCP

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación y actualización de páginas, blocos y propiedades en Notion via servidor MCP

## Objetivo

Crear o actualizar contenido en Notion (páginas, bloques, propiedades de base de datos) via servidor MCP. Cubre cuatro operaciones: crear una nueva página, agregar bloques a una página existente, actualizar propiedades de una página y eliminar un bloque específico. Siempre verifica que el destino existe antes de escribir y confirma acciones destructivas con el usuario.

## Cuándo Usar

- Cuando el usuario necesita crear una nueva página o documento en Notion
- Cuando se debe agregar contenido a una página existente (ej.: notas de reunión, sincronización de artefactos)
- Cuando las propiedades de una entrada de base de datos deben actualizarse (ej.: estado, fecha, responsable)
- Cuando un bloque específico debe eliminarse de una página
- Cuando es invocado por un Warrior que produce output destinado a Notion (ej.: sincronización de documentación, catálogo de eventos, ADR)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Operación | Sí | `create` (nueva página) \| `append` (agregar bloques) \| `update-props` (propiedades de página/entrada) \| `delete-block` (eliminar un bloque) |
| Destino | Condicional | ID o URL de la página o base de datos padre para `create`; ID o URL de la página para `append` y `update-props`; ID del bloque para `delete-block` |
| Contenido | Condicional | Contenido de bloques para `create` y `append`; mapa de propiedades para `update-props` |
| Título | Condicional | Título de la página — obligatorio para `create` |
| Manejo de duplicados | No | `skip` (no hacer nada si ya existe una página con el mismo título), `update` (agregar a la página existente), `create-new` (siempre crear); predeterminado: `skip` |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Verificar precondiciones y directivas del MCP
- [ ] 2. Identificar operación y destino
- [ ] 3. Verificar contenido existente (create / append)
- [ ] 4. Ejecutar operación de escritura
- [ ] 5. Confirmar y retornar resultado
```

### Paso 1: Verificar Precondiciones y Directivas del MCP

1. Consultar `.ahrena/.directives` conforme a `lex-directives`
2. Verificar que `notion` esté listado en `mcp.servers` conforme a `lex-mcp`. Si no está, informar al usuario y detenerse
3. Confirmar que `NOTION_API_KEY` esté definida en el entorno. Si no lo está, informar al usuario qué variable configurar y detenerse
4. Consultar `codex-mcp-notion` para identificar las herramientas y parámetros correctos para la operación solicitada

### Paso 2: Identificar Operación y Destino

1. Confirmar la operación: `create`, `append`, `update-props` o `delete-block`
2. Si el destino es una URL, extraer el ID (últimos 32 caracteres de la URL de Notion, formateados como UUID)
3. Si no se proporcionó el destino:
   - Para `create`: preguntar al usuario la página padre o base de datos donde debe crearse la nueva página
   - Para `append` y `update-props`: preguntar al usuario el ID o URL de la página
   - Para `delete-block`: preguntar al usuario el ID del bloque a eliminar
4. Si no se proporcionó contenido para `create` o `append`, preguntar al usuario qué escribir

### Paso 3: Verificar Contenido Existente (solo create / append)

Para `create`:
1. Llamar a `search(query="{título}", filter={"property": "object", "value": "page"})` para verificar si ya existe una página con el mismo título en Notion
2. Aplicar manejo de duplicados:
   - `skip` — si se encuentra una página correspondiente, informar al usuario y detenerse; retornar la URL de la página existente
   - `update` — si se encuentra una página correspondiente, cambiar al modo `append` usando el ID de la página encontrada
   - `create-new` — proceder independientemente de las páginas existentes

Para `append`:
1. Llamar a `get_page(page_id="{id}")` para confirmar que la página existe y recuperar su título actual
2. Si la página no existe, alertar al usuario y detenerse

Para `update-props` y `delete-block`: proceder directamente al Paso 4 (el destino es explícito).

### Paso 4: Ejecutar Operación de Escritura

**Operación `create`:**
1. Construir el objeto `properties` con el título de la página:
   ```json
   {"title": [{"text": {"content": "{título}"}}]}
   ```
2. Construir el array `children` con los bloques de contenido iniciales (ver formatos de bloques en `codex-mcp-notion`)
3. Llamar a `create_page(parent={...}, properties={...}, children=[...])`
4. Registrar el `id` y la `url` retornados de la nueva página

**Operación `append`:**
1. Construir el array `children` con los bloques a agregar
2. Llamar a `append_block_children(block_id="{page_id}", children=[...])`
3. Para contenido extenso (más de 20 bloques), dividir en múltiples llamadas `append_block_children` para respetar los límites de la API

**Operación `update-props`:**
1. Construir el objeto `properties` solo con los campos a actualizar (no incluir propiedades sin cambios)
2. Llamar a `update_page(page_id="{id}", properties={...})`

**Operación `delete-block`:**
1. **Confirmar con el usuario** antes de eliminar — declarar claramente qué bloque se eliminará (incluir ID del bloque y cualquier texto visible si es recuperable)
2. Tras la confirmación, llamar a `delete_block(block_id="{id}")`

### Paso 5: Confirmar y Retornar Resultado

1. Reportar el resultado al usuario:
   - `create`: "Página '{título}' creada en {url}"
   - `append`: "Contenido agregado a '{título de página}' ({url})"
   - `update-props`: "Propiedades actualizadas en '{título de página}' ({url})"
   - `delete-block`: "Bloque {id} eliminado de '{título de página}'"
2. Incluir la URL de la página en toda confirmación para que el usuario pueda navegar directamente
3. Si la operación falla, reportar el error claramente y sugerir los próximos pasos (verificar acceso, confirmar ID, verificar que la integración tenga acceso a la página o base de datos destino)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Nueva página | Página Notion | Página padre o base de datos especificada por el usuario |
| Contenido agregado | Bloques en página existente | Página especificada por el usuario |
| Propiedades actualizadas | Campos de la entrada de base de datos | Página/entrada especificada por el usuario |
| Confirmación | Texto con URL de la página | Respuesta al usuario |

## Ejemplo de Ejecución

### Ejemplo — Crear una página estructurada

```
Operación: create
Padre: https://notion.so/WIKI-PAGE-ID
Título: Event Storm — Módulo Plataforma
Contenido: heading "Transferencias Agendadas", tabla de eventos con 5 eventos
Manejo de duplicados: skip
```

Pasos ejecutados:
1. `search(query="Event Storm — Módulo Plataforma", filter={"property": "object", "value": "page"})` — ninguna página existente encontrada
2. `create_page(parent={"page_id": "WIKI-PAGE-ID"}, properties={title...}, children=[heading_2, table...])`
3. Resultado: "Página 'Event Storm — Módulo Plataforma' creada en https://notion.so/..."

### Ejemplo — Agregar contenido a página existente

```
Operación: append
Destino: https://notion.so/EXISTING-PAGE-ID
Contenido: párrafo "Actualizado 2026-04-26 — evento cancelado agregado"
```

Pasos ejecutados:
1. `get_page(page_id="EXISTING-PAGE-ID")` — página confirmada
2. `append_block_children(block_id="EXISTING-PAGE-ID", children=[paragraph...])`
3. Resultado: "Contenido agregado a 'Event Storm — Módulo Plataforma' (https://notion.so/...)"

## Restricciones

- **Usar solo MCP:** nunca llamar a la API REST de Notion directamente; siempre usar las herramientas del servidor MCP conforme a `lex-mcp`
- **Sin credenciales hardcoded:** autenticación exclusivamente via variable de entorno `NOTION_API_KEY`
- **Verificar antes de crear:** siempre ejecutar `search` para detectar duplicados antes de `create`, a menos que `create-new` esté explícitamente definido
- **Confirmar antes de eliminar:** siempre pedir confirmación al usuario antes de ejecutar `delete-block`
- **No sobrescribir sin instrucción:** `append` agrega al contenido existente; para reemplazar contenido, el usuario debe solicitar explícitamente la eliminación del bloque primero
- **Acceso de la integración:** si Notion retorna error 403 o "object not found", significa que la integración no recibió acceso a la página o base de datos destino — instruir al usuario a compartirlo con la integración en Notion

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `codex-mcp-notion` — Referencia de herramientas y parámetros del MCP Notion
- `kata-mcp-notion-read` — Kata para lectura de contenido Notion antes de escribir
- `lex-directives` — Cómo leer `.ahrena/.directives`
