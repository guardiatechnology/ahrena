# Kata: Publicar Release (Tag Anotado + GitHub Release)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 2 del ciclo de release orquestado por `warrior-janus` — creación de tag anotado/firmado, push al remoto, espera/edición del release vía GitHub Action y verificación de post-condiciones

## Objetivo

Este Kata define el procedimiento que **publica de hecho** el release tras la aprobación humana obtenida en `kata-release-prepare`. El Kata crea el tag anotado y firmado (vía `kata-tag`), lo empuja al remoto, **detecta si hay un flujo de trabajo `release.yml` que crea el GitHub Release automáticamente** y actúa en consecuencia: aguarda el Release auto-generado o, en repositorios sin flujo de trabajo, crea el Release vía `gh release create`. Verifica que `validate-tag.yml` aprobó el tag.

## Cuándo Usar

- Cuando `warrior-janus` ha recibido aprobación humana explícita tras `kata-release-prepare`
- Nunca directamente sin el paso de preparación — el Kata presupone que la versión y el changelog fueron acordados

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Próxima versión | Sí | String SemVer aprobado (ej. `v1.3.0`) — proviene de `kata-release-prepare` |
| Ruta del changelog | Sí | `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` aprobado por el humano |
| Commit-objetivo | No | SHA específico para el tag (default: HEAD del trunk al momento de la aprobación) |

## Pre-condiciones (bloqueantes)

- [ ] `kata-release-prepare` fue ejecutado y el humano respondió **"sí"** explícitamente
- [ ] La versión respeta `lex-semantic-version`
- [ ] GPG configurado (`lex-signed-commits` / `lex-annotated-tags`)
- [ ] `.github/workflows/validate-tag.yml` existe en el repositorio destino
- [ ] Branch trunk con CI verde en el commit-objetivo (revalidar — la ventana puede haberse abierto entre prepare y publish)

Si cualquier pre-condición falla: **abortar**, registrar el motivo, devolver el control al humano.

## Flujo de trabajo

```
Progreso:
- [ ] 1. Revalidar pre-condiciones
- [ ] 2. Detectar flujo de trabajo de release en el repositorio destino
- [ ] 3. Crear tag anotado y firmado (vía kata-tag)
- [ ] 4. Empujar el tag al remoto
- [ ] 5. Aguardar que validate-tag.yml concluya con éxito
- [ ] 6. Tratar el ciclo del GitHub Release (workflow o fallback)
- [ ] 7. Verificar post-condiciones y reportar
```

### Paso 1: Revalidar Pre-condiciones

Reejecutar las verificaciones listadas en "Pre-condiciones" (no confiar en el estado de hace minutos). Si cualquier ítem falla, abortar y devolver el control al humano.

### Paso 2: Detectar Flujo de Trabajo de Release

Este paso es **crítico** — su ausencia causó un bug en v0.11.0 (race condition entre `gh release create` y workflow automático).

```bash
RELEASE_WORKFLOW=""
for wf in .github/workflows/*release*.yml .github/workflows/*release*.yaml; do
  [ -f "$wf" ] || continue
  # Detecta flujos de trabajo que disparan en push de tag (release-creating)
  if grep -qE '^\s*tags:\s*\[' "$wf" || grep -qE '^\s*-\s*"?v\*"?\s*$' "$wf"; then
    RELEASE_WORKFLOW="$wf"
    break
  fi
done
```

Registrar en el log:
- `RELEASE_WORKFLOW="<path>"` → camino "workflow-driven"
- `RELEASE_WORKFLOW=""` → camino "fallback" (`gh release create`)

### Paso 3: Crear Tag Anotado y Firmado

Invocar `kata-tag` pasando:
- Versión aprobada (ej. `v1.3.0`)
- Mensaje del tag: primera línea del changelog (`# Release v1.3.0`) o el default `"Release v1.3.0"`
- Commit-objetivo (default HEAD; respetar si el humano informó otro)

`kata-tag` devuelve el tag creado localmente. Validar con `git tag -v <versión>` antes de proseguir.

### Paso 4: Empujar el Tag al Remoto

```bash
git push origin "$NEXT_TAG"
```

Capturar el exit code. Si el push falla (ej. tag ya existe en el remoto), abortar con mensaje claro — no reutilizar tag.

A partir de este punto, el tag es visible en GitHub y los flujos de trabajo reactivos pueden dispararse.

### Paso 5: Aguardar validate-tag.yml

La Action `validate-tag.yml` (introducida por `lex-annotated-tags`) verifica que el tag es anotado + firmado + SemVer-válido. **Aguardar su conclusión**:

```bash
RUN_ID=$(gh run list \
  --workflow validate-tag.yml \
  --commit "$(git rev-parse "$NEXT_TAG")" \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')

gh run watch "$RUN_ID" --exit-status
```

