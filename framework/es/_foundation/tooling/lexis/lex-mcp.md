# Lexis: Uso Obligatorio de Herramientas MCP

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Uso de servidores MCP por agentes IA en proyectos Ahrena

## Propósito

Los servidores MCP (Model Context Protocol) exponen capacidades de sistemas externos — como GitHub, Notion y Figma — directamente a agentes IA, con autenticación gestionada y sin necesidad de construir llamadas a la API manualmente. Cuando un servidor MCP está activo para una operación, usarlo es más seguro, más consistente y más trazable que ejecutar el comando CLI equivalente.

Esta Lexis existe para garantizar que **todo agente prefiera las herramientas MCP disponibles sobre los equivalentes CLI**, que **las credenciales nunca se expongan en archivos rastreados** y que **solo se utilicen los servidores declarados en `.ahrena/.directives`**.

## Ley

> **Todo agente DEBE usar la herramienta MCP disponible cuando un servidor MCP activo provee una capacidad para la operación actual. Las credenciales de autenticación DEBEN proporcionarse exclusivamente mediante variables de entorno. El agente NO PUEDE usar servidores MCP no listados en `mcp.servers` en `.ahrena/.directives`.**

## Reglas

### 1. Preferencia por herramientas MCP

Al ejecutar una operación soportada por un servidor MCP activo, el agente **DEBE**:

1. Verificar si el servidor MCP correspondiente está listado en `mcp.servers` en `.ahrena/.directives`.
2. Usar la herramienta MCP en lugar del equivalente CLI (ej.: usar `create_pull_request` del GitHub MCP en lugar de `gh pr create`).
3. Consultar el Codex del servidor MCP correspondiente (`codex-mcp-github`, `codex-mcp-notion`, `codex-mcp-figma`) para identificar la herramienta y los parámetros correctos.

### 2. Autenticación exclusivamente mediante variables de entorno

El agente **DEBE** garantizar que:

1. Las credenciales (tokens, API keys) se proporcionan solo mediante variables de entorno referenciadas en los archivos de configuración MCP (`mcp.json`, `settings.json`).
2. Ningún token, API key o secreto se escribe en `.ahrena/.directives`, en archivos rastreados por git o en ningún artefacto generado.
3. Si la variable de entorno requerida no está definida, el agente informa al usuario qué variable configurar antes de continuar.

### 3. Uso restringido a los servidores declarados

El agente **NO PUEDE**:

1. Activar o usar un servidor MCP no declarado en `mcp.servers` en `.ahrena/.directives`.
2. Agregar servidores MCP a la configuración de plataforma (`.cursor/mcp.json`, `.claude/settings.json`) sin instrucción explícita del usuario.
3. Modificar la sección `mcp.servers` en `.ahrena/.directives` sin solicitud explícita del usuario.

### 4. Comportamiento de fallback cuando MCP no está disponible

Si el servidor MCP requerido no está disponible a mitad de operación (servidor caído, variable de entorno ausente, herramienta no soportada, rate-limit, timeout):

1. **Reintentar una vez** con backoff breve (por defecto: 5 segundos). Las fallas transientes ocurren; un retry evita escalación espuria.
2. Si el retry aún falla, el agente **DEBE** informar al usuario con contexto estructurado:
   - Qué servidor (`github`, `notion`, `figma`).
   - Qué herramienta fue intentada.
   - Error observado (status HTTP, mensaje).
3. El agente **DEBE** entonces ofrecer opciones explícitas — sin elegir silenciosamente:
   - **(a)** Usar el CLI equivalente como fallback (cuando existe y es seguro), claramente etiquetado como fallback.
   - **(b)** Pausar el flujo hasta que el usuario restaure la conectividad (credenciales, restart del servidor).
   - **(c)** Abortar la operación con mensaje claro.
4. El agente **NO PUEDE** caer silenciosamente al CLI sin la opción presentada en el Paso 3.
5. El agente **NO PUEDE** entrar en loop de retry más allá del Paso 1 — la falla persistente exige decisión humana.

Las señales comunes de falla y sus causas típicas están listadas en `codex-mcp-common` — consultar antes de presentar al usuario.

## Alcance

- **Aplica a:** todas las operaciones donde un servidor MCP activo provee una herramienta equivalente a la operación solicitada.
- **Agentes vinculados:** todos los Warriors y agentes genéricos.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Credenciales expuestas:** hacer hardcoding de tokens en archivos rastreados constituye una violación de seguridad grave; requiere rotación inmediata de la credencial afectada.
2. **Servidores no autorizados:** usar servidores no declarados viola el principio de mínimo privilegio y puede exponer datos del proyecto a sistemas no aprobados.
3. **Inconsistencia:** mezclar MCP y CLI para la misma operación sin criterio crea resultados impredecibles y dificulta la auditoría.
4. **Remediación:** el agente debe releer las directivas, identificar los servidores MCP activos y el Codex correspondiente, y repetir la operación usando la herramienta MCP correcta.

## Ejemplos

### Correcto

```
# mcp.servers en .ahrena/.directives lista "github"
# Agente crea PR vía MCP:
create_pull_request(
  owner="acme",
  repo="mi-proyecto",
  title="feat: nueva funcionalidad",
  head="feat/nueva",
  base="main"
)
```

```
# Variable de entorno configurada externamente:
# export NOTION_API_KEY="secret_..."
# Agente crea página en Notion vía MCP:
create_page(parent={"database_id": "..."}, properties={...})
```

### Incorrecto

```
# ❌ Hardcoding de token en .directives o en cualquier archivo rastreado:
# mcp_token: "ghp_abc123..."

# ❌ Usando gh CLI cuando MCP GitHub está disponible y listado:
# gh pr create --title "feat: nueva" --base main

# ❌ Usando servidor MCP no listado en mcp.servers:
# (usando un servidor MCP de un sistema no declarado en las directivas)
```

## Validación Automatizada

- **Herramienta:** verificación por el propio agente antes de ejecutar operaciones cubiertas por MCP; `validate.py` verifica que `mcp.servers` esté presente en `.directives` cuando existen archivos de configuración MCP.
- **Momento:** al iniciar cualquier operación que involucre GitHub, Notion o Figma.
- **Métrica:** 100% de las operaciones cubiertas por MCP activo deben usar la herramienta MCP; 0 credenciales en archivos rastreados.
