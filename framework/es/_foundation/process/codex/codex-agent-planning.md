# Codex: Planificación de Tareas de Agentes

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación, mantenimiento y ciclo de vida de planes de tareas por agentes en el contexto Ahrena

## Visión General

Este Codex es el manual canónico de planificación de tareas por agentes per ADR-002 (modelo Issue-as-plan en tres capas). Complementa `lex-agent-planning` (la Ley) con templates, ejemplos de relleno, cadencia de load/flush, owners de cada transición y directrices para casos límite. Todo agente que crea o mantiene planes DEBE consultar este Codex.

## Contexto

- **Dominio:** disciplina de ejecución de tareas por agentes AI
- **Audiencia:** todos los agentes (Claude, Cursor, warriors, katas) y revisores humanos
- **Actualización:** cuando el template, el enum de status, la tabla de owners o la cadencia de sync cambian (ADR recomendado para cambios estructurales)

---

## 1. Modelo de almacenamiento en tres capas (per ADR-002)

| Capa | Ubicación | Rol | Versionado |
|---|---|---|---|
| **Issue body** | `https://github.com/{owner}/{repo}/issues/{N}` | Canonical. Summary + Plan section (Objective, Steps, Risks, Dependencies, Open Questions) | Audit log nativo de GitHub (timestamp + autor por edición) |
| **`.plans/{N}.md`** | Raíz del repo, gitignored | AI working memory + scratch. Superset del body de la Issue + bloques `<!-- not-flushed -->` | Caché local regenerable |
| **`.issues/{N}/`** | Raíz del repo, committed | Phase artifacts (`01-brief.md` … `06-quality-report.md`) | Git |

### Resolución del path del caché local

```
1. Leer .ahrena/.directives
2. Si paths.plans existe → usar ese valor
3. De lo contrario → usar default `.plans/` (raíz del repo, gitignored)
```

Ejemplo de override:
```yaml
# .ahrena/.directives
paths:
  plans: ".cache/ai-plans/"
```

> **Modelo legado (pre-ADR-002, deprecated):** los archivos `plan-{NNN}-{slug}.md` en `.claude/plans/` fueron migrados a `.issues/_legacy/` en el PR de plan-046. No crear archivos nuevos en ese formato — el body de la Issue es canonical ahora; `.plans/{N}.md` es caché local nombrado por el número de la Issue.

---

## 2. Nombrado del caché local

```
.plans/{N}.md
```

| Campo | Regla |
|---|---|
| `{N}` | Número de la Issue de GitHub correspondiente. Sin padding, sin prefix — `.plans/96.md`, no `.plans/plan-096.md` o `.plans/96-slug.md` |

Ejemplos:
- `.plans/42.md` — caché del plan de la Issue #42
- `.plans/96.md` — caché del plan de la Issue #96
- `.plans/100.md` — caché del plan de la release Issue #100 (Eje B)

El caché es gitignored — no aparece en `git status` ni en `git log`. Para inspeccionar planes sin clonar:

```bash
gh issue view {N} --json body --jq .body
```

Para sincronizar localmente: `kata-load-plan-from-issue {N}`.

---

## 3. Template del body de la Issue (canonical) y del caché local

### 3a. Body de la Issue (canonical per ADR-002)

```markdown
## Summary

**As** {user_role},
**I want** {specific_objective},
**So that** {benefit_and_value}.

(o texto libre de 2-4 frases describiendo el objetivo de alto nivel)

## Plan

### Objective
Alinear el ciclo de vida del plan y de la Issue de GitHub a un único enum
de status (todo → development → to review → review → done para Eje A;
to release → release → done para Eje B), con owner explícito para
cada transición y notificaciones provider-agnósticas vía MCP.

### Steps
- [x] 1. Issue + branch + worktree (Eunomia o fallback)
- [x] 2. ADR-002 (MADR simplificado)
- [x] 3. lex-agent-planning (pt-BR)
- [ ] 4. codex-agent-planning (pt-BR)
- [ ] 5. lex-issue-status split (pt-BR)
- ...

### Dependencies
- plan-043 (PR #93) — merged
- plan-044 (Eunomia) — absorbido por plan-046 Step 10
- plan-045 (Janus pointer) — absorbido por plan-046 Step 3.5

### Risks
- .plans/ perdida en fresh clone — mitigado por kata-load-plan-from-issue
- Flush conflictivo entre sesiones — preflight de drift detecta
- Loop 3×15min puede ser corto fuera de horario comercial — mitigar vía .directives

### Open Questions
Todas resueltas el 2026-05-11.
```

