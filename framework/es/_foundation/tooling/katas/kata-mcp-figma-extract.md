# Kata: Extraer tokens de diseño y specs de Figma vía MCP

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Extracción de tokens de diseño (colores, espaciados, tipografía) y especificaciones de componentes de un archivo Figma vía servidor MCP

## Objetivo

Extraer tokens de diseño y especificaciones de componentes de un archivo Figma vía servidor MCP, generando un archivo `tokens.json` estandarizado y documentación Markdown de specs de componentes. El resultado sirve como contrato de diseño para implementación frontend.

## Cuándo Usar

- Cuando un desarrollador necesita implementar un diseño Figma y solicita los tokens o specs
- Cuando los design tokens cambian en Figma y necesitan actualizarse en el proyecto
- Cuando se crea un nuevo componente en Figma que necesita documentarse para implementación

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| File ID de Figma | Sí | ID del archivo Figma (parte de la URL: `figma.com/file/{FILE_ID}/...`) |
| Modo de extracción | No | `tokens` (solo design tokens), `specs` (solo specs de componentes) o `all` (por defecto: `all`) |
| Node ID(s) | No | IDs de frames o componentes específicos a extraer (por defecto: archivo completo) |
| Destino | No | Directorio de salida (por defecto: `docs/design/`) |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y directivas
- [ ] 2. Identificar archivo y alcance
- [ ] 3. Extraer tokens de diseño (si se solicita)
- [ ] 4. Extraer specs de componentes (si se solicita)
- [ ] 5. Generar archivos de salida
- [ ] 6. Reportar resultado
```

### Paso 1: Verificar precondiciones MCP y directivas

1. Consultar `.ahrena/.directives` según `lex-directives`.
2. Verificar que `figma` esté listado en `mcp.servers` (según `lex-mcp`). Si no, informar al usuario y detener.
3. Confirmar que la variable de entorno `FIGMA_API_KEY` está definida. Si no, informar al usuario qué variable configurar y detener.
4. Consultar `codex-mcp-figma` para identificar las herramientas y parámetros correctos.

### Paso 2: Identificar archivo y alcance

1. Confirmar el File ID con el usuario (solicitar si no se proporcionó).
2. Si se proporcionaron Node IDs específicos, verificar que existen en el archivo vía `get_node`.
3. Definir el directorio de destino: `docs/design/` por defecto, o el valor informado por el usuario. Crear el directorio si no existe.

### Paso 3: Extraer tokens de diseño (si se solicita)

1. Llamar `get_local_variables(file_key="{FILE_ID}")` para obtener todas las variables del archivo.
2. Organizar las variables por tipo: `COLOR`, `FLOAT`, `STRING`, `BOOLEAN`.
3. Para variables del tipo `COLOR`: convertir valores `r/g/b/a` (0–1) a hexadecimal (`#RRGGBB` o `#RRGGBBAA`).
4. Mapear los nombres de variables a la estructura de tokens (ej.: `Color/Primary/500` → `color.primary.500`): reemplazar `/` por `.` y convertir a kebab-case.
5. Generar el objeto JSON de tokens en el formato:
   ```json
   {
     "color": { "primary": { "500": { "value": "#3380FF", "type": "color" } } },
     "spacing": { "4": { "value": "16", "type": "spacing" } }
   }
   ```

### Paso 4: Extraer specs de componentes (si se solicita)

1. Si se proporcionaron Node IDs específicos: llamar `get_node` para cada uno.
2. Si no se proporcionaron: llamar `get_file_components(file_key="{FILE_ID}")` para listar todos los componentes.
3. Para cada componente relevante, extraer: nombre, descripción, dimensiones, propiedades de variantes, estilos aplicados.
4. Estructurar las specs en Markdown con secciones por componente.

### Paso 5: Generar archivos de salida

1. **Tokens:** guardar el JSON generado en `{destino}/tokens.json`.
2. **Specs:** guardar el Markdown de especificaciones en `{destino}/components.md`.
3. Agregar encabezado de metadatos en los archivos generados:
   ```
   <!-- Generado automáticamente por kata-mcp-figma-extract -->
   <!-- Archivo Figma: {FILE_ID} | Fecha: {ISO-DATE} -->
   ```

### Paso 6: Reportar resultado

1. Presentar resumen: tokens extraídos por tipo (colores, espaciados, tipografía), componentes documentados.
2. Listar los archivos generados con sus rutas relativas.
3. En caso de falla parcial, indicar qué extracciones fallaron y el motivo.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Design tokens | JSON (estructura anidada por tipo) | `docs/design/tokens.json` |
| Specs de componentes | Markdown | `docs/design/components.md` |
| Reporte de extracción | Texto estructurado | Respuesta al usuario |

## Restricciones

- **Usar solo MCP:** nunca usar la API REST de Figma directamente; siempre usar herramientas del servidor MCP (según `lex-mcp`).
- **Sin credenciales hardcodeadas:** autenticación exclusivamente mediante variable de entorno `FIGMA_API_KEY`.
- **Solo lectura:** este Kata es read-only; nunca usar herramientas de escritura en Figma.
- **Destino explícito:** siempre confirmar el directorio de destino con el usuario antes de sobrescribir archivos existentes.

## Referencias

- `lex-mcp` — Leyes de uso de herramientas MCP
- `codex-mcp-figma` — Referencia de herramientas y parámetros del Figma MCP
- `lex-directives` — Cómo leer `.ahrena/.directives`
