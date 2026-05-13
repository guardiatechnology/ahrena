# Cry: Revisar Pull Request

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para despachar revisión multi-eje en una Pull Request abierta vía `warrior-argos`

## Descripción

Este comando invoca a `warrior-argos` para ejecutar una revisión multi-eje estructurada en una Pull Request abierta: recolecta contexto desde GitHub (PR diff, view, checks, Issue vinculado) y Notion (PRD, Capability Spec) cuando están disponibles; crea worktree aislado; ejecuta los katas de revisión aplicables (Python, frontend, AWS, OpenAPI, CloudEvents, seguridad); ejecuta tests localmente; detecta breaking changes en contratos públicos; y consolida findings en un único review-comment idempotente publicado vía `gh pr review --request-changes` (o `--comment` cuando no hay findings). Nunca `--approve` — la aprobación permanece como decisión humana.

## Uso

```
/cry-review-pr <PR#> [--repo owner/name]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `PR#` | Sí | Número del Pull Request a revisar | `142` |
| `--repo owner/name` | No | Nombre del repositorio; si se omite, infiere desde el `git remote` actual | `--repo guardiatechnology/ahrena` |

## Lo que el Comando Hace

1. Invoca a `warrior-argos` con el número del PR y el repositorio opcional
2. Argos ejecuta las Fases 0 → 4 (Recolección → Worktree → Revisión Multi-Eje → Consolidación → Limpieza)
3. El reviewer recibe un único review-comment consolidado con findings clasificados como 🔴 BLOCKER o 🟡 WARNING
4. Re-ejecutar en el mismo commit edita el review-comment existente (idempotente); re-ejecutar en un commit nuevo crea una review nueva (audit trail preservado)

## Prompt Template

```
Contexto:
- Número del PR: {{PR#}}
- Repositorio: {{repo}} (o inferido desde `git remote`)

Tarea:
Actúe como `warrior-argos`. Ejecute la revisión multi-eje completa del Pull Request conforme el flujo definido por el warrior:
- Fase 0: Recolectar PR, Issue vinculado, PRD/Capability Spec en Notion (cuando estén disponibles), `.ahrena/issues/{N}/` local, y el plan referenciado
- Fase 1: Crear worktree aislado vía `kata-git-worktree`
- Fase 2: Ejecutar katas de revisión aplicables al diff (Python, frontend, AWS, API design, CloudEvents, seguridad) sumados a los ejes B (alineamiento con specs), C (tests locales), D (retrocompatibilidad), F (conformidad Lexis/Codex)
- Fase 3: Consolidar findings en un único review-comment con marker idempotente `<!-- argos-review-id:sha256(pr_number+commit_sha) -->`; publicar vía `gh pr review --request-changes` (≥1 finding) o `--comment` (0 findings); nunca `--approve`
- Fase 4: Remover el worktree

Formato de salida:
- Resumen de las fases (artefactos recolectados, stack detectado, ejes ruteados)
- Body final del review-comment (también publicado en el PR)
```

## Ejemplo de Invocación

**Input:**

```
/cry-review-pr 142
```

**Output esperado:**

```
Argos aquí. Revisando PR #{N} en guardiatechnology/ahrena.

Fase 0 — Recolección: Issue #138 ✅ | PRD en Notion ✅ | .ahrena/issues/138/ ✅
Fase 1 — Worktree: .worktrees/review-pr-142/ creado
Fase 2 — Stack detectado: Python + OpenAPI + CloudEvents + migrations
         Ejes ruteados: A (python, api-design, events), B, C (pytest+mypy), D (oasdiff ✅, squawk ❌), E, F
Fase 3 — Findings: 🔴 2 BLOCKER, 🟡 4 WARNING → publicado como `--request-changes` (review id: a1b2c3d4)
Fase 4 — Worktree removido

URL de la review: https://github.com/guardiatechnology/ahrena/pull/142#pullrequestreview-...
```

## Restricciones

- El Cry dispara solo la revisión; no aprueba, no modifica el código fuente del PR y no publica fix-up commits
- El reviewer que ejecuta el cry DEBE tener `gh` autenticado y los MCP servers configurados (`github`, opcionalmente `notion`) conforme `.ahrena/.directives`
- Una nueva review se crea por nuevo commit head; despachos subsecuentes en el mismo commit editan el review-comment existente
- El Cry no se ejecuta automáticamente en cada PR abierto — requiere despacho humano explícito (el reviewer humano decide qué PR revisar y cuándo)

## Diferencia de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida con número del PR | Orquestación completa multi-paso |
| **Complejidad** | Baja (un comando) | Alta (Argos ejecuta 5 fases y 6 ejes) |
| **¿Configura agente?** | Sí (asume el rol del Warrior Argos) | N/A (Argos es Warrior, no Kata) |
| **Ejemplo** | `/cry-review-pr 142` | Argos invoca `kata-python-review`, `kata-events-review`, etc. |

## Warrior y Katas Asociados

- **warrior-argos** — Revisor multi-eje de Pull Request (orquestador)
- Katas ejecutados por Argos: `kata-mcp-github-read`, `kata-mcp-notion-read`, `kata-git-worktree`, `kata-python-review`, `kata-frontend-review`, `kata-aws-review`, `kata-api-design-review`, `kata-events-review`, `kata-security-review`, `kata-quality-gate`

## Referencias

- `warrior-argos` — Warrior invocado por este Cry
- `lex-issue-first`, `lex-pr-quality`, `lex-issue-driven` — Leyes aplicadas durante la revisión
- `lex-mcp` — Comportamiento MCP cuando GitHub o Notion no están disponibles
- `cry-implement-issue` — Contraparte pre-PR (Gate 2 de `warrior-athena` en el lado del autor)
