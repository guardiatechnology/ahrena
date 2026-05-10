# Codex: Costo de tokens y tiempo de implementación en Pull Requests (Claude Code)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Cómputo y estampado del costo de asistencia IA (Claude Code) en Pull Requests — tokens, USD y tiempo de implementación

## Visión General

Este Codex es la referencia para computar tokens consumidos, costo estimado en USD y tiempo de implementación (activo + calendario) durante el desarrollo que originó un Pull Request, y estampar esos números en el body del PR. Tokens y costo provienen de los logs JSONL persistidos por Claude Code en `~/.claude/projects/<project-hash>/`, agregados por la herramienta open-source [`ccusage`](https://github.com/ryoppippi/ccusage). El tiempo proviene de los mismos JSONL (parseados por `scripts/pr-cost-stamp.sh`) — `ccusage` no expone `timestamp` por turno en ningún subcomando, así que el script es la fuente única para los agregados de tiempo. El bloque resultante se inserta en el body del PR delimitado por marcadores HTML que garantizan idempotencia. Es consultado por `kata-pr-cost-stamp` (que computa y actualiza el PR) y por `kata-contributing-pr` (que invoca el stamp como paso opcional).

## Contexto

- **Dominio:** observabilidad financiera de la asistencia IA en Pull Requests del framework Ahrena y de los proyectos consumidores.
- **Audiencia:** agentes de IA que ejecutan `kata-pr-cost-stamp`; mantenedores que revisan costos por PR; tech leads evaluando ROI de la automatización.
- **Actualización:** cuando el formato de salida de `ccusage` cambie de major; cuando la tabla de precios de Anthropic se revise; cuando se añadan nuevas dimensiones (p. ej., por usuario, por epic) al bloque.

## Contenido

### Principios

1. **Opt-in por proyecto.** La funcionalidad está desactivada por defecto. El proyecto declara `pr_cost_tracking.enabled: true` en `.ahrena/.directives` para activarla. No hay Lexis que imponga el uso — el costo es dato interno y cada equipo decide si lo expone.
2. **Fuente única de precio.** La tabla de USD por modelo es la de `ccusage`, que refleja el pricing público de Anthropic. El kata nunca hardcodea valores; una auditoría trimestral confirma que `ccusage` sigue actualizado.
3. **Idempotencia por marcadores HTML.** El bloque está delimitado por `<!-- ahrena:cost-stamp:start -->` y `<!-- ahrena:cost-stamp:end -->`. Reejecutar el kata sobre el mismo PR sustituye el contenido entre los marcadores; nunca duplica.
4. **No bloqueante.** Una falla del stamp (red, herramienta no disponible, parsing) no impide el PR. El kata registra el error y continúa.
5. **Estimación, no factura.** El número exhibido es una estimación basada en pricing público; la factura real proviene del console de Anthropic. El bloque lo declara explícitamente.

### Fuente de datos

| Ítem | Detalle |
|------|---------|
| Ubicación de los logs | `~/.claude/projects/<project-hash>/*.jsonl` |
| Granularidad | una línea JSONL por turno; cada turno trae `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `model`, `cwd`, `sessionId`, `timestamp` |
| Hash del proyecto | derivado por Claude Code a partir del path absoluto del proyecto; `ccusage` traduce el hash de vuelta al nombre del proyecto vía `--project` o `--instances` |
| Ventana temporal de tokens | `[branch_creation_date, now]` por defecto (filtro `--since` en `ccusage`/script) |
| Ventana temporal de calendario | `[branch_creation_date, mergedAt o ahora]` — usa `mergedAt` cuando el PR ya fue mergeado, hora actual UTC cuando aún está abierto |
| Gap de inactividad | `pr_cost_tracking.idle_gap_minutes` (default `10`); separa ventanas activas dentro de una sesión para el cálculo de tiempo activo |

### Herramientas soportadas

| Herramienta | Cuándo usar | Comando base |
|-------------|-------------|--------------|
| `ccusage` (preferida) | Cuando `npx`/`node` estén disponibles | `npx ccusage@latest daily --project=<project-id> --since <YYYYMMDD> --json` |
| `scripts/pr-cost-stamp.sh` (fallback) | Entornos sin Node (p. ej., runners minimalistas) | parsing directo de JSONL con `jq` |

El kata intenta `ccusage` primero. Una falla de ejecución (no de datos) cae al fallback. Una falla del fallback emite warning y prosigue sin stamp.

### Filtro por proyecto

Los subcomandos `daily`, `weekly`, `monthly` y `blocks` de `ccusage` aceptan `--project <id>` y `--instances` (breakdown por proyecto). El `<id>` es el identificador derivado del path absoluto del proyecto, con `/` sustituido por `-` y prefijo `-` (p. ej., `/Users/foo/repo` → `-Users-foo-repo`). Usar la forma `--project=<id>` para preservar el prefijo `-` en la línea de comando.

El subcomando `session` no acepta `--project` y, por eso, no es usado por este Codex.

El kata usa `--project=<id>` como filtro primario; el filtro por `cwd` en la línea JSONL permanece como complemento documentado, útil cuando el usuario trabaja con múltiples clones del mismo repositorio con nombres idénticos.

### Tiempo de implementación

El bloque presenta **dos métricas de tiempo**, siempre juntas cuando `pr_cost_tracking.enabled: true`:

| Métrica | Definición | Fuente de datos |
|---------|------------|-----------------|
| **Tiempo activo** | Suma, por `sessionId`, de ventanas con gap ≤ `idle_gap_minutes` entre turnos consecutivos. Cada sesión con al menos un turno tiene piso de 60s. Aproxima horas de trabajo engaged con la IA. | `timestamp` por turno en los JSONL; agregado por `scripts/pr-cost-stamp.sh` |
| **Tiempo de calendario** | `(branch_creation_time, mergedAt o ahora)` en minutos. Aproxima lead time / throughput. | `git log --reverse <base>..<head> --format=%cI`; `gh pr view --json mergedAt` |

#### ¿Por qué dos números?

- **Tiempo activo** responde "cuánto costó en horas de trabajo engaged". Es la métrica de costo en horas, complementaria al USD.
- **Tiempo de calendario** responde "cuánto la feature estuvo en curso en el reloj". Es métrica de flujo (lead time), no de costo.

Los dos juntos diferencian *concentración* (alto activo, bajo calendario — sprint enfocado) de *dilución* (bajo activo, alto calendario — feature parada esperando review, dependencia, decisión).

#### Cálculo del tiempo activo

Modelo canónico: para cada `sessionId`, ordenar turnos por `timestamp`; sumar `delta` solo cuando `delta ≤ idle_gap_minutes × 60`; ventanas con gap mayor contribuyen cero (reflejan ociosidad real). Sesiones con un único turno reciben piso de 60s para evitar registrar "zero work".

Ejemplo: sesión con turnos en `t=0s, t=30s, t=65s, t=9000s, t=9020s` e `idle_gap_minutes=10` (= 600s):
- 30s ≤ 600 → suma 30s
- 35s ≤ 600 → suma 35s
- 8935s > 600 → suma 0 (intervalo ocioso)
- 20s ≤ 600 → suma 20s
- Total: 85s = 1min (después del piso aplicado por el script).

#### Cálculo del tiempo de calendario

`floor((calendar_end − calendar_start) / 60)` en minutos. `calendar_start` = primer commit de la branch (`git log --reverse <base>..<head> --format=%cI | head -1`); `calendar_end` = `mergedAt` del PR o hora actual en UTC cuando aún está abierto.

#### Backend único

`ccusage` agrega a nivel diario (`daily`), en ventanas de billing de 5h (`blocks`) o por sesión (`session` con `lastActivity`), pero **no expone `timestamp` por turno** en ningún subcomando (validado en `docs/guide/json-output.md`). Por eso, el tiempo siempre se calcula con `scripts/pr-cost-stamp.sh`, incluso cuando `ccusage` es el backend de tokens/USD.

### Formato del bloque

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Métrica | Valor |
|---|---|
| Sesiones | 3 |
| Tokens de input | 245.892 |
| Tokens de output | 18.432 |
| Cache reads | 1.245.888 |
| Cache writes | 89.234 |
| Costo estimado | $4.32 USD |
| Tiempo activo | 2h 47min |
| Tiempo de calendario | 1d 4h (2026-05-04 → 2026-05-05) |
| Modelos | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

_Computado por `kata-pr-cost-stamp` el 2026-05-09T01:30:00Z. Ventana: 2026-05-07 → 2026-05-09. Fuente: ccusage 1.x. Gap de inactividad: 10min._
_Estimaciones basadas en pricing público de Anthropic; la factura real proviene del console._
<!-- ahrena:cost-stamp:end -->
```

Reglas del bloque:

- Marcadores HTML en líneas propias, sin indentación; el regex de upsert depende de eso.
- Encabezado fijo `## AI Assistance Cost (Claude Code)` para discoverability.
- Tabla con columnas idénticas en todas las lenguas; etiquetas traducidas.
- Líneas "Tiempo activo" y "Tiempo de calendario" siempre presentes cuando `enabled: true`.
- Línea de procedencia (timestamp UTC, ventana, versión de la herramienta, gap de inactividad) siempre presente.
- Disclaimer de estimación siempre presente.
- Tiempo formateado a partir de minutos enteros: `< 60min` → `<n>min`; `< 24h` → `<h>h <m>min` (omite `<m>min` cuando es cero); `≥ 24h` → `<d>d <h>h` (omite `<h>h` cuando es cero); `0` → `0min`.

### Idempotencia

El kata aplica upsert mediante los marcadores HTML:

1. Lee el body actual del PR vía `gh pr view --json body`.
2. Busca el rango `<!-- ahrena:cost-stamp:start --> ... <!-- ahrena:cost-stamp:end -->`.
3. Si existe → sustituye el rango por el bloque recién generado.
4. Si no existe → agrega el bloque al final del body, separado por línea en blanco.
5. Actualiza el PR vía `gh pr edit --body`.

Reejecutar el kata 2 veces consecutivas produce exactamente el mismo body si no hubo sesiones nuevas en el intervalo.

### Privacidad

- **Repositorios públicos:** el body del PR es público apenas se abre el PR. El costo absoluto en USD puede ser sensible; cada equipo decide si lo expone. El kata respeta el opt-in del `.directives`; nada se estampa por defecto.
- **Enmascarado opcional:** `pr_cost_tracking.mask_absolute_cost: true` sustituye el valor absoluto por una banda cualitativa (`< $1`, `$1–$10`, `$10–$50`, `> $50`). Configuración aún no implementada en esta primera iteración — declarada para iteración futura.
- **Sin PII:** ningún contenido de la sesión (mensajes, prompts, código) se estampa. Solo agregados numéricos.

### Limitaciones conocidas

| Limitación | Mitigación |
|------------|------------|
| Sesiones cross-machine no capturadas (solo la máquina donde corre el kata cuenta) | El Codex lo documenta; agregación cross-machine queda fuera de alcance en esta iteración |
| Ventana heurística `[branch_creation_date, now]` incluye sesiones off-topic en el mismo proyecto | El filtro `--project` reduce; `cwd` complementa; iteración futura puede usar `sessionId` rastreado por hooks |
| Stacked PRs con capas superpuestas — suma del tiempo activo de las capas > tiempo activo real | Cada capa usa su ventana `[branch_checkout_time, mergedAt o ahora]`; aceptar imprecisión; el codex lo documenta |
| Variación de pricing entre versiones de `ccusage` | Smoke test de regresión en CI; pinning de versión mínima testada vía `ccusage@<min-version>` |
| `idle_gap_minutes` mal calibrado distorsiona el tiempo activo | Default 10min cubre la mayoría de los flujos; configurable por proyecto; el valor efectivo se muestra en la línea de procedencia del bloque |
| Tiempo activo ≠ tiempo de lectura/edición manual | La métrica refleja la cadencia de turnos con la IA, no trabajo 100% humano antes/después; documentar como "horas de asistencia IA", no "horas totales de feature" |
| `BRANCH_FIRST_COMMIT_ISO` cae a `date -u` cuando la branch aún no tiene commits sobre el base | Fallback intencional del kata (Paso 2) para que el script nunca reciba una cadena vacía. Resultado: el tiempo de calendario aparece como una ventana mínima recién abierta, sin señal de que el límite fue sintético. Aceptar hasta que la branch acumule commits y el stamp se re-ejecute |

### Decisiones vigentes

| Aspecto | Decisión |
|---------|----------|
| Backend de tokens/USD | `ccusage` vía `npx ccusage@latest` (con fallback a `scripts/pr-cost-stamp.sh`) |
| Backend de tiempo (activo + calendario) | `scripts/pr-cost-stamp.sh` siempre — `ccusage` no expone `timestamp` por turno |
| Filtro de proyecto | flag nativa `--project=<id>` en `ccusage`; basename del `cwd` en el fallback |
| Adopción | opt-in vía `pr_cost_tracking.enabled` en `.directives` |
| `idle_gap_minutes` | sub-flag en `.directives`; default `10` |
| Trigger | paso opcional en `kata-contributing-pr` |
| Idempotencia | marcadores HTML `ahrena:cost-stamp:start/end` |
| Privacidad | sin enmascarado en la primera iteración; flag prevista para después |

## Glosario

| Término | Definición |
|---------|------------|
| Stamp | bloque markdown delimitado por marcadores HTML, insertado en el body del PR por `kata-pr-cost-stamp` |
| Ventana de stamp | intervalo `[branch_creation_date, mergedAt o ahora]` en el cual las sesiones Claude Code se consideran para el cálculo |
| Tiempo activo | suma de ventanas con gap ≤ `idle_gap_minutes` entre turnos consecutivos por `sessionId`; aproxima horas de trabajo engaged con la IA |
| Tiempo de calendario | duración corrida `[branch_creation_date, mergedAt o ahora]`; aproxima lead time / throughput |
| `idle_gap_minutes` | gap (en minutos) que separa ventanas activas dentro de una sesión; default 10, configurable en `.directives` |
| Cache reads / cache writes | tokens leídos del cache / grabados en el cache prompt de Anthropic; pricing distinto del de los tokens regulares |
| ccusage | CLI open-source que parsea los logs JSONL de Claude Code y calcula costo agregado |
| Upsert | operación que inserta el bloque si no existe o sustituye el existente entre los marcadores |

## Referencias

- `lex-directives` — lectura obligatoria de `.ahrena/.directives` antes de cualquier ejecución
- `kata-pr-cost-stamp` — procedimiento que aplica este Codex
- `kata-contributing-pr` — paso opcional que invoca el stamp
- `ccusage` — https://github.com/ryoppippi/ccusage
- Anthropic pricing — https://www.anthropic.com/pricing
