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
| `tags` | No | Objeto de tags de la sesión `{kind, topics: [...]}` para fusionar en el heartbeat. Cuando se omite, las tags existentes se preservan. Ver "Soporte de tags" abajo y `lex-session-tags`. |

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

## Soporte de tags

La kata acepta una entrada opcional `tags` (o la forma equivalente de CLI `--set-tags <kind> [topic1] [topic2]`) regida por `lex-session-tags`.

**Formas de invocación:**

```bash
# Posicional (ergonomía de CLI): kind primero, luego 0-2 topics
kata-session-heartbeat --set-tags tech-task reconciliation api

# Programática (invocación por otra kata o warrior):
kata-session-heartbeat tags='{"kind":"tech-task","topics":["reconciliation","api"]}'
```

**Semántica de merge:**

- Cuando `tags` se proporciona: valida contra `session_tracking.tags.*` en `.directives` (kind está en `kinds`; topics ≤ 2; total de slots ≤ 3); reemplaza el objeto `tags` del heartbeat atómicamente.
- Cuando `tags` se omite: preserva el objeto `tags` existente en el heartbeat en disco (junto con `started_at`).
- Para limpiar las tags: pase un objeto vacío explícito `tags={}` (renderizado en el JSON como `"tags": {}` — o elimine la clave con `tags=null`).

**Merge atómico:**

La escritura atómica de los Pasos 6+7 (`mktemp` → `mv`) ya preserva el resto del JSON. La rama de tags sigue el mismo camino:

```bash
EXISTING=$(cat ".ahrena/workflow/sessions/${SESSION_ID}.json" 2>/dev/null || echo '{}')
NEW=$(echo "$EXISTING" | jq --argjson tags "$TAGS_JSON" '.tags = $tags')
TMP=$(mktemp)
echo "$NEW" > "$TMP"
mv "$TMP" ".ahrena/workflow/sessions/${SESSION_ID}.json"
```

**Errores de validación:**

Cuando la validación en `lex-session-tags` falla (kind fuera del vocabulario, > 2 topics, formato malformado), la kata sale con código 2 e imprime en stderr un error de una línea listando el vocabulario configurado. El archivo de heartbeat queda intacto.

**Interacción con auto-sugerencia:**

`kata-session-tag-suggest` es la kata upstream que produce un objeto `tags` válido a partir del primer prompt del usuario. Esta kata NO la invoca — solo escribe lo que recibe. La orquestación (llamar-sugerencia-luego-llamar-heartbeat) vive en el hook del Plan B o en `cry-tags --auto-suggest` invocado por el usuario.

## Referencias

- `codex-session-tracking` — manual de referencia (schema, cadencia, limpieza, handoff, §9 tags)
- `lex-agent-planning` — front-matter del plan referencia `claude_session` + `session_entrypoint`
- `lex-pr-quality` — exige "Session Trace" en el body del PR
- `lex-session-tags` — ley que rige el objeto `tags`
- `kata-session-tag-suggest` — kata upstream que produce sugerencias de tags
- `kata-pr-prepare` — consume los heartbeat files en la construcción del "Session Trace"
- `cry-tags` — override del usuario (`set`, `show`, `clear`, `--auto-suggest`)
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — invocadores
