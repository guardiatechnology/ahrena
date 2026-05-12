# Lexis: Labels Canónicos de Status en Issue y PR

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Issues y Pull Requests en repositorios Guardia que participan en el flujo Issue-Driven

## Propósito

El body de la Issue (canonical per ADR-002), la Issue y el PR llevan el mismo trabajo en momentos distintos del ciclo. Sin un conjunto canónico de labels de status, el agente pierde la referencia cruzada, los dashboards se desalinean, y el cálculo agregado de child↔subtasks queda impreciso. Esta Ley codifica las labels `status: <name>` que espejan el enum de `lex-agent-planning`, **lo separa en dos ejes disjuntos** (dev cycle y release cycle), garantiza consistencia intra-artefacto, y mantiene ortogonalidad con las labels de Discovery (`pending-spec`/`spec-ready`).

## Ley

> **Toda Issue y todo PR que participan en el flujo Issue-Driven DEBEN llevar exactamente una label `status: <name>` del conjunto canónico. El conjunto se divide en dos ejes disjuntos: **Eje A (dev cycle)** aplicable a Issues/PRs de feature/fix/chore/refactor (`status: todo`, `status: development`, `status: to review`, `status: review`, `status: done`); **Eje B (release cycle)** aplicable exclusivamente a la release Issue dedicada creada por Janus (`status: to release`, `status: release`, `status: done`). El terminal `status: abandoned` es compartido por los dos ejes. La mutex es **intra-artefacto**: ninguna Issue o PR lleva dos labels `status:*` simultáneamente. Aplicar label del Eje B en Issue/PR del Eje A (o viceversa) es PROHIBIDO. La label `status:*` es ortogonal a las labels de Discovery (`pending-spec`/`spec-ready`) y a las labels de tipo (`feature request ➕`, etc.) — múltiples ejes coexisten.**

## Alcance

- **Se aplica a:** todas las Issues abiertas vía templates aprobados (`feature-request`, `user-story-for-api`, `user-story-for-frontend`, `simple-task`, `subtask`, **release** — nuevo template introducido por ADR-002 / plan-046 Step 3.5), y todos los PRs en repositorios Guardia.
- **Agentes vinculados:**
  - Eje A — `warrior-eunomia` (`— → todo`), `warrior-athena` (`todo → development`, `development → to review`, `to review → done`), `warrior-argos` (`to review ↔ review`).
  - Eje B — `warrior-janus` (`— → to release`, `to release → release`, `release → done`).
- **Excepciones:**
  - **Epic** no recibe `status:*` — se descompone en child Issues, cada una con su propio ciclo (Eje A). El Epic se cierra cuando todos los hijos (`Tracked by`) alcanzan `done`.
  - **Issues generadas por Dependabot** o scanners de seguridad siguen su propio flujo y quedan exentas.

## Rules

### 1. Eje A — Dev cycle (Issues/PRs de feature/fix/chore/refactor)

| Label | Color sugerido | Cuándo aplicar | Owner |
|---|---|---|---|
| `status: todo` | `#cccccc` (gris claro) | Plan canónico en el body de la Issue, branch vinculada, worktree listo | `warrior-eunomia` (fallback: agente de la sesión) |
| `status: development` | `#83d2ff` (azul claro) | Implementación en curso (Athena Phase 4) | `warrior-athena` |
| `status: to review` | `#fff3a3` (amarillo claro) | PR abierto, esperando que el reviewer lo tome | `warrior-athena` (entrada); `warrior-argos` (retorno de `review`) |
| `status: review` | `#fbca04` (amarillo) | Argos o humano revisando activamente | `warrior-argos` |
| `status: done` | `#0e8a16` (verde) | PR mergeado; Issue cerrada vía `Closes #N` | `warrior-athena` (en el merge) |
| `status: abandoned` | `#6e6e6e` (gris oscuro) | Plan descartado (terminal alternativo) | creador u owner actual |

### 2. Eje B — Release cycle (exclusivamente release Issue dedicada)

| Label | Color sugerido | Cuándo aplicar | Owner |
|---|---|---|---|
| `status: to release` | `#ffb178` (naranja claro) | Janus abrió release Issue; populó `Tracks: #N1, #N2, ...` | `warrior-janus` |
| `status: release` | `#e07400` (naranja) | `kata-release-prepare` corriendo; humano aprobó bump/changelog | `warrior-janus` |
| `status: done` | `#0e8a16` (verde) | Tag empujada, `validate-tag.yml` pasó, Release publicada | `warrior-janus` |
| `status: abandoned` | `#6e6e6e` (gris oscuro) | Release abortada antes del tag | `warrior-janus` |

La release Issue es creada por Janus como punto de entrada del release cycle. No existe "release branch": el ciclo opera sobre la release Issue + tag + GitHub Release. Detalles en `warrior-janus` y `kata-release-prepare`.

