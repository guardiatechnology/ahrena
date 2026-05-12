# Lexis: Planificación Obligatoria para Tareas de Agentes

> **Prefijo:** `lex-` | **Tipo:** Ley Inviolable | **Alcance:** Toda tarea de múltiples pasos iniciada por cualquier agente o subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Los agentes que ejecutan sin planificación previa producen resultados parciales, dejan archivos en estados inconsistentes y obligan al usuario a reconstruir el contexto manualmente. Esta Lexis elimina ese patrón exigiendo que todo agente documente su plan antes de ejecutar, haciendo que la intención, el alcance y la secuencia sean auditables por humanos y por otros agentes. Además, define un ciclo de vida unificado entre plan, Issue de GitHub y PR — con owner explícito para cada transición — para eliminar drift y dar visibilidad a la "sala de espera" de la revisión.

## Ley

> **Todo agente DEBE crear un documento de plan en `./{agent_dir}/plans/plan-{NNN}-{slug}.md` (o en el path definido en `paths.plans` de `.ahrena/.directives`) ANTES de iniciar cualquier tarea que involucre 2 o más pasos, afecte múltiples archivos o produzca artefactos permanentes. El plan DEBE ser presentado al usuario para confirmación antes de que comience la ejecución. Iniciar ejecución de múltiples pasos sin un plan documentado y confirmado está PROHIBIDO. El `status:` del plan DEBE pertenecer al enum unificado `todo | development | to review | review | to release | release | done` (más el terminal alternativo `abandoned`); cada transición DEBE ser ejecutada por el owner declarado en este Lex.**

## Cobertura

- **Aplica a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, cualquier agente o subagente de IA que invoque katas, warriors o cries en el contexto de Ahrena
- **Agentes vinculados:** todos, sin excepción por rol
- **Excepciones permitidas:** operaciones triviales de un solo paso (editar un único archivo con instrucción directa, consultas de solo lectura, comandos aislados sin efecto secundario permanente)

## Resolución del Path del Plan (precedencia)

| Prioridad | Fuente | Valor |
|:---:|---|---|
| 1 | `paths.plans` en `.ahrena/.directives` | Override de proyecto — reemplaza todo lo demás |
| 2 | Predeterminado por agente | `.claude/plans/` para Claude Code; `.cursor/plans/` para Cursor; `.plans/` para agente desconocido |

Nombre del archivo: `plan-{NNN}-{slug}.md` donde `{NNN}` es secuencial por directorio (001, 002, …), sin saltos.

## Estructura Mínima Obligatoria del Plan

```markdown
---
plan_id: "{NNN}"
title: "{slug}"
status: todo | development | to review | review | to release | release | done | abandoned
agent: claude | cursor | unknown
issue: "{owner/repo#N}"
branch: "{type}/{N}-{slug}"
worktree: ".worktrees/{N}-{slug}"
claude_session: "{short-uuid}"        # opcional; lo completa kata-session-heartbeat
session_entrypoint: "claude-vscode | claude-cli | claude-desktop | claude-web"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Plan: {título legible}

## Objetivo
{Por qué se está realizando esta tarea — 1 a 3 frases}

## Alcance
{Qué se modificará: archivos, sistemas, artefactos afectados}

## Pasos
- [ ] Paso 1
- [ ] Paso 2
...

## Dependencias
{Planes o issues de los que depende esta tarea; "Ninguna" si no hay}

## Riesgos
{Riesgos conocidos y mitigaciones; "Ninguno identificado" si no hay}
```

