# Kata: Push al Framework

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Incorporación de artefactos de proyecto al framework

## Objetivo

Este Kata define el procedimiento para incorporar al framework canónico los artefactos creados en el espacio del proyecto (`.ahrena/artifacts/`). Soporta dos modos: **local** (copia a `framework/` en el repo actual, con i18n) y **remoto** (sincronización con el repositorio del framework en GitHub mediante MCP de GitHub). Opcionalmente elimina las copias del proyecto tras la incorporación.

## Cuándo Usar

- Cuando los artefactos en `.ahrena/artifacts/` han sido validados y están listos para formar parte del framework
- Cuando el usuario solicita explícitamente incorporar artefactos del proyecto al framework
- Cuando se invoca mediante `cry-push-to-framework`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Modo | Sí* | `local` o `remote`. Local: destino = `paths.framework` en el repo actual. Remote: destino = repositorio del framework en GitHub (PR/push vía MCP de GitHub). *Por defecto puede ser `local` si `paths.framework` existe en el repo. |
| Objetivo | No | Ruta(s) relativa(s) en `paths.project_artifacts` (ej: `pt-BR/engineering/quality/lexis/lex-foo.md`) o "todos". Si se omite, el agente lista los artefactos existentes y pregunta o procesa todos |
| Eliminar del proyecto | No | Si "sí", elimina los archivos de `.ahrena/artifacts/` tras copiar al framework (local) o tras envío correcto (remote). Por defecto: "no" |

## Workflow

```
Progreso:
- [ ] 1. Lectura de directivas
- [ ] 2. Identificación de artefactos a incorporar
- [ ] 3. Copia al framework e i18n
- [ ] 4. Eliminación opcional del proyecto
- [ ] 5. Validación final
```

### Paso 1: Lectura de Directivas

1. Leer `.ahrena/.directives` para obtener:
   - `paths.project_artifacts` — raíz de los artefactos de proyecto (ej: `.ahrena/artifacts/`)
   - `paths.framework` — raíz del framework (ej: `framework/`)
   - `language.default` — idioma por defecto
   - `language.i18n` — idiomas obligatorios
   - En modo **remote:** `paths.framework_repo` o `repo.framework` (URL o slug del repositorio del framework en GitHub), si existe
2. Confirmar que el directorio `paths.project_artifacts` existe; si no existe, informar que no hay artefactos para incorporar y finalizar

### Paso 2: Identificación de los Artefactos a Incorporar

1. Si se proporcionó el input **Objetivo**:
   - Si es "todos", listar recursivamente todos los archivos `.md` bajo `paths.project_artifacts`
   - Si es una o más rutas relativas, validar que cada una exista bajo `paths.project_artifacts` y añadir a la lista
2. Si no se proporcionó el input **Objetivo**:
   - Listar todos los archivos `.md` bajo `paths.project_artifacts`
   - Si no hay ninguno, informar y finalizar
   - Si los hay, procesar todos (o preguntar al usuario cuál(es) incorporar)
3. Para cada artefacto, extraer: `{lang}/{clade}/{subclade}/{pilar}/{archivo}` (la ruta relativa dentro de project_artifacts)
4. Validar que la estructura sigue el patrón de direccionamiento (lang/clade/subclade/pilar); ignorar o alertar sobre archivos que no lo cumplan

### Paso 3: Copia al Framework e i18n (modo local) o Envío al remoto (modo remote)

**Si --local:**

Para cada artefacto de la lista:

1. Ruta de origen: `{paths.project_artifacts}/{lang}/{clade}/{subclade}/{pilar}/{archivo}`
2. Ruta de destino en el framework: `{paths.framework}/{lang}/{clade}/{subclade}/{pilar}/{archivo}`
3. Crear los directorios de destino en el framework si no existen
4. Copiar el archivo del proyecto al framework (sobrescribir si ya existe)
5. Verificar idiomas: para cada idioma en `language.i18n` que aún no tenga el archivo en el framework:
   - Si existe en el proyecto en otro idioma, copiar
   - Si no existe, ejecutar `kata-translate` a partir del archivo en el idioma por defecto y guardar en `framework/{lang}/...`
6. Registrar qué archivos se copiaron y qué traducciones se crearon

**Si --remote:**

1. No escribir en `paths.framework` en disco local.
2. Preparar el conjunto de archivos a incorporar en el mismo layout que en `framework/{lang}/{clade}/{subclade}/{pilar}/` (incluyendo traducciones faltantes vía `kata-translate` en memoria o en área temporal).
3. **Obligatorio:** ejecutar el flujo de sincronización con el repositorio del framework **usando exclusivamente el MCP de GitHub**. El agente **DEBE** usar las herramientas MCP de GitHub disponibles (ej.: servidor `project-0-ahrena-github` o equivalente) para: crear branch para los cambios, aplicar los archivos preparados (commit), push, abrir PR. Todas las operaciones en el repositorio remoto del framework deben hacerse vía MCP de GitHub.
4. Registrar archivos preparados, branch creada y enlace del PR devuelto por el MCP de GitHub.

### Paso 4: Eliminación Opcional del Proyecto

1. Si el input **Eliminar del proyecto** es "sí":
   - En modo **local:** tras la copia a `framework/`; en modo **remote:** tras envío correcto (ej.: tras apertura del PR vía MCP de GitHub).
   - Para cada artefacto procesado, eliminar el/los archivo(s) en `paths.project_artifacts` (todos los idiomas del mismo artefacto)
   - Eliminar directorios vacíos bajo `paths.project_artifacts` si aplica
2. Si es "no", dejar los archivos en el proyecto sin cambios

### Paso 5: Validación Final

- [ ] Todos los artefactos objetivo se copiaron a `framework/`
- [ ] Para cada artefacto, existen versiones en todos los idiomas de `language.i18n` en el framework
- [ ] Ningún archivo se corrompió (contenido preservado)
- [ ] Si "Eliminar del proyecto" fue sí, los archivos se eliminaron de `.ahrena/artifacts/`
- [ ] Informe entregado al usuario con lista de archivos incorporados y traducciones generadas

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Artefactos en el framework (modo local) | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| Traducciones (si faltaban, modo local) | Markdown (`.md`) | Misma ruta en cada `framework/{lang}/` |
| Modo remote | — | Informe con archivos preparados, branch, enlace del PR (devuelto por el MCP de GitHub) |
| Informe | Texto | Respuesta al usuario |

## Restricciones

- No alterar el contenido de los artefactos durante la copia o al preparar para envío (copiar tal cual, salvo al generar traducciones)
- Siempre garantizar que, tras el Push, cada artefacto exista en el framework en todos los idiomas de `language.i18n` (en el destino: local o remoto)
- En modo **remote**, **es obligatorio usar el MCP de GitHub**; no usar solo git en línea de comandos para push o apertura de PR
- Si un archivo ya existe en el framework y es más reciente o diferente, considerar sobrescribir solo si el artefacto del proyecto es explícitamente el que se desea promover

## Referencias

- `codex-pilars` — Artefactos en el proyecto (.ahrena) y flujo Push
- `kata-translate` — Procedimiento de traducción para generar idiomas faltantes
- `.ahrena/.directives` — paths.project_artifacts, paths.framework, language.i18n
