# Kata: Planificar una Tarea

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación y mantenimiento de planes de tarea por agentes, conforme a `lex-agent-planning` (modelo de 3 capas — ADR-002)

## Objetivo

Crear el plan canónico de una tarea antes de la ejecución, garantizando que el objetivo, alcance, etapas y dependencias estén en el **body de la Issue de GitHub** (canonical per ADR-002) y confirmados por el usuario antes de que comience cualquier acción irreversible. Este es el procedimiento que **`warrior-eunomia` ejecuta en modo top-level** (per plan-046 / absorción de plan-044) y que el agente de la sesión sigue como fallback mientras Eunomia no esté disponible.

Per `lex-agent-planning` HARD-GATE, la label `status: todo` solo puede aplicarse a la Issue cuando los 5 pasos canónicos se hayan completado: (1) Issue abierta per `lex-issue-quality`; (2) Issue Type verificado per `lex-issue-type-verified`; (3) branch remota creada vía `gh issue develop` y vinculada a la Issue; (4) worktree creado per `lex-git-worktrees`; (5) **body de la Issue rellenado con el plan canónico** (Summary + Plan section).

## Cuándo Usar

- Al inicio de cualquier tarea multi-etapa.
- Antes de invocar warriors, katas en secuencia, o cries.
- Antes de modificar múltiples archivos en una única sesión.
- Cuando el usuario pide "haz X" y X tiene más de una etapa discernible.

## Inputs

| Entrada | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| Descripción de la tarea | Sí | Lo que el agente necesita hacer (puede ser vaga — el kata clarifica) |
| Repo (`owner/repo`) | No | Default: repo actual del worktree |
| Template de Issue | No | `feature-request` (default), `tech-task`, `user-story-for-api`, `user-story-for-frontend` |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Esbozar el plan con el usuario
- [ ] 2. Abrir Issue con body canónico (Summary + Plan)
- [ ] 3. Verificar Issue Type
- [ ] 4. Crear branch vía `gh issue develop`
- [ ] 5. Crear worktree
- [ ] 6. Materializar caché local vía kata-load-plan-from-issue
- [ ] 7. Aplicar label `status: todo` y confirmar al usuario
```

### Paso 1: Esbozar el plan con el usuario

Con base en la descripción de la tarea:

1. Identificar el **Objective** (por qué existe esta tarea — 1-3 frases).
2. Descomponer en **Steps** atómicos y verificables.
3. Identificar **Dependencies** (otros planes, Issues, decisiones pendientes; "None" si no hay).
4. Listar **Risks** conocidos (mitigaciones; "None identified" si no hay).
5. Listar **Open Questions** (decisiones pendientes que afectan la ejecución; "None" si no hay).

Presentar el borrador con:

> "Este es el plan para la tarea. ¿Quieres ajustar algo antes de que abra la Issue?"

Esperar respuesta. Incorporar ajustes. **No abrir Issue antes de la confirmación.**

### Paso 2: Abrir Issue con body canónico (Summary + Plan)

Construir el body conforme al schema de `lex-agent-planning`:

```markdown
## Summary

{2-4 frases describiendo el objetivo. Suele heredarse del template.}

## Plan

