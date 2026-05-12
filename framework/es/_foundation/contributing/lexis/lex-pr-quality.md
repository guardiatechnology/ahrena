# Lexis: Requisitos de Calidad del Pull Request

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los Pull Requests en repositorios Guardia

## Ley

> **Todo PR en un repositorio Guardia DEBE: (1) reflejar todas las labels del issue asociado; (2) tener exactamente una label de tamaño (`size/XS` a `size/XXL`), aplicada automáticamente por GitHub Actions o manualmente cuando la automatización aún no esté configurada; (3) aplicar labels específicas de PR cuando aplique (`breaking change 💥`, `security 🛡️`, `release ↗️`); (4) ser asignado al autor con `--assignee @me`; (5) tener reviewers solicitados a partir del `.github/CODEOWNERS` del repositorio — automáticamente por GitHub cuando la auto-request esté habilitada, o manualmente vía `gh pr edit --add-reviewer` antes del merge. El repositorio DEBE tener un archivo `.github/CODEOWNERS` con al menos un owner por defecto (`* @{team}`). Los PRs que no cumplan estos requisitos NO DEBEN mergearse.**

## Cobertura

- **Se aplica a:** todos los Pull Requests en todos los repositorios Guardia.
- **Agentes vinculados:** desarrolladores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus) que crean o revisan PRs.
- **Excepciones:** PRs automáticos de Dependabot y herramientas de escaneo de seguridad, que siguen su propio flujo. Toda otra excepción requiere justificación explícita en el PR.

## Reglas

### 1. Reflejar labels del issue

Al crear un PR, el agente DEBE:

1. Obtener todas las labels del issue asociado.
2. Aplicar las mismas labels al PR.
3. Añadir labels específicas de PR cuando aplique (ver Regla 3).

```bash
# Obtener labels del issue asociado
LABELS=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(",")')

# Reflejar en el PR
gh pr edit $PR_NUMBER --repo $OWNER/$REPO --add-label "$LABELS"
```

### 2. Label de tamaño obligatoria

Todo PR DEBE tener exactamente una label de tamaño (`size/XS`, `size/S`, `size/M`, `size/L`, `size/XL` o `size/XXL`):

- **Cuando GitHub Actions está configurado:** la label se aplica automáticamente al crear o actualizar el PR. No aplicar manualmente.
- **Cuando GitHub Actions no está configurado o aún no se ejecutó:** el agente DEBE calcular el tamaño manualmente y aplicar la label antes de abrir el PR para revisión.

**Cálculo manual del tamaño:**

```bash
# Contar líneas modificadas respecto a la rama base (ignorando archivos generados)
git diff main...HEAD --stat | tail -1
```

| Label | Líneas modificadas |
|-------|:------------------:|
| `size/XS` | 0–9 |
| `size/S` | 10–29 |
| `size/M` | 30–99 |
| `size/L` | 100–499 |
| `size/XL` | 500–999 |
| `size/XXL` | 1.000+ |

### 3. Labels específicas de PR

Aplicar adicionalmente cuando aplique:

| Label | Cuándo aplicar |
|-------|----------------|
| `breaking change 💥` | El PR introduce un cambio incompatible de API; requiere incremento de versión major |
| `security 🛡️` | El PR resuelve una vulnerabilidad de seguridad |
| `release ↗️` | PR de release — solo mantenedores |

### 4. Asignación al autor

Todo PR DEBE ser asignado al autor:

```bash
gh pr create ... --assignee "@me"
# o después de la creación:
gh pr edit $PR_NUMBER --add-assignee "@me"
```

### 5. Reviewers vía CODEOWNERS

Todo PR DEBE tener reviewers solicitados a partir del `.github/CODEOWNERS` del repositorio:

1. **Precondición (configuración del repo):** el repositorio DEBE tener `.github/CODEOWNERS` con al menos un owner por defecto (`* @org/team`) y la configuración de Branch Protection con auto-request de review de los code owners habilitada.
2. **Cuando la auto-request está habilitada:** GitHub solicita automáticamente los reviewers del CODEOWNERS al crear el PR. El agente DEBE verificar (`gh pr view $PR --json reviewRequests`) que al menos un reviewer fue solicitado.
3. **Cuando no hay reviewers solicitados después de la creación:** el agente DEBE aplicar manualmente antes de marcar el PR como listo:

```bash
# Verificar reviewers actuales
gh pr view $PR_NUMBER --json reviewRequests --jq '[.reviewRequests[].login]'

# Solicitar manualmente el team por defecto del CODEOWNERS
gh pr edit $PR_NUMBER --add-reviewer "org/team"
```

Los PRs sin ningún reviewer solicitado (después de la creación y fallback manual) NO DEBEN mergearse.

### 6. Prerrequisitos antes de crear el PR

El agente DEBE verificar, en este orden, antes de ejecutar `gh pr create`:

1. El issue asociado existe y cumple `lex-issue-quality`.
2. La rama sigue el formato definido en `lex-git-branches`.
3. El cuerpo del PR incluye `Closes #N` o `Refs #N` conforme a `lex-issue-first`.
4. El repositorio tiene `.github/CODEOWNERS` configurado.

Y verificar, **inmediatamente después** de `gh pr create`:

