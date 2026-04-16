# Kata: Sincronizar documentación a Notion vía MCP

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Sincronización de documentos del framework Ahrena a páginas o databases de Notion vía servidor MCP

## Objetivo

Sincronizar documentos del framework Ahrena (Lexis, Codex, Katas, Warriors, Cries) a Notion vía servidor MCP, creando nuevas páginas para documentos ausentes y actualizando páginas existentes para documentos modificados. El resultado es un espejo navegable de la documentación del framework en Notion.

## Cuándo Usar

- Cuando el usuario solicita sincronizar documentación del framework a Notion
- Después de agregar o actualizar artefactos significativos en el framework
- Cuando se crea un nuevo clade o subclade que necesita documentarse en Notion

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Página o database de destino en Notion | Sí | ID o URL de la página/database raíz en Notion donde se crearán los documentos |
| Alcance | No | Clade o subclade específico (ej.: `engineering/platform`); por defecto: todos |
| Idioma | No | Idioma de los documentos a sincronizar; por defecto: `language.default` en `.ahrena/.directives` |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y directivas
- [ ] 2. Determinar alcance y recopilar documentos
- [ ] 3. Localizar destino en Notion
- [ ] 4. Para cada documento: crear o actualizar página
- [ ] 5. Reportar resultado
```

### Paso 1: Verificar precondiciones MCP y directivas

1. Consultar `.ahrena/.directives` según `lex-directives`.
2. Verificar que `notion` esté listado en `mcp.servers` (según `lex-mcp`). Si no, informar al usuario y detener.
3. Confirmar que la variable de entorno `NOTION_API_KEY` está definida. Si no, informar al usuario qué variable configurar y detener.
4. Consultar `codex-mcp-notion` para identificar las herramientas y parámetros correctos.

### Paso 2: Determinar alcance y recopilar documentos

1. Identificar el idioma: leer `language.default` de `.ahrena/.directives`.
2. Determinar el directorio de origen: `.ahrena/framework/{lang}/{alcance}/` (o `.ahrena/framework/{lang}/` para todos).
3. Listar recursivamente los archivos `.md` con prefijo de Pilar (`lex-`, `codex-`, `kata-`, `warrior-`, `cry-`).
4. Para cada archivo, registrar: ruta relativa, título (primera línea H1), tipo de Pilar, fecha de modificación.

### Paso 3: Localizar destino en Notion

1. Usar `search` del Notion MCP para verificar que la página o database de destino existe y es accesible.
2. Si el destino es un database, confirmar que tiene una propiedad `title` para el nombre de la página.
3. Si el destino no se encuentra o no es accesible, informar al usuario y detener.

### Paso 4: Para cada documento — crear o actualizar página

Para cada documento recopilado en el Paso 2:

1. Usar `search` con el título del documento para verificar si ya existe una página correspondiente en Notion.
2. **Si no existe:** usar `create_page` con el título y contenido inicial. Convertir Markdown a bloques Notion (párrafos, headings, code blocks, listas).
3. **Si ya existe:**
   - Comparar la fecha de modificación del archivo con `last_edited_time` de la página Notion.
   - Si el archivo es más reciente: usar `append_block_children` para agregar una sección con el contenido actualizado y registrar fecha de sincronización.
   - Si la página Notion es más reciente: **no sobrescribir**. Registrar como conflicto e informar al usuario.
4. Registrar el resultado de cada documento (creado, actualizado, conflicto, ignorado).

### Paso 5: Reportar resultado

1. Presentar resumen: total de documentos procesados, creados, actualizados, conflictos (páginas más nuevas en Notion), ignorados.
2. Listar los conflictos identificados con nombre y URL de la página Notion, para que el usuario decida la acción.
3. En caso de falla parcial, listar qué documentos fallaron y el motivo.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Páginas creadas | Páginas Notion con contenido del documento | Notion — parent especificado |
| Páginas actualizadas | Bloques agregados a la página Notion existente | Notion — página existente |
| Reporte de sincronización | Texto estructurado (creados, actualizados, conflictos, ignorados) | Respuesta al usuario |

## Restricciones

- **No sobrescribir páginas más nuevas:** si la página Notion fue editada después de la última modificación del archivo, registrar como conflicto y esperar decisión del usuario.
- **Usar solo MCP:** nunca usar la API REST de Notion directamente; siempre usar herramientas del servidor MCP (según `lex-mcp`).
- **Sin credenciales hardcodeadas:** autenticación exclusivamente mediante variable de entorno `NOTION_API_KEY`.
- **Respetar el alcance declarado:** no sincronizar clades o subclades fuera del alcance especificado por el usuario.

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `codex-mcp-notion` — Referencia de herramientas y parámetros del Notion MCP
- `lex-directives` — Cómo leer `.ahrena/.directives`
