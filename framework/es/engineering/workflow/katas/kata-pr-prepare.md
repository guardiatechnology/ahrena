# Kata: Preparar Pull Request

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 7 del flujo Issue-Driven — creación de branch, push de los archivos y apertura de PR en GitHub vía MCP, con body estructurado referenciando todos los artefactos del flujo

## Objetivo

Tras el Gate 2 resultar en `go`, crear la branch, hacer push de los archivos modificados y abrir un Pull Request en GitHub vía MCP. El body del PR es estructurado referenciando la issue original, los ACs numerados, los ADRs creados y los artefactos del flujo en `docs/issues/issue-{n}/`. El resultado es un PR listo para revisión humana, con trazabilidad completa.

## Cuándo Usar

- Fase 7 (última) del flujo orquestado por `warrior-athena`, tras `kata-quality-gate` resultar en `go`
- Cuando es necesario someter una implementación validada a revisión vía PR

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| Número de la issue | Sí | Número de la issue original (ej.: `42`) |
| Repositorio | Sí | `owner/repo` |
| Base branch | No | Branch objetivo del PR; default: `main` |
| Artefactos del flujo | Sí | `docs/issues/issue-{n}/*` y `docs/adr/ADR-*` creados en las fases anteriores |
| Estrategia del PR | No | `draft` (default: `false`) |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones MCP y Gate 2
- [ ] 2. Determinar nombre de la branch y título del PR
- [ ] 3. Crear branch vía GitHub MCP
- [ ] 4. Push de los archivos modificados
- [ ] 5. Componer body del PR con referencias
- [ ] 6. Crear PR linkado a la issue
- [ ] 7. Actualizar status de los ADRs (proposed → accepted)
- [ ] 8. Actualizar checkpoint final
```

### Paso 1: Verificar precondiciones MCP y Gate 2

1. Confirmar que `github` está en `mcp.servers` (conforme a `lex-mcp`). Si no, informar y cerrar.
2. Confirmar `GITHUB_PAT` definida.
3. Leer `docs/issues/issue-{n}/06-quality-report.md` y confirmar resultado `go`. Si `no-go`, rechazar crear PR y retornar al orquestador.
4. Consultar `codex-mcp-github` para identificar herramientas correctas (`create_branch`, `push_files`, `create_pull_request`).

### Paso 2: Determinar nombre de la branch y título del PR

**Nombre de la branch** — convención:

```
{tipo}/issue-{n}-{slug-corto}
```

Donde:
- `{tipo}` — extraer del brief de la Fase 1 (sección "Tipo de trabajo"): `feat`, `fix`, `refactor`, `chore`
- `{slug-corto}` — del título de la issue, convertido a kebab-case, limitado a ~40 chars

**Ejemplo:** `feat/issue-42-add-refund-endpoint`

**Título del PR** — en el formato de Conventional Commits:

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
2. Para cada archivo, leer el contenido del working tree.
3. Invocar `push_files` con:
   - `owner`, `repo`, `branch` (creada en el Paso 3)
   - `message` — mensaje de commit en el formato Conventional Commits:
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

- ✅ Gate 2 aprobado ([reporte](docs/issues/issue-{n}/06-quality-report.md))
- ✅ Revisión de seguridad aprobada ([reporte](docs/issues/issue-{n}/05-security-review.md))
- Cobertura: {actual}% (threshold: {threshold}%)

## Cómo probar

{Instrucciones extraídas del architecture-brief — cómo correr, variables necesarias, escenarios clave}

## Checklist de revisión

- [ ] ACs atendidos (verificar matriz de trazabilidad en el reporte del Gate 2)
- [ ] ADRs revisados (si es aplicable)
- [ ] Las pruebas se ejecutan localmente
- [ ] Documentación de uso actualizada (si es aplicable)

## Session Trace

<!-- Construido por el Paso 5b a partir de .ahrena/workflow/sessions/*.json
     filtrados por branch == {branch}. Obligatorio cuando session_tracking.enabled
     == true y la branch tiene heartbeat files. Los PRs human-driven pueden usar la frase
     "_(human-driven; no session trace)_". Per lex-pr-quality y codex-session-tracking. -->

| Session | Entrypoint | Role | Started | Last Heartbeat |
|---|---|---|---|---|
| `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |

- Plan(s): plan-{NNN}
- Worktree: `.worktrees/{N}-{slug}`
- Cumulative active time: ~Xh Ymin

---

