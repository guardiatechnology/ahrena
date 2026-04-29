# Kata: Validación BDD de la Implementación

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Calidad. Segunda mitad de la Fase 8 del flujo Issue-Driven. Mapea cada escenario Gherkin de `07-bdd-scenarios.md` a las pruebas existentes en el repositorio y reporta gaps.

## Objetivo

Producir `docs/issues/issue-{n}/08-bdd-validation-report.md` con el mapeo `SCN-{N}` ↔ pruebas existentes, detectar lagunas de cobertura, verificar la ausencia de step-runner BDD en los manifiestos y emitir decisión `go | no-go` para el Gate 3 (`kata-quality-gate` Check 8). **Este Kata puede leer código** — esa es exactamente su función; la restricción "ciego al código" aplica solo al diseño de escenarios (Fase 8.1).

## Cuándo Usar

- Fase 8.2 del flujo orquestado por `warrior-athena`/`warrior-themis`, **después** de que `kata-bdd-scenarios-design` concluya.
- Bajo demanda para auditoría de cobertura BDD en funcionalidades ya implementadas.

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `issue_number` | Sí | Número de la issue (ej.: `42`) |
| `repo` | Sí | `owner/repo` |
| `07-bdd-scenarios.md` | Sí | Artefacto de la Fase 8.1; falla si está ausente o malformado |
| Manifiestos del proyecto | Sí (en el repositorio) | `pyproject.toml`, `package.json`, `go.mod`, etc. |
| Suite de pruebas | Sí (en el repositorio) | `tests/`, `__tests__/`, `spec/`, equivalente del stack |

## Workflow

```
Progreso:
- [ ] 1. Verificar precondiciones (Fase 8.1 concluida y sin ACs bloqueadas)
- [ ] 2. Parsear 07-bdd-scenarios.md
- [ ] 3. Indexar pruebas del repositorio (solo lectura)
- [ ] 4. Clasificar cada escenario (covered | partial | missing)
- [ ] 5. Verificar acoplamiento a framework BDD
- [ ] 6. Componer 08-bdd-validation-report.md
- [ ] 7. Emitir decisión go | no-go
- [ ] 8. Actualizar checkpoint
- [ ] 9. Validación final
```

### Paso 1: Verificar precondiciones

1. Confirmar `docs/issues/issue-{n}/07-bdd-scenarios.md` presente.
2. Confirmar frontmatter bien formado: `sources`, `ac_coverage`, `generated_by: warrior-themis`.
3. Verificar que ninguna AC esté con `status: BLOCKED` en el `ac_coverage`. Si hay bloqueo, detenerse y devolver a la Fase 8.1 (la Issue debe complementarse antes de que el Gate 3 pueda pasar).
4. Verificar que `sources` declara solo rutas permitidas (sin `src/`, `tests/`, etc.). Si viola, fallar y exigir regeneración de la Fase 8.1.

### Paso 2: Parsear 07-bdd-scenarios.md

1. Extraer la lista de escenarios: para cada uno, registrar `id (SCN-{N})`, etiquetas AC (`@AC-{N}`), etiqueta de tipo (`@happy-path` etc.), título.
2. Construir mapa `SCN → AC[]` y mapa inverso `AC → SCN[]`.
3. Validar unicidad del `SCN-{N}` en el archivo. Conflicto = falla de precondición (regenerar la Fase 8.1).

### Paso 3: Indexar pruebas del repositorio

Esta etapa **puede** abrir archivos bajo `tests/`, `__tests__/`, `spec/`, etc. Sin ejecutar pruebas — solo descubrimiento estático.

1. Determinar directorios de prueba convencionales del stack:
   - Python: `tests/`, `tests/unit/`, `tests/integration/`, `tests/e2e/`
   - JS/TS: `__tests__/`, `tests/`, `e2e/`, `cypress/`, `playwright/`
   - Go: archivos `*_test.go`
   - Java: `src/test/java/`
2. Para cada archivo de prueba, recorrer:
   - Nombres de funciones/`it`/`describe` buscando `SCN-{N}` (regex `SCN[-_ ]?\d+`).
   - Docstrings/JSDoc/comentarios inmediatamente arriba de la función buscando la misma referencia.
3. Construir mapa `SCN → [test_path:line, ...]`.
4. Para cada ruta de prueba descubierta, registrar el nivel inferido por el directorio (unit | integration | e2e).

### Paso 4: Clasificar cada escenario

