# Lexis: Planificación Obligatoria para Tareas de Agentes

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Toda tarea multi-etapa iniciada por cualquier agente o subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Los agentes que ejecutan sin planificación previa producen resultados parciales, dejan archivos en estados inconsistentes y obligan al usuario a reconstruir el contexto manualmente. Esta Lexis elimina ese patrón exigiendo que todo agente registre su plan antes de ejecutar, haciendo que la intención, el alcance y la secuencia sean auditables por humanos y por otros agentes. Además, define un ciclo de vida unificado entre Plan, Issue de GitHub y PR — con un propietario explícito para cada transición — para eliminar drift y dar visibilidad a la "sala de espera" de la revisión.

El modelo canónico es jerárquico: cada **Issue** (User Story, Bug o Tech Task) lleva el problema (Why/What/How/AC); de cada Issue derivan **1..N Planes**, materializados como **sub-issues de GitHub** (Issue Type Task) que encapsulan unidades ejecutables de trabajo; de cada Plan derivan **1..N PRs**. Los Planes nunca existen como archivo local canónico — el body de la sub-issue es la fuente de verdad. Los caches locales específicos del provider (`.claude/plans/`, `.cursor/plans/`) son derivados regenerables, gitignored.

## Ley

> **Todo agente DEBE registrar un plan canónico como sub-issue de GitHub (Issue Type Task) vinculada a la Issue parent ANTES de iniciar la ejecución de cualquier tarea que involucre 2 o más etapas, afecte múltiples archivos o produzca artefactos permanentes. El plan DEBE ser presentado al usuario para confirmación antes de que comience la ejecución. Iniciar ejecución multi-etapa (crear branch, hacer commit, abrir PR) sin sub-issue Plan creada y confirmada está PROHIBIDO. Esbozar un plan localmente en `.claude/plans/plan-{slug}.md` o `.cursor/plans/plan-{slug}.md` con `status: draft` en el front-matter está PERMITIDO como entry point plan-first, siempre que el agente promueva el borrador a sub-issue antes de iniciar la ejecución (transición `draft → todo` vía `kata-contributing-issue` + `kata-decompose-issue-into-plans` o `kata-plan-task`). El `status:` del plan vive como **label canónica** en la sub-issue (y en el PR, a partir de `to review`); el enum canónico es `todo | development | to review | review | to release | release | done` (más el terminal alternativo `abandoned`, y el estado local-only `draft` pre-promoción, que no existe como label de GitHub); cada transición DEBE ser ejecutada por el propietario declarado en este Lex. La transición `— → todo` aplica el gate de creación (template + labels + Issue Type + Why/What/How); la transición `todo → development` aplica el gate de inicio de ejecución (branch remota + worktree + assignee).**

## Alcance

- **Se aplica a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, cualquier AI agent o subagente que invoque katas, warriors o cries en el contexto Ahrena
- **Agentes vinculados:** todos, sin excepción de rol
- **Excepciones permitidas:** operaciones triviales de etapa única (editar un único archivo con instrucción directa, consulta de lectura pura, comando aislado sin efecto colateral permanente)

## Modelo jerárquico Issue → Plan → PR

```
Issue (User Story | Bug | Tech Task)            ← problema, Why/What/How, AC
   │
   ├─ Plan sub-issue (Task)                     ← unidad ejecutable #1
   │     ├─ status: todo | development | to review | review | done
   │     ├─ branch: {type}/{M}-{slug}
   │     └─ PR(s) que cierran este Plan
   │
   ├─ Plan sub-issue (Task)                     ← unidad ejecutable #2
   │     └─ ...
   │
   └─ Plan sub-issue (Task)                     ← unidad ejecutable #N
         └─ ...
```

| Capa | Ubicación | Rol | Versionado |
|---|---|---|---|
| **Issue (parent)** | `https://github.com/{owner}/{repo}/issues/{N}` | Lleva problema, motivación, criterios de aceptación. No tiene branch propia | GitHub audit log |
| **Plan sub-issue** | `https://github.com/{owner}/{repo}/issues/{M}`, sub-issue de #{N} | Canónico. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Lleva branch dedicada y PR(s) | GitHub audit log |
| **Cache del provider** | `.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`, gitignored | AI working memory + scratch. Superset del body de la sub-issue + bloques `<!-- not-flushed -->`. Nombrado por el número de la sub-issue | Cache local regenerable |
| **Phase artifacts** | `.ahrena/issues/issue-{N}/`, committed | `01-brief.md` … `06-quality-report.md` del flujo Issue-Driven (vinculados a la Issue parent) | Git |

