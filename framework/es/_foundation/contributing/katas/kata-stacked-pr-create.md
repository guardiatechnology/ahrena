# Kata: Crear Stacked Pull Requests

> **Prefix:** `kata-` | **Type:** Skill Repetible | **Scope:** Descomponer una feature grande en una cadena de PRs revisables en aislamiento, usando `git` + `gh` (camino vanilla)

## Objetivo

Esta Kata define el procedimiento para transformar una issue paraguas en una cadena de Pull Requests encadenados (stack), aplicando primero la Decision Checklist canónica de `codex-stacked-prs` para validar que la stack tiene sentido. Si la checklist reprueba, redirige a `kata-contributing-pr` (PR único). Si aprueba, crea el worktree compartido, abre una branch por capa, hace push, crea el PR de cada capa con `base` apuntando a la anterior, y espeja labels/assignee/reviewers en cada PR.

## Cuándo Usar

- Cuando el usuario pide iniciar trabajo en una issue grande y el agente quiere evaluar si vale la pena apilar
- Cuando el usuario invoca explícitamente `cry-new-stacked-pr`
- Cuando una issue paraguas ya tiene ACs numerados y el alcance cruza ≥ 2 Pilares técnicos

## Entradas

| Entrada | Obligatoria | Descripción |
|---------|:-----------:|-------------|
| Issue paraguas | Sí | Número de la issue en formato `owner/repo#N`, atendiendo `lex-issue-quality` (template, labels, Type, assignee, Why/What/How) |
| Alcance previsto | Sí | Descripción informal de componentes a tocar — usado por la Decision Checklist |
| ACs numerados | Sí | Acceptance Criteria de la issue (`AC-1`, `AC-2`, ...) — base para mapeo AC↔capa |
| Descomposición preferida | No | Sugerencia del usuario sobre cómo dividir; si se omite, el agente propone |

## Flujo de Trabajo

```
Progreso:
- [ ] 0. Pre-flight: Decision Checklist
- [ ] 1. Validar issue paraguas
- [ ] 2. Confirmar descomposición en capas con el usuario
- [ ] 3. Crear worktree compartido
- [ ] 4. Para cada capa: branch + commits + push + PR
- [ ] 5. Espejar labels/assignee/reviewers en cada PR
- [ ] 6. Verificación final
```

### Paso 0: Pre-flight — Decision Checklist

Aplicar la Decision Checklist canónica de [codex-stacked-prs](../codex/codex-stacked-prs.md), sección 2:

1. **Contar señales altas** contra issue + alcance previsto:
   - Diff estimado > 500 líneas (1 punto)
   - ≥ 4 ACs independientes (1 punto)
   - ≥ 2 Pilares técnicos atravesados (1 punto)
   - Capas obvias presentes (schema → API → UI; equivalente) (1 punto)
   - Independencia de review entre capas (1 punto)
   - Riesgo de rollback por capa (1 punto)
2. **Verificar anti-señales** (cualquiera veta):
   - Hotfix / respuesta a incidente
   - Cross-fork PR
   - Refactor monolítico sin capas naturales
3. **Decidir:**
   - **≥ 3 señales altas AND 0 anti-señales** → proponer stack al usuario
   - **Caso contrario** → parar y recomendar al usuario invocar `kata-contributing-pr` (o `cry-new-pr`) para un PR único

**Presentar la propuesta al usuario** en formato concreto, ej.:

```
Esta issue parece candidata a stacked PR:
  Señales altas: 4 (diff estimado ~800 líneas, 5 ACs, 2 Pilares, capas obvias)
  Anti-señales: 0

Propuesta de descomposición:
  Capa 1 (schema):  AC-1, AC-2 — migration + entity
  Capa 2 (api):     AC-3, AC-4 — repository + use case + router
  Capa 3 (ui):      AC-5      — frontend components

¿Confirmar y proseguir? (s/n/ajustar)
```

Si el usuario rechaza o pide PR único, finalizar esta kata y recomendar al usuario invocar `kata-contributing-pr` (o `cry-new-pr`) — las katas no encadenan otras katas; la orquestación entre katas es rol de los Warriors.

