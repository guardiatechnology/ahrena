# Kata: Brief Arquitectónico

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 3 del flujo Issue-Driven — mapeo de componentes afectados, decisiones de diseño y delegación a warriors especialistas cuando aplica

## Objetivo

A partir del brief (Fase 1) y de los requisitos (Fase 2), producir un documento de diseño arquitectónico que contenga: mapa de componentes afectados, enfoque técnico propuesto, decisiones por tomar, delegación a warriors especialistas (Daedalus para API, Kronos para eventos), e invocación de `kata-adr-write` cuando haya decisión arquitectónica relevante. El documento final en `docs/issues/issue-{n}/03-architecture.md` es la base del Gate 1 y delimita el alcance contra el cual el Gate 2 hará scope creep check.

## Cuándo Usar

- Fase 3 del flujo orquestado por `warrior-athena`, tras la Fase 2 (`kata-requirements-brief`)
- Cuando es necesario definir técnicamente cómo implementar los ACs antes de codificar

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Brief Fase 1 | Sí | `docs/issues/issue-{n}/01-brief.md` |
| Requisitos Fase 2 | Sí | `docs/issues/issue-{n}/02-requirements.md` |
| Stack del proyecto | Sí | Lenguaje, frameworks, patrones existentes (detectado al leer el repo) |

## Workflow

```
Progreso:
- [ ] 1. Leer brief + requisitos
- [ ] 2. Mapear componentes afectados
- [ ] 3. Proponer enfoque técnico
- [ ] 4. Identificar decisiones arquitectónicas relevantes
- [ ] 5. Delegar a especialistas si aplica (Daedalus/Kronos)
- [ ] 6. Invocar kata-adr-write para cada decisión relevante
- [ ] 7. Persistir en docs/issues/issue-{n}/03-architecture.md
- [ ] 8. Actualizar checkpoint
```

### Paso 1: Leer brief + requisitos

1. Leer `01-brief.md` y `02-requirements.md` en `docs/issues/issue-{n}/`.
2. Si falta alguno, informar y detener — las fases predecesoras deben estar completas.
3. Identificar ACs que exigen atención arquitectónica especial (ej.: performance, consistencia, idempotencia).

### Paso 2: Mapear componentes afectados

Para cada AC:

1. Identificar archivos/módulos existentes que serán modificados.
2. Identificar nuevos archivos/módulos que serán creados.
3. Identificar contratos externos afectados (APIs, eventos, bases de datos, colas).
4. Consolidar en una tabla:

| Componente | Tipo | Acción | ACs cubiertos |
|---|---|---|---|
| `src/refunds/service.py` | módulo | crear | AC-1, AC-2 |
| `src/payments/repository.py` | módulo | modificar (agregar método) | AC-3 |
| `openapi/refunds.yaml` | spec | modificar | AC-1 |
| `events/refund.created` | evento | crear | AC-2 |

Esta tabla es la **frontera de alcance** usada por `kata-quality-gate` en el check de scope creep.

### Paso 3: Proponer el enfoque técnico

Describir en prosa estructurada:

1. **Flujo principal:** secuencia de llamadas/eventos del caso feliz.
2. **Flujos alternativos:** errores, idempotencia, retry.
3. **Persistencia:** entidades afectadas, migraciones necesarias.
4. **Integraciones externas:** contratos, autenticación, rate limits.
5. **Observabilidad:** logs, métricas, traces relevantes.

### Paso 4: Identificar decisiones arquitectónicas relevantes

Para cada punto de diseño, preguntar: ¿es una **decisión** o un **seguimiento de patrón existente**?

Usar el checklist de `codex-issue-workflow` (sección "Cuándo generar ADR"):

| ¿Generar ADR? | Ejemplos |
|:-:|---|
| ✅ | Nueva elección tecnológica; desviación de patrón; trade-off significativo; afecta múltiples componentes; afecta contrato externo |
| ❌ | Bugfix puntual; refactor local siguiendo patrón; endpoint nuevo siguiendo estructura existente |

Registrar cada decisión candidata con: título, motivación, alternativas consideradas.

### Paso 5: Delegar a especialistas si aplica

**Si la issue involucra diseño de API REST:**
1. Invocar `warrior-daedalus` → `kata-api-design-oas`
2. Pasar como contexto: el brief, los requisitos y los componentes afectados.
3. Daedalus produce OAS + Markdown en `paths.oas`.
4. Referenciar esos archivos en el documento de arquitectura de esta fase.