## Ciclo de Vida del Plan

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, cualquier etapa)
```

Semántica de cada estado:

- `todo` — plan creado, Issue abierta, branch remota vinculada, worktree listo, aún no comenzó.
- `development` — Athena delegó y la implementación está en curso.
- `to review` — PR abierto, esperando que un reviewer (humano o Argos) lo tome.
- `review` — Argos (o humano) está revisando activamente.
- `to release` — review aprobado, esperando que el agente de release inicie.
- `release` — release en ejecución (tag/build/deploy).
- `done` — release completa, PR mergeado, ciclo cerrado.
- `abandoned` — terminal alternativo (cualquier etapa → `abandoned`); plan descartado.

La carpeta `archived/` permanece como convención de organización del filesystem para planes post-merge — **ya no es un estado** del enum.

## Owner del `— → todo`: warrior-eunomia

Todo plan (top-level o subtask) DEBE ser creado por `warrior-eunomia` vía `kata-plan-task` (top-level) o `kata-create-subtasks` (subtask, downstream de Athena Phase 4). Eunomia ejecuta los 5 pasos a continuación antes de marcar `status: todo` como definitivo:

1. Abrir el Issue correspondiente (per `lex-issue-first` y `lex-issue-quality`).
2. Verificar Issue Type post-creación (per `lex-issue-type-verified`).
3. Crear la branch remota y vincularla al Issue vía `gh issue develop {N} --base main --name {type}/{N}-{slug}` (registra la branch como "Development" en la sidebar de GitHub).
4. Crear el worktree per `lex-git-worktrees`.
5. Registrar el número del Issue, el nombre de la branch y el path del worktree en el front-matter del plan (`issue:`, `branch:`, `worktree:`). Sin ese amarre, el plan permanece en borrador — no puede presentarse como `todo` al usuario.

**Fallback mientras Eunomia no esté shipada:** la responsabilidad recae en el agente de la sesión actual, siguiendo el mismo contrato — sin refactorización posterior cuando Eunomia entre en producción.

<HARD-GATE>
warrior-eunomia (o el agente de la sesión actuando como fallback mientras
Eunomia no esté shipada) MUST NOT marcar `status: todo` como definitivo
en un plan sin satisfacer TODOS los 5 pasos canónicos:

  (a) Issue abierto per lex-issue-first y lex-issue-quality
      (template, label, Issue Type, assignee, Why/What/How)
  (b) Issue Type verificado per lex-issue-type-verified (entregado
      en plan-044). Mientras plan-044 no se publique, satisfacer vía
      `gh api repos/{owner}/{repo}/issues/{N}` retornando `type`
      poblado y compatible con el template — mismo contrato, sin el
      Lex dedicado todavía
  (c) Branch remota creada y vinculada al Issue vía
      gh issue develop {N} --base main --name {type}/{N}-{slug}
  (d) Worktree creado per lex-git-worktrees en
      `.worktrees/{N}-{slug}/`
  (e) Front-matter del plan actualizado con issue, branch y worktree

Esta regla aplica a TODO plan (top-level o subtask), independientemente de:
  - tamaño percibido ("es solo un chore")
  - urgencia ("incendio en producción")
  - quién pidió ("el CEO lo solicitó")
  - confianza del equipo ("ya probamos mucho")

Excepción declarada: ninguna. Incluso en hotfix, los 5 pasos se ejecutan
en secuencia — Eunomia (o fallback) no salta el amarre Issue↔branch↔worktree.
</HARD-GATE>

## Owners de Cada Transición

| Transición | Owner | Disparador |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente de la sesión) | Crea plan + abre Issue + `gh issue develop` + worktree |
| `todo → development` | `warrior-athena` | Phase 4 (delegación de implementación) |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR |
| `to review → review` | `warrior-argos` | Argos inicia ciclo de revisión automatizada |
| `review → to review` | `warrior-argos` | Argos termina ciclo sin aprobar (changes-requested o awaiting-human) |
| `to review → to release` | `warrior-athena` | Humano aprueba PR (loop de wake-up detecta `APPROVED`) |
| `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano de bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` concluye (tag empujada, `validate-tag.yml` pasa, Release creada); notificación vía MCP en `notifications.channels.release_notify` |
| `cualquier → abandoned` | creador u owner actual | Plan descartado |

Cada owner DEBE:

- Actualizar el `status:` en el front-matter del plan.
- Aplicar la label `status: <name>` correspondiente en el Issue de GitHub (per `lex-issue-status`).
- Aplicar la label `status: <name>` correspondiente en el PR (a partir de `to review`).

## Relación con Otros Artefactos

- **Issue de GitHub:** un plan referencia un issue; un issue puede tener múltiples planes (ej.: diseño, implementación, pruebas). La label `status: <name>` en el Issue espeja el `status:` del plan.
- **PR:** a partir de `to review`, el PR carga la label `status: <name>` correspondiente, actualizada por Athena/Argos/Janus conforme el estado avanza.
- **Checkpoint (`.checkpoint`):** el plan cubre **task** (committed, con Steps, Decisiones, Riesgos); el checkpoint cubre **sesión** (foco de la ventana, hand-off entre planes, hilos paralelos, scratchpad). La superposición está PROHIBIDA — ver `lex-checkpoint` regla 5
- **ADR:** cuando un plan identifica una decisión arquitectónica relevante, DEBE abrirse un ADR conforme a `lex-issue-driven`
- **Heartbeat de sesión:** el front-matter del plan referencia la sesión Claude Code que opera en el momento (`claude_session`, `session_entrypoint`); detalles en `codex-session-tracking`.

### Plan vs `.checkpoint` — qué va dónde

| Contenido | Vive en |
|---|---|
| Objetivo, Steps `[x]`, Status (del enum unificado), Decisiones cerradas, Riesgos, Verificación | Plan — committed |
| Activity, Progress detallado, Artifacts produced, Next steps de una task | Plan — committed |
| Foco general de la ventana de trabajo (Session focus) | `.checkpoint` — gitignored |
| Punteros para múltiples planes activos (Active plans) | `.checkpoint` — gitignored |
| Hilos paralelos que no se convirtieron en plan (Open threads) | `.checkpoint` — gitignored |
| Scratchpad libre, enlaces, recordatorios (Notes) | `.checkpoint` — gitignored |

En caso de duda, el contenido va al plan. El plan vence en durabilidad (committed) y en alcance (cubre task; el checkpoint cubre sesión).

## Ejemplos

### Correcto

```
Tarea: implementar status unificado entre plan e Issue
→ Eunomia abre Issue #90 (template feature-request, Issue Type Feature, labels)
→ Eunomia verifica type vía gh api (per lex-issue-type-verified)
→ Eunomia crea branch vía gh issue develop 90 --base main --name feat/90-...
→ Eunomia crea worktree en .worktrees/90-.../
→ Eunomia escribe plan-043 con status: todo, issue, branch, worktree en el front-matter
→ Athena asume Phase 4: status → development
→ Athena abre PR: status → to review
→ Argos inicia revisión: status → review
→ Argos termina sin cambios: status → to review (humano cobrado en 3×15min)
→ Humano aprueba: status → to release
→ Janus inicia release: status → release
→ Janus concluye: status → done
```

### Incorrecto

```
Tarea: implementar feature X
→ Agente crea branch directo vía git checkout -b sin abrir Issue
→ ❌ Viola lex-issue-first; sin Issue, el plan no puede marcarse todo
→ Agente marca status: todo en el plan sin branch remota linkada al Issue
→ ❌ Viola el HARD-GATE de este Lex (precondición (c) no satisfecha)
```

## Validación Automatizada

- **Herramienta:** verificación por el agente antes de cualquier ejecución de múltiples pasos; `kata-plan-task` como punto de entrada canónico; revisión de PR confirma que el `status:` del plan, la label `status:*` del Issue y la label `status:*` del PR están alineados.
- **Momento:** antes de cualquier ejecución de tarea de múltiples pasos — sin excepción; y en cada transición de estado.
- **Métrica:** 0 tareas de múltiples pasos ejecutadas sin plan documentado en `{agent_dir}/plans/`; 0 PRs mergeados con `status:` divergente entre plan, Issue y PR; 100% de las transiciones ejecutadas por el owner declarado.

## Referencias

- `codex-agent-planning` — manual con plantilla completa, ejemplos y buenas prácticas
- `kata-plan-task` — procedimiento operacional para crear y mantener planes (modo top-level de Eunomia)
- `kata-create-subtasks` — procedimiento de descomposición de child Issue en subtasks (modo subtask de Eunomia)
- `kata-session-heartbeat` — actualización del heartbeat de sesión
- `lex-issue-status` — labels canónicos de status en Issue/PR
- `lex-issue-type-verified` — verificación programática del Issue Type post-creación
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — preconditions del paso `— → todo`
- `lex-checkpoint` — seguimiento del estado de sesión (complementario)
- `lex-issue-driven` — flujo de desarrollo dirigido por issues
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners de las transiciones
