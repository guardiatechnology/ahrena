# Codex: Tracking de Sesión Claude Code

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Registro de la sesión Claude Code que opera en cada plan y de la traza de sesiones que tocó cada PR

## Visión General

Este Codex define el sistema de heartbeat que permite al framework rastrear qué sesión Claude Code está operando en cada plan y qué secuencia de sesiones produjo cada PR. Sin esto, el digest de planes de Eunomia (plan-044) no logra distinguir "plan en movimiento ahora" de "plan olvidado"; el body del PR pierde la auditoría del tiempo de implementación; y los handoffs entre sesiones se vuelven huecos inexplicables en el historial.

El contrato es simple: cada agente que toca un plan ejecuta `kata-session-heartbeat` en puntos significativos, escribiendo/actualizando `.ahrena/workflow/sessions/<session-id>.json`. La persistencia canónica va al body del PR (sección "Session Trace") vía `kata-pr-prepare`; el directorio local es runtime-only y gitignored.

## Contexto

- **Dominio:** rastreo operacional de sesiones Claude Code en el flujo Issue-Driven.
- **Público objetivo:** todo agente que opera en un plan (Eunomia en la creación, Athena en las transiciones, Argos en la revisión, Janus en la release).
- **Actualización:** cuando cambie el schema del heartbeat o cuando se agregue una nueva variable de entorno de Claude Code.

## Contenido

### 1. Variables de entorno de Claude Code

Claude Code expone tres variables estables en cada sesión. El agente lee y propaga:

| Variable | Contenido | Origen |
|---|---|---|
| `CLAUDE_CODE_SESSION_ID` | UUID estable de la sesión (ej.: `85846253-4edf-443d-b294-187ef287d1bb`) | Claude Code lo inyecta en el shell |
| `CLAUDE_CODE_ENTRYPOINT` | Donde corre la sesión: `claude-vscode`, `claude-cli`, `claude-desktop`, `claude-web` | Idem |
| `AI_AGENT` | Versión del agente (ej.: `claude-code_2-1-138_agent`) | Idem |

Cuando el agente corre fuera de Claude Code (CI, Cursor sin env), trata las variables como ausentes y el heartbeat se omite sin error — `kata-session-heartbeat` es idempotente en ese caso.

### 2. Schema del heartbeat file

Cada sesión escribe un archivo JSON en `.ahrena/workflow/sessions/<session-id>.json`:

```json
{
  "session_id": "85846253-4edf-443d-b294-187ef287d1bb",
  "entrypoint": "claude-vscode",
  "agent_version": "claude-code_2-1-138_agent",
  "plan_id": "043",
  "branch": "feat/90-workflow-status-review-loop",
  "cwd": "/Users/.../worktrees/90-workflow-status-review-loop",
  "started_at": "2026-05-11T12:30:00Z",
  "last_heartbeat": "2026-05-11T14:00:00Z",
  "last_activity": "kata-pr-prepare:step3",
  "role": "creator",
  "previous_session": null
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `session_id` | UUID string | Valor de `CLAUDE_CODE_SESSION_ID` |
| `entrypoint` | enum | Valor de `CLAUDE_CODE_ENTRYPOINT` |
| `agent_version` | string | Valor de `AI_AGENT` |
| `plan_id` | string `NNN` | Leído del front-matter del plan en uso |
| `branch` | string | `git rev-parse --abbrev-ref HEAD` en el worktree |
| `cwd` | string | Working directory actual |
| `started_at` | ISO 8601 | Primera escritura del heartbeat |
| `last_heartbeat` | ISO 8601 | Última actualización (sobrescrita en cada llamada) |
| `last_activity` | string | Nombre del step/kata/cry actual (formato `kata-name:stepN` o `cry-name`) |
| `role` | enum | `creator`, `executor`, `reviewer`, `releaser` (depende de quién escribe) |
| `previous_session` | UUID o null | En handoff, apunta a la sesión anterior |

### 3. Cadencia

Heartbeat actualizado:

- **Inicio**: cuando el agente entra al plan (Eunomia al crear; Athena al heredar; Argos al iniciar revisión; Janus al iniciar release).
- **En puntos significativos**: al completar cada Step del plan, al completar cada kata invocada, al cambiar de status.
- **Mínimo**: cada 5–10 minutos de actividad activa.
- **Stale threshold**: 30 min sin heartbeat → Eunomia lo considera offline en el digest. Configurable vía `session_tracking.stale_threshold_minutes`.

Idempotencia: llamar `kata-session-heartbeat` 100×/día es seguro — sobrescribe `last_heartbeat` y `last_activity` sin efecto secundario.

### 4. Limpieza

- Al mover el plan a `done` o `abandoned`: eliminar el heartbeat file de la sesión (ya no se necesita).
- Al reiniciar la sesión con el mismo `session_id` (el entrypoint detecta heartbeat preexistente): continuar del existente, no recrear.

### 5. Multi-sesión por plan (handoff)

Cuando una sesión cede el trabajo a otra (ej.: sesión A empezó, sesión B continuó):

1. La sesión B escribe un nuevo heartbeat con `previous_session: <UUID de la sesión A>`.
2. El heartbeat antiguo de A permanece hasta que se limpie al final del ciclo.
3. El digest de Eunomia muestra la cadena: "plan-043: sesión B (actual, heredó de A)".

### 6. Directorio gitignored

`.ahrena/workflow/sessions/` es runtime-only:

```gitignore
# .ahrena/workflow/sessions/ — runtime heartbeat dir (codex-session-tracking)
.ahrena/workflow/sessions/
```

El historial canónico de las sesiones que tocaron un trabajo persiste en el body del PR (sección "Session Trace"), no en el filesystem.

### 7. Session Trace en el body del PR

`kata-pr-prepare` construye la sección "Session Trace" agregando todos los heartbeat files cuyo `branch` coincide con la branch actual:

```markdown
## Session Trace

| Session | Entrypoint | Role | Started | Last Heartbeat |
|---|---|---|---|---|
| `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |
| `abc12345` | claude-cli | reviewer (Argos) | 2026-05-11T13:45Z | 2026-05-11T13:55Z |

- Plan(s): plan-043
- Worktree: `.worktrees/90-workflow-status-review-loop`
- Cumulative active time: ~1h30min
```

Cálculo de **cumulative active time**: suma de los intervalos `started_at → last_heartbeat` por sesión. Esta métrica es complementaria a `cry-pr-cost-stamp` (que mide tokens/USD); aquí mide tiempo de sesión real.

PRs sin `Session Trace`, cuando el branch tiene heartbeat files asociados, son rechazados en Gate 2 (per `lex-pr-quality`).

### 8. PRs sin agente (humano puro)

En hotfixes manuales o PRs hechos por humano sin agente Claude Code, la sección puede ser:

```markdown
## Session Trace

_(human-driven; no session trace)_
```

Aceptado en Gate 2.

## Restricciones

- **No persistir credenciales o datos sensibles** en el heartbeat file — `cwd`, `branch`, `plan_id`, IDs y timestamps son el límite.
- **No crear el directorio `.ahrena/workflow/sessions/` en commit** — siempre gitignored.
- **No confundir `previous_session` con merge de sesiones** — handoff es secuencial; no hay múltiples sesiones `running` simultáneamente en el mismo plan.

## Referencias

- `lex-agent-planning` — front-matter del plan referencia `claude_session` + `session_entrypoint`
- `lex-pr-quality` — exige sección "Session Trace" en el body del PR (regla introducida por plan-043)
- `kata-session-heartbeat` — procedimiento operacional canónico
- `kata-pr-prepare` — construye la sección "Session Trace" antes de abrir el PR
- `lex-directives` — claves `session_tracking.*` en `.ahrena/.directives`
- `codex-pr-cost-tracking` — métrica de costo (tokens/USD), complementaria a la métrica de tiempo aquí
