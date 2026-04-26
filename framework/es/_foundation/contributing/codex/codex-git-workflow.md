# Codex: Flujo de Trabajo Git

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Flujo completo de contribución git — Issue → Rama → Commits → PR → Merge

## Propósito

Este Codex describe el flujo de trabajo git canónico para todos los repositorios Guardia. Conecta las Lexis individuales en una referencia única de extremo a extremo para que desarrolladores y agentes puedan seguir el ciclo completo de contribución sin consultar cada artefacto por separado.

## Visión General del Flujo

```
Issue → Rama → Commits → PR → Revisión → Merge
```

Cada paso está regido por al menos una Lexis. Saltarse un paso viola el flujo.

## Paso 1 — Issue (`lex-issue-first`)

**Regla:** Ninguna rama sin un Issue.

1. Verifique si ya existe un Issue para el trabajo planificado.
2. Si no existe: abra uno usando `kata-contributing-issue` (o el cry correspondiente: `cry-new-feature-request`, `cry-new-epic`, etc.).
3. El Issue DEBE describir: **qué** (objetivo), **por qué** (motivación e impacto), **resultado esperado** (criterios de aceptación).
4. Anote el número del Issue — es obligatorio para el nombre de la rama.

**Plantillas disponibles (`.ahrena/contributing_templates/`):**

| Tipo | Plantilla |
|------|-----------|
| Feature request | `feature-request.md` |
| Epic | `epic.md` |
| User story (API) | `user-story-for-api.md` |
| User story (frontend) | `user-story-for-frontend.md` |

## Paso 2 — Rama (`lex-git-branches`)

**Formato:** `{type}/{issue-number}-{slug}`

```bash
git checkout main
git pull origin main
git checkout -b feat/42-oauth2-authentication
```

**Tipos válidos:** `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test`

| Ejemplo | Tipo |
|---------|------|
| `feat/42-oauth2-authentication` | Nueva funcionalidad |
| `fix/123-null-pointer-in-transaction` | Corrección de bug |
| `chore/89-update-rust-dependencies` | Mantenimiento |
| `docs/201-contributing-guide-revision` | Documentación |
| `refactor/77-extract-payment-service` | Refactorización |

## Paso 3 — Commits

Cuatro Lexis rigen cada commit:

| Lexis | Regla |
|-------|-------|
| `lex-conventional-commits` | Formato: `{type}[scope]: {description}` |
| `lex-signed-commits` | Todo commit DEBE estar firmado con GPG (`-S` o `commit.gpgsign true`) |
| `lex-small-commits` | Un cambio lógico por commit (atómico) |
| `lex-commit-language` | Subject en inglés; el body PUEDE usar la etiqueta `[lang]` |

### Formato del commit

```
{type}[scope opcional]: {descripción en inglés}

[body opcional — use etiqueta [lang] para idioma local]

[footer opcional: Closes #N, BREAKING CHANGE: ...]
```

### Ejemplos

```bash
# ✅ Correcto: atómico, firmado, convencional, subject en inglés
git commit -S -m "feat(auth): add OAuth2 client configuration"
git commit -S -m "test(auth): add unit tests for OAuth2 flow"

# ❌ Incorrecto: cambios mezclados, sin firma
git commit -m "add OAuth2, fix header bug, update README"
```

### Configuración de firma automática

Consulte `kata-setup-gpg-signing` para configurar la firma GPG automática. Una vez configurado:

```bash
# git firma automáticamente — sin necesidad del flag -S
git commit -m "feat(auth): implement token refresh"
```

## Paso 4 — Pull Request (`lex-issue-first`)

1. Envíe la rama:
   ```bash
   git push -u origin feat/42-oauth2-authentication
   ```
2. Abra el PR usando `kata-contributing-pr` o `gh pr create`.
3. Título del PR: formato Conventional Commits en inglés.
4. El cuerpo del PR DEBE incluir `Closes #N` o `Refs #N`.

### Estructura del cuerpo del PR

```markdown
## Description
{resumen del cambio}

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Related Issues
Closes #42

## How Has This Been Tested?
{describa las pruebas locales o verificaciones automatizadas}

## Checklist
- [ ] Los commits están firmados (GPG Verified)
- [ ] Las pruebas existentes pasan
- [ ] Se añadieron nuevas pruebas para nuevos comportamientos
- [ ] Sin cambios fuera del alcance
```

## Paso 5 — Revisión y Merge

Requisitos para el merge:

- Mínimo 1 aprobación de un mantenedor (según CODEOWNERS).
- Todos los checks de CI pasan.
- Todos los commits muestran **Verified** (firmados con GPG).
- Sin conflictos de merge con `main`.
- El PR referencia un Issue.

Tras el merge: `main` se actualiza; la rama se elimina.

## Releases (`lex-semantic-version`)

Los releases siguen el Versionado Semántico (`MAJOR.MINOR.PATCH`). Las etiquetas DEBEN estar firmadas:

```bash
git tag -s v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

Los breaking changes incrementan `MAJOR`. Las nuevas funcionalidades incrementan `MINOR`. Las correcciones incrementan `PATCH`.

## Referencias

| Artefacto | Propósito |
|-----------|-----------|
| `lex-issue-first` | Todo cambio debe originarse en un Issue |
| `lex-git-branches` | Nomenclatura de rama: `{type}/{issue-number}-{slug}` |
| `lex-conventional-commits` | Formato de mensaje de commit |
| `lex-signed-commits` | Requisito de firma GPG |
| `lex-small-commits` | Commits atómicos |
| `lex-commit-language` | Subject en inglés |
| `lex-semantic-version` | Etiquetado de releases |
| `kata-setup-gpg-signing` | Configurar firma GPG |
| `kata-contributing-issue` | Abrir un Issue en GitHub |
| `kata-contributing-pr` | Abrir un Pull Request |
| `codex-contributing` | Visión general del proceso de contribución |
