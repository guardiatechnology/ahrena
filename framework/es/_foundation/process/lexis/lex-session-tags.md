# Lexis: Tags de Sesión

> **Prefijo:** `lex-` | **Tipo:** Ley Inviolable | **Alcance:** Tags semánticas anexadas a cada sesión de Claude Code, expuestas al humano en la statusline, en el sidebar de la extensión VSCode y en el digest de planes de Eunomia

## Ley

> **Toda sesión de Claude Code que adhiere a `session_tracking.tags.enabled` DEBE cargar como máximo 3 tags en su archivo de heartbeat: exactamente un `kind` (1er slot, tomado del vocabulario controlado en `session_tracking.tags.kinds`) y 0–2 `topics` (libres, en minúsculas, kebab-case, ≤ 20 caracteres cada uno). Las tags DEBEN vivir en el objeto `tags` de `.ahrena/workflow/sessions/<session-id>.json` según `codex-session-tracking` §9. Inventar un `kind` fuera del vocabulario configurado, exceder 3 slots, o persistir tags en cualquier ubicación distinta del heartbeat JSON está PROHIBIDO.**

## Cobertura

- **Se aplica a:** toda sesión de Claude Code que se ejecuta en un repositorio con `session_tracking.enabled: true` y `session_tracking.tags.enabled: true` en `.ahrena/.directives`.
- **Agentes vinculados:** todo agente que escribe un heartbeat (`kata-session-heartbeat`), sugiere tags (`kata-session-tag-suggest`) o acepta override del usuario (`cry-tags`). Los consumidores de superficie (script de statusline, extensión ahrena-vscode, digest de Eunomia) leen, pero no escriben.
- **Excepciones:** sesiones que se ejecutan fuera de Claude Code (sin `CLAUDE_CODE_SESSION_ID`) omiten las tags silenciosamente junto con el heartbeat. Sesiones en repositorios sin el bloque `tags` en `.directives` mantienen heartbeats sin `tags` — compatible con versiones anteriores.

## Reglas

### 1. Modelo de slots

El objeto `tags` tiene exactamente dos claves:

```json
"tags": {
  "kind": "tech-task",
  "topics": ["reconciliation", "api"]
}
```

- `kind` (slot 1): string única, obligatoria cuando `tags` está presente, tomada de `session_tracking.tags.kinds` en `.directives`.
- `topics` (slots 2–3): array de 0 a 2 strings, libres, recomendado en minúsculas kebab-case, cada uno ≤ 20 caracteres.

Arrays planos (`"tags": ["tech-task", "reconciliation", "api"]`), estructuras anidadas o claves extra están PROHIBIDOS.

### 2. Vocabulario controlado para `kind`

`kind` DEBE corresponder exactamente a uno de los valores en `session_tracking.tags.kinds`. El vocabulario por defecto cubre las intenciones comunes del flujo Issue-Driven: `tech-task`, `bug`, `spike`, `user-story`, `epic`, `chore`, `design`, `review`, `exploration`, `release`.

Un proyecto PUEDE extender la lista en su propio `.ahrena/.directives`, pero las adiciones pasan por PR para mantener el vocabulario pequeño y agregable en el digest de Eunomia.

### 3. `topics` libres

Los `topics` no se validan contra ninguna lista. Forma recomendada: minúsculas, kebab-case (`reconciliation-engine`, `pix-integration`). El agente DEBERÍA advertir cuando un topic está en mayúsculas, contiene espacios, o supera 20 caracteres, pero NO DEBE rechazar — la corrección queda con el usuario vía `cry-tags set`.

### 4. Heartbeat como única fuente de verdad

Las tags DEBEN persistirse solo en el heartbeat JSON en `.ahrena/workflow/sessions/<session-id>.json`. Duplicar tags en el front-matter del plan, en el cuerpo de la Issue, en el cuerpo del PR, en mensajes de commit, o en cualquier otra ubicación está PROHIBIDO — cada lector (statusline, extensión, digest) lee el heartbeat directamente. La sección "Session Trace" del PR (construida por `kata-pr-prepare`) PUEDE incluir tags como información derivada de los heartbeats que agrega, pero el heartbeat sigue siendo el canónico.

### 5. La sugerencia automática es silenciosa con nota de visibilidad

