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
| **Task** | `IT_kwDOED9Qy84B7pBh` | `tech-task`, `plan` |
| **Bug** | `IT_kwDOED9Qy84B7pBi` | `bug` |
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
| `api` | `user-story-for-api` | Alcance de diseño o implementación de API |
| `user story 🎯` | `user-story-for-api`, `user-story-for-frontend` | Historia acotada orientada al usuario |
| `frontend` | `user-story-for-frontend` | Alcance de implementación de frontend (UI/UX) |
| `documentation 📃` | `tech-task`, `plan` | Mejoras o adiciones de documentación |
| `ci 🏗️` | `tech-task`, `plan` | Cambios en CI/CD o pipeline |
| `enhancement 🔝` | `tech-task`, `plan` | Mejora a una funcionalidad existente |
| `evolvability ♻️` | `tech-task`, `plan` | Refactorización, código limpio, mantenimiento |

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

### Catálogo Completo de Labels

Catálogo completo sembrado por `scripts/bootstrap_labels.sh` y por `make bootstrap-labels`. El script es idempotente (usa `gh label create --force`) y se salta de forma elegante cuando el CLI `gh` está ausente o no autenticado. Los colores son hexadecimales sin el `#` inicial.

#### Workflow status (7 labels)

Rastrean el ciclo de vida de Issue y PR. Véase `lex-issue-status`.

| Label | Color | Descripción | Artefacto dependiente |
|-------|-------|-------------|------------------------|
| `status: todo` | `cccccc` | Plan creado, Issue abierto, branch enlazada, worktree lista | `lex-issue-status`, `lex-agent-planning` |
| `status: development` | `83d2ff` | Implementación en curso — Athena Fase 4 | `lex-issue-status`, `warrior-athena` |
| `status: to review` | `fff3a3` | PR abierto, esperando que el reviewer lo tome | `lex-issue-status`, `warrior-athena` |
| `status: review` | `fbca04` | Argos o humano revisando activamente | `lex-issue-status`, `warrior-argos` |
| `status: to release` | `ffb178` | Revisión aprobada, esperando que comience el release | `lex-issue-status`, `warrior-janus` |
| `status: release` | `e07400` | Release en ejecución — Janus corriendo tag/build/deploy | `lex-issue-status`, `warrior-janus` |
| `status: done` | `0e8a16` | Release completado, PR fusionado, ciclo cerrado | `lex-issue-status` |

#### Tipos de Issue (10 labels)

Obligatorios según `lex-issue-quality` Regla 2. Mapean a templates en `.github/ISSUE_TEMPLATE/`.

| Label | Color | Descripción | Artefacto dependiente |
|-------|-------|-------------|------------------------|
| `feature request ➕` | `5319E7` | Nueva solicitud de funcionalidad | `feature-request.yml` |
| `feature ➕` | `7828E5` | Nueva funcionalidad añadida. Usar solo después de aprobar una feature request | Alcance de PR |
| `epic` | `5319E7` | Gran iniciativa que agrupa múltiples historias o features | `epic.yml` |
| `user story 🎯` | `6A42EB` | Una nueva user story | `user-story-for-api.yml`, `user-story-for-frontend.yml` |
| `bug report 🐞` | `fc2803` | Reportar un nuevo bug | `bug.yml` |
| `plan 📋` | `7c4dff` | Sub-issue: unidad ejecutable bajo una Issue padre (User Story / Bug / Tech Task) | `plan.yml`, `kata-plan-task` |
| `evolvability ♻️` | `008672` | Issue o PR lanzado para asegurar la evolvability del proyecto (refactorización, código limpio) | `tech-task.yml` |
| `documentation 📃` | `0075ca` | Issue o PR relacionado con mejoras o adiciones en documentación | `tech-task.yml` |
| `ci 🏗️` | `ff7a0e` | Issue o PR relacionado con mejoras en el pipeline de CI/CD | `tech-task.yml` |
| `enhancement 🔝` | `D5BBED` | Issue o PR relacionado con una mejora a una funcionalidad existente | `tech-task.yml` |

#### Transversales y ciclo de vida (14 labels)

Describen la naturaleza del trabajo o estado fuera del flujo de desarrollo.

| Label | Color | Descripción | Artefacto dependiente |
|-------|-------|-------------|------------------------|
| `bugfix 🔧` | `fc4e03` | Issue o PR relacionado con algo que no funciona | Alcance de PR |
| `compliance 📜` | `ae6b09` | Issue o PR relacionado con una mejora para cumplir con algún estándar | Alcance de PR |
| `security 🛡️` | `D93F0B` | Este PR resuelve algún problema de seguridad | `lex-pr-quality` |
| `vulnerability 🚨` | `B60205` | Vulnerabilidad detectada | Workflow de seguridad |
| `breaking change 💥` | `925845` | Issue o PR introduciendo un breaking change. Incremento de versión major requerido | `lex-pr-quality`, `lex-semantic-version` |
| `release ↗️` | `81A5DC` | Definir solo en PR de release | `lex-pr-quality`, `warrior-janus` |
| `deprecate 🪦` | `5f6a70` | Issue para deprecar alguna funcionalidad existente | Workflow de deprecación |
| `blocked 🚧` | `e99695` | Issue o PR con algún bloqueo para avanzar | Triaje manual |
| `hold` | `fbca04` | Pausado / no perseguido activamente | Triaje manual |
| `question ✋` | `d876e3` | Se solicita información adicional | Triaje manual |
| `rejected ❌` | `b52816` | Issue o pull request rechazado | Triaje manual |
| `wontfix 🤷‍♀️` | `ffffff` | Este issue no se trabajará | Triaje manual |
| `duplicate !!` | `cfd3d7` | Este issue o pull request ya existe | Triaje manual |
| `good first issue 🧠` | `CA3AC2` | Issue adecuado para newcomers | Onboarding de open source |

#### Plataforma / alcance (2 labels)

Indican la superficie técnica afectada.

| Label | Color | Descripción | Artefacto dependiente |
|-------|-------|-------------|------------------------|
| `api` | `0075ca` | Issue o PR relacionado con diseño o implementación de API | `user-story-for-api.yml` |
| `frontend` | `D5BBED` | Issue o PR relacionado con implementación de frontend (UI/UX) | `user-story-for-frontend.yml` |

#### Asignados por herramienta (3 labels)

Auto-aplicados por integraciones cuando un PR es abierto por una herramienta de IA.

| Label | Color | Descripción | Artefacto dependiente |
|-------|-------|-------------|------------------------|
| `codex ✨` | `111112` | PR abierto por Codex | Integración |
| `copilot ✨` | `111112` | PR abierto por Copilot | Integración |
| `cursor ✨` | `111112` | PR abierto por Cursor | Integración |

#### Tamaño de PR (6 labels)

Auto-aplicados por el labeler de GitHub Actions. Obligatorios según `lex-pr-quality` Regla 2.

| Label | Color | Descripción | Artefacto dependiente |
|-------|-------|-------------|------------------------|
| `size/XS` | `9b770a` | PR altera 0-9 líneas, ignorando archivos generados. Definido automáticamente | `lex-pr-quality` |
| `size/S` | `e1b207` | PR altera 10-29 líneas, ignorando archivos generados. Definido automáticamente | `lex-pr-quality` |
| `size/M` | `f3c511` | PR altera 30-99 líneas, ignorando archivos generados. Definido automáticamente | `lex-pr-quality` |
| `size/L` | `ffdb4d` | PR altera 100-499 líneas, ignorando archivos generados. Definido automáticamente | `lex-pr-quality` |
| `size/XL` | `cb9e0a` | PR altera 500-999 líneas, ignorando archivos generados. Definido automáticamente | `lex-pr-quality` |
| `size/XXL` | `7a6600` | PR altera más de 1.000 líneas, ignorando archivos generados. Definido automáticamente | `lex-pr-quality` |

#### Procedimiento de bootstrap

Ejecutar una vez por repositorio consumidor. El catálogo también se siembra automáticamente por `make install` y `make update` cuando el destino tiene remote en GitHub.

```bash
# Ejecución manual en el repositorio actual
make bootstrap-labels

# Ejecución manual en un repositorio explícito
bash scripts/bootstrap_labels.sh owner/repo
```

El script requiere el CLI `gh` autenticado con acceso de escritura al repositorio destino. Es idempotente — las reejecuciones actualizan color y descripción sin errores.

## Glosario

| Término | Definición |
|---------|-----------|
| Issue Type | Clasificación a nivel de organización GitHub: Task, Bug, Feature |
| Label de tamaño | Label auto-aplicado que refleja el tamaño del diff del PR (ignorando archivos generados) |
| Label asignado por herramienta | Label auto-aplicado que indica qué herramienta de IA o bot creó el PR |
| Reflejo de labels | Aplicar los mismos labels de un issue en el PR correspondiente |

## Referencias

- `lex-issue-quality` — Ley que exige templates, labels y contenido Why/What/How para todos los issues
- `lex-pr-quality` — Ley que exige reflejo de labels, label de tamaño, assignee y reviewers en PRs
- `lex-issue-status` — Ley que define las labels canónicas de workflow status
- `kata-contributing-issue` — Procedimiento para crear issues (aplica labels obligatorios e Issue Type)
- `kata-contributing-pr` — Procedimiento para crear PRs (refleja los labels del issue)
- `codex-contributing` — Referencia completa del flujo de contribución
- `scripts/bootstrap_labels.sh` — Script idempotente que siembra el catálogo anterior
