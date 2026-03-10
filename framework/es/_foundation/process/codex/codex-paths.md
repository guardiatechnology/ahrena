# Codex: Caminos Canónicos del Framework

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Uso de paths en el framework Ahrena

## Visión general

Este Codex describe los caminos canónicos definidos en la sección `paths` del `.ahrena/.directives`. Explica cuándo usar cada path, cuándo crear artefatos en `project_artifacts` en vez de en el framework, y cómo los scripts de instalación y actualización usan esos caminos. Consulte `lex-directives` para la obligación de usar caminos canónicos; consulte `codex-directives` para el significado de cada clave del `.directives`.

## Contexto

- **Dominio:** Paths del framework y flujo proyecto vs framework
- **Público objetivo:** Agentes de IA que crean o referencian artefatos; mantenedores e integradores
- **Actualización:** Cuando se añadan nuevos paths al `.directives` o cambie el flujo proyecto/framework

## Contenido

### Paths principales

| Path | Dónde existe | Uso |
|------|--------------|-----|
| `paths.root` | En todo proyecto que adopta Ahrena | Raíz del framework en el proyecto — `.ahrena/`. Scripts (install, update, uninstall) y Makefile se copian o referencian desde aquí. |
| `paths.directives` | Dentro de `paths.root` | Archivo `.ahrena/.directives`. Fuente de verdad para paths, language, terminal, naming. |
| `paths.templates` | En el repositorio del Ahrena (repo fuente) | Carpeta `templates/` con lex-sample.md, codex-sample.md, etc. Usada por el instalador y por agentes al crear artefatos (vía `paths.samples.*`). |
| `paths.framework` | En el repositorio del Ahrena | Carpeta `framework/` con el árbol por idioma (pt-BR, es, en) y por clade/subclade/pilar. En proyecto consumidor, puede ser una copia en `.ahrena/framework/` tras instalación. |
| `paths.project_artifacts` | En el proyecto que adopta Ahrena | `.ahrena/artifacts/`. Artefatos creados aquí son específicos del proyecto y pueden ser validados antes de incorporarse al framework. |

### Paths de destino (especificaciones y documentación)

| Path | Uso |
|------|-----|
| `paths.oas` | Directorio donde colocar especificaciones OpenAPI y documento de API (ej.: `docs/oas`). Creado por el agente o por el instalador si no existe. Katas y Warriors de diseño de API escriben aquí. |
| `paths.events` | Directorio donde colocar documentación de eventos (CloudEvents) (ej.: `docs/events`). Creado por el agente o por el instalador si no existe. |

### Paths de los templates (samples)

| Path | Contenido |
|------|-----------|
| `paths.samples.lexis` | Template oficial de Lexis (ej.: `templates/lex-sample.md`) |
| `paths.samples.codex` | Template oficial de Codex |
| `paths.samples.katas` | Template oficial de Katas |
| `paths.samples.warriors` | Template oficial de Warriors |
| `paths.samples.cries` | Template oficial de Cries |

Al crear un nuevo artefato, el agente debe cargar el template correspondiente desde el path definido en `.directives` (o del valor por defecto documentado en `codex-directives`). En general los paths son relativos al repositorio del framework (ej.: `templates/lex-sample.md`).

### Cuándo usar project_artifacts vs framework

| Situación | Dónde crear | Justificación |
|-----------|-------------|---------------|
| Artefato en validación; puede no ir nunca al framework | `paths.project_artifacts` | Iteración local sin contaminar el framework canónico |
| Artefato estable aprobado para el repositorio Ahrena | `paths.framework` (en el repo del framework) | Forma parte del árbol compartido; debe existir en todos los idiomas de `language.i18n` |
| Contribuidor trabajando en el repo Ahrena | Directamente en `framework/` en el repo | No usa `project_artifacts`; edita el árbol canónico |
| Consumidor que quiere proponer artefato al framework | Crear en `project_artifacts`, después usar `kata-push-to-framework` | Flujo recomendado en `codex-pilars` |

### Uso por los scripts

- **install.py / update.py:** leen `paths` (implícito al leer `.directives`) para saber dónde copiar framework, templates y dónde generar `.cursor/` cuando se usa `--platform cursor`.
- **kata-push-to-framework:** copia de `paths.project_artifacts` a `paths.framework` (modo local) o envía cambios al repositorio remoto del framework (modo remoto).

## Glosario

| Término | Definición |
|---------|------------|
| Camino canónico | Path definido en `.ahrena/.directives` bajo la sección `paths`; todos los agentes deben usarlo al referenciar o crear artefatos |
| Proyecto consumidor | Repositorio que instaló el Ahrena (vía install.py o Makefile) y que puede tener `.ahrena/framework/` y `.ahrena/artifacts/` |
| Repo del framework | Repositorio que contiene el árbol canónico `framework/` y `templates/` |

## Referencias

- `lex-directives` — Obligación de usar caminos canónicos
- `codex-directives` — Manual del archivo `.directives` (sección paths)
- `codex-pilars` — Flujo de artefatos en el proyecto y Push al framework
- `.ahrena/.directives` — Fuente de los valores de paths
