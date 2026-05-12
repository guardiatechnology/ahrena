# Kata: Design del Context Pack (con Puente `--from-pov`)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents: design del context pack (`context-pack.md`) del agent en `operational-concrete`, incluyendo el puente canónico que consume salida de `warrior-claudionor` (PoV → Operación Concreta)

## Objetivo

Producir el context pack del agent — few-shot positivos (mínimo 5 en producción, > que en el PoV), ejemplos negativos curados (mínimo 10), histórico observado de los últimos 30-90 días cuando aplicable. Cubre rigurosamente la **Directriz 06 — Contexto Rico** de `lex-agent-construction-directives`.

Este Kata implementa el **puente canónico `--from-pov`**: cuando el agent viene con `entry_mode: with-pov`, lee `docs/{context}/agents-pov/{pov-agent}/` (output de `warrior-claudionor`) y enriquece el context pack con:

- Few-shot positivos derivados de inputs reales experimentados en el PoV
- Ejemplos negativos curados a partir de fallas observadas en el PoV (anti-patrones reales, no inventados)
- Snippets de telemetría del PoV (traces típicos, edge cases observados)

## Cuándo Usar

- Tras `kata-agent-feedback-design` (context pack referencia métricas y thresholds)
- Cuando el agent recibe nuevo material de entrenamiento (re-curaduría periódica)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `context` | Sí | Bounded Context |
| `agent` | Sí | Slug del agent |
| `overview_path` | Sí | `docs/{context}/agents/{agent}/overview.md` |
| `--from-pov <path>` | No | `docs/{context}/agents-pov/{pov-agent}/` (output de `warrior-claudionor`) |
| `--retrain-cadence` | No | `weekly` \| `monthly` \| `quarterly` (default: `quarterly`) |

## Contrato de input `--from-pov`

Cuando el flag `--from-pov` es proporcionado, el Kata espera los siguientes archivos en el path indicado (todos producidos por katas POV de `warrior-claudionor`):

| Archivo | Producido por | Contenido consumido |
|---------|---------------|---------------------|
| `pov.md` | `kata-pov-scope-define` | Caso de uso primario (para confirmar alineación) |
| `scope.md` | `kata-pov-scope-define` | Fuera de alcance (para validar negativos) |
| `system-prompt.md` | `kata-pov-system-prompt` | Identidad pre-operacional (referencia) |
| `tools.md` | `kata-pov-tools-select` | Tools experimentadas en el PoV |
| `context-pack.md` | `kata-pov-context-curate` | **Few-shot positivos + anti-patrones — fuente primaria del enrichment** |
| `feedback.md` | `kata-pov-feedback-attach` | Métrica de valor + pivot trigger |
| `value-proof.md` | `kata-pov-value-track` | Leading metric probada, decisión `ready_for_dooc` (token canónico machine-readable, language-invariant) |
| `observability/value-metrics.md` | `kata-pov-observability-instrument` | Métricas operacionales observadas |
| `observability/prompts-log.md` | `kata-pov-observability-instrument` | Edge cases identificados en producción (referencias, sin PII) |
| `observability/tool-calls-log.md` | `kata-pov-observability-instrument` | Patrones de uso de tools |
| `observability/traces-spec.md` | `kata-pov-observability-instrument` | Snippets de traces típicos |
| `implementation/skill.md` o `subagent.md` | `kata-skill-implement` o `kata-agent-author` | Referencia de la implementación ejecutada en el PoV |

**Pressupuesto de PII redaction:** el Kata confía en que `kata-pov-value-track::Paso 4` aplicó el gate de PII grep antes de marcar `ready_for_dooc` (registrado en `value-proof.md`). No revalida PII en el input; documenta en la sección `Validación de input en frontera` el trust boundary.

Si el PoV aún **no está** `ready_for_dooc` en `value-proof.md`, el Kata aborta con error claro — context pack basado en PoV inmaduro viola el espíritu de la DoOC.

## Workflow

