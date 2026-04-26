# Cry: Event Storm — Descubrimiento y Documentación de CloudEvents

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para descubrir y documentar eventos CloudEvents de una feature o módulo conforme a Lexis y Codex de Guardia

## Descripción

Este comando invoca al Warrior Kronos (especialista en Event Storm) para descubrir y documentar eventos CloudEvents de una feature o módulo en dos fases. Cuando el panorama de eventos es desconocido, Kronos ejecuta primero el **kata-event-storm** (Descubrimiento) para mapear eventos de dominio, comandos, agregados, políticas, hotspots y bounded contexts, y luego procede al **kata-events-doc** (Documentación). Cuando los eventos ya están identificados, Kronos va directamente a la Documentación.

## Uso

```
/cry-event-storm <contexto de la feature o módulo> [source base]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `contexto de la feature o módulo` | Sí | Nombre del módulo y descripción del dominio (para Descubrimiento) o lista explícita de tipos de evento (solo para Documentación) | `"Módulo platform, transferencias agendadas — eventos desconocidos"` o `"event.guardia.platform.scheduled_transfer.created, .updated, .cancelled"` |
| `source base` | No | Base de la URI `source` (ej.: `https://tenant.guardia.finance/platform/api/v1`). Si se omite, el agente propone conforme codex-cloudevents | `https://tenant.guardia.finance/platform/api/v1` |

## Qué Hace el Comando

1. Lee `.ahrena/.directives` para obtener `paths.events`, `language.default` y configuración MCP
2. Asume el rol del Warrior Kronos y **determina el punto de entrada**:
   - El contexto describe un dominio sin eventos conocidos → **Fase 1: Descubrimiento** (kata-event-storm) luego **Fase 2: Documentación** (kata-events-doc)
   - El contexto proporciona una lista explícita de tipos de evento → **Fase 2: Documentación únicamente** (kata-events-doc)
3. **Fase 1 — Descubrimiento** (cuando aplica): ejecuta kata-event-storm de forma iterativa — mapea eventos de dominio (línea de tiempo), comandos, actores, agregados, políticas, sistemas externos, read models, hotspots y bounded contexts; produce catálogo CloudEvents; lo presenta al usuario para confirmación; resuelve hotspots P1 antes de avanzar
4. **Fase 2 — Documentación**: ejecuta kata-events-doc — documenta estructura del evento, payload (data), idempotencia; genera o actualiza el documento formal de eventos en **paths.events**
5. Persiste ambos artefactos (documento de descubrimiento cuando se ejecutó la Fase 1; documento de eventos siempre) en **paths.events** (predeterminado `docs/events`); crea el directorio si no existe

## Prompt Template

```
Contexto:
- Contexto de la feature/módulo: {{contexto de la feature o módulo}}
- Source base (opcional): {{source base}}

Tarea:
Actúe como el Warrior Kronos (Especialista en Event Storm). Lea .ahrena/.directives
y determine el punto de entrada:
- Si el panorama de eventos es desconocido o el dominio no ha sido mapeado →
  ejecute kata-event-storm primero (Fase 1 — Descubrimiento), luego kata-events-doc
  (Fase 2 — Documentación).
- Si se proporciona una lista explícita de tipos de evento → ejecute kata-events-doc
  directamente (Fase 2 — Documentación únicamente).

Trabaje de forma iterativa: haga preguntas de clarificación cuando sea necesario y
espere respuestas antes de avanzar. No pase de la Fase 1 a la Fase 2 si hay
hotspots P1 sin resolver.

Formato de salida:
- Consultar paths.events en .ahrena/.directives para el destino (predeterminado docs/events)
- Crear el directorio si no existe
- Fase 1 (cuando se ejecuta): guardar documento de descubrimiento de event storm (ej.: event-storm-{modulo}.md)
- Fase 2: crear o actualizar el documento formal de eventos (ej.: events.md)
- Confirmar los paths de todos los artefactos persistidos
```

## Ejemplos de Invocación

**Escenario A — Panorama de eventos desconocido (Fase 1 → Fase 2):**

```
/cry-event-storm "Módulo platform, transferencias agendadas — contadores programan transferencias bancarias para ejecución futura; se requiere aprobación del supervisor antes de la ejecución"
```

Output esperado:
- Kronos ejecuta kata-event-storm: mapea línea de tiempo, comandos, actores, agregados, hotspots
- Presenta catálogo CloudEvents para confirmación; resuelve hotspots P1
- Ejecuta kata-events-doc y produce documento formal de eventos
- Ambos artefactos guardados en `paths.events`

**Escenario B — Eventos ya conocidos (solo Fase 2):**

```
/cry-event-storm "event.guardia.platform.scheduled_transfer.created, .updated, .cancelled"
```

Output esperado:
- Kronos ejecuta kata-events-doc directamente
- Hace preguntas sobre source base y payload si es necesario
- Documento de eventos creado o actualizado en `paths.events`

## Restricciones

- El Cry no implementa código (publicadores o consumidores); solo dispara descubrimiento y documentación
- Hotspots P1 identificados en la Fase 1 bloquean la transición a la Fase 2 — deben resolverse antes de la documentación
- El contexto debe ser suficiente para identificar el módulo y el dominio o los tipos de evento; si es vago, Kronos solicita complemento
- Excepciones a las Lexis deben documentarse en ADR

## Katas y Warrior Asociados

| Artefacto | Fase | Descripción |
|-----------|------|-------------|
| `kata-event-storm` | 1 — Descubrimiento | Eventos de dominio, comandos, agregados, políticas, bounded contexts, catálogo CloudEvents |
| `kata-events-doc` | 2 — Documentación | Documento formal de CloudEvents (Markdown) en paths.events |
| `warrior-kronos` | Orquestador | Determina el punto de entrada y orquesta las dos fases |

## Referencias

- `warrior-kronos` — Especialista en Event Storm; enruta entre Descubrimiento y Documentación según el contexto
- `kata-event-storm` — Procedimiento de Descubrimiento (Fase 1)
- `kata-events-doc` — Procedimiento de Documentación (Fase 2)
