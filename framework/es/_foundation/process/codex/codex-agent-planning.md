# Codex: Planificación de Tareas de Agentes

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación, mantenimiento y ciclo de vida de Planes en el contexto Ahrena

## Visión General

Este Codex es el manual canónico de planificación de tareas por agentes en el modelo jerárquico **Issue → Plan → PR**. Complementa `lex-agent-planning` (la Ley) con templates, ejemplos de llenado, walkthroughs Top-down y Plan-first, cadencia de load/flush, propietarios de cada transición y directrices para casos límite. Todo agente que cree o mantenga Planes DEBE consultar este Codex.

## Contexto

- **Dominio:** disciplina de ejecución de tareas por agentes AI
- **Audiencia:** todos los agentes (Claude, Cursor, warriors, katas) y revisores humanos
- **Actualización:** cuando el template, el enum de status, la tabla de propietarios o la cadencia de sync cambian (ADR recomendado para cambios estructurales)

---

## 1. Modelo jerárquico Issue → Plan → PR

```
Issue (User Story | Bug | Tech Task)            ← problema, Why/What/How, AC
   │
   ├─ Plan sub-issue #M1 (Task)                  ← unidad ejecutable #1
   │     ├─ status: todo | development | to review | review | done
   │     ├─ branch: {type}/{M1}-{slug}
   │     └─ PR(s) que cierran este Plan
   │
   ├─ Plan sub-issue #M2 (Task)
   │     └─ ...
   │
   └─ Plan sub-issue #M3 (Task)
         └─ ...
```

| Capa | Ubicación | Rol | Versionado |
|---|---|---|---|
| **Issue parent** | `https://github.com/{owner}/{repo}/issues/{N}` | Problema, AC, motivación. No tiene branch propia | GitHub audit log |
| **Plan sub-issue** | `https://github.com/{owner}/{repo}/issues/{M}`, sub-issue de #{N} | Canónico. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Lleva branch y PR(s) | GitHub audit log |
| **Cache del provider** | `.claude/plans/plan-{M}-{slug}.md` o `.cursor/plans/plan-{M}-{slug}.md`, gitignored | AI working memory + scratch. Superset del body + bloques `<!-- not-flushed -->`. Nombrado por número de sub-issue | Cache local regenerable |
| **Phase artifacts** | `.ahrena/issues/issue-{N}/`, committed | `01-brief.md` … `06-quality-report.md` del flujo Issue-Driven (vinculados a la Issue parent) | Git |

### Resolución del path del cache local

```
1. Determinar el provider (Claude Code → .claude/plans/, Cursor → .cursor/plans/)
2. Nombrar el archivo plan-{M}-{slug}.md, donde {M} es el número de la sub-issue
3. Confirmar vía .gitignore que el directorio del provider está excluido
```

> **Modelo legado (deprecated):** archivos `plan-{NNN}-{slug}.md` en `.claude/plans/` (sin sub-issue correspondiente) son considerados zombies. No crear archivos nuevos sin sub-issue Plan abierta en GitHub. Caches existentes que no mapean a una sub-issue deben ser triados en `.ahrena/issues/_legacy/` o descartados.

---

## 2. Nomenclatura del cache local

```
.claude/plans/plan-{M}-{slug}.md      (agente Claude)
.cursor/plans/plan-{M}-{slug}.md      (agente Cursor)
```

| Campo | Regla |
|---|---|
| `{M}` | Número de la sub-issue Plan en GitHub. Sin padding, sin prefix — `plan-201.md`, no `plan-0201.md` ni `plan-201-slug.md` |

Ejemplos:
- `.claude/plans/plan-201.md` — cache del Plan de la sub-issue #201
- `.cursor/plans/plan-222.md` — cache del Plan de la sub-issue #222

El cache es gitignored — no aparece en `git status` ni en `git log`. Para inspeccionar Planes sin clonar:

```bash
gh issue view {M} --json body --jq .body
```

Para sincronizar localmente: `kata-load-plan-from-subissue {M}`.

---

## 3. Template del body de la sub-issue Plan (canónico) y del cache local

