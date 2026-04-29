# Lexis: Pruebas BDD sin Acoplamiento a Framework BDD

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ingeniería — Calidad. Implementación de pruebas que validan escenarios Gherkin.

## Propósito

Los step-runners (behave, pytest-bdd, cucumber y similares) crean una infraestructura paralela de pruebas (step definitions, regex matchers, hooks) que diverge de la suite real, duplica el costo de mantenimiento y entrena al equipo a perseguir glue en vez de comportamiento. El beneficio prometido — "el negocio lee las pruebas" — rara vez paga el costo: en la práctica, nadie del negocio lee el `.feature` ejecutándose, y el equipo termina arreglando regex en archivos `steps/`.

Esta Lexis existe para que **los escenarios Gherkin se mantengan como documentación black-box** (per `lex-bdd-spec-only-sources` y `lex-bdd-gherkin-format`) y **la suite de pruebas siga siendo la suite de pruebas** — una sola, estándar, con trazabilidad explícita al escenario mediante una convención de nombre.

## Ley

> **Las pruebas que validan un escenario Gherkin DEBEN ser pruebas regulares (unit/integración/E2E) escritas en el framework de pruebas que el proyecto ya usa (pytest, vitest, jest, junit, go test, etc.). El uso de cualquier step-runner BDD (behave, pytest-bdd, cucumber, jest-cucumber, lettuce, godog, specflow, gauge) está PROHIBIDO. Cada escenario mapea a una o más pruebas estándar mediante referencia `SCN-{N}` en el nombre o docstring de la prueba; el archivo de escenarios es documentación, no código pegamento ejecutable.**

## Reglas

### 1. Dónde vive el escenario

Los escenarios viven en **uno** de los formatos siguientes, ambos como documentación no ejecutada por un runner:

- `docs/issues/issue-{n}/07-bdd-scenarios.md` (consolidado, formato preferido).
- `docs/issues/issue-{n}/scenarios/*.feature` (un archivo por `Feature`, cuando el volumen lo justifique).

Ningún runner consume estos archivos. Son solo Markdown/feature leídos por humanos y por `kata-bdd-validate-implementation`.

### 2. Dónde vive la prueba

Las pruebas que validan escenarios viven **en la suite normal** del proyecto:

- `tests/unit/`, `tests/integration/`, `tests/e2e/` (o equivalente del stack), siguiendo `lex-test-pyramid`.
- **NO** viven en `features/`, `steps/`, `step_definitions/` ni en un directorio paralelo dedicado a BDD.

### 3. Trazabilidad obligatoria

Cada prueba que valida un escenario **DEBE** referenciar el id `SCN-{N}` en al menos uno de estos lugares:

- Nombre de la función/`it`/`describe`:
  - Python: `def test_scn_1_cliente_programa_transferencia_valida():`
  - JS/TS: `it("SCN-1 cliente programa transferencia válida", () => { ... })`
  - Go: `func TestSCN1ClienteProgramaTransferenciaValida(t *testing.T) { ... }`
- O docstring/JSDoc de la prueba, cuando el nombre quedaría pesado:

```python
def test_programacion_sin_saldo():
    """Valida SCN-2 (AC-2): el cliente intenta programar sin saldo."""
```

Una prueba **PUEDE** validar más de un escenario (ej.: `"Valida SCN-3 y SCN-4"`); un escenario **PUEDE** ser validado por más de una prueba (ej.: SCN-1 unitaria + SCN-1 integración).

### 4. Dependencias prohibidas

Los manifiestos del proyecto (`pyproject.toml`, `requirements*.txt`, `package.json`, `go.mod`, `pom.xml`, `*.csproj`, etc.) **NO PUEDEN** declarar:

- `behave`, `pytest-bdd`, `lettuce`, `radish-bdd`
- `cucumber`, `cucumber-js`, `@cucumber/cucumber`, `jest-cucumber`
- `specflow`, `reqnroll`
- `godog`
- `gauge`
- Cualquier otro step-runner BDD

### 5. Artefactos prohibidos

**NO PUEDEN** existir en el repositorio:

- `features/*.feature` leídos por un runner (los escenarios como documentación viven en `docs/issues/...`).
- Directorios `steps/`, `step_definitions/`, `support/world.js`, etc. con glue para escenarios.
- Decoradores/anotaciones `@given`, `@when`, `@then`, `@step` ligados a escenarios.
- Archivos de configuración `behave.ini`, `cucumber.json`, `cypress-cucumber-preprocessor`, etc.

### 6. Proyectos legacy

