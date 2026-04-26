# Lexis: Convención de Nomenclatura de Ramas

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todas las ramas git en repositorios Guardia

## Ley

> **Toda rama DEBE seguir el formato `{type}/{issue-number}-{kebab-slug}`, donde `type` DEBE ser uno de los tipos de Conventional Commits (`feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test`), `{issue-number}` es el número del Issue de GitHub al que la rama está vinculada, y `{kebab-slug}` es una descripción breve, en minúsculas y separada por guiones. Crear o enviar una rama sin un Issue asociado está PROHIBIDO. Los nombres de rama fuera de este formato están PROHIBIDOS.**

## Cobertura

- **Se aplica a:** todas las ramas en todos los repositorios Guardia (excepto `main` y `release/*`, gestionadas por los mantenedores).
- **Agentes vinculados:** desarrolladores, agentes de IA que crean ramas (warrior-athena, warrior-apollo, warrior-hephaestus).
- **Excepciones:** Ninguna. Las ramas fuera del formato válido son rechazadas al hacer push.

## Reglas

### 1. Formato

```
{type}/{issue-number}-{slug}
```

| Parte | Regla |
|-------|-------|
| `type` | Uno de: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `issue-number` | Entero positivo correspondiente al número del Issue de GitHub asociado |
| `slug` | Minúsculas, kebab-case, máximo 50 caracteres; resume el cambio |

### 2. Issue antes de la rama

Una rama NO DEBE crearse antes de que exista el Issue correspondiente. Consulte `lex-issue-first`.

### 3. Una rama por Issue (por defecto)

Cada Issue corresponde típicamente a una rama. Las excepciones (múltiples ramas para un único Issue complejo) requieren justificación explícita en los comentarios del Issue.

## Ejemplos

### Correctos

```
feat/42-oauth2-authentication
fix/123-null-pointer-in-transaction
chore/89-update-rust-dependencies
docs/201-contributing-guide-revision
refactor/77-extract-payment-service
test/310-coverage-for-refund-module
ci/95-add-github-actions-lint
```

### Incorrectos

```
seguim/wizardly-ptolemy-adb24b   # ❌ nombre generado, sin type, sin número de issue
my-feature                       # ❌ sin type, sin número de issue
wip/auth                         # ❌ wip no es un tipo válido de Conventional Commits
feat-42-oauth2                   # ❌ separador con barra oblicua requerido entre type y el resto
feat/oauth2-authentication       # ❌ número de issue ausente
```

## Validación Automatizada

- **Herramienta:** hook pre-push con regex `^(feat|fix|docs|build|chore|ci|style|refactor|perf|test)\/[0-9]+-[a-z0-9][a-z0-9-]{0,49}$`; reglas de protección de rama en GitHub.
- **Cuándo:** al hacer push de la rama al remoto; al crear el PR.
- **Métrica:** 0 ramas en el remoto fuera del formato definido.