El body de la Issue es grabado por:
- `kata-plan-task` en la creación inicial (Paso 5 del HARD-GATE de `— → todo`)
- `kata-flush-plan-to-issue` en cada disparador de sync (transición, Step concluido, fin de sesión)

### 3b. Caché local `.plans/{N}.md` (working memory)

```markdown
## Summary
... (espeja el body de la Issue)

## Plan
... (espeja el body de la Issue)

<!-- not-flushed -->
## Working notes
- 23:30 — terminó Step 3
- Decision: usar git mv para preservar history en Step 14

## Next actions
1. Step 4 — codex-agent-planning
2. Step 5 — path move
3. Step 17 — abrir PR draft

## Scratch
gh issue develop registra branch como "Development" en la sidebar.
Límite del body de la Issue: ~65KB (probado con plan-046).
<!-- /not-flushed -->
```

El caché **no tiene front-matter YAML** — el GitHub Issue ya lleva toda la metadata (assignees, labels `status:*`, milestones, dates). Los bloques `<!-- not-flushed -->` se filtran antes del flush a la Issue.

> **Front-matter legacy:** los planes en `.issues/_legacy/` (pre-ADR-002) mantienen YAML front-matter histórico (`plan_id`, `status`, `claude_session`, `merge_commit`, `closed_at`). Ese formato es reconocido para audit, pero NO replicar en planes nuevos.

---

## 4. Estados del ciclo de vida (enum unificado)

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, cualquier etapa)
```

| Status | Cuándo usar | Owner que transiciona |
|---|---|---|
| `todo` | Plan creado, Issue abierta, branch remota vinculada, worktree listo, aún no comenzó | Quien lo crea: `warrior-eunomia` (fallback: agente de la sesión) |
| `development` | Implementación en curso (Athena Phase 4) | `warrior-athena` |
| `to review` | PR abierto, esperando que el reviewer lo tome | `warrior-athena` (entrada); `warrior-argos` (retorno de `review`) |
| `review` | Argos o humano revisando activamente | `warrior-argos` (entrada y salida) |
| `to release` | Review aprobado, esperando que comience la release | `warrior-athena` (detecta `APPROVED`) |
| `release` | Release en ejecución (tag/build/deploy) | `warrior-janus` |
| `done` | Release concluida, PR mergeado, ciclo cerrado | `warrior-janus` |
| `abandoned` | Plan descartado (cualquier etapa) | Creador u owner actual |

**Estado canónico per ADR-002:** el `status:` vive como **label** en la Issue de GitHub (y en el PR, a partir de `to review`). Ya no hay "front-matter del plan" — el body de la Issue es canonical; `.plans/{N}.md` es caché regenerable. Los planes legados en `.issues/_legacy/` mantienen front-matter histórico para audit, sin retrofit.

### Split en dos ejes (per ADR-002 / plan-045 absorbido)

- **Eje A — Dev cycle** (feature/fix/chore Issues/PRs): `todo → development → to review → review → done` + `abandoned`. Owners: Eunomia/Athena/Argos.
- **Eje B — Release cycle** (release Issue exclusivamente): `to release → release → done` + `abandoned`. Owner: Janus.

La mutex es **intra-artefacto** (dentro de cada Issue/PR), no cross-artifact. Aplicar label del Eje B en Issue/PR de feature (o viceversa) está prohibido per HARD-GATE en `lex-issue-status`.

---

## 5. Owners de cada transición (visión de flujo)

### Eje A — Dev cycle (Eunomia/Athena/Argos)

```
Eunomia: — ──→ todo                                                  [feature Issue + PR]
                 │
                 ▼
