# Kata: Instrumentar Observability en PoV

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): instrumentación de telemetría nativa en el PoV — traces, prompts log, tool calls log, métricas de valor

## Objetivo

Producir `docs/{context}/agents-pov/observability/` con 4 archivos canónicos (`traces-spec.md`, `prompts-log.md`, `tool-calls-log.md`, `value-metrics.md`) declarando el **contrato** de observability del PoV: qué spans, qué campos de log, qué métricas leading. Observability es **ciudadana de primera clase** en el PoV — sin instrumentación, no hay base para la Directriz 06 (contexto rico para retrofit) ni para la DoOC ítem 5 (observability data ≥ 7 días). Aplica `lex-observability-required` en el rigor pre-operacional: 1 trace + 1 métrica + structured log son suficientes.

## Cuándo Usar

- Después de `kata-pov-tools-select` (tools son input para `tool-calls-log.md`)
- En paralelo con `kata-pov-feedback-attach` (value-metrics conversan con criterio de feedback)
- Cuando una operación del PoV revela una métrica leading nueva a rastrear

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `docs/{context}/agents-pov/overview.md` | Sí | Define value metric leading |
| `docs/{context}/agents-pov/tools.md` | Sí | Lista de tools para los logs |
| `lex-observability-required` | Sí | Rigor mínimo (trace + métrica + log) |
| `lex-data-retention` | Sí | Restricciones de PII en logs |

## Workflow

```
Progreso:
- [ ] 1. Definir spans (traces-spec.md)
- [ ] 2. Definir schema de prompts log (sin PII)
- [ ] 3. Definir schema de tool calls log
- [ ] 4. Definir métricas leading (value-metrics.md)
- [ ] 5. Cross-link con lex-observability-required (rigor mínimo)
- [ ] 6. Persistir observability/
```

### Paso 1: Definir spans (traces-spec.md)

Estructura canónica (compatible con OpenTelemetry, **mismo schema que Mêtis adoptará** — facilita la puente):

```yaml
# traces-spec.md (extracto)

spans:
  - name: agent.turn
    attributes:
      - agent.name: <pov-name>
      - agent.stage: pre-operational
      - session_id: <opaque>
      - turn_index: <int>
      - input_tokens: <int>
      - output_tokens: <int>
      - latency_ms: <int>
      - outcome: success | error | refusal

  - name: agent.tool_call
    parent: agent.turn
    attributes:
      - tool.name: <web_search | code_execution | ...>
      - tool.duration_ms: <int>
      - tool.outcome: success | error | timeout
      - tool.error_class: <if outcome=error>
```

Cada PoV declara explícitamente qué spans emite. Mínimo: `agent.turn`. Recomendado cuando hay tools: `agent.turn` + `agent.tool_call`.

### Paso 2: Definir schema de prompts log (sin PII)

```yaml
# prompts-log.md (extracto)

fields:
  - session_id: opaque, hashed
  - turn_index: int
  - prompt_hash: sha256(user_input)   # NO almacena texto bruto
  - prompt_token_count: int
  - context_size_tokens: int
  - timestamp: ISO 8601

excluded:
  - user_input (texto bruto)
  - PII (CPF, CNPJ, email, nombre completo)

retention:
  - 30 días para PoV activo
  - destruir al cerrar el PoV
```

El schema vive en `lex-data-retention` por default; si el PoV justifica retención mayor, se registra en `value-proof.md` con motivo. Aplicar `lex-data-retention` es responsabilidad de este kata.

### Paso 3: Definir schema de tool calls log

```yaml
# tool-calls-log.md (extracto)

fields:
  - session_id: opaque, hashed
  - turn_index: int
  - tool_name: enum [web_search | code_execution | str_replace_editor | bash]
  - parameters_hash: sha256(parameters)   # NO almacena parámetros brutos
  - parameters_size_bytes: int
  - duration_ms: int
  - outcome: success | error | timeout
  - error_class: string | null
  - result_size_bytes: int   # NO el contenido

excluded:
  - parámetros brutos (especialmente si contienen datos del cliente)
  - result content

retention:
  - 30 días para PoV activo
```

### Paso 4: Definir métricas leading (value-metrics.md)

Métricas leading **operacionales** que el PoV debe rastrear continuamente:

```markdown
# value-metrics.md (extracto)

## Métrica primaria

- nombre: reconciliation_auto_rate
- definición: turns donde la respuesta generó pareo con confianza ≥ alta / total turns
- frecuencia: por sesión y agregada por día
- ventana: rolling 7 días
- threshold de descontinuación: < 30% tras 4 semanas

## Métricas de calidad

- nombre: refusal_rate
  - definición: turns con outcome=refusal / total turns
  - alarma: > 10% indica prompt mal calibrado
- nombre: avg_latency_ms
  - definición: p95 latencia por turn
  - alarma: > 5000ms indica tool con timeout
```

### Paso 5: Cross-link con lex-observability-required

Al final de `traces-spec.md`, se añade sección `## Conformidad con lex-observability-required`:

| Requisito | Cómo el PoV lo atiende |
|---|---|
| 1 trace por unidad de trabajo | `agent.turn` span emitido por turn |
| 1 métrica leading | `reconciliation_auto_rate` (ver value-metrics.md) |
| Structured logging con PII redacted | prompt_hash + parameters_hash (nunca raw) |
| Ventana ≥ 7 días para DoOC | retention 30 días declarada |

### Paso 6: Persistir observability/

Se crea el directorio `docs/{context}/agents-pov/observability/` con:

- `traces-spec.md`
- `prompts-log.md`
- `tool-calls-log.md`
- `value-metrics.md`

Se añade `README.md` corto listando los 4 archivos y el propósito del directorio.

### Validación Final

- [ ] 4 archivos presentes en `observability/`
- [ ] `agent.stage: pre-operational` aparece en `traces-spec.md`
- [ ] Logs declaran **hash** de prompt/parameters, nunca el texto bruto
- [ ] `value-metrics.md` tiene 1 métrica primaria con threshold de descontinuación
- [ ] Cross-link `lex-observability-required` presente

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `observability/traces-spec.md` | Markdown + YAML | `docs/{context}/agents-pov/observability/` |
| `observability/prompts-log.md` | Markdown + YAML | idem |
| `observability/tool-calls-log.md` | Markdown + YAML | idem |
| `observability/value-metrics.md` | Markdown | idem |
| `observability/README.md` | Markdown | idem |

## Restricciones

- **Nunca** almacenar texto bruto de prompt o de parámetros de tool — siempre hash.
- **Nunca** ausencia de métrica leading — sin métrica, `kata-pov-value-track` no puede operar.
- **Nunca** retención indefinida en PoV — límite máximo es 90 días e incluso eso requiere justificación.
- **Siempre** el schema es el mismo que Mêtis (plan-032) consumirá vía `--from-pov`. Divergencia aquí quiebra la puente.

---

**Modelo:** Este Kata trata observability como ciudadana de primera clase en PoV. El contrato declarado aquí es la puente para `kata-dooc-validate` ítem 5.
