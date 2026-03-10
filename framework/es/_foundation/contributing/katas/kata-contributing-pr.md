# Kata: Contribuir vía Pull Request

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de Pull Request en el repositorio origin vía MCP

## Objetivo

Este Kata define el procedimiento estandarizado para abrir un Pull Request en el repositorio origin del proyecto usando las herramientas MCP de GitKraken y la plantilla en `.ahrena/contributing_templates/pull_request_template.md` (o `.github/pull_request_template.md`). Garantiza que toda contribución siga el flujo unificado definido en `codex-contributing`. Se alinea con el `kata-contribute` existente.

## Cuándo Usar

- Cuando los cambios están listos para envío al repositorio
- Cuando el usuario solicita crear un PR
- Cuando se invoca por cry-new-pr o por cry-contribute con acción pr

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Cambios commitados | Sí | Commits listos en el branch local (ya validados por `kata-commit`) |
| Título | No | Título del PR en Conventional Commits. Si se omite, el agente infiere de los commits |
| Issue relacionada | No | Número de la issue que el PR resuelve. Si se omite, el agente pregunta |

## Workflow

```
Progreso:
- [ ] 1. Analizar cambios
- [ ] 2. Preparar branch
- [ ] 3. Push al remote
- [ ] 4. Componer PR (plantilla en .ahrena/contributing_templates/)
- [ ] 5. Crear PR vía MCP (GitKraken: pull_request_create)
- [ ] 6. Verificación final
```

### Paso 1: Analizar cambios

1. Ejecutar `git status` para verificar el estado del repositorio
2. Ejecutar `git log main..HEAD --oneline` para listar los commits a incluir
3. Verificar que todos los commits cumplan las Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`)
4. Si hay cambios no commitados, invocar `kata-commit` primero

### Paso 2: Preparar branch

1. Verificar el nombre del branch actual: `git branch --show-current`
2. Si está en `main`, crear branch siguiendo la convención: `feat/{nombre}`, `fix/{nombre}`, `docs/{nombre}` (nombre inferido del alcance de los commits)
3. Usar MCP `git_branch` con `action: create` y `branch_name`; MCP `git_checkout` para cambiar al nuevo branch

### Paso 3: Push al remote

1. Ejecutar push vía MCP `git_push` con `directory` apuntando al repositorio
2. Si el push falla porque el branch no existe en el remote, git lo creará

### Paso 4: Componer PR (plantilla)

1. Extraer `repository_organization` y `repository_name` del remote (p. ej. `git remote get-url origin`)
2. Componer el título en Conventional Commits (inglés): un commit → subject del commit; varios commits → título que resuma el cambio
3. **Plantilla:** Leer `.ahrena/contributing_templates/pull_request_template.md`; si no existe, usar `.github/pull_request_template.md`
4. Rellenar el body: Description, Type of Change, Prerequisites, How Has This Been Tested, Checklist, Related Issues (`Closes #N` o `Related to #N`); Breaking Changes, Security, Performance cuando aplique

### Paso 5: Crear PR vía MCP

Invocar MCP `pull_request_create` (servidor: `user-GitKraken`) con: `provider`: `github`; `repository_name`; `repository_organization`; `title`; `source_branch`; `target_branch`: `main`; `body`; `is_draft` según corresponda.

### Paso 6: Verificación final

- [ ] El PR se creó correctamente
- [ ] El título sigue Conventional Commits en inglés
- [ ] El body está rellenado con la plantilla del repositorio
- [ ] La issue está referenciada en el PR
- [ ] Todos los commits están firmados (GPG verified)
- [ ] El branch source es correcto

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Pull Request | GitHub PR | Repositorio origin |
| URL del PR | Enlace | Presentado al usuario |

## Restricciones

- No crear PR sin que los commits cumplan las 4 Lexis de commit
- No crear PR directamente en `main` (siempre usar branch)
- Si no hay plantilla en `.ahrena/` ni en `.github/`, usar formato estándar (Description + Related Issues)
- Si falla el MCP `pull_request_create`, presentar el error y sugerir creación manual vía `gh pr create`

## Referencias

- `codex-contributing` — Flujo de contribución Guardia
- `codex-commit-standards` — Estándares de mensaje de commit
- `kata-commit` — Procedimiento para hacer commits conformes
- `kata-contribute` — Procedimiento canónico de PR (este kata se alinea o reutiliza)
- cry-new-pr, cry-contribute — Atajos que invocan este Kata
- `.ahrena/contributing_templates/pull_request_template.md` — Plantilla de PR (fuente canónica tras el install)
