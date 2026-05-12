# Lexis: Planificación Obligatoria para Tareas de Agentes

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Toda tarea multi-etapa iniciada por cualquier agente o subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Los agentes que ejecutan sin planificación previa producen resultados parciales, dejan archivos en estados inconsistentes y obligan al usuario a reconstruir el contexto manualmente. Esta Lexis elimina ese patrón al exigir que todo agente registre su plan antes de ejecutar, haciendo que la intención, el alcance y la secuencia sean auditables por humanos y por otros agentes. Además, define un ciclo de vida unificado entre el plan, la Issue de GitHub y el PR — con owner explícito para cada transición — para eliminar drift y dar visibilidad a la "sala de espera" de la revisión.

Esta versión (per ADR-002) cambia el **medio de almacenamiento** del plan: el contenido canónico vive en el **body de la Issue** de GitHub; `.plans/{N}.md` es caché local de la IA (gitignored); `.issues/{N}/` guarda los Phase artifacts del flujo Issue-Driven (committed). El archivo de plan dedicado en `.claude/plans/*.md` deja de ser el canónico.

## Ley

> **Todo agente DEBE registrar un plan canónico en el **body de la Issue de GitHub** correspondiente ANTES de iniciar cualquier tarea que involucre 2 o más etapas, afecte múltiples archivos o produzca artefactos permanentes. El plan DEBE ser presentado al usuario para confirmación antes de que comience la ejecución. Iniciar ejecución multi-etapa sin un plan registrado y confirmado es PROHIBIDO. El `status:` del plan vive como **label canónica** en la Issue (y en el PR, a partir de `to review`); el enum unificado es `todo | development | to review | review | to release | release | done` (más el terminal alternativo `abandoned`); cada transición DEBE ser ejecutada por el owner declarado en esta Lex.**

## Alcance

- **Se aplica a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, cualquier AI agent o subagente que invoque katas, warriors o cries en el contexto Ahrena
- **Agentes vinculados:** todos, sin excepción de rol
- **Excepciones permitidas:** operaciones triviales de etapa única (editar un único archivo con instrucción directa, consulta de lectura pura, comando aislado sin efecto colateral permanente)

## Modelo de almacenamiento en tres capas (per ADR-002)

| Capa | Ubicación | Rol | Versionado |
|---|---|---|---|
| **Issue body** | `https://github.com/{owner}/{repo}/issues/{N}` | Canonical. Summary + Plan section con Objective, Steps, Risks, Dependencies, Open Questions | Audit log nativo de GitHub (timestamp + autor por edición) |
| **`.plans/{N}.md`** | Raíz del repo, gitignored | AI working memory + scratch. Superset del body de la Issue + secciones `<!-- not-flushed -->` | Caché local regenerable; `kata-load-plan-from-issue` materializa, `kata-flush-plan-to-issue` flushea |
| **`.issues/{N}/`** | Raíz del repo, committed | Phase artifacts del flujo Issue-Driven (`01-brief.md` … `06-quality-report.md`) | Git |

El path de `.plans/` es configurable vía `paths.plans` en `.ahrena/.directives` (default: `.plans/`). No confundir con el `paths.plans` legado que apuntaba a `.claude/plans/` — el nuevo default es `.plans/` en la raíz, agente-agnóstico.

## Schema del body de la Issue (plan canónico)

```markdown
## Summary

{2-4 frases describiendo el objetivo. Típicamente se hereda del template (feature-request "Objective" / simple-task "Why").}

## Plan

### Objective
{Por qué se está haciendo esta tarea — 1 a 3 frases.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{Planes, Issues o PRs de los cuales depende esta tarea; "None" si no hay.}

### Risks
{Riesgos conocidos y mitigaciones; "None identified" si no hay.}

### Open Questions
{Preguntas abiertas que requieren decisión antes/durante la ejecución; "None" si no hay.}
```