Athena:  todo ──→ development ──→ to review
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ done   (humano aprueba; merge cierra Issue)
                                       │
                  cualquier ──→ abandoned (terminal alternativo)
```

### Eje B — Release cycle (Janus)

```
Janus:   — ──→ to release ──→ release ──→ done                      [release Issue dedicada]
                  │
                  cualquier ──→ abandoned (release abortada antes del tag)
```

Cada owner actualiza simultáneamente:

1. Body de la Issue vía `kata-flush-plan-to-issue` (canonical per ADR-002 — solo si hubo edición en el caché local).
2. Label `status: <name>` en la Issue de GitHub (per `lex-issue-status` mutex intra-artefacto).
3. Label `status: <name>` en el PR (a partir de `to review`, solo en el Eje A).

---

## 6. Owner de `— → todo`: 5 pasos canónicos

Eunomia (o fallback) ejecuta en secuencia antes de marcar `status: todo`:

| Paso | Acción | Lex de referencia |
|---|---|---|
| 1 | Abrir Issue (template, label, type, assignee, Why/What/How) | `lex-issue-first`, `lex-issue-quality` |
| 2 | Verificar Issue Type post-creación | `lex-issue-type-verified` |
| 3 | Crear branch remota y vincular a la Issue: `gh issue develop {N} --base main --name {type}/{N}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 4 | Crear worktree en `.worktrees/{N}-{slug}/` | `lex-git-worktrees` |
| 5 | Rellenar body de la Issue con plan canónico (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) vía MCP `update_issue` (preferido) o `gh issue edit --body-file` (fallback) | `lex-agent-planning`, `lex-mcp` |

La falla en cualquier paso deja el plan en borrador (no puede ser presentado como `todo`). Per HARD-GATE en `lex-agent-planning`, incluso en hotfix los 5 pasos son obligatorios.

---

## 7. Cuándo un plan es obligatorio (y cuándo no lo es)

### Obligatorio

- Tarea con 2+ etapas encadenadas
- Cualquier operación que toque 2+ archivos
- Toda invocación de warrior o cry (por definición multi-etapa)
- Cualquier tarea que produzca artefactos permanentes (archivos, commits, PRs, posts)

### No obligatorio (etapa única trivial)

- Editar un único archivo con instrucción directa y precisa
- Leer/consultar archivos sin escritura
- Ejecutar un único comando aislado sin efecto colateral permanente
- Responder una pregunta factual

### Zona gris — usar plan por precaución

- Tarea aparentemente simple que puede ramificarse (ej.: "corregir el bug" sin conocer el alcance)
- Operación irreversible incluso siendo de etapa única (ej.: eliminar archivos)

---

## 8. Relación entre planes y otros artefactos

```
Issue GitHub                                    canonical (per ADR-002)
    ├── body: plan canónico (Summary + Plan)
    ├── label: status: <name> (Eje A o Eje B)
    │
    ├── PR (label: status: <name>, a partir de "to review")        [solo Eje A]
    │
    ├── .plans/{N}.md (gitignored)                                  caché local de la IA
    │   └── superset del body + bloques <!-- not-flushed -->
    │
    ├── .issues/{N}/ (committed)                                    Phase artifacts
    │   ├── 01-brief.md
    │   ├── 02-requirements.md
    │   ├── 03-architecture.md
    │   ├── 05-security-review.md
    │   └── 06-quality-report.md
    │
    ├── docs/adr/ADR-{n}-*.md (committed)                           si hay decisión arquitectural
    │
    ├── Heartbeat de sesión (.ahrena/workflow/sessions/<uuid>.json, gitignored)
    │
    └── ─ ─ ─ no confundir con ─ ─ ─
        Checkpoint (.checkpoint — gitignored, sesión)
```

- Body de la Issue, label de la Issue y label del PR son sincronizados por el owner en cada transición.
- El ADR se abre cuando el plan identifica una decisión arquitectural relevante (vive en `docs/adr/`, no en `.issues/`).
- El heartbeat de sesión (`codex-session-tracking`) registra qué sesión Claude Code opera en el plan ahora.
- El checkpoint NO está subordinado al plan; es artefacto paralelo de **sesión**, no de **task**.

