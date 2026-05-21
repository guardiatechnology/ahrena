# Kata: Event Storming

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — descubrimiento de eventos de dominio, comandos, agregados, políticas y bounded contexts para una feature o módulo

## Objetivo

Este Kata define el procedimiento para **conducir una sesión de Event Storming** en un dominio o feature: identificar eventos de dominio, comandos, aggregates, políticas, sistemas externos, read models, hotspots y bounded contexts; mapear los eventos descubiertos a tipos CloudEvents; y producir un catálogo de descubrimiento estructurado listo para alimentar `kata-events-doc`.

## Cuándo Usar

- Al iniciar el diseño de una nueva feature o módulo cuando el panorama de eventos aún no se conoce
- Al mapear un dominio existente para identificar eventos ausentes, implícitos o no documentados
- Cuando es invocado por el Warrior Kronos en la fase de descubrimiento, antes de `kata-events-doc`
- Cuando `cry-event-storm` es activado por el usuario

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Descripción del dominio o feature | Sí | Descripción textual del dominio de negocio, alcance de la feature o módulo a analizar |
| Nombre del módulo | Sí | Identificador del módulo Guardia usado en el tipo CloudEvents (ej: `platform`, `reconciliation`, `fiscal`) |
| Alcance de bounded context | No | Si analizar un único bounded context o múltiples. Si se omite, analiza un único contexto |
| Eventos conocidos | No | Lista de eventos ya conocidos para usar como punto de partida. Si se proporcionan, extender y validar a partir de ellos |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Leer directivas y alcance
- [ ] 2. Consultar Lexis y Codex
- [ ] 3. Identificar eventos de dominio (línea de tiempo)
- [ ] 4. Identificar comandos y actores
- [ ] 5. Identificar aggregates
- [ ] 6. Identificar políticas (reacciones automáticas)
- [ ] 7. Identificar sistemas externos y read models
- [ ] 8. Marcar hotspots
- [ ] 9. Identificar bounded contexts
- [ ] 10. Mapear a tipos CloudEvents
- [ ] 11. Producir documento de Event Storming
```

### Paso 1: Leer Directivas y Alcance

1. Leer `.ahrena/.directives` para obtener `language.default`
2. Confirmar que la descripción del dominio/feature, el nombre del Bounded Context (PascalCase) y el módulo CloudEvents fueron proporcionados. Si son insuficientes, **preguntar al usuario** (¿cuál es el proceso de negocio principal? ¿quiénes son los actores? ¿cuál es el límite del sistema? ¿qué dispara la primera acción?) y esperar respuestas
3. Verificar si ya existe `docs/{context}/events/events.md` — incorporarlo como input si está disponible
4. Identificar el alcance de bounded context: único o múltiples contextos

### Paso 2: Consultar Lexis y Codex

1. Consultar **lex-cloudevents** — los eventos DEBEN seguir la spec CloudEvents; formato del tipo `event.guardia.{module}.{entity_type}.{event_name}`
2. Consultar **codex-cloudevents** — estructura del evento: id, source, specversion, type, time, subject, idempotencykey, data; tamaño < 12KB
3. Consultar **lex-entities** y **codex-entities** — campos de entidad en `data` (entity_id, entity_type, version, created_at, updated_at; history omitido)
4. Consultar **lex-idempotency** — los eventos DEBEN llevar idempotencykey; los consumidores DEBEN deduplicar

### Paso 3: Identificar Eventos de Dominio (Línea de Tiempo)

Los eventos de dominio son **cosas que ocurrieron** en el dominio — expresadas en tiempo pasado, desde la perspectiva del negocio:

1. Preguntar al usuario: "Describa el proceso de negocio paso a paso. ¿Qué ocurre primero y qué sigue?" — o inferir de la descripción cuando el flujo sea claro
2. Listar todos los eventos de dominio en **orden cronológico** (ej: `TransferenciaAgendadaSolicitada`, `TransferenciaAgendadaAprobada`, `TransferenciaAgendadaEjecutada`, `TransferenciaAgendadaFallida`)
3. Para cada evento, registrar:
   - **Nombre** — tiempo pasado, PascalCase (ej: `TransferenciaAgendadaEjecutada`)
   - **Cuándo ocurre** — disparador de negocio (ej: "después de que el contador envía el formulario de transferencia")
   - **Entidad relacionada** — el aggregate afectado
4. Identificar **brechas** en la línea de tiempo — eventos que deben existir lógicamente entre otros dos pero aún no han sido nombrados
5. Marcar eventos disputados o inciertos como hotspots (ver Paso 8)

### Paso 4: Identificar Comandos y Actores

Los comandos son **intenciones que disparan eventos** — expresados en imperativo, representando algo que un usuario o sistema quiere que ocurra:

1. Para cada evento de dominio, preguntar: "¿Qué disparó esto? ¿Quién o qué emitió el comando?"
2. Identificar el **actor**: rol de usuario, sistema interno, sistema externo, temporizador/scheduler o política (reacción automática)
3. Documentar la cadena: `[Actor] → [Comando] → [Evento de Dominio]`
   - ej: `Contador → SolicitarTransferenciaAgendada → TransferenciaAgendadaSolicitada`
   - ej: `Scheduler → EjecutarTransferenciaAgendada → TransferenciaAgendadaEjecutada`
4. Señalar comandos sin actor claro como hotspots

### Paso 5: Identificar Aggregates

Los aggregates son **entidades que procesan comandos y producen eventos** — aplican reglas de negocio y mantienen consistencia:

1. Agrupar comandos y eventos relacionados por la entidad que los procesa
2. Nombrar cada aggregate (sustantivo singular, PascalCase, ej: `TransferenciaAgendada`, `AsientoContable`, `EjecucionReconciliacion`)
3. Para cada aggregate, documentar:
   - **Comandos que acepta** — lista de nombres de comandos
   - **Eventos que produce** — lista de nombres de eventos de dominio
   - **Invariantes** — reglas de negocio que aplica (ej: "una transferencia no puede ejecutarse si el saldo del origen es insuficiente")
4. Identificar aggregates referenciados en múltiples comandos — candidatos potenciales a shared kernel o anti-corruption layer

### Paso 6: Identificar Políticas (Reacciones Automáticas)

Las políticas son **reacciones automáticas** que se activan en respuesta a eventos: "Cuando [Evento], entonces [Comando]":

1. Para cada evento de dominio, preguntar: "¿Este evento dispara automáticamente algo más en el sistema?"
2. Documentar cada política: `Cuando {EventoDominio} → Entonces {Comando} (en {Aggregate})`
   - ej: `Cuando TransferenciaAgendadaEjecutada → Entonces AsentarContablemente (en AsientoContable)`
   - ej: `Cuando ReconciliacionCompletada → Entonces NotificarContador (en Notificacion)`
3. Identificar políticas que **cruzan bounded contexts** — estas se convierten en eventos de integración y necesitan enrutamiento explícito

### Paso 7: Identificar Sistemas Externos y Read Models

**Sistemas externos** — servicios fuera de este bounded context:

1. Nombrar cada sistema (ej: `SocioBancario`, `AutoridadFiscal`, `ServicioNotificacion`, `ServicioContable`)
2. Identificar si cada sistema **produce eventos** (entrada) o **recibe comandos** (salida)
3. Documentar el punto de integración de cada uno

**Read models** — proyecciones de datos necesarias para soportar decisiones o vistas de usuario:

1. Nombrar cada read model (ej: `HistorialTransferenciasAgendadas`, `PanelReconciliacion`)
2. Identificar qué eventos de dominio alimentan cada read model (proyecciones)
3. Registrar el consumidor de cada vista (rol de usuario, reporte externo, Isac)

### Paso 8: Marcar Hotspots

Los hotspots son **preguntas, incertidumbres, conflictos y riesgos** que requieren resolución humana antes de la implementación:

1. Documentar cada hotspot con:
   - **Tipo** — `Pregunta` (regla o responsabilidad unclear) | `Conflicto` (dos interpretaciones válidas) | `Brecha` (evento ausente) | `Riesgo` (race condition, pérdida de datos, cumplimiento)
   - **Descripción** — declaración precisa de la incertidumbre
   - **Prioridad** — `P1` (bloquea el diseño, resolver antes de continuar) | `P2` (resolver antes de la implementación) | `P3` (puede abordarse en un follow-up)
   - **Responsable** — equipo o persona que debe resolverlo
2. No omitir este paso — los hotspots no resueltos son la principal fuente de bugs de integración y descontrol de alcance

### Paso 9: Identificar Bounded Contexts

1. Agrupar aggregates y eventos en **bounded contexts** — áreas donde los términos tienen un significado consistente y compartido
2. Nombrar cada bounded context y describir su responsabilidad (ej: `Pagos`, `Reconciliacion`, `InformeFiscal`)
3. Identificar **límites de contexto** — donde los eventos de dominio cruzan de un contexto a otro (estos se convierten en eventos publicados de integración)
4. Mapear responsabilidad: qué equipo o servicio es responsable de cada bounded context

### Paso 10: Mapear a Tipos CloudEvents

Traducir cada evento de dominio a la convención de nomenclatura CloudEvents de Guardia:

1. Para cada evento de dominio, producir el `type` CloudEvents:
   - Formato: `event.guardia.{module}.{entity_type}.{event_name}`
   - `entity_type` — nombre de la entidad en snake_case (ej: `scheduled_transfer`, `reconciliation_run`)
   - `event_name` — verbo en pasado en snake_case (ej: `created`, `approved`, `executed`, `failed`, `cancelled`)
2. Para cada tipo, definir el shape inicial de `data` según codex-entities:
   - Obligatorio: `entity_id`, `entity_type`, campos de negocio clave relevantes para consumidores
   - Omitir `history`; no incluir PII a menos que sea estrictamente necesario
3. Marcar eventos de integración (que cruzan bounded contexts) — requieren valores explícitos de `source` y `subject`

### Paso 11: Entregar el Catálogo de Descubrimiento

El descubrimiento **no se convierte en un archivo monolítico**. El resultado se entrega como input para la Fase 2 (`kata-events-doc`) y como notas que `warrior-prometheus` consolida.

Estructura interna a transmitir:

1. **Encabezado** — dominio, Bounded Context, módulo CloudEvents, fecha, alcance
2. **Línea de Tiempo de Eventos de Dominio** — lista cronológica: nombre, disparador, entidad
3. **Comandos y Actores** — tabla: Actor | Comando | Evento de Dominio
4. **Aggregates** — una subsección por aggregate: comandos aceptados, eventos producidos, invariantes
5. **Políticas** — tabla: Cuando (Evento) | Entonces (Comando) | En (Aggregate)
6. **Sistemas Externos** — tabla: Sistema | Dirección (entrada/salida) | Eventos / Comandos
7. **Read Models** — tabla: Vista | Eventos que la alimentan | Consumidor
8. **Hotspots** — tabla: Tipo | Descripción | Prioridad | Responsable
9. **Bounded Contexts** — diagrama o tabla: Contexto | Responsabilidad | Equipo | Eventos de Integración
10. **Catálogo CloudEvents** — tabla: Evento de Dominio | Tipo CloudEvents | Shape inicial de data

La persistencia canónica de los eventos descubiertos ocurre en la Fase 2, en `docs/{context}/events/events.md`, vía `kata-events-doc` + `kata-feature-design-docs`. Los hotspots y descubrimientos auxiliares son publicados por Prometheus en Notion (Guardia Platform > Domain Models).

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Catálogo CloudEvents | Tabla en memoria | Input directo para `kata-events-doc` |
| Lista de hotspots | Tabla | Notas para que `warrior-prometheus` revise y resuelva |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Dominio: Transferencias agendadas — los contadores pueden agendar transferencias bancarias para ejecutarse en una fecha futura. Un supervisor debe aprobar antes de la ejecución. El scheduler dispara la ejecución en el horario agendado.
Módulo: platform
```

