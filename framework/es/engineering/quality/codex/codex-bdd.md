# Codex: Behavior-Driven Development en Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Metodología BDD usada en proyectos Guardia — cuándo, por qué y cómo se redactan los escenarios desde fuentes de negocio, se mapean a pruebas y se mantienen en el tiempo

## Visión general

Este Codex es la referencia operacional para la **redacción y cobertura de escenarios BDD** en Guardia. Consultado por `warrior-hera` al diseñar planes de prueba, por agentes que ejecutan `kata-bdd-create-scenarios` y `kata-bdd-validate-scenarios`, y por revisores de código que verifican que escenarios y pruebas se mantengan alineados.

BDD aquí es **opcional e independiente**. No es una fase del flujo Issue-Driven. Los equipos lo adoptan para features donde la intención de negocio se beneficia de ser capturada en lenguaje de dominio antes de que comience la implementación. Cuando se adopta, aplican `lex-bdd-scenarios` y `lex-bdd-coverage`.

## Contexto

- **Dominio:** especificación de comportamiento mediante escenarios Gherkin derivados de fuentes de negocio (issue + Notion), con mapeo a pruebas en cualquier nivel vía marcadores canónicos.
- **Público objetivo:** `warrior-hera`, agentes que redactan o validan escenarios, revisores de código.
- **Actualización:** cuando cambia el stack de pruebas (nuevo framework adoptado), cuando evoluciona la convención de marcador canónico, cuando un proyecto elige adoptar un Gherkin runner (addendum a nivel de proyecto, no por defecto del framework).

## Contenido

### Por qué BDD aquí, por qué independiente

El flujo Issue-Driven ya impone criterios de aceptación numerados con trazabilidad AC↔prueba. BDD agrega una **capa en lenguaje de negocio** entre el issue y las pruebas. Es útil cuando la brecha entre los ACs técnicos y la intención de negocio es lo suficientemente amplia como para que los escenarios capturen la intención con más claridad que ACs en formato Given/When/Then. Para la mayoría de issues esto es overhead. Para features tier-1, reglas de dominio complejas y procesos regulados (pago, reembolso, ledger), vale la pena.

Independiente, porque no bloquea a equipos que no lo usan. `/cry-bdd-create-scenarios` y `/cry-bdd-validate-scenarios` son puntos de entrada autónomos que se ejecutan antes, después o totalmente fuera del flujo Issue-Driven.

### Orientado al negocio vs orientado a API/UI — la diferencia

Las plantillas de contribución `user-story-for-api.md` y `user-story-for-frontend.md` ya traen escenarios Gherkin, pero esos escenarios codifican el **contrato** (HTTP, superficie de UI). Son útiles para contract testing y permanecen en el issue. Los escenarios orientados al negocio codifican la **intención** detrás del contrato.

| Aspecto | Escenario API/UI (plantilla) | Escenario de negocio (BDD) |
|---|---|---|
| Sujeto | La superficie API/UI | La operación de dominio |
| Vocabulario | Verbo/ruta HTTP, código de estado, campo de payload, selector DOM | Actor, entidad, resultado de negocio |
| Audiencia | Revisores de backend/frontend, integradores | Producto, expertos de dominio, todos los ingenieros |
| Estabilidad | Cambia cuando cambia el contrato | Cambia cuando cambia la regla de negocio |
| Objetivo de la prueba | Contract test (E2E API, UI E2E) | Cualquier nivel, donde resida la regla |

Ambas formas coexisten. La cry duplica el escenario API/UI en una forma de negocio; no lo reemplaza.

### Convenciones Gherkin usadas aquí

Usar solo `Scenario`, `Given`, `When`, `Then`, `And`. No usar `Background`, `Scenario Outline` ni tablas `Examples` — fomentan la deriva técnica y mapeos más difíciles. Un comportamiento observable por escenario. Titular cada escenario con una frase que el equipo de producto reconozca.

