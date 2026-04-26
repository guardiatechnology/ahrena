# Kata: Modelado de Dominio (DDD)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Plataforma Guardia — descubrimiento y modelado de dominio para una feature o módulo usando Domain-Driven Design

## Objetivo

Producir un modelo de dominio completo para una feature o módulo mediante diálogo DDD estructurado con el usuario: establecer el Lenguaje Ubicuo, mapear Bounded Contexts, definir Entidades y Agregados (conforme a lex-entities y lex-entity-naming), documentar Use Cases y Application Services, identificar eventos de integración y anti-corruption layers, y dibujar un Context Map. El output alimenta directamente el diseño de API (warrior-daedalus) y la documentación de eventos (warrior-kronos).

## Cuándo Usar

- Antes de diseñar APIs o documentar eventos para una nueva feature o módulo
- Cuando el dominio es complejo, tiene múltiples actores o cruza fronteras de servicio
- Cuando es invocado por warrior-theseus o warrior-prometheus como primera fase del diseño de feature
- Cuando el equipo necesita un Lenguaje Ubicuo compartido antes del inicio de la implementación

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Descripción del dominio | Sí | Dominio de negocio, alcance de la feature o módulo a modelar |
| Nombre del módulo | Sí | Identificador del módulo Guardia (ej.: `platform`, `reconciliation`, `fiscal`) |
| Entidades conocidas | No | Entidades ya identificadas; si se proporcionan, validar y extender a partir de ellas |
| Alcance de bounded context | No | Único o múltiples contextos; si se omite, el agente determina a partir de la descripción |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Leer directivas y alcance
- [ ] 2. Consultar Lexis y Codex
- [ ] 3. Elicitar descripción del dominio
- [ ] 4. Definir Lenguaje Ubicuo
- [ ] 5. Mapear Bounded Contexts
- [ ] 6. Definir Entidades y Agregados
- [ ] 7. Definir Use Cases y Application Services
- [ ] 8. Identificar eventos de integración y anti-corruption layers
- [ ] 9. Dibujar Context Map
- [ ] 10. Producir documento de modelo de dominio
```

### Paso 1: Leer Directivas y Alcance

1. Leer `.ahrena/.directives` para obtener `paths.domain`, `language.default` y nombre del módulo
2. Confirmar que la descripción del dominio y el nombre del módulo fueron proporcionados; si son insuficientes, **preguntar al usuario** (¿Cuál es el proceso de negocio principal? ¿Quiénes son los actores? ¿Cuáles son los límites del sistema? ¿Qué desencadena la primera acción?) y esperar respuestas
3. Verificar si ya existe un documento de modelo de dominio en `paths.domain` para este módulo — incorporarlo como input si está disponible
4. Identificar el alcance de bounded context: único o múltiples contextos

### Paso 2: Consultar Lexis y Codex

1. Consultar **lex-entities** — toda entidad persistente DEBE tener entity_id (UUID v7), entity_type, version, created_at, updated_at, discarded_at
2. Consultar **lex-entity-naming** — `entity_type` y nombres de campo usan snake_case; nombres de agregados en documentos DDD usan PascalCase
3. Consultar **lex-cloudevents** — los eventos siguen `event.guardia.{module}.{entity_type}.{event_name}` con segmentos en snake_case
4. Consultar **codex-entities** — referencia del modelo de entidades base

### Paso 3: Elicitar Descripción del Dominio

Si la descripción del dominio es insuficiente para iniciar el modelado, hacer preguntas dirigidas al usuario:

1. **Proceso de negocio:** "Describa el flujo principal paso a paso. ¿Qué lo inicia y qué lo concluye?"
2. **Actores:** "¿Quién inicia las acciones — usuarios, sistemas externos, jobs programados?"
3. **Reglas de negocio:** "¿Cuáles son las principales restricciones? ¿Qué puede o no puede ocurrir?"
4. **Límites del sistema:** "¿Qué está dentro de este módulo y qué pertenece a otro servicio?"
5. **Puntos problemáticos conocidos:** "¿Hay áreas del dominio que no están claras o son disputadas?"

Esperar respuestas antes de proceder al Paso 4.

### Paso 4: Definir Lenguaje Ubicuo

Establecer un vocabulario compartido que especialistas de dominio e ingenieros usarán consistentemente:

1. Para cada término clave del dominio, documentar:
   - **Término** — nombre acordado (PascalCase para entidades/agregados, simple para conceptos)
   - **Definición** — significado preciso en este bounded context
   - **Sinónimos a evitar** — términos alternativos que no deben usarse (para evitar ambigüedad)
2. Resolver conflictos de nomenclatura: si dos stakeholders usan términos diferentes para el mismo concepto, acordar uno y documentar el alternativo rechazado
3. Validar términos contra lex-entity-naming: nombres de entidad en snake_case para APIs/eventos, PascalCase en documentos DDD

Ejemplo de entrada en el glosario:
| Término | Definición | Sinónimos a Evitar |
|---------|------------|-------------------|
| ScheduledTransfer | Transferencia bancaria ordenada por un contador para ejecución en fecha futura, requiriendo aprobación del supervisor | "transferencia planificada", "pago futuro" |
| Execution | El momento en que la transferencia es procesada por el socio bancario en la fecha programada | "procesamiento", "liquidación" |

### Paso 5: Mapear Bounded Contexts

Un Bounded Context es un límite dentro del cual un modelo de dominio específico está definido y es aplicable:

1. Identificar límites donde los términos cambian de significado o la responsabilidad cambia
2. Para cada Bounded Context, documentar:
   - **Nombre** — descriptivo, refleja su responsabilidad (ej.: `ScheduledPayments`, `Approval`, `Reconciliation`)
   - **Responsabilidad** — qué posee y decide
   - **Responsable** — equipo o servicio responsable
   - **Entidades que posee** — lista de agregados dentro de este contexto
3. Marcar entidades que aparecen en múltiples contextos — requerirán mapeo explícito en los límites
4. Señalar límites de contexto que no están claros como hotspots

### Paso 6: Definir Entidades y Agregados

#### Entidades

Para cada entidad persistente, documentar (conforme a lex-entities):

| Campo | Requisito |
|-------|-----------|
| Nombre | PascalCase en documento DDD; snake_case como `entity_type` en APIs/eventos |
| `entity_type` | Cadena en snake_case (ej.: `scheduled_transfer`) |
| Bounded Context | Qué contexto es dueño de esta entidad |
| Campos clave | Atributos relevantes para el negocio (más allá de la estructura base) |
| Estados del ciclo de vida | Estados por los que transita la entidad (ej.: `requested → approved → executed`) |

Todas las entidades DEBEN incluir la estructura base de lex-entities: `entity_id`, `entity_type`, `version`, `created_at`, `updated_at`, `discarded_at`.

#### Agregados

Un Agregado es un conjunto de entidades y value objects tratados como una única unidad con una entidad raíz:

1. Identificar la **Raíz del Agregado** — el punto de entrada; todas las referencias externas pasan por ella
2. Documentar:
   - **Raíz del Agregado** — la entidad raíz (ej.: `ScheduledTransfer`)
   - **Miembros** — entidades y value objects dentro del límite del agregado
   - **Invariantes** — reglas de negocio que siempre se mantienen en el agregado (ej.: "Un ScheduledTransfer no puede ejecutarse si su estado no es `approved`")
   - **Comandos aceptados** — operaciones que el agregado procesa
   - **Eventos producidos** — eventos de dominio emitidos en el cambio de estado

### Paso 7: Definir Use Cases y Application Services

Los Use Cases describen lo que el sistema hace desde la perspectiva del actor:

1. Para cada use case, documentar:
   - **Nombre** — verbo imperativo + sustantivo (ej.: `RequestScheduledTransfer`, `ApproveScheduledTransfer`)
   - **Actor** — quién lo inicia (rol de usuario, sistema externo, scheduler)
   - **Precondiciones** — qué debe ser verdadero antes de que el use case pueda ejecutarse
   - **Pasos** — secuencia ordenada de acciones
   - **Postcondiciones** — qué es verdadero después de la ejecución exitosa
   - **Caminos de fallo** — qué ocurre cuando el use case no puede completarse (listar como hotspots si no están definidos)
   - **Agregado afectado** — qué agregado procesa el comando
   - **Eventos emitidos** — eventos de dominio producidos en el éxito

2. Agrupar use cases por actor o por agregado para mejorar la legibilidad

### Paso 8: Identificar Eventos de Integración y Anti-Corruption Layers

**Eventos de integración** cruzan límites de bounded context:

1. Para cada evento que debe salir del bounded context, documentar:
   - **Tipo de evento** — `event.guardia.{module}.{entity_type}.{event_name}` (lex-cloudevents)
   - **Publicador** — qué bounded context / agregado lo produce
   - **Consumidores** — qué contextos lo consumen
   - **Esquema de payload** — campos de datos principales (snake_case conforme lex-entity-naming)
2. Señalar eventos donde el mismo concepto tiene nombres diferentes en distintos contextos — requieren **traducción en el límite**

**Anti-Corruption Layers (ACL):**

1. Identificar sistemas externos cuyos modelos difieren del modelo de dominio Guardia
2. Para cada ACL, documentar:
   - **Sistema externo** — nombre y responsable
   - **Traducción** — cómo los conceptos externos se mapean a entidades Guardia
   - **Dirección** — entrada (externo → Guardia) o salida (Guardia → externo)

### Paso 9: Dibujar Context Map

Producir un Context Map textual o en tabla Markdown mostrando relaciones entre bounded contexts:

| Patrón de Relación | Cuándo Usar |
|--------------------|-------------|
| **Shared Kernel** | Dos contextos comparten un subconjunto del modelo de dominio; los cambios requieren coordinación |
| **Customer/Supplier** | El contexto upstream provee lo que el downstream consume; el downstream tiene requisitos |
| **Conformist** | El downstream adopta el modelo upstream sin influencia |
| **Anti-Corruption Layer** | El downstream traduce el modelo upstream para proteger el suyo |
| **Open Host Service** | El upstream publica un protocolo / API para múltiples downstreams |
| **Published Language** | Lenguaje compartido (ej.: CloudEvents) usado entre contextos |

Para cada par de contextos con relación, documentar el patrón y cualquier restricción.

### Paso 10: Producir Documento de Modelo de Dominio

Generar un documento Markdown estructurado y guardarlo en `paths.domain`:

1. **Encabezado** — módulo, descripción del dominio, fecha, participantes, alcance
2. **Lenguaje Ubicuo** — tabla de glosario: Término | Definición | Sinónimos a Evitar
3. **Bounded Contexts** — una subsección por contexto: nombre, responsabilidad, responsable, entidades que posee
4. **Catálogo de Entidades y Agregados** — tabla: Entidad | entity_type | Bounded Context | Estados del Ciclo de Vida | Raíz del Agregado
5. **Detalles de Agregados** — una subsección por agregado: raíz, miembros, invariantes, comandos, eventos
6. **Use Cases** — una subsección por use case: actor, precondiciones, pasos, postcondiciones, caminos de fallo, eventos emitidos
7. **Eventos de Integración** — tabla: Tipo de Evento | Publicador | Consumidores | Esquema de Payload
8. **Anti-Corruption Layers** — tabla: Sistema Externo | Dirección | Traducción
9. **Context Map** — tabla o diagrama: Contexto A | Relación | Contexto B | Restricciones
10. **Hotspots Abiertos** — tabla: Descripción | Prioridad (P1/P2/P3) | Responsable

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Documento de modelo de dominio | Markdown | `paths.domain` (ej.: `docs/domain/{module}-domain-model.md`) |
| Glosario de lenguaje ubicuo | Tabla en el documento | Compartido con el equipo antes de la implementación |
| Catálogo de entidades/agregados | Tabla en el documento | Input para warrior-daedalus (APIs) y warrior-kronos (eventos) |
| Lista de eventos de integración | Tabla en el documento | Input para warrior-kronos (documentación de eventos) |

## Ejemplo de Ejecución

### Input

```
Dominio: Transferencias agendadas — contadores programan transferencias bancarias futuras; aprobación del supervisor obligatoria antes de la ejecución; un scheduler dispara la ejecución en la fecha programada.
Módulo: platform
```

### Resumen del Output

Archivo `docs/domain/platform-domain-model.md` conteniendo:

**Lenguaje Ubicuo:**
| Término | Definición | Sinónimos a Evitar |
|---------|------------|-------------------|
| ScheduledTransfer | Transferencia ordenada para ejecución futura, requiriendo aprobación | "transferencia planificada", "pago futuro" |
| Execution | Procesamiento por el socio bancario en la fecha programada | "procesamiento", "liquidación" |

**Bounded Contexts:** `ScheduledPayments` (dueño de ScheduledTransfer), `Approval` (dueño del flujo de aprobación), `BankingIntegration` (ACL para el socio bancario)

**Catálogo de Entidades:**
| Entidad | entity_type | Bounded Context | Ciclo de Vida |
|---------|-------------|-----------------|---------------|
| ScheduledTransfer | `scheduled_transfer` | ScheduledPayments | requested → approved → executed \| failed \| cancelled |

**Use Cases:** `RequestScheduledTransfer`, `ApproveScheduledTransfer`, `ExecuteScheduledTransfer`, `CancelScheduledTransfer`

**Eventos de Integración:** `event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`

**Hotspots Abiertos:**
| Descripción | Prioridad | Responsable |
|-------------|-----------|-------------|
| Política de retry ante fallo de ejecución no definida | P1 | Equipo de plataforma |

## Restricciones

- Este Kata produce solo el documento de modelo de dominio; no diseña APIs ni documenta CloudEvents
- No omitir la identificación de hotspots — toda incertidumbre no documentada se convierte en un bug o brecha de alcance
- El catálogo de entidades DEBE ser lo suficientemente completo para alimentar warrior-daedalus y warrior-kronos sin descubrimiento adicional
- Escalar a un humano cuando la responsabilidad del bounded context sea ambigua o cuando un único agregado abarque múltiples equipos sin un dueño claro
- Los valores de entity_type en el catálogo DEBEN estar en snake_case (lex-entity-naming); los nombres de agregados en las secciones DDD DEBEN estar en PascalCase

## Referencias

- `lex-entities` — estructura base de entidades
- `lex-entity-naming` — snake_case para entity_type, campos y segmentos CloudEvents
- `lex-cloudevents` — formato del tipo CloudEvents
- `codex-entities` — referencia del modelo de entidades
- [Domain-Driven Design — Eric Evans](https://www.domainlanguage.com/ddd/reference/)
- [Implementing Domain-Driven Design — Vaughn Vernon](https://vaughnvernon.com/)
