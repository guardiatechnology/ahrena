# Lexis: Desarrollo Orientado por Issue

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Flujo de desarrollo de features y bugfixes orientado por issues de GitHub en el framework Ahrena

## Propósito

En proyectos que adoptan el flujo Issue-Driven Development (orquestado por `warrior-athena`), cada feature o bugfix comienza en una issue de GitHub y atraviesa fases obligatorias de análisis, diseño, implementación y validación. Sin reglas firmes, ese flujo pierde integridad: se saltan gates, los criterios de aceptación se vuelven opcionales, las decisiones arquitectónicas no quedan registradas y la documentación producida se dispersa en ubicaciones inconsistentes.

Esta Lexis existe para garantizar que **toda implementación tenga trazabilidad desde la issue original hasta el PR final**, que **los gates de calidad no sean eludidos**, que **las decisiones arquitectónicas relevantes sean registradas como ADRs** y que **toda la documentación producida por el flujo quede estructurada en `docs/`**.

## Ley

> **Toda implementación conducida por `warrior-athena` DEBE partir de una issue existente, pasar por ambos Gates (Alcance y Calidad), respetar la trazabilidad bidireccional entre criterios de aceptación y pruebas, registrar decisiones arquitectónicas relevantes como ADRs en `docs/adr/`, y producir toda la documentación pública del flujo en `docs/issues/issue-{n}/`.**

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
3. Marcar ítems del Gate 2 como atendidos sin ejecutar realmente la verificación (ej.: no puede declarar "pruebas pasan" sin ejecutar `pytest`).

### 3. Trazabilidad bidireccional AC ↔ prueba

Para que el Gate 2 pase:

1. **Cada criterio de aceptación** numerado en la Fase 2 **DEBE** tener al menos una prueba que lo cubra.
2. **Cada prueba nueva** introducida en la Fase 4 **DEBE** estar vinculada a al menos un AC mediante la convención `AC-{N}` en el nombre o docstring de la prueba.
3. Las pruebas nuevas sin AC correspondiente se tratan como **scope creep** y bloquean el gate.

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
6. `docs/adr/ADR-{n}-*.md` — ADRs cuando corresponda

El estado efímero de orquestación (checkpoint entre fases) puede ir en `.ahrena/workflow/issue-{n}/checkpoint.md`, **nunca** en `docs/`.

### 6. El scope creep es bloqueo, no aviso

El Gate 2 **DEBE** fallar si:

1. Los archivos modificados están fuera del alcance declarado en la Fase 3.
2. Funciones o clases públicas nuevas no están justificadas por algún AC.

Cuando se detecte, el agente **DEBE** presentar dos opciones al usuario:
- Ampliar los ACs (nueva iteración del Gate 1) para cubrir el código adicional.
- Eliminar el código fuera de alcance del PR actual y abrir una nueva issue para él.

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

- **Herramienta:** `kata-quality-gate` (Gate 2) ejecuta la verificación de trazabilidad, scope creep y best practices antes del PR; `scripts/validate.py` verifica la presencia obligatoria de artefactos en `docs/issues/issue-{n}/` cuando el flujo concluye.
- **Momento:** Gate 1 (antes de la Fase 4), Gate 2 (antes de la Fase 7).
- **Métrica:** 100% de las issues pasan por ambos gates; 100% de los ACs tienen al menos una prueba; 0 pruebas sin AC correspondiente; 100% de las decisiones arquitectónicas relevantes tienen ADR en `docs/adr/`.
