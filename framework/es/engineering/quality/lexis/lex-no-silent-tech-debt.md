# Lexis: Sin Deuda Técnica Silenciosa

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Comentarios y secciones dejadas en código o documentación durante la ejecución de un Plan activo

## Propósito

Los comentarios `# TODO`, `# FIXME`, `# XXX`, `# follow-up`, `# later`, `# revisit` y las secciones de documentación del tipo `## TODO`, `## Follow-up`, `## Out of scope (to revisit)` son marcadores de deuda técnica silenciosa: registran que algo quedó para después, pero no conectan ese "después" a una Issue o Plan rastreable. El resultado es entropía: la deuda se acumula, nadie es responsable y el usuario lo descubre semanas después cuando la deuda se convierte en incidente.

El framework Ahrena trata cada hallazgo tangencial como **decisión deliberada**: el agente PAUSA, lo lleva al humano y ofrece tres caminos explícitos — expandir el Plan actual, abrir un Plan nuevo bajo el mismo parent Issue, o abrir una Issue nueva de capability. Ninguno de esos caminos es "dejar un TODO".

## Ley

> **Durante la ejecución de un Plan activo (status `development`), commitear código con comentarios `# TODO`, `// TODO`, `# FIXME`, `# XXX`, `# follow-up`, `# later`, `# revisit` (o variantes equivalentes en otros lenguajes) O commitear documentación con secciones `## TODO`, `## Follow-up`, `## Out of scope (to revisit)`, sin que esos marcadores referencien una Issue o Plan rastreable (formato `# TODO(#NNN): ...` o equivalente), está FORBIDDEN. Los hallazgos tangenciales identificados durante la ejecución DEBEN ser surfaceados al humano con tres opciones explícitas: (a) expandir el alcance del Plan actual, (b) abrir un Plan sub-issue nuevo bajo el mismo parent Issue, (c) abrir una Issue parent nueva de capability.**

## Alcance

- **Aplica a:** todo código de aplicación (Python, TypeScript/JavaScript, Go, Swift, Kotlin, Dart) y toda documentación (Markdown bajo `docs/`, `README.md`, comentarios estructurados en código) commiteada vía un Plan en `status: development`
- **Agentes vinculados:** `warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-claudionor`, y cualquier warrior que ejecute código durante un Plan activo
- **Excepciones declaradas:** (i) comentarios `# WHY: ...` que explican decisión no obvia (lineage, no deuda); (ii) `pytest.mark.xfail(reason="bug:#N")` con número de Issue rastreable; (iii) bloques `<!-- not-flushed -->` en provider cache (`.claude/plans/`, `.cursor/plans/`) — scratch transitorio, no canónico

## Aplicabilidad Prospectiva

Esta Lex aplica prospectivamente: los comentarios `# TODO`/`# FIXME`/`# follow-up` existentes en código histórico de proyectos que adoptaron Ahrena antes de esta Lex **no** se bloquean retroactivamente. El lint detecta solo marcadores añadidos o modificados en el diff del PR actual. La migración de deuda histórica es trabajo de un Plan dedicado, surfaceado cuando sea relevante para el alcance del Plan actual.

<HARD-GATE>
Todo agente NO DEBE commitear código o documentación que contenga
marcadores `# TODO`, `// TODO`, `# FIXME`, `# XXX`, `# follow-up`,
`# later`, `# revisit`, `## TODO`, `## Follow-up`, `## Out of scope`
sin referencia a una Issue o Plan rastreable.

Precondiciones obligatorias para commitear tales marcadores:
  (a) El marcador referencia una Issue/Plan rastreable (ej: `# TODO(#NNN): descripción`)
  (b) O el hallazgo fue surfaceado al humano con 3 opciones explícitas (expandir Plan, abrir Plan nuevo, abrir Issue nueva)
  (c) Y el humano confirmó la decisión por escrito (respuesta en la sesión o comment en la Issue)

Esta regla se aplica a TODO Plan en `status: development`, independientemente de:
  - "es solo una línea"
  - "el usuario no lo pidió pero lo necesitará"
  - "es deuda técnica, no feature"
  - "es solo un comentario, nadie lee TODOs"

Excepciones declaradas (no silenciosas):
  - Comentarios `# WHY: ...` explicando una decisión no obvia (lineage)
  - `pytest.mark.xfail(reason="bug:#N")` con Issue number rastreable
  - Bloques `<!-- not-flushed -->` en provider cache de plan
  - Marcadores preexistentes en código histórico, fuera del diff del PR actual
</HARD-GATE>

## Protocolo de Hallazgo Tangencial

Al identificar un hallazgo fuera del alcance declarado del Plan actual durante la ejecución, el agente DEBE:

1. PAUSAR la implementación actual
2. Presentar al humano: descripción del hallazgo, alcance afectado, costo estimado de tratarlo ahora vs. después
3. Ofrecer tres opciones discretas:
   - **(a) Expandir el Plan actual** — si es trivial y directamente relacionado con el alcance corriente; requiere actualizar el cuerpo de la sub-issue Plan
   - **(b) Abrir un nuevo Plan sub-issue** — si es material pero separable, aún bajo el mismo parent Issue (User Story / Bug / Tech Task)
   - **(c) Abrir una nueva Issue parent** — si constituye una capability nueva, no derivada del parent Issue actual
4. Registrar la decisión del humano en la Issue/Plan correspondiente antes de retomar
5. Nunca aceptar implícitamente un TODO silencioso

## Ejemplos

### Correcto

```python
# WHY: integer arithmetic on cents avoids floating-point error in money math
fee_cents = int(amount_cents * Decimal("0.015"))

# TODO(#172): switch to bank-specific fee table once spec arrives
return fee_cents
```

```python
@pytest.mark.xfail(reason="bug:#185 — race condition in retry path")
def test_concurrent_retries(): ...
```

### Incorrecto

```python
# TODO: handle edge case later                    # FORBIDDEN — sin #N rastreable
def parse_value(raw: str) -> int:
    return int(raw)

# FIXME: this is broken for negative numbers      # FORBIDDEN — silencioso
def calc(x): return x * 2

# XXX: refactor when we have time                 # FORBIDDEN — silencioso
```

```markdown
## Out of scope (to revisit)                      <!-- FORBIDDEN — sin Issue/Plan -->
- Migration of legacy plans under docs/
- Cleanup of orphan worktrees
```

## Validación Automatizada

- **Herramienta:** ripgrep pre-commit hook ejecutando `rg -n '(^|\s)(# |// |## )(TODO|FIXME|XXX|follow-up|later|revisit)(?!\(#\d+\))'` en el diff staged; extensión de `kata-quality-gate` (Check 4 o check nuevo) que aplica el mismo patrón al diff del PR
- **Momento:** pre-commit local + Gate 2 del flujo Issue-Driven en todo PR
- **Métrica:** 0 marcadores de deuda silenciosa añadidos/modificados en el diff del PR; 100% de los hallazgos tangenciales durante la ejecución surfaceados al humano con 3 opciones explícitas
