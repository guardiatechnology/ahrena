# Kata: Estampar costo de tokens y tiempo de implementación (Claude Code) en el PR

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Computar tokens, costo USD y tiempo de implementación de la asistencia IA durante el desarrollo de un PR y estampar el resultado en el body vía `gh pr edit`

## Objetivo

Calcular tokens, costo estimado en USD y tiempo de implementación (activo + calendario) de las sesiones Claude Code que originaron un Pull Request y grabar un bloque markdown idempotente en el body del PR. Apoya la visibilidad financiera, el ROI de la automatización y la lectura de throughput por feature, bug o refactor. Es invocada por `kata-contributing-pr` cuando `pr_cost_tracking.enabled: true` en `.ahrena/.directives` y puede correr de manera independiente para actualizar PRs existentes.

## Cuándo Usar

- Justo después de crear o actualizar un PR vía `kata-contributing-pr` en un proyecto que activó `pr_cost_tracking.enabled: true`.
- Manualmente en un PR existente para actualizar el stamp con sesiones adicionales (p. ej., tras nuevos commits).
- En CI o hook post-merge para auditoría histórica (uso futuro).

## Entradas

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| Número del PR | Sí | `$PR_NUMBER` en el repositorio actual |
| Repositorio | No | `owner/repo`; default: `gh repo view --json nameWithOwner` |
| Branch | No | nombre de la branch del PR; default: `gh pr view <PR> --json headRefName` |
| Ventana inicial | No | fecha ISO; default: fecha del primer commit de la branch (`git log --reverse <base>..<head> --format=%cI \| head -1`) |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Verificar precondiciones y directivas
- [ ] 2. Resolver contexto del PR
- [ ] 3. Computar tokens y costo vía ccusage (o fallback) — bucket Development
- [ ] 4. Computar tiempo de implementación (activo + calendario) — buckets Development y Review
- [ ] 5. Computar revisores externos vía pr-cost-stamp-reviews.sh
- [ ] 6. Renderizar bloque markdown con subsecciones Development / Review / Total
- [ ] 7. Upsert en el body del PR
- [ ] 8. Verificación final
```

### Paso 1: Verificar precondiciones y directivas

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Leer `pr_cost_tracking.enabled`. Si es `false` o ausente → finalizar silenciosamente con mensaje `pr-cost-stamp: disabled in directives, skipping`.
3. Leer `pr_cost_tracking.idle_gap_minutes` (default `10`). Ese valor es el gap (en minutos) que separa ventanas activas dentro de una sesión Claude Code para el cálculo de tiempo activo.
4. Leer `pr_cost_tracking.attribution_mode` (default `hook`). Modos:
   - `hook` — `scripts/pr-cost-stamp.sh` se invoca con `--branch <HEAD_REF>` y `--purpose <dev|review>`, consumiendo el sidecar `~/.claude/projects/*/branches.jsonl` producido por el hook `pr-cost-attribution.sh`. Permite separar Development y Review.
   - `project` (legado) — comportamiento anterior: filtro solo por project + since, sin distinción de branch ni de purpose. Mantenido para proyectos que aún no migraron. El bloque renderizado en este modo omite la subsección Review (Claude Code local) y agrega un aviso `meta.warnings`.
5. Leer `pr_cost_tracking.known_ai_reviewers` (lista, opcional). El default trae `gemini-code-assist[bot]`, `claude[bot]`, `coderabbitai[bot]`, `qodo-merge-pro[bot]`. Los proyectos pueden extenderlo para reconocer otros bots de revisión.
6. Leer `pr_cost_tracking.known_ai_authors` (lista, opcional). El default trae `ahrena-bot[bot]`, `claude[bot]`, `copilot[bot]`. Conduce el reconocimiento de autor-bot descrito en `## Identidad del autor`. Los proyectos extienden la lista para reconocer autores-bot adicionales.
7. Verificar disponibilidad de `gh` (autenticado), `git`, `scripts/pr-cost-stamp.sh` y `scripts/pr-cost-stamp-reviews.sh`. Cualquier ausencia → finalizar con warning, sin propagar el error.
8. Intentar `npx ccusage@latest --version` (timeout 30s). Éxito → `ccusage` es el backend de tokens/USD para el bucket Development. Falla → `scripts/pr-cost-stamp.sh` también cubre tokens (sin costo). En ambos caminos, el script es la fuente única de verdad de los tiempos (activo + calendario) — `ccusage` no expone `timestamp` por turno en ningún subcomando.

### Paso 2: Resolver contexto del PR

1. `OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)`.
2. `PR_NUMBER` desde el input o desde `gh pr view --json number --jq .number`.
3. `HEAD_REF=$(gh pr view $PR_NUMBER --json headRefName --jq .headRefName)`.
4. `BASE_REF=$(gh pr view $PR_NUMBER --json baseRefName --jq .baseRefName)`.
5. `SINCE_DATE` (formato `YYYYMMDD` para `--since`) y `BRANCH_FIRST_COMMIT_ISO` (ISO 8601 para `--calendar-start`). Si la branch aún no tiene commits sobre el base (branch nueva o error de resolución), usar la fecha actual como fallback:
   ```bash
   SINCE_DATE=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cd --date=format:%Y%m%d | head -1)
   BRANCH_FIRST_COMMIT_ISO=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cI | head -1)
   [ -z "$SINCE_DATE" ] && SINCE_DATE=$(date -u +%Y%m%d)
   [ -z "$BRANCH_FIRST_COMMIT_ISO" ] && BRANCH_FIRST_COMMIT_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   ```
6. `PR_END_ISO`: extremo superior de la ventana de calendario. Si el PR ya fue mergeado, usar `mergedAt`; en caso contrario, hora actual en UTC:
   ```bash
   MERGED_AT=$(gh pr view $PR_NUMBER --json mergedAt --jq .mergedAt)
   if [ -n "$MERGED_AT" ] && [ "$MERGED_AT" != "null" ]; then
     PR_END_ISO="$MERGED_AT"
   else
     PR_END_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   fi
   ```
7. Resolver el directorio raíz del repositorio principal (no del worktree, cuando aplique):
   ```bash
   MAIN_DIR=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
   ```
   `git rev-parse --git-common-dir` apunta al `.git/` del repositorio principal incluso desde worktrees, garantizando que sesiones registradas en main y en worktrees se agreguen juntas.
8. `PROJECT_BASENAME=$(basename "$MAIN_DIR")` — usado por el fallback y por el cálculo de tiempo (matching por basename del `cwd` en el JSONL).
9. `PROJECT_ID=$(echo "$MAIN_DIR" | tr / -)` — id en formato Claude Code (path con `/` → `-`, prefijo `-`); usado por el filtro `--project=<id>` de `ccusage`.

### Paso 3: Computar tokens y costo vía ccusage (o fallback) — bucket Development

`ccusage` agrega por proyecto, sin distinción de branch ni de purpose. Para la subsección **Development** el resultado bruto entra directo; los turnos rotulados como `purpose=review` siguen contando aquí en el modo `project`. En el modo `hook`, el filtro lo aplica `scripts/pr-cost-stamp.sh` en paralelo (Paso 4) y los números de Development en la subsección del bloque se refieren **solo** a los turnos dev (los turnos review entran en la subsección Review).

**Preferido — `ccusage`:**

```bash
RAW_DEV=$(npx --yes ccusage@latest daily \
  --project="$PROJECT_ID" \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null)
```

Notas:
- El subcomando es `daily`. El `session` no acepta `--project`. La forma `--project=<id>` (con `=`) preserva el prefijo `-` del id.
- `--offline` usa la tabla de pricing embebida en `ccusage`; quitar para forzar fetch online cuando online esté disponible y actualizado.
- La salida JSON contiene `daily` (entradas por fecha) y `totals` (agregado), con `modelBreakdowns` por entrada.

**Conteo de sesiones únicas** (llamada complementaria; `daily` no lo expone):

```bash
SESSIONS_DEV=$(npx --yes ccusage@latest session \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null \
  | jq --arg pid "$PROJECT_ID" '[.sessions[] | select(.sessionId | startswith($pid))] | length')
```

El `sessionId` en `ccusage session --json` comienza con el id del proyecto (mismo formato `--project=<id>`), lo que permite filtrar vía `startswith`. Sesión aquí es la sesión del Claude Code (una conversación continua), no commit individual: 6 commits dentro de la misma conversación cuentan como 1 sesión.

**Fallback — `scripts/pr-cost-stamp.sh`:** cuando `ccusage` no está disponible, el propio script cubre los tokens (sin USD). En el modo `hook`, pase `--branch` y `--purpose` para aislar Development:

```bash
RAW_DEV=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  ${ATTR_MODE_HOOK:+--branch "$HEAD_REF" --purpose dev})
```

Salida JSON con schema equivalente al de `ccusage` (claves `totals`, `breakdown`, `meta`).

### Paso 4: Computar tiempo de implementación (activo + calendario) — buckets Development y Review

El tiempo siempre proviene de `scripts/pr-cost-stamp.sh`, independientemente del backend de tokens, porque `ccusage` no expone `timestamp` por turno en ningún subcomando (validado en `docs/guide/json-output.md`).

**Modo `hook`** — script invocado **dos veces**, separando dev y review por `--purpose`:

```bash
TIME_DEV=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --branch "$HEAD_REF" \
  --purpose dev \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")

TIME_REVIEW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --branch "$HEAD_REF" \
  --purpose review \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")

ACTIVE_MIN_DEV=$(echo    "$TIME_DEV"    | jq -r '.totals.active_minutes')
ACTIVE_MIN_REVIEW=$(echo "$TIME_REVIEW" | jq -r '.totals.active_minutes')
CALENDAR_MIN=$(echo      "$TIME_DEV"    | jq -r '.totals.calendar_minutes')
WARNINGS=$(echo "$TIME_DEV" "$TIME_REVIEW" | jq -s '[.[].meta.warnings // []] | add | unique')
```

`--branch` filtra los turnos por el branch del PR vía sidecar; `--purpose` filtra por bucket. El calendario sale del bucket dev (ambas invocaciones usan la misma ventana; tomar una evita duplicar). Cuando el sidecar está ausente, el script popula `meta.warnings` automáticamente — propague al renderizador.

**Modo `project` (legado)** — invocación única, sin distinción de purpose:

```bash
TIME_DEV=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")
TIME_REVIEW=""  # la subsección Claude Code (local) se omite del bloque
```

Modelo de cálculo (codificado en el script, no reimplementar en el kata):

- **Tiempo activo:** suma, por `sessionId`, de ventanas con gap ≤ `idle_gap_minutes` entre turnos consecutivos. Cada sesión con al menos un turno tiene piso de 60 segundos para evitar que sesiones cortas registren cero. Ventanas con gap mayor contribuyen cero (refleja tiempo ocioso real).
- **Tiempo de calendario:** `(calendar_end − calendar_start) / 60`, en minutos, con `floor`.

Ambos campos vienen como **minutos enteros**; el renderizador (Paso 6) los convierte a `Xh Ymin`.

### Paso 5: Computar revisores externos vía pr-cost-stamp-reviews.sh

Detecta revisores AI externos (Gemini, Claude bot, CodeRabbit, etc.) a partir de los reviews y comentarios del PR. Solo reviews formales por defecto (los drive-by comments inflan el conteo).

```bash
KNOWN_AI=$(echo "$KNOWN_AI_REVIEWERS_LIST" | paste -sd, -)  # CSV proveniente de .directives
REVIEWS_RAW=$(scripts/pr-cost-stamp-reviews.sh \
  --repo "$OWNER_REPO" \
  --pr   "$PR_NUMBER" \
  ${KNOWN_AI:+--known-ai-reviewers "$KNOWN_AI"})

AI_REVIEWERS=$(echo "$REVIEWS_RAW" | jq -c '.ai_reviewers')
HUMAN_REVIEWERS=$(echo "$REVIEWS_RAW" | jq -c '.human_reviewers')
```

Salida: `{ai_reviewers, human_reviewers, meta}`. Cada revisor tiene `{login, count, first_at, last_at}`. **USD no está disponible** para revisores externos (Gemini/Ultrareview/Cursor no exponen usage por-PR); el renderizador muestra `n/a` en la columna USD.

### Paso 6: Renderizar bloque markdown con subsecciones Development / Review / Total

A partir de los JSONs (`RAW_DEV`, `TIME_DEV`, `TIME_REVIEW`, `REVIEWS_RAW`), armar el bloque siguiente. El comentario de apertura trae `v=2` (versión del schema del bloque); los parsers downstream lo detectan por el atributo.

```markdown
<!-- ahrena:cost-stamp:start v=2 -->
## AI Assistance Cost (Claude Code)

### Development

| Métrica | Valor |
|---|---|
| Sesiones | <sessions_dev> |
| Tokens de input / output | <input_tokens_dev> / <output_tokens_dev> |
| Cache reads / writes | <cache_read_dev> / <cache_create_dev> |
| Costo estimado | $<cost_usd_dev> USD |
| Tiempo activo | <active_time_dev_human> |
| Tiempo de calendario | <calendar_time_human> (<since_date> → <pr_end_date>) |
| Modelos | <model_breakdown_dev> |

### Review

| Fuente | Sesiones / Ocurrencias | USD | Tiempo activo |
|--------|:---------------------:|:---:|:-------------:|
| Claude Code (local, `purpose=review`) | <sessions_review> sessions | $<cost_usd_review> | <active_time_review_human> |
<filas adicionales — una por revisor AI externo del `ai_reviewers` de `pr-cost-stamp-reviews.sh`, USD = `n/a`>

### Total

**Costo AI rastreado: $<cost_total> USD · <active_total_human> activo · <calendar_time_human> calendario**
Actividad externa de AI (sin USD público): <count_external_ai> (<comma-separated logins>)

_Computado por `kata-pr-cost-stamp` el <utc_now>. Ventana: <since_date> → <pr_end_date>. Fuente: ccusage <ccusage_version> + pr-cost-stamp.sh <stamp_version>. Gap de inactividad: <idle_gap_minutes>min._
_Estimaciones basadas en pricing público de Anthropic; la factura real proviene del console. Las fuentes externas de AI sin usage público se listan solo a fines de visibilidad._
<!-- ahrena:cost-stamp:end -->
```

**Omisiones condicionales:**

- Cuando `attribution_mode: project` o `TIME_REVIEW` está vacío/zero, **omitir la fila** "Claude Code (local, `purpose=review`)" — mantener el resto de la subsección Review si hay revisores externos.
- Cuando `ai_reviewers` está vacío Y no hay sesiones `purpose=review`, **omitir la subsección Review entera** (el "Total" referencia solo Development).
- Cuando `meta.warnings` no está vacío, agregar una línea tras el footer:
  `_Avisos: <warning1>; <warning2>._`

**Idempotencia al migrar de `v=1` → `v=2`:** si el body actual contiene `<!-- ahrena:cost-stamp:start -->` (sin atributo `v=`), trátelo como `v=1` y reemplace por el bloque `v=2`. Idempotencia preservada: ejecutar 2x sin nuevos turnos/reviews produce el mismo body.

Reglas de formato:

- Números con separador de miles por locale (`es` usa punto). Para `pt-BR` y `en` aplicar el separador apropiado.
- `cost_usd` con 2 decimales.
- `model_breakdown`: lista de `<model_id> (<percent>%)` ordenada por participación decreciente, separada por coma.
- `<utc_now>`, `<since_date>` y `<pr_end_date>` en ISO 8601 con sufijo `Z` (o fecha simple para `since_date`/`pr_end_date` cuando la hora no aporta contexto).
- **Tiempo humanizado** a partir de minutos enteros:
  - `< 60min` → `"<n>min"` (p. ej., `47min`)
  - `< 24h`  → `"<h>h <m>min"` (p. ej., `2h 47min`); omitir `<m>min` cuando es cero (`3h`)
  - `≥ 24h` → `"<d>d <h>h"` (p. ej., `1d 4h`); omitir `<h>h` cuando es cero (`2d`)
- Si `active_minutes` o `calendar_minutes` es `0`, renderizar `0min`.

### Paso 7: Upsert en el body del PR

1. Obtener body actual:
   ```bash
   CURRENT_BODY=$(gh pr view $PR_NUMBER --json body --jq .body)
   ```
2. Aplicar upsert por marcadores vía Python — sustitución literal segura, sin interpolación de backreferences (`$1`, `\1`, `\n`, etc.) dentro del bloque renderizado. El regex acepta tanto `v=1` como `v=2` para soportar migración in-place:
   ```bash
   echo "$CURRENT_BODY" > /tmp/pr-body.in
   echo "$RENDERED_BLOCK" > /tmp/pr-body.block

   python3 - <<'PY'
   import re, pathlib
   body = pathlib.Path("/tmp/pr-body.in").read_text()
   block = pathlib.Path("/tmp/pr-body.block").read_text().rstrip("\n")
   pattern = re.compile(
       r"<!-- ahrena:cost-stamp:start( v=\d+)? -->.*?<!-- ahrena:cost-stamp:end -->",
       re.DOTALL,
   )
   if pattern.search(body):
       # sustituir bloque existente; lambda fuerza replacement literal
       new_body = pattern.sub(lambda _: block, body)
   else:
       # agregar al final del body separado por línea en blanco
       new_body = body.rstrip("\n") + "\n\n" + block + "\n"
   pathlib.Path("/tmp/pr-body.in").write_text(new_body)
   PY

   NEW_BODY=$(cat /tmp/pr-body.in)
   ```

   Por qué Python y no `awk`/`perl`/`sed`: el `awk` BWK de macOS no pasa variables multilínea; el `s///` de `perl` (sin `e`) interpreta secuencias como `\n` en el replacement; `sed` exige escaping pesado de caracteres especiales. Python con `lambda _: block` en `re.sub` sustituye el bloque literalmente, sin reinterpretar backreferences. Python 3 está presente por defecto en macOS, Linux y en la mayoría de los runners de CI.
3. Actualizar el PR:
   ```bash
   gh pr edit $PR_NUMBER --body "$NEW_BODY"
   ```

### Paso 8: Verificación final

- [ ] `pr_cost_tracking.enabled: true` confirmado en `.directives`
- [ ] `pr_cost_tracking.attribution_mode` leído (default `hook`)
- [ ] Backend de tokens identificado (`ccusage` o fallback) y versión registrada en el bloque
- [ ] En modo `hook`: `scripts/pr-cost-stamp.sh` invocado **dos veces** (`--purpose dev` y `--purpose review`), con `--branch <HEAD_REF>`, `--idle-gap-minutes`, `--calendar-start` y `--calendar-end` poblados
- [ ] `scripts/pr-cost-stamp-reviews.sh` invocado, clasificando `ai_reviewers` y `human_reviewers`
- [ ] `PR_AUTHOR_LOGIN` leído vía `gh pr view --json author`; clasificación de autor-bot aplicada conforme `## Identidad del autor`
- [ ] Subsecciones Development, Review (cuando aplica) y Total presentes en el bloque renderizado
- [ ] Línea `Bot-authored: yes (<login>)` emitida cuando `PR_AUTHOR_IS_BOT` es verdadero
- [ ] Marcadores `<!-- ahrena:cost-stamp:start v=2 -->` / `:end` en líneas propias
- [ ] Body actualizado contiene exactamente una ocurrencia de los marcadores
- [ ] `meta.warnings` (si los hay) anexado al footer del bloque
- [ ] `gh pr view $PR_NUMBER --json body` muestra el bloque visible y formateado

## Identidad del autor

Cuando `warriors_default_author.enabled: true`, los PRs conducidos por warriors llevan la identidad `[bot]` del App como autor en GitHub (conforme `codex-git-workflow` "Identidad del autor"). El stamp reconoce ese escenario para atribuir el trabajo correctamente:

1. **Lectura del autor:** durante el Paso 2 la kata consulta `gh pr view $PR_NUMBER --json author --jq '.author.login'` y lo almacena como `PR_AUTHOR_LOGIN`.
2. **Allow-list de autor-AI:** los built-ins son `ahrena-bot[bot]`, `claude[bot]`, `copilot[bot]`. El proyecto extiende vía `pr_cost_tracking.known_ai_authors` (véase `lex-directives`).
3. **Clasificación:** `PR_AUTHOR_IS_BOT = PR_AUTHOR_LOGIN ∈ (built-ins ∪ pr_cost_tracking.known_ai_authors)`.
4. **Impacto en la renderización (Paso 6 — subsección Development):** cuando `PR_AUTHOR_IS_BOT` es verdadero, el renderizador emite una línea de pie poco antes del cierre del bloque de costo:
   ```
   **Bot-authored: yes (<PR_AUTHOR_LOGIN>)**
   _PR conducido por la identidad warriors-default de Ahrena; los trailers `Co-authored-by:` listan los conductores humanos._
   ```
5. **Impacto en la renderización (Paso 6 — subsección Total):** el texto cambia de "Tracked AI cost" a "Tracked AI cost (PR entero — autor y herramental son AI)" para dejar claro que tanto la implementación como la actividad de revisión son conducidas por AI en ese PR.

Ese reconocimiento es simétrico a `known_ai_reviewers` (Paso 5) y reutiliza el mismo camino de parse en `parse_directives`. El script del stamp (`scripts/pr-cost-stamp.sh`) no depende del autor — el reconocimiento de autor vive a nivel de orquestación de la kata, lo que encaja con el diseño de los warriors Ahrena (Athena/Apollo) que ya consultan `gh pr view` para metadatos del PR.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Bloque de costo | Markdown delimitado por marcadores HTML | Body del PR |
| Mensaje de estado | Texto | Stdout del agente |

## Ejemplo de Ejecución

### Input

```bash
PR_NUMBER=67
# directivas: pr_cost_tracking.enabled: true
```

### Salida esperada (stdout)

```
pr-cost-stamp: backend=ccusage version=1.x project=ahrena since=20260507
pr-cost-stamp: 3 sessions, 245892 input, 18432 output, $4.32 USD
pr-cost-stamp: time backend=pr-cost-stamp.sh 1.1.0 idle_gap=10min
pr-cost-stamp: active 167min (2h 47min), calendar 1680min (1d 4h)
pr-cost-stamp: PR #{N} body updated (block upserted)
```

### Bloque resultante (en el body del PR)

Ver `codex-pr-cost-tracking` → sección "Formato del bloque".

## Restricciones

- **No bloqueante:** cualquier falla (red, parsing, herramienta) emite warning y finaliza con exit 0. El kata nunca aborta `kata-contributing-pr`.
- **Sin hardcode de pricing:** el kata jamás recalcula costo desde tabla propia; usa exclusivamente el resultado de `ccusage` o del fallback.
- **Sin PII en el body:** ningún contenido de sesión (mensajes, código, prompts) se estampa; solo agregados.
- **Idempotencia obligatoria:** una reejecución sin sesiones nuevas produce el mismo body.
- **Respetar directiva:** `pr_cost_tracking.enabled: false` o ausente → el kata es no-op.
- **Tiempo activo es heurística:** depende de `idle_gap_minutes` para separar trabajo engaged de pausas; cross-machine no captura sesiones en otras máquinas; en stacked PRs las ventanas de las capas se superponen. Limitaciones documentadas en `codex-pr-cost-tracking`.

## Referencias

- `codex-pr-cost-tracking` — Manual de referencia (fuente de datos, formato, idempotencia, privacidad)
- `lex-directives` — Lectura obligatoria de `.ahrena/.directives`
- `kata-contributing-pr` — Paso opcional que invoca este kata
- `scripts/pr-cost-stamp.sh` — Fallback Bash cuando `ccusage` no está disponible
- `ccusage` — https://github.com/ryoppippi/ccusage
