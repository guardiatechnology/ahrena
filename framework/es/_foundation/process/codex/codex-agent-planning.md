# Codex: Planificación de Tareas de Agentes

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Creación, mantenimiento y ciclo de vida de planes de tareas de agentes en el contexto de Ahrena

## Visión General

Este Codex es el manual canónico de planificación de tareas de agentes. Complementa `lex-agent-planning` (la Ley) con plantillas, ejemplos de relleno, reglas de numeración, buenas prácticas, owners de cada transición y orientación para casos límite. Todo agente que cree o mantenga planes DEBE consultar este Codex.

## Contexto

- **Dominio:** disciplina de ejecución de tareas por agentes de IA
- **Público objetivo:** todos los agentes (Claude, Cursor, warriors, katas) y revisores humanos
- **Actualización:** cuando la plantilla, el enum de status o la tabla de owners cambien (se recomienda ADR para cambios estructurales)

---

## 1. Resolución del Path de Planes

El agente resuelve el directorio de planes en el siguiente orden:

```
1. Leer .ahrena/.directives
2. Si paths.plans existe → usar ese valor (ej.: ".plans/")
3. En caso contrario → usar predeterminado por agente:
   - Claude Code (CLI, VSCode, Desktop, claude.ai) → .claude/plans/
   - Cursor                                         → .cursor/plans/
   - Agente desconocido                             → .plans/
```

Ejemplo de override en el proyecto:
```yaml
# .ahrena/.directives
paths:
  root: ".ahrena/"
  plans: ".plans/"    # override: todos los agentes usan .plans/
```

Subcarpetas por estado de filesystem (no por estado del enum):

- `{plans}/todo/` — planes con `status: todo` esperando inicio (antes `pending/`)
- `{plans}/archived/` — planes con `status: done` o `abandoned` después de mergear el PR correspondiente

La carpeta de filesystem es convención de organización. El estado canónico vive en el front-matter (`status:`).

---

## 2. Convención de Nombre de Archivo

```
plan-{NNN}-{slug}.md
```

| Campo | Regla |
|---|---|
| `{NNN}` | Número secuencial de 3 dígitos con ceros (001, 002, …). Incrementar desde el mayor existente en el directorio. Sin saltos cuando sea posible; si hay un salto (plan abandonado), no reutilizar el número |
| `{slug}` | kebab-case, máximo 60 caracteres, resumen de la tarea |

Ejemplos:
- `plan-001-complete-feature-design-docs.md`
- `plan-002-create-warrior-hecate.md`
- `plan-090-workflow-status-and-review-loop.md`

---

## 3. Plantilla Completa del Plan

```markdown
---
plan_id: "043"
title: "workflow-status-and-review-loop"
status: todo
agent: claude
issue: "guardiatechnology/ahrena#90"
branch: "feat/90-workflow-status-review-loop"
worktree: ".worktrees/90-workflow-status-review-loop"
claude_session: "85846253"            # opcional; lo completa kata-session-heartbeat
session_entrypoint: "claude-vscode"
created_at: "2026-05-10T00:00:00Z"
updated_at: "2026-05-11T15:30:00Z"
---

# Plan: Workflow status unificado entre plan e Issue

## Objetivo

Alinear el ciclo de vida del plan y del Issue de GitHub a un único enum de status
(todo → development → to review → review → to release → release → done),
con owner explícito para cada transición y notificaciones provider-agnósticas
vía MCP configurado en .ahrena/.directives.

## Alcance

Archivos a modificar:
- framework/{pt-BR,es,en}/_foundation/process/lexis/lex-agent-planning.md
- framework/{pt-BR,es,en}/_foundation/process/codex/codex-agent-planning.md
- framework/{pt-BR,es,en}/_foundation/contributing/lexis/lex-issue-status.md (nuevo)
- framework/{pt-BR,es,en}/engineering/workflow/warriors/warrior-athena.md
- framework/{pt-BR,es,en}/engineering/quality/warriors/warrior-argos.md
- (...)

## Pasos

- [x] 1. Issue + branch + worktree (Eunomia o fallback)
- [x] 2. ADR-001 (MADR simplificado)
- [x] 3. lex-agent-planning (3 idiomas)
- [ ] 4. codex-agent-planning (3 idiomas)
- [ ] 5. lex-issue-status nuevo (3 idiomas)
- (...)

## Dependencias

- plan-027 (Janus) — merged
- plan-042 (make mcp-enable) — merged
- plan-044 (Eunomia) — depende de este
- plan-045 (Janus pointer/wiring) — depende de este

## Riesgos

- Renombrar carpeta pending/ → todo/ exige grep cruzado por referencias
- Loop 3×15min puede ser corto fuera de horario laboral — mitigar vía .directives
- Notificaciones vía MCP se vuelven ruido si muchos PRs quedan parados — mitigar con 1 disparo en el 3er ciclo
```

