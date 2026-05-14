# Kata: Planificar una Tarea

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de una sub-issue Plan vinculada a una Issue parent, conforme a `lex-agent-planning` (modelo jerárquico Issue → Plan → PR)

## Objetivo

Crear una sub-issue Plan (Issue Type Task) vinculada a una Issue parent existente, con body canónico (Summary + Plan section), label `status: todo` aplicada e Issue Type verificado. Este es el procedimiento que `warrior-eunomia` ejecuta en modo top-level (Plan independiente vinculado a una Issue existente) y que el agente de la sesión sigue como fallback mientras Eunomia no esté shipada.

Per el HARD-GATE de Gate 1 de `lex-agent-planning`, la label `status: todo` solo puede aplicarse a la sub-issue Plan cuando los 4 pasos canónicos se hayan completado: (1) Issue parent abierta y conforme a `lex-issue-first` y `lex-issue-quality`; (2) sub-issue Plan creada vía MCP `create_issue` (preferido) o `gh issue create --type Task` (fallback), vinculada a la Issue parent, con template Plan y labels obligatorias; (3) body rellenado con el plan canónico (Summary + Plan); (4) Issue Type verificado como `Task` per `lex-issue-type-verified`.

Branch, worktree y assignee **NO** son preconditions de este kata. Pertenecen a `todo → development` (Athena, codificado en Gate 2 de `lex-agent-planning`).

## Cuándo Usar

- Cuando el usuario pide registrar un Plan independiente vinculado a una Issue parent existente.
- Cuando `kata-decompose-issue-into-plans` necesita crear cada sub-issue Plan de la descomposición (una invocación por Plan).
- Al inicio de cualquier tarea multi-etapa cuyo plan aún no esté materializado como sub-issue en GitHub.
- Antes de invocar `kata-load-plan-from-subissue` (el kata de load rechaza si la sub-issue no existe).

## Inputs

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| `parent_issue_number` | Sí | Número `{N}` de la Issue parent (User Story, Bug o Tech Task) donde el Plan se conecta |
| `plan_summary` | Sí | Resumen ejecutable del Plan (2-4 frases). Típicamente una porción del alcance de la Issue parent |
| `plan_objective` | Sí | Por qué esta unidad existe y qué entrega al final (1-3 frases) |
| `plan_steps` | Sí | Lista de Steps atómicos y verificables (mínimo 1) |
| `plan_dependencies` | No | Otros Plans, Issues o PRs de los que esta tarea depende. Default: `"None"` |
| `plan_risks` | No | Riesgos conocidos y mitigaciones. Default: `"None identified"` |
| `plan_open_questions` | No | Preguntas pendientes que requieren decisión. Default: `"None"` |
| `owner/repo` | No | Repo donde vive la Issue parent. Default: repo actual del worktree |

## Workflow

```
Progreso:
- [ ] 1. Confirmar que la Issue parent existe y está bien formada
- [ ] 2. Bosquejar el Plan con el usuario y confirmar
- [ ] 3. Crear la sub-issue Plan (Task) vinculada a la Issue parent
- [ ] 4. Rellenar el body de la sub-issue con el plan canónico
- [ ] 5. Verificar el Issue Type post-creación
- [ ] 6. Aplicar la label `status: todo` y confirmar al usuario
```

### Paso 1: Confirmar que la Issue parent existe y está bien formada

Antes de crear la sub-issue Plan, verificar que la Issue parent `{N}` existe y satisface `lex-issue-first` y `lex-issue-quality`:

```bash
# Preferido — vía MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)

# Fallback — vía gh
gh issue view {N} --repo {owner}/{repo} --json number,title,state,labels,body,assignees
```

Verificar:

- Issue parent existe y está abierta (state `open`).
- Body contiene Why/What/How rellenados (per `lex-issue-quality`).
- Labels obligatorias del template están presentes.
- Issue Type compatible (`Feature` para User Story; `Bug` para bug; `Task` para Tech Task).

Si algún criterio falla, **abortar** con mensaje orientando a invocar `kata-contributing-issue` para abrir o corregir la Issue parent primero.

