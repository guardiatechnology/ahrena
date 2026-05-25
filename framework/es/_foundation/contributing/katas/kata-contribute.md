# Kata: Contribuir mediante Pull Request

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de Pull Request en el repositorio origin mediante MCP

## Objetivo

Este Kata define el procedimiento estandarizado para abrir un Pull Request en el repositorio origin del proyecto, usando las herramientas MCP de GitKraken. Se garantiza que toda contribución siga el flujo unificado definido en `codex-contributing`.

## Cuándo Usar

- Cuando los cambios están listos para su envío al repositorio
- Cuando el usuario solicita crear un PR
- Cuando se invoca mediante `cry-contribute pr`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Cambios con commit | Sí | Commits listos en el branch local (ya validados por `kata-commit`) |
| Título | No | Título del PR en Conventional Commits. Si se omite, el agente infiere a partir de los commits |
| Issue relacionada | No | Número de la issue que el PR resuelve. Si se omite, el agente pregunta |

## Workflow

```
Progreso:
- [ ] 1. Analizar cambios
- [ ] 2. Preparar branch
- [ ] 3. Push al remote
- [ ] 4. Componer PR
- [ ] 5. Crear PR mediante MCP
- [ ] 6. Verificación final
```

### Paso 1: Analizar Cambios

1. Ejecutar `git status` para verificar el estado del repositorio
2. Ejecutar `git log main..HEAD --oneline` para listar los commits a incluir
3. Verificar que todos los commits siguen las Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`)
4. Si hay cambios sin commit, invocar `kata-commit` primero

### Paso 2: Preparar Branch

1. Verificar el nombre del branch actual:
   ```
   git branch --show-current
   ```
2. Si se está en `main`, crear branch siguiendo la convención:
   - `feat/{nombre}` para features
   - `fix/{nombre}` para correcciones
   - `docs/{nombre}` para documentación
   - El nombre se infiere del alcance de los commits
3. Usar MCP `git_branch` con `action: create` y `branch_name` para crear
4. Usar MCP `git_checkout` para cambiar al nuevo branch

### Paso 3: Push al Remote

1. Ejecutar push mediante MCP `git_push` con `directory` apuntando al repositorio
2. Si el push falla porque el branch no existe en el remote, git lo creará automáticamente

### Paso 4: Componer PR

1. Extraer información del remote:
   ```
   git remote get-url origin
   ```
   Parsear `repository_organization` y `repository_name` de la URL
2. Componer el título en formato Conventional Commits (en inglés):
   - Si hay un único commit: usar el subject del commit como título
   - Si hay múltiples commits: componer título que resuma el cambio
3. Leer `.github/pull_request_template.md` y completar el body:
   - **Description:** resumen del cambio y issue resuelta
   - **Type of Change:** marcar checkboxes relevantes
   - **Prerequisites:** asociar issue, milestone y labels
   - **How Has This Been Tested:** describir pruebas
   - **Checklist:** validar ítems aplicables
   - **Related Issues:** referenciar con `Closes #N` o `Related to #N`
   - Completar secciones opcionales (Breaking Changes, Security, Performance) cuando aplique

### Paso 5: Crear PR mediante MCP

Invocar MCP `pull_request_create` (server: `user-GitKraken`) con:

| Parámetro | Valor |
|-----------|-------|
| `provider` | `github` |
| `repository_name` | Extraído del remote (ej.: `ahrena`) |
| `repository_organization` | Extraído del remote (ej.: `guardiatechnology`) |
| `title` | Título en Conventional Commits |
| `source_branch` | Branch actual |
| `target_branch` | `main` |
| `body` | Template completado |
| `is_draft` | `false` (o `true` si el usuario lo solicita) |

### Paso 6: Verificación Final

- [ ] El PR fue creado con éxito
- [ ] El título sigue Conventional Commits en inglés
- [ ] El body está completado con el template del repositorio
- [ ] La issue está referenciada en el PR
- [ ] Todos los commits están firmados (GPG verified)
- [ ] El branch source es correcto

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Pull Request | GitHub PR | Repositorio origin |
| URL del PR | Link | Mostrado al usuario |

## Restricciones

- No crear PR sin que los commits cumplan las 4 Lexis de commit
- No crear PR directamente en `main` (siempre usar branch)
- Si no existe `.github/pull_request_template.md`, usar formato estándar (Description + Related Issues)
- Si MCP `pull_request_create` falla, mostrar el error y sugerir creación manual mediante `gh pr create`

## Referencias

- `codex-contributing` — Flujo de contribución Guardia
- `codex-commit-standards` — Estándares de mensaje de commit
- `kata-commit` — Procedimiento para realizar commits conformes
- `cry-contribute` — Atajo que invoca este Kata
- `.github/pull_request_template.md` — Template de PR del repositorio
