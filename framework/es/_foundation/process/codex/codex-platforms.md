# Codex: Aplicación del framework por plataforma (platforms.yaml)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Transposición y aplicación de los artefactos del Ahrena en cada plataforma (Cursor, futuras)

## Visión general

Este Codex documenta el archivo **`platforms.yaml`**, que define por plataforma **cómo se transponen y aplican los artefactos del framework**: qué Pilar se convierte en qué recurso de la plataforma (transposición) y con qué opciones (alwaysApply, globs, description) se genera cada artefacto. El instalador y el sync (ej. `python .ahrena/update.py --sync-cursor`) usan este archivo para generar `.cursor/` (u otra IDE) de forma controlada y optimizada.

## Contexto

- **Dominio:** Integración del Ahrena con plataformas (Cursor hoy; OpenAI, Claude, otras en el futuro)
- **Público:** Mantenedores del framework, integradores y quien personalice la generación por plataforma
- **Actualizar cuando:** Se añada una nueva plataforma o se cambie la política de aplicación (alwaysApply, globs)

## Contenido

### Ubicación del archivo

| Origen | Ruta | Uso |
|--------|------|-----|
| **Por defecto (framework)** | `framework/platforms.yaml` | Se envía con el framework; se copia a `.ahrena/framework/platforms.yaml` en la instalación |
| **Override (proyecto)** | `.ahrena/platforms.yaml` | Opcional; el proyecto puede sobrescribir o extender el valor por defecto |

El script de instalación/sync hace merge: primero carga el default, luego aplica el override (por clave de plataforma y, dentro de `rules`, por rule key).

### Estructura por plataforma

Cada plataforma tiene una clave de primer nivel (ej. `cursor`) con:

1. **`transposition`** — mapeo Pilar Ahrena → recurso de la plataforma  
   - Ejemplo Cursor: `lex` → `rules`, `codex` → `rules`, `kata` → `skills`, `warrior` → `agents`, `cry` → `commands`
2. **Secciones por recurso** (ej. `rules`) — configuración de aplicación por artefacto  
   - Para Cursor: en `rules`, cada clave es el **rule key** (ruta del artefacto sin idioma y sin `.md`); el valor define `alwaysApply`, `globs` y `description`.

### Rule key

El **rule key** identifica el artefacto de forma invariante entre idiomas y plataformas:

- Ruta relativa al framework **sin** el segmento de idioma y **sin** `.md`  
- Ejemplo: `en/_foundation/process/lexis/lex-directives.md` → `_foundation/process/lexis/lex-directives`

### Política por defecto (Cursor)

- **Por defecto para todas las rules:** `alwaysApply: false`; **description** siempre presente (en el YAML o derivada del cuerpo del artefacto) para que Cursor aplique la rule de forma inteligente.
- **Excepciones con `alwaysApply: true`** (definidas en `platforms.yaml`): ej. `lex-directives`, `lex-checkpoint`.

### Disciplina con `alwaysApply: true` / `essential: true`

Ambas flags inflan el contexto base de cada sesión (rules Cursor con `alwaysApply: true` se cargan siempre; docs Claude Code con `essential: true` se inlinan en `CLAUDE.md`). Agregar un artefacto con esas flags cuesta tokens de contexto en 100% de las sesiones, no solo en las relevantes.

Reglas:

1. **Por defecto es siempre `false`.** Marcar `true` exige justificación explícita en el PR que introduce el cambio.
2. **Un PR que agrega `alwaysApply: true` o `essential: true` a una Lexis/Codex DEBE incluir un ADR** (vía `kata-adr-write`) explicando por qué el artefacto es esencial al punto de vivir en el contexto base de cada sesión.
3. **Revisar candidatos periódicamente** (sugerido: cada versión mayor del framework): ¿el artefacto sigue siendo leído en la mayoría de las sesiones? Si no → degradar a `false`.

### Subconjunto YAML soportado por el parser customizado

`scripts/install.py` trae un parser YAML stdlib-only intencionalmente estrecho. El parser soporta:

- Claves de nivel superior con claves anidadas (indentación 2+ espacios).
- Valores escalares: strings (con o sin comillas, escape `"` soportado), booleanos (`true`/`false` case-insensitive), enteros.
- Mapas anidados vía indentación.
- Listas vía entradas `- item` bajo clave que declara lista.

El parser **NO** soporta:

- Anchors (`&anchor`) y aliases (`*alias`).
- Escalares multi-línea con `|` o `>`.
- Flow-style (`[a, b]`, `{k: v}`).
- Strings entre comillas cruzando múltiples líneas.

Si `platforms.yaml` o `.directives` necesita feature fuera de ese subset: o (a) refactorizar para quedar dentro del subset, o (b) instalar `pyyaml` opcional — `scripts/install.py` detecta automáticamente y usa cuando está disponible.

### Uso en el sync de Cursor

Al ejecutar `python .ahrena/update.py --sync-cursor` (o `make sync-cursor`):

1. El script carga `platforms.yaml` (default + override).
2. Usa `cursor.transposition` para decidir el destino de cada Pilar (ruta y formato).
3. Usa `cursor.rules` para construir el frontmatter de los `.mdc` (alwaysApply, globs, description). Las rules no listadas reciben el default: alwaysApply false, description derivada del cuerpo.

### OpenAI Codex

Con `--platform codex`, Ahrena transpone sus pilares a recursos nativos de OpenAI Codex:

| Pilar Ahrena | Recurso OpenAI Codex |
|---|---|
| Lexis | `.codex/docs/lex/` y contrato operativo administrado en `AGENTS.md` |
| Codex | `.codex/docs/codex/` para consulta progresiva |
| Katas | `.agents/skills/<nombre>/SKILL.md` |
| Warriors | `.codex/agents/<nombre>.toml` |
| Cries | `.agents/skills/<nombre>/SKILL.md` |

En este contexto, **Codex Ahrena** significa manual de referencia, mientras **OpenAI Codex** significa la plataforma de agentes. Los Cries se convierten en skills porque los prompts personalizados son personales y las skills son el mecanismo compartible recomendado. El instalador preserva el contenido del proyecto fuera de los marcadores administrados en `AGENTS.md` y `.codex/config.toml`. Los gates humanos siguen siendo obligatorios, mientras las acciones externas (Issues, PRs, mensajes y recursos cloud) respetan los límites de autorización de OpenAI Codex.

La proyección se regenera con `python .ahrena/update.py --sync-codex` o `make sync-codex`.

## Referencias

- **`lex-platforms-rules`** — todo Lexis y Codex debe tener entrada en `cursor.rules` en `platforms.yaml` (al menos `description`); consultar al crear o publicar lex/codex
- `lex-directives` — obligación de leer `.directives`; rutas y convenciones
- `codex-pilars` — sistema de Pilares y flujo de creación
- Kata/Cry de sync-cursor (ej. `kata-make-sync-cursor`, `cry-make`) — cuándo regenerar `.cursor/`