### Plan vs `.checkpoint` — delimitación canónica

El plan cubre **task**: Objetivo, Alcance, Steps `[x]`, Decisiones cerradas, Riesgos, Verificación. Committed.
El checkpoint cubre **sesión**: Session focus, Active plans (punteros), Open threads, Notes. Gitignored.

| Contenido | Body de la Issue (plan canónico) | `.plans/{N}.md` (caché + scratch) | `.checkpoint` (sesión) |
|---|:---:|:---:|:---:|
| Steps `[x]` | ✅ | ✅ (espejado) | ❌ |
| Decisiones cerradas de la task | ✅ (o ADR) | ✅ (espejado) | ❌ |
| Riesgos de la task | ✅ | ✅ (espejado) | ❌ |
| Working notes / debugging diary | ❌ | ✅ (bloque `<!-- not-flushed -->`) | ❌ |
| Foco general de la ventana de trabajo | ❌ | ❌ | ✅ |
| Lista de planes activos en la sesión | ❌ | ❌ | ✅ |
| Threads paralelos que no se convirtieron en plan | ❌ | ❌ | ✅ |
| Scratchpad libre, links, recordatorios | ❌ | ❌ | ✅ |

Si el contenido se repite en ambos, hay superposición — el plan gana (committed). La superposición es PROHIBIDA por `lex-checkpoint` regla 5 y por `lex-agent-planning`.

---

## 9. Cadencia de load/flush (per ADR-002)