El cache local es específico del provider: los agentes Claude usan `.claude/plans/plan-{M}-{slug}.md`; los agentes Cursor usan `.cursor/plans/plan-{M}-{slug}.md`. No hay cache compartido entre providers — cada uno lleva su working memory de forma independiente, regenerado desde la sub-issue vía `kata-load-plan-from-subissue`.

## Schema del body de la sub-issue Plan (canónico)

```markdown
## Summary

{2-4 frases describiendo el objetivo ejecutable de este Plan. Típicamente una rebanada del alcance de la Issue parent.}

Parent: #{N}

## Plan

### Objective
{Por qué existe esta unidad y qué entrega al finalizar — 1 a 3 frases.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{Otros Planes, Issues o PRs de los que esta tarea depende; "None" si no hay.}

### Risks
{Riesgos conocidos y mitigaciones; "None identified" si no hay.}

### Open Questions
{Preguntas abiertas que requieren decisión antes/durante la ejecución; "None" si no hay.}
```

Schema del cache local `.claude/plans/plan-{M}-{slug}.md` (o `.cursor/plans/plan-{M}-{slug}.md`): **superset** del body de la sub-issue. Lleva front-matter YAML para metadatos de sesión + el body completo espejado + secciones locales marcadas.

**Front-matter** (canónico):

```yaml
---
plan_id: "{M}"              # número de la sub-issue Plan; "draft" pre-promoción
title: "{slug}"             # slug usado en la branch (y en el nombre del archivo mientras es draft)
status: todo | development | to review | review | done | abandoned
                            # | draft (estado local-only, pre-promoción)
                            # | to release | release (eje release)
agent: claude | cursor
issue: "{owner/repo#M}"     # "TBD" mientras es draft
parent: "{owner/repo#N}"    # Issue parent (User Story | Bug | Tech Task)
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
promoted_at: "YYYY-MM-DDTHH:MM:SSZ"   # OPCIONAL — completado en la transición draft → todo
---
```

Los campos `merge_commit:` y `closed_at:` NO aparecen en el front-matter — son derivados de las APIs de GitHub en el audit post-merge (ver §Auditoría de cierre). El campo `promoted_at:` registra el timestamp UTC de la promoción plan-first (transición `draft → todo`); completar solo para planes que nacieron en `draft`.

**Body**: superset del body de la sub-issue + secciones locales marcadas con bloques `<!-- not-flushed -->`:

```markdown
<!-- not-flushed -->
## Working notes
- decisión de debugging X a las 14:32
- error Y reproducido en test-Z

## Next actions
1. probar enfoque A; si falla, B

## Scratch
cualquier texto libre que la IA quiera mantener como contexto local
<!-- /not-flushed -->
```

`kata-flush-plan-to-subissue` filtra los bloques `<!-- not-flushed -->` antes de grabar en el body de la sub-issue. El front-matter NUNCA se flushea a GitHub — vive solo en el cache local.

## Ciclo de vida del Plan

El ciclo opera sobre **dos ejes disjuntos**:

### Eje A — Dev cycle (Plan derivado de User Story / Bug / Tech Task)

```
(draft, local-only) ⇢ — → todo → development → to review → review → done
                                                       ↘
                                                       abandoned (terminal alternativo, cualquier etapa)
```

- `(draft)` — estado **local-only** pre-`todo`. Vive en el front-matter del plan-archivo (`.claude/plans/plan-{slug}.md` o `.cursor/plans/plan-{slug}.md`) con `status: draft, issue: TBD`. No existe como label canónica en GitHub. La transición `draft → todo` es la **promoción plan-first** (ver Guardrail plan-first abajo).
- `— → todo` — sub-issue Plan creada con template + labels + Issue Type + Why/What/How; sin branch, sin worktree, sin assignee aún.
- `todo → development` — Plan tomado para ejecución: branch remota creada vía `gh issue develop`; worktree per `lex-git-worktrees`; assignee aplicado (quien se compromete a ejecutar); primer commit inminente.
- `development → to review` — implementación completada; PR abierto; flush previo del cache local vía `kata-flush-plan-to-subissue`.
- `to review ↔ review` — reviewer (humano o Argos) entra y sale del ciclo de revisión activa.
- `to review → done` — PR mergeado; sub-issue Plan cerrada vía `Closes #{M}`.
- `abandoned` — terminal alternativo; Plan descartado en cualquier etapa.

