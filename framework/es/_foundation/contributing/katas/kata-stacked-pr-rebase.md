# Kata: Cascade Rebase en Stacked PRs

> **Prefix:** `kata-` | **Type:** Skill Repetible | **Scope:** Propagar cambios hechos en una capa inferior de la stack hacia todas las capas superiores, usando `git rebase` + `git push --force-with-lease` (camino vanilla)

## Objetivo

Esta Kata define el procedimiento manual para resolver la situación en que una capa de la stack recibe nuevo cambio (commit adicional, amend, o squash vía review) y las capas arriba de ella deben rebasearse para incorporar ese cambio. El agente trabaja de abajo hacia arriba dentro del worktree compartido, siempre con `--force-with-lease` para evitar sobrescribir commits de otros revisores.

## Cuándo Usar

- Cuando review pidió ajuste en una capa ya enviada (ej.: amend en la capa 1)
- Cuando `main` avanzó y la capa 1 debe rebasearse (`git rebase main`)
- Cuando una capa superior debe absorber cambios de una capa inferior antes de volverse mergeable
- Cuando squash merge de PR upstream creó divergencia (requiere `git rebase --onto`)

## Entradas

| Entrada | Obligatoria | Descripción |
|---------|:-----------:|-------------|
| Worktree de la stack activo | Sí | `.worktrees/${N}-${SLUG}-stack/` existente, creado por `kata-stacked-pr-create` |
| Capa modificada | Sí | Identificador de la capa donde el cambio ocurrió (ej.: `stack-1-schema`) |
| Capas superiores | Sí | Lista de las branches que necesitan rebase (`stack-2-...`, `stack-3-...`) |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Identificar capa modificada y cadena arriba
- [ ] 2. Push de la capa modificada con --force-with-lease
- [ ] 3. Para cada capa superior: rebase + push
- [ ] 4. Resolver conflictos cuando ocurran
- [ ] 5. Verificación final
```

### Paso 1: Identificar capa modificada y cadena arriba

1. Entrar en el worktree compartido:
   ```bash
   cd .worktrees/${ISSUE_NUMBER}-${SLUG}-stack
   ```
2. Listar todas las branches de la stack en orden (base → tope):
   ```bash
   git branch --list "feat/${ISSUE_NUMBER}-stack-*-${SLUG}" | sort
   ```
3. Identificar la capa modificada y las capas arriba de ella. Ej.: si la capa 2 cambió, capas 3..N necesitan rebase.

### Paso 2: Push de la capa modificada con `--force-with-lease`

La capa modificada ya está commiteada localmente (amend, nuevo commit, o rebase contra `main`). Push con lease:

```bash
git checkout "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"
git push --force-with-lease origin "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"
```

**Nunca usar `--force` ciego.** El `--force-with-lease` rechaza el push si otro revisor commiteó encima desde el último fetch — protege contra sobrescribir trabajo ajeno.

### Paso 3: Para cada capa superior — rebase + push

Loop ascendente, de la capa `MODIFIED_LAYER + 1` hasta `N`:

```bash
for i in $(seq $((MODIFIED_LAYER + 1)) $N); do
  PREV="feat/${ISSUE_NUMBER}-stack-$((i-1))-${PREV_SLUG}"
  THIS="feat/${ISSUE_NUMBER}-stack-${i}-${THIS_SLUG}"

  git checkout "$THIS"
  git rebase "$PREV"

  # si hay conflicto, ver Paso 4 antes de continuar

  git push --force-with-lease origin "$THIS"
done
```

Cada iteración:
1. Checkout de la capa superior
2. `git rebase {capa anterior}` — replay de los commits únicos de la capa superior encima de la capa anterior actualizada
3. `git push --force-with-lease`

### Paso 4: Resolver conflictos

Cuando `git rebase` se detiene con conflicto:

1. **Identificar archivos en conflicto:**
   ```bash
   git status
   ```
2. **Resolver manualmente** los marcadores `<<<<<<<` / `=======` / `>>>>>>>`. La elección de resolución depende del contexto — si hay incertidumbre, parar y consultar al usuario.
3. **Marcar resuelto y continuar:**
   ```bash
   git add <archivos-resueltos>
   git rebase --continue
   ```
4. **Abortar cuando irrecuperable** (raro):
   ```bash
   git rebase --abort
   ```
   Vuelve al estado pre-rebase. Investigar e intentar de nuevo, posiblemente con descomposición diferente.

**Caso especial — squash merge upstream creó divergencia:**

Si la capa anterior fue mergeada con squash en `main`, los commits originales desaparecieron y el rebase común genera "artificial conflicts". Usar `--onto`:

```bash
# En vez de:
# git rebase feat/${N}-stack-1-${SLUG}
# Hacer:
git rebase --onto main "feat/${N}-stack-1-${SLUG}" "feat/${N}-stack-2-${SLUG}"
```

`--onto` reaplica solamente los commits únicos de la capa 2 (excluyendo los de la capa 1 ya squashed) encima de `main`.

### Paso 5: Verificación final

- [ ] La capa modificada fue empujada con `--force-with-lease` (y no `--force`)
- [ ] Todas las capas superiores fueron rebaseadas en orden ascendente
- [ ] Todos los pushes succedieron (ninguno rechazado por divergencia inesperada)
- [ ] `git log --oneline {tope} ^main` muestra la historia lineal esperada
- [ ] Conflictos resueltos preservaron intención de las dos capas (no descartar cambios por error)
- [ ] Comentar en los PRs de GitHub si el cambio es significativo para que revisores recontextualicen

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Branches superiores rebaseadas | Historia git lineal | Repositorio remoto |
| PRs actualizados | GitHub PRs | Auto-actualizados vía push (mismo `head` ref) |

## Restricciones

- **Nunca** usar `--force` ciego — siempre `--force-with-lease`
- **Nunca** rebasear `main` en el flujo de cascade — solo rebaseamos branches de la stack
- **No** rebasear en orden errado (de arriba hacia abajo) — puede reintroducir cambios ya obsoletos
- Si conflicto es grande o ambiguo, **parar** y consultar al usuario en vez de adivinar
- Si la stack queda inconsistente (rebase falló en el medio), **no esconder el estado** — listar branches restantes al usuario y proponer `git rebase --abort` o continuación manual
- Hooks pre-push pesados (linters, tests) pueden volver el cascade muy lento; en casos extremos, considerar `--no-verify` **con autorización explícita del usuario** y justificación registrada

## Variant: git-spice

Aplicable cuando `.ahrena/.directives` declara `stacked_prs.tool: gs`. La gran ventaja del camino gs en este kata es el **auto-restack**: alterar una capa inferior (commit nuevo, amend o rebase contra trunk) reaplica automáticamente los commits de las capas superiores sobre la nueva base. El agente raramente necesita un loop manual; ante conflicto, `gs rebase continue` sustituye `git rebase --continue`. Consultar `codex-git-spice` para el mapeo completo.

### Caso 1: amend o commit nuevo en una capa ya submitida

Estando dentro del worktree compartido y en la capa modificada:

```bash
git-spice branch checkout "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"