5. Las labels del issue fueron reflejadas.
6. La label de tamaño fue aplicada (manualmente si es necesario).
7. Al menos un reviewer fue solicitado (auto vía CODEOWNERS o manual vía `--add-reviewer`).
8. Label `status: <name>` aplicada (`status: to review` por defecto al abrir el PR; per `lex-issue-status`).
9. Sección **"Session Trace"** presente en el body del PR cuando `session_tracking.enabled == true` en `.ahrena/.directives` y el branch tiene heartbeat files asociados (per `codex-session-tracking` §7). Construida por `kata-pr-prepare` agregando `.ahrena/workflow/sessions/*.json` filtrados por la branch actual. En PRs dirigidos exclusivamente por humano (sin agente Claude Code), la sección puede ser `_(human-driven; no session trace)_`.

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](framework/es/_foundation/quality/lexis/lex-hard-gate-pattern.md), el bloqueo textual de esta Lex se expresa canónicamente como:

```
<HARD-GATE>
warrior-athena, warrior-apollo, warrior-hephaestus y cualquier otro
agente NO DEBE mergear PR sin que él satisfaga TODOS los criterios:

  (a) Issue asociada está en conformidad con lex-issue-quality
  (b) Branch sigue formato {type}/{issue-number}-{slug} per lex-git-branches
  (c) Cuerpo del PR incluye Closes #N o Refs #N per lex-issue-first
  (d) Labels del issue reflejadas en el PR
  (e) Exactamente una label de tamaño (size/XS a size/XXL) aplicada
  (f) Labels específicas de PR (breaking change, security, release)
      aplicadas cuando aplicable
  (g) Assignee = autor del PR
  (h) Al menos un reviewer solicitado desde .github/CODEOWNERS
  (i) Label `status: <name>` aplicada per lex-issue-status (entrada
      en `status: to review` al abrir el PR; refleja `status:` del plan)
  (j) Sección "Session Trace" presente en el body cuando
      session_tracking.enabled == true y el branch tiene heartbeat files
      asociados, per codex-session-tracking §7 (PRs human-driven pueden
      usar la frase canónica de excepción)

Esta regla se aplica a TODO PR, independientemente de:
  - tamaño percibido ("es un cambio trivial")
  - urgencia ("incendio en producción")
  - quién solicitó ("el CEO pidió")
  - confianza del equipo ("el reviewer ya lo vio")

Excepción única declarada: PRs automáticos de Dependabot y herramientas
de escaneo de seguridad siguen su propio flujo. Toda otra excepción
exige justificación explícita en el PR.
</HARD-GATE>
```

### Aplicación a Stacked PRs

En flujos de **stacked Pull Requests** (`codex-stacked-prs`), cada capa de la cadena es un **PR real** en GitHub. El HARD-GATE de arriba se evalúa **por PR de la stack**, no una sola vez para la cadena completa: cada capa debe satisfacer **todos** los criterios (a)–(h) antes de ser mergeada. Los criterios en sí no cambian; solo el alcance de aplicación es por capa.

Implicaciones operativas:

- **Labels del issue (d):** reflejadas en todos los PRs de la stack.
- **Label de tamaño (e):** calculada a partir del diff de **cada capa** contra su base (no contra `main` de la stack completa).
- **Closes/Refs (c, vía `lex-issue-first`):** las capas intermedias usan `Refs #N`; la última usa `Closes #N`.
- **Reviewers de CODEOWNERS (h):** solicitados en cada PR; pueden ser los mismos cuando los archivos tocados mapean al mismo owner.

`kata-stacked-pr-create` automatiza el mirroring en todas las capas para reducir el esfuerzo manual, pero no relaja ningún criterio.

## Ejemplos

### Correcto

```bash
# Issue #42 con labels: documentation 📃, ci 🏗️
# Diff: 4.516 adiciones + 2.877 eliminaciones → size/XXL

gh pr create \
  --title "docs: create public documentation site with MkDocs" \
  --body "Closes #42" \
  --base main \
  --assignee "@me"

gh pr edit 42 --add-label "documentation 📃,ci 🏗️,size/XXL"
```

### Incorrecto

```bash
# ❌ PR creado sin labels
gh pr create --title "docs: add site" --body "Closes #42"
# Faltan: labels reflejadas del issue, label de tamaño, assignee

# ❌ Label de tamaño no aplicada porque "Actions lo hará"
# Cuando Actions no está configurado, el agente DEBE aplicar manualmente
```

## Validación Automatizada

- **Herramienta:** GitHub Actions PR size labeler (auto-aplica `size/*`); GitHub Branch Protection con `required_pull_request_reviews` exigiendo aprobación de code owners; checklist de revisión verifica labels reflejadas, assignee y reviewers; `kata-contributing-pr` aplica todas las reglas de esta Lexis al crear PRs.
- **Cuándo:** al crear y actualizar el PR; en el checklist de revisión; auditoría mensual del CODEOWNERS de los repositorios.
- **Métrica:** 0 PRs mergeados sin label de tamaño; 0 PRs mergeados sin reflejar las labels del issue; 0 PRs sin assignee; 0 PRs mergeados sin ningún reviewer solicitado; 100% de los repositorios Guardia con `.github/CODEOWNERS` configurado.