Cuando `session_tracking.tags.auto_suggest: true` y el heartbeat de la sesión actual no tiene objeto `tags`, el agente invoca `kata-session-tag-suggest` en el primer turno del usuario, escribe las tags inferidas vía `kata-session-heartbeat`, y emite una nota de visibilidad de una línea en la misma respuesta (formato: `tagged: [kind] [topic1] [topic2]`). El usuario mantiene el control total vía `/cry-tags set`, `/cry-tags clear` o `/cry-tags --auto-suggest` para volver a inferir.

Volver a ejecutar la auto-sugerencia cuando `tags` ya está presente está PROHIBIDO — las tags tienen alcance de sesión y solo el usuario las limpia.

### 6. Compatibilidad con versiones anteriores

Los heartbeats escritos antes de que las tags existieran (sin clave `tags`) siguen siendo válidos. Cada lector DEBE tratar el campo `tags` como opcional y renderizar con elegancia cuando esté ausente (p. ej., la statusline muestra `main ahrena` sin chip; la línea del digest omite la columna de tags para esa sesión).

```
<HARD-GATE>
Todo agente NO DEBE escribir un heartbeat de sesión que contenga `tags`
sin satisfacer TODAS las precondiciones:

  (a) `session_tracking.tags.enabled: true` en `.ahrena/.directives`
  (b) `tags.kind` es una string tomada de `session_tracking.tags.kinds`
  (c) `tags.topics` es un array de 0 a 2 strings
  (d) Total de slots usados ≤ 3 (1 kind + hasta 2 topics)
  (e) El formato es el objeto `{kind, topics: [...]}` —
      los arrays planos o claves extra se rechazan
  (f) El destino es `.ahrena/workflow/sessions/<id>.json`
      (sin duplicación en el front-matter del plan, en el cuerpo
      de la Issue/PR, o en mensajes de commit)

Esta regla se aplica a TODA sesión de Claude Code, independientemente de:
  - tamaño percibido ("es solo una tag")
  - urgencia ("el usuario quiere verla ahora")
  - confianza del equipo ("ya validamos el kind")
  - confianza de la inferencia ("estoy seguro de que es un bug")

Excepción declarada única: las sesiones que se ejecutan fuera de
Claude Code (sin `CLAUDE_CODE_SESSION_ID`) omiten el heartbeat y
las tags silenciosamente, sin error y sin persistencia fallback.
</HARD-GATE>
```

## Ejemplos

### Correcto

```json
{
  "session_id": "85846253-4edf-443d-b294-187ef287d1bb",
  "plan_id": "321",
  "branch": "feat/321-session-tags-foundation",
  "tags": {
    "kind": "tech-task",
    "topics": ["session-tracking", "framework"]
  },
  "last_heartbeat": "2026-05-28T04:10:00Z"
}
```

```
Usuario: /cry-tags set bug reconciliation api
Agente: tags actualizadas → [bug] [reconciliation] [api]
```

### Incorrecto

```json
"tags": ["tech-task", "reconciliation", "api"]
```
Array plano — viola la regla 1.

```json
"tags": {"kind": "documentation", "topics": []}
```
`documentation` no está en la lista por defecto de `kinds`; o se agrega al `.directives` del proyecto (vía PR) o se elige del vocabulario controlado.

```json
"tags": {"kind": "tech-task", "topics": ["a","b","c"]}
```
Tres topics — excede el límite de 2 slots. El total sería 4 (1 kind + 3 topics).

## Validación Automatizada

- **Herramienta:** validador de JSON schema en la escritura del heartbeat (`kata-session-heartbeat`); `cry-tags` rechaza `kind` fuera del vocabulario con un error de una línea listando el vocabulario configurado; el digest de Eunomia lee `tags` defensivamente y omite entradas malformadas.
- **Cuándo:** toda escritura de heartbeat; toda invocación de `/cry-tags set`; tick del loop PM de Eunomia.
- **Métrica:** 0 heartbeats con `tags.kind` fuera de `session_tracking.tags.kinds`; 0 heartbeats con más de 3 slots de tags; 0 tags persistidas fuera del heartbeat JSON.

## Referencias

- `codex-session-tracking` — §9 schema de las tags y contrato de lectura/escritura
- `kata-session-heartbeat` — merge atómico de `tags` en el heartbeat JSON
- `kata-session-tag-suggest` — procedimiento de inferencia en el primer turno del usuario
- `cry-tags` — comandos de override del usuario
- `lex-directives` — claves `session_tracking.tags.*`
- `lex-no-plans-under-docs` — regla hermana que mantiene las tags fuera de `docs/` (solo en el heartbeat)
