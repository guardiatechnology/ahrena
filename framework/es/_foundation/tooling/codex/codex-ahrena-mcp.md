# Codex: Servidor MCP de Ahrena

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Servidor MCP interno del framework Ahrena para Cursor y Claude Code

## Visión General

Este Codex es la referencia del **servidor MCP `ahrena`** — el servidor interno del framework que expone Lexis, Codex, Katas, Warriors y Cries como herramientas consultables (solo lectura) por cualquier cliente MCP. A diferencia de `github`/`notion`/`figma` (integraciones externas opt-in), `ahrena` es **default-on**: viene activo en todo proyecto que adopta Ahrena. Lo consultan agentes que necesitan consumir el framework de forma quirúrgica (sin cargar archivos enteros) o agentes externos sin acceso a `.claude/`/`.cursor/` (Strands, automatizaciones, scripts).

## Contexto

- **Dominio:** Consulta de solo lectura al framework Ahrena (artefactos de Lexis, Codex, Katas, Warriors, Cries) y lectura de `.ahrena/.directives`.
- **Audiencia:** Agentes IA de Cursor y Claude Code; agentes externos (Strands, `apollo-agents`); scripts que necesitan leer el framework programáticamente.
- **Actualización:** Cuando se añadan nuevas herramientas al servidor (mutación del contrato de tools); cuando cambie el canal de distribución (release v1 GitHub Release → v2 PyPI).

## Contenido

### Configuración por plataforma

La configuración canónica está en `framework/mcp/ahrena.json`. `install.py` la mergea en:

**Cursor (`.cursor/mcp.json`):**
```json
"ahrena": {
  "command": "ahrena-mcp",
  "args": ["--root", "${workspaceFolder}"]
}
```

**Claude Code (`.mcp.json` en el root del proyecto + `enabledMcpjsonServers` en `.claude/settings.json`):**
```json
"ahrena": {
  "command": "ahrena-mcp",
  "args": ["--root", "${workspaceFolder}"]
}
```

> El comando `ahrena-mcp` es el console script declarado en `tools/ahrena-mcp/pyproject.toml` (`[project.scripts]`). Queda disponible en `PATH` después de que `install.py` ejecute `pipx install --force .ahrena/tools/ahrena-mcp` (ver §Instalación). pipx copia el paquete a su entorno gestionado; por eso, el comando sigue disponible si se elimina el directorio `.ahrena/` local del proyecto. No existe dependencia de PyPI ni de `uv`/`uvx` para que el camino default-on funcione.

### Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `ahrena_query_lex` | Devuelve el markdown completo de un Lexis (e.g., `lex-idempotency`) |
| `ahrena_get_codex` | Devuelve el markdown completo de un Codex (e.g., `codex-restful-apis`) |
| `ahrena_list_warriors` | Lista warriors; filtro opcional por `clade` (e.g., `engineering`) |
| `ahrena_list_cries` | Lista cries (slash commands) registradas en el framework |
| `ahrena_search` | Búsqueda ranqueada en todo el framework; filtros por `pilar` y `lang` |
| `ahrena_resolve_ref` | Verifica si una referencia existe (e.g., `lex-idempotency`); fallback cross-language |
| `ahrena_get_directives` | Devuelve `.ahrena/.directives` parseado |

### Parámetros de las herramientas

**`ahrena_query_lex`**
```
name (string, obligatorio) — nombre corto del Lexis (e.g., "lex-idempotency")
lang (string, opcional)    — código BCP 47; default: language.default en .directives
```

**`ahrena_get_codex`**
```
name (string, obligatorio) — nombre corto del Codex
lang (string, opcional)    — default: language.default en .directives
```

**`ahrena_list_warriors`**
```
clade (string, opcional)   — filtro por clade (e.g., "engineering"); vacío = sin filtro
lang  (string, opcional)   — default: language.default
```

**`ahrena_list_cries`**
```
lang (string, opcional)    — default: language.default
```

**`ahrena_search`**
```
query (string, obligatorio) — término de búsqueda
pilar (string, opcional)    — "lexis" \| "codex" \| "katas" \| "warriors" \| "cries"; vacío = todos
lang  (string, opcional)    — default: language.default
limit (integer, opcional)   — default: 30
```

Salida: lista ranqueada por número de coincidencias en el archivo, con `artifact`, `pilar`, `lang`, `path`, `line`, `snippet`, `score`.

