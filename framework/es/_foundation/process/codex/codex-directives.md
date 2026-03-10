# Codex: Manual del Archivo .directives

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Configuración canónica del framework Ahrena

## Visión general

Este Codex documenta el archivo `.ahrena/.directives`, que centraliza las configuraciones canónicas del framework. Describe el propósito de cada sección, el significado de las claves y cuándo usar cada path u opción. Es el manual de referencia que complementa la `lex-directives` (que establece la obligación de leer y aplicar el archivo). Consulte la Lex para la ley; consulte este Codex para interpretar y extender el `.directives`.

## Contexto

- **Dominio:** Configuración transversal del Ahrena (paths, idiomas, terminal, naming, tono)
- **Público objetivo:** Agentes de IA, mantenedores del framework e integradores que instalan o personalizan el Ahrena
- **Actualización:** Siempre que se añada una nueva sección al `.directives` o se altere el significado de una clave

## Contenido

### Propósito del archivo

El `.directives` es el punto único de verdad para:

- Caminos canónicos del framework (dónde están templates, artefatos, specs)
- Idioma por defecto e idiomas obligatorios para artefatos
- Tipo de terminal para comandos (bash o PowerShell)
- Convenciones de nomenclatura (prefijos, extensiones, casing, direccionamiento, clades reservados)
- Tono y estilo de escritura para artefatos y comunicación

Ningún agente debe inferir esos valores sin consultar el archivo (conforme `lex-directives`).

### Sección `paths`

| Clave | Significado | Uso |
|-------|-------------|-----|
| `paths.root` | Directorio raíz del framework en el proyecto | `.ahrena/` — punto de entrada en cualquier proyecto que adopta el Ahrena |
| `paths.directives` | Camino del archivo de directivas | `.ahrena/.directives` — siempre relativo a la raíz del repositorio |
| `paths.templates` | Directorio de templates en el repositorio del framework | `templates/` — contiene los samples (lex, codex, kata, warrior, cry) |
| `paths.framework` | Directorio del framework en el repo Ahrena | `framework/` — árbol por idioma y clade |
| `paths.project_artifacts` | Dónde crear artefatos específicos del proyecto antes de ir al framework | `.ahrena/artifacts/` — misma estructura que el framework |
| `paths.oas` | Destino de especificaciones OpenAPI | Ej.: `docs/oas` — creado por el instalador o por el agente si ausente |
| `paths.events` | Destino de documentación CloudEvents | Ej.: `docs/events` |
| `paths.samples.lexis` | Camino del template de Lexis | Ej.: `templates/lex-sample.md` |
| `paths.samples.codex` | Camino del template de Codex | Ej.: `templates/codex-sample.md` |
| `paths.samples.katas` | Camino del template de Katas | Ej.: `templates/kata-sample.md` |
| `paths.samples.warriors` | Camino del template de Warriors | Ej.: `templates/warrior-sample.md` |
| `paths.samples.cries` | Camino del template de Cries | Ej.: `templates/cry-sample.md` |

Al crear artefatos, use siempre los caminos de `paths.samples` (o el equivalente en `.directives`) para localizar el template. Para detalles sobre cuándo usar `project_artifacts` vs `framework`, consulte `codex-paths`.

### Sección `language`

| Clave | Significado | Uso |
|-------|-------------|-----|
| `language.default` | Idioma por defecto del framework | Ej.: `pt-BR` — artefatos se crean primero en este idioma; fuente de verdad |
| `language.i18n` | Lista de idiomas obligatorios | Ej.: `pt-BR`, `es`, `en` — todo artefato en el framework debe existir en todos |
| `language.cursor` | Idioma usado en los artefatos generados para Cursor (`.mdc`) | Ej.: `en` — único idioma en `.cursor/`; no hay carpetas por idioma |

Consulte `lex-framework-language` y `codex-framework-language` para la estructura de carpetas por idioma.

### Sección `terminal`

| Clave | Significado | Uso |
|-------|-------------|-----|
| `terminal` | Tipo de shell para comandos | Valores: `bash` o `powershell` — los agentes deben usar ese tipo al proponer o ejecutar comandos (ver `lex-terminal-type` y `codex-terminal-type`) |

Si está ausente, el agente infiere por el sistema operativo o pregunta al usuario.

### Sección `naming`

| Clave | Significado | Uso |
|-------|-------------|-----|
| `naming.prefixes.lexis` | Prefijo de archivos Lexis | `lex-` |
| `naming.prefixes.codex` | Prefijo de archivos Codex | `codex-` |
| `naming.prefixes.katas` | Prefijo de archivos Katas | `kata-` |
| `naming.prefixes.warriors` | Prefijo de archivos Warriors | `warrior-` |
| `naming.prefixes.cries` | Prefijo de archivos Cries | `cry-` |
| `naming.extensions.framework` | Extensión en el framework | `.md` |
| `naming.extensions.cursor` | Extensión en Cursor (rules) | `.mdc` |
| `naming.casing.files` | Convención para nombres de archivo | Ej.: `kebab-case` |
| `naming.casing.directories` | Convención para nombres de directorio | Ej.: `kebab-case` |
| `naming.addressing` | Patrón de direccionamiento de artefatos | `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}` |
| `naming.reserved_clades` | Clades con reglas especiales (prefijo `_`) | Ej.: `_foundation` |
| `naming.tone_and_writing_style` | Lista de directrices de tono y estilo | Aplicadas al producir artefatos y comunicación (ver `lex-tone` y `codex-tone`) |

Consulte `codex-naming` para detalles y ejemplos; consulte `lex-naming` para la ley que obliga al uso de estas convenciones.

### Extensibilidad

Se pueden añadir nuevas secciones al `.directives` (ej.: `security`, `notifications`). El agente debe interpretar secciones desconocidas de forma razonable. El archivo **NO DEBE** ser modificado por el agente sin solicitud explícita del usuario (`lex-directives`).

### Relación con lex-directives

- **lex-directives:** establece que todo agente DEBE leer y aplicar el `.directives` antes de producir artefatos o comunicación. Define aplicación por sección (paths, language, naming.*).
- **codex-directives:** explica qué significa cada sección y clave y cuándo usarlas. Use la Lex para la obligación; use este Codex para interpretación y referencia rápida.

## Glosario

| Término | Definición |
|---------|------------|
| Directiva | Par clave-valor (o estructura anidada) en el archivo `.directives` que rige un aspecto del comportamiento del framework |
| Camino canónico | Path definido en `paths` que todos los agentes deben usar al referenciar o crear artefatos |
| Fuente de verdad | El idioma definido en `language.default`; las versiones en otros idiomas deben ser equivalentes a él |

## Referencias

- `lex-directives` — Ley de consulta obligatoria al `.directives`
- `codex-paths` — Manual de los caminos canónicos (paths.*)
- `codex-naming` — Manual de convenciones de nomenclatura
- `codex-tone` — Aplicación de tone_and_writing_style
- `.ahrena/.directives` — Archivo canónico (ubicación en `paths.directives`)
