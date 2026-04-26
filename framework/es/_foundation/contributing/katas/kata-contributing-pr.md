# Kata: Contribuir mediante Pull Request

> **Prefix:** `kata-` | **Type:** Skill Repetible | **Scope:** Crear Pull Request en el repositorio de origen mediante GitHub MCP o CLI gh

## Objetivo

Esta Kata define el procedimiento estandarizado para abrir un Pull Request en el repositorio de origen del proyecto usando el template en `.ahrena/contributing_templates/pull_request_template.md` (o `.github/pull_request_template.md`). El agente refleja los labels del issue asociado, se auto-asigna el PR y garantiza que toda contribución siga el flujo unificado definido en `codex-contributing`. Se alinea con la `kata-contribute` existente.

## Cuándo Usar

- Cuando los cambios están listos para enviarse al repositorio
- Cuando el usuario solicita crear un PR
- Cuando es invocada por cry-new-pr o por cry-contribute con acción de pr

## Entradas

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| Commits realizados | Sí | Commits listos en la rama local (ya validados por `kata-commit`) |
| Título | No | Título del PR en formato Conventional Commits. Si se omite, el agente lo infiere a partir de los commits |
| Issue relacionado | No | Número del issue que el PR resuelve. Si se omite, el agente lo pregunta |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Analizar los cambios
- [ ] 2. Preparar la rama
- [ ] 3. Push al remoto
- [ ] 4. Componer el PR (template en .ahrena/contributing_templates/)
- [ ] 5. Crear PR mediante GitHub MCP (o gh)
- [ ] 6. Aplicar labels y assignee
- [ ] 7. Verificación final
```

### Paso 1: Analizar los cambios

1. Ejecutar `git status` para verificar el estado del repositorio.
2. Ejecutar `git log main..HEAD --oneline` para listar los commits que se incluirán.
3. Verificar que todos los commits siguen las Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`).
4. Si hay cambios sin commit, invocar `kata-commit` primero.

### Paso 2: Preparar la rama

1. Verificar el nombre de la rama actual: `git branch --show-current`.
2. La rama DEBE seguir el formato `{type}/{issue-number}-{slug}` según `lex-git-branches`. Si no lo sigue, renombrarla antes de continuar.
3. Confirmar que el issue asociado existe y está completo según `lex-issue-quality`.

### Paso 3: Push al remoto

1. Hacer push de la rama:
   ```bash
   git push -u origin $(git branch --show-current)
   ```
2. Si el push falla (la rama no existe en el remoto), `git push` la crea automáticamente.

### Paso 4: Componer el PR (template)

1. Extraer `owner` y `repo` de la URL remota (por ejemplo, `git remote get-url origin`).
2. Componer el título en Conventional Commits (en inglés): un solo commit → asunto del commit; múltiples commits → un título que resume el conjunto de cambios.
3. **Template:** Leer `.ahrena/contributing_templates/pull_request_template.md`; si no existe, usar `.github/pull_request_template.md`.
4. Completar el cuerpo: Descripción, Tipo de Cambio, Prerequisitos, Cómo Se Ha Probado, Checklist, Issues Relacionados (`Closes #N` o `Refs #N`); Breaking Changes, Seguridad, Rendimiento cuando corresponda.

### Paso 5: Crear PR mediante GitHub MCP (o gh)

**Preferido:** Usar la herramienta GitHub MCP `pull_request_create` (o `issue_write` con método `create_pr`) con: `owner`; `repo`; `title`; `source_branch`; `target_branch`: `main`; `body`; `assignees`: `["@me"]`; `is_draft` según sea necesario.

**Fallback (CLI gh):**
```bash
gh pr create \
  --title "..." \
  --base main \
  --body "..." \
  --assignee "@me"
```

Registrar el número del PR devuelto — necesario para el Paso 6.

### Paso 6: Aplicar labels y assignee

Los labels de tamaño se aplican **automáticamente** por GitHub Actions — no se aplican manualmente.

Aplicar labels manualmente:

1. **Obtener labels del issue asociado:**
   ```bash
   gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO \
     --json labels --jq '[.labels[].name] | join(",")'
   ```
2. **Reflejar cada label en el PR:**
   ```bash
   gh pr edit $PR_NUMBER --repo $OWNER/$REPO \
     --add-label "label1" --add-label "label2"
   ```
3. **Aplicar labels específicos de PR cuando corresponda** (ver `codex-labels`):
   - `breaking change 💥` — si algún commit introduce un cambio de API incompatible
   - `security 🛡️` — si el PR resuelve un problema de seguridad

### Paso 7: Verificación final

- [ ] El PR fue creado correctamente
- [ ] El título sigue Conventional Commits en inglés
- [ ] El cuerpo está completado con el template del repositorio
- [ ] El issue está referenciado con `Closes #N` o `Refs #N`
- [ ] Todos los labels del issue están reflejados en el PR
- [ ] Labels específicos de PR aplicados cuando corresponda (`breaking change 💥`, `security 🛡️`)
- [ ] El PR está auto-asignado (`@me`)
- [ ] Todos los commits están firmados (verificación GPG)
- [ ] La rama de origen sigue el formato `lex-git-branches`

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Pull Request | GitHub PR | Repositorio de origen |
| URL del PR | Enlace | Presentado al usuario |

## Restricciones

- No crear un PR a menos que los commits cumplan con las 4 Lexis de commit.
- No crear un PR directamente en `main` (siempre usar una rama siguiendo `lex-git-branches`).
- No aplicar labels `size/*` manualmente — son auto-aplicados por GitHub Actions.
- Si no existe template en `.ahrena/` o `.github/`, usar el formato por defecto (Descripción + Issues Relacionados).
- Siempre auto-asignarse el PR (`--assignee "@me"`), a menos que el usuario especifique explícitamente un assignee diferente.

## Referencias

- `codex-contributing` — Flujo de contribución Guardia
- `codex-labels` — Taxonomía completa de labels: reglas de reflejo, umbrales de tamaño, labels específicos de PR
- `lex-issue-quality` — Requisitos de calidad del issue (template, labels, Why/What/How)
- `lex-git-branches` — Nomenclatura de rama: `{type}/{issue-number}-{slug}`
- `codex-commit-standards` — Estándares de mensaje de commit
- `kata-commit` — Procedimiento para realizar commits conformes
- `kata-contribute` — Procedimiento canónico de PR (esta Kata se alinea con o reutiliza dicho procedimiento)
- cry-new-pr, cry-contribute — Atajos que invocan esta Kata
- `.ahrena/contributing_templates/pull_request_template.md` — Template de PR (fuente canónica tras el install)
