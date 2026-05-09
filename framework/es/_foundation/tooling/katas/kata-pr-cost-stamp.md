# Kata: Estampar costo de tokens (Claude Code) en el PR

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Computar tokens consumidos y costo USD de la asistencia IA durante el desarrollo de un PR y estampar el resultado en el body vía `gh pr edit`

## Objetivo

Calcular tokens y costo estimado en USD de las sesiones Claude Code que originaron un Pull Request y grabar un bloque markdown idempotente en el body del PR. Apoya la visibilidad financiera y el baseline de ROI de la automatización por feature, bug o refactor. Es invocada por `kata-contributing-pr` cuando `pr_cost_tracking.enabled: true` en `.ahrena/.directives` y puede correr de manera independiente para actualizar PRs existentes.

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
- [ ] 3. Computar uso vía ccusage (o fallback)
- [ ] 4. Renderizar bloque markdown
- [ ] 5. Upsert en el body del PR
- [ ] 6. Verificación final
```

### Paso 1: Verificar precondiciones y directivas

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Leer `pr_cost_tracking.enabled`. Si es `false` o ausente → finalizar silenciosamente con mensaje `pr-cost-stamp: disabled in directives, skipping`.
3. Verificar disponibilidad de `gh` (autenticado) y `git`. Faltando → finalizar con warning, sin propagar el error.
4. Intentar `npx ccusage@latest --version` (timeout 30s). Éxito → `ccusage` es el backend. Falla → intentar `scripts/pr-cost-stamp.sh --version`. Falla → finalizar con warning `pr-cost-stamp: no backend available, skipping`.

### Paso 2: Resolver contexto del PR

1. `OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)`.
2. `PR_NUMBER` desde el input o desde `gh pr view --json number --jq .number`.
3. `HEAD_REF=$(gh pr view $PR_NUMBER --json headRefName --jq .headRefName)`.
4. `BASE_REF=$(gh pr view $PR_NUMBER --json baseRefName --jq .baseRefName)`.
5. `SINCE_DATE`: fecha del primer commit de la branch en `YYYYMMDD`.
   ```bash
   SINCE_DATE=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cd --date=format:%Y%m%d | head -1)
   ```
6. Resolver el directorio raíz del repositorio principal (no del worktree, cuando aplique):
   ```bash
   MAIN_DIR=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
   ```
   `git rev-parse --git-common-dir` apunta al `.git/` del repositorio principal incluso desde worktrees, garantizando que sesiones registradas en main y en worktrees se agreguen juntas.
7. `PROJECT_BASENAME=$(basename "$MAIN_DIR")` — usado por el fallback (matching por basename del `cwd` en el JSONL).
8. `PROJECT_ID=$(echo "$MAIN_DIR" | tr / -)` — id en formato Claude Code (path con `/` → `-`, prefijo `-`); usado por el filtro `--project=<id>` de `ccusage`.

### Paso 3: Computar uso vía ccusage (o fallback)

**Preferido — `ccusage`:**

```bash
RAW=$(npx --yes ccusage@latest daily \
  --project="$PROJECT_ID" \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null)
```

Notas:
- El subcomando es `daily`. El `session` no acepta `--project`. La forma `--project=<id>` (con `=`) preserva el prefijo `-` del id.
- `--offline` usa la tabla de pricing embebida en `ccusage`; quitar para forzar fetch online cuando online esté disponible y actualizado.
- La salida JSON contiene `daily` (entradas por fecha) y `totals` (agregado), con `modelBreakdowns` por entrada. Para el conteo de sesiones únicas, hacer una llamada complementaria `ccusage session --since "$SINCE_DATE" --json` y filtrar por `cwd` en la línea JSONL.

**Fallback — `scripts/pr-cost-stamp.sh`:**

```bash
RAW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE")
```

Salida JSON con schema equivalente al de `ccusage` (claves `totals`, `breakdown`, `meta`).

### Paso 4: Renderizar bloque markdown

A partir del JSON en `RAW`, armar:

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Métrica | Valor |
|---|---|
| Sesiones | <sessions> |
| Tokens de input | <input_tokens> |
| Tokens de output | <output_tokens> |
| Cache reads | <cache_read_tokens> |
| Cache writes | <cache_create_tokens> |
| Costo estimado | $<cost_usd> USD |
| Modelos | <model_breakdown> |

_Computado por `kata-pr-cost-stamp` el <utc_now>. Ventana: <since_date> → ahora. Fuente: <tool_name> <tool_version>._
_Estimación basada en pricing público de Anthropic; la factura real proviene del console._
<!-- ahrena:cost-stamp:end -->
```

