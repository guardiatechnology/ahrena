# Cry: Feature Design — Dominio, API y Eventos

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ciclo completo de diseño de feature: modelado de dominio, diseño de API REST y documentación de CloudEvents en secuencia

## Descripción

Este comando activa al **Warrior Prometheus** (Technical Product Manager) para orquestar el ciclo completo de diseño de feature en tres fases secuenciales: modelado de dominio (warrior-theseus), diseño de API (warrior-daedalus) y documentación de eventos (warrior-kronos). Cada fase usa el output de la fase anterior como input autoritativo. El usuario confirma cada fase antes de que comience la siguiente.

## Uso

```
/cry-feature-design <descripción de la feature> [módulo] [restricciones]
```

## Parámetros

| Parámetro | Requerido | Descripción | Ejemplo |
|-----------|:---------:|-------------|---------|
| `descripción de la feature` | Sí | Descripción del alcance de la feature, objetivo de negocio y cualquier regla o actor conocido | "Transferencias agendadas: contadores crean, supervisores aprueban, ejecutadas en la fecha agendada" |
| `módulo` | No | Identificador del módulo CloudEvents. Si se omite, Prometheus preguntará | `platform` |
| `restricciones` | No | Restricciones conocidas: seguridad, compliance, integraciones existentes, restricciones de breaking change | "Sin breaking changes en los endpoints existentes /v1/transfers" |

## Lo que Hace el Comando

1. **Asume el rol del warrior-prometheus** y lee `.ahrena/.directives` para obtener `paths.domain`, `paths.oas`, `paths.events` y `language.default`
2. **Hace preguntas de clarificación** si la descripción de la feature, módulo o restricciones son insuficientes
3. **Fase 1 — Modelado de Dominio (warrior-theseus):** modela el dominio de forma iterativa; resuelve hotspots P1; confirma el modelo de dominio con el usuario antes de proceder
4. **Fase 2 — Diseño de API (warrior-daedalus):** diseña la API usando el modelo de dominio como input autoritativo; confirma el diseño de API con el usuario antes de proceder
5. **Fase 3 — Documentación de Eventos (warrior-kronos):** documenta CloudEvents usando modelo de dominio + eventos de integración de la Fase 1; omite el descubrimiento (ya realizado); confirma la documentación de eventos con el usuario
6. **Verificación de consistencia:** verifica que los nombres de entidad, valores de entity_type y segmentos del tipo CloudEvents coincidan con el modelo de dominio en todos los outputs
7. **Entrega el paquete final de artefactos** con los paths de todos los archivos producidos

## Template de Prompt

```
Contexto:
- Descripción de la feature: {{descripción de la feature}}
- Módulo (opcional): {{módulo}}
- Restricciones (opcional): {{restricciones}}

Tarea:
Actúa como el Warrior Prometheus (Technical Product Manager). Lee `.ahrena/.directives` para obtener `paths.domain`, `paths.oas`, `paths.events` y `language.default`.

Si la descripción de la feature, módulo o restricciones son insuficientes, haz preguntas de clarificación antes de comenzar.

Orquesta el ciclo completo de diseño de feature en secuencia:

1) **Fase 1 — Modelado de Dominio (warrior-theseus):** Delega al warrior-theseus con la descripción de la feature y el módulo. Monitorea hotspots P1 — no avances hasta que estén resueltos. Presenta el resumen del modelo de dominio (catálogo de entidades, use cases, eventos de integración) y pregunta: "¿El modelo de dominio es correcto? ¿Debo proceder al diseño de API?"

2) **Fase 2 — Diseño de API (warrior-daedalus):** Tras confirmación explícita del usuario, delega al warrior-daedalus usando el documento de modelo de dominio como input principal. Instruye a Daedalus a usar los valores de entity_type y nombres de campo del modelo de dominio (lex-entity-naming). Presenta el resumen del diseño de API y pregunta: "¿El diseño de API es correcto? ¿Debo proceder a la documentación de eventos?"

3) **Fase 3 — Documentación de Eventos (warrior-kronos):** Tras confirmación explícita del usuario, delega al warrior-kronos con modelo de dominio + lista de eventos de integración. Instruye a Kronos a omitir el descubrimiento (los eventos fueron identificados en la Fase 1) e ir directamente a la documentación. Verifica que los segmentos del tipo CloudEvents coincidan con los valores de entity_type del modelo de dominio. Presenta el resumen de eventos.

Tras todas las fases, verifica la consistencia: los nombres de entidad en APIs y eventos deben coincidir con el modelo de dominio. Señala cualquier divergencia con un camino claro de resolución.

Entrega el paquete final de artefactos:
- Modelo de dominio: `paths.domain/{módulo}-domain-model.md`
- Especificación de API: `paths.oas/{módulo}-api.yaml` (OAS) y `paths.oas/{módulo}-api.md` (doc)
- Documento de eventos: `paths.events/{módulo}-events.md`
```

