# Lexis: Convenciones de Nomenclatura Obligatorias

> **Prefijo:** conforme `naming.prefixes.lexis` en `.ahrena/.directives` | **Tipo:** Ley Inquebrantable | **Alcance:** Nomenclatura y direccionamiento de artefatos del framework Ahrena

## Propósito

El Ahrena define convenciones de nomenclatura en el archivo `.ahrena/.directives` (sección `naming`): prefijos por Pilar, extensiones por contexto, casing para archivos y directorios, patrón de direccionamiento y clades reservados. Sin una Ley que obligue al uso de esas convenciones, los artefatos pueden crearse con prefijos erróneos, casing inconsistente o fuera de la taxonomía, rompiendo la navegabilidad y la gobernanza del framework.

Esta Lexis consolida la obligación de seguir **naming.prefixes**, **naming.extensions**, **naming.casing**, **naming.addressing** y **naming.reserved_clades** definidos en `.ahrena/.directives`. La consulta al archivo está establecida por la `lex-directives`; esta Lexis explicita que todo artefato **DEBE** conformar a las convenciones de nomenclatura.

## Ley

> **Todo artefato del framework Ahrena DEBE seguir las convenciones de nomenclatura definidas en la sección `naming` de `.ahrena/.directives`: prefijo obligatorio del Pilar (`naming.prefixes`), extensión conforme al contexto (`naming.extensions`), casing para archivos y directorios (`naming.casing`), patrón de direccionamiento (`naming.addressing`) y respeto a los clades reservados (`naming.reserved_clades`).**

## Reglas

### 1. Prefijos

Todo artefato DEBE usar el prefijo de su Pilar conforme `naming.prefixes` en `.ahrena/.directives`. Los prefijos los define el usuario o el proyecto; las claves son `lexis`, `codex`, `katas`, `warriors`, `cries`. El agente identifica el tipo del artefato (Lexis, Codex, Kata, etc.) observando qué prefijo configurado usa el nombre del archivo — no debe asumir valores fijos.

Ejemplo: si `naming.prefixes.lexis` es `lex-`, el archivo de Ley debe nombrarse `lex-{nombre}.md`; si el proyecto define otro valor (ej. `lei-`), ese valor es el obligatorio. Nunca usar prefijo de otro Pilar ni omitir el prefijo.

### 2. Extensiones

- En el framework (árbol `framework/`): usar `naming.extensions.framework` (en general `.md`).
- En Cursor (rules): usar `naming.extensions.cursor` (en general `.mdc`).

### 3. Casing

- Archivos: seguir `naming.casing.files` (en general kebab-case). Ejemplo: `lex-no-secrets.md`.
- Directorios: seguir `naming.casing.directories` (en general kebab-case). Ejemplo: `engineering/backend/`.

### 4. Direccionamiento

Todo artefato en el framework DEBE posicionarse conforme `naming.addressing`. El patrón canónico es:

`{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`

El idioma es el primer nivel de navegación (`lex-framework-language`). Ningún artefato puede quedar fuera de esa estructura (ej.: en la raíz de `framework/` sin idioma/clade/subclade/pilar).

### 5. Clades reservados

Los valores en `naming.reserved_clades` (ej.: `_foundation`) son clades especiales. El agente DEBE reconocerlos y respetar sus reglas (ej.: prefijo `_` para clades transversales). No crear clades con nombres que conflijan con los reservados.

### 6. Fuente de verdad

Las claves y valores exactos (prefijos, extensiones, casing) están definidos en `.ahrena/.directives`. En ausencia del archivo, el agente DEBE alertar al usuario. No inferir convenciones sin consultar el archivo (`lex-directives`).

## Alcance

- **Se aplica a:** todo artefato creado o mantenido en el framework Ahrena y en el espacio de proyecto (`.ahrena/artifacts/`) cuando la estructura refleja la del framework.
- **Agentes vinculados:** todos los Warriors y agentes genéricos que crean o nombran artefatos.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de violación

1. **Artefato no conforme:** artefato con nombre o posición fuera de las convenciones no debe ser aceptado; debe ser renombrado o movido.
2. **Navegación rota:** artefatos fuera del direccionamiento canónico rompen la taxonomía y la generación correcta del `.cursor/`.
3. **Remediación:** el agente debe consultar `.directives` y `codex-naming`, corregir el nombre y el camino del artefato.

## Ejemplos

### Correcto

- `framework/pt-BR/_foundation/authoring/lexis/lex-pilars.md` — idioma, clade, subclade, pilar, prefijo y kebab-case.
- `framework/pt-BR/engineering/platform/codex/codex-restful-apis.md` — convenciones respetadas.

### Incorrecto

- `framework/lexis/lex-pilars.md` — falta idioma y clade/subclade.
- `framework/pt-BR/_foundation/authoring/lexis/pilars.md` — falta el prefijo del Pilar Lexis (consultar `naming.prefixes.lexis` en `.directives`).
- `framework/pt-BR/_foundation/Authoring/lexis/lex-pilars.md` — directorio no está en kebab-case.

## Validación automatizada

- **Herramienta:** verificación por el agente al crear o revisar artefato; posible extensión con script de validación.
- **Momento:** en la creación (kata-create-*), en la revisión de PR y en el push al framework.
- **Métrica:** 0 artefatos con prefijo incorrecto, casing incorrecto o fuera del direccionamiento canónico.

## Referencias

- `lex-directives` — Consulta obligatoria al `.ahrena/.directives`
- `codex-naming` — Manual de convenciones de nomenclatura y ejemplos
- `codex-directives` — Significado de la sección naming en el .directives
- `lex-framework-language` — Idioma como primer nivel y estructura de carpetas