### Paso 2: Bosquejar el Plan con el usuario y confirmar

A partir de los inputs (`plan_summary`, `plan_objective`, `plan_steps`, `plan_dependencies`, `plan_risks`, `plan_open_questions`), armar el body candidato (per schema de la sección *Schema del body de la sub-issue Plan* en `lex-agent-planning`):

```markdown
## Summary

{plan_summary — 2-4 frases}

Parent: #{N}

## Plan

### Objective
{plan_objective — 1-3 frases}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{plan_dependencies o "None"}

### Risks
{plan_risks o "None identified"}

### Open Questions
{plan_open_questions o "None"}
```

Presentar el bosquejo al usuario:

> "Este es el Plan vinculado a la #{N}. ¿Desea ajustar algo antes de abrir la sub-issue?"

Esperar confirmación. Incorporar ajustes. **No crear la sub-issue antes de la confirmación.**

### Paso 3: Crear la sub-issue Plan (Task) vinculada a la Issue parent

Preferir MCP `create_issue` per regla 1 de `lex-mcp`:

```python
# Preferido — vía MCP
result = mcp.github.create_issue(
    owner=owner,
    repo=repo,
    title="plan: {short title derivado de plan_summary}",
    body=body_content,
    labels=["plan 📋"] + parent_labels_mirror,
    type="Task",
)
M = result["number"]
M_db_id = result["id"]  # node ID requerido para sub-issue link
```

Fallback CLI per regla 4 de `lex-mcp`:

```bash
# Fallback CLI — capturar number e ID del database atómicamente desde la respuesta de create
result=$(gh issue create \
  --repo {owner}/{repo} \
  --title "plan: {short title}" \
  --body-file /tmp/plan-{M}-body.md \
  --label "plan 📋" \
  --label "{mirror parent labels}" \
  --json number,id)

M=$(echo "$result" | jq -r .number)
M_db_id=$(echo "$result" | jq -r .id)
```

Vincular la sub-issue como sub-issue de la Issue parent:

```bash
gh api -X POST repos/{owner}/{repo}/issues/{N}/sub_issues -F sub_issue_id={M_db_id}
```

Capturar `{M}` (número de la sub-issue Plan) para los siguientes pasos.

### Paso 4: Rellenar el body de la sub-issue con el plan canónico

Si el body ya fue grabado en el Paso 3 vía MCP `create_issue` con `body=body_content`, este paso es confirmatorio. Si el template Plan por defecto fue aplicado por GitHub (en lugar del body candidato), grabar vía update:

```python
# Preferido — vía MCP
mcp.github.update_issue(
    owner=owner, repo=repo, issue_number=M,
    body=body_content,
)

# Fallback CLI
gh issue edit {M} --repo {owner}/{repo} --body-file /tmp/plan-{M}-body.md
```

Validar que el body grabado contiene las 5 secciones canónicas: Summary, Plan → Objective, Steps, Risks, Dependencies, Open Questions.

### Paso 5: Verificar el Issue Type post-creación

Per `lex-issue-type-verified`, confirmar que el tipo nativo es `Task`:

```bash
gh api repos/{owner}/{repo}/issues/{M} --jq '.type.name'
```

Si está vacío o es diferente de `Task`, aplicar manualmente:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{M} -f type=Task
```

### Paso 6: Aplicar la label `status: todo` y confirmar al usuario

```bash
gh issue edit {M} --repo {owner}/{repo} --add-label "status: todo"
```

Confirmar al usuario:

> "Plan registrado en #{M} (sub-issue de #{N}). Body canónico, label `status: todo` aplicada, Issue Type `Task` verificado. Listo para `todo → development` cuando se decida iniciar la ejecución."

Branch, worktree y assignee **no** se aplican en este kata — pertenecen a `todo → development`, owned por Athena.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Sub-issue Plan | GitHub Issue (Task) | `{owner}/{repo}#{M}`, sub-issue de `#{N}` |
| Body canónico | Markdown (Summary + Plan section) | Body de la sub-issue `{M}` |
| Label `status: todo` | GitHub label | Sub-issue `{M}` |
| Issue Type `Task` | GitHub Issue Type | Sub-issue `{M}` |
| URL de la sub-issue | Link | Presentado al usuario |

