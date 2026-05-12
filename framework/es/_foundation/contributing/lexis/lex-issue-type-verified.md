# Lexis: Verificación Programática del Issue Type

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Toda Issue creada en repositorios Guardia que participa del flujo Issue-Driven

## Propósito

`lex-issue-quality` exige que toda Issue tenga un Issue Type definido (`Feature`, `Task`, `Bug`, `Epic`). El campo nativo de Issue Type de GitHub se popula automáticamente cuando la Issue se crea vía template (`.github/ISSUE_TEMPLATE/*.yml` declara `type:`), pero **NO** se popula cuando la Issue se crea vía `gh issue create` sin template. Sin verificación programática post-creación, las Issues creadas vía CLI quedan sin type — lo que desalinea el HARD-GATE de `lex-agent-planning` y rompe la tabla de owners por tipo. Esta Ley codifica la verificación obligatoria.

## Ley

> **Todo agente que crea una Issue (humano o IA, vía UI/CLI/MCP) DEBE verificar programáticamente, inmediatamente tras la creación, que el campo nativo `type` de la Issue está populado con un valor compatible con el template usado (`Feature` para `feature-request` / `user-story-for-api` / `user-story-for-frontend`; `Task` para `simple-task` / `subtask`; `Epic` para `epic`; `Bug` cuando aplicable). Si está vacío, el agente DEBE aplicar el type vía `gh api -X PATCH repos/{owner}/{repo}/issues/{N} -f type={Feature|Task|Bug|Epic}` antes de cualquier transición subsiguiente de la Issue. Aplicar label `status: todo` (per `lex-issue-status` Eje A) en una Issue sin `type` populado está PROHIBIDO.**

## Alcance

- **Aplica a:** todas las Issues creadas en repositorios Guardia, independiente del mecanismo (UI de GitHub, `gh issue create`, MCP `create_issue`, script automatizado).
- **Agentes vinculados:** `warrior-eunomia` (modo top-level y subtask), `warrior-athena` (cuando delega creación de child Issue), `warrior-calliope` (decomposición de Epic), y cualquier agente que invoque `kata-plan-task`, `kata-create-subtasks` o `kata-contributing-issue`.
- **Excepciones:** Issues generadas por Dependabot o scanners de seguridad siguen flujo propio y quedan exentas.

## Rules

### 1. Verificación post-creación obligatoria

Inmediatamente tras crear la Issue, el agente **DEBE**:

```bash
gh api repos/{owner}/{repo}/issues/{N} --jq '.type.name // empty'
```

- Si retorna un valor (`Feature`, `Task`, `Bug`, `Epic`) → sigue con la verificación de compatibilidad (Regla 2).
- Si retorna vacío → aplicar manualmente (Regla 3).

### 2. Compatibilidad template ↔ type

| Template | Issue Type aceptado |
|---|---|
| `feature-request` | `Feature` |
| `epic` | `Epic` |
| `user-story-for-api` | `Feature` |
| `user-story-for-frontend` | `Feature` |
| `simple-task` | `Task` |
| `subtask` | `Task` |

Si el type retornado es incompatible con el template, **abortar y alertar al usuario** — no intentar reescribir silenciosamente (puede enmascarar error de creación).

### 3. Aplicación manual cuando ausente

Si la verificación retorna vacío:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{N} -f type={Feature|Task|Bug|Epic}
```

Luego re-verificar (Regla 1) para confirmar persistencia.

### 4. Precondición para transiciones

Aplicar label `status: todo` (entrada en el Eje A de `lex-issue-status`) **SIEMPRE** ocurre **TRAS** el type estar populado y verificado. El HARD-GATE de `lex-agent-planning` precondición (b) lo exige explícitamente.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../quality/lex-hard-gate-pattern.md):

```
<HARD-GATE>
warrior-eunomia, warrior-athena, warrior-calliope y cualquier agente que
crea Issue MUST NOT aplicar label `status: todo` (entrada en el Eje A de
lex-issue-status) sin satisfacer TODOS los criterios:

  (a) `gh api repos/{owner}/{repo}/issues/{N} --jq '.type.name'` retorna
      valor no-vacío
  (b) Valor retornado es uno de: Feature | Task | Bug | Epic
  (c) Valor es compatible con el template usado per Regla 2 de esta Lex

Esta regla aplica a TODA Issue en el flujo Issue-Driven, independiente de:
  - tamaño percibido ("es solo un chore")
  - urgencia ("incendio en producción")
  - quién pidió ("el CEO solicitó")
  - confianza del equipo ("ya testamos mucho")

Excepción declarada: Issues generadas por Dependabot o scanners de seguridad
siguen flujo propio. Toda otra Issue en el flujo respeta el gate.
</HARD-GATE>
```

## Ejemplos

### Correcto

```bash
# 1. Eunomia crea Issue vía gh CLI (sin template)
gh issue create --title "chore: ..." --body "..." --label "evolvability ♻️"
# → Issue #105 creada

# 2. Verificación post-creación
TYPE=$(gh api repos/guardiatechnology/ahrena/issues/105 --jq '.type.name // empty')

# 3. Type vacío (CLI no aplica) — aplicar manualmente
[ -z "$TYPE" ] && gh api -X PATCH repos/guardiatechnology/ahrena/issues/105 -f type=Task

# 4. Re-verificar
gh api repos/guardiatechnology/ahrena/issues/105 --jq '.type.name'
# → "Task" ✓

# 5. Ahora puede aplicar status: todo per lex-issue-status Eje A
gh issue edit 105 --add-label "status: todo"
```

### Incorrecto

```bash
# ❌ Saltar verificación tras gh issue create
gh issue create --title "feat: ..." --label "feature request ➕"
gh issue edit 106 --add-label "status: todo"
# Issue #106 queda sin type — viola HARD-GATE precondición (b) de lex-agent-planning

# ❌ Aplicar type incompatible con template
# Issue creada vía template feature-request pero con `type=Task` manual
# Compatibilidad rota — viola Regla 2
```

## Validación Automatizada

- **Herramienta:** `kata-contributing-issue` aplica esta verificación en el Paso final; `kata-plan-task` invoca la verificación en el Paso 3 del HARD-GATE de Eunomia; revisión de PR confirma alineación.
- **Momento:** inmediatamente tras `gh issue create` / MCP `create_issue` / UI submit; antes de cualquier label `status:*` ser aplicada.
- **Métrica:** 0 Issues en el flujo Issue-Driven sin `type` populado; 100% de Issues con type compatible con el template usado.

## Referencias

- `lex-issue-quality` — exige Issue Type entre los requisitos base
- `lex-agent-planning` — HARD-GATE precondición (b) cita esta Lex
- `lex-issue-status` — Eje A (status: todo) requiere type populado
- `lex-issue-first` — Issue como punto de origen; type es parte de la calidad de la Issue
- `kata-plan-task`, `kata-create-subtasks`, `kata-contributing-issue` — invocan esta verificación
- `warrior-eunomia` — owner que dispara la verificación en la creación del plan
- Issue Types nativos de GitHub: https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization
