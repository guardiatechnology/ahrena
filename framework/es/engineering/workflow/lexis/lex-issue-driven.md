# Lexis: Desarrollo Orientado por Issue

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Flujo de desarrollo de features y bugfixes orientado por issues de GitHub en el framework Ahrena

## Propósito

En proyectos que adoptan el flujo Issue-Driven Development (orquestado por `warrior-athena`), cada feature o bugfix comienza en una issue de GitHub y atraviesa fases obligatorias de análisis, diseño, implementación y validación. Sin reglas firmes, ese flujo pierde integridad: se saltan gates, los criterios de aceptación se vuelven opcionales, las decisiones arquitectónicas no quedan registradas y la documentación producida se dispersa en ubicaciones inconsistentes.

Esta Lexis existe para garantizar que **toda implementación tenga trazabilidad desde la issue original hasta el PR final**, que **los gates de calidad no sean eludidos**, que **las decisiones arquitectónicas relevantes sean registradas como ADRs** y que **toda la documentación producida por el flujo quede estructurada en `docs/`**.

## Ley

> **Toda implementación conducida por `warrior-athena` DEBE partir de una issue existente, pasar por los tres Gates (Alcance, Calidad y Comportamental), respetar la trazabilidad bidireccional entre criterios de aceptación, escenarios BDD y pruebas, registrar decisiones arquitectónicas relevantes como ADRs en `docs/adr/`, y producir toda la documentación pública del flujo en `docs/issues/issue-{n}/`.**

## Reglas

### 1. Issue obligatoria como punto de partida

El agente **DEBE**:

1. Exigir una referencia de issue existente (`owner/repo#número` o equivalente) antes de iniciar cualquier fase del flujo.
2. Leer la issue vía `kata-mcp-github-read` en la Fase 1.
3. Si la issue no existe o está vacía, informar al usuario y detener — no crear la issue automáticamente ni inferir el alcance.

### 2. Los gates no pueden saltarse

El agente **NO PUEDE**:

1. Avanzar de la Fase 3 a la Fase 4 sin aprobación humana explícita en el Gate 1 (alcance).
2. Crear el PR en la Fase 7 si el Gate 2 (calidad) no resultó en `go`.
3. Crear el PR en la Fase 7 si el Gate 3 (comportamental) no resultó en `go` — i.e., si `08-bdd-validation-report.md` reporta escenarios `missing` o `partial`, o si hay acoplamiento a step-runner BDD.
4. Marcar ítems del Gate 2 o Gate 3 como atendidos sin ejecutar realmente la verificación (ej.: no puede declarar "pruebas pasan" sin ejecutar `pytest`; no puede declarar "los escenarios cubren los ACs" sin el reporte de `kata-bdd-validate-implementation`).

### 3. Trazabilidad triple AC ↔ Escenario ↔ Prueba

Para que el Gate 2 y el Gate 3 pasen:

1. **Cada criterio de aceptación** numerado en la Fase 2 **DEBE** tener al menos una prueba que lo cubra (trazabilidad Gate 2).
2. **Cada prueba nueva** introducida en la Fase 4 **DEBE** estar vinculada a al menos un AC mediante la convención `AC-{N}` en el nombre o docstring (trazabilidad Gate 2).
3. **Cada AC DEBE** tener al menos un escenario Gherkin `SCN-{N}` con etiqueta `@AC-{N}` en `07-bdd-scenarios.md` (trazabilidad Gate 3, per `lex-bdd-gherkin-format`).
4. **Cada escenario `SCN-{N}` DEBE** tener al menos una prueba estándar que lo referencie por nombre o docstring (trazabilidad Gate 3, per `lex-bdd-no-framework-coupling`).
5. Las pruebas nuevas sin AC correspondiente se tratan como **scope creep** y bloquean el Gate 2.
6. Los escenarios sin prueba correspondiente se tratan como **gap de comportamiento** y bloquean el Gate 3.

### 4. ADRs obligatorios para decisiones arquitectónicas relevantes

El agente **DEBE** invocar `kata-adr-write` cuando la Fase 3 identifique:

1. Nueva elección tecnológica (framework, librería, patrón arquitectónico).
2. Desviación de un patrón existente en el codebase.
3. Trade-off significativo entre alternativas.
4. Decisión que afecta a múltiples componentes o contratos externos.

El ADR **DEBE** ser guardado en `docs/adr/ADR-{n}-{título-en-kebab}.md` en el formato MADR simplificado.

### 5. Documentación en `docs/`

El agente **DEBE** estructurar toda la documentación pública del flujo en `docs/`:

1. `docs/issues/issue-{n}/01-brief.md` — análisis de la issue (Fase 1)
2. `docs/issues/issue-{n}/02-requirements.md` — ACs numerados (Fase 2)
3. `docs/issues/issue-{n}/03-architecture.md` — diseño (Fase 3)
4. `docs/issues/issue-{n}/05-security-review.md` — revisión de seguridad (Fase 5)
5. `docs/issues/issue-{n}/06-quality-report.md` — informe del Gate 2 (Fase 6)
6. `docs/issues/issue-{n}/07-bdd-scenarios.md` — escenarios Gherkin (Fase 8.1)
7. `docs/issues/issue-{n}/08-bdd-validation-report.md` — informe del Gate 3 (Fase 8.2)
8. `docs/adr/ADR-{n}-*.md` — ADRs cuando corresponda

El estado efímero de orquestación (checkpoint entre fases) puede ir en `.ahrena/workflow/issue-{n}/checkpoint.md`, **nunca** en `docs/`. El checkpoint **DEBE** usar front-matter YAML versionado (ver Regla 7).

### 7. Schema versionado del checkpoint

El agente **DEBE** mantener el checkpoint en `.ahrena/workflow/issue-{n}/checkpoint.md` con **front-matter YAML estructurado** que contenga al menos:

```yaml
---
schema_version: 1
issue: 42
repo: guardiafinance/ahrena
phase_completed: 3
phase_next: 4
artifacts:
  brief: docs/issues/issue-42/01-brief.md
  requirements: docs/issues/issue-42/02-requirements.md
  architecture: docs/issues/issue-42/03-architecture.md
adrs:
  - ADR-008-use-event-sourcing-for-refund-audit-trail.md
gate_1:
  status: approved | pending | rejected
  approved_at: "2026-04-16T14:30:00Z"
  approver: "@user"
gate_2:
  status: go | no-go | pending
  last_run_at: "..."
delegations:
  - warrior: warrior-daedalus
    kata: kata-api-design-oas
    status: completed | running | failed | timed-out
    started_at: "..."
    completed_at: "..."
    output_refs: ["docs/..."]
updated_at: "2026-04-16T15:00:00Z"
---

# Notas narrativas (opcional, para contexto humano)
```

El contenido tras `---` puede contener prosa libre para lectura humana, pero el estado operativo **DEBE** estar en el front-matter. Los campos desconocidos se preservan; la eliminación de campos obligatorios invalida el checkpoint y exige reconstrucción manual.

### 8. Protocolo de delegación (máquina de estados)

Cuando `warrior-athena` delega una fase a un warrior especialista (Apollo, Hephaestus, Daedalus, Kronos, Atlas, Hera, Hestia, Demeter, Iris), el handoff **DEBE** seguir una máquina de estados registrada en el checkpoint:

```
delegated → running → completed | failed | timed-out
```

Reglas:

1. **`delegated`**: Athena graba la entrada de delegación en el front-matter del `checkpoint.md` (warrior, kata, refs de entrada, `started_at`). Especialista es invocado.
2. **`running`**: el especialista confirma actualizando la entrada con `status: running` en el primer paso. Si el agente no logra confirmar en 60 segundos de la invocación, la delegación se trata como `timed-out`.
3. **`completed`**: el especialista termina y graba `output_refs: [...]` + `completed_at`; status pasa a `completed`. Athena retoma desde el checkpoint.
4. **`failed`**: el especialista registra motivo explícito + outputs parciales (si los hay). Athena presenta la falla al humano y pide dirección (retry, escalar, abandonar).
5. **`timed-out`**: inferido por Athena cuando no hay actualización de status dentro del deadline configurado (default: 30 min para `kata-*-implement`; 10 min para katas cortos). Tratado como `failed` — el humano decide.

Athena **NUNCA** re-invoca silenciosamente una delegación en `running` o `completed`. La re-invocación tras `failed`/`timed-out` **DEBE** crear nueva entrada de delegación (preservando la anterior como trazabilidad) — nunca mutar el historial.

El formato de la entrada de delegación está definido en la Regla 7 (lista `delegations:`); los timestamps y status son fuente de verdad para el estado de la orquestación.

### 9. El checkpoint se mantiene esbelto

El archivo checkpoint se re-lee en cada transición de fase. Para mantener el consumo de tokens previsible, el checkpoint **DEBE**:

- Contener solo **estado operativo activo** (fase actual, última delegación, outcomes de los gates, punteros a artefactos).
- **No duplicar contenido** de `docs/issues/issue-{n}/*.md` — esos son la narrativa durable; el checkpoint carga referencias (rutas), no copias.
- **No acumular historial más allá de la última delegación failed/timed-out mantenida para auditoría** (historial más antiguo pertenece a los archivos de narrativa de la issue, no al checkpoint).

Tamaño objetivo: menos de ~2 KB tras el flujo completo. Si el checkpoint excede 5 KB, el agente **DEBE** podar entradas históricas antes de continuar; el contenido podado va a `history.md` hermano (opcional) o se descarta si ya está capturado en `docs/issues/issue-{n}/`.

### 6. El scope creep es bloqueo, no aviso

El Gate 2 **DEBE** fallar si:

1. Los archivos modificados están fuera del alcance declarado en la Fase 3.
2. Funciones o clases públicas nuevas no están justificadas por algún AC.

Cuando se detecte, el agente **DEBE** presentar dos opciones al usuario:
- Ampliar los ACs (nueva iteración del Gate 1) para cubrir el código adicional.
- Eliminar el código fuera de alcance del PR actual y abrir una nueva issue para él.