## Ejemplo de Ejecución

### Input de Ejemplo

```
parent_issue_number: 200
plan_summary: "Refactorizar el agregado Ledger a event sourcing, separando
  comandos (write-side) de lecturas (read-side projection)."
plan_objective: "Entregar la primera porción ejecutable de la User Story
  #200: Ledger reescrito como aggregate event-sourced, con factory + repository."
plan_steps:
  - "Step 1 — Modelar LedgerEvent base class"
  - "Step 2 — Reescribir Ledger.apply() como event projection"
  - "Step 3 — Repository persistiendo events en lugar de state"
  - "Step 4 — Migration helper para legacy state → events"
  - "Step 5 — Tests de aggregate"
plan_dependencies: "None"
plan_risks: "- migration helper puede fallar en datasets con inconsistencia
  histórica — mitigado por dry-run + checksum."
plan_open_questions: "None"
```

### Sub-issue Plan #201 creada

```markdown
## Summary

Refactorizar el agregado Ledger a event sourcing, separando comandos
(write-side) de lecturas (read-side projection).

Parent: #200

## Plan

### Objective
Entregar la primera porción ejecutable de la User Story #200: Ledger
reescrito como aggregate event-sourced, con factory + repository.

### Steps
- [ ] Step 1 — Modelar LedgerEvent base class
- [ ] Step 2 — Reescribir Ledger.apply() como event projection
- [ ] Step 3 — Repository persistiendo events en lugar de state
- [ ] Step 4 — Migration helper para legacy state → events
- [ ] Step 5 — Tests de aggregate

### Dependencies
None

### Risks
- migration helper puede fallar en datasets con inconsistencia
  histórica — mitigado por dry-run + checksum.

### Open Questions
None
```

### Confirmación al usuario

```
Agente: "Plan registrado en #201 (sub-issue de #200).
  Body canónico, label `status: todo` aplicada, Issue Type `Task` verificado.
  Listo para `todo → development` cuando se decida iniciar la ejecución."
```

## Restricciones

- **Nunca aplicar `status: todo` antes del Paso 6** — el HARD-GATE de Gate 1 en `lex-agent-planning` exige los 4 pasos canónicos completados.
- **Nunca crear la sub-issue Plan sin Issue parent confirmada** — sin Issue parent abierta y conforme, no hay Plan que crear; invocar `kata-contributing-issue` antes.
- **Nunca crear branch, worktree ni aplicar assignee en este kata** — pertenecen a `todo → development` (Athena, Gate 2 de `lex-agent-planning`).
- **Nunca crear archivo en `.claude/plans/` o `.cursor/plans/` en este kata** — el cache local se materializa por `kata-load-plan-from-subissue` en un momento posterior, y el kata de load rechaza si la sub-issue no existe.
- **Nunca omitir Summary, Parent ni secciones del Plan en el body** — un body sin Summary, Objective, Steps, Risks, Dependencies, Open Questions no satisface la precondition (c) de Gate 1.
- **Preferir MCP > CLI** — per regla 1 de `lex-mcp`; CLI `gh issue create` es fallback per regla 4.

## Referencias

- `lex-agent-planning` — Ley (modelo jerárquico Issue → Plan → PR; Gate 1 owned por Eunomia)
- `lex-issue-status` — labels canónicas; `status: todo` aplicado en el Paso 6
- `lex-issue-quality` — requisitos del body de la Issue parent
- `lex-issue-type-verified` — verificación programática del Issue Type
- `lex-issue-first` — Issue parent precede a la sub-issue Plan
- `lex-mcp` — preferencia MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- `kata-contributing-issue` — creación de la Issue parent (precondition)
- `kata-decompose-issue-into-plans` — descompone la Issue parent en N sub-issues Plan; invoca este kata por Plan
- `kata-load-plan-from-subissue` — materializa el cache local después de que la sub-issue Plan exista
- `kata-flush-plan-to-subissue` — usado en transiciones posteriores (no en este kata)
- `warrior-eunomia` — owner top-level de este kata
