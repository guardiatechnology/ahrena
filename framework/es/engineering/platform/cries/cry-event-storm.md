# Cry: Event Storm — Descubrimiento y Documentación de CloudEvents

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para descubrir y documentar eventos CloudEvents de una feature o módulo conforme a Lexis y Codex de Guardia

## Descripción

Este comando invoca al Warrior Kronos (o al agente asumiendo su rol) para ejecutar el descubrimiento y documentación de eventos CloudEvents de una nueva feature: consultar Lexis y Codex de CloudEvents y producir la **documentación de eventos en Markdown** (kata-events-doc), en **`docs/{context}/events/`**.

## Uso

```
/cry-event-storm <descripción de la feature> [contexto de eventos]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `descripción de la feature` | Sí | Descripción del dominio, entidades, operaciones y reglas de negocio relevantes para los eventos | "Módulo de transferencias programadas: crear, listar, actualizar y cancelar; eventos emitidos en cada transición de estado" |
| `contexto de eventos` | No | Complemento específico para los eventos (ej.: módulo, tipo de entidad, base de source). Si se omite, el agente infiere del contexto de la feature o hace preguntas | "Módulo platform, tipo de entidad scheduled_transfer" |

## Qué Hace el Comando

1. Interpreta la descripción de la feature y el contexto de eventos (si se informó)
2. Asume el rol del Warrior Kronos (especialista en eventos) o delega al agente que ejecuta kata-events-doc
3. El Warrior Kronos (o el agente en su rol) consulta lex-cloudevents, lex-idempotency y los Codex de CloudEvents
4. Identifica entidades, transiciones de estado y eventos relevantes para la feature
5. Produce documentación de eventos en Markdown con catálogo, ciclos de vida (diagramas Mermaid) y payloads CloudEvents
6. Entrega el artefacto en **`docs/{context}/events/`**

## Template de Prompt

```
Contexto:
- Descripción de la feature: {{descripción de la feature}}
- Contexto de eventos (opcional): {{contexto de eventos}}

Tarea:
Actúa como el Warrior Kronos (Especialista en Event Storm) y ejecuta **kata-events-doc** (el Kata consulta las Lexis y Codex de CloudEvents conforme su documentación). Basándote en la descripción de la feature, haz preguntas de clarificación cuando sea necesario (ej.: módulo, tipos de entidad, transiciones de estado, consumidores) y refina el diseño en base a las respuestas. Produce la documentación de eventos en `docs/{context}/events/`. Usa el contexto de eventos informado o propón uno adecuado.

Formato de salida:
- Guardar en `docs/{context}/events/` conforme a `lex-feature-design-docs`
- Crear el directorio si no existe en el proyecto
- Crear o actualizar el documento de eventos Markdown en ese path
- Catálogo de eventos (entity_type, event_name, tipo completo, publicadores, consumidores); para cada evento: diagrama de ciclo de vida Mermaid, payload CloudEvents completo con todos los campos del atributo `data`, tabla de campos
```

## Ejemplo de Invocación

**Input:**

```
/cry-event-storm "Módulo de transferencias programadas: crear, actualizar y cancelar; eventos emitidos en requested, approved, executed, failed, cancelled" "módulo platform, entidad scheduled_transfer"
```

**Output esperado:**

Respuesta estructurada del Warrior Kronos con:
- Eventos identificados: `event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`
- Diagrama de ciclo de vida Mermaid para `scheduled_transfer`
- Payload CloudEvents completo para cada evento (specversion, id, source, type, subject, time, idempotencykey, data)
- Documentación creada o actualizada en `docs/{context}/events/` (directorio creado si no existía)

## Restricciones

- El Cry no implementa código; solo dispara el descubrimiento y documentación de eventos
- La descripción de la feature debe ser suficiente para identificar entidades y transiciones de estado; si está vaga, el agente puede pedir complemento
- Las excepciones a las Lexis deben documentarse en un ADR; el agente puede señalar cuándo una decisión requiere ADR

## Cry vs Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida con descripción de la feature | Procedimiento completo en múltiples pasos |
| **Complejidad** | Baja (1 comando) | Alta (pasos: directivas, consulta Lexis/Codex, entidades, eventos, payloads, documentación, validación) |
| **¿Configura agente?** | Sí (asume el rol del Warrior Kronos) | Sí (define todos los pasos del descubrimiento) |
| **Ejemplo** | "/cry-event-storm crear/listar/cancelar transferencias programadas" | Ejecutar kata-events-doc con inputs explícitos |

## Kata y Warrior Asociados

- **kata-events-doc** — Descubrimiento de eventos y producción de documentación Markdown en `docs/{context}/events/`
- **warrior-kronos** — Especialista en Event Storm; ejecuta kata-events-doc

## Referencias

- `kata-events-doc` — Procedimiento ejecutado por el Warrior Kronos (el Kata consulta las Lexis y Codex de CloudEvents; ver documentación del Kata)
- `lex-feature-design-docs` — estructura canónica `docs/{context}/{category}/`