---

## 4. Estados del Ciclo de Vida (enum unificado)

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, cualquier etapa)
```

| Status | Cuándo usar | Owner que transiciona |
|---|---|---|
| `todo` | Plan creado, Issue abierta, branch remota vinculada, worktree listo, aún no comenzó | Quien crea: `warrior-eunomia` (fallback: agente de la sesión) |
| `development` | Implementación en curso (Athena Phase 4) | `warrior-athena` |
| `to review` | PR abierto, esperando reviewer | `warrior-athena` (entrada); `warrior-argos` (retorno desde `review`) |
| `review` | Argos o humano revisando activamente | `warrior-argos` (entrada y salida) |
| `to release` | Review aprobado, esperando que release inicie | `warrior-athena` (detecta `APPROVED`) |
| `release` | Release en ejecución (tag/build/deploy) | `warrior-janus` |
| `done` | Release concluida, PR mergeado, ciclo cerrado | `warrior-janus` |
| `abandoned` | Plan descartado (cualquier etapa) | Creador u owner actual |

**Filesystem ≠ estado:** mover el archivo a `archived/` es convención de organización tras el merge. El estado canónico permanece en el front-matter.

---

## 5. Owners de Cada Transición (vista de flujo)

```
Eunomia: — ──→ todo
                 │
                 ▼
Athena:  todo ──→ development ──→ to review
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ to release  (humano aprueba)
                                       │
                                       ▼
Janus:           to release ──→ release ──→ done
                                       │
                  cualquier ──→ abandoned (terminal alternativo)
```

Cada owner actualiza simultáneamente:

1. `status:` en el front-matter del plan.
2. Label `status: <name>` en el Issue de GitHub (per `lex-issue-status`).
3. Label `status: <name>` en el PR (a partir de `to review`).

---

## 6. Owner del `— → todo`: 5 pasos canónicos

Eunomia (o fallback) ejecuta en secuencia antes de marcar `status: todo`:

| Paso | Acción | Lex de referencia |
|---|---|---|
| 1 | Abrir Issue (template, label, type, assignee, Why/What/How) | `lex-issue-first`, `lex-issue-quality` |
| 2 | Verificar Issue Type post-creación | `lex-issue-type-verified` |
| 3 | Crear branch remota y vincular al Issue: `gh issue develop {N} --base main --name {type}/{N}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 4 | Crear worktree en `.worktrees/{N}-{slug}/` | `lex-git-worktrees` |
| 5 | Actualizar front-matter del plan: `issue:`, `branch:`, `worktree:` | `lex-agent-planning` |

La falla en cualquier paso deja el plan en borrador (no puede presentarse como `todo`). Per HARD-GATE en `lex-agent-planning`, incluso en hotfix los 5 pasos son obligatorios.

---

## 7. Cuándo se Requiere un Plan (y Cuándo No)

### Obligatorio

- Tarea con 2+ pasos encadenados
- Cualquier operación que toque 2+ archivos
- Toda invocación de warrior o cry (por definición de múltiples pasos)
- Cualquier tarea que produzca artefactos permanentes (archivos, commits, PRs, publicaciones)

### No obligatorio (paso único trivial)

- Editar un único archivo con instrucción directa y precisa
- Leer/consultar archivos sin escritura
- Ejecutar un único comando aislado sin efecto secundario permanente
- Responder una pregunta factual

### Zona gris — usar plan por precaución

- Tarea aparentemente simple que puede ramificarse (ej.: "arreglar el bug" sin conocer el alcance)
- Operación irreversible aunque sea de un solo paso (ej.: eliminar archivos)

---

## 8. Relación Entre Planes y Otros Artefactos

```
Issue de GitHub (label: status: <name>)
    │
    ├── PR (label: status: <name>, a partir de "to review")
    │
    └── Plan (status: <name> en el front-matter, committed)
            ├── ADR (si hay decisión arquitectónica relevante)
            ├── Heartbeat de sesión (.ahrena/workflow/sessions/<uuid>.json, gitignored)
            └── ─ ─ ─ no confundir con ─ ─ ─
                Checkpoint (.checkpoint — gitignored, sesión)
```