### Objective
{Objective del borrador — 1-3 frases.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{Lista o "None".}

### Risks
{Lista o "None identified".}

### Open Questions
{Lista o "None".}
```

Abrir la Issue (preferir MCP `create_issue` per `lex-mcp` regla 1, fallback `gh issue create`):

```bash
# MCP preferido
mcp.github.create_issue(
    owner=owner, repo=repo,
    title="{type}: {summary}",
    body=body_content,
    labels=["feature request ➕"],  # o label del template aplicable
    assignees=["@me"],
)

# Fallback CLI
gh issue create \
  --title "{type}: {summary}" \
  --body-file /tmp/plan-body.md \
  --label "feature request ➕" \
  --assignee "@me"
```

Capturar el número `{N}` retornado.

### Paso 3: Verificar Issue Type

Per `lex-issue-type-verified`, comprobar que el tipo nativo fue aplicado por el template:

```bash
gh api repos/{owner}/{repo}/issues/{N} --jq '.type.name'
```

Si está vacío (creación vía CLI sin template), aplicar manualmente:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{N} -f type={Feature|Task|Bug|Epic}
```

### Paso 4: Crear branch vía `gh issue develop`

```bash
gh issue develop {N} --base main --name {type}/{N}-{slug}
```

`{slug}` es la versión kebab-case del summary (máx. 50 chars). Ese comando registra la branch como "Development" en la sidebar de GitHub, satisfaciendo HARD-GATE precondition (c).

### Paso 5: Crear worktree

Per `lex-git-worktrees`:

```bash
git fetch origin {type}/{N}-{slug}
git worktree add .worktrees/{N}-{slug} {type}/{N}-{slug}
```

### Paso 6: Materializar caché local vía kata-load-plan-from-issue

Correr `kata-load-plan-from-issue` pasando `{N}` — materializa `.plans/{N}.md` espejando el body recién grabado. Esto garantiza que las ediciones posteriores de la IA tengan un caché local de referencia (rellena los bloques `<!-- not-flushed -->` con working notes durante la ejecución).

### Paso 7: Aplicar label `status: todo` y confirmar al usuario

```bash
gh issue edit {N} --add-label "status: todo"
```

Confirmar al usuario:

> "Plan registrado en #{N} (body canónico). Branch `{type}/{N}-{slug}` y worktree `.worktrees/{N}-{slug}/` listos. Caché local en `.plans/{N}.md`. Status: todo. ¿Puedo iniciar?"

Esperar OK del usuario antes de cualquier ejecución irreversible posterior.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Body canónico de la Issue | Markdown (Summary + Plan section) | GitHub Issue `{N}` |
| Branch remota | git ref | `origin/{type}/{N}-{slug}` |
| Worktree | git worktree | `.worktrees/{N}-{slug}/` |
| Caché local | Markdown | `.plans/{N}.md` (gitignored) |
| Label | GitHub label | `status: todo` en la Issue |

## Ejemplo de Ejecución

### Input

```
Tarea: migrar almacenamiento del plan al modelo Issue-as-plan
(3-layer: Issue body + .plans/ caché + .ahrena/issues/ artifacts)
```

### Paso 2 — Body grabado en la Issue #96

```markdown
## Summary

**As** an Ahrena framework contributor,
**I want** to migrate plan storage to a 3-layer model,
**So that** plans live where they belong (audit in GitHub Issue,
scratch in .plans/ cache, Phase artifacts in .ahrena/issues/).

## Plan

### Objective
Refactorizar la capa de almacenamiento del plan para que viva en tres
capas con roles claros: Issue body (canonical) + .plans/{N}.md
(working memory de la IA, gitignored) + .ahrena/issues/{N}/ (committed Phase
artifacts).

### Steps
- [ ] Step 1 — Open Issue + branch + worktree (HARD-GATE)
- [ ] Step 2 — ADR-002
- [ ] Step 3 — Rewrite lex-agent-planning (3 langs)
- [ ] Step 3.5 — Split lex-issue-status (3 langs)
...

### Dependencies
plan-043 (PR #93) merged.

### Risks
- .plans/ perdida en fresh clone — mitigado por kata-load-plan-from-issue.
- Flush conflictivo entre sesiones — preflight detecta drift.
...

### Open Questions
Todas resueltas el 2026-05-11 (ver draft).
```

### Paso 4 — Branch creada

```
$ gh issue develop 96 --base main --name feat/96-issue-as-plan-and-issues-folder
github.com/guardiatechnology/ahrena/tree/feat/96-issue-as-plan-and-issues-folder
```

### Paso 7 — Confirmación al usuario

```
Agente: "Plan registrado en #96 (body canónico).
  Branch feat/96-issue-as-plan-and-issues-folder y worktree
  .worktrees/96-issue-as-plan-and-issues-folder/ listos.
  Caché local en .plans/96.md.
  Status: todo. ¿Puedo iniciar?"
```

## Restricciones

- **Nunca aplicar `status: todo` antes del Paso 7** — HARD-GATE de `lex-agent-planning` exige los 5 pasos canónicos completados.
- **Nunca crear archivo `.claude/plans/*.md` como canónico** — modelo legado pre-ADR-002. El body de la Issue es canonical; `.plans/{N}.md` es caché regenerable.
- **Nunca saltar el user OK en el Paso 7** — la ejecución irreversible posterior exige confirmación explícita.
- **Nunca omitir Summary o secciones del Plan** — body sin Summary, Steps, Risks, Dependencies, Open Questions no satisface HARD-GATE precondition (e).
- **Preferir MCP > CLI** — per `lex-mcp` regla 1.

## Referencias

- `lex-agent-planning` — Ley (modelo de 3 capas)
- `lex-issue-status` — labels canónicas (`status: todo` aplicada en el Paso 7)
- `lex-issue-quality` — requisitos del body de la Issue
- `lex-issue-type-verified` — verificación del Issue Type
- `lex-issue-first`, `lex-git-branches`, `lex-git-worktrees` — preconditions
- `lex-mcp` — preferencia MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- ADR-002 — modelo de almacenamiento en 3 capas
- `kata-load-plan-from-issue` — Paso 6 (materializa caché local)
- `kata-flush-plan-to-issue` — usado en transiciones posteriores (no en este kata)
- `kata-create-subtasks` — modo subtask de Eunomia (descomposición de child Issue)
- `warrior-eunomia` — owner top-level de este kata