Schema del `.plans/{N}.md` (per Open Question #4 de plan-046): **superset** del body de la Issue. Lleva el body completo espejado + secciones locales marcadas:

```markdown
<!-- not-flushed -->
## Working notes
- decisión de debugging X a las 14:32
- error Y reproducido en test-Z

## Next actions
1. intentar enfoque A; si falla, B

## Scratch
cualquier texto libre que la IA quiera mantener como contexto local
<!-- /not-flushed -->
```

`kata-flush-plan-to-issue` filtra los bloques `<!-- not-flushed -->` antes de grabar en el body de la Issue.

## Ciclo de vida del plan

El ciclo opera sobre **dos ejes disjuntos** (per ADR-002 / plan-045 absorbido):

### Eje A — Dev cycle (Issue de feature/fix/chore/refactor)

```
todo → development → to review → review → done
                           ↘
                           abandoned (terminal alternativo, cualquier etapa)
```

- `todo` — plan creado, Issue abierta, branch remota vinculada, worktree listo.
- `development` — Athena delegó y la implementación está en curso.
- `to review` — PR abierto, esperando que el reviewer (humano o Argos) lo tome.
- `review` — Argos (o humano) está revisando activamente.
- `done` — PR mergeado; Issue cerrada vía `Closes #N`.
- `abandoned` — terminal alternativo; plan descartado.

### Eje B — Release cycle (Issue de release dedicada)

```
to release → release → done
                  ↘
                  abandoned (terminal alternativo, cualquier etapa)
```

- `to release` — release Issue creada por Janus; `Tracks: #N1, #N2, ...` listando los PRs mergeados desde el último tag.
- `release` — release en ejecución (`kata-release-prepare` corriendo; humano aprobó bump/changelog).
- `done` — tag empujada, `validate-tag.yml` pasó, Release publicada en GitHub.
- `abandoned` — release abortada antes del tag.

La mutex de labels es **intra-artefacto** (dentro de cada Issue/PR), no cross-artifact: una Issue lleva exactamente una label `status: <name>` a la vez. El HARD-GATE en `lex-issue-status` prohíbe aplicar labels del Eje B en Issue/PR de feature, y viceversa.

La carpeta `.issues/_legacy/` (histórico anterior a ADR-002) preserva planes en formato antiguo — **ya no es un estado** del enum.

## Owner de `— → todo`: warrior-eunomia

Todo plan (top-level o subtask) DEBE ser creado por `warrior-eunomia` vía `kata-plan-task` (top-level) o `kata-create-subtasks` (subtask, downstream de Athena Phase 4). Eunomia ejecuta los 5 pasos siguientes antes de marcar la label `status: todo` como definitiva:

1. Abrir la Issue correspondiente (per `lex-issue-first` y `lex-issue-quality`).
2. Verificar el Issue Type post-creación (per `lex-issue-type-verified`).
3. Crear la branch remota y vincularla a la Issue vía `gh issue develop {N} --base main --name {type}/{N}-{slug}` (registra la branch como "Development" en la sidebar de GitHub).
4. Crear el worktree per `lex-git-worktrees`.
5. **Rellenar el body de la Issue con el plan canónico** (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) vía MCP `update_issue` (GitHub MCP) — o fallback CLI `gh issue edit {N} --body-file <path>` (per `lex-mcp` regla 4). Sin el body relleno, el plan permanece en borrador — no puede ser presentado como `todo` al usuario.

**Fallback mientras Eunomia no esté shipada:** la responsabilidad recae en el agente de la sesión actual, siguiendo el mismo contrato — sin refactorización posterior cuando Eunomia entre en producción.

<HARD-GATE>
warrior-eunomia (o el agente de la sesión actuando como fallback mientras Eunomia
no esté shipada) MUST NOT aplicar la label `status: todo` en una Issue
sin satisfacer TODOS los 5 pasos canónicos:

  (a) Issue abierta per lex-issue-first y lex-issue-quality
      (template, label, Issue Type, assignee, Why/What/How)
  (b) Issue Type verificado per lex-issue-type-verified (entregado
      en plan-044; absorbido por plan-046). Mientras no se shipea,
      se satisface vía `gh api repos/{owner}/{repo}/issues/{N}` retornando
      `type` populado y compatible con el template — mismo contrato
  (c) Branch remota creada y vinculada a la Issue vía
      gh issue develop {N} --base main --name {type}/{N}-{slug}
  (d) Worktree creado per lex-git-worktrees en
      `.worktrees/{N}-{slug}/`
  (e) Body de la Issue rellenado con plan canónico (Summary +
      Plan section conteniendo Objective, Steps, Risks, Dependencies,
      Open Questions) vía MCP `update_issue` (preferido) o
      `gh issue edit {N} --body-file <path>` (fallback)

Esta regla se aplica a TODO plan (top-level o subtask), independientemente de:
  - tamaño percibido ("es solo un chore")
  - urgencia ("incendio en producción")
  - quién lo pidió ("el CEO lo solicitó")
  - confianza del equipo ("ya probamos mucho")

Excepción declarada: ninguna. Incluso en hotfix, los 5 pasos se ejecutan
en secuencia — Eunomia (o fallback) no salta el amarre
Issue↔branch↔worktree↔body.
</HARD-GATE>

## Owners de cada transición

### Tabla A — Dev cycle (Eunomia / Athena / Argos)

| Transición | Owner | Disparador |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente de la sesión) | Crea plan + abre Issue + `gh issue develop` + worktree + body rellenado |
| `todo → development` | `warrior-athena` | Phase 4 (delegación de implementación) |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR; flush previo del `.plans/{N}.md` vía `kata-flush-plan-to-issue` |
| `to review → review` | `warrior-argos` | Argos inicia ciclo de revisión automatizada |
| `review → to review` | `warrior-argos` | Argos termina el ciclo sin aprobar (changes-requested o awaiting-human) |
| `to review → done` | `warrior-athena` | Humano aprueba PR; merge cierra Issue vía `Closes #N` |
| `cualquier → abandoned` | creador u owner actual | Plan descartado |