### 3a. Body de la sub-issue Plan (canónico)

```markdown
## Summary

{2-4 frases describiendo el objetivo ejecutable de este Plan — típicamente
una rebanada del alcance de la Issue parent.}

Parent: #{N}

## Plan

### Objective
Refactorizar el aggregate Ledger para event sourcing — sustituir CRUD directo
en PostgreSQL por event store append-only + projection write-side.

### Steps
- [x] 1. Mapear comandos actuales del Ledger
- [x] 2. Modelar eventos canónicos (LedgerEntryRecorded, LedgerEntryReversed)
- [ ] 3. Implementar EventStore con optimistic concurrency
- [ ] 4. Migrar handlers a emit-only
- [ ] 5. Tests de invariante (saldo nunca negativo)

### Dependencies
- Plan #202 (projection write-side) — puede correr en paralelo
- Plan #203 (read-side) — bloqueado por este Plan

### Risks
- Migration de datos existentes — mitigado por shadow-write durante cutover
- Optimistic concurrency en alta contención — benchmark en staging primero

### Open Questions
- None
```

El body de la sub-issue es grabado por:
- `kata-decompose-issue-into-plans` en la creación (downstream de la Issue parent)
- `kata-plan-task` cuando el Plan es independiente (top-level vinculado a una Issue existente)
- `kata-flush-plan-to-subissue` en cada disparador de sync (transición, Step completado, fin de sesión)

### 3b. Cache local `.claude/plans/plan-{M}-{slug}.md` (working memory)

```markdown
## Summary
... (espeja el body de la sub-issue)

## Plan
... (espeja el body de la sub-issue)

<!-- not-flushed -->
## Working notes
- 23:30 — terminó Step 2; eventos modelados en src/ledger/events.py
- Decision: usar UUID v7 como event_id (per lex-entities)
- Bug encontrado en EventStore: retry sin idempotency key — escribir
  test reproduciendo antes de fixar

## Next actions
1. Step 3 — EventStore con optimistic concurrency
2. Step 4 — handlers emit-only
3. Step 5 — tests de invariante

## Scratch
gh issue develop registra la branch como "Development" en la sidebar.
Límite del body de la Issue: ~65KB.
<!-- /not-flushed -->
```

El cache **no tiene front-matter YAML** — la sub-issue de GitHub ya lleva toda la metadata (assignees, labels `status:*`, milestones, fechas). Los bloques `<!-- not-flushed -->` son filtrados antes del flush a la sub-issue.

> **Front-matter legacy:** archivos en `.ahrena/issues/_legacy/` (deprecated) mantienen YAML front-matter histórico (`plan_id`, `status`, `claude_session`, `merge_commit`, `closed_at`). Ese formato es reconocido para audit, pero NO replicar en Planes nuevos.

---

## 4. Estados del ciclo de vida (enum unificado)

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, cualquier etapa)
```

| Status | Cuándo usar | Propietario que transiciona |
|---|---|---|
| `todo` | Sub-issue Plan creada con body canónico, sin branch ni worktree, aún no comenzó | Quien crea: `warrior-eunomia` (fallback: agente de la sesión) |
| `development` | Implementación en curso (Athena Phase 4); branch + worktree + assignee aplicados | `warrior-athena` |
| `to review` | PR abierto, esperando que un reviewer lo tome | `warrior-athena` (entrada); `warrior-argos` (retorno desde `review`) |
| `review` | Argos o humano revisando activamente | `warrior-argos` (entrada y salida) |
| `to release` | (Eje B solamente) Release sub-issue creada, esperando inicio | `warrior-janus` |
| `release` | (Eje B solamente) Release en ejecución (tag/build/publish) | `warrior-janus` |
| `done` | PR mergeado y sub-issue Plan cerrada vía `Closes #{M}` (Eje A) O release publicado (Eje B) | `warrior-athena` (Eje A) / `warrior-janus` (Eje B) |
| `abandoned` | Plan descartado (cualquier etapa) | Creador o propietario actual |