### 10. Fase 8 (Validación Comportamental) y Gate 3

Luego de que el Gate 2 resulte en `go`, `warrior-athena` **DEBE** delegar la Fase 8 a `warrior-themis` antes de invocar `kata-pr-prepare`:

1. **Fase 8.1** — `kata-bdd-scenarios-design` produce `07-bdd-scenarios.md` derivando escenarios **exclusivamente** de las fuentes de especificación (per `lex-bdd-spec-only-sources`). Leer código está PROHIBIDO en esta sub-fase.
2. **Fase 8.2** — `kata-bdd-validate-implementation` produce `08-bdd-validation-report.md` mapeando cada `SCN-{N}` a las pruebas existentes (la lectura de pruebas está permitida en esta sub-fase) y verifica la ausencia de step-runner BDD en los manifiestos.
3. **Gate 3 (Comportamental)** — pasa cuando:
   - Todos los ACs tienen al menos un escenario (`@AC-{N}` presente).
   - Todos los escenarios tienen al menos una prueba estándar referenciando `SCN-{N}`.
   - Ningún manifiesto declara un step-runner BDD prohibido (per `lex-bdd-no-framework-coupling`).
   - Ninguna AC permanece con `status: BLOCKED` por ambigüedad de la Issue.
4. Cuando el Gate 3 da `no-go`, `warrior-athena` **DEBE** delegar los gaps reportados al warrior responsable (Apollo, Hephaestus, Iris) antes de avanzar a la Fase 7.

## Alcance

- **Se aplica a:** toda invocación de `/cry-implement-issue` y toda actividad conducida por `warrior-athena`.
- **Agentes vinculados:** `warrior-athena` (orquestador) y todos los warriors/katas delegados durante el flujo.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Gate saltado:** un PR creado sin el Gate 2 equivale a código no revisado en producción; bloquea el merge y exige reabrir el flujo desde la Fase 5.
2. **Trazabilidad rota:** AC sin prueba o prueba sin AC invalida el PR; requiere corrección antes de reabrir el Gate 2.
3. **ADR ausente:** decisión arquitectónica sin ADR deja a la organización sin historial de racional; el ADR debe ser escrito retroactivamente antes del merge.
4. **Documentación fuera de `docs/`:** rompe el patrón de auditoría; los archivos deben moverse a la estructura correcta antes del merge.
5. **Scope creep no declarado:** el código fuera de alcance se revierte o se justifica en una nueva iteración del Gate 1.

## Ejemplos

### Correcto

```
# Flujo conducido a partir de una issue existente:
/cry-implement-issue 42 guardiafinance/ahrena

# Athena lee la issue #42, produce:
# docs/issues/issue-42/01-brief.md
# docs/issues/issue-42/02-requirements.md   (AC-1, AC-2, AC-3)
# docs/issues/issue-42/03-architecture.md
# docs/adr/ADR-007-use-fastapi-routers.md   (decisión relevante)

# Espera Gate 1 → humano aprueba
# Apollo implementa: cada prueba referencia AC-N
# Gate 2 ejecuta 6 checks, todos ✅
# docs/issues/issue-42/06-quality-report.md registra el resultado
# PR creado con body referenciando los artefactos anteriores
```

### Incorrecto

```
# ❌ Athena inicia el flujo sin issue:
/cry-implement-issue "agregar refund"

# ❌ Humano pide "saltar Gate 1, ya está ok":
# (el Gate 1 es obligatorio — Athena debe rehusarse)

# ❌ Prueba nueva sin vínculo a AC:
# def test_random_helper(): ...   (sin docstring AC-N)

# ❌ ADR guardado en ubicación incorrecta:
# .ahrena/workflow/issue-42/adr.md
# (la ruta correcta es docs/adr/ADR-{n}-*.md)

# ❌ Modificación de archivo fuera del alcance declarado:
# (el Gate 2 bloquea; el usuario decide entre ampliar AC o abrir una nueva issue)
```

## Validación Automatizada

- **Herramienta:** `kata-quality-gate` (Gate 2 y Check 8 del Gate 3) ejecuta la verificación de trazabilidad, scope creep, best practices, cobertura de escenarios BDD y acoplamiento a framework antes del PR; `kata-bdd-validate-implementation` produce el reporte consumido por el Check 8; `scripts/validate.py` verifica la presencia obligatoria de artefactos en `docs/issues/issue-{n}/` cuando el flujo concluye.
- **Momento:** Gate 1 (antes de la Fase 4), Gate 2 (antes de la Fase 8), Gate 3 (antes de la Fase 7).
- **Métrica:** 100% de las issues pasan por los tres gates; 100% de los ACs tienen al menos una prueba; 0 pruebas sin AC correspondiente; 100% de los ACs tienen al menos un escenario `SCN-{N}`; 0 escenarios `missing` o `partial` en el Gate 3; 100% de las decisiones arquitectónicas relevantes tienen ADR en `docs/adr/`.
