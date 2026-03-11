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

### Uso en el sync de Cursor

Al ejecutar `python .ahrena/update.py --sync-cursor` (o `make sync-cursor`):

1. El script carga `platforms.yaml` (default + override).
2. Usa `cursor.transposition` para decidir el destino de cada Pilar (ruta y formato).
3. Usa `cursor.rules` para construir el frontmatter de los `.mdc` (alwaysApply, globs, description). Las rules no listadas reciben el default: alwaysApply false, description derivada del cuerpo.

## Referencias

- **`lex-platforms-rules`** — todo Lexis y Codex debe tener entrada en `cursor.rules` en `platforms.yaml` (al menos `description`); consultar al crear o publicar lex/codex
- `lex-directives` — obligación de leer `.directives`; rutas y convenciones
- `codex-pilars` — sistema de Pilares y flujo de creación
- Kata/Cry de sync-cursor (ej. `kata-make-sync-cursor`, `cry-make`) — cuándo regenerar `.cursor/`