### Tabla B — Release cycle (Janus)

| Transición | Owner | Disparador |
|---|---|---|
| `— → to release` | `warrior-janus` | Abre release Issue; popula `Tracks: #N1, #N2, ...` con los PRs mergeados desde el último tag |
| `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano de bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` concluye (tag empujada, `validate-tag.yml` pasa, Release creada); notificación vía MCP en `notifications.channels.release_notify` |
| `cualquier → abandoned` | `warrior-janus` | Release abortada antes del tag |

Cada owner DEBE:

- Aplicar la label `status: <name>` correspondiente en la Issue de GitHub (per `lex-issue-status`).
- Aplicar la label `status: <name>` correspondiente en el PR (a partir de `to review`).
- Disparar `kata-flush-plan-to-issue` si el caché local `.plans/{N}.md` está por delante del body de la Issue.

## Auditoría de cierre

Para audit post-merge, dos campos se derivan de APIs nativas de GitHub (sin front-matter dedicado en el plan):

| Campo lógico | Fuente canónica | Comando |
|---|---|---|
| `closed_at` | `Issue.closedAt` | `gh issue view {N} --json closedAt --jq .closedAt` |
| `merge_commit` | `PullRequest.mergeCommit.oid` | `gh pr view {PR} --json mergeCommit --jq .mergeCommit.oid` |

Para planes legados en `.issues/_legacy/` que mantienen YAML front-matter histórico (planes 043-045 y anteriores), `merge_commit:` y `closed_at:` son reconocidos como front-matter opcional aceptado — preserva el audit sin retrofit.

## Cadencia de load/flush (per ADR-002 §3)

La sincronización entre `.plans/{N}.md` y el body de la Issue ocurre en **3 disparadores canónicos** (no en cada toggle):

| Disparador | Operación |
|---|---|
| Inicio de sesión / handoff entre agentes | `kata-load-plan-from-issue` |
| Transición de label `status:` en la Issue/PR | `kata-flush-plan-to-issue` |
| Step del plan marcado como concluido (`[ ]` → `[x]`) | `kata-flush-plan-to-issue` |
| Fin de sesión (heartbeat concluye o Athena/Argos sale) | `kata-flush-plan-to-issue` |

Toggles intermedios, ediciones de scratch (`<!-- not-flushed -->`) y working notes son **libres** — no disparan flush. Documentación operacional en `codex-agent-planning` §9.

## Relación con otros artefactos

- **Issue GitHub:** lleva el plan canónico en el body; la label `status: <name>` es la única fuente de verdad para el estado.
- **PR:** a partir de `to review`, el PR lleva la label `status: <name>` correspondiente, actualizada por Athena/Argos/Janus conforme avanza el estado. Sync de la label es responsabilidad del owner de la transición.
- **`.plans/{N}.md`:** caché local regenerable; nunca commiteado; reconstruido por `kata-load-plan-from-issue` en fresh clone.
- **`.issues/{N}/`:** committed; recibe Phase artifacts del flujo Issue-Driven (per `lex-issue-driven`).
- **Checkpoint (`.checkpoint`):** el plan cubre **task** (Steps, Decisiones, Riesgos en el body de la Issue); el checkpoint cubre **sesión** (foco de la ventana, hand-off entre planes, threads paralelos). La superposición es PROHIBIDA — ver `lex-checkpoint` regla 5.
- **ADR:** cuando un plan identifica una decisión arquitectural relevante, un ADR DEBE ser abierto conforme `lex-issue-driven`.
- **Heartbeat de sesión:** la sesión Claude Code que opera en el plan se registra en `.ahrena/workflow/sessions/<session-id>.json` (per `codex-session-tracking`); no vive en el body de la Issue.

### Plan (body de la Issue) vs `.plans/` vs `.checkpoint` — qué va dónde