Los proyectos preexistentes con framework BDD ya entrincherado **DEBEN**:

1. Registrar ADR con plan de remoción (per `kata-adr-write`).
2. Congelar la creación de nuevos escenarios ejecutados por el runner.
3. Migrar incrementalmente a pruebas estándar con referencia `SCN-{N}`.

Para el código nuevo (PRs después de que esta Lexis entre en vigor), el Gate 3 bloquea importaciones de los runners prohibidos.

### 7. Dónde vive el estilo de la prueba

La elección del nivel (unit/integración/E2E) y del estilo (mock, fixture, contenedor) sigue `lex-test-pyramid`, `lex-test-isolation`, `lex-python-testing`, `lex-frontend-testing` y la Codex aplicable. Esta Lexis no impone nivel — solo exige que, sea cual sea la prueba elegida, sea **una prueba regular del framework del proyecto** con referencia `SCN-{N}`.

## Alcance

- **Aplica a:** toda prueba agregada o modificada durante la Fase 8 del flujo Issue-Driven, y a toda prueba nueva creada en proyectos bajo esta Lexis.
- **Agentes vinculados:** `warrior-themis` (mapea escenario↔prueba), `warrior-apollo`/`warrior-hephaestus`/`warrior-iris` (cuando implementan pruebas para llenar gaps detectados).
- **Excepciones:** Ninguna. Los proyectos legacy registran ADR de remoción; el código nuevo no importa un runner BDD.

## Consecuencias de Violación

1. **Gate 3 falla:** `kata-quality-gate` Check 8 detecta una dependencia de step-runner o un directorio `features/` ejecutado, y bloquea el PR.
2. **Prueba no trazable:** una prueba sin referencia `SCN-{N}` correspondiente no cuenta como cobertura BDD; el escenario queda como gap en `08-bdd-validation-report.md`.
3. **Deuda de mantenimiento visible:** el ADR de remoción mantiene la deuda explícita hasta que la migración concluya.

## Ejemplos

### Correcto

```python
# tests/integration/test_transfer_scheduling.py
import pytest

@pytest.mark.asyncio
async def test_scn_1_cliente_programa_transferencia_valida(client, db_session):
    """Valida SCN-1 (AC-1): cliente con saldo programa transferencia válida."""
    customer = await create_active_customer(db_session, balance=1000_00)
    response = await client.post("/v1/transfers", json={
        "amount": 100_00, "scheduled_for": "2026-04-30"
    })
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "scheduled"
```

```
docs/issues/issue-42/07-bdd-scenarios.md   # escenario SCN-1 documentado
tests/integration/test_transfer_scheduling.py   # prueba estándar con referencia
pyproject.toml   # sin behave / pytest-bdd
```

### Incorrecto

```
# pyproject.toml
[project.optional-dependencies]
test = ["pytest-bdd>=7.0"]   # ❌ runner BDD prohibido

# features/transfer.feature   # ❌ feature consumida por runner

# tests/steps/transfer_steps.py
from pytest_bdd import given, when, then, scenario

@scenario("../../features/transfer.feature", "Cliente programa transferencia válida")
def test_programa(): pass

@given("el saldo disponible es $ 1.000,00")
def saldo_mil(db): ...   # ❌ glue paralelo

@when("el cliente programa una transferencia de $ 100,00 para mañana")
def programa(client): ...   # ❌ regex matchers
```

## Validación Automatizada

- **Herramienta:** lint de dependencias que recorre `pyproject.toml`/`requirements*.txt`/`package.json`/`go.mod`/etc. contra la lista prohibida; lint de pruebas que asegura referencia `SCN-{N}`; `kata-bdd-validate-implementation` produce `08-bdd-validation-report.md` con el mapeo; `kata-quality-gate` Check 8 falla el gate ante una violación.
- **Momento:** Fase 8 del flujo Issue-Driven (pre-PR), CI en todo PR que agregue/modifique pruebas o manifiestos.
- **Métrica:** 0 dependencias de step-runner BDD; 100% de los escenarios con al menos una prueba que referencia `SCN-{N}`.

## Referencias

- `lex-bdd-spec-only-sources` — fuentes permitidas para derivar escenarios
- `lex-bdd-gherkin-format` — formato declarativo de los escenarios
- `lex-test-pyramid` — distribución de niveles de prueba
- `lex-test-isolation` — independencia entre pruebas
- `kata-bdd-validate-implementation` — procedimiento de validación escenario↔prueba
- `warrior-themis` — agente que orquesta la validación