Reglas de formato:

- Números con separador de miles por locale (`es` usa punto). Para `pt-BR` y `en` aplicar el separador apropiado.
- `cost_usd` con 2 decimales.
- `model_breakdown`: lista de `<model_id> (<percent>%)` ordenada por participación decreciente, separada por coma.
- `<utc_now>` en ISO 8601 con sufijo `Z`.

### Paso 5: Upsert en el body del PR

1. Obtener body actual:
   ```bash
   CURRENT_BODY=$(gh pr view $PR_NUMBER --json body --jq .body)
   ```
2. Aplicar upsert por marcadores. Usar `perl` (portable entre macOS/Linux; el `awk` BWK de macOS no maneja bien variables multilínea):
   ```bash
   echo "$CURRENT_BODY" > /tmp/pr-body.in
   echo "$RENDERED_BLOCK" > /tmp/pr-body.block

   if grep -q '<!-- ahrena:cost-stamp:start -->' /tmp/pr-body.in; then
     # sustituir bloque existente
     perl -0777 -i -pe '
       BEGIN { local $/; open(my $fh, "<", "/tmp/pr-body.block") or die; $b = <$fh>; chomp $b; }
       s|<!-- ahrena:cost-stamp:start -->.*?<!-- ahrena:cost-stamp:end -->|$b|s
     ' /tmp/pr-body.in
   else
     # agregar al final del body separado por línea en blanco
     printf "\n\n" >> /tmp/pr-body.in
     cat /tmp/pr-body.block >> /tmp/pr-body.in
   fi

   NEW_BODY=$(cat /tmp/pr-body.in)
   ```
3. Actualizar el PR:
   ```bash
   gh pr edit $PR_NUMBER --body "$NEW_BODY"
   ```

### Paso 6: Verificación final

- [ ] `pr_cost_tracking.enabled: true` confirmado en `.directives`
- [ ] Backend identificado (`ccusage` o fallback) y versión registrada en el bloque
- [ ] JSON de uso obtenido sin error
- [ ] Bloque renderizado contiene marcadores `start`/`end` en líneas propias
- [ ] Body actualizado contiene exactamente una ocurrencia de los marcadores
- [ ] `gh pr view $PR_NUMBER --json body` muestra el bloque visible y formateado

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
pr-cost-stamp: PR #67 body updated (block upserted)
```

### Bloque resultante (en el body del PR)

Ver `codex-pr-cost-tracking` → sección "Formato del bloque".

## Restricciones

- **No bloqueante:** cualquier falla (red, parsing, herramienta) emite warning y finaliza con exit 0. El kata nunca aborta `kata-contributing-pr`.
- **Sin hardcode de pricing:** el kata jamás recalcula costo desde tabla propia; usa exclusivamente el resultado de `ccusage` o del fallback.
- **Sin PII en el body:** ningún contenido de sesión (mensajes, código, prompts) se estampa; solo agregados.
- **Idempotencia obligatoria:** una reejecución sin sesiones nuevas produce el mismo body.
- **Respetar directiva:** `pr_cost_tracking.enabled: false` o ausente → el kata es no-op.

## Referencias

- `codex-pr-cost-tracking` — Manual de referencia (fuente de datos, formato, idempotencia, privacidad)
- `lex-directives` — Lectura obligatoria de `.ahrena/.directives`
- `kata-contributing-pr` — Paso opcional que invoca este kata
- `scripts/pr-cost-stamp.sh` — Fallback Bash cuando `ccusage` no está disponible
- `ccusage` — https://github.com/ryoppippi/ccusage
