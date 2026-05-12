# Kata: Design del Catálogo Tripartito de Herramientas

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents: design del catálogo de herramientas (`tools.md`) del agent en `operational-concrete`

## Objetivo

Producir el catálogo canónico de herramientas del agent, dividido en **tres categorías** per `lex-agent-construction-directives::Directriz 03 — Herramientas Concretas`:

1. **Deterministic** — funciones determinísticas (búsqueda por clave, validaciones, parsing controlado)
2. **ML** — modelos entrenados o inferencia específica (clasificación, embeddings, OCR)
3. **MCP** — herramientas expuestas vía servidor MCP (per `lex-mcp` y `codex-mcp-common`)

El catálogo declara contrato (input, output, idempotencia, latencia típica, lateral effects) de cada herramienta. Cubre rigurosamente la **Directriz 03**.

## Cuándo Usar

- Tras `kata-agent-orchestrator-design` y (cuando aplicable) `kata-agent-specialists-design`
- Cuando el agent necesita revisión del catálogo (nueva herramienta añadida, herramienta deprecada vía ADR)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `context` | Sí | Bounded Context |
| `agent` | Sí | Slug del agent |
| `orchestrator_path` | Sí | `docs/{context}/agents/{agent}/orchestrator.md` |
| `specialists_paths` | No | Lista de `docs/{context}/agents/{agent}/specialists/{name}.md` |
| `--from-pov <path>` | No | PoV path; hereda subset de tools experimentadas y desambigua catálogo de producción |

## Workflow

```
Progreso:
- [ ] 1. Extraer tools mencionadas en orchestrator + specialists
- [ ] 2. Clasificar cada tool (deterministic | ML | MCP)
- [ ] 3. Declarar contrato de cada tool (I/O, idempotencia, lateral effects)
- [ ] 4. Verificar idempotencia donde escritura está involucrada
- [ ] 5. Validación de input en frontera
- [ ] 6. Validación final
```

### Paso 1: Extraer tools mencionadas

Lee `orchestrator.md::Workflow (con tools y dependencias)` y cada `specialists/{name}.md::Tools consumidas`. Consolida lista única.

### Paso 2: Clasificar cada tool

| Señal | Categoría |
|-------|-----------|
| Función pura sin llamada externa, output 100% determinístico para input fijo | **Deterministic** |
| Inferencia vía modelo (clasificador, embeddings, regresor, OCR, ASR) | **ML** |
| Llamada vía servidor MCP listado en `mcp.servers` en `.ahrena/.directives` | **MCP** |
| Llamada HTTP externa sin MCP | **MCP** (DEBE ser expuesta vía MCP per `lex-mcp` cuando posible) o justificación en ADR |

Cada tool aparece en **exactamente una** categoría. Duplicar está prohibido.

### Paso 3: Declarar contrato de cada tool

Template canónico para `tools.md`:

