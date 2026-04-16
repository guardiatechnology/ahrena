# Kata: Preparar Pull Request

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 7 del flujo Issue-Driven — creación de branch, push de archivos y apertura de PR en GitHub vía MCP, con body estructurado referenciando todos los artefactos del flujo

## Objetivo

Tras que el Gate 2 resulte en `go`, crear la branch, hacer push de los archivos modificados y abrir un Pull Request en GitHub vía MCP. El body del PR está estructurado referenciando la issue original, los ACs numerados, los ADRs creados y los artefactos del flujo en `docs/issues/issue-{n}/`. El resultado es un PR listo para revisión humana, con trazabilidad completa.

## Cuándo Usar

- Fase 7 (última) del flujo orquestado por `warrior-athena`, tras que `kata-quality-gate` resulte en `go`
- Cuando es necesario someter una implementación validada para revisión vía PR

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Número de la issue | Sí | Número de la issue original (ej.: `42`) |
| Repositorio | Sí | `owner/repo` |
| Base branch | No | Branch objetivo del PR; por defecto: `main` |
| Artefactos del flujo | Sí | `docs/issues/issue-{n}/*` y `docs/adr/ADR-*` creados en fases anteriores |
| Estrategia del PR | No | `draft` (por defecto: `false`) |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y Gate 2
- [ ] 2. Determinar nombre de branch y título del PR
- [ ] 3. Crear branch vía GitHub MCP
- [ ] 4. Push de los archivos modificados
- [ ] 5. Componer body del PR con referencias
- [ ] 6. Crear PR vinculado a la issue
- [ ] 7. Actualizar status de los ADRs (proposed → accepted)
- [ ] 8. Actualizar checkpoint final
```

### Paso 1: Verificar precondiciones MCP y Gate 2

1. Confirmar que `github` está en `mcp.servers` (según `lex-mcp`). Si no, informar y detener.
2. Confirmar que `GITHUB_PAT` está definida.
3. Leer `docs/issues/issue-{n}/06-quality-report.md` y confirmar resultado `go`. Si `no-go`, rehusar crear PR y regresar al orquestador.
4. Consultar `codex-mcp-github` para identificar herramientas correctas (`create_branch`, `push_files`, `create_pull_request`).

### Paso 2: Determinar nombre de branch y título del PR

**Nombre de branch** — convención:

```
{tipo}/issue-{n}-{slug-corto}
```

Donde:
- `{tipo}` — extraer del brief de la Fase 1 (sección "Tipo de trabajo"): `feat`, `fix`, `refactor`, `chore`
- `{slug-corto}` — del título de la issue, convertido a kebab-case, limitado a ~40 chars

**Ejemplo:** `feat/issue-42-add-refund-endpoint`

**Título del PR** — en formato Conventional Commits:

```
{tipo}({alcance}): {descripción} (#{n})
```

Donde:
- `{alcance}` — módulo principal afectado (detectado vía componentes de la Fase 3)
- `{descripción}` — resumen corto del cambio

**Ejemplo:** `feat(refunds): add refund creation endpoint (#42)`

### Paso 3: Crear branch vía GitHub MCP

1. Invocar `create_branch` con:
   - `owner`, `repo`
   - `branch` — nombre generado en el Paso 2
   - `from_branch` — base branch (`main` o el configurado)
2. Si la branch ya existe (de iteración anterior), saltar este paso.

### Paso 4: Push de los archivos modificados

1. Ejecutar `git diff --name-only {base}...HEAD` para listar archivos tocados.
2. Para cada archivo, leer contenido del working tree.
3. Invocar `push_files` con:
   - `owner`, `repo`, `branch` (creada en el Paso 3)
   - `message` — mensaje de commit en formato Conventional Commits:
     ```
     {tipo}({alcance}): {descripción}
     
     Refs: #{n}
     ```
   - `files` — array de `{path, content}`
4. Si hay múltiples commits lógicos (recomendado para PRs grandes), invocar `push_files` múltiples veces con mensajes distintos.

### Paso 5: Componer body del PR con referencias

Estructura:

```markdown
## Resumen

{1-2 párrafos describiendo el cambio, extraídos del brief y requirements}

Resolves #{n}

## Criterios de Aceptación

<!-- Copiados de docs/issues/issue-{n}/02-requirements.md -->

- [x] **AC-1:** {descripción}
- [x] **AC-2:** {descripción}
- [x] **AC-3:** {descripción}

## Arquitectura

Ver [documento de arquitectura](docs/issues/issue-{n}/03-architecture.md).

### ADRs creados

- [ADR-{n}: {título}](docs/adr/ADR-{n}-{slug}.md)

(omitir si no hubo ADR)

## Calidad

- ✅ Gate 2 aprobado ([informe](docs/issues/issue-{n}/06-quality-report.md))
- ✅ Revisión de seguridad aprobada ([informe](docs/issues/issue-{n}/05-security-review.md))
- Cobertura: {actual}% (threshold: {threshold}%)

## Cómo probar

{Instrucciones extraídas del architecture-brief — cómo ejecutar, variables necesarias, escenarios clave}

## Checklist de revisión

- [ ] ACs atendidos (verificar matriz de trazabilidad en el informe del Gate 2)
- [ ] ADRs revisados (si aplica)
- [ ] Las pruebas ejecutan localmente
- [ ] Documentación de uso actualizada (si aplica)

---

🤖 Generado por el flujo Issue-Driven Development de Ahrena (`warrior-athena`)
```

### Paso 6: Crear PR vinculado a la issue

1. Invocar `create_pull_request` con:
   - `owner`, `repo`
   - `title` — del Paso 2
   - `head` — nombre de la branch
   - `base` — branch objetivo
   - `body` — del Paso 5
   - `draft` — según input (por defecto `false`)
2. Capturar `html_url` del PR creado.
3. Si `Resolves #{n}` está en el body, GitHub vinculará automáticamente la issue.

### Paso 7: Actualizar status de los ADRs (proposed → accepted)

Para cada ADR creado en la Fase 3 (listados en el checkpoint):

1. Leer `docs/adr/ADR-{n}-{slug}.md`.
2. Cambiar `**Status:** proposed` a `**Status:** accepted`.
3. El ADR fue aprobado en el Gate 1 y sobrevivió al Gate 2 — ahora es oficial.
4. Incluir esos archivos modificados en el push (o hacer un commit adicional si ya se hizo push).

### Paso 8: Actualizar checkpoint final

1. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase completada: 7
   - status final: `completed`
   - URL del PR creado
   - branch creada
   - ADRs transicionados a `accepted`
2. Informar a `warrior-athena` (y al humano):
   - PR creado en `{URL}`
   - Siguiente paso humano: revisar y aprobar

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Branch | Git branch | GitHub (vía `create_branch` MCP) |
| Commits | Git commits con mensajes Conventional | GitHub (vía `push_files` MCP) |
| Pull Request | PR con body estructurado | GitHub (vía `create_pull_request` MCP) |
| URL del PR | String | Retorno al orquestador |
| ADRs transicionados | Markdown actualizado | `docs/adr/ADR-*` con `Status: accepted` |
| Checkpoint final | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restricciones

- **Usar solo MCP:** no usar `git push` directo ni `gh pr create` cuando el MCP GitHub está activo (según `lex-mcp`).
- **Sin credenciales hardcodeadas:** autenticación exclusivamente vía `GITHUB_PAT`.
- **Gate 2 `go` es prerequisito inviolable:** no abrir PR si `06-quality-report.md` resultó `no-go`.
- **El body del PR debe referenciar docs/issues/issue-{n}/:** la trazabilidad desde la issue hasta el PR exige esos enlaces.
- **Conventional Commits obligatorio:** título del PR y mensajes de commit deben seguir el formato (según `lex-conventional-commits`).

## Referencias

- `lex-issue-driven` — leyes del flujo
- `codex-issue-workflow` — posición de esta kata
- `kata-mcp-github-read` — patrón análogo de uso de GitHub MCP
- `codex-mcp-github` — herramientas y parámetros
- `lex-conventional-commits` — formato de commits y título del PR
- `codex-contributing` — flujo de contribución del proyecto