Si `validate-tag.yml` falla: el tag remoto es eliminado por la propia Action; reportar al humano y finalizar con error. La remediación es rehacer el tag local (probablemente un problema de firma) e intentar publicar nuevamente.

### Paso 6: Tratar el Ciclo del GitHub Release

**Camino A — workflow-driven (`RELEASE_WORKFLOW != ""`):**

1. Aguardar la conclusión del flujo de trabajo de release:
   ```bash
   REL_RUN_ID=$(gh run list \
     --workflow "$(basename "$RELEASE_WORKFLOW")" \
     --commit "$(git rev-parse "$NEXT_TAG")" \
     --limit 1 \
     --json databaseId \
     --jq '.[0].databaseId')

   gh run watch "$REL_RUN_ID" --exit-status
   ```
2. Verificar que el Release existe: `gh release view "$NEXT_TAG"`.
3. Comparar las notas auto-generadas con el changelog de `kata-release-prepare`:
   - Si el draft es **sustancialmente más informativo** (agrupación por tipo, issues cerradas, breaking changes destacadas): sobrescribir con `gh release edit`.
   - Caso contrario: **preservar el Release auto-generado** (camino default).
4. Registrar en el log del Kata qué camino fue seguido — auditable.

```bash
# Sobrescritura opcional, solo cuando el draft es más informativo
gh release edit "$NEXT_TAG" --notes-file "$CHANGELOG_PATH"
```

**Camino B — fallback (`RELEASE_WORKFLOW == ""`):**

```bash
gh release create "$NEXT_TAG" \
  --title "Release $NEXT_TAG" \
  --notes-file "$CHANGELOG_PATH"
```

### Paso 7: Verificar Post-condiciones y Reportar

- [ ] Tag local existe y `git tag -v <versión>` verifica la firma
- [ ] Tag remoto existe (`gh api repos/$OWNER/$REPO/git/refs/tags/<versión>`)
- [ ] `validate-tag.yml` concluyó con éxito
- [ ] El GitHub Release existe y es accesible
- [ ] La ruta del changelog (draft) movida a `.ahrena/workflow/release/changelog-<versión>.published.md` (rename simple)
- [ ] Reporte final al humano: URL del Release, camino seguido (workflow-driven / fallback), tamaño del changelog (auto vs custom)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Tag publicado | Git tag anotado + firmado | Remoto (`origin`) |
| GitHub Release | URL HTTPS | Presentada al humano y registrada en el log |
| Changelog publicado | Markdown | `.ahrena/workflow/release/changelog-<versión>.published.md` |
| Camino seguido | `workflow-driven` o `fallback` | Log del Kata (auditoría) |

## Restricciones

- **NUNCA invocar `gh release create`** cuando el repositorio destino tiene un flujo de trabajo del tipo `on: push: tags: ['v*']` que ya crea el Release — la race condition causa HTTP 422 (confirmado en v0.11.0, PR #68).
- **NUNCA saltarse la espera de `validate-tag.yml`** — sin ella, releases inválidos pueden ser visibles a consumidores por segundos antes de que la Action elimine el tag.
- **NUNCA sobrescribir silenciosamente** notas auto-generadas — exigir el criterio "draft sustancialmente más informativo" y registrar la decisión.
- **NUNCA rehacer push** tras falla de `validate-tag.yml` en el mismo SHA sin corregir la causa raíz (probablemente firma inválida).
- **NUNCA invocar este Kata** sin aprobación humana explícita registrada por `kata-release-prepare` — Janus es orquestador, no ejecutor autónomo.

## Anti-patrón (lección aprendida — v0.11.0)

```bash
# ❌ INCORRECTO — causa HTTP 422 cuando el workflow crea el Release antes
git push origin v1.2.3
gh release create v1.2.3 --notes-file ./changelog.md
# → tag empujado dispara release.yml, que crea el Release
# → 5 segundos después, gh release create intenta crear de nuevo y falla con:
#    "tag_name was used by an immutable release"
```

```bash
# ✅ CORRECTO — detecta workflow, aguarda, edita solo si es necesario
git push origin v1.2.3
gh run watch "$(gh run list --workflow release.yml --commit "$(git rev-parse v1.2.3)" \
                 --limit 1 --json databaseId --jq '.[0].databaseId')"
# Workflow concluyó; el Release fue creado automáticamente.
# Solo edita las notas si el changelog preparado es sustancialmente más informativo.
gh release edit v1.2.3 --notes-file ./changelog.md
```

## Referencias

- `lex-annotated-tags` — todo tag DEBE ser anotado + firmado
- `lex-semantic-version` — formato de la versión
- `lex-signed-commits` — configuración GPG
- `kata-tag` — crea el tag localmente
- `kata-release-prepare` — Kata anterior; provee la versión aprobada + changelog
- `warrior-janus` — Warrior que orquesta prepare + gate humano + publish
- `cry-release` — cry que invoca `warrior-janus`
- Histórico: v0.11.0 (PR #68) — race condition que motivó la detección del workflow
