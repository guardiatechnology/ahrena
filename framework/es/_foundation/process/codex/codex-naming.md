# Codex: Convenciones de Nomenclatura del Framework

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Nomenclatura y direccionamiento de artefatos del Ahrena

## Visión general

Este Codex detalla las convenciones de nomenclatura definidas en la sección `naming` del `.ahrena/.directives`. Complementa la `lex-naming` (que establece la obligación) con ejemplos, buenas prácticas y trampas habituales. Use este Codex al crear o revisar nombres de archivos, directorios y posición de artefatos en la taxonomía.

## Contexto

- **Dominio:** Nomenclatura de artefatos y estructura de directorios del framework
- **Público objetivo:** Agentes de IA que crean o mueven artefatos; mantenedores del framework
- **Actualización:** Cuando las convenciones en el `.directives` sean alteradas o se definan nuevos clades reservados

## Contenido

### Prefijos por Pilar

El prefijo de cada Pilar es el valor definido en `naming.prefixes` en `.ahrena/.directives` (claves: `lexis`, `codex`, `katas`, `warriors`, `cries`). Quien define es el usuario o el proyecto; el agente DEBE consultar el archivo para saber el valor en uso.

| Pilar | Clave en naming.prefixes | Ejemplo de archivo (cuando se usa el valor por defecto) |
|-------|--------------------------|----------------------------------------------------------|
| Lexis | `lexis` | `lex-directives.md`, `lex-pilars.md` |
| Codex | `codex` | `codex-naming.md`, `codex-pilars.md` |
| Katas | `katas` | `kata-create-lexis.md`, `kata-translate.md` |
| Warriors | `warriors` | `warrior-translator.md`, `warrior-daedalus.md` |
| Cries | `cries` | `cry-new-lex.md`, `cry-translate.md` |

Nunca use un prefijo de otro Pilar (ej.: no nombrar un Codex como `manual-xyz.md`). El prefijo identifica el tipo del artefato; la identificación se hace por el valor configurado en `.directives`, no por valor fijo.

### Extensiones

| Contexto | Extensión | Ejemplo |
|----------|-----------|---------|
| Framework (archivos .md en el repo) | `.md` | `lex-pilars.md` |
| Cursor rules | `.mdc` | `lex-pilars.mdc` (generado a partir del .md) |
| Skills y commands en Cursor | Conforme recurso (ej.: SKILL.md, .md) | Definido por el instalador |

### Casing

| Elemento | Convención | Ejemplo correcto | Ejemplo incorrecto |
|----------|------------|------------------|---------------------|
| Nombre de archivo | kebab-case | `codex-restful-apis.md` | `codex_restful_apis.md`, `codexRestfulApis.md` |
| Nombre de directorio | kebab-case | `project_artifacts`, `_foundation` | `ProjectArtifacts`, `_Foundation` |

Nota: los clades reservados usan prefijo `_` (ej.: `_foundation`); el resto del nombre sigue kebab-case.

### Direccionamiento (taxonomía)

Patrón: `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`

| Segmento | Significado | Ejemplo |
|----------|-------------|---------|
| `lang` | Código BCP 47 del idioma | `pt-BR`, `es`, `en` |
| `clade` | Disciplina o dominio de primer nivel | `_foundation`, `engineering`, `documentation` |
| `subclade` | Área dentro del clade | `authoring`, `platform`, `i18n` |
| `pilar` | Nombre del pilar (plural en carpetas): lexis, codex, katas, warriors, cries | `lexis`, `codex`, `katas` |
| `prefix-name.ext` | Nombre del archivo con prefijo y extensión | `lex-pilars.md` |

Ejemplo completo: `pt-BR/_foundation/authoring/lexis/lex-pilars.md`

### Clades reservados

Definidos en `naming.reserved_clades`. Ej.: `_foundation`.

- Usan prefijo `_` para indicar que son transversales o especiales.
- No cree un clade con el mismo nombre sin el prefijo (ej.: no usar `foundation` como clade si `_foundation` está reservado).
- Consulte el `.directives` para la lista actual.

### Tono y estilo (naming.tone_and_writing_style)

La sección `naming.tone_and_writing_style` en el `.directives` contiene directrices de tono y estilo de escritura. Su aplicación es obligatoria por `lex-tone` y está detallada en `codex-tone`. No forma parte de la nomenclatura de archivos/directorios, pero está bajo la sección `naming` en el archivo.

### Buenas prácticas

| Práctica | Descripción |
|----------|-------------|
| Nombre descriptivo tras el prefijo | Use `lex-no-secrets` en vez de `lex-1`; el nombre debe indicar el contenido |
| Consistencia entre idiomas | El mismo artefato en pt-BR, es y en debe tener el mismo nombre de archivo (ej.: `lex-pilars.md` en todas las carpetas de idioma) |
| Evitar siglas oscuras | Prefiera `codex-restful-apis` a `codex-ra` si el contexto no es obvio |
| Subclade específico | Elija el subclade más específico que tenga sentido (ej.: `authoring` dentro de `_foundation`) |

### Trampas habituales

| Trampa | Problema | Solución |
|--------|----------|----------|
| Olvidar el prefijo | Archivo `directives.md` en el directorio lexis | Nombrar `lex-directives.md` |
| Casing erróneo | `Lex-Pilars.md` o `lex_pilars.md` | Usar kebab-case: `lex-pilars.md` |
| Artefato fuera del árbol | Archivo en la raíz de `framework/` o sin idioma | Posicionar en `{lang}/{clade}/{subclade}/{pilar}/` |
| Pilar como carpeta | El nombre de la carpeta debe ser plural (lexis, codex, katas, warriors, cries) | Usar `lexis/`, no `lex/` |

## Glosario

| Término | Definición |
|---------|------------|
| Direccionamiento | Posición completa del artefato en la taxonomía (lang/clade/subclade/pilar/archivo) |
| Clade reservado | Clade listado en `naming.reserved_clades` con reglas especiales (ej.: prefijo `_`) |
| kebab-case | Palabras en minúsculas separadas por guion (ej.: `lex-no-secrets`) |

## Referencias

- `lex-naming` — Ley que obliga al uso de las convenciones de nomenclatura
- `lex-directives` — Consulta obligatoria al `.ahrena/.directives`
- `codex-directives` — Manual del archivo .directives (sección naming)
- `lex-framework-language` — Estructura de idiomas y primer nivel de navegación
- `codex-tone` — Aplicación de tone_and_writing_style (bajo naming en el .directives)