```gherkin
Scenario: Customer requests a refund for an eligible payment
  Given a captured payment of 1000 BRL made by the customer in the last 30 days
  When the customer requests a refund for that payment
  Then a refund is recorded against the payment in pending state
  And the audit trail records the refund attempt with the requesting customer
```

Los escenarios viven en el cuerpo del issue, entre marcadores dedicados:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...

Scenario: ...
<!-- bdd:scenarios:end -->
```

Re-ejecutar la kata de redacción reemplaza solo este bloque, nunca ninguna otra parte del cuerpo.

### Fuente de verdad

| Fuente | Rol |
|---|---|
| Cuerpo del issue de GitHub (bloque `bdd:scenarios`) | El registro canónico y mutable. |
| Páginas de Notion | Contexto de enriquecimiento (estrategia de producto, decisiones previas). No es donde viven los escenarios. |
| Código (servicios, pruebas, OAS) | Fuente prohibida. El código refleja lo que fue construido; los escenarios reflejan lo que se quiere. |

### Convenciones de mapeo a pruebas (tabla completa)

`<scenario-slug>` es la forma kebab-case de `Scenario: <title>`. Ejemplo: `Customer requests a refund for an eligible payment` → `customer-requests-a-refund-for-an-eligible-payment`.

| Stack | Marcador canónico | Fallback (nombre de prueba o docstring) |
|---|---|---|
| Python / pytest | decorador `@bdd_scenario("scenario-slug")` | `BDD: <title>` en el docstring |
| JS/TS (Jest, Vitest) | etiqueta JSDoc `// @bdd_scenario scenario-slug`, o wrapper `bddScenario("scenario-slug", () => { ... })` | `BDD: <title>` en el nombre de la prueba |
| Go | `// bdd_scenario: scenario-slug` arriba de `func TestXxx` | `BDD<Slug>` en el nombre de la función |
| Genérico | docstring o nombre de prueba que coincida con `BDD:\s*<title-or-slug>` | — |

Una prueba PUEDE mapear a más de un escenario cuando legítimamente ejercita múltiples comportamientos a la vez (raro; preferir un escenario por prueba).

### El identificador `bdd_scenario`

`bdd_scenario` es el token canónico, estable a grep, entre stacks. El framework no entrega el decorador de Python ni el wrapper de JS/TS. Los proyectos que adopten BDD definen un pequeño helper local para que el call site quede limpio.

Helper de Python de referencia:

```python
# project/tests/conftest.py (or a small bdd.py utility)
import pytest

def bdd_scenario(slug: str):
    """Mark a test as covering a BDD scenario by its kebab-case slug."""
    return pytest.mark.bdd_scenario(slug)
```

Helper de JS/TS de referencia:

```typescript
// tests/_helpers/bdd.ts
export function bddScenario(slug: string, body: () => void): void {
  // The slug surfaces in test reporting via the test name and via the
  // `// @bdd_scenario <slug>` JSDoc tag; either is sufficient for the
  // validation kata to pick the mapping up.
  body();
}
```

La kata de validación reconoce el token canónico independientemente de cómo esté implementado el helper, mientras el slug del escenario viaje con él.

### Qué hace bueno a un escenario

| Propiedad | Detalle |
|---|---|
| Comportamiento único | Un solo triple Given/When/Then por escenario; múltiples líneas `And` para contexto están bien, pero la aserción es única. |
| Resultado observable | `Then` describe algo que un stakeholder puede verificar (existe un registro, se envió una notificación, cambió un saldo). El estado interno ("la caché fue invalidada") es detalle de implementación y no pertenece aquí. |
| Redacción estable | Los títulos de escenario son lo suficientemente estables como para mapear por slug. Renombrar es un breaking change para la trazabilidad (Regla 6 de `lex-bdd-coverage`). |
| Vocabulario de dominio | Un product manager entiende cada palabra. Si parsearlo requiere leer la spec de la API, reescribir. |

### Anti-patterns

| Anti-pattern | Por qué es malo |
|---|---|
| Copiar el escenario API verbatim al bloque de negocio | Anula el propósito; ambas versiones se vuelven ruido. |
| Múltiples resultados `Then` por escenario | El escenario se vuelve un checklist; las pruebas que cubren se vuelven difusas; el mapeo se vuelve ambiguo. |
| Renombrar escenarios a la ligera | Rompe el mapeo por slug. Renombrar = tratar como breaking change para la trazabilidad y actualizar los marcadores en el mismo cambio. |
| Redactar escenarios desde el código base | Codifica lo que el sistema hace, no lo que el negocio quiere. Anula BDD por completo. |
| Imponer un Gherkin runner | Agrega peso de herramientas sin agregar señal. Las pruebas son el artefacto ejecutable; el mapeo es el contrato. |
| Asertar sobre estado interno | Los escenarios hablan solo de resultados observables externamente. El estado interno es una elección de implementación. |

### Ciclo de vida de un escenario

1. Redactado desde el issue y Notion (`/cry-bdd-create-scenarios`).
2. Persistido en el cuerpo del issue dentro de los marcadores `bdd:scenarios`.
3. Mapeado desde el código de prueba durante la implementación (marcador canónico agregado).
4. Validada la cobertura bajo demanda (`/cry-bdd-validate-scenarios`) y en la revisión del PR.
5. Cuando cambia la regla de negocio: reescribir el escenario en el issue primero, luego actualizar las pruebas que lo cubren en el mismo cambio. El mapeo es un contrato; ambos extremos se mueven juntos.

### Relación con el flujo Issue-Driven

| Evento del flujo | Interacción con BDD |
|---|---|
| La Fase 2 (`kata-requirements-brief`) produce ACs numerados | Los escenarios PUEDEN complementar los ACs; ambos pueden coexistir en el issue. |
| Fase 4 (implementación) | Las pruebas llevan tanto marcadores `@ac("AC-N")` como `@bdd_scenario("...")` cuando ambas capas existen. |
| Gate 2 (`kata-quality-gate`) | Valida el mapeo AC↔prueba. La cobertura BDD se verifica por separado mediante `kata-bdd-validate-scenarios`. |

Las dos superficies permanecen ortogonales. Ninguna bloquea a la otra.

## Glosario

| Término | Definición |
|---|---|
| Escenario BDD | Triple Gherkin Given/When/Then redactado en lenguaje de negocio y persistido en el issue de GitHub. |
| Slug del escenario | Derivación kebab-case del título del escenario, usada como clave canónica del mapeo. |
| Marcador canónico | Anotación de prueba específica del stack que referencia explícitamente un slug de escenario. |
| Marcador fallback | Nombre de prueba o docstring que contiene `BDD: <title-or-slug>`, aceptado cuando el marcador canónico no está disponible. |
| Bloque `bdd:scenarios` | La sección delimitada por marcadores HTML en el cuerpo del issue que contiene los escenarios de negocio. |
| Gap | Escenario en el issue sin prueba que lo cubra. |
| Drift | Marcador de prueba que apunta a un escenario ausente del issue. |

## Referencias

- `lex-bdd-scenarios` — ley de redacción (fuentes, lenguaje, persistencia)
- `lex-bdd-coverage` — ley de cobertura (mapeo, drift, neutralidad de nivel)
- `kata-bdd-create-scenarios`, `kata-bdd-validate-scenarios` — procedimientos
- `cry-bdd-create-scenarios`, `cry-bdd-validate-scenarios` — puntos de entrada
- `lex-test-pyramid`, `lex-test-isolation`, `codex-test-strategy` — decisiones de nivel de prueba
- `framework/templates/contributing_templates/user-story-for-api.md`, `user-story-for-frontend.md` — origen de los escenarios API/UI que se duplican
