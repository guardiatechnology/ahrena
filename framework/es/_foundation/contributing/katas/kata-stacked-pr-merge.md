# Kata: Merge Bottom-Up de Stacked PRs

> **Prefix:** `kata-` | **Type:** Skill Repetible | **Scope:** Mergear una cadena de Pull Requests encadenados en el orden correcto (base → tope), actualizando explícitamente el `base` de la próxima capa tras cada merge, usando `gh` + `git` (camino vanilla)

## Objetivo

Esta Kata define el procedimiento para mergear una stack entera respetando la política bottom-up: la capa inferior (`stack-1`) se mergea primero en `main`; en seguida, el PR de la capa 2 tiene su `base` actualizado de `stack-1` a `main` vía `gh pr edit`, la branch se rebasea onto `main` y se hace force-push; el ciclo se repite hasta la última capa. Tras el merge de la última capa (que tiene `Closes #N`), la issue paraguas se cierra automáticamente, y el agente hace cleanup del worktree compartido y de las branches locales.

## Cuándo Usar

- Cuando la capa base (`stack-1`) recibió approval de review y está lista para mergear
- Cuando una capa intermedia está aprobada y la anterior ya fue mergeada
- Cuando todas las capas están aprobadas y el usuario quiere cerrar la stack entera en secuencia

## Entradas

| Entrada | Obligatoria | Descripción |
|---------|:-----------:|-------------|
| Stack activa | Sí | N PRs en GitHub creados por `kata-stacked-pr-create`, en orden `stack-1` → `stack-N` |
| Approval de review | Sí | Al menos la capa base aprobada conforme `lex-pr-quality` (CODEOWNERS) |
| Estrategia de merge | No | `--squash` (default recomendado), `--merge`, o `--rebase` — hereda de la configuración del repo |
| Worktree compartido | Sí | `.worktrees/${N}-${SLUG}-stack/` aún existente |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Verificar pre-requisitos (CI verde, approval, sin conflicto)
- [ ] 2. Mergear capa inferior (1)
- [ ] 3. Para cada capa arriba: actualizar base → rebase → force-push → mergear
- [ ] 4. Confirmar cierre de la issue paraguas
- [ ] 5. Cleanup del worktree y branches locales
- [ ] 6. Verificación final
```

### Paso 1: Verificar pre-requisitos

Para la capa que será mergeada ahora (`current_layer`):

```bash
PR_NUMBER=$(gh pr view "$LAYER_BRANCH" --json number --jq .number)

# ¿CI verde?
gh pr checks "$PR_NUMBER" --repo "$OWNER/$REPO"

# ¿Approval presente?
gh pr view "$PR_NUMBER" --json reviews \
  --jq '[.reviews[] | select(.state=="APPROVED")] | length'

# ¿Sin conflicto declarado por GitHub?
gh pr view "$PR_NUMBER" --json mergeable --jq .mergeable
```

Si algún criterio falla, parar y reportar al usuario. No intentar forzar.

### Paso 2: Mergear capa inferior (1)

La capa 1 tiene `base: main`. Merge directo:

```bash
gh pr merge "$PR_NUMBER" \
  --repo "$OWNER/$REPO" \
  --squash \
  --delete-branch=false
```

| Flag | Razón |
|---|---|
| `--squash` | Default recomendado — produce historia lineal en `main` |
| `--delete-branch=false` | Importante: la branch `feat/${N}-stack-1-${SLUG}` aún es base del PR de la capa 2; eliminarla rompe la referencia |

Tras el merge, actualizar `main` en el worktree:

```bash
git fetch origin main
```

### Paso 3: Para cada capa arriba — actualizar base → rebase → force-push → mergear

Loop para capas `2..N`:

```bash
PREV_PR="$PR_NUMBER"   # PR ya mergeado (capa i-1)
for i in $(seq 2 $N); do
  THIS_BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}"
  THIS_PR=$(gh pr view "$THIS_BRANCH" --json number --jq .number)

  # 3a. Actualizar base del PR a main (GitHub no migra automáticamente)
  gh pr edit "$THIS_PR" --repo "$OWNER/$REPO" --base main

  # 3b. Rebase local de la branch onto main
  git checkout "$THIS_BRANCH"
  git rebase origin/main

  # si conflicto, resolver per kata-stacked-pr-rebase paso 4

  # 3c. Force-push con lease
  git push --force-with-lease origin "$THIS_BRANCH"

  # 3d. Verificar pre-requisitos (CI verde tras force-push, approval)
  gh pr checks "$THIS_PR"
  gh pr view "$THIS_PR" --json reviews \
    --jq '[.reviews[] | select(.state=="APPROVED")] | length'

  # 3e. Mergear (si última capa, eliminar branch tras)
  if [ "$i" -eq "$N" ]; then
    gh pr merge "$THIS_PR" --squash --delete-branch
  else
    gh pr merge "$THIS_PR" --squash --delete-branch=false
  fi

  PREV_PR="$THIS_PR"
  git fetch origin main
