# Kata: Iniciar una Sesión de Revisión de PR (con `purpose=review` en el sello de costo)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Iniciar una sesión Claude Code para revisar una Pull Request, garantizando que los turnos se contabilicen en la subsección `Review` del sello de costo (`kata-pr-cost-stamp`)

## Objetivo

Garantizar que toda sesión Claude Code dedicada a revisar una PR sea marcada explícitamente con `purpose=review`, para que el agregador (`scripts/pr-cost-stamp.sh --purpose review`) pueda separar el costo de **desarrollo** del costo de **revisión** cuando `kata-pr-cost-stamp` selle la PR. Sin esa marca, los turnos de revisión caen en el balde `dev` y contaminan la lectura del esfuerzo que produjo la PR.

Este Kata es un wrapper instructivo fino: el trabajo de revisión real lo hace `/review` (o un prompt equivalente). El Kata existe para hacer la etiqueta `purpose=review` descubrible y consistente.

## Cuándo Usar

- El usuario desea revisar una PR con Claude Code y el proyecto tiene `pr_cost_tracking.enabled: true`.
- El usuario quiere hacer dogfood del sello: medir el costo de revisión de la propia PR antes del merge.
- Invocado por `cry-pr-review`.

## Entradas

| Entrada | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| Número de PR | Sí | `$PR_NUMBER` en el repositorio actual |
| Repositorio | No | `owner/repo`; por defecto: `gh repo view --json nameWithOwner` |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Verificar precondiciones
- [ ] 2. Marcar la sesión como purpose=review
- [ ] 3. Disparar la revisión
- [ ] 4. Verificación final
```

### Paso 1: Verificar precondiciones

1. Leer `.ahrena/.directives` (`lex-directives`).
2. Confirmar `pr_cost_tracking.enabled: true`. Si está deshabilitado, el Kata informa que el sello no diferenciará dev vs. review y prosigue de todas formas (la revisión sigue funcionando; solo no se contabiliza).
3. Confirmar `pr_cost_tracking.attribution_mode: hook` (valor por defecto cuando se omite). Si es `project`, el Kata avisa que el legado no separa por `purpose` y prosigue.
4. Verificar que el hook `pr-cost-attribution.sh` esté instalado en `.claude/hooks/` y conectado en `.claude/settings.json` (instalado por `scripts/install.py` cuando el sello está habilitado).

### Paso 2: Marcar la sesión como purpose=review

Hay tres caminos soportados — elija el que corresponda. El camino A (variable de entorno) es el oficial y elimina la dependencia de la heurística:

**A) Variable de entorno — recomendado.** Inicie la sesión Claude Code con la variable definida:

```bash
GUARDIA_PURPOSE=review claude
```

o, si Claude Code ya está abierto, expórtela antes del próximo turno:

```bash
export GUARDIA_PURPOSE=review
```

El hook lee esta variable y escribe `purpose=review` en el sidecar para todos los turnos siguientes.

**B) Convención textual (heurística del hook).** Cuando la variable no está definida, el hook inspecciona la primera línea del prompt. Inicie la sesión de revisión con un prompt que coincida con la lista canónica:

| Patrón (case-insensitive) | Idioma | Ejemplo |
|---|---|---|
| `^/review` | en | `/review PR #72` |
| `^review pr` | en | `review PR #72` |
| `^review #N` | en | `review #72` |
| `^revise pr` | en | `revise PR #72` |
| `^revisar pr` | pt-BR | `revisar PR #72` |
| `^revisão de pr` | pt-BR | `revisão de PR #72` |
| `^revisión de pr` | es | `revisión de PR #72` |
| `pull request review` (en cualquier posición de la primera línea) | en | `let's do a pull request review` |

La heurística decide turno a turno — no persiste entre turnos. Ante la duda, prefiera el camino A.

**C) Combinado.** Use ambos: la variable como contrato y el prompt iniciado con `/review` como hábito. La primera regla que coincide gana (la variable de entorno gana siempre que está presente).

### Paso 3: Disparar la revisión

1. Con la sesión correctamente marcada, invoque el slash command oficial de Claude Code:
   ```
   /review #<PR_NUMBER>
   ```
   o conduzca la revisión por prompt normal — lo que importa para el sello es la marca `purpose`, no la forma de la revisión.
2. Conduzca el ciclo de revisión (lectura del diff, comentarios, sugerencias, follow-ups) como de costumbre.

### Paso 4: Verificación final

- [ ] Sesión iniciada con `GUARDIA_PURPOSE=review` exportada **o** primer prompt en la lista canónica
- [ ] El hook escribió al menos una línea en `~/.claude/projects/<hash>/branches.jsonl` con `purpose: "review"` (verificable con `tail -1` en el archivo)
- [ ] Cuando `kata-pr-cost-stamp` se ejecute, el bloque de la PR mostrará la subsección **Review → Claude Code (local, `purpose=review`)** con el conteo de sesiones correspondiente.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Sidecar marcado | Líneas JSONL con `purpose: "review"` | `~/.claude/projects/<hash>/branches.jsonl` |
| Revisión de la PR | Comentarios, sugerencias, conversaciones | PR objetivo |

## Ejemplo de Ejecución

```bash
# Recomendado: definir la variable antes de la sesión
$ GUARDIA_PURPOSE=review claude
# Dentro de la sesión:
> /review PR #72

# Verificar (en otra shell):
$ tail -1 ~/.claude/projects/-Users-fulano-proyectos-ahrena/branches.jsonl
{"ts":"...","session_id":"...","purpose":"review", ...}
```

## Restricciones

- **Sin efecto cuando el sello está deshabilitado:** si `pr_cost_tracking.enabled: false`, el Kata orienta la marcación de todos modos (costo cero), pero no habrá sello para reportarla.
- **No reemplaza al revisor humano:** la revisión por agente es una capa complementaria; CODEOWNERS y políticas de PR siguen aplicando (`lex-pr-quality`).
- **Sin costo público para revisores externos:** si la revisión la hace otro agente AI (Gemini, Cursor, Ultrareview), `kata-pr-review` no cubre — esa ruta la detecta automáticamente `pr-cost-stamp-reviews.sh` a partir de los comentarios de la PR.

## Referencias

- `codex-pr-cost-tracking` — Manual con la cascada de detección de `purpose` y el formato del bloque con la subsección `Review`
- `kata-pr-cost-stamp` — Sella el resultado en la PR consumiendo el sidecar
- `cry-pr-review` — Atajo que invoca este Kata
- `framework/templates/claude-code-hooks/pr-cost-attribution.sh` — Implementación del hook
- `lex-pr-quality` — Política de calidad de PR