### Eje B — Release cycle (Plan dedicado al release)

```
— → to release → release → done
                       ↘
                       abandoned (terminal alternativo, cualquier etapa)
```

- `— → to release` — release sub-issue creada por Janus, listando los PRs mergeados desde el último tag.
- `to release → release` — release en ejecución; humano aprobó bump/changelog.
- `release → done` — tag empujado, build de release pasó, GitHub Release publicada.
- `abandoned` — release abortado antes del tag.

La mutex de labels es **intra-artefacto** (dentro de cada Issue/PR), no cross-artifact: una sub-issue lleva exactamente una label `status: <name>` a la vez. El HARD-GATE en `lex-issue-status` prohíbe aplicar labels del Eje B en sub-issue de feature, y viceversa.

## Gate 1 — Plan creado (`— → todo`)

Propietario: `warrior-eunomia` (fallback: agente de la sesión mientras Eunomia no esté desplegada).

Toda sub-issue Plan DEBE ser creada por Eunomia vía `kata-decompose-issue-into-plans` (downstream del análisis de la Issue parent) o `kata-plan-task` (Plan independiente top-level vinculado a una Issue existente). El agente ejecuta los 4 pasos abajo antes de marcar la label `status: todo`:

1. **Confirmar que la Issue parent existe y está bien formada** (per `lex-issue-first` y `lex-issue-quality`). Sin Issue parent abierta, no hay Plan a crear — invocar `kata-contributing-issue` primero para abrir la Issue.
2. **Crear la sub-issue Plan** vinculada a la Issue parent vía MCP `create_issue` (preferido) o `gh issue create --type Task` (fallback), aplicando el template Plan, labels obligatorias e Issue Type `Task`.
3. **Completar el body de la sub-issue con el plan canónico** (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) vía MCP `update_issue` o `gh issue edit --body-file <path>` (fallback per `lex-mcp` regla 4).
4. **Verificar Issue Type pos-creación** (per `lex-issue-type-verified`) — los Planes son siempre `Task`.

Branch, worktree y assignee **NO** son precondiciones de `— → todo`. Pertenecen a `todo → development`.

<HARD-GATE>
warrior-eunomia (o el agente de la sesión actuando como fallback mientras
Eunomia no esté desplegada) MUST NOT aplicar la label `status: todo` en una
sub-issue Plan sin satisfacer TODOS los 4 pasos canónicos:

  (a) Issue parent abierta y en conformidad con lex-issue-first y
      lex-issue-quality (template, labels, Issue Type compatible,
      Why/What/How completados)
  (b) Sub-issue Plan creada vinculada a la Issue parent vía MCP create_issue
      (preferido) o gh issue create --type Task (fallback), con template
      Plan y labels obligatorias aplicadas
  (c) Body de la sub-issue completado con el plan canónico (Summary + Plan
      conteniendo Objective, Steps, Risks, Dependencies, Open Questions)
      vía MCP update_issue o gh issue edit --body-file (fallback)
  (d) Issue Type verificado como Task per lex-issue-type-verified

Esta regla se aplica a TODO Plan (top-level o subtask de descomposición),
independiente de:
  - tamaño percibido ("es solo un chore")
  - urgencia ("incendio en producción")
  - quién lo pidió ("el CEO lo solicitó")
  - confianza del equipo ("ya probamos mucho")

Excepción declarada: ninguna. Branch, worktree y assignee NO son
precondiciones de este gate — pertenecen al gate todo → development.
</HARD-GATE>

### Guardrail plan-first

Plan-first es un camino legítimo: el agente (o humano) PUEDE esbozar un plan localmente en `.claude/plans/plan-{slug}.md` o `.cursor/plans/plan-{slug}.md` llevando `status: draft` en el front-matter (e `issue: TBD` mientras no haya sub-issue correspondiente). Lo que está PROHIBIDO es iniciar la ejecución (branch, commits, PR) sin antes promover el borrador a sub-issue Plan en GitHub.

