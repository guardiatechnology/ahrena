# Cry: Contribuir a Repositorio Guardia

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para contribuir con issues, PRs y discusiones en repositorios Guardia

## Invocación

```
/cry-contribute <acción> [opciones]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `acción` | Sí | Tipo de contribución: `pr`, `issue`, `discuss` | `pr` |
| `opciones` | No | Parámetros adicionales según la acción | `--type feature-request` |

## Acciones Disponibles

### `pr` — Crear Pull Request

```
/cry-contribute pr [--base main] [--title "..."]
```

Comportamiento:
1. Ejecuta `kata-commit` para garantizar commits conformes (si hay cambios pendientes)
2. Crea branch siguiendo la convención (`feat/nombre`, `fix/nombre`, `docs/nombre`)
3. Push al remote
4. Abre PR vía `gh pr create` completando el template `.github/pull_request_template.md`:
   - **Description:** resumen del cambio y la issue resuelta
   - **Type of Change:** marca los checkboxes relevantes (bug fix, feature, breaking change, docs, security, performance, refactoring, tests, CI/CD)
   - **Prerequisites:** asocia issue, milestone y labels correctas (breaking change, security, feature, bugfix, enhancement, evolvability, documentation)
   - **How Has This Been Tested:** describe las pruebas ejecutadas
   - **Checklist:** valida estilo, self-review, documentación, pruebas
   - **Related Issues:** referencia issues con `Closes #N` o `Related to #N`
   - **Breaking Changes:** describe migraciones si corresponde
   - **Security Considerations:** implicaciones de seguridad
   - **Performance Impact:** benchmarks si corresponde
   - **Documentation:** enlaces a documentación actualizada
5. Define el título en Conventional Commits (en inglés)
6. Valida que los commits estén firmados (`lex-signed-commits`)

### `issue` — Crear Issue

```
/cry-contribute issue [--type <template>]
```

Templates disponibles (definidos en `.github/ISSUE_TEMPLATE/`):

| Template | Uso | Estructura |
|----------|-----|-----------|
| `feature-request` | Nueva funcionalidad | User story (As/I want/So that), comportamiento actual vs deseado, valor de negocio, áreas de impacto |
| `epic` | Épico agrupando user stories | Por qué es importante, de qué se trata |
| `user-story-for-frontend` | Story de frontend detallada | User story, criterios de aceptación (Gherkin), entidades, métricas, diagramas de secuencia, mockups |
| `user-story-for-api` | Story de API detallada | User story, criterios de aceptación (Gherkin), entidades, spec de API (método, path, headers, schemas), métricas, SLIs/SLOs |

Si se omite `--type`, el agente pregunta qué template utilizar.

Comportamiento:
1. Identifica el template correcto
2. Recopila la información necesaria del usuario (o la infiere del contexto)
3. Crea la issue vía `gh issue create` con el template completado

### `discuss` — Abrir Discusión

```
/cry-contribute discuss [--category Ideas]
```

Comportamiento:
1. Verifica si la propuesta justifica una discusión (cambios significativos)
2. Estructura la discusión en formato Golden Circle (QUÉ, POR QUÉ, CÓMO)
3. Abre en GitHub Discussions vía `gh discussion create`

## Ejemplos de Uso

```
# Crear PR a partir del branch actual
/cry-contribute pr

# Crear PR con título específico
/cry-contribute pr --title "feat(auth): implement OAuth2 authentication"

# Crear issue de feature request
/cry-contribute issue --type feature-request

# Crear epic
/cry-contribute issue --type epic

# Crear user story de API
/cry-contribute issue --type user-story-for-api

# Abrir discusión antes de un cambio grande
/cry-contribute discuss
```

## Reglas

- Las blank issues están deshabilitadas — toda issue DEBE utilizar un template
- Los cambios significativos DEBEN comenzar con una discusión antes de convertirse en issue
- Los PRs DEBEN seguir todas las 4 Lexis de commit
- El título del PR DEBE seguir Conventional Commits en inglés

## Kata Asociado

`kata-contribute` — Procedimiento completo para contribuir mediante Pull Request

## Referencias

- `codex-contributing` — Flujo de contribución Guardia
- `kata-commit` — Procedimiento de commit (invocado por `pr`)
- `kata-contribute` — Procedimiento para contribuir vía PR
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Lexis de commit
- `.github/ISSUE_TEMPLATE/` — Templates de issue del repositorio
- `.github/pull_request_template.md` — Template de PR del repositorio
