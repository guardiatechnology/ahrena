# Lexis: Requisitos de Calidad del Pull Request

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los Pull Requests en repositorios Guardia

## Ley

> **Todo PR en un repositorio Guardia DEBE: (1) reflejar todas las labels del issue asociado; (2) tener exactamente una label de tamaño (`size/XS` a `size/XXL`), aplicada automáticamente por GitHub Actions o manualmente cuando la automatización aún no esté configurada; (3) aplicar labels específicas de PR cuando aplique (`breaking change 💥`, `security 🛡️`, `release ↗️`); (4) ser asignado al autor con `--assignee @me`. Los PRs que no cumplan estos requisitos NO DEBEN mergearse.**

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

### 5. Prerrequisitos antes de crear el PR

El agente DEBE verificar, en este orden, antes de ejecutar `gh pr create`:

1. El issue asociado existe y cumple `lex-issue-quality`.
2. La rama sigue el formato definido en `lex-git-branches`.
3. El cuerpo del PR incluye `Closes #N` o `Refs #N` conforme a `lex-issue-first`.
4. Las labels del issue fueron reflejadas.
5. La label de tamaño fue aplicada (manualmente si es necesario).

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

- **Herramienta:** GitHub Actions PR size labeler (auto-aplica `size/*`); checklist de revisión verifica labels reflejadas y assignee; `kata-contributing-pr` aplica todas las reglas de esta Lexis al crear PRs.
- **Cuándo:** al crear y actualizar el PR; en el checklist de revisión.
- **Métrica:** 0 PRs mergeados sin label de tamaño; 0 PRs mergeados sin reflejar las labels del issue; 0 PRs sin assignee.