**Estado canónico:** el `status:` vive como **label** en la sub-issue Plan en GitHub (y en el PR, a partir de `to review`). No hay "front-matter del Plan" — el body de la sub-issue es canónico; el cache local es regenerable.

### Split en dos ejes

- **Eje A — Dev cycle** (Plan derivado de User Story / Bug / Tech Task): `todo → development → to review → review → done` + `abandoned`. Propietarios: Eunomia/Athena/Argos.
- **Eje B — Release cycle** (release sub-issue exclusivamente): `to release → release → done` + `abandoned`. Propietario: Janus.

La mutex es **intra-artefacto** (dentro de cada sub-issue/PR), no cross-artifact. Aplicar label del Eje B en sub-issue de feature (o viceversa) está prohibido per HARD-GATE en `lex-issue-status`.

---

## 5. Propietarios de cada transición (vista de flujo)

### Eje A — Dev cycle (Eunomia/Athena/Argos)

```
Eunomia: — ──→ todo                                                  [Plan sub-issue creada]
                 │
                 ▼
Athena:  todo ──→ development ──→ to review                          [branch + worktree + assignee]
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ done   (humano aprueba; merge cierra sub-issue)
                                       │
                  cualquiera ──→ abandoned (terminal alternativo)
```

### Eje B — Release cycle (Janus)

```
Janus:   — ──→ to release ──→ release ──→ done                      [release sub-issue dedicada]
                  │
                  cualquiera ──→ abandoned (release abortado antes del tag)
```

Cada propietario actualiza simultáneamente:

1. Body de la sub-issue Plan vía `kata-flush-plan-to-subissue` (solo si hubo edición en el cache local).
2. Label `status: <name>` en la sub-issue Plan (per `lex-issue-status` mutex intra-artefacto).
3. Label `status: <name>` en el PR (a partir de `to review`, solo en Eje A).

---

## 6. Walkthrough A — Top-down (la Issue parent existe)

Escenario: el usuario apunta a una Issue parent existente y pide descomponerla en Planes ejecutables.

### Paso 1 — Verificar la Issue parent

```bash
gh issue view 200 --repo {owner}/{repo} --json title,body,labels,issueType
```

Confirma: Issue Type `Feature` (o `Bug`/`Task`), template usado, AC numerados, labels obligatorias, Why/What/How completados. Si algo falta, invocar `kata-contributing-issue` para completar antes.

### Paso 2 — Descomposición en sub-issues Plan

```bash
# Eunomia invoca kata-decompose-issue-into-plans
# Lee la Issue parent, propone N sub-issues Plan, confirma con el usuario,
# crea cada sub-issue vía MCP create_issue (Issue Type Task) vinculada
# a la parent, completa body canónico (Summary + Plan), aplica labels
# obligatorias, verifica Issue Type, aplica status: todo
```

Resultado típico:

```
Issue #200 (Feature) — "Event sourcing for ledger"
├── #201 (Task)   — "Refactor Ledger aggregate"
├── #202 (Task)   — "Implement projection write-side"
└── #203 (Task)   — "Migrate read-side via projection"
```

### Paso 3 — Eunomia aplica `status: todo` en las 3 sub-issues (Gate 1 OK)

Cada sub-issue ahora tiene body canónico, Issue Type `Task`, labels obligatorias. Branch, worktree, assignee NO fueron aplicados — pertenecen a Athena en el Gate 2.

### Paso 4 — Athena toma el primer Plan ejecutable (#201)

```bash
# Gate 2 — todo → development
gh issue develop 201 --base main --name refactor/201-ledger-event-sourcing
git worktree add .worktrees/201-ledger-event-sourcing refactor/201-ledger-event-sourcing
gh issue edit 201 --add-assignee fernandoseguim
gh issue edit 201 --add-label "status: development" --remove-label "status: todo"
```

### Paso 5 — Cargar cache local y ejecutar

```bash
kata-load-plan-from-subissue 201   # materializa .claude/plans/plan-201.md
# implementación corre en el worktree
# en cada Step completado: kata-flush-plan-to-subissue 201
# en fin de sesión: kata-flush-plan-to-subissue 201
```

### Paso 6 — Abrir PR

