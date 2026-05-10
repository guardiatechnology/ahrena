# Codex: MCP — Patrones Comunes

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Patrones transversales para cualquier integración de servidor MCP (Model Context Protocol) — preámbulo consumido por todas las referencias `codex-mcp-{servidor}`

## Visión General

Este Codex centraliza los patrones conceptuales y operativos compartidos por toda integración de servidor MCP en Ahrena (GitHub, Notion, Figma y cualquier nuevo servidor agregado). Los documentos individuales `codex-mcp-{servidor}` ahora se enfocan en herramientas, parámetros y ejemplos específicos de ese servidor, delegando el preámbulo común a este archivo. El objetivo es reducir el consumo de tokens cuando múltiples codexes MCP son referenciados en la misma operación y mantener autenticación, configuración y fallback en sincronía entre servidores.

## Contexto

- **Dominio:** cualquier servidor MCP integrado en Cursor o Claude Code.
- **Público objetivo:** Warriors y Katas que invocan herramientas MCP; consultado junto al codex específico del servidor.
- **Actualización:** cuando el framework agrega nuevo servidor MCP, introduce nueva plataforma (más allá de Cursor/Claude Code), o cambia el patrón de auth.

## Contenido

### Qué es MCP, brevemente

MCP (Model Context Protocol) expone capacidades de sistemas externos (servicios de API) directamente a agentes IA a través de una interfaz estandarizada de herramientas, con autenticación gestionada por la plataforma (Cursor, Claude Code) y sin construcción manual de llamadas de API. Cada herramienta MCP aparece al agente como una llamada de función tipada.

### Patrón de configuración compartido

Cada servidor MCP se define por un template JSON en `framework/mcp/<name>.json` con dos bloques de plataforma — `cursor` y `claude-code` — fusionados por `scripts/install.py` en la config de la respectiva plataforma:

```
.cursor/mcp.json          ← poblado desde el bloque "cursor"
.claude/settings.json     ← poblado desde el bloque "claude-code"
```

El merge es **aditivo**: las entradas gestionadas por el usuario para otros servidores se preservan; solo los servidores listados en `mcp.servers` en `.ahrena/.directives` se escriben/sobrescriben.

### Preferencia de transporte — racional de los trade-offs

`lex-mcp` §5 establece el orden obligatorio al declarar un servidor MCP: **HTTP remoto → binario nativo → npx**. Cada nivel agrega una clase distinta de dependencia local. Trade-offs por nivel:

| Nivel | Dep. local | Latencia | Actualización | Control de versión | Cuándo preferir |
|---|---|---|---|---|---|
| HTTP remoto | ninguna | red + servidor hospedado | proveedor (server-side) | proveedor | default cuando el proveedor ofrece endpoint oficial |
| Binario nativo stdio | ejecutable instalado | stdio local | release versionado | usuario (elige la versión instalada) | sin HTTP; el proveedor publica binario oficial |
| npx | Node.js + caché npm | stdio local con overhead de Node | en cada ejecución (`npx -y`) | paquete npm | sin HTTP ni binario oficial |

**Por qué HTTP es el default:**
- Cero dependencia local — el usuario no instala runtime ni binario; el servidor evoluciona sin release manual.
- Auth estandarizada vía header (`Authorization: Bearer ...`) o OAuth-per-user, ambos soportados por las plataformas (Cursor y Claude Code).
- Las fallas se exponen en status HTTP claros (401/403/429/5xx) con retry exponencial automático en los clientes oficiales.

**Por qué el binario es la segunda opción:**
- Funciona offline y tiene latencia mínima (sin hop de red).
- Ofrece control preciso de versión — útil cuando el proveedor introduce breaking changes entre releases.
- Costo: el usuario debe instalar/actualizar manualmente (o vía gestor de paquetes).

**Por qué npx queda al final:**
- Arrastra Node.js como dependencia transitiva — runtime pesado para un único caso de uso.
- `npx -y` descarga/cachea en cada ejecución fría, introduciendo latencia inicial.
- Los paquetes npm de terceros pueden ser archivados o comprometidos sin aviso (cadena de suministro más frágil que vendor-hosted).