Cuando el usuario señala intención de plan sin referenciar una Issue (e.g., "vamos a planificar X"), el agente PUEDE seguir uno de dos caminos:

- **Camino A (issue-first):** invocar `kata-contributing-issue` para abrir la Issue parent inmediatamente; luego `kata-decompose-issue-into-plans` o `kata-plan-task` para crear la(s) sub-issue(s) Plan; después `kata-load-plan-from-subissue` para materializar el cache local. No hay estado `draft` en este camino.

- **Camino B (plan-first / draft):** esbozar el plan directamente en `.claude/plans/plan-{slug}.md` (o `.cursor/plans/...`) con front-matter `status: draft, issue: TBD`. Cuando el borrador madura, **promover** en un paso atómico:
  1. `kata-contributing-issue` crea la Issue parent si aún no la hay.
  2. `kata-decompose-issue-into-plans` o `kata-plan-task` crea la sub-issue Plan canónica.
  3. Renombrar el archivo de `plan-{slug}.md` a `plan-{M}-{slug}.md` (donde `{M}` es el número de la sub-issue creada).
  4. Actualizar el front-matter — `status: draft → todo`, `issue: TBD → {owner/repo#M}`, registrar `promoted_at` con timestamp UTC.
  5. Aplicar la label canónica `status: todo` en la sub-issue recién creada (Gate 1 de Eunomia).

`status: draft` es estado **puramente local** — vive en el front-matter del plan-archivo, NO existe como label canónica en GitHub. La label `status: todo` solo aparece después de la promoción. `kata-load-plan-from-subissue` retorna `PROMOTION_REQUIRED` (señal de flujo, no error fatal) cuando recibe un plan-archivo orphan con `status: draft` o `issue: TBD`, orientando al agente invocador a accionar la promoción antes de la materialización canónica.

## Gate 2 — Plan iniciado (`todo → development`)

Propietario: `warrior-athena`.

Athena toma el Plan cuando la ejecución está por comenzar (no antes). En `todo → development`, Athena ejecuta los 3 pasos canónicos:

1. **Crear la branch remota** y vincularla a la sub-issue Plan vía `gh issue develop {M} --base main --name {type}/{M}-{slug}` (registra la branch como "Development" en la sidebar de GitHub).
2. **Crear el worktree** per `lex-git-worktrees` en `.worktrees/{M}-{slug}/`.
3. **Aplicar assignee** en la sub-issue Plan (quien se compromete a ejecutar — humano o identidad de agente).

Aplicar `status: development` sin los 3 pasos completos está PROHIBIDO. Athena no inicia Phase 4 de Issue-Driven sin el gate satisfecho.

<HARD-GATE>
warrior-athena MUST NOT aplicar la label `status: development` en una
sub-issue Plan sin satisfacer TODOS los 3 pasos canónicos:

  (a) Branch remota creada y vinculada a la sub-issue Plan vía
      gh issue develop {M} --base main --name {type}/{M}-{slug}
  (b) Worktree creado per lex-git-worktrees en
      `.worktrees/{M}-{slug}/`
  (c) Assignee aplicado en la sub-issue Plan (la persona o agente que
      se compromete a ejecutar)

Esta regla se aplica a TODA transición todo → development, independiente de:
  - tamaño percibido ("es solo un chore")
  - urgencia ("incendio en producción")
  - quién lo pidió ("el CEO lo solicitó")
  - confianza del equipo ("ya probamos mucho")

Excepción declarada: ninguna. Athena no inicia ejecución sin branch,
worktree y assignee — esos tres son el amarre mínimo para audit
y para evitar trabajo fantasma fuera de una sub-issue Plan.
</HARD-GATE>

## Propietarios de cada transición

### Tabla A — Dev cycle (Eunomia / Athena / Argos)

| Transición | Propietario | Disparador |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente de la sesión) | Crea sub-issue Plan + completa body canónico + verifica Issue Type |
| `todo → development` | `warrior-athena` | Crea branch vía `gh issue develop` + worktree + assignee; inicia Phase 4 |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR; flush previo del cache vía `kata-flush-plan-to-subissue` |
| `to review → review` | `warrior-argos` | Argos inicia ciclo de revisión automatizada |
| `review → to review` | `warrior-argos` | Argos termina ciclo sin aprobar (changes-requested o awaiting-human) |
| `to review → done` | `warrior-athena` | Humano aprueba PR; merge cierra sub-issue Plan vía `Closes #{M}` |
| `cualquiera → abandoned` | creador o propietario actual | Plan descartado |