```bash
# Athena vía kata-pr-prepare:
# - kata-flush-plan-to-subissue 201 (flush final)
# - gh pr create --title "..." --body "Closes #201\nRefs #200" ...
# - aplica status: to review en la sub-issue #201 + PR
```

### Paso 7 — Review y merge

Argos entra (`status: review`), sale (`status: to review`); humano aprueba; merge cierra sub-issue #201 vía `Closes #201`; Athena aplica `status: done`. Repite para #202, #203. Cuando el último PR cierra la Issue parent #200 (`Closes #200`), todo termina.

---

## 7. Walkthrough B — Plan-first (intención sin Issue parent)

Escenario: el usuario dice "vamos a planificar la migración del logger a Loguru" sin referenciar ninguna Issue.

### Paso 1 — El agente NO materializa archivo local

Materializar `.claude/plans/plan-XXX.md` ahora violaría el guardrail plan-first de `lex-agent-planning`. El agente pausa y sigue la secuencia canónica.

### Paso 2 — Crea la Issue parent

```bash
# Agente invoca kata-contributing-issue
# Pregunta tipo: User Story, Bug o Tech Task?
# Usuario elige Tech Task (refactor interno sin AC orientado al usuario final)
# Issue #220 creada con template tech-task, Issue Type Task,
# Why/What/How completados, labels obligatorias, status: todo
```

### Paso 3 — Descomposición en Planes

```bash
# Eunomia invoca kata-decompose-issue-into-plans 220
# Propone 2 sub-issues:
#   #221 (Task) — "Migrate framework code to loguru"
#   #222 (Task) — "Migrate tooling and scripts to loguru"
# Confirma con el usuario; crea sub-issues; completa body canónico;
# aplica status: todo en las dos
```

### Paso 4 — Desde aquí, es Walkthrough A

Athena toma #221, ejecuta Gate 2 (`todo → development`), implementa, abre PR, etc.

La diferencia entre Walkthrough A y B es solo el paso inicial. Una vez que existen Issue parent + sub-issues Plan en GitHub, el flujo converge.

---

## 8. Gate 1 — checklist completa (`— → todo`)

Eunomia (o fallback) ejecuta en secuencia antes de marcar `status: todo`:

| Paso | Acción | Lex de referencia |
|---|---|---|
| 1 | Confirmar Issue parent abierta y en conformidad | `lex-issue-first`, `lex-issue-quality` |
| 2 | Crear sub-issue Plan vinculada a la parent vía MCP `create_issue` (preferido) o `gh issue create --type Task` (fallback) | `lex-mcp` |
| 3 | Completar body de la sub-issue con Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions) vía MCP `update_issue` o `gh issue edit --body-file` | `lex-agent-planning` |
| 4 | Verificar Issue Type pos-creación (debe ser `Task`) | `lex-issue-type-verified` |

Branch, worktree y assignee NO son precondiciones de este gate.

## 9. Gate 2 — checklist completa (`todo → development`)

Athena ejecuta en secuencia antes de marcar `status: development`:

| Paso | Acción | Lex de referencia |
|---|---|---|
| 1 | Crear branch remota y vincularla a la sub-issue: `gh issue develop {M} --base main --name {type}/{M}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 2 | Crear worktree en `.worktrees/{M}-{slug}/` per `lex-git-worktrees` | `lex-git-worktrees` |
| 3 | Aplicar assignee en la sub-issue Plan (humano o identidad de agente que se compromete a ejecutar) | `lex-issue-quality` |

Aplicar `status: development` sin los 3 pasos está PROHIBIDO.

---

## 10. Cuándo un Plan es obligatorio (y cuándo no lo es)

### Obligatorio

- Tarea con 2+ etapas encadenadas
- Cualquier operación que toque 2+ archivos
- Toda invocación de warrior o cry (multi-etapa por definición)
- Cualquier tarea que produzca artefactos permanentes (archivos, commits, PRs, posts)

### No obligatorio (etapa única trivial)

- Editar un único archivo con instrucción directa y precisa
- Leer/consultar archivos sin escritura
- Ejecutar un único comando aislado sin efecto colateral permanente
- Responder una pregunta factual

### Zona gris — usar Plan por precaución

- Tarea aparentemente simple que puede ramificarse (ej.: "corregir el bug" sin conocer el alcance)
- Operación irreversible aunque sea de etapa única (ej.: borrar archivos)

---

## 11. Relación entre Planes y otros artefactos

```
Issue parent (#N) — User Story | Bug | Tech Task
    │
    ├── label: status: <name> (Eje A o Eje B en la release sub-issue)
    │
    ├── Sub-issues Plan (#M1, #M2, ..., Task)              canónico de cada unidad
    │   ├── body: Summary + Plan
    │   ├── label: status: <name>
    │   │
    │   ├── PR (label: status: <name>, a partir de "to review")    [solo Eje A]
    │   │
    │   ├── .claude/plans/plan-{M}-{slug}.md o .cursor/plans/plan-{M}-{slug}.md  cache local
    │   │   └── superset del body + bloques <!-- not-flushed -->   gitignored
    │   │
    │   └── docs/adr/ADR-{n}-*.md (committed)                       si decisión arquitectónica
    │
    ├── .ahrena/issues/issue-{N}/ (committed)                       Phase artifacts
    │   ├── 01-brief.md
    │   ├── 02-requirements.md
    │   ├── 03-architecture.md
    │   ├── 05-security-review.md
    │   └── 06-quality-report.md
    │
    ├── Heartbeat de sesión (.ahrena/workflow/sessions/<uuid>.json, gitignored)
    │
    └── ─ ─ ─ no confundir con ─ ─ ─
        Checkpoint (.checkpoint — gitignored, sesión)
```

- Body de la sub-issue Plan, label de la sub-issue y label del PR son sincronizados por el propietario en cada transición.
- ADR es abierto cuando el Plan identifica una decisión arquitectónica relevante (vive en `docs/adr/`, no en `.ahrena/issues/`). Ejemplos de nombre: `ADR-008-use-event-sourcing-for-refund-audit-trail.md`, `ADR-007-use-fastapi-routers.md`, `ADR-001-use-event-sourcing-for-ledger.md`, `ADR-002-migrate-to-fastapi.md`.
- Heartbeat de sesión (`codex-session-tracking`) registra qué sesión Claude Code opera en el Plan ahora.
- Checkpoint NO está subordinado al Plan; es artefacto paralelo de **sesión**, no de **task**.

### Plan vs `.checkpoint` — delimitación canónica

El Plan cubre **task**: Objetivo, Alcance, Steps `[x]`, Decisiones cerradas, Riesgos, Verificación. Vive en GitHub.
El checkpoint cubre **sesión**: Session focus, Active plans (punteros), Open threads, Notes. Gitignored.

| Contenido | Body de la sub-issue Plan (canónico) | Cache local (working memory) | `.checkpoint` (sesión) |
|---|:---:|:---:|:---:|
| Steps `[x]` | ✅ | ✅ (espejado) | ❌ |
| Decisiones cerradas de la task | ✅ (o ADR) | ✅ (espejado) | ❌ |
| Riesgos de la task | ✅ | ✅ (espejado) | ❌ |
| Working notes / debugging diary | ❌ | ✅ (bloque `<!-- not-flushed -->`) | ❌ |
| Foco general de la ventana de trabajo | ❌ | ❌ | ✅ |
| Lista de Planes activos en la sesión | ❌ | ❌ | ✅ |
| Threads paralelos que no se volvieron Plan | ❌ | ❌ | ✅ |
| Scratchpad libre, links, recordatorios | ❌ | ❌ | ✅ |

Si el contenido se repite en ambos, hay superposición — el Plan gana (canónico). La superposición está PROHIBIDA por `lex-checkpoint` regla 5 y por `lex-agent-planning`.

---

## 12. Cadencia de load/flush

La sincronización entre el body de la sub-issue Plan (canónico) y el cache local ocurre en **4 disparadores canónicos**:

| Disparador | Operación | Quién dispara |
|---|---|---|
| Inicio de sesión / handoff entre agentes | `kata-load-plan-from-subissue` | Athena, Argos, Janus (al inicio de cada sesión de trabajo en un Plan) |
| Transición de label `status:` en sub-issue/PR | `kata-flush-plan-to-subissue` | Eunomia, Athena, Argos, Janus (al momento de la transición) |
| Step del plan marcado como completado (`[ ]` → `[x]`) | `kata-flush-plan-to-subissue` | Agente que completa el Step |
| Fin de sesión (heartbeat termina o agente sale) | `kata-flush-plan-to-subissue` | `kata-session-heartbeat` en el shutdown |

Toggles intermedios, ediciones de scratch (bloques `<!-- not-flushed -->`) y working notes son **libres** — no disparan flush. La regla es: el body de la sub-issue debe reflejar el estado **estable** (entre transiciones y Steps), no el estado **transiente** (durante working).

### Flujo típico de una sesión de trabajo

```
1. Athena entra (recibe handoff de Eunomia):
   → kata-load-plan-from-subissue {M}    (materializa cache local)
   → Gate 2: gh issue develop + worktree + assignee
   → aplica label status: development en la sub-issue + PR (si ya existe)
   → kata-flush-plan-to-subissue {M}     (registra la transición)

2. Athena trabaja:
   → edita archivos en el worktree
   → registra notas en el cache local (bloques <!-- not-flushed -->)
   → marca Step [x] en el cache
   → kata-flush-plan-to-subissue {M}     (Step completado)

3. Athena abre PR vía kata-pr-prepare:
   → flush final del cache pre-PR
   → create_pull_request (Closes #{M}, Refs #{N})
   → aplica status: to review en sub-issue + PR
   → kata-flush-plan-to-subissue {M}     (transición registrada)

4. Athena sale:
   → kata-session-heartbeat en el shutdown dispara
   → kata-flush-plan-to-subissue {M}     (cleanup final)

5. Argos entra:
   → kata-load-plan-from-subissue {M}    (refresh del cache local)
   → ...
```

### Detección de drift remoto (preflight)

`kata-flush-plan-to-subissue` por default ejecuta preflight: lee el body actual de la sub-issue, compara con el último estado conocido y bloquea si hay edición remota desconocida (otra sesión, edición vía UI de GitHub). Ofrece: (a) mostrar diff y abortar, (b) merge manual, (c) overwrite vía `force=true`. El heartbeat de sesión permite identificar la sesión concurrente.

---

## 13. Loop de revisión pendiente (estado `to review`)

Después de que Athena abre el PR, el ciclo de review opera en **dos fases distintas y secuenciales** + un handler para CHANGES_REQUESTED:

### Fase A — Argos pre-flight cycles

Hasta 3 ciclos interactivos `A1, A2, A3`, gateados por `AskUserQuestion` (Athena nunca invoca a Argos sin confirmación). Cada ciclo: Athena pregunta "¿Quieres review del Argos en el HEAD actual?" — opciones (a) sí, (b) saltar a human review, (c) stop. Si (a) → Argos corre, publica review con marker idempotente; Athena lee findings; P0 BLOCKER address obligatorio; P1 AskUserQuestion (address o defer); P2 nota. Commit + push si hubo cambios → HEAD nuevo. Repite hasta A3 o el usuario elige (b)/(c).

### Fase B — Human nudge loop

Después de que Fase A termina, Athena pregunta el modo de agendamiento: (a) `/loop` en la sesión, (b) cron remoto, (c) manual. Modos (a)/(b) agendan 3 ciclos `H1, H2, H3` con 15 min entre cada uno. En cada cycle, Athena dispara notificación vía MCP en `notifications.channels.pr_review_timeout` — el mensaje escala en urgencia (H1 "PR listo", H2 "reminder #1", H3 "reminder #2, 2da cobranza"). Consulta `gh pr view {N} --json reviewDecision,mergedAt`:

- `mergedAt != null` → transición `status: to review → done`, captura `mergeCommit.oid`, termina loop.
- `reviewDecision == APPROVED` (sin merge) → comenta "PR aprobado, esperando merge", termina loop.
- `reviewDecision == CHANGES_REQUESTED` → **dispara Fase C**.
- En caso contrario → si H<3, reagenda; si H==3, termina silenciosamente.

### Fase C — CHANGES_REQUESTED handler

Si humano pide cambios durante Fase B: Athena lee los comentarios del reviewer y pregunta vía AskUserQuestion: (a) address ahora, (b) defer para follow-up Issue, (c) stop. Si (a) → Athena implementa, commitea, push (HEAD nuevo). Después de (a) o (b) → **reset completo**: Athena reagenda el loop a partir de la **Fase A** (3 nuevos Argos cycles en el HEAD nuevo) — porque commits nuevos invalidan la review anterior de Argos. No salta directo a Fase B.

Argos opera el sub-ciclo `to review ↔ review` en Fase A (con cambio de label durante la ejecución) y en Fase C cuando es re-invocado. Argos nunca mueve a `done`; la transición `to review → done` es exclusiva de Athena al detectar merge.

---

## 14. Buenas prácticas

1. **Escribir el Plan antes de saber todo.** El objetivo es hacer la intención visible, no producir documentación perfecta. Un Plan impreciso que evoluciona es mejor que ningún Plan.
2. **Mantener Steps atómicos.** Cada Step debe ser verificable: hecho o no hecho. Evitar Steps vagos como "encargarse de la parte de events".
3. **Actualizar en tiempo real.** Marcar `[x]` a medida que cada Step concluye, no al final de todo — y disparar `kata-flush-plan-to-subissue` para persistir.
4. **Sincronizar label `status:` en sub-issue + PR.** Toda transición de propietario toca la sub-issue Plan y el PR. Skippear cualquiera produce drift que aparece en auditoría.
5. **No crear Planes fantasma.** Si la tarea es cancelada antes de comenzar, aplicar `status: abandoned` en la sub-issue con comentario explicando — no borrar la sub-issue.
6. **Plan canónico vive en GitHub.** No crear archivos `.claude/plans/*.md` o `.cursor/plans/*.md` como canónicos. El body de la sub-issue es canónico; el cache local es regenerable; `.ahrena/issues/issue-{N}/` lleva Phase artifacts.
7. **Working notes libres en el cache local.** Usar bloques `<!-- not-flushed -->` para registrar decisiones en borrador, debugging notes y próximos pasos volátiles — esos bloques son filtrados en el flush, así que no contaminan el body canónico.
8. **La descomposición es parte del planificar.** Antes de tomar una Issue grande, descomponerla en sub-issues Plan vía `kata-decompose-issue-into-plans`. Un único Plan gigante que cubre toda una Feature es antipattern — partir en unidades ejecutables.

---

## Referencias

- `lex-agent-planning` — Ley correspondiente (Gate 1 de `— → todo` + Gate 2 de `todo → development` + Tablas A y B)
- `lex-issue-status` — labels canónicos; split Eje A (dev) + Eje B (release)
- `lex-issue-type-verified` — verificación programática del Issue Type
- `lex-issue-first`, `lex-issue-quality` — precondiciones de creación de Issue parent y sub-issues Plan
- `lex-git-branches`, `lex-git-worktrees` — precondiciones del Gate 2
- `lex-mcp` — preferencia MCP + fallback CLI
- `kata-contributing-issue` — creación de la Issue parent (precondición del Gate 1)
- `kata-decompose-issue-into-plans` — descomposición de Issue parent en sub-issues Plan
- `kata-plan-task` — creación de Plan independiente top-level vinculado a Issue existente
- `kata-load-plan-from-subissue` — materializa cache local desde el body canónico de la sub-issue
- `kata-flush-plan-to-subissue` — flushea el cache local (filtrando scratch) al body de la sub-issue
- `kata-session-heartbeat` — heartbeat de sesión Claude Code
- `codex-session-tracking` — manual de tracking de sesión
- `codex-notifications` — manual provider-agnóstico de envío vía MCP
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — propietarios de las transiciones
- `lex-checkpoint` — rastreo de estado de sesión (complementario)
- `lex-issue-driven` — flujo Issue-Driven de Athena
