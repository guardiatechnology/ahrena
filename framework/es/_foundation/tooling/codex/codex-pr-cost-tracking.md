# Codex: Costo de tokens en Pull Requests (Claude Code)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Cómputo y estampado del costo de asistencia IA (Claude Code) en Pull Requests

## Visión General

Este Codex es la referencia para computar tokens consumidos y costo estimado en USD durante el desarrollo que originó un Pull Request, y estampar esos números en el body del PR. El cómputo parte de los logs JSONL persistidos por Claude Code en `~/.claude/projects/<project-hash>/`, agregados por la herramienta open-source [`ccusage`](https://github.com/ryoppippi/ccusage). El bloque resultante se inserta en el body del PR delimitado por marcadores HTML que garantizan idempotencia. Es consultado por `kata-pr-cost-stamp` (que computa y actualiza el PR) y por `kata-contributing-pr` (que invoca el stamp como paso opcional).

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
| Ventana temporal | `[branch_creation_date, now]` por defecto; override opcional vía `pr_cost_tracking.window_override_days` |

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
| Modelos | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

_Computado por `kata-pr-cost-stamp` el 2026-05-09T01:30:00Z. Ventana: 2026-05-07 → ahora. Fuente: ccusage 1.x._
_Estimación basada en pricing público de Anthropic; la factura real proviene del console._
<!-- ahrena:cost-stamp:end -->
```

Reglas del bloque:

- Marcadores HTML en líneas propias, sin indentación; el regex de upsert depende de eso.
- Encabezado fijo `## AI Assistance Cost (Claude Code)` para discoverability.
- Tabla con columnas idénticas en todas las lenguas; etiquetas traducidas.
- Línea de procedencia (timestamp UTC, ventana, versión de la herramienta) siempre presente.
- Disclaimer de estimación siempre presente.

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
| Stacked PRs con capas superpuestas | Cada capa usa su ventana `[branch_checkout_time, now]`; aceptar imprecisión; el codex lo documenta |
| Variación de pricing entre versiones de `ccusage` | Smoke test de regresión en CI; pinning de versión mínima testada vía `ccusage@<min-version>` |

### Decisiones vigentes

| Aspecto | Decisión |
|---------|----------|
| Backend primario | `ccusage` vía `npx ccusage@latest` |
| Filtro de proyecto | flag nativa `--project <repo-name>` |
| Fallback | `scripts/pr-cost-stamp.sh` con `jq` |
| Adopción | opt-in vía `pr_cost_tracking.enabled` en `.directives` |
| Trigger | paso opcional en `kata-contributing-pr` |
| Idempotencia | marcadores HTML `ahrena:cost-stamp:start/end` |
| Privacidad | sin enmascarado en la primera iteración; flag prevista para después |

## Glosario

| Término | Definición |
|---------|------------|
| Stamp | bloque markdown delimitado por marcadores HTML, insertado en el body del PR por `kata-pr-cost-stamp` |
| Ventana de stamp | intervalo `[branch_creation_date, now]` en el cual las sesiones Claude Code se consideran para el cálculo |
| Cache reads / cache writes | tokens leídos del cache / grabados en el cache prompt de Anthropic; pricing distinto del de los tokens regulares |
| ccusage | CLI open-source que parsea los logs JSONL de Claude Code y calcula costo agregado |
| Upsert | operación que inserta el bloque si no existe o sustituye el existente entre los marcadores |

## Referencias

- `lex-directives` — lectura obligatoria de `.ahrena/.directives` antes de cualquier ejecución
- `kata-pr-cost-stamp` — procedimiento que aplica este Codex
- `kata-contributing-pr` — paso opcional que invoca el stamp
- `ccusage` — https://github.com/ryoppippi/ccusage
- Anthropic pricing — https://www.anthropic.com/pricing