```markdown
# Tools — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **Source of truth:** este archivo. Tools usadas en runtime DEBEN constar en este catálogo; tools fuera del catálogo son bloqueadas por guardrail (cross-link `guardrails.md::Tool injection`).

## Deterministic

### `{tool-name}`

- **Descripción:** {1-2 frases}
- **Cuándo usar:** {gatillo concreto}
- **Input schema:** {JSON schema o referencia a Pydantic model}
- **Output schema:** {JSON schema}
- **Idempotencia:** sí (función pura)
- **Lateral effects:** ninguno
- **Latencia típica:** < {N}ms
- **Errores posibles:** {códigos per lex-error-handling}

(repetir para cada deterministic tool)

## ML

### `{tool-name}`

- **Descripción:** {modelo + versión + dataset de entrenamiento}
- **Cuándo usar:** {gatillo}
- **Input schema:** {}
- **Output schema:** {con confidence score}
- **Idempotencia:** parcial (mismo modelo + misma versión → output determinístico módulo random seed)
- **Lateral effects:** uso de inferencia pagada (costo declarado en ADR de modelo)
- **Latencia típica:** ~ {N}ms p99
- **Threshold de confidence:** {valor} (debajo → escalar vía `escalation.md`)
- **Versión del modelo:** {tag/SHA}
- **Retrain trigger:** {cuándo el modelo se reentrena}

(repetir para cada ML tool)

## MCP

### `{tool-name}`

- **Servidor MCP:** `{server-name}` (declarado en `mcp.servers` en `.ahrena/.directives`)
- **Descripción:** {1-2 frases}
- **Cuándo usar:** {gatillo}
- **Input schema:** {}
- **Output schema:** {}
- **Idempotencia:** sí/no — cuando "no", DEBE recibir `Idempotency-Key` en el input per `lex-idempotency`
- **Lateral effects:** {escritura en sistema externo: ERP, banco, e-mail, S3}
- **Latencia típica:** ~ {N}ms p99
- **Retry policy:** {exponential backoff, max retries, circuit breaker}
- **Errores posibles:** {códigos per lex-error-handling}
- **Auth:** credenciales vía variable de ambiente per `lex-mcp` (nunca en código)

(repetir para cada MCP tool)

## Idempotencia

Tools que producen efecto lateral (categoría MCP, en su mayoría) DEBEN ser idempotentes per `lex-idempotency`. Implementación:

- Endpoint recibe `Idempotency-Key` en el header o input
- Servidor MCP deduplica por clave + hash del payload
- Retry con misma clave + mismo payload retorna mismo resultado (no duplica efecto)

Tools que fallan este requisito DEBEN ser deprecadas y sustituidas.

## Validación de input en frontera

Toda tool DEBE validar el input antes de ejecutar:

- Schema validation vía Pydantic o Zod
- Type checking estricto
- Bounds checking (e.g., `amount > 0` per invariante del aggregate)
- `org_id`/`client_id` checking — tool nunca cruza frontera de tenant

Cross-link `guardrails.md::Tool injection` para controles OWASP.

## Referencias

- `lex-agent-construction-directives::Directriz 03`
- `lex-mcp`, `codex-mcp-common`
- `lex-idempotency`
- `lex-error-handling`, `codex-known-errors`
- `guardrails.md` — controles OWASP aplicados a las tools
- `orchestrator.md`, `specialists/` — quién invoca qué
```

### Paso 4: Verificar idempotencia donde escritura está involucrada

Para cada tool en `MCP` con `lateral effects ≠ ninguno`:

1. Confirma que acepta `Idempotency-Key`
2. Confirma que el servidor MCP deduplica
3. Confirma que retry policy no duplica efecto

Cuando falla, registra tool como `pending idempotency review` en el PR de promoción; bloquea merge hasta resolver.

### Paso 5: Validación de input en frontera

Para cada tool:

- Existe schema (Pydantic, Zod o equivalente)
- Schema valida `org_id`/`client_id` cuando aplicable
- Errores de validación retornan `ERR400_INVALID_PARAMETER` per `lex-error-handling`

### Validación Final

- [ ] Toda tool aparece en exactamente una categoría
- [ ] Tools con lateral effects tienen idempotencia verificada
- [ ] Tools ML declaran versión del modelo + threshold de confidence
- [ ] Tools MCP referencian servidor declarado en `mcp.servers`
- [ ] Schemas declarados (input + output) — no placeholders
- [ ] Cross-references con `guardrails.md` para OWASP applied controls

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `tools.md` | Markdown | `docs/{context}/agents/{agent}/tools.md` |

## Restricciones

- Toda tool DEBE estar en una de las 3 categorías; cuarta categoría está prohibida sin ADR
- Tools con lateral effects sin idempotencia están prohibidas en `operational-concrete`
- Tool expuesta directamente sin servidor MCP está prohibida cuando MCP es viable (per `lex-mcp`); justificación exige ADR
- No duplicar tools entre categorías

---

**Modelo:** Kata produce catálogo tripartito (deterministic | ML | MCP) con contratos claros. Toda tool en runtime DEBE constar en este archivo; guardrails bloquean tools fuera del catálogo.