Para cada `SCN-{N}` de la Fase 8.1:

| Clasificación | Criterio |
|---|---|
| **covered** | ≥ 1 prueba referencia `SCN-{N}` **y** el nivel es compatible con la etiqueta de tipo |
| **partial** | La prueba referencia `SCN-{N}` **pero** el nivel es insuficiente para el tipo del escenario (ver tabla abajo), o solo parte del `Then` se asserta |
| **missing** | Ninguna prueba referencia `SCN-{N}` |

**Compatibilidad nivel ↔ tipo:**

| Etiqueta de tipo | Nivel compatible |
|---|---|
| `@happy-path` | unit OR integration OR e2e (cualquiera, conforme `lex-test-pyramid`) |
| `@alternative` | unit OR integration |
| `@edge` | unit OR integration |
| `@error` | unit OR integration |
| `@nfr` (latencia, idempotencia, disponibilidad) | integration OR e2e (unit puro no observa NFR real) |

Si un escenario `@nfr` cubre solo prueba unit → `partial` con recomendación de subir nivel.

### Paso 5: Verificar acoplamiento a framework BDD

1. Recorrer manifiestos contra la lista prohibida de `lex-bdd-no-framework-coupling` Regla 4:
   - Python: `pyproject.toml`, `requirements*.txt`, `Pipfile`, `setup.py` → buscar `behave`, `pytest-bdd`, `lettuce`, `radish-bdd`.
   - JS/TS: `package.json` (deps + devDeps) → buscar `cucumber`, `cucumber-js`, `@cucumber/cucumber`, `jest-cucumber`, `cypress-cucumber-preprocessor`.
   - Go: `go.mod` → buscar `godog`.
   - Java: `pom.xml`, `build.gradle` → buscar `cucumber-jvm`.
   - .NET: `*.csproj` → buscar `specflow`, `reqnroll`.
2. Recorrer la estructura de directorios:
   - Existencia de `features/` o `tests/features/` consumida por runner.
   - Existencia de `step_definitions/`, `steps/`, `support/world.js` ligados a escenarios.
   - Decoradores/anotaciones `@given`/`@when`/`@then`/`@step` en archivos de prueba.
3. Registrar resultado: `clean` (sin violación) o `violations: [...]` (lista de las ocurrencias).

Adicionalmente, si una prueba valida un escenario sin referencia `SCN-{N}` (aunque la prueba sea correcta), registrar como **violación de trazabilidad** — no impide el go, pero va como nota en la sección de gaps.

### Paso 6: Componer 08-bdd-validation-report.md

Estructura:

```yaml
---
issue: {n}
repo: {owner/repo}
generated_at: "{ISO-8601}"
generated_by: warrior-themis
scenarios_total: 12
covered_count: 9
partial_count: 2
missing_count: 1
framework_coupling: clean   # o: violations
gate_3_decision: go | no-go
---
```

Contenido:

```markdown
# Reporte de Validación BDD — Issue #{n}

## Resumen

- Total de escenarios: 12
- Cubiertos: 9
- Parciales: 2
- Faltantes: 1
- Acoplamiento a framework BDD: limpio

## Mapeo Escenario ↔ Prueba

| SCN | AC | Tipo | Status | Pruebas |
|---|---|---|---|---|
| SCN-1 | AC-1 | @happy-path | covered | tests/integration/test_transfer_scheduling.py:23 |
| SCN-2 | AC-2 | @alternative | covered | tests/integration/test_transfer_scheduling.py:48 |
| SCN-3 | AC-3 | @error | covered | tests/integration/test_transfer_scheduling.py:71 |
| SCN-4 | AC-3 | @edge | partial | tests/unit/test_transfer_rules.py:15 (solo borde inferior) |
| SCN-5 | AC-4 | @nfr | partial | tests/unit/test_balance_query.py:8 (cubre solo lógica, no latencia observable) |
| SCN-6 | AC-5 | @nfr | missing | — |

## Gaps (ítems no-go)

### SCN-4 — partial (cobertura parcial)
- **AC:** AC-3
- **Lo que cubre hoy:** borde inferior (saldo igual al valor)
- **Lo que falta:** borde superior (saldo igual al valor + tarifa)
- **Nivel recomendado:** integration
- **Responsable sugerido:** warrior-apollo

### SCN-5 — partial (nivel insuficiente)
- **AC:** AC-4 (@nfr — latencia)
- **Lo que cubre hoy:** lógica unitaria de la consulta
- **Lo que falta:** assert observable de latencia
- **Nivel recomendado:** integration con medición
- **Responsable sugerido:** warrior-apollo

### SCN-6 — missing
- **AC:** AC-5 (@nfr — idempotencia)
- **Nivel recomendado:** integration
- **Responsable sugerido:** warrior-apollo

## Verificación de Acoplamiento a Framework

- pyproject.toml: ✓ sin step-runner
- package.json: ✓ sin step-runner
- features/: ✓ ausente
- step_definitions/: ✓ ausente

## Decisión para el Gate 3

**no-go**

Razón: 1 escenario faltante (SCN-6) + 2 parciales (SCN-4, SCN-5).

## Próximas Acciones

| Gap | Acción | Responsable | Nivel | Iteración |
|---|---|---|---|---|
| SCN-6 | Crear prueba integration validando idempotencia de la operación | warrior-apollo | integration | next |
| SCN-5 | Agregar prueba integration midiendo latencia observable | warrior-apollo | integration | next |
| SCN-4 | Extender prueba existente para cubrir borde superior | warrior-apollo | integration | next |
```