### Tabla B — Release cycle (Janus)

| Transición | Propietario | Disparador |
|---|---|---|
| `— → to release` | `warrior-janus` | Abre release sub-issue; puebla `Tracks: #N1, #N2, ...` con PRs mergeados desde el último tag |
| `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano de bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` concluye (tag empujado, validate-tag pasa, Release creada); notificación vía MCP en `notifications.channels.release_notify` |
| `cualquiera → abandoned` | `warrior-janus` | Release abortado antes del tag |

Cada propietario DEBE:

- Aplicar la label `status: <name>` correspondiente en la sub-issue Plan en GitHub (per `lex-issue-status`).
- Aplicar la label `status: <name>` correspondiente en el PR (a partir de `to review`).
- Disparar `kata-flush-plan-to-subissue` si el cache local está adelantado al body de la sub-issue.

## Auditoría de cierre

Para audit pos-merge, dos campos se derivan de las APIs nativas de GitHub (sin front-matter dedicado en el Plan):

| Campo lógico | Fuente canónica | Comando |
|---|---|---|
| `closed_at` | `Issue.closedAt` | `gh issue view {M} --json closedAt --jq .closedAt` |
| `merge_commit` | `PullRequest.mergeCommit.oid` | `gh pr view {PR} --json mergeCommit --jq .mergeCommit.oid` |

Para archivos legados en `.ahrena/issues/_legacy/` que mantienen YAML front-matter histórico, `merge_commit:` y `closed_at:` son reconocidos como front-matter opcional aceptado — preserva el audit sin retrofit.

## Cadencia de load/flush

La sincronización entre el cache local y el body de la sub-issue Plan ocurre en **4 disparadores canónicos** (no en cada toggle):

| Disparador | Operación |
|---|---|
| Inicio de sesión / handoff entre agentes | `kata-load-plan-from-subissue` |
| Transición de label `status:` en la sub-issue/PR | `kata-flush-plan-to-subissue` |
| Step del plan marcado como completado (`[ ]` → `[x]`) | `kata-flush-plan-to-subissue` |
| Fin de sesión (heartbeat termina o propietario sale) | `kata-flush-plan-to-subissue` |

Toggles intermedios, ediciones de scratch (`<!-- not-flushed -->`) y working notes son **libres** — no disparan flush. Documentación operacional en `codex-agent-planning` §9.

## Relación con otros artefactos

- **Issue parent (User Story / Bug / Tech Task):** lleva problema, motivación, AC. No tiene branch propia. Generalmente cierra vía `Closes #{N}` en el último PR de la última sub-issue Plan.
- **Sub-issue Plan:** lleva el plan canónico en el body; la label `status: <name>` es la única fuente de verdad para el estado.
- **PR:** a partir de `to review`, el PR lleva la label `status: <name>` correspondiente, actualizada por Athena/Argos/Janus a medida que el estado avanza. La sync de la label es responsabilidad del propietario de la transición.
- **`.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`:** cache local específico del provider regenerable; nunca commiteado; reconstruido por `kata-load-plan-from-subissue` en fresh clone.
- **`.ahrena/issues/issue-{N}/`:** committed; recibe Phase artifacts del flujo Issue-Driven de la Issue parent #{N} (per `lex-issue-driven`).
- **Checkpoint (`.checkpoint`):** el Plan cubre **task** (Steps, Decisiones, Riesgos en el body de la sub-issue); el checkpoint cubre **sesión** (foco de la ventana, hand-off entre Planes, threads paralelos). La superposición está PROHIBIDA — ver `lex-checkpoint` regla 5.
- **ADR:** cuando un Plan identifica una decisión arquitectónica relevante, un ADR DEBE ser abierto conforme `lex-issue-driven`. Ejemplos de nombre de archivo: `ADR-008-use-event-sourcing-for-refund-audit-trail.md`, `ADR-007-use-fastapi-routers.md`, `ADR-001-use-event-sourcing-for-ledger.md`, `ADR-002-migrate-to-fastapi.md`.
- **Heartbeat de sesión:** la sesión Claude Code que opera en el Plan es registrada en `.ahrena/workflow/sessions/<session-id>.json` (per `codex-session-tracking`); no vive en el body de la sub-issue.

