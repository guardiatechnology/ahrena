# Lexis: Labels Canónicos de Status en Issue y PR

> **Prefijo:** `lex-` | **Tipo:** Ley Inviolable | **Alcance:** Issues y Pull Requests en repositorios Guardia que participan del flujo Issue-Driven

## Propósito

Plan, Issue de GitHub y PR cargan el mismo trabajo en momentos distintos del ciclo. Sin un conjunto canónico de labels de status, el agente pierde la referencia cruzada entre los tres artefactos, los dashboards se desalinean, y el cálculo agregado de child↔subtasks se vuelve impreciso. Esta Ley codifica los 7 labels `status: <name>` que espejean el enum unificado de `lex-agent-planning`, garantiza consistencia entre plan/Issue/PR, y separa estos labels del gating de Discovery (`pending-spec`/`spec-ready`).

## Ley

> **Todo Issue y todo PR que participan del flujo Issue-Driven DEBEN cargar exactamente un label `status: <name>` del conjunto canónico (`status: todo`, `status: development`, `status: to review`, `status: review`, `status: to release`, `status: release`, `status: done`), espejando el `status:` del plan correspondiente. Ningún agente DEBE aplicar dos labels `status: *` simultáneamente al mismo Issue o PR. El label `status:*` es ortogonal a los labels de Discovery (`pending-spec`/`spec-ready`) y a los labels de tipo (`feature request ➕`, `user story 🎯`, etc.) — múltiples ejes coexisten en el mismo Issue.**

## Cobertura

- **Aplica a:** todos los Issues abiertos vía templates aprobados (`feature-request`, `user-story-for-api`, `user-story-for-frontend`, `simple-task`, `subtask`) y todos los PRs en repositorios Guardia.
- **Agentes vinculados:** `warrior-eunomia` (aplica `status: todo` en la creación), `warrior-athena` (mueve `todo → development`, `development → to review`, `to review → to release`), `warrior-argos` (mueve `to review ↔ review`), `warrior-janus` (mueve `to release → release → done`), y cualquier agente que cree o modifique Issues/PRs.
- **Excepciones:**
  - **Epic** no recibe `status:*` — se descompone en child Issues, cada una con su propio ciclo. El Epic cierra cuando todos los hijos (`Tracked by`) alcanzan `done`.
  - **Issues generados por Dependabot** o scanners de seguridad siguen flujo propio y quedan exentos.

## Reglas

### 1. Conjunto canónico de 7 labels

| Label | Color sugerido | Cuándo aplicar | Owner |
|---|---|---|---|
| `status: todo` | `#cccccc` (gris claro) | Plan creado, Issue abierto, branch vinculada, worktree listo | `warrior-eunomia` (fallback: agente de la sesión) |
| `status: development` | `#83d2ff` (azul claro) | Implementación en curso (Athena Phase 4) | `warrior-athena` |
| `status: to review` | `#fff3a3` (amarillo claro) | PR abierto, esperando reviewer | `warrior-athena` (entrada); `warrior-argos` (retorno desde `review`) |
| `status: review` | `#fbca04` (amarillo) | Argos o humano revisando activamente | `warrior-argos` |
| `status: to release` | `#ffb178` (naranja claro) | Review aprobado, esperando release iniciar | `warrior-athena` |
| `status: release` | `#e07400` (naranja) | Release en ejecución (tag/build/deploy) | `warrior-janus` |
| `status: done` | `#0e8a16` (verde) | Release concluida, PR mergeado, ciclo cerrado | `warrior-janus` |

La descripción del label en GitHub DEBE contener la semántica resumida del estado para auditoría visual rápida.

### 2. Mutex entre labels `status:*`

En cualquier instante, el Issue o PR DEBE tener **exactamente un** label `status:*`. Cada transición se ejecuta vía:

```bash
gh issue edit {N} --remove-label "status: <previous>" --add-label "status: <next>"
gh pr edit {N}    --remove-label "status: <previous>" --add-label "status: <next>"
```

Aplicar dos labels `status:*` simultáneamente (ej.: `status: to review` + `status: review`) está PROHIBIDO.

### 3. Sincronización con el plan

El label `status:*` en el Issue DEBE espejar el `status:` del front-matter del plan correspondiente en todo instante. El agente que ejecuta la transición (per `lex-agent-planning` "Owners de cada transición") DEBE actualizar simultáneamente:

1. `status:` en el front-matter del plan.
2. Label `status: <name>` en el Issue.
3. Label `status: <name>` en el PR (a partir de `to review`).

Falla en cualquiera de los tres produce drift detectable en el Gate 2 (per `kata-quality-gate`).

### 4. Ortogonalidad con labels de Discovery

Los labels de Discovery (`pending-spec`, `spec-ready`, definidos por plan-038) operan en un eje separado:

