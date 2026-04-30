# Lexis: Cobertura BDD a través del Mapeo a Pruebas

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Relación de cobertura entre escenarios BDD en el issue de GitHub y la suite de pruebas

## Propósito

Cuando se redactan escenarios BDD para una feature, estos se vuelven la declaración canónica de la intención de negocio. Esa declaración no vale nada si la suite de pruebas no se conecta a ella. Sin un mapeo exigible, los escenarios decaen a documentación obsoleta mientras las pruebas evolucionan en su propia dirección.

Esta Lexis define el mapeo (los escenarios son referenciados por su slug desde el propio código de prueba), prohíbe la deriva en cualquiera de las dos direcciones (escenarios sin cobertura, marcadores huérfanos), y se mantiene neutral respecto al nivel de prueba (cualquier nivel puede cubrir un escenario, gobernado por `lex-test-pyramid` y `codex-test-strategy`).

## Ley

> **Cada escenario BDD de negocio publicado en el issue de GitHub (en el bloque `bdd:scenarios`) DEBE estar cubierto por al menos una prueba de cualquier nivel (unit, integración, E2E). El mapeo DEBE ser detectable solo a partir de la prueba, mediante el marcador canónico `@bdd_scenario` (decorador en Python, etiqueta JSDoc/JS-TS, comentario en Go) que lleva el slug del escenario, o por fallback (`BDD: <title-or-slug>` en el nombre o docstring de la prueba). El framework NO impone un Gherkin runner — los escenarios siguen siendo documentación, las pruebas siguen siendo el artefacto ejecutable. Los escenarios sin una prueba que los cubra son gaps; los marcadores que apuntan a escenarios ausentes del issue son drift; ambos son violaciones.**

## Alcance

- **Aplica a:** features que tienen escenarios BDD redactados vía `/cry-bdd-create-scenarios` (o que estén presentes en el issue dentro de los marcadores `bdd:scenarios`).
- **Agentes vinculados:** `warrior-hera`, `kata-bdd-validate-scenarios`, revisores de código.
- **Excepciones:** las features sin escenarios BDD permanecen gobernadas por sus propias reglas de calidad (trazabilidad AC↔prueba del Issue-Driven, Gate 2). Esta Lexis está en reposo para ellas.

## Reglas

### 1. Un escenario, al menos una prueba que lo cubra

Para cada `Scenario: <title>` en el cuerpo del issue, al menos una prueba lo referencia explícitamente.

### 2. El mapeo es detectable desde la prueba

Mecánicas de mapeo, en orden de preferencia:

| Stack | Marcador canónico | Fallback |
|---|---|---|
| Python (pytest) | decorador `@bdd_scenario("scenario-slug")` sobre la función de prueba | docstring contiene `BDD: <scenario-title>` |
| JS/TS (Jest, Vitest) | etiqueta JSDoc `// @bdd_scenario scenario-slug` inmediatamente arriba de la prueba, o un wrapper `bddScenario("scenario-slug", () => { ... })` | el nombre de la prueba contiene `BDD: <scenario-title>` |
| Go | comentario `// bdd_scenario: scenario-slug` inmediatamente arriba de `func TestXxx` | el nombre de la función contiene el slug en CamelCase |
| Otros | nombre de prueba o docstring que coincida con `BDD:\s*<title-or-slug>` | — |

`<scenario-slug>` es la derivación en kebab-case de `Scenario: <title>` (minúsculas, no alfanuméricos reemplazados por `-`, `-` repetidos colapsados, `-` final removido). Ejemplo: `Customer requests a refund` → `customer-requests-a-refund`.

El identificador `bdd_scenario` es el token canónico entre stacks. El framework no entrega el decorador de Python ni el wrapper de JS/TS; los proyectos que adopten BDD definen un helper local delgado (`bdd_scenario` / `bddScenario`) para que el marcador sea estable a grep. La kata de validación reconoce el token canónico independientemente de la implementación subyacente, mientras lleve el slug del escenario.

### 3. El nivel de prueba es abierto

La prueba que cubre puede vivir en cualquier nivel (unit, integración, E2E). Los escenarios son agnósticos al nivel. Las decisiones de nivel siguen `lex-test-pyramid` y `codex-test-strategy`.

### 4. No se requiere Gherkin runner

El framework no impone ni recomienda un Gherkin runner (Behave, Cucumber, SpecFlow). Los escenarios son documentación; las pruebas son el artefacto ejecutable. Los proyectos que elijan adoptar un runner pueden hacerlo, pero las pruebas generadas por el runner igualmente deben exponer el mapeo según la Regla 2.

### 5. Integridad bidireccional

Un marcador de prueba que apunta a un escenario ausente del issue es drift. La causa es alguna de: el escenario fue renombrado (renombrar el marcador), el escenario fue eliminado (eliminar la prueba o actualizar su alcance), el escenario nunca existió (corregir la prueba). El drift es una violación, no un warning.

### 6. Renombrar es un breaking change para el mapeo

Cuando se renombra un escenario en el issue, el slug cambia; los marcadores DEBEN ser actualizados en el mismo cambio. Renombrar sin actualizar el marcador produce drift en la siguiente ejecución de validación.

## Ejemplos

### Correcto

```python
# Issue body has: Scenario: Customer requests a refund for an eligible payment
@bdd_scenario("customer-requests-a-refund-for-an-eligible-payment")
def test_creates_pending_refund_and_audit_entry():
    """BDD: Customer requests a refund for an eligible payment."""
    ...
```

```typescript
// Issue body has: Scenario: Concurrent refunds deduplicate by idempotency key
// @bdd_scenario concurrent-refunds-deduplicate-by-idempotency-key
test("only one refund persists when two requests share an idempotency key", () => { ... });
```

### Incorrecto

```python
# Scenario exists in the issue but no test references it (Rule 1 violation)
def test_creates_refund(): ...
```

```python
# Marker references a scenario absent from the issue (Rule 5 violation)
@bdd_scenario("legacy-scenario-removed-2-sprints-ago")
def test_legacy(): ...
```

## Validación Automatizada

- **Herramienta:** `kata-bdd-validate-scenarios` parsea el bloque `bdd:scenarios` del issue, escanea la suite de pruebas en busca de marcadores canónicos y fallbacks por stack, y emite un reporte bidireccional de cobertura (cubierto, gaps, drift).
- **Momento:** bajo demanda (`/cry-bdd-validate-scenarios <issue>`); recomendado en la revisión del PR para cualquier feature con escenarios BDD.
- **Métrica:** 100% de los escenarios tienen ≥1 prueba que los cubre; 0 marcadores que apunten a escenarios ausentes del issue.