### Output de Ejemplo (resumen)

Catálogo de descubrimiento entregado a la Fase 2 (`kata-events-doc`):

**Línea de tiempo:** TransferenciaAgendadaSolicitada → TransferenciaAgendadaAprobada → TransferenciaAgendadaEjecutada | TransferenciaAgendadaFallida → TransferenciaAgendadaCancelada

**Comandos y actores:**
| Actor | Comando | Evento de Dominio |
|-------|---------|-------------------|
| Contador | SolicitarTransferenciaAgendada | TransferenciaAgendadaSolicitada |
| Supervisor | AprobarTransferenciaAgendada | TransferenciaAgendadaAprobada |
| Scheduler | EjecutarTransferenciaAgendada | TransferenciaAgendadaEjecutada / TransferenciaAgendadaFallida |
| Contador | CancelarTransferenciaAgendada | TransferenciaAgendadaCancelada |

**Hotspots:**
| Tipo | Descripción | Prioridad | Responsable |
|------|-------------|-----------|-------------|
| Pregunta | ¿Qué ocurre ante fallo de ejecución: fallo inmediato o retry? Política de retry indefinida | P1 | Equipo de plataforma |
| Riesgo | Race condition si el supervisor aprueba mientras el scheduler ya está ejecutando | P1 | Equipo de plataforma |

