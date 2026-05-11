# Kata: Preparar Release (Bump + Changelog)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 1 del ciclo de release orquestado por `warrior-janus` — análisis de commits, propuesta de bump SemVer, generación de changelog y verificación del estado del trunk

## Objetivo

Este Kata define el procedimiento estandarizado para analizar Conventional Commits desde el último tag, proponer el bump SemVer apropiado (major/minor/patch o "sin release"), redactar un changelog draft agrupado por tipo, y verificar que el trunk se encuentra en estado adecuado para liberar. El Kata **finaliza presentando la propuesta al humano**; la publicación ocurre en `kata-release-publish` solo tras la aprobación explícita.

## Cuándo Usar

- Cuando `warrior-janus` es invocado para iniciar un ciclo de release
- Cuando el usuario invoca `cry-release` (con o sin `--dry-run` / `--type`)
- Como paso independiente para previsualizar la versión y el changelog sin publicar

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Bump override | No | `major`, `minor`, o `patch` para sobrescribir la heurística (vía `cry-release --type`) |
| Modo dry-run | No | Cuando está activo, se genera la propuesta pero no se persiste nada (vía `cry-release --dry-run`) |
| Base ref | No | Tag o ref de partida (default: último tag SemVer en el remoto) |

## Workflow

```
Progreso:
- [ ] 1. Sincronizar tags e identificar la última versión
- [ ] 2. Recolectar commits desde el último tag
- [ ] 3. Clasificar Conventional Commits y proponer bump
- [ ] 4. Generar changelog draft
- [ ] 5. Verificar el estado del trunk
- [ ] 6. Presentar la propuesta al humano
```

### Paso 1: Sincronizar Tags e Identificar la Última Versión

1. Ejecutar `git fetch --tags --prune-tags origin` para garantizar una visión actualizada.
2. Identificar el último tag SemVer:
   ```bash
   LAST_TAG=$(git describe --tags --abbrev=0 --match 'v[0-9]*.[0-9]*.[0-9]*' 2>/dev/null || true)
   ```
   - Si no existe ningún tag, registrar **first-release** y tratar como `v0.0.0` para fines de análisis; el bump inicial sugerido es `v0.1.0` (minor) cuando hay `feat:` o `v1.0.0` si el equipo decide marcar GA (el humano decide en el Paso 6).
3. Resolver el SHA correspondiente al tag para uso en `git log <SHA>..HEAD`.

### Paso 2: Recolectar Commits Desde el Último Tag

1. Ejecutar:
   ```bash
   git log "${LAST_TAG:-$(git rev-list --max-parents=0 HEAD | tail -1)}"..HEAD \
     --no-merges \
     --pretty=format:'%H%x09%s%x09%b%x1e'
   ```
2. Separar cada commit en tres campos: SHA, subject, body.
3. Descartar commits cuyo subject no tenga un prefijo válido de Conventional Commits — registrar por separado en "commits sin tipo" (para ser listados al humano como ruido potencial).

### Paso 3: Clasificar Conventional Commits y Proponer Bump

Aplicar la tabla:

| Señal en el commit | Bump |
|--------------------|------|
| Body contiene línea que empieza con `BREAKING CHANGE:` | **major** |
| Subject usa `<type>!:` o `<type>(<scope>)!:` | **major** |
| Subject empieza con `feat:` o `feat(...):` | **minor** |
| Subject empieza con `fix:`, `perf:`, o `revert:` | **patch** |
| Solamente commits `docs:`, `chore:`, `ci:`, `style:`, `test:`, `refactor:`, `build:` | **none** (sin release) |

Regla de combinación: aplicar el **mayor** bump entre los encontrados (major > minor > patch).

Si hay override `--type`, **usar el override** pero registrar en la propuesta la heurística calculada para que el humano pueda comparar.

Calcular la próxima versión:
```
v1.2.3 + major → v2.0.0
v1.2.3 + minor → v1.3.0
v1.2.3 + patch → v1.2.4
v1.2.3 + none  → (sin release; finalizar con mensaje claro)
```

### Paso 4: Generar Changelog Draft

Agrupar los commits clasificados por tipo, en el orden: `feat` → `fix` → `perf` → `refactor` → `docs` → `build` → `ci` → `chore` → `test` → `style` → `revert`. Para cada commit, formato:

```
- <scope-si-aplica>: <subject sin el prefijo> (<short-sha>) by @<autor>
```

Estructura del changelog:

```markdown
# Release vX.Y.Z

> **Fecha:** YYYY-MM-DD
> **Bump:** major | minor | patch (vAAA.BBB.CCC → vXXX.YYY.ZZZ)
> **Issues cerradas:** #N1, #N2, ...

## ⚠ Breaking Changes
- ...

## ✨ Features
- ...

## 🐛 Fixes
- ...

## ⚡ Performance
- ...

## 🔧 Otros (refactor, docs, build, ci, chore, test, style)
- ...
```

Listar issues cerradas extrayendo `Closes #N` o `Fixes #N` de los commit bodies.

Persistir el draft en `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (crear el directorio si es necesario) — excepto en `--dry-run`, donde el draft se presenta solo en memoria.

### Paso 5: Verificar el Estado del Trunk

1. Identificar la branch trunk (default: `main`) y resolver el **SHA del commit-objetivo** (`TARGET_SHA=$(git rev-parse HEAD)`).
2. Verificar el estado de CI en el commit-objetivo (filtrar por SHA, no por branch — la branch puede haber avanzado entre la decisión y la verificación):
   ```bash
   gh run list --commit "$TARGET_SHA" --limit 5 --json status,conclusion,workflowName
   ```
   - Falla (`conclusion: failure` en flujo de trabajo obligatorio) → **bloquear propuesta**; reportar al humano.
   - En ejecución (`status: in_progress`) → **aguardar hasta 5 minutos**; si sigue en ejecución, señalar y dejar que el humano decida.
   - Éxito → proseguir.
3. Listar los PRs abiertos en el repositorio (informativo, no bloqueante):
   ```bash
   gh pr list --state open --limit 20 --json number,title,labels
   ```
   - Presentar al humano con aviso: "Estos PRs quedarán fuera del release; confirme si es intencional."

### Paso 6: Presentar la Propuesta al Humano

Salida estructurada presentando:

1. **Versión actual y próxima:** `LAST_TAG` → `NEXT_TAG`
2. **Bump:** `minor` (heurística) o `minor (override vía --type)`
3. **Resumen de commits:** conteo por tipo (`feat: 3, fix: 5, ...`)
4. **Ruta del changelog draft:** `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (o inline si dry-run)
5. **Estado del trunk:** ✅ CI verde / ⚠ PRs abiertos / ❌ CI roto
6. **Pregunta explícita:** "¿Aprobar y publicar este release? (sí / editar / cancelar)"

El Kata **finaliza aquí**. La aprobación es responsabilidad del humano; la publicación es responsabilidad de `kata-release-publish`. Sin entrada explícita "sí", `warrior-janus` no invoca la fase siguiente.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Próxima versión propuesta | String SemVer (ej. `v1.3.0`) | Presentada al humano + payload para `kata-release-publish` |
| Changelog draft | Markdown | `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (o stdout en dry-run) |
| Diagnóstico del trunk | Estructurado (estado, conteo) | Presentado al humano |
| Lista de commits sin tipo | Lista de SHAs + subjects | Presentada al humano (ruido potencial) |

## Restricciones

- **Nunca publicar** — este Kata se detiene en la propuesta. La publicación es privilegio exclusivo de `kata-release-publish` mediante aprobación humana.
- **Nunca inferir bump silenciosamente** — siempre mostrar la heurística aplicada y los commits que dispararon cada nivel.
- **Nunca confundir override y heurística** — si el humano usó `--type major` pero los commits sugieren `patch`, ambos DEBEN aparecer en la propuesta para reducir el riesgo de error humano.
- **Nunca saltarse la verificación de CI** — un trunk con CI en rojo no merece release, salvo decisión humana documentada.
- **Sin release** (bump `none`) NO es falla del Kata; es un resultado válido. Finalizar con un mensaje claro.

## Referencias

- `lex-conventional-commits` — formato de los commits analizados
- `lex-semantic-version` — formato de la próxima versión propuesta
- `lex-annotated-tags` — prerrequisito para la publicación (consumido por el Kata siguiente)
- `kata-release-publish` — Kata siguiente; recibe la versión y el changelog aprobados
- `warrior-janus` — Warrior que orquesta este Kata + gate humano + `kata-release-publish`
- `cry-release` — cry que invoca `warrior-janus`