| Contenido | Vive en |
|---|---|
| Objective, Steps `[x]`, Risks, Dependencies, Open Questions | Body de la Issue (canonical) |
| Decisiones arquitecturales relevantes | ADR en `docs/adr/` (referenciado por el plan) |
| Working notes, debugging diary, scratch | `.plans/{N}.md` en bloques `<!-- not-flushed -->` |
| Foco general de la ventana de trabajo (Session focus) | `.checkpoint` — gitignored |
| Punteros a múltiples planes activos (Active plans) | `.checkpoint` — gitignored |
| Threads paralelos que no se convirtieron en plan (Open threads) | `.checkpoint` — gitignored |

En caso de duda: el contenido estructural va al body de la Issue; el contenido volátil a `.plans/{N}.md` en bloque not-flushed; el foco de la sesión al `.checkpoint`.

## Ejemplos

### Correcto

```
Tarea: migrar almacenamiento del plan al modelo Issue-as-plan
→ Eunomia (fallback: agente de la sesión) abre Issue #96
   (template feature-request, Issue Type Feature, labels)
→ Eunomia verifica type vía gh api (per lex-issue-type-verified)
→ Eunomia crea branch vía gh issue develop 96 --base main
   --name feat/96-issue-as-plan-and-issues-folder
→ Eunomia crea worktree en .worktrees/96-issue-as-plan-and-issues-folder/
→ Eunomia rellena body de la Issue #96 con Summary + Plan section
   (Objective, Steps, Risks, Dependencies, Open Questions)
→ Eunomia aplica label `status: todo` en la Issue
→ Athena asume Phase 4: aplica `status: development`
→ Athena abre PR; aplica `status: to review` en la Issue + PR;
   dispara kata-flush-plan-to-issue
→ Argos inicia revisión: `status: review`
→ Argos termina sin aprobar: `status: to review` (humano cobrado en 3×15min)
→ Humano aprueba; merge cierra Issue vía Closes #N: `status: done`

Release cycle (separado):
→ Janus abre release Issue (e.g. #100); Tracks: #93, #96, #101
→ Janus aplica `status: to release` en la release Issue
→ Janus inicia kata-release-prepare: `status: release`
→ Janus concluye kata-release-publish: `status: done`
```

### Incorrecto

```
Tarea: implementar feature X
→ Agente crea branch directo vía git checkout -b sin abrir Issue
→ ❌ Viola lex-issue-first; sin Issue, el plan no puede ser registrado

→ Agente aplica label `status: todo` en la Issue sin rellenar el body
→ ❌ Viola HARD-GATE precondition (e): el body necesita llevar
   Summary + Plan section antes de status: todo definitivo

→ Agente crea `.claude/plans/plan-NNN-*.md` como canónico
→ ❌ Modelo legado pre-ADR-002. El plan canónico vive en el body de la Issue;
   `.plans/{N}.md` es caché local regenerable, no fuente de verdad

→ Agente aplica `status: to release` en Issue de feature
→ ❌ Viola la mutex intra-artefacto de lex-issue-status: `to release`
   pertenece al Eje B (release Issue), prohibido en el Eje A
```

## Validación Automatizada

- **Herramienta:** verificación por el agente antes de cualquier ejecución multi-etapa; `kata-plan-task` como punto de entrada canónico; la revisión de PR confirma que la label `status:*` de la Issue y la label `status:*` del PR están alineadas, y que el body de la Issue lleva Summary + Plan section.
- **Momento:** antes de cualquier ejecución de tarea multi-etapa — sin excepción; y en cada transición de estado.
- **Métrica:** 0 tareas multi-etapa ejecutadas sin body de Issue rellenado; 0 PRs mergeados con `status:` divergente entre Issue y PR; 100% de las transiciones ejecutadas por el owner declarado; 100% de las Issues de release con `Tracks:` listando los PRs mergeados desde el último tag.

## Referencias

- ADR-002 — modelo de almacenamiento en tres capas
- `lex-issue-status` — labels canónicas de status; split Tabla A (dev) / Tabla B (release)
- `lex-issue-type-verified` — verificación programática del Issue Type post-creación
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — preconditions del paso `— → todo`
- `lex-mcp` — preferencia MCP + fallback CLI para `gh issue edit`
- `lex-checkpoint` — rastreo de estado de sesión (complementario)
- `lex-issue-driven` — flujo Issue-Driven; Phase artifacts en `.issues/{N}/`
- `codex-agent-planning` — manual operacional del modelo de 3 capas (load → edit → flush)
- `kata-plan-task` — procedimiento operacional para crear planes (rellena body de la Issue)
- `kata-load-plan-from-issue` — materializa `.plans/{N}.md` a partir del body de la Issue
- `kata-flush-plan-to-issue` — flushea `.plans/{N}.md` (filtrando `<!-- not-flushed -->`) al body de la Issue
- `kata-create-subtasks` — descomposición de child Issue en subtasks
- `kata-session-heartbeat` — actualización del heartbeat de sesión
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners de las transiciones