### Paso 7: Emitir decisión go | no-go

- **go**: `missing_count == 0`, `partial_count == 0`, `framework_coupling == clean`.
- **no-go**: cualquier otra combinación. Listar próximas acciones con responsable (warrior) y nivel (per `codex-test-strategy`).

### Paso 8: Actualizar checkpoint

Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md` con:

```yaml
phase_completed: 8.2
phase_next: 6.b   # si go: volver al Quality Gate (Check 8)
                  # si no-go: aguardar a warrior-apollo/hephaestus/iris para implementar gaps
artifacts:
  bdd_validation_report: docs/issues/issue-{n}/08-bdd-validation-report.md
gate_3:
  status: go | no-go
  last_run_at: "{ISO-8601}"
updated_at: "{ISO-8601}"
```

### Paso 9: Validación Final

Antes de devolver el control:

- [ ] Todos los `SCN-{N}` de la Fase 8.1 aparecen en el mapeo.
- [ ] Cada escenario `partial` o `missing` tiene acción recomendada con responsable y nivel.
- [ ] La verificación de acoplamiento a framework está completa (todos los manifiestos recorridos).
- [ ] La decisión `go | no-go` es coherente con el contenido del reporte.
- [ ] Checkpoint actualizado.

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Reporte de validación | Markdown YAML + tablas | `docs/issues/issue-{n}/08-bdd-validation-report.md` |
| Decisión Gate 3 | `go` o `no-go` | Respuesta al orquestador + checkpoint |
| Lista de próximas acciones | Tabla | Sección del reporte |
| Checkpoint actualizado | Markdown YAML | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restricciones

- **PUEDE leer código:** el descubrimiento estático de pruebas es parte del objetivo de este Kata. La restricción "ciego al código" aplica solo a `kata-bdd-scenarios-design` (Fase 8.1).
- **NO PUEDE ejecutar pruebas:** el descubrimiento es estático (parsing de nombres/docstrings); la validación de ejecución queda para el `kata-quality-gate` Check 1.
- **NO PUEDE modificar pruebas:** cuando hay gap, el Kata reporta. La implementación de las pruebas faltantes queda para `warrior-apollo`/`warrior-hephaestus`/`warrior-iris` en iteración subsiguiente.
- **NO PUEDE inferir cobertura sin referencia `SCN-{N}`:** si una prueba valida el comportamiento sin referenciar el escenario, es violación de `lex-bdd-no-framework-coupling` Regla 3 — se registra como nota, pero no cuenta como cobertura.
- **DEBE bloquear el gate** cuando un manifiesto declara step-runner BDD o se encuentra un directorio `features/` consumido por runner.

## Referencias

- `lex-bdd-no-framework-coupling` — prohibiciones de framework y reglas de trazabilidad
- `lex-bdd-gherkin-format` — formato de los escenarios parseados
- `codex-bdd` — principios y taxonomía
- `codex-gherkin` — sintaxis esperada
- `codex-test-strategy` — elección de niveles para gaps
- `lex-test-pyramid` — distribución de niveles
- `kata-bdd-scenarios-design` — etapa anterior (Fase 8.1)
- `kata-quality-gate` — Check 8 consume el `gate_3_decision` de este reporte
- `lex-issue-driven` — flujo Issue-Driven (Fase 8 y Gate 3)
- `warrior-themis` — agente que invoca este Kata
