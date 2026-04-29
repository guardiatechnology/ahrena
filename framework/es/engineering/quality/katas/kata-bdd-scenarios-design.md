# Kata: Diseño de Escenarios BDD

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Calidad. Primera mitad de la Fase 8 del flujo Issue-Driven. Produce el conjunto de escenarios Gherkin de una issue, **ciego al código de implementación**.

## Objetivo

Producir `docs/issues/issue-{n}/07-bdd-scenarios.md` derivando escenarios Gherkin **exclusivamente** de las fuentes de especificación (Issue de GitHub, páginas Notion vinculadas y artefactos de las Fases 1-3 del flujo). El artefacto es validación black-box del comportamiento esperado y sirve como contrato para la etapa siguiente (`kata-bdd-validate-implementation`).

## Cuándo Usar

- Fase 8.1 del flujo orquestado por `warrior-athena`, **después** de que pase el Gate 2.
- Siempre que una funcionalidad o corrección necesite un conjunto de escenarios BDD actualizado (ej.: ACs añadidos en una nueva iteración del Gate 1).
- Bajo demanda cuando el equipo pide una validación BDD independiente sobre una funcionalidad ya implementada.

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `issue_number` | Sí | Número de la issue en GitHub (ej.: `42`) |
| `repo` | Sí | `owner/repo` (ej.: `guardiafinance/ahrena`) |
| Artefactos del flujo | Sí | `01-brief.md`, `02-requirements.md`, `03-architecture.md` en `docs/issues/issue-{n}/` |
| Páginas Notion | No | Referenciadas por la Issue o por los artefactos; recolectadas vía `kata-mcp-notion-read` |
| ADRs vinculados | No | En `docs/adr/` cuando son referenciados por la arquitectura |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones y directives
- [ ] 2. Declarar guarda de lectura (ciego al código)
- [ ] 3. Leer fuentes de especificación permitidas
- [ ] 4. Construir inventario de ACs
- [ ] 5. Derivar escenarios por AC (taxonomía)
- [ ] 6. Redactar Gherkin declarativo
- [ ] 7. Auto-lint (regex del codex-gherkin)
- [ ] 8. Componer 07-bdd-scenarios.md (frontmatter + Gherkin)
- [ ] 9. Tratar ambigüedades (comentario en la Issue)
- [ ] 10. Persistir y actualizar checkpoint
- [ ] 11. Validación final
```

### Paso 1: Verificar precondiciones y directives

1. Leer `.ahrena/.directives` per `lex-directives`.
2. Confirmar que `github` y `notion` están en `mcp.servers` per `lex-mcp`. Si `notion` no está, proseguir solo con Issue + artefactos (registrar en el frontmatter).
3. Confirmar las variables `GITHUB_PAT` y `NOTION_API_KEY` (cuando apliquen).
4. Confirmar la presencia de `docs/issues/issue-{n}/01-brief.md`, `02-requirements.md`, `03-architecture.md`. Si alguno falta, detenerse y reportar — la Fase 8 exige Fases 1-3 completas.

### Paso 2: Declarar guarda de lectura (ciego al código)

Antes de cualquier lectura, registrar internamente el conjunto de fuentes prohibidas (per `lex-bdd-spec-only-sources` Regla 2). El agente **NO** puede abrir archivos en:

```
src/, app/, lib/, pkg/, internal/, tests/, spec/, __tests__/,
cypress/, e2e/, playwright/, *.feature consumidos por runner,
cualquier extensión de código (.py, .ts, .tsx, .js, .jsx, .java, .go, .rs)
```

Si una fuente permitida (ej.: `03-architecture.md`) cita un archivo de implementación, **la ruta citada es solo referencia textual** — el agente no abre el archivo.

### Paso 3: Leer fuentes de especificación permitidas

En orden (per `codex-bdd` Sección 2):

1. `docs/issues/issue-{n}/02-requirements.md` — ACs numerados.
2. `docs/issues/issue-{n}/01-brief.md` — contexto.
3. GitHub Issue vía `kata-mcp-github-read` — título, body, comentarios relevantes.
4. Páginas Notion referenciadas vía `kata-mcp-notion-read` en modo `page` profundidad `full`.
5. `docs/issues/issue-{n}/03-architecture.md` — restricciones y contratos visibles al usuario.
6. ADRs en `docs/adr/` cuando son referenciados por `03-architecture.md`.

Para cada fuente abierta, registrar internamente la ruta/URL (será listada en el frontmatter del output).

### Paso 4: Construir inventario de ACs

1. Extraer de `02-requirements.md` cada criterio numerado `AC-{N}`.
2. Para cada AC, identificar:
   - Tipo de exigencia (positiva, negativa, con frontera numérica, con NFR).
   - Términos del dominio que aparecen (para preservar el lenguaje ubicuo per `codex-bdd` Sección 6).
   - Dependencias entre ACs (cuando aplique).
3. Mantener el inventario como tabla mental o borrador (no se persiste).

### Paso 5: Derivar escenarios por AC (taxonomía)

Aplicar la regla de cobertura mínima de `codex-bdd` Sección 4:

| Para cada AC | Al menos |
|---|---|
| Siempre | 1 `@happy-path` |
| Tiene requisito negativo explícito ("rechaza cuando", "rechaza si") | 1 `@error` |
| Tiene frontera numérica/temporal (límites, rangos, fechas) | 1 `@edge` |
| Tiene camino alternativo de éxito | 1 `@alternative` |
| Tiene NFR observable (latencia, idempotencia) | 1 `@nfr` |

Asignar id `SCN-{N}` único, contiguo dentro del archivo (regenerar la numeración si los escenarios se eliminan en la revisión).

### Paso 6: Redactar Gherkin declarativo

Para cada escenario:

1. Aplicar la estructura de `codex-gherkin` Sección 1 (subset adoptado).
2. Usar `Background` solo para precondición de negocio compartida (per `lex-bdd-gherkin-format` Regla 6).
3. Steps en tercera persona, voz activa, presente — en lenguaje del dominio (per `codex-bdd` Sección 6).
4. `Then` siempre con resultado **observable** (no "la operación ocurre").
5. Para variaciones ≥ 3 del mismo trío, usar `Scenario Outline` + `Examples`.
6. Aplicar etiquetas: ≥ 1 `@AC-{N}` + exactamente 1 etiqueta de tipo (per `lex-bdd-gherkin-format` Regla 4).

### Paso 7: Auto-lint (regex del codex-gherkin)

Antes de guardar, recorrer el contenido de los pasos contra el conjunto de regex en `codex-gherkin` Sección 12:

```
Prohibido en cualquier step:
- métodos HTTP + path
- status codes (numéricos o nombrados)
- nombres de función/método con paréntesis
- SQL (SELECT, INSERT INTO, UPDATE)
- rutas de implementación (src/, app/, etc.)
- selectores CSS/XPath
- extensiones de archivo de código

