# Codex: Domain-Driven Design

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Modelado estratégico y táctico de dominios complejos

## Resumen

Este Codex orienta decisiones de Domain-Driven Design sin reducir DDD a una estructura de carpetas o catálogo obligatorio de patterns. Se comienza por lenguaje, fronteras, ownership e invariantes; los patterns tácticos aparecen solo cuando la complejidad los justifica.

## Contexto

- **Dominio:** diseño de bounded contexts, modelos e integraciones
- **Público objetivo:** ingeniería, producto, expertos de dominio y agentes de diseño
- **Actualización:** cuando cambien arquitectura por componentes, taxonomía de entidades o contratos de eventos

## Contenido

### Principios

1. **Estratégico antes que táctico:** Lenguaje Ubicuo, subdominios, bounded contexts y Context Map preceden a Aggregate, Repository o Domain Service.
2. **Modelo local:** un término puede tener modelos diferentes entre contextos; la traducción explícita protege cada lenguaje.
3. **Aggregate por invariante:** la frontera garantiza consistencia transaccional, no similitud con tablas o árboles de objetos.
4. **Complejidad ganada:** un CRUD simple no necesita imitar un dominio rico; el modelo evoluciona cuando aparecen reglas y conflictos.
5. **Eventos semánticos:** Domain Event registra un hecho interno; Integration Event es un contrato publicado y puede requerir outbox, versión y política de datos.

### Secuencia de Decisión

| Gate | Pregunta | Evidencia esperada |
|---|---|---|
| Lenguaje | ¿Son explícitos los términos y conflictos de significado? | Glosario y ejemplos aceptados por el dominio |
| Frontera | ¿Quién decide y posee datos y reglas? | Bounded context y responsables |
| Relación | ¿Cómo dependen y traducen modelos los contextos? | Context Map y contrato publicado |
| Consistencia | ¿Qué reglas deben cumplirse en el mismo commit? | Invariantes y límite del Aggregate |
| Persistencia | ¿Qué concurrencia y fallos importan? | Unidad de trabajo, versión y política de retry |
| Integración | ¿Qué hecho puede salir y con qué garantía? | Evento versionado, outbox/inbox e idempotencia según necesidad |

### Patterns Tácticos — Cuándo No Usarlos

| Pattern | Usar cuando | Evitar cuando |
|---|---|---|
| Entity | Importan identidad y ciclo de vida | El valor depende solo de sus atributos |
| Value Object | Concepto inmutable con invariantes | Es solo una bolsa de datos |
| Aggregate | Invariantes exigen consistencia conjunta | Los objetos solo necesitan consulta/join |
| Repository | El dominio necesita una colección abstracta | Un handler CRUD directo es suficiente y claro |
| Domain Service | La regla no pertenece naturalmente a Entity/VO | Es solo orquestación de IO |
| CQRS | Lectura y escritura tienen presiones distintas comprobadas | CRUD común sin asimetría demostrada |
| Event Sourcing | El historial es el modelo primario y existe capacidad operativa | Basta un log de auditoría simple |

### Fronteras Operativas

- Una transacción local no abarca HTTP, colas o proveedores externos.
- Un commit incierto exige reconciliación; retries ciegos pueden duplicar efectos financieros.
- La consistencia eventual declara ventana, indicador de retraso, reprocesamiento y responsable.
- Integraciones externas usan Adapter/ACL cuando los vocabularios divergen.

### Decisiones Vigentes

| Decisión | Estado | Consecuencia |
|---|---|---|
| DDD-first comienza por comprender el dominio | Confirmada | El documento no es un formulario de Aggregate |
| El layout físico es guía, no definición de DDD | Confirmada | Validadores estructurales no reemplazan revisión semántica |
| Diccionario consultable de patterns | Propuesta para Ahrena v2 | Este Codex aporta criterios que el catálogo debe preservar |

### Restricciones Técnicas

- No derivar bounded contexts directamente de tablas, equipos o endpoints sin evidencia de lenguaje y ownership.
- No permitir acceso externo directo a miembros internos del Aggregate.
- No confundir Domain Event con Integration Event ni publicar datos sensibles por conveniencia.
- No imponer una única arquitectura de capas o carpetas a todas las stacks.

## Glosario

| Término | Definición |
|---|---|
| Bounded Context | Frontera donde lenguaje y modelo tienen significado consistente |
| Invariante | Regla que permanece verdadera durante un cambio de estado |
| Context Map | Relaciones y dirección de dependencia entre bounded contexts |
| Hotspot | Ambigüedad o conflicto que requiere más descubrimiento |

## Referencias

- `kata-domain-model`, `codex-component-architecture`, `codex-feature-design-docs`
- `lex-entities`, `lex-entity-naming`, `lex-cloudevents`, `lex-idempotency`
