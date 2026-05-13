# Kata: Descomponer Issue en Sub-issues Plan

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Descomposición de una Issue parent (User Story, Bug, Tech Task) en N sub-issues Plan ejecutables, conforme a `lex-agent-planning`

## Objetivo

Quebrar una Issue parent en **1..N sub-issues Plan** (Issue Type Task), cada una representando una unidad ejecutable de trabajo con body canónico (Summary + Plan section) y label `status: todo`. Procedimiento canónico de `warrior-eunomia` cuando el alcance de la Issue parent no cabe en un único PR o cuando el trabajo necesita distribuirse entre múltiples agentes/sesiones.

La descomposición **invoca `kata-plan-task` por sub-issue** — toda la lógica de creación canónica (template, labels, Issue Type, body, vinculación sub-issue) se delega al kata de creación individual. Este kata añade la capa de **estrategia de descomposición** (cómo dividir el alcance) y la capa de **orquestación** (crear N sub-issues consistentes en secuencia).

## Cuándo Usar

- Issue parent (User Story, Bug o Tech Task) cuyo alcance evidentemente no cabe en un único PR.
- Trabajo que involucra múltiples capas (ej.: backend + frontend + migración) donde cada capa es un PR independiente.
- Trabajo con **dependencias secuenciales** entre etapas donde cada etapa merece su propio audit.
- Cuando Eunomia entra en la cola de planificación de una Issue recién creada e identifica que necesita más de un Plan.
- Cuando el usuario dice "descompone la #N" o "quebra la #N en Plans".

## Inputs

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| `parent_issue_number` | Sí | Número `{N}` de la Issue parent a descomponer |
| `decomposition_strategy` | No | Estrategia explícita del usuario (ej.: "por capa", "por endpoint", "por feature flag"). Si está ausente, el agente infiere de la estructura de la Issue parent y del análisis de scope |
| `plan_drafts` | No | Lista pre-bosquejada de Plans (cada item con `summary`, `objective`, `steps`). Si está ausente, el agente bosqueja en sesión con el usuario |
| `owner/repo` | No | Repo donde vive la Issue parent. Default: repo actual del worktree |

## Workflow

```
Progreso:
- [ ] 1. Confirmar que la Issue parent existe y está bien formada
- [ ] 2. Determinar la estrategia de descomposición
- [ ] 3. Bosquejar N Plans con el usuario y confirmar la descomposición
- [ ] 4. Para cada Plan: invocar kata-plan-task
- [ ] 5. Presentar el resumen de la descomposición al usuario
```

### Paso 1: Confirmar que la Issue parent existe y está bien formada

Antes de descomponer, verificar que la Issue parent `{N}` existe y satisface `lex-issue-first` y `lex-issue-quality`:

```bash
# Preferido — vía MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)

# Fallback — vía gh
gh issue view {N} --repo {owner}/{repo} --json number,title,state,labels,body,assignees
```

Validar:

- Issue parent existe y está abierta (state `open`).
- Body contiene Why/What/How (per `lex-issue-quality`).
- Labels obligatorias del template están presentes.
- Issue Type compatible (`Feature`, `Bug` o `Task`).

Si algún criterio falla, abortar con mensaje orientando a invocar `kata-contributing-issue` para corregir la Issue parent antes de descomponer.

### Paso 2: Determinar la estrategia de descomposición

Si `decomposition_strategy` se pasó explícitamente, usarla.

Si no, **inferir** a partir del análisis del alcance de la Issue parent. Estrategias comunes:

| Estrategia | Cuándo preferir | Ejemplo de división |
|---|---|---|
| Por capa | Trabajo atraviesa el stack (backend + frontend + infra) | Plan 1: backend; Plan 2: frontend; Plan 3: migration |
| Por endpoint/feature flag | Múltiples endpoints REST o múltiples flags independientes | Plan 1: POST endpoint; Plan 2: GET endpoint; Plan 3: PATCH endpoint |
| Por fase del flujo | Trabajo tiene fases secuenciales (design → impl → docs) | Plan 1: design + ADR; Plan 2: implementación; Plan 3: documentación |
| Por bounded context | Trabajo cruza contextos en DDD | Plan 1: context A; Plan 2: context B |
| Por dependencia | Cadena de prerequisitos clara | Plan 1: spike; Plan 2: refactor de base; Plan 3: feature encima |

Presentar la estrategia al usuario y pedir confirmación antes de bosquejar los Plans.

### Paso 3: Bosquejar N Plans con el usuario y confirmar la descomposición

Si `plan_drafts` se pasó, usarlo como punto de partida.

Si no, bosquejar con el usuario. Para cada Plan, rellenar:

| Campo | Contenido |
|---|---|
| `plan_summary` | 2-4 frases — porción ejecutable del alcance de la Issue parent |
| `plan_objective` | 1-3 frases — qué entrega este Plan al final |
| `plan_steps` | Lista atómica y verificable (mínimo 1 step) |
| `plan_dependencies` | Otros Plans de esta descomposición, Issues, PRs, o `"None"` |
| `plan_risks` | Riesgos + mitigaciones, o `"None identified"` |
| `plan_open_questions` | Preguntas pendientes, o `"None"` |

Atención especial a **dependencias entre Plans de la misma descomposición**: el Plan 2 de la descomposición de la Issue #N puede depender del Plan 1; el Plan 3, de los Plans 1 y 2. Documentar explícitamente — se convertirá en `plan_dependencies` en `kata-plan-task`.

Presentar el conjunto de Plans bosquejados al usuario:

> "Esta es la descomposición de la #{N} en {len(plans)} Plans. ¿Desea ajustar la división, fusionar Plans, o separar más antes de que cree las sub-issues?"