🤖 Generado por el flujo Issue-Driven Development de Ahrena (`warrior-athena`)
```

### Paso 5b: Construir la sección "Session Trace"

Per `lex-pr-quality` (reglas 9, j) y `codex-session-tracking` §7, antes de invocar `create_pull_request` agregar todos los heartbeat files de la branch actual:

1. Verificar `session_tracking.enabled` en `.ahrena/.directives` (default `true`). Si `false`, saltar este paso.
2. Resolver `session_tracking.heartbeat_dir` (default `.ahrena/workflow/sessions/`).
3. Listar `*.json` en el directorio; filtrar por aquellos cuyo `branch` coincide con la branch actual (`git rev-parse --abbrev-ref HEAD`).
4. Ordenar por `started_at` ascendente.
5. Calcular `cumulative_active_time` = suma de `(last_heartbeat - started_at)` por sesión. Formatear como `~Xh Ymin`.
6. Construir tabla con columnas `Session` (UUID corto — primeros 8 chars), `Entrypoint`, `Role`, `Started`, `Last Heartbeat`.
7. Insertar la sección en el body del PR antes del bloque "🤖 Generado...".
8. **PR sin heartbeats asociados** (humano puro, sin agente Claude Code corriendo): sustituir la tabla por la frase canónica `_(human-driven; no session trace)_`.

Esta sección es métrica complementaria al `cry-pr-cost-stamp` (que mide tokens/USD). Aquí mide tiempo de sesión real.

### Paso 5c: Flush del plan (per ADR-002)

Antes de invocar `create_pull_request`, garantizar que el body de la Issue refleja el estado actual del trabajo:

1. Invocar `kata-flush-plan-to-issue` pasando el número de la Issue.
2. El kata lee `.plans/{N}.md`, filtra bloques `<!-- not-flushed -->`, ejecuta preflight de drift remoto, y graba el contenido filtrado en el body de la Issue vía MCP `update_issue` (preferido) o `gh issue edit --body-file` (fallback).
3. En caso de drift remoto detectado (default `force=false`), el kata pausa y ofrece merge manual — no proseguir hasta resolución.

Ese paso sustituye la mecánica antigua de "actualizar `status:` en el front-matter del plan" (modelo legado pre-ADR-002): en el Issue-as-plan model, el body de la Issue es el canonical; el caché local `.plans/{N}.md` es regenerable.

### Paso 6: Crear PR linkado a la issue

1. Invocar `create_pull_request` con:
   - `owner`, `repo`
   - `title` — del Paso 2
   - `head` — nombre de la branch
   - `base` — branch objetivo
   - `body` — del Paso 5
   - `draft` — conforme al input (default `false`)
2. Capturar `html_url` del PR creado.
3. Si `Resolves #{n}` está en el body, GitHub linkará automáticamente la issue.

### Paso 6b: Aplicar `status: to review` (transición `development → to review`)

Per `lex-issue-status` Eje A y `lex-agent-planning` Tabla A, al abrir el PR Athena ejecuta la transición `development → to review`:

```bash
# 1. PR — entra en "to review" inmediatamente
gh pr edit {pr_number} --add-label "status: to review"

# 2. Issue — sincronizar (mutex intra-artefacto)
gh issue edit {issue_number} \
  --remove-label "status: development" \
  --add-label "status: to review"
```

Per `lex-issue-status` Regla 3 (mutex intra-artefacto), garantizar que cada artefacto queda con exactamente un `status:*`. Per Regla 5 (sync Issue↔PR), actualizar simultáneamente.

La label es la única fuente de verdad del estado per ADR-002 — el body de la Issue (canonical del plan) ya fue actualizado en el Paso 5c.

### Paso 7: Actualizar status de los ADRs (proposed → accepted)

Para cada ADR creado en la Fase 3 (listados en el checkpoint):

1. Leer `docs/adr/ADR-{n}-{slug}.md`.
2. Alterar `**Status:** proposed` a `**Status:** accepted`.
3. El ADR fue aprobado en el Gate 1 y sobrevivió al Gate 2 — ahora es oficial.
4. Incluir esos archivos modificados en el push (o hacer un commit adicional si ya se hizo push).

### Paso 8: Actualizar checkpoint final

1. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase concluida: 7
   - status final: `completed`
   - URL del PR creado
   - branch creada
   - ADRs transicionados a `accepted`
2. Informar al `warrior-athena` (y al humano):
   - PR creado en `{URL}`
   - Próximo paso humano: revisar y aprobar

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Branch | Git branch | GitHub (vía `create_branch` MCP) |
| Commits | Git commits con mensajes Conventional | GitHub (vía `push_files` MCP) |
| Pull Request | PR con body estructurado | GitHub (vía `create_pull_request` MCP) |
| URL del PR | String | Retorno al orquestador |
| ADRs transicionados | Markdown actualizado | `docs/adr/ADR-*` con `Status: accepted` |
| Checkpoint final | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restricciones

- **Usar únicamente MCP:** no usar `git push` directo ni `gh pr create` cuando el MCP GitHub está activo (conforme a `lex-mcp`).
- **Sin credenciales hardcoded:** autenticación exclusivamente vía `GITHUB_PAT`.
- **Gate 2 `go` es prerrequisito inviolable:** no abrir PR si `06-quality-report.md` resultó `no-go`.
- **El body del PR debe referenciar docs/issues/issue-{n}/:** la trazabilidad desde la issue hasta el PR exige esos links.
- **Conventional Commits obligatorio:** título del PR y mensajes de commit deben seguir el formato (conforme a `lex-conventional-commits`).

## Referencias

- `lex-issue-driven` — leyes del flujo
- `codex-issue-workflow` — posición de este kata
- `kata-mcp-github-read` — patrón análogo de uso de GitHub MCP
- `codex-mcp-github` — herramientas y parámetros
- `lex-conventional-commits` — formato de commits y título del PR
- `codex-contributing` — flujo de contribución del proyecto
