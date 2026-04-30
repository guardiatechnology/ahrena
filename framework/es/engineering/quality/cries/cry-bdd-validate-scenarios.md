# Cry: Validar Cobertura de Escenarios BDD en la Suite de Pruebas

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Independiente — confirma que cada escenario BDD de negocio en un issue de GitHub tenga al menos una prueba que lo cubra (mediante marcador canónico o fallback)

## Descripción

Atajo independiente para invocar `kata-bdd-validate-scenarios`. Lee el bloque `bdd:scenarios` de un issue de GitHub, escanea la suite de pruebas en busca de marcadores canónicos `@bdd_scenario` (y equivalentes por stack) más patrones fallback, y emite un reporte bidireccional de cobertura. No ejecuta pruebas, no modifica el issue ni ningún archivo fuente. Independiente del flujo Issue-Driven.

## Uso

```
/cry-bdd-validate-scenarios <issue-number> [<owner>/<repo>]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `issue-number` | Sí | Issue que contiene el bloque `bdd:scenarios` | `42` |
| `<owner>/<repo>` | No | Por defecto: repo actual vía git remote | `guardiafinance/ahrena` |

## Prerrequisitos

- `github` listado en `mcp.servers` en `.ahrena/.directives`
- Variables de entorno: `GITHUB_PAT` (obligatoria)
- Issue existente con un bloque `bdd:scenarios` (de lo contrario, la kata reporta "nothing to validate" y se detiene)

## Qué Hace el Comando

1. Invoca `kata-bdd-validate-scenarios`.
2. La kata lee el cuerpo del issue y extrae los escenarios con sus slugs.
3. La kata escanea el working tree en busca de marcadores canónicos `bdd_scenario` por stack (decorador `@bdd_scenario("slug")` en Python, etiqueta JSDoc `// @bdd_scenario slug` o wrapper `bddScenario("slug", ...)` en JS/TS, comentario `// bdd_scenario: slug` en Go) y patrones fallback (`BDD: <title-or-slug>` en el nombre o docstring de la prueba).
4. La kata emite un reporte de cobertura listando escenarios cubiertos, gaps y drift, con evidencia concreta de archivo/línea y una recomendación por hallazgo.

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Run kata-bdd-validate-scenarios for issue #{{issue-number}}. Read the bdd:scenarios block from the issue body. Scan the test suite for canonical `bdd_scenario` markers per stack (`@bdd_scenario("slug")` in Python, `// @bdd_scenario slug` or `bddScenario(...)` in JS/TS, `// bdd_scenario: slug` in Go) and fallback patterns (`BDD: <title-or-slug>` in test name or docstring). Build the bidirectional map. Report `complete`, `gaps`, `drift`, or `gaps+drift` with concrete file/line evidence and a recommendation per finding.

Do not run tests. Do not modify any file. Do not infer scenarios from test code.

Strictly respect lex-bdd-coverage and lex-mcp.
```

## Ejemplo de Invocación

**Input:**

```
/cry-bdd-validate-scenarios 42
```

**Salida esperada:**

```
BDD Coverage — Issue #42 — Result: gaps

Scenarios in issue: 3
Covered: 2 | Uncovered: 1 | Orphan markers: 0

| Scenario | Slug | Tests | Status |
|---|---|---|:-:|
| Customer requests a refund for an eligible payment | customer-requests-a-refund-for-an-eligible-payment | tests/refunds/test_create.py::test_pending_refund | ✅ |
| Customer cannot refund after 30 days | customer-cannot-refund-after-30-days | tests/refunds/test_eligibility.py::test_30d_window | ✅ |
| Concurrent refunds deduplicate by idempotency key | concurrent-refunds-deduplicate-by-idempotency-key | — | ❌ |

Recommendation:
- `concurrent-refunds-deduplicate-by-idempotency-key` is uncovered. Add a test (any level) marked `@bdd_scenario("concurrent-refunds-deduplicate-by-idempotency-key")` or with `BDD: Concurrent refunds deduplicate by idempotency key` in its docstring.
```

## Restricciones

- **Solo lectura.** No modifica el issue, las pruebas ni ningún otro archivo.
- **No ejecuta pruebas.** Es una verificación estructural de mapeo, no comportamental.
- **Independiente.** No bloquea ni modifica ningún otro flujo (Issue-Driven, Gate 2). Ejecutarlo cuando sea útil.
- **Sin pasadas silenciosas.** Cuando el issue no tiene bloque `bdd:scenarios`, el comando lo dice explícitamente.

## Cry vs Kata

| Aspecto | Cry | Kata |
|---|---|---|
| Naturaleza | Invocación rápida por número de issue | Procedimiento completo (parsear, escanear, clasificar, reportar) |
| Complejidad | Baja | Alta (8 pasos incluyendo escaneo multi-stack) |

## Cries y Katas Asociados

- `kata-bdd-validate-scenarios` — invocada por esta cry
- `cry-bdd-create-scenarios` — cry predecesora (redacta los escenarios)
- `kata-quality-gate` — ortogonal; puede ejecutarse junto a esta cry para un panorama de cobertura más completo, pero no está acoplada

## Referencias

- `lex-bdd-coverage` — ley de cobertura
- `codex-bdd` — metodología y convenciones de marcador
- `kata-bdd-validate-scenarios` — procedimiento
- `lex-test-pyramid`, `codex-test-strategy` — decisiones de nivel de prueba para las pruebas que cubren