### Paso 1: Validar issue paraguas

1. Leer la issue: `gh issue view $N --repo $OWNER/$REPO --json number,title,labels,assignees,body`
2. Confirmar que cumple `lex-issue-quality`:
   - Template usado (feature-request / user-story-* / epic / simple-task)
   - Labels mínimas presentes
   - Issue Type definido (Feature / Task / Epic)
   - Al menos un assignee
   - Body responde Why / What / How
3. Si algún criterio falta, alertar al usuario y parar — la issue debe corregirse antes de la branch (`lex-issue-first`).

### Paso 2: Confirmar descomposición en capas

Tras confirmación del usuario en el Paso 0, formalizar la descomposición:

1. Para cada capa, registrar:
   - Slug corto (kebab-case): `schema`, `api`, `ui`, `tests`, etc.
   - ACs cubiertos: subset de los ACs de la issue paraguas
   - Componentes tocados: lista informal de módulos/directorios
2. Presentar al usuario la descomposición final como tabla (ej.: ver Paso 0).
3. Guardar mentalmente — se va a usar en el body de cada PR.

### Paso 3: Crear worktree compartido

Naming canónico (`codex-stacked-prs` sección 4):

```bash
ISSUE_NUMBER=42
SLUG="scheduled-payments"   # sin el segmento stack-{layer}
WORKTREE_DIR=".worktrees/${ISSUE_NUMBER}-${SLUG}-stack"
BASE_BRANCH="feat/${ISSUE_NUMBER}-stack-1-${SLUG}"

git worktree add "$WORKTREE_DIR" -b "$BASE_BRANCH" main
cd "$WORKTREE_DIR"
```

La branch de la capa 1 ya se crea junto con el worktree, partiendo de `main`. A diferencia del flujo estándar (`lex-git-worktrees`), una stack entera ocupa **un único** worktree compartido — excepción declarada en la Lexis.

### Paso 4: Para cada capa — branch + commits + push + PR

**Capa 1 (ya en `feat/${N}-stack-1-${SLUG}`):**

1. Implementar el alcance de la capa
2. Commits atómicos firmados (seguir `lex-conventional-commits`, `lex-small-commits`, `lex-signed-commits`)
3. Push:
   ```bash
   git push -u origin "feat/${ISSUE_NUMBER}-stack-1-${SLUG}"
   ```
4. Crear PR con base en `main`:
   ```bash
   gh pr create \
     --base main \
     --head "feat/${ISSUE_NUMBER}-stack-1-${SLUG}" \
     --title "feat(scope): capa 1 — schema (1/N)" \
     --body "Refs #${ISSUE_NUMBER} (1/N — schema)
   
   Cubre: AC-1, AC-2.
   Próxima capa: feat/${ISSUE_NUMBER}-stack-2-${SLUG}." \
     --assignee "@me"
   ```
5. Capturar el número del PR retornado.

**Capas 2..N:**

Para cada capa `i` de `2..N`, partiendo de la branch de la capa anterior:

```bash
PREV_BRANCH="feat/${ISSUE_NUMBER}-stack-$((i-1))-${SLUG}"
THIS_BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG}"

git checkout -b "$THIS_BRANCH" "$PREV_BRANCH"
# implementar
# commitear
git push -u origin "$THIS_BRANCH"

gh pr create \
  --base "$PREV_BRANCH" \
  --head "$THIS_BRANCH" \
  --title "feat(scope): capa ${i} — ${LAYER_NAME} (${i}/N)" \
  --body "Refs #${ISSUE_NUMBER} (${i}/N — ${LAYER_NAME})

Cubre: AC-X, AC-Y.
Base: ${PREV_BRANCH} (PR #PREV_PR_NUMBER).
$( [ "$i" -eq "$N" ] && echo "Última capa — cerrará la issue al mergear." )" \
  --assignee "@me"
```

**Capa N (última):** cambiar `Refs #${ISSUE_NUMBER}` por `Closes #${ISSUE_NUMBER}` en el body del PR.

### Paso 5: Espejar labels/assignee/reviewers en cada PR

Labels de tamaño (`size/*`) son auto-aplicadas por GitHub Actions — no aplicar manualmente.

Para cada PR creado en el Paso 4:

```bash
# Tomar labels de la issue paraguas
LABELS=$(gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" \
  --json labels --jq '[.labels[].name] | join(",")')

# Espejar en el PR
gh pr edit "$PR_NUMBER" --repo "$OWNER/$REPO" --add-label "$LABELS"

# Verificar reviewers vía CODEOWNERS (auto-request cuando configurado)
gh pr view "$PR_NUMBER" --json reviewRequests \
  --jq '[.reviewRequests[].login]'

# Si vacío, agregar manualmente per .github/CODEOWNERS:
gh pr edit "$PR_NUMBER" --add-reviewer "org/team"
```

Aplicar labels específicos de PR cuando aplicable (ver `codex-labels`):
- `breaking change 💥` — algún commit rompe contrato
- `security 🛡️` — resuelve vulnerabilidad

### Paso 6: Verificación final

- [ ] Decision Checklist documentada (señales contadas, anti-señales en cero)
- [ ] Issue paraguas atiende `lex-issue-quality`
- [ ] Worktree compartido creado en `.worktrees/${N}-${SLUG}-stack/`
- [ ] N branches creadas siguiendo `feat/${N}-stack-{i}-{slug}`
- [ ] N PRs abiertos con `base` correcto (capa 1 → main; capas 2..N → capa anterior)
- [ ] Body de cada PR referencia issue: `Refs #N` (intermedias) o `Closes #N` (última)
- [ ] Body de cada PR informa cobertura de ACs y relación con capas adyacentes
- [ ] Labels de la issue espejadas en **cada** PR
- [ ] Reviewers vía CODEOWNERS solicitados en cada PR
- [ ] Cada PR auto-asignado (`@me`)
- [ ] Commits de cada capa firmados (verificación GPG)
- [ ] Cada PR cumple `lex-pr-quality` HARD-GATE individualmente

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Stack de PRs encadenados | N PRs en GitHub | Repositorio de origen |
| Worktree compartido | Directorio local | `.worktrees/${N}-${SLUG}-stack/` |
| URLs de los PRs | Lista | Presentadas al usuario en orden (capa 1 → N) |

## Restricciones

- **Nunca** proseguir sin confirmación explícita del usuario en el Paso 0 — el agente propone, el usuario decide
- **Nunca** crear branches de la stack sin worktree compartido correspondiente
- **Nunca** mergear PRs en GitHub vía UI durante la fase de creación — el merge bottom-up tiene kata propia (`kata-stacked-pr-merge`)
- **No** aplicar labels `size/*` manualmente — GitHub Actions aplica
- Si la Decision Checklist reprueba, **no intentar argumentar** — redirigir inmediatamente a `kata-contributing-pr`
- Cada commit en cualquier capa debe seguir las 4 Lexis de commit (`lex-conventional-commits`, `lex-commit-language`, `lex-small-commits`, `lex-signed-commits`)

## Variant: git-spice

Aplicable cuando `.ahrena/.directives` declara `stacked_prs.tool: gs`. Pre-requisito: `git-spice` instalado (`brew install git-spice`) y `gs auth login` realizado una vez. Toda la estrategia (Paso 0 — Decision Checklist, validación de la issue, descomposición en capas) permanece **idéntica** al camino vanilla; solo los pasos operativos 3, 4 y 5 cambian de comandos. Consultar `codex-git-spice` para el mapeo completo.

### Paso 3 (gs): Inicializar gs y crear el worktree compartido

```bash
ISSUE_NUMBER=42
SLUG="scheduled-payments"
WORKTREE_DIR=".worktrees/${ISSUE_NUMBER}-${SLUG}-stack"

# El worktree sigue siendo uno solo compartido (codex-stacked-prs §4)
git worktree add "$WORKTREE_DIR" main
cd "$WORKTREE_DIR"

# Idempotente: solo la primera vez que el repositorio encuentra gs.
# Verifique con `cat .git/spice/store/info` y omita si ya está inicializado.
git-spice repo init --trunk main --remote origin
```

### Paso 4 (gs): Crear y submitir cada capa

**Capa 1** (desde el trunk):

```bash
# Implementar archivos de la capa 1, luego:
git add <archivos-de-la-capa-1>
git-spice branch create "feat/${ISSUE_NUMBER}-stack-1-${SLUG}" \
  -m "feat(scope): capa 1 — schema (1/N)"
# `gs branch create` commitea el stage automáticamente.
```

**Capas 2..N** (cada una sobre la anterior):

```bash
git add <archivos-de-la-capa-i>
git-spice branch create "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" \
  -m "feat(scope): capa ${i} — ${LAYER_NAME} (${i}/N)"
# Estando checked out en la capa i-1, gs la usa como base automáticamente.
```

> **Auto-restack:** cuando commiteas en la capa `i` vía `gs commit create` o `gs commit amend`, `gs` reaplica los commits de las capas `i+1..N` sobre la nueva base. Por eso: **siempre** empiece por la capa inferior; **nunca** mezcle cambios de dos capas en el mismo `commit create`.

**Submitir todos los PRs de una sola vez:**

```bash
git-spice stack submit --draft --fill
# --draft   → todos los PRs como borrador
# --fill    → completa título/body del commit message
```

`gs stack submit` acepta `--label`, `--reviewer`, `--assign` pero los aplica iguales a **todos** los PRs del stack. Para mirror exacto de la issue (con variaciones por capa), prefiera aplicar vía `gh pr edit` en el Paso 5 (gs).

**Body personalizado por capa** (opcional, cuando `--fill` no alcanza):

```bash
git-spice branch checkout "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}"
git-spice branch submit \
  --title "feat(scope): capa ${i} — ${LAYER_NAME} (${i}/N)" \
  --body "Refs #${ISSUE_NUMBER} (${i}/N — ${LAYER_NAME})

Cubre: AC-X, AC-Y."
```

Para la **última capa**, cambie `Refs #${ISSUE_NUMBER}` por `Closes #${ISSUE_NUMBER}` en el body.

### Paso 5 (gs): Espejar labels/assignee/reviewers en cada PR

Idéntico al camino vanilla — `gs` no diferencia por capa al mirror la issue. Reutilice el loop con `gh pr edit`:

```bash
LABELS=$(gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" \
  --json labels --jq '[.labels[].name] | join(",")')

for PR in "${PR_NUMBERS[@]}"; do
  gh pr edit "$PR" --repo "$OWNER/$REPO" \
    --add-label "$LABELS" \
    --add-assignee "@me"
  # Reviewers vía CODEOWNERS: auto-request cuando está configurado;
  # si no, agregue manualmente:
  gh pr edit "$PR" --add-reviewer "org/team"
done
```

### Notas operativas (gs)

- **Force-push seguro por default:** `gs branch submit` y `gs stack submit` ya usan `--force-with-lease`; nunca pase `--force` sin justificación registrada.
- **Hooks pesados:** el auto-restack repite el ciclo de hooks por cada capa superior; optimice pre-commit o use `--no-verify` con autorización del usuario (la misma disciplina del vanilla).
- **Firma GPG:** preservada si `commit.gpgsign=true` está global; `gs` no tiene flag específico.
- **Confusión de nombre:** el binario se llama `git-spice`. Use `git-spice` en scripts; `gs` solo en shell interactivo (alias).

## Referencias

- `codex-stacked-prs` — Decision Checklist canónica, naming, ciclo de vida
- `codex-git-spice` — instalación, catálogo de comandos `gs`, mapeo vanilla→gs
- `kata-stacked-pr-rebase` — cascade rebase cuando una capa inferior cambia
- `kata-stacked-pr-merge` — merge bottom-up tras review aprobada
- `kata-contributing-pr` — fallback para PR único cuando Decision Checklist reprueba
- `lex-issue-first`, `lex-issue-quality` — pre-condiciones de la issue paraguas
- `lex-git-branches` — naming `{type}/{N}-stack-{layer}-{slug}`
- `lex-git-worktrees` — excepción declarada para worktree compartido de stack
- `lex-pr-quality` — HARD-GATE aplicado por PR de la stack
- `cry-new-stacked-pr` — atajo que invoca esta Kata
