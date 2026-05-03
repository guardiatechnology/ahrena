# Lexis: Uso Obligatorio de Git Worktrees

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Toda tarea basada en branch ejecutada por agentes AI en el contexto Ahrena

## Ley

> **Todo agente que necesite crear un branch para implementar una tarea DEBE hacerlo dentro de un git worktree dedicado, creado a partir del repositorio principal. El branch del worktree DEBE seguir `lex-git-branches` (`{type}/{issue-number}-{slug}`) y un Issue de GitHub DEBE existir antes de la creación (conforme a `lex-issue-first`). El directorio del worktree DEBE usar el slug del branch como nombre legible. Trabajar directamente en el checkout principal con cambios pertenecientes a un branch de tarea está PROHIBIDO. El worktree DEBE ser eliminado tras el merge del PR correspondiente.**

## Alcance

- **Se aplica a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, cualquier agente AI que cree branches para implementar tareas
- **Agentes vinculados:** todos los warriors y katas que producen código o artefactos en branches dedicados (`warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`)
- **Excepciones permitidas:** commits directos en `main` para correcciones triviales de tipografía o formato (conforme a `lex-issue-first`); operaciones de solo lectura que no producen branch

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

El directorio del worktree DEBE usar el mismo slug `{issue-number}-{slug}` como nombre, prefijado con el nombre del repositorio para legibilidad:

```
../{repo-name}-{issue-number}-{slug}/
```

Ejemplo: branch `feat/42-scheduled-payments-api` → directorio `../ahrena-42-scheduled-payments-api/`

### 3. Worktree como entorno aislado

El agente DEBE usar el worktree como entorno exclusivo para la tarea:

- Todas las ediciones de archivos ocurren **dentro** del worktree
- Los commits se realizan en el contexto del worktree
- El checkout principal permanece limpio — sin cambios no relacionados con su propio branch

### 4. Limpieza obligatoria tras el merge

Tras el merge del PR correspondiente:

1. Salir del directorio del worktree (si se está dentro)
2. Eliminar el worktree: `git worktree remove ../{repo}-{issue-number}-{slug} --force`
3. Eliminar el branch local: `git branch -d {branch}`
4. Confirmar: `git worktree list` no debe mostrar el worktree eliminado

## Ejemplos

### Correcto

```
Issue #42 existe: "Add scheduled payments API"
Branch: feat/42-scheduled-payments-api
Worktree: ../ahrena-42-scheduled-payments-api/

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