Obligatorio por escenario:
- @AC-\d+ (≥ 1)
- @(happy-path|alternative|edge|error|nfr) (exactamente 1)
- SCN-\d+ único en el archivo
```

Violación → reescribir el paso en lenguaje de negocio antes de continuar. No guardar el archivo con violación.

### Paso 8: Componer 07-bdd-scenarios.md

Estructura final del archivo:

```yaml
---
issue: {n}
repo: {owner/repo}
generated_at: "{ISO-8601}"
generated_by: warrior-themis
sources:
  github_issue: "{owner/repo}#{n}"
  notion_pages:
    - "{URL página 1}"
  flow_artifacts:
    - docs/issues/issue-{n}/01-brief.md
    - docs/issues/issue-{n}/02-requirements.md
    - docs/issues/issue-{n}/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2, SCN-3]
---
```

Bloque Gherkin debajo, con `# language: <lang>` cuando el idioma no es `en`.

Cuando hay > 3 Features o > 30 escenarios, dividir per `codex-gherkin` Sección 2 en `scenarios/*.feature` y mantener `07-bdd-scenarios.md` solo como índice + frontmatter.

### Paso 9: Tratar ambigüedades

Si una AC no permite escribir el escenario a partir de las fuentes:

1. **NO** consultar el código (per `lex-bdd-spec-only-sources` Regla 4).
2. Listar la ambigüedad en comentario en la Issue (vía `kata-mcp-github-write` si está disponible; si no, pedir al orquestador que lo haga).
3. Marcar la AC en el frontmatter como bloqueada:

```yaml
ac_coverage:
  - ac: AC-3
    scenarios: []
    status: BLOCKED
    blockers:
      - "Falta definir qué pasa cuando el cliente ya tiene una programación activa para la misma fecha"
```

4. No inventar el escenario. La Issue debe ser complementada antes de que el Gate 3 pase.

### Paso 10: Persistir y actualizar checkpoint

1. Crear `docs/issues/issue-{n}/` si no existe.
2. Guardar `07-bdd-scenarios.md` (y archivos `scenarios/*.feature` cuando aplique).
3. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md` con YAML front-matter (per `lex-issue-driven` Regla 7):
   - `phase_completed: 8.1`
   - `phase_next: 8.2`
   - artefacto bajo `artifacts.bdd_scenarios`
   - timestamp en `updated_at`

### Paso 11: Validación Final

Antes de devolver el control al orquestador, verificar:

- [ ] El frontmatter declara solo fuentes permitidas (sin rutas bajo `src/`, `tests/`, etc.).
- [ ] `ac_coverage` lista todas las ACs del `02-requirements.md` (con `scenarios` o `status: BLOCKED`).
- [ ] Cada escenario tiene id `SCN-{N}` único.
- [ ] Cada escenario tiene ≥ 1 `@AC-{N}` y exactamente 1 etiqueta de tipo.
- [ ] El auto-lint pasa en todos los escenarios.
- [ ] Los escenarios con requisito negativo tienen `@error`; los escenarios con frontera tienen `@edge`.
- [ ] El idioma del bloque Gherkin es consistente en todo el archivo.
- [ ] Checkpoint actualizado.

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Escenarios consolidados | Markdown + Gherkin | `docs/issues/issue-{n}/07-bdd-scenarios.md` |
| Escenarios por Feature (split opcional) | `.feature` | `docs/issues/issue-{n}/scenarios/*.feature` |
| Comentario en la Issue (cuando hay ambigüedad) | GitHub comment | Issue `{repo}#{n}` |
| Checkpoint actualizado | Markdown YAML | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Resumen al orquestador | Texto estructurado | Respuesta a `warrior-themis` / `warrior-athena` |

## Restricciones

- **Ciego al código:** nunca abrir archivos bajo `src/`, `app/`, `lib/`, `pkg/`, `internal/`, `tests/`, `spec/`, `cypress/`, `e2e/`, etc., ni ejecutar `grep`/`find` sobre ellos (per `lex-bdd-spec-only-sources`).
- **Sin step-runner:** el output es documentación; no crear archivos `step_definitions/`, `behave.ini`, etc. (per `lex-bdd-no-framework-coupling`).
- **Sin escenario imperativo:** nada de selectores de UI, status codes, nombres de función/tabla (per `lex-bdd-gherkin-format`).
- **Sin invención:** si la Issue no permite escribir el escenario, el agente bloquea la AC y la devuelve al origen; no consulta el código ni deduce comportamiento.
- **Lenguaje ubicuo:** cuando el escenario toca dominio core (transferencia, conciliación, asiento contable), usar los términos del modelo de dominio (`warrior-theseus`, Event Storm).

## Referencias

- `lex-bdd-spec-only-sources` — fuentes permitidas
- `lex-bdd-gherkin-format` — formato declarativo
- `lex-bdd-no-framework-coupling` — sin step-runner
- `codex-bdd` — principios y taxonomía
- `codex-gherkin` — sintaxis y patrones
- `lex-issue-driven` — flujo Issue-Driven (Fase 8)
- `kata-bdd-validate-implementation` — etapa siguiente (Fase 8.2)
- `kata-mcp-github-read`, `kata-mcp-notion-read` — lectura vía MCP
- `warrior-themis` — agente que invoca este Kata
