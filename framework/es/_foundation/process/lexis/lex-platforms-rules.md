# Lexis: Regla obligatoria en platforms.yaml para Lexis y Codex

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Creación de Lexis y Codex en el framework Ahrena

## Propósito

El archivo `framework/platforms.yaml` define, por plataforma (ej. Cursor), cómo se transponen y aplican los artefactos. Para la plataforma Cursor, cada Lexis y cada Codex se convierte en una **rule** (`.mdc` en `.cursor/rules/`), y la aplicación (alwaysApply, globs, description) se controla con la sección `cursor.rules`.

Sin una entrada explícita por artefacto, el sync no sabe cómo exponer la rule a Cursor (description para aplicación inteligente, alwaysApply, globs). Esta Lexis existe para garantizar que **todo Lexis y todo Codex creado en el framework tenga su entrada correspondiente en `cursor.rules`** en `framework/platforms.yaml` (o en el override `.ahrena/platforms.yaml`).

## Ley

> **Todo Lexis y todo Codex creado en el framework DEBE tener una entrada correspondiente en `cursor.rules` en `framework/platforms.yaml`. La entrada DEBE incluir al menos la clave `description`.**

## Reglas

### 1. Entrada obligatoria

Para cada artefacto Lexis o Codex (archivo `lex-*.md` o `codex-*.md` en el framework), debe existir en `cursor.rules` una clave igual al **rule key** del artefacto (ruta relativa al framework sin idioma y sin `.md`). Ej.: `_foundation/process/lexis/lex-directives`, `documentation/i18n/codex-language-ptbr`.

### 2. Clave `description` obligatoria

Cada entrada en `cursor.rules` **DEBE** contener la clave **`description`** con un texto que oriente a la plataforma (ej. Cursor) para aplicar la rule de forma inteligente. Las claves `alwaysApply` y `globs` son opcionales (por defecto: alwaysApply false; sin globs).

### 3. Momento de creación

Al crear un nuevo Lexis o Codex (vía kata-create-lexis, kata-create-codex o flujo equivalente), el agente **DEBE** añadir de inmediato la entrada en `framework/platforms.yaml` en `cursor.rules`, con al menos `description`. El sync (`python .ahrena/update.py --sync-cursor`) fallará si algún lex/codex no está listado.

### 4. Override en el proyecto

El proyecto puede definir o sobrescribir entradas en `.ahrena/platforms.yaml`. La obligación aplica a la existencia de la entrada (en el default o en el override); la fuente puede ser el framework o el proyecto.

## Referencias

- `codex-platforms` — estructura de `platforms.yaml` y rule key
- `lex-directives` — rutas y convenciones del framework
