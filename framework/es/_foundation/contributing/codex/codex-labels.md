# Codex: Taxonomía de Labels

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Labels y GitHub Issue Types en repositorios Guardia

## Descripción General

Este Codex documenta todos los labels utilizados en los repositorios Guardia y los GitHub Issue Types configurados para la organización. Sirve como fuente única de verdad para: qué labels se aplican a qué tipo de artefacto, cuáles se aplican automáticamente versus manualmente, y cómo se calcula el tamaño de un PR. Es consultado por `kata-contributing-issue`, `kata-contributing-pr` y `lex-issue-quality`.

## Contexto

- **Dominio:** Flujo de contribución — gobernanza de labels
- **Público objetivo:** Agentes de IA, desarrolladores y colaboradores de la comunidad
- **Fuente canónica:** `.github/labeling/labels.yml` en `guardiatechnology/project-automations-experiments`
- **Actualización:** Cuando se añaden, eliminan o redefinen labels en `labels.yml`

## Contenido

### GitHub Issue Types

La organización Guardia configura tres Issue Types a nivel de repositorio. Todo issue DEBE tener un Issue Type definido en el momento de su creación mediante la API GraphQL (el CLI `gh issue create` no expone `--type`).

| Issue Type | ID | Templates que lo mapean |
|------------|----|--------------------------|
| **Task** | `IT_kwDOED9Qy84B7pBh` | `simple-task` |
| **Bug** | `IT_kwDOED9Qy84B7pBi` | `bug-report` *(futuro)* |
| **Feature** | `IT_kwDOED9Qy84B7pBj` | `feature-request`, `epic`, `user-story-for-api`, `user-story-for-frontend` |

**Definición del Issue Type después de la creación:**

```bash
# Obtener el node ID del issue
ISSUE_ID=$(gh issue view $NUMBER --repo $OWNER/$REPO --json id -q .id)

# Definir el Issue Type (ejemplo: Task)
gh api graphql -f query="
  mutation {
    updateIssue(input: {id: \"$ISSUE_ID\", issueTypeId: \"IT_kwDOED9Qy84B7pBh\"}) {
      issue { number }
    }
  }
"
```

### Categorías de Labels

#### 1. Labels de Tipo de Issue (Obligatorios — aplicados en la creación)

Obligatorios según `lex-issue-quality`. Aplicados manualmente en la creación del issue por el agente de contribución.

| Label | Template | Descripción |
|-------|----------|-------------|
| `feature request ➕` | `feature-request` | Nueva solicitud de funcionalidad (antes de la aprobación) |
| `epic` | `epic` | Gran iniciativa que agrupa múltiples historias |
| `user story 🎯` | `user-story-for-api`, `user-story-for-frontend` | Historia acotada orientada al usuario |
| `documentation 📃` | `simple-task` | Mejoras o adiciones de documentación |
| `ci 🏗️` | `simple-task` | Cambios en CI/CD o pipeline |
| `enhancement 🔝` | `simple-task` | Mejora a una funcionalidad existente |
| `evolvability ♻️` | `simple-task` | Refactorización, código limpio, mantenimiento |

> **Brecha conocida:** Los labels `api`, `frontend` y `epic` se mencionan en `lex-issue-quality` como obligatorios para algunos templates, pero aún no están definidos en `labels.yml`. DEBEN añadirse al conjunto canónico de labels antes de que esos templates puedan aplicarse completamente. Seguimiento mediante enmienda a `lex-issue-quality`.

#### 2. Labels de Contenido y Naturaleza

Aplicados manualmente para describir la naturaleza del cambio. Pueden aplicarse a issues o PRs.

| Label | Cuándo usar |
|-------|-------------|
| `bug report 🐞` | Para reportar un nuevo bug (solo en issue) |
| `bugfix 🔧` | PR o issue que corrige un bug |
| `compliance 📜` | Cambio requerido por cumplimiento regulatorio o de estándares |
| `deprecate 🪦` | Marcando una funcionalidad para deprecación |
| `feature ➕` | PR de implementación después de que un `feature request ➕` es aprobado |
| `security 🛡️` | PR que resuelve una vulnerabilidad de seguridad |
| `vulnerability 🚨` | Vulnerabilidad de seguridad detectada (issue) |
| `breaking change 💥` | Cambio que introduce una modificación de API incompatible; requiere incremento de versión major |
| `question ✋` | Issue que solicita más información |
| `good first issue 🧠` | Issue adecuado para nuevos colaboradores |

#### 3. Labels de Estado

Aplicados para rastrear el estado del ciclo de vida del issue o PR.

| Label | Cuándo aplicar |
|-------|----------------|
| `blocked 🚧` | Issue o PR bloqueado y que no puede avanzar |
| `duplicate !!` | Issue o PR que duplica uno existente |
| `rejected ❌` | Issue o PR rechazado (cerrado sin merge) |
| `wontfix 🤷‍♀️` | Issue reconocido pero que no se tratará |
| `triage 🔍` | Issue que requiere triaje antes de iniciar el trabajo |

#### 4. Labels Exclusivos de PR

Se aplican exclusivamente a Pull Requests.

| Label | Cuándo aplicar |
|-------|----------------|
| `release ↗️` | PR de release (incremento de versión + changelog) — solo mantenedores |
| `breaking change 💥` | PR que introduce un breaking change que requiere incremento de versión major |
| `security 🛡️` | PR que resuelve un problema de seguridad |

#### 5. Labels de Tamaño (Auto-aplicados por GitHub Actions)

Aplicados automáticamente por la acción de labels de tamaño de PR. **Nunca se aplican manualmente.** El tamaño se calcula contando las líneas netas modificadas (adiciones + eliminaciones), ignorando archivos generados (archivos de lock, migrations, artefactos de build).

| Label | Líneas modificadas | Descripción |
|-------|:-----------------:|-------------|
| `size/XS` | 0–9 | Cambio mínimo |
| `size/S` | 10–29 | Cambio pequeño |
| `size/M` | 30–99 | Cambio medio |
| `size/L` | 100–499 | Cambio grande |
| `size/XL` | 500–999 | Cambio extra grande |
| `size/XXL` | 1.000+ | Cambio masivo — considerar dividir |

**Orientación sobre tamaño de PR:**

| Tamaño | Orientación |
|--------|-------------|
| XS / S | Ideal. Ciclo de revisión rápido. |
| M | Aceptable. Mantener el alcance enfocado. |
| L | Aceptable para ramas de feature. Añadir contexto en la descripción del PR. |
| XL | Requiere justificación. Considerar dividir. |
| XXL | Se debe dividir en PRs más pequeños siempre que sea posible. |

#### 6. Labels Asignados por Herramienta (Auto-aplicados)

Aplicados automáticamente según quién o qué abrió el PR.

| Label | Aplicado cuando |
|-------|----------------|
| `codex ✨` | PR abierto por GitHub Copilot (Codex legado) |
| `copilot ✨` | PR abierto por GitHub Copilot |
| `cursor ✨` | PR abierto por Cursor AI |
| `dependabot 🤖` | PR abierto por Dependabot |

### Reglas de Labels para PR

Al crear un PR, el agente DEBE:

1. **Reflejar todos los labels del issue asociado** — si el issue tiene `documentation 📃` y `evolvability ♻️`, el PR recibe los mismos labels.
2. **No aplicar labels de tamaño manualmente** — el labeler de GitHub Actions los aplica automáticamente en la creación y actualización del PR.
3. **Aplicar labels específicos de PR cuando corresponda** — `breaking change 💥`, `security 🛡️`, `release ↗️`.
4. **Assignee** — siempre definir `--assignee "@me"` para que el PR quede asignado al colaborador que lo creó.

**Aplicación de labels a un PR mediante CLI:**

```bash
# Obtener labels del issue asociado
LABELS=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(",")')

# Reflejar en el PR (repetir --label para cada uno)
gh pr edit $PR_NUMBER --repo $OWNER/$REPO --add-label "$LABELS"
```

## Glosario

| Término | Definición |
|---------|-----------|
| Issue Type | Clasificación a nivel de organización GitHub: Task, Bug, Feature |
| Label de tamaño | Label auto-aplicado que refleja el tamaño del diff del PR (ignorando archivos generados) |
| Label asignado por herramienta | Label auto-aplicado que indica qué herramienta de IA o bot creó el PR |
| Reflejo de labels | Aplicar los mismos labels de un issue en el PR correspondiente |

## Referencias

- `lex-issue-quality` — Ley que exige templates, labels y contenido Why/What/How para todos los issues
- `kata-contributing-issue` — Procedimiento para crear issues (aplica labels obligatorios e Issue Type)
- `kata-contributing-pr` — Procedimiento para crear PRs (refleja los labels del issue)
- `codex-contributing` — Referencia completa del flujo de contribución
- `labels.yml` — Definiciones canónicas de labels (`guardiatechnology/project-automations-experiments`)
