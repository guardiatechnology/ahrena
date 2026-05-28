# Kata: Sugerir Tags de Sesión a partir del Primer Prompt

> **Prefijo:** `kata-` | **Tipo:** Habilidad Repetible | **Alcance:** Inferir un objeto `tags` válido (1 kind + hasta 2 topics) a partir del primer prompt del usuario y del contexto del plan activo

## Objetivo

Producir un objeto `tags` válido — `{kind, topics: [...]}` según `lex-session-tags` — a partir del primer prompt del usuario en una nueva sesión de Claude Code, opcionalmente enriquecido por el front-matter del plan activo y el nombre del branch. La kata es pura inferencia: devuelve las tags sugeridas y NO escribe el heartbeat. El llamador (hook del Plan B o `cry-tags --auto-suggest`) decide si persiste vía `kata-session-heartbeat --set-tags`.

## Cuándo Usar

- Primer turno del usuario en una nueva sesión de Claude Code cuando el heartbeat no tiene objeto `tags` y `session_tracking.tags.auto_suggest: true` (disparado por el hook UserPromptSubmit del Plan B).
- Re-inferencia manual disparada por el usuario vía `/cry-tags --auto-suggest`.
- Invocación programática por un warrior que necesita una sugerencia de tag estructurada antes de escribir.

NO usar cuando el heartbeat ya carga un objeto `tags` — la re-sugerencia en ese caso está prohibida por la regla 5 de `lex-session-tags`.

## Entradas

| Entrada | Obligatorio | Descripción |
|---|:---:|---|
| `user_prompt` | Sí | Texto del primer prompt del usuario en la sesión (crudo, sin preprocesamiento). |
| `plan_front_matter` | No | Front-matter YAML del plan activo (`.claude/plans/plan-{M}-{slug}.md` cuando exista). Aporta slug + status como señales adicionales de inferencia. |
| `branch_name` | No | Nombre del branch actual (p. ej. `feat/321-session-tags-foundation`). El prefijo del tipo (`feat`, `fix`, etc.) es una señal fuerte para `kind`. |
| `kinds_vocabulary` | Sí | Lista de valores de `kind` permitidos, leída de `session_tracking.tags.kinds` en `.ahrena/.directives`. |

## Flujo

```
Progreso:
- [ ] 1. Leer kinds_vocabulary de .ahrena/.directives
- [ ] 2. Derivar kind del prefijo del branch + verbos del prompt + slug del plan
- [ ] 3. Derivar topics de los sustantivos del prompt + slug del plan + pistas de alcance
- [ ] 4. Validar contra lex-session-tags (kind en el vocabulario, topics ≤ 2)
- [ ] 5. Emitir el objeto {kind, topics} como salida estructurada
```

### Paso 1 — Leer vocabulario

```bash
KINDS=$(yq '.session_tracking.tags.kinds' .ahrena/.directives)
```

Si `session_tracking.tags.kinds` está ausente o vacío, sale con código 1 — la sugerencia no puede hacerse sin un vocabulario.

### Paso 2 — Derivar `kind`

El agente elige un valor de `kinds_vocabulary` usando esta escalera de señales (primera coincidencia gana):

| Señal | Mapea a `kind` |
|---|---|
| Prefijo `feat/` + prompt menciona una nueva capacidad | `user-story` (cuando la Issue parent es una User Story) o `tech-task` (cuando es una Tech Task) |
| Prefijo `fix/` + prompt menciona bug, error, regresión | `bug` |
| Prefijo `chore/`, `ci/`, `build/`, `docs/`, `style/`, `refactor/` | `chore` |
| Prompt menciona "design", "wireframe", "mockup", "API design" | `design` |
| Prompt menciona "review", "audit", "check", "approve" + ref a PR/Issue | `review` |
| Prompt menciona "explore", "investigate", "spike", "PoC", "research" | `spike` (o `exploration` cuando no hay entregable time-boxed) |
| Prompt menciona "release", "tag", "publish", "version bump" | `release` |
| El prompt es una pregunta o cuestión abierta | `exploration` |
| Ninguna señal dispara | `tech-task` (default seguro para el framework) |

Cuando múltiples señales disparan, el **prefijo del branch** gana — refleja el alcance comprometido, no la conversación.

### Paso 3 — Derivar `topics`

Elegir hasta 2 topics en este orden de preferencia:

1. **Slug del plan** sin el número inicial: `321-session-tags-foundation` → `session-tags-foundation` → `session-tags` (mantenido) + `foundation` (mantenido).
2. **Sustantivo de dominio** del prompt: identificar el sustantivo de dominio más concreto (p. ej. "reconciliation", "pix", "fiscal", "auth"). Minúsculas, kebab-case.
3. **Repo/componente** de `cwd` cuando el prompt es genérico.

Truncar a ≤ 20 caracteres cada uno. Omitir topics demasiado genéricos (`feature`, `code`, `system`, `change`).

### Paso 4 — Validar

Aplicar las verificaciones de precondición del HARD-GATE de `lex-session-tags`:

- `kind` ∈ `kinds_vocabulary`
- `topics` es un array de 0 a 2 strings
- Total ≤ 3 slots
- Formato de objeto `{kind, topics: [...]}` (sin array plano, sin claves extra)

Cuando la validación falla, recurrir a `{"kind": "tech-task", "topics": []}` y emitir una advertencia en stderr — la escritura del heartbeat es no-bloqueante.

### Paso 5 — Emitir salida estructurada

Imprimir una sola línea JSON en stdout:

```json
{"kind":"tech-task","topics":["session-tags","foundation"]}
```

El llamador encadena esto directamente a `kata-session-heartbeat --set-tags` o renderiza la nota de visibilidad `tagged: [tech-task] [session-tags] [foundation]` en la respuesta del agente.

## Salidas

| Salida | Formato | Destino |
|---|---|---|
| Sugerencia de tags | Una sola línea JSON | stdout |
| Advertencia (cuando hay fallback) | Texto de una línea | stderr |

## Restricciones

- **Sin persistencia.** La kata nunca toca el archivo de heartbeat. Escribir es trabajo del llamador.
- **Sin prompt interactivo.** La inferencia es silenciosa; la confirmación del usuario vive en la nota de visibilidad + `cry-tags set`.
- **Sin re-sugerencia en un heartbeat con tags existentes.** El llamador DEBE verificar `tags == null` antes de invocar; de lo contrario esta kata es un no-op (código de salida 0, stdout vacío).
- **Sin invención de `kind`.** Recurrir a un valor por defecto es aceptable; inventar un nuevo valor de vocabulario no lo es.

## Referencias

- `lex-session-tags` — schema, contrato del vocabulario, HARD-GATE
- `kata-session-heartbeat` — kata downstream que escribe el objeto de tag
- `cry-tags` — wrapper para el usuario que invoca esta kata para `--auto-suggest`
- `codex-session-tracking` — sección §9 sobre tags
- `lex-directives` — fuente de verdad de `session_tracking.tags.kinds`
