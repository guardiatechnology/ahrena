# Lexis: Las Ramas Trunk Están Protegidas Contra Escritura Directa

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ramas trunk (`main`, `master`, `release/*`) en todos los repositorios Guardia

## Propósito

Permitir commits directos en `main`/`master`/`release/*` colapsa todo el flujo de gobernanza: el issue deja de ser exigido en la práctica, la rama nombrada por convención (`lex-git-branches`) se vuelve opcional, la revisión por PR no ocurre, el gate de CI no bloquea código roto y el historial del trunk se convierte en un log lineal sin trazabilidad. Esta Ley cierra el loop haciendo explícita la invariante que las demás Lexis de contributing asumen implícitamente: el trunk recibe código exclusivamente mediante PR mergeado desde una rama nombrada según la convención, con todos los checks obligatorios aprobados.

## Ley

> **Las ramas trunk (`main`, `master`, `release/*`) DEBEN estar protegidas contra escritura directa. Todo desarrollo DEBE iniciar en una rama creada conforme a `lex-git-branches` (`{type}/{N}-{slug}`) y el código DEBE llegar al trunk exclusivamente mediante un Pull Request mergeado, con el issue asociado referenciado mediante `Closes #N` o `Refs #N` (`lex-issue-first`) y todos los checks de CI obligatorios aprobados. Push directo, commit directo en la working copy del trunk, force-push, bypass de admin y edición vía web UI en el trunk están PROHIBIDOS.**

## Alcance

- **Se aplica a:** todos los repositorios Guardia, sin excepción. Las ramas `main`, `master` y `release/*` son consideradas trunk en cualquier repositorio donde existan.
- **Agentes vinculados:** todos los contribuyentes (humanos e IA) — incluyendo `warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-atlas`, mantenedores y administradores del repositorio.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones. La corrección de emergencia en incidente sigue el mismo flujo (rama `fix/{N}-...` → PR con fast-track de revisión y merge), nunca commit directo.

## Consecuencias de la Violación

1. **Bloqueo automático:** las GitHub Branch Protection Rules configuradas en el repositorio rechazan push directo, force-push, edición vía web UI y merge sin PR aprobado en `main`, `master` y `release/*`. El bypass de admin está deshabilitado en las configuraciones de protección (`allow_force_pushes: false`, `enforce_admins: true`, `required_pull_request_reviews`, `required_status_checks`).
2. **Alerta:** un intento rechazado genera un evento de auditoría; un `Lex-bypass` por administrador (en caso de que la configuración sea afrouxada) dispara una alerta para el owner del repositorio y para Security.
3. **Remediación:** si un commit llegó al trunk fuera de un PR (ej.: configuración de protección deshabilitada temporalmente), la remediación es (a) revertir el commit mediante un PR de revert, (b) restaurar la configuración de protección, (c) abrir un post-mortem registrando cómo fue posible el bypass.

## Ejemplos

### Correcto

```
# Issue #42 abierto con template y labels (lex-issue-quality)
git checkout main
git pull
git checkout -b feat/42-oauth2-authentication
# ... implementación, commits atómicos firmados (lex-small-commits, lex-signed-commits) ...
git push -u origin feat/42-oauth2-authentication
gh pr create --base main --head feat/42-oauth2-authentication --title "feat(auth): add OAuth2 authentication" --body "Closes #42"
# Revisión aprobada, CI verde, merge vía UI/CLI; main avanza únicamente por el merge commit del PR.
```

### Incorrecto

```
# ❌ Commit directo en la working copy de main
git checkout main
git commit -am "fix: small typo"
git push origin main
# Aun con issue asociado, el trunk recibió escritura fuera de PR — VIOLA LA LEY.

# ❌ Force push en main para "limpiar historial"
git push --force origin main

# ❌ Edición vía web UI en archivo del trunk sin abrir PR
# (GitHub lo permite cuando la protección está deshabilitada — VIOLA LA LEY)

# ❌ Admin bypass para mergear PR sin revisión obligatoria
gh pr merge 19 --admin
```

## Validación Automatizada

- **Herramienta:**
  - GitHub Branch Protection Rules en `main`, `master`, `release/*`: `required_pull_request_reviews` (≥1 aprobación), `required_status_checks` (CI obligatorio), `allow_force_pushes: false`, `allow_deletions: false`, `enforce_admins: true`, `required_linear_history` opcional, `required_conversation_resolution: true`.
  - GitHub Actions workflow auditando el historial: detecta commits en el trunk cuyo `parent count` ≠ 2 (no-merge) y cuyo SHA no es tip de PR mergeado, fallando el pipeline y abriendo alerta.
  - `kata-quality-gate` (Phase 6 del flujo Issue-Driven) verifica que la rama no es `main`/`master`/`release/*` antes de proseguir.
- **Momento:** configuración en el setup del repositorio; auditoría continua en cada push al trunk; verificación en el Gate 2.
- **Métrica:** 0 commits non-merge en el trunk fuera de un PR aprobado; 100% de los repositorios Guardia con Branch Protection Rules configuradas según especificación; 0 incidentes de admin bypass no documentados en post-mortem.