**`ahrena_resolve_ref`**
```
ref  (string, obligatorio) — nombre corto (e.g., "lex-idempotency")
lang (string, opcional)    — default: language.default
```

Salida: `{exists, name, pilar, lang, path}`. Cuando la referencia existe en otro idioma pero no en el solicitado, devuelve el resultado con la clave `warning` indicando el fallback.

**`ahrena_get_directives`**
Sin parámetros. Devuelve el YAML parseado de `.ahrena/.directives`.

### Cuándo usar (y cuándo no)

**Se deben usar las herramientas de `ahrena` cuando:**
- El agente necesita consultar **un** Lexis o Codex específico en medio de la sesión (sin inflar el contexto vía `@` import del archivo entero).
- El agente necesita hacer búsqueda cross-pilar (`circuit breaker` en cualquier artefacto; ranking por score).
- El agente es externo a Cursor/Claude Code y no tiene acceso a los archivos espejados en `.cursor/`/`.claude/` (e.g., Strands, scripts CI, `apollo-agents`).
- El agente necesita resolver una referencia de forma determinística (`lex-idempotency` existe? en qué path?).

**NO se debe usar `ahrena` para:**
- Cargar **muchos** artefactos a la vez — la lectura directa del filesystem es más eficiente.
- Mutar artefactos del framework. El servidor es solo lectura por diseño (write tools `ahrena_create_lex` etc. están fuera de alcance en la primera iteración).
- Sustituir los Lexis con `alwaysApply: true` que Cursor/Claude Code cargan en el boot — esos siguen siendo el mecanismo nativo de gobernanza eager.

### Instalación

#### Adopción estándar (default-on, vía `install.py`)

Toda adopción del framework Ahrena activa `ahrena` automáticamente. `scripts/install.py` hace todo:

1. **Copia el source del paquete** — `tools/ahrena-mcp/` (del source repo Ahrena) se copia a `.ahrena/tools/ahrena-mcp/` en el proyecto adopter, sin `.venv` ni caches.
2. **Instala vía `pipx`** — `pipx install --force .ahrena/tools/ahrena-mcp`. pipx crea una copia autocontenida y el console script `ahrena-mcp` (declarado en `pyproject.toml`) queda disponible en `PATH` sin conservar una dependencia del directorio source copiado.
3. **Mergea configs MCP** — `framework/mcp/ahrena.json` se mergea en `.cursor/mcp.json` (Cursor) y `.mcp.json` en el root + `enabledMcpjsonServers: ["ahrena"]` en `.claude/settings.json` (Claude Code).
4. **Prerrequisito activador** — `framework/.directives.sample` lista `mcp.servers: [ahrena]` descomentado por defecto; cuando `ahrena` está en `mcp.servers`, los pasos anteriores se ejecutan.

El adopter ejecuta `make install` (o el equivalente `python3 .ahrena/install.py`) — listo. Tras reiniciar el cliente MCP (Claude Code/Cursor), aparecen las 7 herramientas `ahrena_*`.

**Comportamiento en re-install / update:**
- Primera vez (no instalado): `pipx install` silencioso.
- Instalación editable heredada, o modo de instalación no verificable: reparación automática no editable sin prompt.
- Paquete ya instalado + sesión interactiva: prompt `[y/N]` para reinstalar (default-no, preserva).
- Paquete ya instalado + no-TTY (CI): preserva sin prompt.

**Opt-out:** comentar la línea `- ahrena` en `.ahrena/.directives` antes del install. Para desactivar post-install: ejecutar `scripts/uninstall.py` (que invoca `pipx uninstall ahrena-mcp` best-effort) o quitar `ahrena` de `enabledMcpjsonServers` en `.claude/settings.json` + de `mcpServers` en `.cursor/mcp.json` y `.mcp.json`.

#### Cuando `pipx` no está disponible