**Catálogo CloudEvents:**
| Evento de Dominio | Tipo CloudEvents | data (campos clave) |
|---|---|---|
| TransferenciaAgendadaSolicitada | event.guardia.financial.scheduled_transfer.requested | entity_id, amount, currency, scheduled_date, requestor_id |
| TransferenciaAgendadaAprobada | event.guardia.financial.scheduled_transfer.approved | entity_id, approver_id, approved_at |
| TransferenciaAgendadaEjecutada | event.guardia.financial.scheduled_transfer.executed | entity_id, executed_at, ledger_entry_id |
| TransferenciaAgendadaFallida | event.guardia.financial.scheduled_transfer.failed | entity_id, failure_reason, failed_at |
| TransferenciaAgendadaCancelada | event.guardia.financial.scheduled_transfer.cancelled | entity_id, cancelled_by, cancelled_at |

## Restricciones

- Este Kata produce solo el catálogo de descubrimiento; no implementa publishers, consumers ni contratos de API
- No omitir la identificación de hotspots — toda incertidumbre no documentada se convierte en un bug o brecha de alcance
- El catálogo CloudEvents producido aquí DEBE ser suficientemente completo para ejecutar `kata-events-doc` sin descubrimiento adicional; señalar campos faltantes explícitamente
- Escalar a un humano cuando la responsabilidad del bounded context sea ambigua o cuando un único evento abarque múltiples aggregates sin un propietario claro
- No asumir que la línea de tiempo de eventos está completa — verificar activamente eventos ausentes en cada brecha de la cadena causal

## Referencias

- lex-cloudevents, lex-entities, lex-idempotency
- codex-cloudevents, codex-entities, codex-idempotency
- [Event Storming — Alberto Brandolini](https://www.eventstorming.com/)
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/ddd/reference/)
