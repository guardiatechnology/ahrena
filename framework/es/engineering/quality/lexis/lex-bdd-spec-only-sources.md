# Lexis: Escenarios BDD Derivados Exclusivamente de las Fuentes de Especificación

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ingeniería — Calidad. Validación de comportamiento de funcionalidades entregadas mediante el flujo Issue-Driven Development.

## Propósito

La validación BDD solo detecta "construimos la cosa equivocada" cuando los escenarios son independientes de la implementación. Un escenario derivado del código solo puede describir lo que se construyó — nunca lo que se pidió. Esta Lexis garantiza que los escenarios funcionen como contrato de comportamiento black-box: si la especificación no permite escribirlos, el requisito está incompleto y debe volver al origen antes de que la validación continúe.

Esta Lexis existe para que **la validación BDD sea capaz de detectar divergencia entre lo que se pidió y lo que se entregó**, e impedir que el agente "complete" especificaciones ambiguas mirando el código producido.

## Ley

> **Los escenarios Gherkin producidos para validación de comportamiento DEBEN derivarse exclusivamente de la Issue de GitHub (título, cuerpo, criterios de aceptación, comentarios) y de las páginas de Notion vinculadas. Leer, abrir, ejecutar grep o consultar de cualquier forma el código de implementación (archivos bajo `src/`, `app/`, `lib/`, `tests/`, etc.) para descubrir, refinar o completar escenarios está PROHIBIDO. Si las fuentes de especificación no permiten escribir los escenarios, el agente DEBE detenerse y solicitar que la Issue sea complementada — nunca recurrir al código como atajo.**

## Reglas

### 1. Fuentes permitidas

El agente que produce los escenarios **PUEDE** consultar:

- La Issue de GitHub vinculada (título, cuerpo, comentarios, etiquetas).
- Páginas de Notion referenciadas por la Issue o por los artefactos del flujo Issue-Driven.
- Los artefactos del propio flujo: `docs/issues/issue-{n}/01-brief.md`, `02-requirements.md`, `03-architecture.md`.
- ADRs en `docs/adr/` cuando estén explícitamente referenciados por la arquitectura.

### 2. Fuentes prohibidas

El agente que produce los escenarios **NO PUEDE**:

- Abrir archivos bajo `src/`, `app/`, `lib/`, `pkg/`, `internal/`, `tests/`, `spec/`, `__tests__/`, `cypress/`, `e2e/`, o directorios equivalentes del stack.
- Ejecutar `grep`/`rg`/`find` sobre el código de implementación.
- Solicitar la explicación del código a otro agente para inferir comportamiento.
- Inspeccionar PRs, diffs o commits de la funcionalidad en validación.

### 3. Declaración de fuentes en el artefacto

El archivo `docs/issues/issue-{n}/07-bdd-scenarios.md` **DEBE** declarar, en frontmatter YAML, el conjunto de fuentes consultadas:

```yaml
---
issue: 42
repo: guardiafinance/ahrena
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/page-id-1"
    - "https://www.notion.so/page-id-2"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
generated_at: "2026-04-29T10:00:00Z"
---
```

Rutas bajo `src/`, `app/`, `tests/`, etc. en este bloque invalidan el artefacto.

### 4. Especificación insuficiente

Si las fuentes permitidas **no** permiten escribir escenarios completos para algún criterio de aceptación:

1. El agente **DEBE** detener la producción del artefacto.
2. **DEBE** abrir comentario en la Issue o bloque de bloqueo en `07-bdd-scenarios.md` listando las ambigüedades.
3. **NO PUEDE** consultar el código para resolver la ambigüedad.
4. La Issue **DEBE** ser complementada (por el PM, ingeniería, diseño) y el flujo retomado.

### 5. Verificación independiente

La validación de los escenarios contra la implementación (ejecutada por `kata-bdd-validate-implementation`) **PUEDE** leer el código — esta es la etapa de mapear escenario ↔ prueba existente. La producción de los escenarios (`kata-bdd-scenarios-design`) **NO PUEDE**.

La separación entre "diseñar escenarios" (ciego al código) y "validar implementación" (con acceso al código) es la columna vertebral de esta Lexis.

## Alcance

- **Aplica a:** toda funcionalidad o corrección de bug que completó el flujo Issue-Driven y entró en la Fase 8 (Validación BDD).
- **Agentes vinculados:** `warrior-themis` (ejecutor de la Fase 8), `warrior-athena` (orquestador que delega), y cualquier Kata invocada dentro de la Fase 8.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Bloqueo del PR:** el Gate 3 (Comportamental) de `kata-quality-gate` falla cuando el frontmatter de `07-bdd-scenarios.md` referencia rutas de implementación o cuando el agente registra lectura de código durante la Fase 8 de diseño.
2. **Escenario descartado:** los escenarios producidos con violación detectada se descartan; el artefacto se regenera a partir de las fuentes permitidas.
3. **Issue incompleta se vuelve evento de proceso:** ambigüedades repetidas generan revisión de la Fase 2 (`kata-requirements-brief`) — el problema está en el requisito, no en el validador.

## Ejemplos

### Correcto

```
El agente warrior-themis recibe orden de validar la issue #42.
1. Lee: docs/issues/issue-42/01-brief.md, 02-requirements.md.
2. Lee: GitHub Issue #42 (cuerpo + comentarios).
3. Lee: páginas Notion referenciadas por la Issue.
4. Produce docs/issues/issue-42/07-bdd-scenarios.md con:
   - frontmatter declarando esas 4 fuentes;
   - escenarios cubriendo cada AC numerado.
5. No abre ningún archivo bajo src/.
```

### Incorrecto

```
El agente warrior-themis recibe orden de validar la issue #42.
1. Lee los artefactos de las Fases 1-3.
2. "Para entender el flujo de reembolso", abre src/refund_service.py.
3. Escribe escenarios basados en el comportamiento observado en el código.

→ Violación. Los escenarios ahora describen lo que se construyó, no lo
que se pidió — pierden la capacidad de detectar "construimos la cosa
equivocada".
```

## Validación Automatizada

- **Herramienta:** lint del frontmatter de `07-bdd-scenarios.md` rechazando rutas bajo `src/`, `app/`, `lib/`, `tests/`; checklist de `kata-bdd-scenarios-design` exigiendo declaración explícita de las fuentes; revisión por `kata-quality-gate` Check 8 (BDD coverage).
- **Momento:** Fase 8 del flujo Issue-Driven (pre-PR), antes de `kata-pr-prepare`.
- **Métrica:** 0 archivos `07-bdd-scenarios.md` que referencian rutas de implementación; 100% de los escenarios trazables a una fuente de especificación declarada.

## Referencias

- `lex-bdd-gherkin-format` — formato Gherkin obligatorio de los escenarios
- `lex-bdd-no-framework-coupling` — implementación de las pruebas sin framework BDD
- `lex-issue-driven` — flujo Issue-Driven que precede la validación BDD
- `kata-bdd-scenarios-design` — procedimiento de producción de los escenarios
- `kata-bdd-validate-implementation` — procedimiento de validación contra implementación
- `warrior-themis` — agente especializado en validación BDD