### 3. Mutex intra-artefacto

En cualquier instante, **una misma Issue (o PR)** lleva exactamente una label `status:*`. Aplicar dos labels `status:*` simultáneamente a la misma Issue/PR (ej.: `status: to review` + `status: review`) es PROHIBIDO.

La mutex **no** es cross-artifact: la release Issue (Eje B) coexiste con N feature Issues en `done` (Eje A) sin conflicto — son artefactos distintos.

Cada transición se ejecuta mediante:

```bash
gh issue edit {N} --remove-label "status: <previous>" --add-label "status: <next>"
gh pr edit {N}    --remove-label "status: <previous>" --add-label "status: <next>"
```

Preferir MCP `update_issue` / `update_pull_request` cuando el servidor GitHub MCP esté listado en `mcp.servers` y activo (per `lex-mcp` regla 1).

### 4. Cross-cycle labeling prohibido

Las labels del Eje B (`status: to release`, `status: release`) **no pueden** ser aplicadas en Issues/PRs de feature/fix/chore/refactor. Las labels del Eje A (`status: todo`, `status: development`, `status: to review`, `status: review`) **no pueden** ser aplicadas en release Issue.

Detección: el tipo de la Issue (`gh issue view {N} --json type`) determina el eje permitido. La release Issue lleva Issue Type `Task` (o `Feature` cuando se crea como release feature por convención del template) + label `release ↗️`. Cross-cycle labeling es violación del HARD-GATE.

### 5. Sincronización Issue ↔ PR

Cuando un PR es abierto para una Issue en `status: development`, el agente que ejecuta la transición (per `lex-agent-planning` Tabla A) DEBE actualizar simultáneamente:

1. Label `status: <name>` en la Issue.
2. Label `status: <name>` en el PR.
3. Disparar `kata-flush-plan-to-issue` para garantizar que el body de la Issue refleja el estado post-transición.

La falla en cualquiera de los tres produce drift detectable en el Gate 2 (per `kata-quality-gate`).

### 6. Ortogonalidad con labels de Discovery

Las labels de Discovery (`pending-spec`, `spec-ready`, definidas por plan-038) operan en un eje separado:

- `pending-spec`/`spec-ready` controlan **entrada** en el flujo Athena para US-child (User Story child de Epic). Conviven con `status:*` en la misma Issue.
- US-child creada por Calliope nace con `pending-spec` y **sin** `status:*`. Recibe `status: todo` solo cuando gana `spec-ready` (transición hecha por el PM correspondiente después de producir la spec).
- Bug y Tech-task saltan el gate de spec y reciben `status: todo` directo en la creación por Eunomia.

### 7. Epic no recibe `status:*`

Epic es descompuesto por Calliope (plan-038) y nunca pasa por Athena directamente. El Epic no tiene ciclo `todo → development → ...` propio; su estado se deriva de `Tracked by` (children con `status:*`). Aplicar `status:*` a un Epic es PROHIBIDO.

### 8. Creación inicial de las labels en el repositorio

