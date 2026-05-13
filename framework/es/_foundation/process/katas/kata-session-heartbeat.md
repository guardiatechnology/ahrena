# Kata: Actualizar Heartbeat de Sesión Claude Code

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Registro/actualización del heartbeat de la sesión Claude Code actual para un plan activo

## Objetivo

Escribir o actualizar el archivo de heartbeat `.ahrena/workflow/sessions/<session-id>.json` de la sesión Claude Code actual. Idempotente, bajo costo, seguro de correr en cualquier punto del flujo. Invocado por Eunomia (creación), Athena (transiciones), Argos (revisión) y Janus (release) en momentos significativos.

## Cuándo Usar

- Cuando el agente entra a un plan (Eunomia al crear; Athena al iniciar Phase 4; Argos en `cry-review-pr`; Janus en `kata-release-prepare`/`kata-release-publish`).
- Al completar un Step del plan o una kata invocada.
- Al cambiar el `status:` del plan.
- Periódicamente (cada 5–10min) durante actividad prolongada.
- Por Eunomia en cada tick del loop PM antes de procesar el digest.

## Inputs

| Input | Obligatorio | Descripción |
|---|:---:|---|
| `plan_id` | Sí | NNN del plan en uso (leído del front-matter del plan en el worktree actual) |
| `last_activity` | Sí | Identificador del paso/kata/cry actual (ej.: `kata-pr-prepare:step3`, `cry-review-pr`) |
| `role` | Sí | `creator`, `executor`, `reviewer`, `releaser` |
| `previous_session` | No | UUID de la sesión anterior en caso de handoff |

Variables de entorno leídas automáticamente:

| Variable | Origen | Tratamiento si ausente |
|---|---|---|
| `CLAUDE_CODE_SESSION_ID` | Claude Code shell env | Omitir kata sin error (corriendo fuera de Claude Code) |
| `CLAUDE_CODE_ENTRYPOINT` | Claude Code shell env | Omitir kata sin error |
| `AI_AGENT` | Claude Code shell env | Aceptar valor vacío; los demás campos siguen |

## Workflow

```
Progreso:
- [ ] 1. Leer variables de entorno; si SESSION_ID/ENTRYPOINT ausentes, omitir silenciosamente
- [ ] 2. Resolver heartbeat_dir de .ahrena/.directives (default .ahrena/workflow/sessions/)
- [ ] 3. Crear directorio si no existe
- [ ] 4. Componer JSON conforme schema de codex-session-tracking §2
- [ ] 5. Si el heartbeat file ya existe con mismo session_id, preservar started_at; si no, started_at = now
- [ ] 6. Actualizar last_heartbeat = now y last_activity per input
- [ ] 7. Escribir atómicamente (write + rename)
```

### Paso 1 — Leer variables de entorno

```bash
SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
ENTRYPOINT="${CLAUDE_CODE_ENTRYPOINT:-}"
AGENT_VERSION="${AI_AGENT:-}"

if [[ -z "$SESSION_ID" || -z "$ENTRYPOINT" ]]; then
  # Corriendo fuera de Claude Code; heartbeat es no-op
  exit 0
fi
```

### Paso 2 — Resolver heartbeat_dir

Leer `session_tracking.heartbeat_dir` de `.ahrena/.directives` (default `.ahrena/workflow/sessions/`). Si `session_tracking.enabled == false`, omitir silenciosamente.

### Paso 3 — Garantizar directorio

```bash
mkdir -p .ahrena/workflow/sessions
```

(El directorio es gitignored por `.gitignore` — ver `codex-session-tracking` §6.)

### Paso 4 — Componer JSON

```json
{
  "session_id": "<SESSION_ID>",
  "entrypoint": "<ENTRYPOINT>",
  "agent_version": "<AGENT_VERSION>",
  "plan_id": "<plan_id input>",
  "branch": "<git rev-parse --abbrev-ref HEAD>",
  "cwd": "<pwd>",
  "started_at": "<preservado del archivo existente O now>",
  "last_heartbeat": "<now en ISO 8601>",
  "last_activity": "<last_activity input>",
  "role": "<role input>",
  "previous_session": "<previous_session input o null>"
}
```

### Paso 5 — Preservar `started_at` al reescribir

Si `.ahrena/workflow/sessions/<SESSION_ID>.json` ya existe, leer `started_at` del archivo existente y preservar; solo `last_heartbeat` y `last_activity` cambian.

### Paso 6+7 — Escritura atómica

```bash
TMP=$(mktemp)
echo "$JSON" > "$TMP"
mv "$TMP" ".ahrena/workflow/sessions/${SESSION_ID}.json"
```

Mover (`mv`) es atómico en el mismo filesystem — evita race cuando dos llamadas concurrentes ocurren.

## Salidas

| Salida | Formato | Destino |
|---|---|---|
| Heartbeat file | JSON conforme schema | `.ahrena/workflow/sessions/<session-id>.json` |

Sin stdout obligatorio. La kata es silenciosa en éxito. En falla (error de I/O), reportar a stderr y propagar; el agente invocador decide si aborta o prosigue.

## Restricciones

- **Sin efecto secundario más allá del heartbeat file.** No modifica plan, Issue, PR, ni git.
- **Sin credenciales o datos sensibles en el JSON** per `codex-session-tracking`.
- **Idempotente.** Múltiples llamadas rápidas sucesivas producen el mismo archivo final.
- **No-op fuera de Claude Code.** Sin `CLAUDE_CODE_SESSION_ID`, la kata sale con código 0 sin error.

## Referencias

- `codex-session-tracking` — manual de referencia (schema, cadencia, limpieza, handoff)
- `lex-agent-planning` — front-matter del plan referencia `claude_session` + `session_entrypoint`
- `lex-pr-quality` — exige "Session Trace" en el body del PR
- `kata-pr-prepare` — consume los heartbeat files en la construcción del "Session Trace"
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — invocadores