```
Progreso:
- [ ] 1. Validar input --from-pov (cuando aplicable)
- [ ] 2. Curar ≥ 5 few-shot positivos
- [ ] 3. Curar ≥ 10 ejemplos negativos
- [ ] 4. Seleccionar snippets de telemetría (30-90 días)
- [ ] 5. Declarar política de re-curaduría
- [ ] 6. Validación final
```

### Paso 1: Validar input `--from-pov` (cuando aplicable)

1. Si `--from-pov` proporcionado:
   - Verifica que `pov_path/value-proof.md::status == ready_for_dooc`. Falla si diferente
   - Verifica que `pov_path/context-pack.md` existe (es la fuente primaria)
   - Verifica que `pov_path/observability/` contiene los 4 archivos esperados
2. Si `--from-pov` ausente:
   - En `entry_mode: direct-entry`, registra modo `cold-start`: few-shot necesitarán ser sintetizados a partir del dominio (sin inputs reales); marca obligación de re-curaduría tras los primeros 7 días de producción vía runbook automatizado

### Paso 2: Curar ≥ 5 few-shot positivos

Source de prioridad (en orden):

1. **PoV `context-pack.md`** (cuando `with-pov`) — copia/refina los ejemplos que probaron acierto consistente
2. **PoV `observability/prompts-log.md`** (sample real del uso pre-operacional, anonimizado)
3. **Dominio** (cuando `direct-entry`/`cold-start`) — sintetiza a partir de `docs/{context}/entities/` + `docs/{context}/features/`

Cada few-shot DEBE contener:

```markdown
### Ejemplo positivo #{N}: {nombre corto}

**Escenario:** {1-2 frases sobre el contexto}

**Input (sanitizado):**
```
{input del usuario, con PII redacted}
```

**Pensamiento esperado:**
```
{thought process — para patrones react/reflexion}
```

**Tools invocadas:**
- `{tool-name}` con input `{}`

**Output esperado:**
```
{output canónico, conforme schema declarado en system-prompt.md::Bloque 4}
```

**Origen:** PoV {agent-pov-slug} | sintético derivado de {entity}
```

### Paso 3: Curar ≥ 10 ejemplos negativos

Ejemplos negativos = anti-patrones. **Mínimo 10** en producción (vs. ≥ 2 en el PoV — rigor diferencial). Categorías obligatorias:

| Categoría | Mínimo | Source |
|-----------|--------|--------|
| Out-of-scope (input fuera del alcance del agent) | 2 | scope.md del PoV + síntesis |
| Ambigüedad no resuelta (necesita pedir aclaración, no adivinar) | 2 | observability del PoV |
| PII leakage (agent NO DEBE revelar PII en determinado contexto) | 2 | guardrails |
| Prompt injection (input adversarial intenta override system prompt) | 2 | `kata-system-prompt-adversarial-validate` outputs |
| Tool injection (input pide tool fuera del catálogo) | 1 | guardrails |
| Cross-tenant boundary (input pide datos de otro `org_id`) | 1 | guardrails |

Cada ejemplo negativo:

```markdown
### Ejemplo negativo #{N}: {nombre corto}

**Categoría:** out-of-scope | ambiguity | pii-leakage | prompt-injection | tool-injection | cross-tenant

**Input (adversarial o edge case):**
```
{input}
```

**Comportamiento INCORRECTO:**
```
{lo que el agent NO DEBE hacer — y por qué}
```

**Comportamiento CORRECTO:**
```
{recusa estructurada con código de error per lex-error-handling | escalamiento vía escalation.md | pedido de aclaración}
```

**Origen:** PoV observability | guardrails | adversarial suite
```

### Paso 4: Seleccionar snippets de telemetría

Cuando `with-pov`, incluye:

1. Trace típico (`agent.turn` + `agent.tool_call` para un caso fácil) — sanitizado
2. Trace de edge case (caso medio con ambigüedad resuelta) — sanitizado
3. Distribución de outcomes observada en el PoV (% éxito, % escalado, % rechazado)

