# Kata: Crear y Gestionar un Git Worktree

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación, uso y eliminación de git worktrees para tareas basadas en branch, conforme a `lex-git-worktrees`

## Objetivo

Crear un git worktree aislado para una tarea, ejecutar el trabajo dentro de él, abrir el PR y realizar la limpieza tras el merge — garantizando que el checkout principal permanezca limpio y que cada tarea tenga su propio entorno dedicado.

## Cuándo Usar

- Al inicio de cualquier tarea que requiera un branch dedicado
- Antes de invocar warriors o katas que producen código o artefactos en branches
- Cuando el usuario solicita "implementa X" y X requiere un nuevo branch
- Al retomar una tarea en curso que ya tiene un worktree existente

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Número de issue | Sí | Issue de GitHub existente que origina la tarea (conforme a `lex-issue-first`) |
| Tipo de branch | Sí | Uno de: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| Slug | Sí | Descripción corta en kebab-case (máx. 50 chars) |


## Flujo de Trabajo

```
Progreso:
- [ ] 1. Verificar el issue
- [ ] 2. Componer los nombres del branch y del directorio
- [ ] 3. Verificar worktrees existentes
- [ ] 4. Crear el worktree
- [ ] 5. Entrar al worktree y ejecutar la tarea
- [ ] 6. Hacer commit y abrir PR
- [ ] 7. Realizar la limpieza tras el merge
```

### Paso 1: Verificar el issue

1. Confirmar que el Issue de GitHub existe y está abierto (conforme a `lex-issue-first`)
2. Registrar el número del issue — será parte obligatoria del branch y del directorio
3. Si el issue no existe → detener y solicitar al usuario que cree el issue antes de continuar

### Paso 2: Componer los nombres del branch y del directorio

Con base en los inputs:

```
branch  = {type}/{issue-number}-{slug}
wtDir   = .worktrees/{issue-number}-{slug}/
```

Ejemplos:
- Issue #42, tipo `feat`, slug `scheduled-payments-api`
- Branch: `feat/42-scheduled-payments-api`
- Directorio: `.worktrees/42-scheduled-payments-api`

Presentar al usuario para confirmación antes de crear.

### Paso 3: Verificar worktrees existentes

```powershell
git worktree list
```

- Si el branch ya está en uso en un worktree existente → preguntar al usuario si desea retomar ese worktree (saltar al Paso 5) o crear uno nuevo
- Si el directorio objetivo ya existe pero no es un worktree → alertar al usuario y solicitar confirmación antes de sobreescribir

### Paso 4: Crear el worktree

**Vía Claude Code (preferido):**

Usar el tool `EnterWorktree` con el branch compuesto en el Paso 2.

**Vía CLI (PowerShell):**

```powershell
git worktree add $wtDir -b $branch
```

Confirmar la creación:
```powershell
git worktree list
```

### Paso 5: Entrar al worktree y ejecutar la tarea

```powershell
Set-Location $wtDir
```

Dentro del worktree:
- Ejecutar toda la implementación dentro de este directorio
- Hacer commits con mensajes en formato Conventional Commits (conforme a `lex-conventional-commits`)
- Hacer push del branch regularmente al remote:
  ```powershell
  git push -u origin $branch
  ```

### Paso 6: Hacer commit y abrir PR

Cuando la tarea esté completa:

1. Asegurar que todos los commits estén hechos y el branch esté actualizado en el remote
2. Abrir el PR referenciando el issue:

```powershell
gh pr create --title "{type}({scope}): {description}" `
             --body "Closes #$issue" `
             --base main `
             --head $branch
```

3. Registrar la URL del PR y comunicarla al usuario

### Paso 7: Realizar la limpieza tras el merge

Tras confirmar que el PR fue mergeado:

```powershell
# 1. Navegar a la raíz del repositorio (si se está dentro del worktree)
Set-Location ../..

# 2. Eliminar el worktree
git worktree remove $wtDir --force

# 3. Borrar el branch local
git branch -d $branch

# 4. Verificar
git worktree list
```

Confirmar al usuario: "Worktree `{wtDir}` eliminado. Branch `{branch}` borrado."

## Outputs

| Output | Descripción |
|--------|-------------|
| Worktree creado | Directorio `.worktrees/{issue-number}-{slug}/` con el branch activo |
| Branch creado | `{type}/{issue-number}-{slug}` en el repositorio |
| PR abierto | URL del PR referenciando el issue |
| Limpieza | Worktree y branch eliminados tras el merge |

## Ejemplo de Ejecución

### Input

```
Issue: #42 "Add scheduled payments API"
Tipo: feat
Slug: scheduled-payments-api
Repositorio: ahrena
```

### Paso 2 — Nombres compuestos

```
Branch:     feat/42-scheduled-payments-api
Directorio: .worktrees/42-scheduled-payments-api
```

### Paso 4 — Creación

```powershell
git worktree add .worktrees/42-scheduled-payments-api -b feat/42-scheduled-payments-api
# Preparing worktree (new branch 'feat/42-scheduled-payments-api')
# HEAD is now at 4df8e43 Merge pull request #33...
```

### Paso 6 — PR

```powershell
gh pr create --title "feat(payments): add scheduled payments API" `
             --body "Closes #42" --base main --head feat/42-scheduled-payments-api
# https://github.com/guardiatechnology/ahrena/pull/43
```

### Paso 7 — Limpieza

```powershell
git worktree remove .worktrees/42-scheduled-payments-api --force
git branch -d feat/42-scheduled-payments-api
# Deleted branch feat/42-scheduled-payments-api
```

## Restricciones

- **Nunca crear un worktree sin issue existente** — detener e informar al usuario si el issue no existe
- **Nunca reutilizar un worktree de otro issue** — cada tarea tiene su propio worktree
- **Nunca realizar ediciones fuera del worktree** durante la ejecución de la tarea
- **Nunca omitir la limpieza** — los worktrees obsoletos se acumulan y contaminan `git worktree list`
- **Nunca borrar el branch antes de eliminar el worktree** — git rechaza la operación

## Referencias

- `lex-git-worktrees` — Ley
- `codex-git-worktrees` — Manual con convenciones, ciclo de vida y resolución de problemas
- `lex-git-branches` — Convención de nomenclatura de branches
- `lex-issue-first` — Issue obligatorio antes del branch
- `lex-conventional-commits` — Formato de commits
- `lex-agent-planning` — Planificación de la tarea
