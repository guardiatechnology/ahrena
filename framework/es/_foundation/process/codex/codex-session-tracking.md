# Codex: Tracking de Sesión Claude Code

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Registro de la sesión Claude Code que opera en cada plan y de la traza de sesiones que tocó cada PR

## Visión General

Este Codex define el sistema de heartbeat que permite al framework rastrear qué sesión Claude Code está operando en cada plan y qué secuencia de sesiones produjo cada PR. Sin esto, el digest de planes de Eunomia no logra distinguir "plan en movimiento ahora" de "plan olvidado"; el body del PR pierde la auditoría del tiempo de implementación; y los handoffs entre sesiones se vuelven huecos inexplicables en el historial.

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
3. El digest de Eunomia muestra la cadena: "sesión B (actual, heredó de A)".

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

### 9. Tags de sesión

Las sesiones PUEDEN cargar hasta 3 tags cortas escritas en el heartbeat bajo el objeto `tags`. Las tags exponen la intención de la sesión (kind + topics libres) al humano a través de la statusline de Claude Code, del sidebar de la extensión ahrena-vscode y del digest de planes de Eunomia.

**Formato en el heartbeat:**

```json
"tags": {
  "kind": "tech-task",
  "topics": ["session-tracking", "framework"]
}
```

**Schema:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|:---:|---|
| `tags.kind` | string | Cuando `tags` está presente | Un valor de `session_tracking.tags.kinds` en `.directives` |
| `tags.topics` | array de 0–2 strings | No | Libres, recomendado en minúsculas kebab-case, ≤ 20 caracteres cada uno |

El máximo es de **3 slots en total** (1 `kind` + hasta 2 `topics`). El formato es fijo: el objeto `{kind, topics: [...]}`. Los arrays planos o claves extra se rechazan.

**Contrato de escritura:**

- Las tags se fusionan en el heartbeat vía `kata-session-heartbeat --set-tags`.
- Escritura atómica (archivo temporal + `mv`) preserva el resto del JSON (`session_id`, `started_at`, `last_activity`, …).
- Compatible con versiones anteriores: los heartbeats escritos antes de que existieran las tags no tienen la clave `tags` y cada lector trata el campo como opcional.

**Contrato de lectura:**

- El script de statusline lee `tags.kind` y `tags.topics[]` e imprime chips después del branch (p. ej. `main ahrena · [tech-task] [reconciliation]`).
- La extensión ahrena-vscode observa `.ahrena/workflow/sessions/<id>.json` y renderiza chips en la fila de la sesión.
- El digest de planes de Eunomia agrega las tags por sesión activa en el reporte periódico de estado.

**Sugerencia automática:**

Cuando `session_tracking.tags.auto_suggest: true` y el heartbeat no tiene objeto `tags`, el agente invoca `kata-session-tag-suggest` en el primer turno del usuario de la sesión y escribe el resultado vía `kata-session-heartbeat`. Una nota de visibilidad de una línea en la misma respuesta muestra las tags elegidas para que el usuario corrija vía `/cry-tags set` si la inferencia falló. Volver a ejecutar la auto-sugerencia cuando `tags` ya está presente se rechaza — las tags tienen alcance de sesión; solo el usuario las limpia.

El contrato está regido por `lex-session-tags`.

**Hook (UserPromptSubmit):**

La auto-sugerencia está cableada por un hook de Claude Code a nivel del proyecto en `.claude/hooks/session-tags-auto-suggest.sh`, instalado por `scripts/install.py`. El hook se ejecuta en cada `UserPromptSubmit`, aplica gates baratos (jq + python3 + PyYAML presentes, `.directives` legible, `session_tracking.{enabled, tags.enabled, tags.auto_suggest}` todos `true`, session_id resoluble, archivo de heartbeat presente, `.tags` null/ausente) y, en caso de éxito, emite un bloque `<system-reminder>` único en stdout. El bloque instruye a Claude a derivar tags del prompt actual + plan activo + nombre del branch, escribirlas vía `kata-session-heartbeat --set-tags` y agregar la nota de visibilidad `tagged: [...]`. Una vez que el heartbeat carga `tags`, el hook es un no-op por el resto de la sesión. El hook NO bootstrapea heartbeats — la creación del heartbeat permanece bajo responsabilidad de `kata-session-heartbeat` invocado por Eunomia/Athena en las transiciones del plan. Desactive estableciendo `session_tracking.tags.auto_suggest: false` en `.ahrena/.directives`.

## Restricciones

- **No persistir credenciales o datos sensibles** en el heartbeat file — `cwd`, `branch`, `plan_id`, IDs y timestamps son el límite.
- **No crear el directorio `.ahrena/workflow/sessions/` en commit** — siempre gitignored.
- **No confundir `previous_session` con merge de sesiones** — handoff es secuencial; no hay múltiples sesiones `running` simultáneamente en el mismo plan.

## Referencias

- `lex-agent-planning` — front-matter del plan referencia `claude_session` + `session_entrypoint`
- `lex-pr-quality` — exige sección "Session Trace" en el body del PR
- `kata-session-heartbeat` — procedimiento operacional canónico
- `kata-pr-prepare` — construye la sección "Session Trace" antes de abrir el PR
- `lex-directives` — claves `session_tracking.*` en `.ahrena/.directives`
- `codex-pr-cost-tracking` — métrica de costo (tokens/USD), complementaria a la métrica de tiempo aquí