# (a) Commit adicional en la misma capa
git add <archivos>
git-spice commit create -m "fix(scope): ajuste pedido en review"
# → gs reaplica las capas i+1..N sobre el nuevo commit

# (b) Amend del último commit de la capa
git add <archivos>
git-spice commit amend --no-edit
# → ídem; auto-restack ocurre tras el amend

# Submitir el stack para reflejar en los PRs (idempotente)
git-spice stack submit
# o solo las capas afectadas:
git-spice upstack submit
```

`gs commit create` y `gs commit amend` llaman a `git commit` por debajo (firma GPG preservada cuando `commit.gpgsign=true` está global) y luego disparan `gs upstack restack` para todas las capas superiores.

### Caso 2: trunk (`main`) avanzó y la capa base requiere rebase

```bash
# Estando en cualquier capa del worktree compartido
git-spice repo sync --restack
# Pull del trunk + elimina branches ya mergeadas localmente +
# rebasea el stack actual contra el trunk actualizado
```

Equivalente al loop vanilla `git fetch && git rebase origin/main && cascade rebase manual`, en un único comando.

### Caso 3: squash merge upstream creó divergencia

Si la capa anterior fue mergeada con squash (en el trunk) y el historial unsquashed desapareció:

```bash
git-spice repo sync --restack
# Cubre la mayoría de los casos: gs detecta el squash y ajusta la base.
```

Si aún queda inconsistencia (raro):

```bash
# Mueve la capa superior directamente sobre main
git-spice upstack onto main
# o sobre otra base explícita
git-spice upstack onto "feat/${ISSUE_NUMBER}-stack-3-${LAYER_SLUG}"
```

### Caso 4: conflicto durante el auto-restack

`gs` se detiene con un mensaje similar a `git rebase` en conflicto. Resolución:

```bash
git status
# resolver marcadores <<<<<<< / >>>>>>> manualmente
git add <archivos-resueltos>
git-spice rebase continue
# o para abortar:
git-spice rebase abort
```

`gs rebase continue` retoma el auto-restack desde donde se detuvo — incluidas las capas superiores aún no tocadas. No use `git rebase --continue` directo; puede desincronizar la metadata de gs en cascadas multi-capa.

### Caso 5: push tras los cambios

`gs` aplica `--force-with-lease` automáticamente en `branch submit` y `stack submit`:

```bash
git-spice stack submit             # default seguro: --force-with-lease
git-spice stack submit --force     # bypassa el lease (NO usar sin motivo)
git-spice stack submit --no-verify # salta los pre-push hooks (autorización explícita)
```

### Notas operativas (gs)

- **El orden importa, y gs lo maneja:** comience siempre por la capa modificada — `gs` propaga hacia arriba por sí solo.
- **¿Salté `gs commit create`?** Si hizo `git commit` directo, la capa superior no fue auto-restacked. Use `gs upstack restack` manualmente.
- **Hooks lentos:** el auto-restack repite `pre-commit` por capa superior; optimizar o usar `--no-verify` con autorización (la misma disciplina del vanilla).
- **Firma GPG:** preservada en los commits resultantes del auto-restack si `commit.gpgsign=true` está global; verificar con `git log --show-signature`.

## Referencias

- `codex-stacked-prs` — modelo conceptual y ciclo de vida
- `codex-git-spice` — comandos `gs commit create/amend`, `gs repo sync`, `gs rebase continue/abort`
- `kata-stacked-pr-create` — creación inicial de la stack
- `kata-stacked-pr-merge` — merge bottom-up (etapa siguiente en la vida de la stack)
- `lex-protected-trunk` — trunk nunca recibe force-push
- `lex-signed-commits` — firma GPG preservada en rebase cuando `commit.gpgsign=true`
- `lex-conventional-commits` — disciplina de commit mantenida
