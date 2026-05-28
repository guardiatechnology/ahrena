# Cry: Gestionar Tags de Sesión

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo del usuario para leer, definir, limpiar o volver a inferir las tags de la sesión Claude Code actual, según `lex-session-tags`

## Descripción

Atajo del usuario que gestiona el objeto `tags` en el heartbeat de la sesión actual (`.ahrena/workflow/sessions/<id>.json`). Encapsula `kata-session-heartbeat` (para escrituras) y `kata-session-tag-suggest` (para auto-inferencia). El Cry nunca invoca Lexis o Codex directamente — enruta a través de las Katas según `lex-pilars`.

La auto-sugerencia se ejecuta silenciosamente en el primer turno del usuario cuando `session_tracking.tags.auto_suggest: true`; `cry-tags` es la superficie manual de override.

## Uso

```
/cry-tags <subcomando> [args]
```

## Subcomandos

| Subcomando | Efecto |
|---|---|
| `set <kind> [topic1] [topic2]` | Reemplaza el objeto de tags actual con los valores dados. `kind` DEBE estar en `session_tracking.tags.kinds`; los topics son opcionales. |
| `show` | Imprime el objeto de tags actual al usuario sin modificar nada. |
| `clear` | Elimina la clave `tags` del heartbeat (resetea a "sin tags"). |
| `--auto-suggest` | Fuerza una nueva inferencia vía `kata-session-tag-suggest` aunque `tags` ya esté presente, y luego escribe la sugerencia vía `kata-session-heartbeat`. |

## Qué Hace el Comando

1. Lee `session_tracking.tags.*` de `.ahrena/.directives`.
2. Lee el heartbeat actual en `.ahrena/workflow/sessions/<session_id>.json` (cuando esté presente).
3. Despacha por subcomando:
   - `set`: valida `kind` contra el vocabulario configurado; rechaza con un error de una línea listando el vocabulario cuando es inválido. Invoca `kata-session-heartbeat` con el objeto `tags` fusionado.
   - `show`: imprime el objeto `tags` actual (o `"(sin tags)"` cuando está ausente).
   - `clear`: invoca `kata-session-heartbeat` pasando `tags=null` para eliminar el campo.
   - `--auto-suggest`: invoca `kata-session-tag-suggest` con el primer prompt del usuario (leído de la sesión) + front-matter del plan + nombre del branch; encadena la salida JSON a `kata-session-heartbeat --set-tags`.
4. Emite una confirmación de una línea en el formato `tagged: [kind] [topic1] [topic2]` (o `tags cleared` / `(sin tags)`).

## Plantilla de Prompt

```
Invoque la kata relevante para el {subcomando}:

- Para `set`: valide el kind contra session_tracking.tags.kinds, luego llame a
  kata-session-heartbeat con tags={kind, topics: [...]}.

- Para `show`: lea .ahrena/workflow/sessions/<session_id>.json e imprima el
  objeto tags o "(sin tags)" cuando esté ausente.

- Para `clear`: llame a kata-session-heartbeat con tags=null.

- Para `--auto-suggest`: llame a kata-session-tag-suggest con el primer
  prompt del usuario de la sesión, luego encadene la salida JSON a
  kata-session-heartbeat --set-tags.

Después de cualquier escritura, emita la confirmación de una línea:
  tagged: [kind] [topic1] [topic2]
o:
  tags cleared
```

## Ejemplos de Invocación

**Definir tags:**

```
/cry-tags set bug reconciliation api
```

Salida:

```
tagged: [bug] [reconciliation] [api]
```

**Mostrar tags actuales:**

```
/cry-tags show
```

Salida:

```
tagged: [tech-task] [session-tags] [foundation]
```

**Limpiar:**

```
/cry-tags clear
```

Salida:

```
tags cleared
```

**Forzar re-inferencia vía auto-sugerencia:**

```
/cry-tags --auto-suggest
```

Salida:

```
tagged: [tech-task] [session-tracking] [framework]
```

**Kind inválido:**

```
/cry-tags set documentation
```

Salida (stderr, sin escritura):

```
ERROR: kind 'documentation' no está en session_tracking.tags.kinds.
Kinds configurados: tech-task, bug, spike, user-story, epic, chore, design, review, exploration, release.
```

## Restricciones

- NO persiste tags en ningún lugar más que en el heartbeat JSON — la duplicación en el front-matter del plan, en el cuerpo de la Issue o en el mensaje del commit está prohibida por la regla 4 de `lex-session-tags`.
- NO inventa valores de `kind` fuera de `session_tracking.tags.kinds`. Las adiciones del proyecto pasan por revisión de PR en `.ahrena/.directives`.
- NO opera cuando `session_tracking.enabled: false` o `session_tracking.tags.enabled: false` — sale silenciosamente con una nota de una línea.
- NO opera fuera de Claude Code (sin `CLAUDE_CODE_SESSION_ID`) — sale silenciosamente según la cláusula de excepción de `lex-session-tags`.
- La salida respeta el tono de Guardia (`lex-tone`, `lex-brand-voice`) — directo, sin buzzwords.

## Diferencia con la Kata

| Aspecto | `cry-tags` | `kata-session-heartbeat` / `kata-session-tag-suggest` |
|---|---|---|
| **Naturaleza** | Atajo del usuario | Procedimientos completos |
| **Invocación** | `/cry-tags <subcomando>` (1 línea) | Llamada por `cry-tags` o por warriors |
| **¿Conoce el vocabulario?** | Lee de `.directives`, valida entrada del usuario | La kata también valida, pero no presenta el mensaje de error al humano |
| **Salida** | Confirmación de una línea para el usuario | JSON estructurado + código de salida |
