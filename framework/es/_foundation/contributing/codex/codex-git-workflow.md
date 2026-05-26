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

## Identidad de autor: humano vs identidad predeterminada de los warriors

Los proyectos Ahrena eligen cómo se atribuyen los commits y PRs conducidos por warriors: como el ser humano contribuyente (predeterminado) o como la identidad predeterminada de la flota — el GitHub App `[bot]` (opt-in).

### Modo predeterminado — autor humano

Cuando `warriors_default_author.enabled` es `false` (o la sección está ausente de `.ahrena/.directives`), los warriors hacen commit utilizando la identidad git y la llave GPG del desarrollador, exactamente como si un ser humano hubiera escrito los comandos. `git log --pretty='%an <%ae>'` muestra al desarrollador; los PRs aparecen bajo el login GitHub del desarrollador. Este es el comportamiento histórico; actualizar el framework no lo cambia.

| Aspecto | Predeterminado (autor humano) |
|---------|-------------------------------|
| Autor del commit | `user.name` / `user.email` del desarrollador |
| Firma del commit | Llave GPG del desarrollador (por `lex-signed-commits`) |
| Autor del PR en GitHub | Login GitHub del desarrollador |
| `gh pr view` | `Author: <login-del-desarrollador>` |
| Pista de auditoría | Cada contribuyente aparece individualmente en los commits y PRs |

### Modo opt-in — identidad predeterminada de los warriors

Cuando `warriors_default_author.enabled` es `true`, los warriors listados en `warriors_default_author.apply_to` invocan `scripts/ahrena-auth.sh` antes de cada `git commit` / `gh pr create`. El script intercambia las credenciales del GitHub App Ahrena por un token de instalación de corta duración y exporta la identidad del App `[bot]` al shell invocante:

```
GH_TOKEN_AHRENA_WARRIORS_DEFAULT=<installation-token>
GIT_AUTHOR_NAME=ahrena-bot[bot]
GIT_AUTHOR_EMAIL=<numeric-user-id>+ahrena-bot[bot]@users.noreply.github.com
GIT_COMMITTER_NAME=ahrena-bot[bot]
GIT_COMMITTER_EMAIL=<igual que el autor>
```

Los commits producidos bajo esta identidad se firman en el servidor mediante el token de instalación del App (no se requiere llave GPG en la máquina del desarrollador para la identidad predeterminada de los warriors). Cuando `warriors_default_author.commit_co_author` es `human`, el body del commit lleva `Co-authored-by: <nombre humano> <email humano>` para que la persona que condujo el trabajo permanezca rastreable.

| Aspecto | Opt-in (identidad predeterminada de los warriors) |
|---------|---------------------------------------------------|
| Autor del commit | `ahrena-bot[bot]` |
| Firma del commit | Firmada en el servidor por el token de instalación del GitHub App |
| Autor del PR en GitHub | `ahrena-bot[bot]` |
| `gh pr view` | `Author: ahrena-bot[bot]` |
| Trailer de coautor | `Co-authored-by: <humano>` (cuando `commit_co_author=human`) |
| Pista de auditoría | Agente vs humano se responde desde la UI de GitHub sin necesidad de parsear trailers |

### Trade-offs

- **Identidad predeterminada de los warriors** — separación más clara entre contribuciones conducidas por humanos y por agentes, pista de auditoría más simple en la capa de identidad, sin GPG en la máquina del desarrollador para los commits de agentes y señal limpia para herramientas de cost tracking y revisión de PR que ya reconocen identidades `[bot]`. Requiere registrar el GitHub App predeterminado y aprovisionar las credenciales.
- **Autor humano** — preserva el reconocimiento por contribuyente en `git log`, mantiene el flujo GPG existente y elimina una pieza móvil para desarrolladores solitarios o proyectos en los que el ser humano es el único remitente. No requiere registro adicional de GitHub App.

### Opt-out por warrior

`warriors_default_author.apply_to` es una lista de nombres de warriors. Sólo los warriors en esa lista invocan el resolver de auth; los warriors omitidos de la lista mantienen el comportamiento de autor humano aunque la llave maestra esté activada. Esto permite adopción parcial (por ejemplo, identidad predeterminada para `apollo` y `hephaestus` mientras `iris` mantiene la identidad del desarrollador).

### Commits fuera de banda

Un commit escrito directamente por el ser humano (sin participación de warrior) mantiene la identidad del desarrollador independientemente de la directiva — el resolver de auth sólo se dispara cuando un warrior envuelve el commit. La directiva gobierna la atribución vía warrior, no las invocaciones directas de `git commit`. Los warriors que poseen su propio GitHub App (por ejemplo, Argos consume `AHRENA_WARRIOR_ARGOS_GH_*`) no dependen de esta identidad predeterminada — atienden a su App específico.

### Almacenamiento de credenciales

Las credenciales del GitHub App siguen la misma convención de almacenamiento que `scripts/argos/auth.sh`. El resolver de auth consulta cada fuente en orden y acepta cualquier subconjunto de valores por fuente — el APP_ID puede provenir del entorno mientras que la clave privada proviene del Keychain, y así sucesivamente.

| Fuente | Usado cuando |
|--------|--------------|
| Variables de entorno (`AHRENA_WARRIORS_DEFAULT_GH_APP_ID`, `AHRENA_WARRIORS_DEFAULT_GH_INSTALLATION_ID`, `AHRENA_WARRIORS_DEFAULT_GH_PRIVATE_KEY_PATH`) | Entornos de CI / no interactivos |
| `.env.local` en la raíz del repositorio | Desarrollo local en Linux/Windows |
| Keychain de macOS (tres entradas `security` listadas abajo) | Desarrollo local en macOS — la clave privada nunca queda en disco |

#### Configuración del Keychain en macOS

En macOS, almacene cada credencial como una entrada `security` separada. El resolver de auth completa cualquier variable que aún falte después de cargar `.env.local` + entorno:

```bash
security add-generic-password -U -s ahrena-warriors-default-gh-app-id -a "$USER" -w "<APP_ID>"
security add-generic-password -U -s ahrena-warriors-default-gh-installation-id -a "$USER" -w "<INSTALLATION_ID>"
security add-generic-password -U -s ahrena-warriors-default-gh-private-key -a "$USER" -w "$(cat /ruta/a/key.pem)"
```

La entrada `ahrena-warriors-default-gh-private-key` almacena el contenido PEM literal — el resolver de auth lo materializa en un archivo temporal con permiso 600 al momento de firmar y elimina el archivo temporal mediante el trap `_ahrena_auth_cleanup` en cada camino de salida. La clave privada nunca persiste en disco bajo el `$HOME` del operador.

En Linux / Windows / hosts no macOS, la CLI `security` está ausente; el bloque del Keychain se omite mediante `command -v security` y el resolver recurre a env / `.env.local` sin error.

Las credenciales NUNCA se envían al repositorio en un commit; el resolver de auth materializa las credenciales sólo en el entorno del shell invocante, nunca en stdout ni en logs.

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