La sincronización entre el body de la Issue (canonical) y el caché local `.plans/{N}.md` ocurre en **3 disparadores canónicos** (per Open Question #3 de plan-046):

| Disparador | Operación | Quién dispara |
|---|---|---|
| Inicio de sesión / handoff entre agentes | `kata-load-plan-from-issue` | Athena, Argos, Janus (al comienzo de cada sesión de trabajo en un plan) |
| Transición de label `status:` en la Issue/PR | `kata-flush-plan-to-issue` | Eunomia, Athena, Argos, Janus (en el momento de la transición) |
| Step del plan marcado como concluido (`[ ]` → `[x]`) | `kata-flush-plan-to-issue` | Agente que concluye el Step |
| Fin de sesión (heartbeat concluye o agente sale) | `kata-flush-plan-to-issue` | `kata-session-heartbeat` en el shutdown |

Toggles intermedios, ediciones de scratch (bloques `<!-- not-flushed -->`) y working notes son **libres** — no disparan flush. La regla es: el body de la Issue debe reflejar el estado **estable** (entre transiciones y Steps), no el estado **transitorio** (durante el working).

### Flujo típico de una sesión de trabajo

```
1. Athena entra (recibe handoff de Eunomia):
   → kata-load-plan-from-issue {N}    (materializa .plans/{N}.md)
   → aplica label status: development en la Issue + PR
   → kata-flush-plan-to-issue {N}     (registra la transición)

2. Athena trabaja:
   → edita archivos
   → registra notas en .plans/{N}.md (bloques <!-- not-flushed -->)
   → marca Step [x] en el .plans/{N}.md
   → kata-flush-plan-to-issue {N}     (Step concluido)

3. Athena abre PR vía kata-pr-prepare:
   → Paso 5c: kata-flush-plan-to-issue {N}  (estado final pre-PR)
   → Paso 6: create_pull_request
   → Paso 6b: aplica status: to review en la Issue + PR
   → kata-flush-plan-to-issue {N}     (transición registrada)

4. Athena sale:
   → kata-session-heartbeat en el shutdown dispara
   → kata-flush-plan-to-issue {N}     (cleanup final)

5. Argos entra:
   → kata-load-plan-from-issue {N}    (refresh del caché local)
   → ...
```

### Detección de drift remoto (preflight)

`kata-flush-plan-to-issue` por default ejecuta preflight: lee el body actual de la Issue, compara con el último estado conocido, y bloquea si hay edición remota desconocida (otra sesión, edición vía UI de GitHub). Ofrece: (a) mostrar diff y abortar, (b) merge manual, (c) overwrite vía `force=true`. El heartbeat de sesión permite identificar la sesión concurrente.

---

## 10. Loop de revisión pendiente (estado `to review`)

Cuando Athena abre el PR, agenda 3 ciclos de 15 min vía `ScheduleWakeup`. En cada wake-up:

1. Consulta `gh pr view {N} --json reviewDecision,reviews` y `gh pr checks {N}`.
2. Si `reviewDecision == APPROVED` por humano → mueve a `to release` y sale del loop.
3. Si `reviewDecision == CHANGES_REQUESTED` → actualiza el plan con nota, hace ping al PR vía `gh pr comment`, mantiene en `to review`, sale del loop.
4. Si Argos publicó findings P0/P1 → mantiene en `to review` (espera a que el autor corrija); sale del loop y reagenda cuando Argos señalice nueva ronda.
5. De lo contrario (`REVIEW_REQUIRED` / `null`, sin aprobación humana) → cuenta ciclo; si < 3, reagenda 15 min; si == 3, dispara notificación vía MCP en `notifications.channels.pr_review_timeout` (per `codex-notifications`) y cierra el loop.

Argos opera el sub-ciclo `to review ↔ review` en paralelo, intercalado con la ventana de espera de Athena. Argos nunca mueve a `to release`; eso es exclusivo de Athena al detectar aprobación humana.

---

## 11. Buenas prácticas

1. **Escribir el plan antes de saber todo.** El objetivo es hacer visible la intención, no producir documentación perfecta. Un plan impreciso que evoluciona es mejor que ningún plan.
2. **Mantener etapas atómicas.** Cada etapa debe ser verificable: hecha o no hecha. Evitar etapas vagas como "ocuparse de la parte de events".
3. **Actualizar en tiempo real.** Marcar `[x]` a medida que cada etapa concluye, no al final de todo — y disparar `kata-flush-plan-to-issue` para persistir.
4. **Sincronizar label `status:` en Issue + PR.** Toda transición de owner toca la Issue y el PR. Saltar cualquiera produce drift que aparece en auditoría.
5. **No crear planes fantasma.** Si la tarea es cancelada antes de comenzar, aplicar `status: abandoned` en la Issue con comentario explicando — no eliminar la Issue.
6. **El plan canónico vive en GitHub.** No crear archivos `.claude/plans/*.md` como canónicos (modelo legado pre-ADR-002). El body de la Issue es canonical; `.plans/{N}.md` es caché regenerable; `.issues/{N}/` lleva los Phase artifacts.
7. **Working notes libres en `.plans/{N}.md`.** Usar bloques `<!-- not-flushed -->` para registrar decisiones en borrador, debugging notes y próximos pasos volátiles — esos bloques se filtran en el flush, así no contaminan el body canónico.

---

## Referencias

- ADR-002 — modelo de almacenamiento en tres capas (Issue body + `.plans/` + `.issues/`)
- `lex-agent-planning` — Ley correspondiente (HARD-GATE de `— → todo` + Tablas A y B)
- `lex-issue-status` — labels canónicos; split Eje A (dev) + Eje B (release)
- `lex-issue-type-verified` — verificación programática del Issue Type
- `lex-mcp` — preferencia MCP + fallback CLI
- `kata-plan-task` — procedimiento operacional (modo top-level de Eunomia); rellena body de la Issue
- `kata-create-subtasks` — descomposición de child Issue en subtasks (modo subtask de Eunomia)
- `kata-load-plan-from-issue` — materializa `.plans/{N}.md` del body canónico
- `kata-flush-plan-to-issue` — flushea `.plans/{N}.md` (filtrando scratch) al body
- `kata-session-heartbeat` — heartbeat de sesión Claude Code
- `codex-session-tracking` — manual de tracking de sesión
- `codex-notifications` — manual provider-agnóstico de envío vía MCP
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners de las transiciones
- `lex-checkpoint` — rastreo de estado de sesión (complementario)
- `lex-issue-driven` — flujo Issue-Driven de Athena
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners de las transiciones