### Plan vs cache local vs `.checkpoint` — qué va dónde

| Contenido | Vive en |
|---|---|
| Objective, Steps `[x]`, Risks, Dependencies, Open Questions | Body de la sub-issue Plan (canónico) |
| Decisiones arquitectónicas relevantes | ADR en `docs/adr/` (referenciado por el Plan) |
| Working notes, debugging diary, scratch | Cache local en bloques `<!-- not-flushed -->` |
| Foco general de la ventana de trabajo (Session focus) | `.checkpoint` — gitignored |
| Punteros a múltiples Planes activos (Active plans) | `.checkpoint` — gitignored |
| Threads paralelos que no se convirtieron en Plan (Open threads) | `.checkpoint` — gitignored |

En caso de duda: contenido estructural va al body de la sub-issue Plan; contenido volátil al cache local en bloque not-flushed; foco de la sesión al `.checkpoint`.

## Ejemplos

### Correcto — flujo Top-down (Issue first)

```
Usuario: "Necesitamos migrar el ledger a event sourcing — abre una User Story"
→ Agente invoca kata-contributing-issue (template user-story-for-api)
→ Issue #200 creada (Why/What/How, AC numerados, Issue Type Feature, label
  `user story 🎯`, status: todo vía Gate 1 de lex-issue-quality)

Próxima sesión, agente descompone:
→ Eunomia invoca kata-decompose-issue-into-plans 200
→ 3 sub-issues Plan creadas:
   #201 (Task) — refactorizar Ledger aggregate para event sourcing
   #202 (Task) — implementar projection write-side
   #203 (Task) — migrar lectura vía projection read-side
→ Cada sub-issue lleva Summary + Plan section
→ Eunomia aplica status: todo en las 3 sub-issues (Gate 1 OK)
→ Issue #200 permanece status: todo hasta que comience el primer PR

Ejecución del Plan #201:
→ Athena (Gate 2): gh issue develop 201 --base main --name refactor/201-ledger-event-sourcing
→ Athena crea worktree en .worktrees/201-ledger-event-sourcing/
→ Athena aplica assignee fernandoseguim en la sub-issue #201
→ Athena aplica status: development en la sub-issue #201
→ kata-load-plan-from-subissue 201 materializa .claude/plans/plan-201.md
→ La implementación corre; kata-flush-plan-to-subissue 201 en cada Step completado
→ Athena abre PR vía kata-pr-prepare: status: to review en #201 + PR
→ Argos entra: status: review; sale sin aprobar: status: to review
→ Humano aprueba; merge cierra #201 vía Closes #201: status: done

Repite para #202, #203. Cuando #203 mergea con Closes #200 en el body del PR,
la Issue parent #200 cierra automáticamente.

Release cycle (separado):
→ Janus abre release sub-issue (e.g., #210); Tracks: #201-PR, #202-PR, #203-PR
→ Janus aplica status: to release en la release sub-issue
→ Janus inicia kata-release-prepare: status: release
→ Janus concluye kata-release-publish: status: done
```

### Correcto — flujo Plan-first, Camino A (issue-first inmediato)

```
Usuario: "vamos a planificar la migración del logger a Loguru"
→ Agente reconoce: no hay Issue referenciada
→ Agente invoca kata-contributing-issue (template tech-task o user-story)
→ Issue parent #220 creada (Why/What/How, AC)
→ Agente invoca kata-decompose-issue-into-plans 220
→ 2 sub-issues Plan #221, #222 creadas
→ Eunomia aplica status: todo en las 2 sub-issues
→ kata-load-plan-from-subissue 221 materializa .claude/plans/plan-221.md
→ Ejecución sigue per Gate 2 (Athena)
```

### Correcto — flujo Plan-first, Camino B (draft → promoción)