Snippets DEBEN ser hash-only para cualquier PII residual.

En `direct-entry`/`cold-start`, omite esta sección; marca obligación de añadir tras 30 días de producción (re-curaduría).

### Paso 5: Declarar política de re-curaduría

```markdown
## Política de re-curaduría

- **Cadencia:** {weekly | monthly | quarterly} — default quarterly
- **Trigger automático:** pivot trigger disparado en `feedback.md`
- **Owner:** {owner del agent declarado en overview.md}
- **Proceso:** invocar `kata-agent-context-pack-design --refresh` con snapshot de la telemetría más reciente
- **Versionado:** cambios en `context-pack.md` registrados en `Apéndice — Versiones` con fecha + PR ref
```

### Validación Final

- [ ] ≥ 5 few-shot positivos con schema completo
- [ ] ≥ 10 ejemplos negativos cubriendo las 6 categorías obligatorias (mínimos por categoría)
- [ ] En `with-pov`, fuente de cada ejemplo declarada (PoV path o síntesis)
- [ ] Snippets de telemetría sanitizados cuando `with-pov`
- [ ] Política de re-curaduría declarada con cadencia + owner
- [ ] PII redaction confirmada en el input (trust boundary documentado para `with-pov`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `context-pack.md` | Markdown | `docs/{context}/agents/{agent}/context-pack.md` |

## Estructura del archivo `context-pack.md`

```markdown
# Context Pack — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **Source:** {with-pov: docs/{context}/agents-pov/{pov-agent}/} | {direct-entry: synthesized from domain}
> **Re-curation cadence:** {cadence}
> **Last refresh:** {ISO 8601}

## Validación de input en frontera

- **PII trust boundary:** confiamos en el gate de PII grep aplicado por `kata-pov-value-track::Paso 4` en el PoV de origen (cuando `with-pov`). Este Kata no revalida PII; asume `pov_path/value-proof.md::status == ready_for_dooc` como prueba de aprobación del gate
- **Source attribution:** cada ejemplo declara origen (PoV path | sintético)
- **Versionado:** cambios pasan por `kata-system-prompt-adversarial-validate` cuando alteren negativos relacionados a prompt injection

## Few-shot positivos (≥ 5)

(secciones `### Ejemplo positivo #{N}` per Paso 2)

## Ejemplos negativos (≥ 10)

(secciones `### Ejemplo negativo #{N}` per Paso 3)

## Telemetría observada (30-90 días)

(snippets del Paso 4)

## Política de re-curaduría

(per Paso 5)

## Apéndice — Versiones

- v1.0.0 — {fecha} — primera versión derivada de PoV {pov-path} (PR ref)
- v1.1.0 — {fecha} — re-curaduría trimestral (PR ref)

## Referencias

- `lex-agent-construction-directives::Directriz 06`
- `system-prompt.md` — identidad que el context-pack refuerza
- `guardrails.md` — categorías negativas alineadas a los controles
- `feedback.md` — pivot trigger disparan re-curaduría
- `kata-system-prompt-adversarial-validate` — suite invocada cuando negativos cambian
- `docs/{context}/agents-pov/{pov-agent}/` — fuente primaria en modo `with-pov`
```

## Restricciones

- < 5 few-shot positivos viola Directriz 06 en rigor de producción
- < 10 ejemplos negativos viola Directriz 06 en rigor de producción
- Few-shot inventado cuando hay PoV disponible está prohibido — preferir fuentes reales
- PoV inmaduro (`value-proof.md::status != ready_for_dooc`) como fuente está prohibido — aborta el Kata
- Snippets de telemetría con PII clara (no sanitizada) están prohibidos

---

**Modelo:** Kata es el puente canónico PoV → Operación Concreta. Lee 12 archivos del output de Claudionor cuando `--from-pov`, enriquece context pack con material real (few-shot + negativos + telemetría). En `direct-entry`, opera en modo cold-start con obligación de re-curaduría post-deploy. Confía (no revalida) el gate de PII del PoV.