Las desviaciones al orden (ej.: usar npx cuando HTTP existe) **DEBEN** justificarse en un comentario (`_comment`) dentro del JSON del servidor — ver ejemplo abajo. Justificaciones comunes aceptables: necesidad de configuración compartida vía env var (en lugar de OAuth-per-user), entorno air-gapped, dependencia de una característica presente solo en el nivel inferior.

```json
{
  "_comment": "Override: el equipo prefiere NOTION_API_KEY compartido en lugar del OAuth-per-user del endpoint HTTP oficial. Decisión registrada en ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "NOTION_API_KEY": "${env:NOTION_API_KEY}" }
  }
}
```

Docker no forma parte de la jerarquía hoy. Cuando se adopte un servidor MCP en Docker, su nivel **DEBE** definirse por ADR (decisión sobre overhead vs. aislamiento).

### Autenticación — regla uniforme

Todas las credenciales de servidor MCP **DEBEN**:

1. Provenir exclusivamente de variables de entorno declaradas en el template JSON.
2. Usar `${env:VAR_NAME}` en Cursor (MCP maneja la resolución) y `${VAR_NAME}` en Claude Code.
3. Nunca aparecer hardcodeadas en código, `.directives` o cualquier artefacto versionado (ver `lex-mcp`).

Nombres estándar de variables por servidor:

| Servidor | Env Var |
|---|---|
| GitHub | `GITHUB_PAT` |
| Notion | `NOTION_API_KEY` |
| Figma | `FIGMA_API_KEY` |

### Preferencia sobre CLI

Según `lex-mcp`, cuando un servidor MCP está **activo** (listado en `mcp.servers`) Y la herramienta existe en ese servidor, el agente **DEBE** usar la herramienta MCP en preferencia a cualquier CLI equivalente (ej.: MCP `create_pull_request` sobre `gh pr create`). El codex específico del servidor lista las herramientas disponibles.

### Comportamiento de fallback (común)

Si el servidor MCP está indisponible a mitad de la operación (red, auth expirada, herramienta ausente):

1. Reintentar una vez tras un breve backoff (el agente espera antes del retry; sin busy loop).
2. Si aún falla, el agente **DEBE** informar al usuario: qué servidor, qué herramienta, error observado.
3. Ofrecer alternativas explícitas:
   - Usar el CLI equivalente (si disponible) etiquetado como fallback.
   - Pausar el flujo hasta que el usuario restaure la conectividad.
   - Abortar la operación.
4. El agente **NO PUEDE** caer silenciosamente al CLI sin comunicar la indisponibilidad del MCP.

Ver `lex-mcp` §4 para la ley completa de fallback.

### Señales comunes de falla

| Síntoma | Causa probable | Acción |
|---|---|---|
| 401 / 403 en la primera llamada | Env var ausente / expirada | Pedir al usuario establecer/rotar la variable |
| 429 o rate-limit explícito | Demasiadas llamadas | Back off, reducir tamaño de batch, re-encolar |
| Timeout en cada llamada | Proceso del servidor MCP no corriendo | Reiniciar la plataforma (Cursor/Claude Code) o revisar logs de startup |
| "Tool not found" | Mismatch de versión o servidor no listado en `mcp.servers` | Confirmar config; actualizar paquete del servidor |

### Cuándo agregar nuevo servidor MCP

1. Crear `framework/mcp/<name>.json` con bloques `cursor` y `claude-code`.
2. Agregar `<name>` a `mcp.servers` en `.ahrena/.directives` cuando esté listo para usar.
3. Crear `codex-mcp-<name>.md` (específico del servidor: catálogo de herramientas + parámetros + ejemplos); referenciar **este codex** para patrones comunes.
4. Actualizar ejemplos en `lex-mcp` si el nuevo servidor introduce un modelo de autenticación novel.
5. Si el servidor alimenta un nuevo Kata, considerar un Kata de solo lectura primero (`kata-mcp-<name>-read`) antes de cualquier patrón de escritura.

## Referencias

- `lex-mcp` — leyes inquebrantables sobre uso de herramientas MCP
- `codex-mcp-github`, `codex-mcp-notion`, `codex-mcp-figma` — referencias específicas por servidor
- [Model Context Protocol spec](https://modelcontextprotocol.io/)
