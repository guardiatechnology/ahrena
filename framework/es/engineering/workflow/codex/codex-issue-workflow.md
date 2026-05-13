# Codex: Flujo Issue-Driven Development

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Estructura, fases, gates y artefactos del flujo de desarrollo orientado por issues orquestado por `warrior-athena`

## Visión General

Este Codex es la referencia operacional del flujo **Issue-Driven Development** de Ahrena. Define las 7 fases del proceso, los 2 gates de calidad, el formato de los artefactos intermedios, la convención de trazabilidad entre criterios de aceptación y tests, el formato de los ADRs (Architecture Decision Records) y la estructura de **Phase artifacts en `.ahrena/issues/{n}/`**. Consultado por `warrior-athena` y por todos los katas del clade `engineering/workflow/`.

> **Ventana de transición:** durante 1 release tras el merge de , **ambos** caminos son aceptados como válidos — `.ahrena/issues/{n}/` (nuevo, canónico) y `.ahrena/issues/issue-{n}/` (legado). Tras el release siguiente, Gate 2 (`kata-quality-gate`) falla encontrando archivos en `.ahrena/issues/issue-{n}/` — fuerza migración vía `git mv .ahrena/issues/issue-{n} .ahrena/issues/{n}` en cada repo consumidor. Los ADRs permanecen en `docs/adr/` (son documentación de producto).

## Contexto

- **Dominio:** flujo de entrega de features y bugfixes partiendo de issues de GitHub, con orquestación vía `warrior-athena`.
- **Audiencia:** `warrior-athena`, katas del clade `engineering/workflow/`, y warriors especialistas delegados (Apollo, Daedalus, Kronos).
- **Actualización:** cuando se agreguen/eliminen fases, cuando los criterios del Gate 2 cambien, o cuando la estructura de `docs/` evolucione.

## Contenido

### Las 7 fases del flujo

| # | Fase | Kata principal | Salida |
|:-:|---|---|---|
| 1 | Análisis de la issue | `kata-issue-analysis` | `.ahrena/issues/{n}/01-brief.md` |
| 2 | Elicitación de requisitos | `kata-requirements-brief` | `.ahrena/issues/{n}/02-requirements.md` |
| 3 | Design arquitectural | `kata-architecture-brief` (+ `kata-adr-write` si es aplicable) | `.ahrena/issues/{n}/03-architecture.md` + `docs/adr/ADR-*` |
| 4 | Implementación | delega a `warrior-apollo` → `kata-python-implement` (Python) | código + tests con marcación `AC-N` |
| 5 | Revisión de seguridad | `kata-security-review` | `.ahrena/issues/{n}/05-security-review.md` |
| 6 | Gate de calidad | `kata-quality-gate` | `.ahrena/issues/{n}/06-quality-report.md` |
| 7 | Preparación del PR | `kata-pr-prepare` | URL del PR en GitHub |

### Los 2 gates

**Gate 1 — Aprobación de Alcance** (entre la Fase 3 y la Fase 4)

- Ejecutado por: `warrior-athena`
- Presenta al humano: brief + ACs + arquitectura + ADRs propuestos
- Criterio de aprobación: aprobación explícita humana
- Si falla: flujo cerrado o retorna a la Fase 1/2/3 con feedback

**Gate 2 — Calidad de Implementación** (entre la Fase 6 y la Fase 7)

- Ejecutado por: `kata-quality-gate`
- 7 verificaciones; el resultado es `go` (todas ✅ o `unverifiable` donde no aplique), `no-go` (cualquier ❌), o `go-with-caveats` (>2 `unverifiable`, el humano decide):

| # | Verificación | Cómo |
|:-:|---|---|
| 1 | Trazabilidad AC ↔ test (bidireccional) | Markers canónicos por stack (pytest marker, JS `@ac` tag); regex solo como fallback |
| 2 | Scope creep check | `git diff` vs. componentes declarados en la Fase 3 |
| 3 | Best practices (Lexis aplicables por stack) | Python/Frontend/IaC Lexis; convenciones cross-stack |
| 4 | Tests ejecutados | `pytest` / `yarn test` / comando específico del stack |
| 5 | Cobertura | `pytest --cov` ≥ `quality.coverage_threshold` en `.directives` |
| 6 | Tipos | `mypy --strict` / `tsc --noEmit` sin errores nuevos |
| 7 | Performance budget | Lighthouse/bundle (Frontend); benchmark p99 (Backend); Infracost (IaC) |

- Si falla: retorna a la Fase 4 (Apollo) con reporte detallado; el humano puede optar por ampliar ACs (nueva iteración del Gate 1) si el problema es scope creep justificable.

### Best practices verificadas en el Gate 2

| Lexis | Verificación |
|---|---|
| `lex-python-typing` | `mypy --strict` sin errores |
| `lex-python-testing` | Todas las funciones públicas tienen test |
| `lex-python-security` | Sin credenciales hardcoded; inputs validados |
| `lex-python-immutability` | Sin mutación en estructuras compartidas |
| `lex-python-error-handling` | Sin `except: pass` o swallowing silencioso |
| `lex-conventional-commits` | Commits en el formato `type(scope): message` |