- Issue, plan y PR cargan el **mismo** `status:` en cualquier instante.
- Se abre ADR cuando el plan identifica una decisión arquitectónica relevante.
- Heartbeat de sesión (`codex-session-tracking`) registra qué sesión Claude Code opera en el plan ahora.
- Checkpoint NO está subordinado al plan; es artefacto paralelo de **sesión**, no de **task**.

### Plan vs `.checkpoint` — delimitación canónica

Plan cubre **task**: Objetivo, Alcance, Steps `[x]`, Decisiones cerradas, Riesgos, Verificación. Committed.
Checkpoint cubre **sesión**: Session focus, Active plans (punteros), Open threads, Notes. Gitignored.

| Contenido | Plan | Checkpoint |
|---|:---:|:---:|
| Steps `[x]` | ✅ | ❌ |
| Decisiones cerradas de la task | ✅ | ❌ |
| Riesgos de la task | ✅ | ❌ |
| Artifacts produced | ✅ | ❌ |
| Foco general de la ventana de trabajo | ❌ | ✅ |
| Lista de planes activos en la sesión | ❌ | ✅ |
| Hilos paralelos que no se convirtieron en plan | ❌ | ✅ |
| Scratchpad libre, enlaces, recordatorios | ❌ | ✅ |

Si el contenido se repite en ambos, hay superposición — el plan vence (committed). La superposición está PROHIBIDA por `lex-checkpoint` regla 5 y por `lex-agent-planning`.

---

## 9. Loop de Revisión Pendiente (estado `to review`)

Cuando Athena abre el PR, agenda 3 ciclos de 15 min vía `ScheduleWakeup`. En cada wake-up:

1. Consulta `gh pr view {N} --json reviewDecision,reviews` y `gh pr checks {N}`.
2. Si `reviewDecision == APPROVED` por humano → mueve a `to release` y sale del loop.
3. Si `reviewDecision == CHANGES_REQUESTED` → actualiza plan con nota, hace ping en el PR vía `gh pr comment`, mantiene en `to review`, sale del loop.
4. Si Argos publicó findings P0/P1 → mantiene en `to review` (espera al autor corregir); sale del loop y reagenda cuando Argos señale nueva ronda.
5. Caso contrario (`REVIEW_REQUIRED` / `null`, sin aprobación humana) → cuenta ciclo; si < 3, reagenda 15 min; si == 3, dispara notificación vía MCP en `notifications.channels.pr_review_timeout` (per `codex-notifications`) y cierra el loop.

Argos opera el sub-ciclo `to review ↔ review` en paralelo, intercalado con la ventana de espera de Athena. Argos nunca mueve a `to release`; eso es exclusivo de Athena al detectar aprobación humana.

---

## 10. Buenas Prácticas

1. **Escribir el plan antes de saberlo todo.** El objetivo es hacer visible la intención, no producir documentación perfecta. Un plan impreciso que evoluciona es mejor que ningún plan.
2. **Mantener pasos atómicos.** Cada paso debe ser verificable: hecho o no hecho. Evitar pasos vagos como "encargarse de la parte de eventos".
3. **Actualizar en tiempo real.** Marcar `[x]` a medida que se completa cada paso, no al final de todo.
4. **Sincronizar `status:` en tres lugares.** Toda transición de owner toca plan + Issue + PR. Saltar cualquiera produce drift que aparece en auditoría.
5. **Sin planes fantasma.** Si la tarea se cancela antes de comenzar, marcar `abandoned` con motivo — no eliminar el archivo.
6. **Commitear el plan.** El plan es parte del trabajo; debe ir en el mismo PR que los artefactos que describe.

---

## Referencias

- `lex-agent-planning` — Ley correspondiente
- `lex-issue-status` — labels canónicos de status en Issue/PR
- `lex-issue-type-verified` — verificación programática del Issue Type
- `kata-plan-task` — procedimiento operacional (modo top-level de Eunomia)
- `kata-create-subtasks` — descomposición de child Issue en subtasks (modo subtask de Eunomia)
- `kata-session-heartbeat` — heartbeat de sesión Claude Code
- `codex-session-tracking` — manual de tracking de sesión
- `codex-notifications` — manual provider-agnóstico de envío vía MCP
- `lex-checkpoint` — seguimiento del estado de sesión (complementario)
- `lex-issue-driven` — flujo Issue-Driven de Athena
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners de las transiciones