```
Usuario: "vamos a esbozar un plan para refactorizar el logger"
→ Agente crea .claude/plans/plan-logger-refactor.md con front-matter:
   status: draft, issue: TBD, parent: TBD, plan_id: "draft"
→ El borrador madura en N ediciones (Objective, Steps, Risks)
→ Usuario aprueba: "ok, vamos a ejecución"
→ Agente promueve en paso atómico:
   1. kata-contributing-issue → Issue parent #220 (tech-task)
   2. kata-plan-task → sub-issue Plan #221 (Task), body del borrador copiado
   3. mv .claude/plans/plan-logger-refactor.md .claude/plans/plan-221.md
   4. front-matter: status: draft → todo, issue: TBD → guardiatechnology/ahrena#221,
      parent: guardiatechnology/ahrena#220, promoted_at: 2026-05-13T19:00:00Z
   5. Eunomia aplica label "status: todo" en #221 (Gate 1 OK)
→ Ejecución sigue per Gate 2 (Athena)
```

### Incorrecto

```
Tarea: implementar feature X
→ Agente crea branch directamente vía git checkout -b sin abrir Issue parent
→ ❌ Viola lex-issue-first; sin Issue parent, no hay Plan a crear

→ Agente crea archivo .claude/plans/plan-feature-x.md con status: draft
  y luego crea branch vía git checkout -b feat/x sin promover el borrador
  a sub-issue Plan en GitHub
→ ❌ Viola el guardrail plan-first; un borrador local con status: draft está
  permitido, pero iniciar la ejecución (branch, commits, PR) sin antes
  promover el borrador vía kata-contributing-issue +
  kata-decompose-issue-into-plans (Camino B) está prohibido

→ Agente aplica label status: todo en la sub-issue Plan sin completar el body
→ ❌ Viola Gate 1 precondición (c): el body necesita llevar Summary +
   Plan section antes de status: todo definitivo

→ Agente aplica label status: development en la sub-issue sin crear la branch
  remota ni el worktree
→ ❌ Viola Gate 2 precondiciones (a), (b) y (c): branch vía gh issue develop,
  worktree en .worktrees/, y assignee aplicado son los tres pasos mínimos

→ Agente aplica label status: to release en sub-issue de feature
→ ❌ Viola la mutex intra-artefacto de lex-issue-status: `to release`
   pertenece al Eje B (release sub-issue), prohibido en el Eje A
```

## Validación Automatizada

- **Herramienta:** verificación por el agente antes de cualquier ejecución multi-etapa; `kata-plan-task` y `kata-decompose-issue-into-plans` como puntos de entrada canónicos; la revisión de PR confirma que la label `status:*` de la sub-issue Plan y la label `status:*` del PR están alineadas, y que el body de la sub-issue lleva Summary + Plan section. Argos enumera `.claude/plans/*.md` y `.cursor/plans/*.md` en la revisión; para cada `plan_id` en el cache, verifica que existe una sub-issue correspondiente en GitHub (orphans son bloqueo).
- **Momento:** antes de cualquier ejecución de tarea multi-etapa — sin excepción; y en cada transición de estado.
- **Métrica:** 0 tareas multi-etapa ejecutadas sin sub-issue Plan abierta; 0 archivos en `.claude/plans/` o `.cursor/plans/` sin sub-issue correspondiente; 0 PRs mergeados con `status:` divergente entre sub-issue y PR; 100% de las transiciones ejecutadas por el propietario declarado; 100% de las release sub-issues con `Tracks:` listando los PRs mergeados desde el último tag.

## Referencias

- `lex-issue-status` — labels canónicas de status; split Tabla A (dev) / Tabla B (release)
- `lex-issue-type-verified` — verificación programática del Issue Type pos-creación
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — precondiciones de los gates
- `lex-mcp` — preferencia MCP + fallback CLI para `gh issue edit`
- `lex-checkpoint` — rastreo de estado de sesión (complementario)
- `lex-issue-driven` — flujo Issue-Driven; Phase artifacts en `.ahrena/issues/issue-{N}/`
- `codex-agent-planning` — manual operacional del modelo jerárquico (load → edit → flush)
- `kata-plan-task` — procedimiento operacional para crear Plan independiente top-level
- `kata-decompose-issue-into-plans` — descomposición de Issue parent en sub-issues Plan
- `kata-contributing-issue` — creación de Issue parent (precondición del Gate 1)
- `kata-load-plan-from-subissue` — materializa cache local desde el body de la sub-issue Plan
- `kata-flush-plan-to-subissue` — flushea el cache local (filtrando `<!-- not-flushed -->`) al body de la sub-issue
- `kata-session-heartbeat` — actualización del heartbeat de sesión
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — propietarios de las transiciones