### Estructura de documentación en `docs/`

```
docs/
├── adr/
│   ├── ADR-001-use-event-sourcing-for-ledger.md
│   ├── ADR-002-migrate-to-fastapi.md
│   └── ...
└── issues/
    └── issue-{n}/
        ├── 01-brief.md
        ├── 02-requirements.md
        ├── 03-architecture.md
        ├── 05-security-review.md
        └── 06-quality-report.md
```

### Estado efímero en `.ahrena/workflow/`

```
.ahrena/workflow/issue-{n}/
└── checkpoint.md       # Contexto de handoff entre fases
```

### Convención de trazabilidad AC ↔ test

Cada AC de la Fase 2 es numerado (`AC-1`, `AC-2`, ...). Cada test nuevo en la Fase 4 **debe** referenciar el/los AC(s) que cubre, en una de las formas:

**Forma 1 — nombre del test:**
```python
def test_create_refund_returns_201_AC_1():
    ...
```

**Forma 2 — docstring:**
```python
def test_refund_idempotency():
    """AC-2: las llamadas repetidas con mismo Idempotency-Key retornan el mismo resultado."""
    ...
```

**Forma 3 — marker pytest:**
```python
@pytest.mark.ac("AC-3")
def test_refund_audit_log():
    ...
```

El `kata-quality-gate` usa regex para extraer las referencias y cruza con la lista de ACs. No hay coerción automática — es responsabilidad del implementador (Apollo u otro warrior) marcar correctamente.

### Formato de ADR (MADR simplificado)

```markdown
# ADR-{n}: {Título corto}

- **Status:** proposed | accepted | deprecated | superseded by ADR-XXX
- **Date:** {YYYY-MM-DD}
- **Issue:** #{issue-number}

## Context

{problema o fuerza que motivó la decisión}

## Decision

{la decisión tomada, en voz activa}

## Consequences

### Positive
- ...

### Negative
- ...

### Neutral
- ...

## Alternatives Considered

- **{Alternativa A}:** rechazada porque ...
- **{Alternativa B}:** rechazada porque ...
```

**Numeración:** `ADR-{n}` es secuencial global en `docs/adr/`. El `kata-adr-write` detecta el próximo número listando los archivos existentes.

### Cuándo generar ADR (checklist)

| Situación | ¿Generar ADR? |
|---|:-:|
| Nueva elección tecnológica (framework, library) | ✅ Sí |
| Desviación de patrón existente en el codebase | ✅ Sí |
| Trade-off significativo entre alternativas | ✅ Sí |
| Decisión que afecta múltiples componentes | ✅ Sí |
| Decisión que afecta contrato externo (API, evento) | ✅ Sí |
| Fix puntual de bug sin cambio de patrón | ❌ No |
| Refactor localizado siguiendo patrón existente | ❌ No |
| Adición de endpoint siguiendo patrón del codebase | ❌ No |

### Delegación a warriors especialistas

`warrior-athena` **no implementa** las fases 4 (código) ni 3 (cuando involucra API/eventos). En su lugar, delega:

| Situación | Delega a | Vía |
|---|---|---|
| Feature involucra API REST | `warrior-daedalus` | `kata-api-design-oas` |
| Feature involucra eventos (CloudEvents) | `warrior-kronos` | `kata-events-doc` |
| Feature involucra infraestructura AWS | `warrior-atlas` | `kata-aws-design` |
| Implementación en Python | `warrior-apollo` | `kata-python-implement` |
| Implementación en Frontend | `warrior-hephaestus` | `kata-frontend-implement` |

El handoff ocurre vía `.ahrena/workflow/issue-{n}/checkpoint.md` — Athena graba el contexto necesario, invoca al warrior especialista, y retoma la orquestación tras la conclusión.

### Mapeo de entrada del cry

El `/cry-implement-issue` acepta como argumentos:

```
/cry-implement-issue <issue-number> [<owner>/<repo>]
```

- `<issue-number>` (obligatorio): número de la issue en GitHub.
- `<owner>/<repo>` (opcional): repositorio de destino; default es el repo del proyecto actual (detectado vía git remote).

## Referencias

- `lex-issue-driven` — leyes inquebrantables del flujo Issue-Driven
- `warrior-athena` — orquestador del flujo
- `cry-implement-issue` — punto de entrada
- `kata-issue-analysis`, `kata-requirements-brief`, `kata-architecture-brief`, `kata-adr-write`, `kata-security-review`, `kata-quality-gate`, `kata-pr-prepare` — katas del flujo
- `kata-mcp-github-read`, `kata-mcp-notion-read` — lectura de contexto externo
- `lex-mcp`, `codex-mcp-github`, `codex-mcp-notion` — uso de los MCPs
- `warrior-apollo`, `warrior-daedalus`, `warrior-kronos`, `warrior-hephaestus`, `warrior-atlas` — especialistas delegados
- [MADR — Markdown Architectural Decision Records](https://adr.github.io/madr/)