**Si la issue involucra diseño de eventos (CloudEvents):**
1. Invocar `warrior-kronos` → `kata-events-doc`
2. Pasar los mismos artefactos como contexto.
3. Kronos produce catálogo de eventos en `paths.events`.
4. Referenciar esos archivos en el documento de arquitectura.

Registrar en el checkpoint qué warrior fue delegado y dónde está el output.

### Paso 6: Invocar `kata-adr-write` para cada decisión relevante

Para cada decisión identificada en el Paso 4 que merece ADR:

1. Invocar `kata-adr-write` con: título de la decisión, contexto, decisión propuesta, alternativas.
2. `kata-adr-write` crea `docs/adr/ADR-{n}-{título}.md` con status `proposed`.
3. El ADR transiciona a `accepted` tras la aprobación en el Gate 1.
4. Referenciar cada ADR creado en el documento de arquitectura.

### Paso 7: Persistir en `docs/issues/issue-{n}/03-architecture.md`

Estructura:

```markdown
# Arquitectura — Issue #{n}: {título}

- **Referencias:** [Brief](./01-brief.md) · [Requisitos](./02-requirements.md)
- **Fecha:** {YYYY-MM-DD}

## Componentes Afectados

| Componente | Tipo | Acción | ACs cubiertos |
|---|---|---|---|
| ... | ... | ... | ... |

> Esta tabla define el alcance exacto de archivos a modificar.
> Modificaciones fuera de esta tabla son bloqueadas por el Gate 2 como scope creep.

## Enfoque Técnico

### Flujo principal

{descripción en prosa, diagrama de secuencia en Mermaid opcional}

### Flujos alternativos

- **Error {X}:** {cómo se maneja}
- **Idempotencia:** {cómo se garantiza}
- **Retry:** {política}

### Persistencia

{entidades afectadas, migraciones necesarias}

### Integraciones externas

{contratos, auth, rate limits}

### Observabilidad

{logs, métricas, traces}

## Delegaciones a Especialistas

- **Daedalus (API):** ver `{ruta OAS}`, `{ruta doc}`
- **Kronos (Eventos):** ver `{ruta catálogo}`

(omitir secciones no aplicables)

## Decisiones Arquitectónicas (ADRs)

- [ADR-{n}: {título}](../../adr/ADR-{n}-{slug}.md) — status: proposed
- [ADR-{m}: {título}](../../adr/ADR-{m}-{slug}.md) — status: proposed

(sección ausente si no hubo decisión relevante)

## Riesgos Técnicos

- {Riesgo 1 y mitigación}
- {Riesgo 2 y mitigación}

## Siguiente fase

Gate 1 — Aprobación de Alcance (espera aprobación humana).
```

### Paso 8: Actualizar checkpoint

1. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase completada: 3
   - siguiente: Gate 1 (aprobación humana)
   - referencias: `03-architecture.md`, ADRs creados
   - delegaciones: warriors especialistas invocados y sus outputs
2. `warrior-athena` pide aprobación humana antes de avanzar a la Fase 4.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Documento de arquitectura | Markdown | `docs/issues/issue-{n}/03-architecture.md` |
| ADRs (0 o más) | Markdown MADR | `docs/adr/ADR-{n}-*.md` |
| OAS/doc/events (si aplica) | según Daedalus/Kronos | `paths.oas`, `paths.events` |
| Checkpoint actualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restricciones

- **La tabla de componentes es vinculante:** define el alcance exacto que el Gate 2 usará para scope creep check. Todo lo que esté fuera de esa tabla será bloqueado.
- **ADRs en status `proposed`:** hasta el Gate 1, todos los ADRs producidos en esta fase quedan con status `proposed`. La transición a `accepted` solo ocurre tras aprobación humana.
- **La delegación no sustituye el documento de esta fase:** incluso al delegar a Daedalus/Kronos, el kata debe producir el `03-architecture.md` con el contexto general y referencias a los outputs de los especialistas.
- **Sin codificar:** este kata describe **qué** y **dónde**, no **cómo** (Apollo hará el cómo en la Fase 4).
- **Destino fijo:** `docs/issues/issue-{n}/03-architecture.md` y `docs/adr/ADR-*` (según `lex-issue-driven`).

## Referencias

- `lex-issue-driven` — leyes del flujo
- `codex-issue-workflow` — checklist de cuándo generar ADR
- `kata-adr-write` — escritura de ADR en formato MADR
- `warrior-daedalus`, `kata-api-design-oas` — delegación para API
- `warrior-kronos`, `kata-events-doc` — delegación para eventos
- `codex-codex`, `codex-lexis` — convenciones de artefacto
