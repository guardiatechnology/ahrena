# Codex: Behavior-Driven Development en Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Ingeniería — Calidad. Principios y práctica de BDD aplicados en la Fase 8 del flujo Issue-Driven.

## Visión General

Este Codex es la referencia operativa para **validación de comportamiento** de funcionalidades en Guardia. Consultado por `warrior-themis` al diseñar escenarios, por `warrior-athena` al decidir delegación y por revisores de PR en el Gate 3.

BDD aquí no es una metodología de planificación ni un framework de pruebas — es un **mecanismo de validación black-box** que protege contra "construimos la cosa equivocada", complementando la trazabilidad AC↔prueba ya exigida por `lex-issue-driven`.

## Contexto

- **Dominio:** validación de comportamiento posterior a la implementación (Fase 8 del flujo Issue-Driven).
- **Público:** `warrior-themis`, `warrior-athena`, `warrior-hera`, revisores que abren o aprueban PRs.
- **Actualización:** cuando la taxonomía de escenarios resulte insuficiente, cuando se adopten nuevos tipos de fuente (ej.: especificación en Figma) o cuando patrones anti-pattern se repitan en revisiones.

## Contenido

### 1. Por qué BDD en Guardia

La trazabilidad AC↔prueba obligada por `lex-issue-driven` Regla 3 garantiza que cada AC tiene prueba y cada prueba tiene AC. Pero no garantiza que **la prueba valide el comportamiento correcto**: un AC ambiguo puede recibir una prueba que pasa sin demostrar la regla de negocio.

BDD cierra esa rendija:

| Sin BDD | Con BDD |
|---|---|
| AC: "debe validar saldo" → prueba: `assert response.status_code == 422` | AC: "debe validar saldo" → SCN-1: "dado saldo X, cuando se solicita Y > X, entonces rechaza por saldo insuficiente" → la prueba valida la regla de negocio observable |

La diferencia es simple: **el escenario describe el comportamiento; la prueba valida el escenario**. Si el escenario fue escrito sin mirar el código (`lex-bdd-spec-only-sources`), la divergencia entre lo pedido y lo entregado aparece en el mapeo.

### 2. Jerarquía de fuentes

`warrior-themis` consulta las fuentes en este orden (siempre ciego a `src/`):

```
1. docs/issues/issue-{n}/02-requirements.md   ← ACs numerados
2. docs/issues/issue-{n}/01-brief.md          ← contexto de la Issue
3. GitHub Issue #{n}                          ← título, cuerpo, comentarios
4. Páginas Notion referenciadas               ← especificación detallada
5. docs/issues/issue-{n}/03-architecture.md   ← restricciones, contratos
6. ADRs en docs/adr/                          ← cuando se referencian
```

Si esas fuentes no alcanzan, **la Issue está incompleta** — el agente se detiene y la devuelve al origen (per `lex-bdd-spec-only-sources` Regla 4). Nunca recurre al código como atajo.

### 3. Three Amigos en nuestro contexto

El ritual clásico (PM + Dev + QA en sala) es asíncrono y distribuido aquí:

| Rol | Quién | Dónde conversa |
|---|---|---|
| PM (autor del pedido) | autor de la Issue | cuerpo de la Issue + páginas Notion |
| Tech Lead (viabilidad) | autor de `03-architecture.md` | comentarios del `03-architecture.md` y de la Issue |
| Validador (escenarios) | `warrior-themis` | `07-bdd-scenarios.md` + comentarios en la Issue para ambigüedades |

Cuando un escenario no se puede escribir a partir de las fuentes, `warrior-themis` abre comentario en la Issue listando las ambigüedades. PM y Tech Lead responden; el escenario se escribe cuando las tres voces convergen por escrito. Sin reunión sincrónica — la evidencia queda en el historial.

### 4. Taxonomía de escenarios

Cada escenario tiene **una** etiqueta de tipo. Use esta tabla como guía:

| Etiqueta | Cuándo | Regla de cobertura |
|---|---|---|
| `@happy-path` | Camino principal: input válido, flujo de éxito | **Toda AC** necesita al menos 1 |
| `@alternative` | Camino de éxito alternativo (misma intención, branch distinto) | Cuando la AC menciona "o", "si ya existe", "cuando el usuario tiene perfil X" |
| `@edge` | Límites, fronteras, datos extremos válidos | ACs con límites numéricos, rangos, fechas, tamaños máximos |
| `@error` | Falla esperada con tratamiento definido | ACs con requisito negativo explícito ("rechaza cuando", "rechaza si") |
| `@nfr` | Requisito no funcional observable (latencia, idempotencia, disponibilidad) | Cuando los NFRs son parte del AC o del `03-architecture.md` |

**Mínimo aceptable por AC:** 1 happy-path + (1 error si hay requisito negativo) + (1 edge si hay frontera numérica/temporal). Cobertura completa exige todos los tipos aplicables.

### 5. De AC a SCN

Patrón para transformar un AC numerado en escenarios:

```
AC-3: El sistema debe rechazar la programación de transferencia
       cuando el saldo disponible es menor que el monto solicitado,
       informando el motivo al cliente.
```

Se descompone en comportamientos observables:

```
SCN-3.1 @AC-3 @error
  Saldo insuficiente para el monto exacto → rechaza con motivo

SCN-3.2 @AC-3 @edge
  Saldo igual al monto (incluyendo tarifa) → rechaza por borde

SCN-3.3 @AC-3 @happy-path
  Saldo suficiente → acepta (cubre el "debe rechazar" por contraste)
```

Use el eje de la plantilla de Issue (Why/What/How) como brújula: el **What** se vuelve el `When` del escenario; el **How** observable se vuelve el `Then`; el **Why** suele quedar como contexto en la descripción de la Feature.

### 6. Lenguaje ubicuo

Los escenarios que tocan dominio core (transferencia, conciliación, asiento contable, evento contable) **DEBEN** usar los términos del modelo de dominio producido por `warrior-theseus` o por el Event Storm (`kata-event-storm`). Términos divergentes en escenarios generan drift entre diseño e implementación.

| Bueno | Malo |
|---|---|
| "el cliente programa una transferencia" | "el usuario crea un registro de transferencia" |
| "la conciliación es aprobada" | "el status del reconcile pasa a 'approved'" |
| "el asiento contable se reversa" | "la entrada del ledger se elimina" |

Cuando el término del dominio aún no existe, **el escenario crea una duda explícita** en la Issue (per Three Amigos) antes de inventar nomenclatura.

### 7. Definition of Done del conjunto de escenarios

`07-bdd-scenarios.md` está listo cuando:

1. **Toda AC tiene ≥ 1 escenario** (cobertura básica).
2. **Toda AC con requisito negativo tiene ≥ 1 `@error`**.
3. **Toda AC con frontera numérica/temporal tiene ≥ 1 `@edge`**.
4. **Frontmatter declara solo fuentes permitidas** (per `lex-bdd-spec-only-sources` Regla 3).
5. **Lint de formato pasa** (per validación de `lex-bdd-gherkin-format`).
6. **Ids `SCN-{N}` únicos** dentro del archivo.
7. **Sin ambigüedades pendientes** — comentarios en la Issue resueltos o escenarios removidos.

### 8. Anti-patterns

| Anti-pattern | Por qué es malo | Síntoma |
|---|---|---|
| Escenario imperativo ("hace clic en ...", "POST /api/...") | Se acopla a la UI/protocolo, envejece mal | El lint de `lex-bdd-gherkin-format` lo rechaza |
| Escenario por pantalla | Cubre layout, no comportamiento | Varias pantallas con el mismo escenario corriendo — Background es el lugar correcto |
| Escenario por función | Ya existe la prueba unitaria; el escenario no aporta | SCN cita nombre de función |
| Boilerplate "logueado" en el Given de cada escenario | Repetición que enmascara el `When` real | Mover a `Background` |
| `Then` sin resultado observable | El escenario no prueba nada | `Then la operación ocurre` (sin efecto declarado) |
| Escenario con orden implícito ("después de SCN-1, ...") | Rompe la independencia exigida por `lex-bdd-gherkin-format` Regla 5 | Refactorizar con Background o Given explícito |

### 9. Relación con `kata-test-plan-design`

Escenario y prueba son **complementarios**:

| Artefacto | Pregunta que responde |
|---|---|
| Escenario (BDD) | "**Qué** comportamiento debe tener el sistema?" |
| Plan de pruebas | "**En qué nivel** validamos cada comportamiento?" |
| Prueba implementada | "**Cómo** lo validamos en el código de prueba?" |

Un SCN puede mapear a 1 prueba (camino simple), 2 pruebas (unit + integración) o N pruebas (unit + integración + E2E cuando es jornada crítica). `kata-bdd-validate-implementation` produce el mapa en `08-bdd-validation-report.md`.

### 10. Glosario

| Término | Definición en Guardia |
|---|---|
| **Feature** | Bloque Gherkin que agrupa escenarios de una funcionalidad o epic |
| **Background** | Precondición compartida entre escenarios de la misma Feature, en lenguaje de negocio |
| **Scenario** | Comportamiento observable; un caso concreto Given/When/Then |
| **Scenario Outline + Examples** | Escenario paramétrico; una estructura, varios ejemplos en tabla |
| **SCN-{N}** | Identificador único del escenario, usado para rastrear ↔ prueba |
| **Lenguaje ubicuo** | Vocabulario del dominio compartido entre negocio, diseño e ingeniería |
| **Three Amigos** | PM + Tech Lead + Validador conversando sobre cada escenario (asíncrono en Guardia) |
| **Black-box validation** | Validación que ignora cómo se construye el sistema, solo observa qué hace |

## Referencias

- `lex-bdd-spec-only-sources` — fuentes permitidas para derivar escenarios
- `lex-bdd-gherkin-format` — formato Gherkin obligatorio
- `lex-bdd-no-framework-coupling` — implementación de pruebas sin step-runner
- `codex-gherkin` — manual del Gherkin adoptado
- `codex-test-strategy` — elección de niveles de prueba
- `kata-bdd-scenarios-design` — producción del `07-bdd-scenarios.md`
- `kata-bdd-validate-implementation` — producción del `08-bdd-validation-report.md`
- `warrior-themis` — agente de la Fase 8
- `lex-issue-driven` — flujo que precede a la Fase 8
- [North, "Introducing BDD" (2006)](https://dannorth.net/introducing-bdd/)
