# Codex: Git Worktrees en el Contexto Ahrena

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Convenciones, ciclo de vida y comandos para el uso de git worktrees por agentes AI en el contexto Ahrena

## Visión General

Este Codex es el manual canónico para el uso de git worktrees. Complementa `lex-git-worktrees` (la Ley) con explicaciones, convenciones de nomenclatura, ciclo de vida completo, comandos e integración con el Claude Code SDK. Todo agente que cree o gestione worktrees DEBE consultar este Codex.

## Contexto

- **Dominio:** aislamiento de entorno de desarrollo por tarea
- **Público objetivo:** todos los agentes (Claude, Cursor, warriors, katas) y revisores humanos
- **Actualización:** cuando los comandos o convenciones cambien

---

## 1. Qué es un git worktree

Un git worktree es un directorio de trabajo adicional vinculado al mismo repositorio git. Cada worktree tiene su propio branch activo, pero comparte el historial, los objetos y la configuración del repositorio raíz.

```
repositorio raíz (main)
├── .git/                         ← único objeto git compartido
├── src/
└── framework/

worktree (feat/42-payments-api)   ← directorio separado, branch propio
├── .git                          ← archivo puntero, no directorio
├── src/
└── framework/
```

**Por qué usarlo:** cada tarea de feature se ejecuta en un entorno aislado — sin riesgo de mezclar cambios, sin necesidad de `stash`, sin conflicto de branch activo entre tareas paralelas.

---

## 2. Convención de nomenclatura

### Branch

Sigue `lex-git-branches` obligatoriamente:

```
{type}/{issue-number}-{slug}
```

| Campo | Regla |
|---|---|
| `type` | Uno de: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `issue-number` | Número entero del Issue de GitHub asociado |
| `slug` | kebab-case, máximo 50 caracteres |

Ejemplos válidos:
- `feat/42-scheduled-payments-api`
- `fix/87-null-pointer-transfer`
- `docs/101-update-contributing-guide`

### Directorio del worktree

El path base se define en `paths.worktrees` en `.ahrena/.directives` (valor por defecto: `.worktrees/`):

```
.worktrees/{issue-number}-{slug}/
```

| Campo | Regla |
|---|---|
| `issue-number` | Mismo número de issue que el branch |
| `slug` | Mismo slug que el branch |

Ejemplos:
- `.worktrees/42-scheduled-payments-api/`
- `.worktrees/87-null-pointer-transfer/`

El directorio `.worktrees/` está dentro del repositorio y es ignorado por git mediante `.gitignore`. El path es configurable mediante `paths.worktrees` en `.ahrena/.directives`.

---

## 3. Ciclo de vida

```
issue existe
    ↓
crear worktree  →  trabajar dentro  →  commit + push  →  PR abierto  →  PR mergeado
                                                                            ↓
                                                                  eliminar worktree
                                                                  borrar branch local
```

### 3.1 Crear el worktree

**Vía Claude Code (recomendado):**

Claude Code expone el tool `EnterWorktree` que crea y entra al worktree automáticamente, con un branch que sigue la convención Ahrena.

**Vía CLI:**

```powershell
# PowerShell (terminal: powershell conforme .ahrena/.directives)
$repo    = "ahrena"
$issue   = 42
$type    = "feat"
$slug    = "scheduled-payments-api"
$branch  = "$type/$issue-$slug"
$wtDir   = ".worktrees/$issue-$slug"

git worktree add $wtDir -b $branch
```

### 3.2 Trabajar en el worktree

```powershell
Set-Location $wtDir

# editar archivos, hacer commit normalmente
git add .
git commit -m "feat(payments): add scheduled transfer entity"

# push del branch del worktree
git push -u origin $branch
```

### 3.3 Abrir el PR

Abrir el PR referenciando el issue conforme a `lex-issue-first`:

```powershell
gh pr create --title "feat(payments): add scheduled payments API" `
             --body "Closes #$issue" `
             --base main `
             --head $branch
```

### 3.4 Limpieza tras el merge

```powershell
# Navegar a la raíz del repositorio (si se está dentro del worktree)
Set-Location ../..

# Eliminar el worktree
git worktree remove $wtDir --force

# Borrar el branch local
git branch -d $branch

# Verificar
git worktree list
```

---

## 4. Integración con Claude Code

El Claude Code SDK expone el tool `EnterWorktree` para crear y navegar worktrees de forma automatizada. El agente debe preferirlo al CLI manual.

Parámetros esperados por `EnterWorktree`:
- `branch`: nombre del branch en formato `lex-git-branches`
- Crea automáticamente el directorio `.worktrees/{issue-number}-{slug}/`
- Devuelve la ruta del worktree creado

Tras completar la tarea y hacer merge del PR, el agente usa `ExitWorktree` para salir y luego ejecuta la limpieza vía CLI.

---

## 5. Worktrees en paralelo

Un repositorio admite múltiples worktrees simultáneos — cada tarea tiene el suyo:

```
git worktree list

/c/Workspace/guardia/public/ahrena                [main]
/c/Workspace/guardia/public/ahrena/.worktrees/42-payments    [feat/42-scheduled-payments-api]
/c/Workspace/guardia/public/ahrena/.worktrees/87-fix-null    [fix/87-null-pointer-transfer]
```

Restricciones de git:
- El mismo branch **no puede** estar activo en dos worktrees al mismo tiempo
- Operaciones como `git branch -d` fallan si el branch está en uso en un worktree activo — eliminar el worktree primero

---

## 6. Resolución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| `fatal: '{dir}' already exists` | Directorio creado manualmente | Eliminar el directorio y recrear con `git worktree add` |
| `error: branch already checked out` | Branch activo en otro worktree | Listar con `git worktree list`; eliminar el worktree obsoleto |
| `git branch -d` falla | Branch aún referenciado por worktree activo | `git worktree remove {dir} --force` primero |
| `git worktree list` muestra worktree sin directorio | Directorio eliminado manualmente sin `remove` | `git worktree prune` para limpiar referencias obsoletas |

---

## 7. Buenas prácticas

1. **Nombrar descriptivamente.** El slug debe ser legible por humanos — quien ejecute `ls ..` debe entender el propósito del worktree sin abrirlo.
2. **Un worktree por issue.** No reutilizar worktrees de diferentes issues — crear uno nuevo para cada tarea.
3. **Hacer commit antes de cambiar.** Antes de cambiar a otro worktree, hacer commit o stash de los cambios en el actual.
4. **Limpieza inmediata tras el merge.** No acumular worktrees obsoletos — la limpieza debe ser parte del flujo de finalización de la tarea.
5. **No editar `.git` en el worktree.** El archivo `.git` en el directorio del worktree es un puntero — no es un directorio `.git` completo; no modificarlo manualmente.

---

## Referencias

- `lex-git-worktrees` — Ley correspondiente
- `kata-git-worktree` — Procedimiento paso a paso
- `lex-git-branches` — Convención de nomenclatura de branches
- `lex-issue-first` — Issue obligatorio antes del branch
- `lex-agent-planning` — Planificación de la tarea antes de la ejecución