Cada repositorio que adopta el flujo DEBE crear las labels vía `gh label create` (script idempotente en `scripts/bootstrap_status_labels.sh`). Todas las labels ya existen desde plan-043 (PR #93); plan-046 no introduce labels nuevas — solo reorganiza la semántica en dos ejes.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../quality/lex-hard-gate-pattern.md), el bloque textual de esta Lex se expresa canónicamente como:

```
<HARD-GATE>
warrior-eunomia, warrior-athena, warrior-argos, warrior-janus y cualquier
otro agente MUST NOT aplicar label `status:*` en Issue o PR sin
satisfacer TODOS los criterios:

  (a) Label pertenece al conjunto canónico del eje correcto:
      - Eje A (feature/fix/chore Issues/PRs): todo | development |
        to review | review | done | abandoned
      - Eje B (release Issue exclusivamente): to release | release |
        done | abandoned
  (b) Issue/PR no está en estado terminal (done|abandoned) al recibir
      la nueva label
  (c) Ninguna otra label `status:*` permanece en la Issue/PR después de la
      transición (mutex intra-artefacto aplicado)
  (d) Label del eje correcto para el tipo de la Issue/PR:
      - Issues/PRs de feature/fix/chore/refactor → Eje A únicamente
      - Release Issue (label `release ↗️`) → Eje B únicamente
  (e) Body de la Issue actualizado por el último kata-flush-plan-to-issue
      (Eje A) o Tracks populado con PRs mergeados desde el último
      tag (Eje B, transición `— → to release`)
  (f) Issue no es Epic (Epic no recibe status:*)

Esta regla se aplica a TODA Issue y TODO PR en el flujo Issue-Driven,
independientemente de:
  - tamaño percibido ("es solo un chore")
  - urgencia ("incendio en producción")
  - quién lo pidió ("el CEO lo solicitó")
  - confianza del equipo ("ya probamos mucho")

Excepción declarada: Epic e Issues generadas por Dependabot/scanners
siguen su propio flujo. Todo otro tipo de Issue/PR en el flujo
Issue-Driven respeta la mutex y la separación de ejes.
</HARD-GATE>
```

## Ejemplos

### Correcto — Eje A (feature Issue + PR)

```bash
# Eunomia crea Issue #96 con body canónico
gh issue edit 96 --add-label "status: todo"

# Athena entra en Phase 4
gh issue edit 96 --remove-label "status: todo" --add-label "status: development"

# Athena abre PR #97; aplica label simultáneamente
gh pr create ... && gh pr edit 97 --add-label "status: to review"
gh issue edit 96 --remove-label "status: development" --add-label "status: to review"

# Argos inicia revisión
gh pr edit 97 --remove-label "status: to review" --add-label "status: review"
gh issue edit 96 --remove-label "status: to review" --add-label "status: review"

# Argos termina sin aprobar; humano cobrado en 3×15min
gh pr edit 97 --remove-label "status: review" --add-label "status: to review"
gh issue edit 96 --remove-label "status: review" --add-label "status: to review"

# Humano aprueba; merge cierra Issue
gh pr edit 97 --remove-label "status: to review" --add-label "status: done"
gh issue edit 96 --remove-label "status: to review" --add-label "status: done"
```

### Correcto — Eje B (release Issue)

```bash
# Janus abre release Issue #100; popula Tracks con PRs mergeados
# desde el último tag
gh issue create --title "release: 0.4.0" \
  --body "Tracks: #93, #96, #98, #99" \
  --label "release ↗️,status: to release"

# Janus inicia kata-release-prepare
gh issue edit 100 --remove-label "status: to release" --add-label "status: release"

# Janus concluye: tag empujada, validate-tag.yml pasa, Release creada
gh issue edit 100 --remove-label "status: release" --add-label "status: done"
```

### Incorrecto

```bash
# ❌ Dos labels status:* simultáneas (viola mutex intra-artefacto)
gh issue edit 96 --add-label "status: to review" --add-label "status: review"

# ❌ Cross-cycle labeling: status: to release en Issue de feature
gh issue edit 96 --add-label "status: to release"
# Issue #96 es feature (Eje A); status: to release pertenece al Eje B

# ❌ Cross-cycle labeling inverso: status: development en release Issue
gh issue edit 100 --add-label "status: development"
# Issue #100 es release Issue (Eje B); status: development pertenece al Eje A

# ❌ Aplicar status:* en Epic
gh issue edit 88 --add-label "status: development"
# Issue #88 tiene Issue Type Epic — prohibido per Rule 7
```

## Validación Automatizada

- **Herramienta:**
  - Script `scripts/bootstrap_status_labels.sh` crea las labels idempotentemente en cualquier repositorio.
  - PR review (humano o Argos) verifica:
    - Alineación entre label de la Issue y label del PR (mismo eje, mismo estado).
    - Body de la Issue refleja el último flush (`kata-flush-plan-to-issue` fue ejecutado en la transición).
    - Eje correcto aplicado al tipo de la Issue (feature ⇒ Eje A; release Issue ⇒ Eje B).
  - GitHub Action de verificación periódica (futuro) detecta:
    - Issues/PRs con 0 o ≥2 labels `status:*`
    - Cross-cycle labeling (label de Eje A en release Issue, o label de Eje B en feature Issue)
    - Issues con Issue Type Epic llevando `status:*`
- **Momento:** al abrir/actualizar Issue, al abrir/actualizar PR, en cada transición de owner, en el Gate 2 (`kata-quality-gate`).
- **Métrica:** 0 Issues/PRs con label `status:*` cross-cycle; 0 Epics con `status:*`; 100% de las transiciones registradas por el owner declarado; 100% de las release Issues con `Tracks:` populado.

## Referencias

- ADR-002 — split en dos ejes (absorción de plan-045)
- `lex-agent-planning` — enum unificado de `status:` y tablas de owners (Tabla A / Tabla B)
- `lex-issue-quality` — requisitos base de Issues (template, label de tipo, Issue Type, assignee, Why/What/How)
- `lex-issue-first` — todo cambio parte de una Issue
- `lex-pr-quality` — requisitos del PR (label de tamaño, CODEOWNERS, etc.) — complementario
- `lex-mcp` — preferencia MCP + fallback CLI para `update_issue` / `update_pull_request`
- `lex-hard-gate-pattern` — sintaxis del bloque `<HARD-GATE>`
- `codex-agent-planning` — manual operacional con flujo visual y loop 3×15min
- `codex-labels` — convención general de labels en GitHub
- `kata-flush-plan-to-issue` — disparado en cada transición
- `kata-release-prepare`, `kata-release-publish` — operaciones de Janus en el Eje B
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners de las transiciones