## Ejemplo de Invocación

**Input:**

```
/cry-feature-design "Transferencias agendadas: contadores agendan una transferencia para una fecha futura, supervisores aprueban transferencias por encima de $ 10.000, el sistema ejecuta en la fecha agendada, los fallos disparan un reintento tras 30 minutos" platform
```

**Output esperado:**

- **Confirmación Fase 1:** Catálogo de entidades (`ScheduledTransfer`, entity_type `scheduled_transfer`), ciclo de vida, use cases, eventos de integración — usuario confirma antes de la Fase 2
- **Confirmación Fase 2:** Endpoints (POST /v1/scheduled-transfers, GET, GET/:id, PATCH, DELETE), Idempotency-Key, payloads — usuario confirma antes de la Fase 3
- **Confirmación Fase 3:** Catálogo de CloudEvents (`event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`) — resumen final
- **Paquete de artefactos:**
  - `docs/domain/platform-domain-model.md`
  - `docs/oas/platform-api.yaml`
  - `docs/oas/platform-api.md`
  - `docs/events/platform-events.md`

## Cuándo Usar Este Cry vs Otros

| Cry | Cuándo usar |
|-----|-------------|
| **cry-feature-design** | El dominio es desconocido o debe modelarse; se necesita un paquete consistente dominio → API → eventos |
| **cry-full-design** | El dominio ya está modelado; solo se necesita API + eventos a partir de una descripción de feature |
| **cry-api-design** | El dominio está modelado y los eventos están fuera del alcance; solo se necesita la API |
| **cry-event-storm** | Solo se necesita descubrimiento o documentación de eventos (el dominio y la API ya existen) |

## Restricciones

- No implementa código — solo orquesta el diseño
- No avanza a la siguiente fase sin confirmación explícita del usuario
- No omite la Fase 1 (modelado de dominio) cuando el dominio es genuinamente desconocido — un dominio mal modelado produce APIs y eventos incorrectos
- Las excepciones a las Lexis deben documentarse en un ADR; Prometheus señalará cuando una decisión lo requiera

## Warriors y Katas Asociados

| Artefacto | Rol |
|-----------|-----|
| `warrior-prometheus` | Orquestador — invocado por este Cry |
| `warrior-theseus` | Fase 1 — Modelado de Dominio |
| `warrior-daedalus` | Fase 2 — Diseño de API |
| `warrior-kronos` | Fase 3 — Documentación de Eventos |
| `kata-domain-model` | Ejecutado por warrior-theseus |
| `kata-api-design-oas` | Ejecutado por warrior-daedalus |
| `kata-api-design-doc` | Ejecutado por warrior-daedalus |
| `kata-events-doc` | Ejecutado por warrior-kronos |

## Referencias

- `warrior-prometheus` — Technical Product Manager y orquestrador de diseño de feature
- `lex-entity-naming` — reglas snake_case/PascalCase aplicadas en todas las fases
- `lex-entities` — estructura base de entidades (entity_id, entity_type, version, timestamps) consultada durante el modelado de dominio
- `lex-cloudevents` — formato del tipo CloudEvents consultado durante la documentación de eventos