Esperar confirmación. Incorporar ajustes. **No crear ninguna sub-issue antes de la confirmación del conjunto completo.**

### Paso 4: Para cada Plan: invocar kata-plan-task

Para cada `plan_draft` confirmado, invocar `kata-plan-task` pasando los campos rellenados:

```python
for draft in plan_drafts:
    result = invoke("kata-plan-task",
        parent_issue_number=N,
        plan_summary=draft.summary,
        plan_objective=draft.objective,
        plan_steps=draft.steps,
        plan_dependencies=draft.dependencies,
        plan_risks=draft.risks,
        plan_open_questions=draft.open_questions,
        owner=owner,
        repo=repo,
    )
    created_plans.append(result.subissue_number)
```

`kata-plan-task` ejecuta, por Plan, los 6 pasos canónicos: confirma la Issue parent, bosqueja (ya confirmado), crea la sub-issue, rellena el body, verifica Issue Type, aplica `status: todo`. Cada invocación es independiente — si una falla, las anteriores ya creadas permanecen (no es transaccional).

Si una invocación falla:

1. Capturar el error.
2. Reportar al usuario con la lista de Plans ya creados (`created_plans`) y el Plan que falló.
3. Ofrecer: (a) intentar de nuevo solo lo que falló, (b) pausar para investigación, (c) abortar la descomposición (los Plans ya creados permanecen como sub-issues huérfanas hasta decisión manual).

### Paso 5: Presentar el resumen de la descomposición al usuario

Después de crear todas las sub-issues, presentar:

> "Descomposición de la #{N} completa. {len(created_plans)} Plans creados:
> - #{M1} — {summary truncado del Plan 1}
> - #{M2} — {summary truncado del Plan 2}
> - ...
>
> Todos con `status: todo`. Listos para que Athena inicie `todo → development` en cada uno, en el orden de las dependencias mapeadas."

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| N sub-issues Plan | GitHub Issues (Task) | `{owner}/{repo}#{M_i}`, cada una sub-issue de `#{N}` |
| Bodies canónicos | Markdown (Summary + Plan section) | Body de cada sub-issue |
| Labels `status: todo` | GitHub label | En cada sub-issue creada |
| Issue Types `Task` | GitHub Issue Type | En cada sub-issue creada |
| Resumen de la descomposición | Mensaje al usuario con URLs | Sesión del agente |

## Ejemplo de Ejecución

### Input de Ejemplo

```
parent_issue_number: 200
decomposition_strategy: "por capa del event sourcing"
plan_drafts: (será bosquejado en sesión)
```

### Después del Paso 2 (estrategia confirmada)

Estrategia: "por capa del event sourcing" — separar aggregate write-side, projection read-side, y migración legacy.

### Después del Paso 3 (3 Plans bosquejados y confirmados)

```
Plan 1: Refactorizar Ledger aggregate a event sourcing (write-side)
Plan 2: Implementar projection read-side
Plan 3: Migration helper legacy state → events

Dependencias:
- Plan 2 depende de Plan 1
- Plan 3 depende de Plans 1 y 2
```

### Después del Paso 4 (3 sub-issues Plan creadas)

```
#201 — Refactorizar Ledger aggregate a event sourcing (write-side) [status: todo]
#202 — Implementar projection read-side [status: todo, depends on #201]
#203 — Migration helper legacy state → events [status: todo, depends on #201, #202]
```

### Resumen presentado al usuario

```
Agente: "Descomposición de la #200 completa. 3 Plans creados:
  - #201 — Refactorizar Ledger aggregate a event sourcing (write-side)
  - #202 — Implementar projection read-side
  - #203 — Migration helper legacy state → events

  Todos con `status: todo`. Listos para que Athena inicie
  `todo → development` en cada uno, en el orden: #201 → #202 → #203."
```

## Restricciones

- **Nunca descomponer sin Issue parent confirmada** — la Issue parent precede a cualquier Plan; sin Issue, no hay descomposición.
- **Nunca saltar la confirmación del conjunto completo en el Paso 3** — presentar la descomposición entera al usuario antes de crear la primera sub-issue evita medias descomposiciones inconsistentes.
- **Nunca crear branch, worktree ni aplicar assignee en este kata** — delegado a `kata-plan-task` (que tampoco los crea — pertenecen a `todo → development`).
- **Nunca descomponer una Issue parent ya descompuesta sin chequear sub-issues existentes** — antes de crear, listar sub-issues actuales (`gh api repos/{owner}/{repo}/issues/{N}/sub_issues`) y presentar al usuario; decisión manual para crear más, fusionar, o abandonar la operación.
- **Documentar dependencias entre Plans de la misma descomposición** — `plan_dependencies` debe listar explícitamente los otros Plans de esta descomposición cuando aplique; Athena usa ese orden para secuenciar `todo → development`.
- **No es transaccional** — si la 3a invocación de `kata-plan-task` falla, las 2 anteriores permanecen; la recuperación es manual.

## Referencias

- `lex-agent-planning` — modelo jerárquico Issue → Plan → PR; Gate 1 owned por Eunomia
- `lex-issue-quality` — requisitos de la Issue parent
- `lex-issue-status` — labels canónicas; `status: todo` aplicado por `kata-plan-task`
- `lex-issue-first` — Issue parent precede a la sub-issue Plan
- `lex-mcp` — preferencia MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- `kata-plan-task` — invocado por Plan; crea cada sub-issue
- `kata-contributing-issue` — creación de la Issue parent (precondition)
- `kata-load-plan-from-subissue` — materializa el caché local después de la descomposición (llamado después, por Plan)
- `warrior-eunomia` — owner top-level de este kata
