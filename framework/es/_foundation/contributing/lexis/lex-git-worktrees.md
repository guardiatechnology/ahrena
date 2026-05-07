# Lexis: Uso Obligatorio de Git Worktrees

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Toda tarea basada en branch ejecutada por agentes AI en el contexto Ahrena

## Ley

> **Todo agente que necesite crear un branch para implementar una tarea DEBE hacerlo dentro de un git worktree dedicado, creado a partir del repositorio principal. El branch del worktree DEBE seguir `lex-git-branches` (`{type}/{issue-number}-{slug}`) y un Issue de GitHub DEBE existir antes de la creación (conforme a `lex-issue-first`). El directorio del worktree DEBE usar el slug del branch como nombre legible. Trabajar directamente en el checkout principal con cambios pertenecientes a un branch de tarea está PROHIBIDO. El worktree DEBE ser eliminado tras el merge del PR correspondiente.**

## Alcance

- **Se aplica a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, cualquier agente AI que cree branches para implementar tareas
- **Agentes vinculados:** todos los warriors y katas que producen código o artefactos en branches dedicados (`warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`)
- **Excepciones permitidas:**
  - Commits directos en `main` para correcciones triviales de tipografía o formato (conforme a `lex-issue-first`)
  - Operaciones de solo lectura que no producen branch
  - **Stacked Pull Requests** — una stack entera ocupa un único worktree compartido en lugar de un worktree por branch. Regla detallada en la sección 5 abajo

## Reglas

### 1. Issue antes del worktree

Antes de crear el worktree, el agente DEBE:

1. Verificar que existe un Issue de GitHub para la tarea (conforme a `lex-issue-first`)
2. Anotar el número del issue — es parte obligatoria del nombre del branch y del directorio del worktree

### 2. Nomenclatura del branch y del directorio

El branch DEBE seguir el formato de `lex-git-branches`:

```
{type}/{issue-number}-{slug}
```

El directorio del worktree DEBE seguir el path definido en `paths.worktrees` en `.ahrena/.directives` (valor por defecto: `.worktrees/`) y usar `{issue-number}-{slug}` como nombre:

```
.worktrees/{issue-number}-{slug}/
```

Ejemplo: branch `feat/42-scheduled-payments-api` → directorio `.worktrees/42-scheduled-payments-api/`

El path `.worktrees/` está dentro del repositorio y es ignorado por git mediante `.gitignore`.

### 3. Worktree como entorno aislado

El agente DEBE usar el worktree como entorno exclusivo para la tarea:

- Todas las ediciones de archivos ocurren **dentro** del worktree
- Los commits se realizan en el contexto del worktree
- El checkout principal permanece limpio — sin cambios no relacionados con su propio branch

### 4. Limpieza obligatoria tras el merge

Tras el merge del PR correspondiente:

1. Salir del directorio del worktree (si se está dentro)
2. Eliminar el worktree: `git worktree remove .worktrees/{issue-number}-{slug} --force`
3. Eliminar el branch local: `git branch -d {branch}`
4. Confirmar: `git worktree list` no debe mostrar el worktree eliminado

### 5. Worktree compartido para Stacked Pull Requests

Cuando una feature se descompone en N capas encadenadas (conforme a `codex-stacked-prs`), la regla de "un worktree por branch" de las secciones 2-4 NO se aplica. Una stack entera opera dentro de un **único** worktree compartido.

**Justificación:** el cascade rebase (`kata-stacked-pr-rebase`) opera leyendo y reescribiendo las branches de la stack en secuencia, y exige working dir único. Worktree por branch rompe ese supuesto.

#### 5.1 Nomenclatura del directorio

```
.worktrees/{issue-number}-{slug}-stack/
```

| Campo | Regla |
|---|---|
| `issue-number` | Número de la issue paraguas (1 issue → N capas) |
| `slug` | Slug descriptivo de la feature, **sin** el segmento `stack-{layer}` |
| Sufijo `-stack` | Literal y obligatorio — señal canónica de que el directorio aloja una stack |

Ejemplo: para la issue #42 ("Scheduled Payments"), el worktree es `.worktrees/42-scheduled-payments-stack/`. Dentro de él coexisten las branches `feat/42-stack-1-schema`, `feat/42-stack-2-api`, `feat/42-stack-3-ui`.

#### 5.2 Branches dentro del worktree compartido

Cada capa tiene branch propia, siguiendo el pattern de `lex-git-branches`:

```
{type}/{issue-number}-stack-{layer}-{slug}
```

La capa base (`layer = 1`) se crea junto con el worktree partiendo de `main`. Capas superiores (`layer ≥ 2`) se crean a partir de la capa anterior:

```bash
git worktree add .worktrees/${N}-${SLUG}-stack -b feat/${N}-stack-1-${SLUG} main
cd .worktrees/${N}-${SLUG}-stack
# trabajo en la capa 1, commit, push
git checkout -b feat/${N}-stack-2-${SLUG} feat/${N}-stack-1-${SLUG}
# trabajo en la capa 2, commit, push
```

#### 5.3 Cambio de capa

El agente alterna entre capas con `git checkout` dentro del mismo directorio — **nunca** creando worktrees adicionales para la misma stack:

```bash
git checkout feat/${N}-stack-1-${SLUG}    # volver a la capa base
git checkout feat/${N}-stack-3-${SLUG}    # ir al tope
```

#### 5.4 Limpieza tras el merge de la stack

Cuando la última capa de la stack mergea (la que tiene `Closes #N`), la issue se cierra y la limpieza es única:

```bash
cd ../..
git worktree remove .worktrees/${N}-${SLUG}-stack --force
# eliminar TODAS las branches locales de la stack
for i in $(seq 1 $N); do
  git branch -D feat/${N}-stack-${i}-${SLUG_i} 2>/dev/null || true
done
```

Ver `kata-stacked-pr-merge` (Paso 5) para el procedimiento completo.

#### 5.5 Restricciones específicas

- **Nunca** crear más de un worktree para la misma stack — todas las capas viven en el directorio `-stack/`
- **Nunca** mezclar branches de stacks diferentes en el mismo worktree
- **Nunca** trabajar en una branch de la stack desde el checkout principal — la stack entera es tarea del worktree dedicado
- El sufijo `-stack` en el nombre del directorio es **literal** — no sustituir por convención interna

## Ejemplos

### Correcto

```
Issue #42 existe: "Add scheduled payments API"
Branch: feat/42-scheduled-payments-api
Worktree: .worktrees/42-scheduled-payments-api/

→ El agente entra al worktree vía EnterWorktree o git worktree add
→ Todas las ediciones se realizan dentro del worktree
→ El checkout principal permanece en main, limpio
→ Tras el merge del PR: worktree eliminado, branch borrado
```

### Incorrecto

```
# El agente edita archivos en el checkout principal para implementar una feature
# ❌ El checkout principal acumula cambios mezclados

# Branch creado sin issue asociado
# ❌ Viola lex-issue-first y lex-git-branches

# Worktree no eliminado tras el merge — acumulación de directorios obsoletos
# ❌ git worktree list muestra worktrees muertos
```

## Validación Automatizada

- **Herramienta:** `git worktree list` para verificar worktrees activos; Claude Code `EnterWorktree` para creación y navegación; `kata-git-worktree` como punto de entrada canónico
- **Momento:** antes de iniciar cualquier tarea que produzca un branch; tras el merge del PR (limpieza)
- **Métrica:** 0 tareas de feature ejecutadas fuera de un worktree dedicado; 0 worktrees creados sin Issue de GitHub correspondiente; checkout principal siempre limpio durante ejecuciones de feature

## Referencias

- `codex-git-worktrees` — manual con convenciones, ciclo de vida y comandos
- `kata-git-worktree` — procedimiento paso a paso
- `lex-git-branches` — convención de nomenclatura de branches
- `lex-issue-first` — issue obligatorio antes del branch
- `codex-stacked-prs` — excepción declarada: una stack ocupa un único worktree compartido