- `pending-spec`/`spec-ready` controlan **entrada** al flujo Athena para US-child (User Story child de Epic). Conviven con `status:*` en el mismo Issue.
- US-child creada por Calliope nace con `pending-spec` y **sin** `status:*`. Recibe `status: todo` solamente cuando gana `spec-ready` (transición hecha por el PM correspondiente tras producir la spec).
- Bug y Tech-task saltan el gate de spec y reciben `status: todo` directo en la creación por Eunomia.

### 5. Epic no recibe `status:*`

Epic es descompuesto por Calliope (plan-038) y nunca pasa por Athena directamente. El Epic no tiene ciclo `todo → development → ...` propio; su estado se deriva de `Tracked by` (children con `status:*`). Aplicar `status:*` a un Epic está PROHIBIDO.

### 6. Creación inicial de las labels en el repositorio

Cada repositorio que adopta el flujo DEBE crear los 7 labels vía `gh label create` (script idempotente en `scripts/bootstrap_status_labels.sh` o kata dedicado). La creación manual vía UI de GitHub también es aceptable, siempre que respete nombres, colores y descripciones canónicas.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../quality/lex-hard-gate-pattern.md), el bloque textual de esta Ley se expresa canónicamente como:

```
<HARD-GATE>
warrior-eunomia, warrior-athena, warrior-argos, warrior-janus y cualquier
otro agente MUST NOT aplicar label `status:*` en Issue o PR sin
satisfacer TODOS los criterios:

  (a) Label pertenece al conjunto canónico de 7
      (status: todo | development | to review | review | to release
       | release | done)
  (b) Issue/PR no está en estado terminal (done|abandoned) al recibir
      el nuevo label
  (c) Ningún otro label `status:*` permanece en Issue/PR después de
      la transición (mutex aplicado)
  (d) Plan correspondiente tuvo `status:` actualizado en el mismo paso
  (e) Issue no es Epic (Epic no recibe status:*)

Esta regla aplica a TODO Issue y TODO PR en el flujo Issue-Driven,
independientemente de:
  - tamaño percibido ("es solo un chore")
  - urgencia ("incendio en producción")
  - quién pidió ("el CEO lo solicitó")
  - confianza del equipo ("ya probamos mucho")

Excepción declarada: Epic e Issues generados por Dependabot/scanners
siguen flujo propio. Todo otro tipo de Issue/PR en el flujo
Issue-Driven respeta el mutex.
</HARD-GATE>
```

## Ejemplos

### Correcto

```bash
# Eunomia crea Issue #90 y plan-043 en "todo"
gh issue edit 90 --add-label "status: todo"
# (plan-043 front-matter: status: todo)

# Athena entra en Phase 4
gh issue edit 90 --remove-label "status: todo" --add-label "status: development"
# (plan-043 front-matter: status: development)

# Athena abre PR #91 — aplica label simultáneamente
gh pr create ... && gh pr edit 91 --add-label "status: to review"
gh issue edit 90 --remove-label "status: development" --add-label "status: to review"
# (plan-043 front-matter: status: to review)

# Argos inicia revisión
gh pr edit 91 --remove-label "status: to review" --add-label "status: review"
gh issue edit 90 --remove-label "status: to review" --add-label "status: review"
# (plan-043 front-matter: status: review)
```

### Incorrecto

```bash
# ❌ Dos labels status:* simultáneos
gh issue edit 90 --add-label "status: to review" --add-label "status: review"

# ❌ Label aplicado sin actualizar plan (drift)
gh issue edit 90 --add-label "status: development"
# (plan-043 quedó en status: todo)

# ❌ Aplicar status:* en Epic
gh issue edit 100 --add-label "status: development"
# Issue #100 tiene Issue Type Epic
```

## Validación Automatizada

- **Herramienta:**
  - Script `scripts/bootstrap_status_labels.sh` crea los 7 labels idempotentemente en cualquier repositorio.
  - PR review (humano o Argos) verifica alineación entre `status:` del plan, label del Issue, y label del PR.
  - GitHub Action de verificación periódica (futuro) detecta:
    - Issues/PRs con 0 o ≥2 labels `status:*`
    - Issues con Issue Type Epic cargando `status:*`
    - Drift entre `status:` del plan y label del Issue
- **Momento:** al abrir/actualizar Issue, al abrir/actualizar PR, en cada transición de owner, en el Gate 2 (`kata-quality-gate`).
- **Métrica:** 0 Issues/PRs con label `status:*` divergente del plan correspondiente; 0 Epics con `status:*`; 100% de las transiciones registradas por el owner declarado.

## Referencias

- `lex-agent-planning` — enum unificado de `status:` y tabla de owners
- `lex-issue-quality` — requisitos base de Issues (template, label de tipo, Issue Type, assignee, Why/What/How)
- `lex-issue-first` — todo cambio parte de un Issue
- `lex-pr-quality` — requisitos del PR (label de tamaño, CODEOWNERS, etc.) — complementario
- `lex-hard-gate-pattern` — sintaxis del bloque `<HARD-GATE>`
- `codex-agent-planning` — manual operacional con flujo visual y loop 3×15min
- `codex-labels` — convención general de labels en GitHub
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners de las transiciones