`install.py` detecta la ausencia de `pipx` en el `PATH`, imprime `WARNING` en `stderr` con el enlace de instalación ([pipx.pypa.io](https://pipx.pypa.io/stable/installation/)), y continúa (no fatal). Caminos para desbloquear:

1. **Instalar pipx y re-ejecutar `install.py`** (recomendado): `brew install pipx` (macOS), `python3 -m pip install --user pipx` + `python3 -m pipx ensurepath` (Linux/Windows).
2. **Instalar manualmente sin pipx**: `pip install --user .ahrena/tools/ahrena-mcp` y ajustar `PATH` para incluir `~/.local/bin` (Linux/macOS) o `%APPDATA%\Python\Scripts` (Windows). El `command: ahrena-mcp` en `.mcp.json` sigue siendo válido.

#### Adopter externo sin framework instalado (después del release)

Para agentes o scripts que **no** ejecutan `install.py` (Strands en proyecto no-Ahrena, CI ad-hoc), ver `.claude/plans/plan-021-ahrena-mcp-server.md` §Release & Distribution. Tras release v1 (PyPI), el camino recomendado es `uvx ahrena-mcp --root <repo-ahrena>` (zero-install) o `pipx install ahrena-mcp` (persistente). Pre-release, `pipx install --spec <github-release-url> ahrena-mcp`.

### Rendimiento

Mediciones del spike (759 artefactos × 3 idiomas):

| Operación | Latencia típica |
|---|---|
| Boot del server (cold) | ~1.0 s (Python + imports + scan inicial) |
| Boot subsiguiente en sesión (cache caliente) | < 50 ms |
| `ahrena_query_lex` (cache hit) | < 1 ms |
| `ahrena_search` (con `ripgrep`) | 80–100 ms |
| `ahrena_search` (fallback Python regex) | 200–500 ms |

Recomendación: instalar `ripgrep` en el host (`brew install ripgrep`) para el camino rápido. Sin ripgrep, el servidor cae automáticamente al fallback Python — funciona, pero más lento en frameworks grandes.

### Descubrimiento del `--root`

El servidor descubre el root del framework Ahrena en el siguiente orden:

1. Flag `--root <path>` en la invocación.
2. Variable de entorno `AHRENA_ROOT`.
3. Walk-up desde `cwd` buscando el directorio `.ahrena/`.

Cuando el servidor sube en un proyecto Ahrena, el walk-up encuentra `.ahrena/` automáticamente. Los adopters que ejecuten el servidor desde fuera del proyecto deben usar `--root` o `AHRENA_ROOT`.

### Limitaciones conocidas (spike inicial)

- **Sin `ahrena_get_topology`** hasta que `docs/internal/warrior-topology-2026.md` exista (depende del plan-011).
- **Cache solo por `mtime` en archivos ya indexados** — `loader.get()` re-escanea cuando el `mtime` cambia, pero **no detecta archivos nuevos ni borrados** durante una sesión larga del server (el índice se construye en el boot y se actualiza por archivo individual). En la práctica esto rara vez importa (los artefactos del framework cambian poco intra-sesión); cuando importe, reiniciar el cliente MCP recrea el índice.
- **Sin parsing de frontmatter** — las tools devuelven markdown crudo. Filtrar por metadatos (e.g., `alwaysApply: true`) es responsabilidad del consumidor.
- **Búsqueda cross-language puede tener dedup parcial** — un término presente en pt-BR y en inglés aparece dos veces en la lista de hits (una por idioma) cuando no se especifica `lang`.

## Restricciones

- **Solo lectura.** La mutación de Lexis/Codex/Katas/Warriors/Cries vía MCP está fuera de alcance. Para crear artefactos, se deben usar las Cries del framework (`/cry-new-lex`, `/cry-new-codex`, etc.).
- **No sustituye `lex-mcp`.** El servidor está sujeto a `lex-mcp` rule 3 (declarado en `mcp.servers`) — `.directives.sample` ya cumple.
- **Path absoluto fijado se rompe al mover el repo.** Cuando se use override local con `command: python -m ahrena_mcp.server`, la venv donde el paquete está instalado debe permanecer en el path acordado.

## Referencias

- `lex-mcp` — Lexis que gobierna el uso de servidores MCP.
- `codex-mcp-common` — Patrones MCP compartidos (autenticación vía env vars, fallback).
- `framework/mcp/ahrena.json` — Configuración canónica mergeada por el installer.
- `tools/ahrena-mcp/` — Código fuente del servidor (en el repo Ahrena).
- `tools/ahrena-mcp/README.md` — Manual técnico del paquete (instalación, smoke test).
- `tools/ahrena-mcp/CHANGELOG.md` — Histórico de cambios del servidor.
- `.claude/plans/plan-021-ahrena-mcp-server.md` — Plan de implementación completo, incluyendo §Release & Distribution.