done
```

**Puntos críticos:**

- El `gh pr edit --base main` debe correr **antes** del rebase + push. Si la base del PR todavía es `feat/${N}-stack-1-...` (que acaba de mergear), GitHub queda confundido; cambiar primero evita sorpresa.
- El `--delete-branch=false` en capas intermedias preserva la referencia usada por las próximas capas (aun cuando ya tengan su base cambiada, mantener consistencia).
- El `--delete-branch` en la **última capa** dispara cleanup automático en GitHub.

### Paso 4: Confirmar cierre de la issue paraguas

La última capa tiene `Closes #N` en el body. Tras su merge, GitHub cierra la issue.

```bash
gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" --json state --jq .state
# esperado: CLOSED
```

Si todavía está `OPEN`, verificar si la última capa tenía `Closes #N` en el body — si faltó, cerrar manualmente con referencia en el comentario:

```bash
gh issue close "$ISSUE_NUMBER" --comment "Cerrada por #${LAST_PR_NUMBER} (última capa de la stack)."
```

### Paso 5: Cleanup del worktree y branches locales

Tras todas las capas mergeadas:

```bash
# Salir del worktree
cd ../..  # volver al repo raíz

# Eliminar el worktree compartido
git worktree remove ".worktrees/${ISSUE_NUMBER}-${SLUG}-stack" --force

# Eliminar branches locales (todas las capas)
for i in $(seq 1 $N); do
  git branch -D "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" 2>/dev/null || true
done

# Verificar
git worktree list
git branch --list "feat/${ISSUE_NUMBER}-stack-*"
```

`git worktree list` no debe mostrar más el worktree de la stack. `git branch --list` no debe retornar nada.

### Paso 6: Verificación final

- [ ] N PRs mergeados en `main`, en el orden `stack-1` → `stack-N`
- [ ] Para cada PR intermedio (`stack-2` a `stack-N`), el `base` fue explícitamente actualizado a `main` antes del merge
- [ ] Cada capa superior fue rebaseada onto `main` antes del merge (historia lineal preservada)
- [ ] Issue paraguas está `CLOSED` (auto-cerrada por el último `Closes #N` o manualmente)
- [ ] Worktree compartido eliminado
- [ ] Todas las branches locales de la stack eliminadas
- [ ] Plan correspondiente (`plan-NNN-...`) movido a `archived/` si existe

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Stack mergeada | N commits squash en `main` | `main` del repositorio |
| Issue cerrada | GitHub Issue state CLOSED | Repositorio |
| Worktree limpio | Directorio eliminado | Filesystem local |
| Branches eliminadas | Branches locales y remotas removidas | Local + remoto |

## Restricciones

- **Nunca** mergear fuera del orden (capa 3 antes de la capa 2) — rompe la base del PR siguiente y fuerza reconstrucción manual
- **Nunca** eliminar la branch de la capa `i-1` antes de mergear la capa `i` (referencia usada por el PR siguiente)
- **No** cambiar la estrategia de merge entre capas — mantener `--squash` (o lo que el repo estandariza) consistente
- **No** mergear vía UI de GitHub durante la secuencia — usar exclusivamente `gh pr merge` vía CLI para coordinar con los pasos de rebase
- Si un conflicto aparece en el rebase de una capa superior, **parar** e invocar `kata-stacked-pr-rebase` (paso 4) — no intentar resolver dentro de esta kata
- Si la issue paraguas no se cierra automáticamente, **investigar antes de cerrar manualmente** — puede indicar que `Closes #N` falta en el PR errado

## Referencias

- `codex-stacked-prs` — modelo conceptual; ciclo de vida; política bottom-up
- `kata-stacked-pr-create` — creación inicial de la stack
- `kata-stacked-pr-rebase` — cascade rebase cuando hay conflicto
- `lex-pr-quality` — HARD-GATE de 8 criterios atendido por cada PR antes del merge
- `lex-protected-trunk` — `main` recibe código solamente vía merge de PR aprobado
- `lex-issue-first` — `Closes #N` en la última capa cierra la issue
- `lex-git-worktrees` — excepción stack=worktree compartido
