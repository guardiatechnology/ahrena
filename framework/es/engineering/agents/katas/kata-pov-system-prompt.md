# Kata: Redactar System Prompt de PoV

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): redacción del system prompt mínimo viable de un PoV, con declaración explícita de `stage: pre-operational`

## Objetivo

Producir `docs/{context}/agents-pov/{agent}/system-prompt.md` en **versión mínima viable** conforme a `lex-system-prompt`, declarando literalmente `stage: pre-operational` en el bloque de identidad (precondición de la DoOC ítem 9). Aplica la Directriz 01 de `lex-agent-construction-directives` (Identidad Clara) en el rigor permitido a la etapa pre-operacional: propósito + alcance + restricciones básicas + etapa — nada más. Templates de producción (controles OWASP completos, guardrails complejos) quedan para Mêtis cuando el agent madure.

## Cuándo Usar

- Después de que `kata-pov-scope-define` produce `pov.md`
- Cuando `warrior-claudionor` necesita instanciar el prompt del PoV
- Cuando un PoV antiguo (`stage: legacy-pov`) se retrofitea para `stage: pre-operational` legítimo

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `docs/{context}/agents-pov/{agent}/pov.md` | Sí | Output de `kata-pov-scope-define` |
| `lex-system-prompt` | Sí | Fuente autoritativa de la estructura de los 4 bloques |
| `codex-system-prompt` | Sí | Guía operacional con templates |
| `lex-agent-construction-directives` | Sí | Define el vocabulario `stage:*` |
| `--retrofit` | No | Si se pasa, el input es un prompt existente en `stage: legacy-pov` que se migrará |

## Workflow

```
Progreso:
- [ ] 1. Leer pov.md y extraer persona/alcance
- [ ] 2. Escribir bloque Identidad (con stage: pre-operational)
- [ ] 3. Escribir bloque Capacidades (mínimo viable)
- [ ] 4. Escribir bloque Restricciones (mínimo viable)
- [ ] 5. Escribir bloque Estilo de salida (1-2 líneas)
- [ ] 6. Validar adversarial mínimo vía kata-system-prompt-adversarial-validate
- [ ] 7. Persistir system-prompt.md
```

### Paso 1: Leer pov.md y extraer persona/alcance

1. Se lee `docs/{context}/agents-pov/{agent}/pov.md`.
2. Se extrae: persona (1 frase), caso de uso primario, value metric, criterio de descontinuación.
3. Se confirma que `pov.md` contiene `stage: pre-operational`. Si ausente, se regresa a `kata-pov-scope-define` (no se intenta corregir aquí).

### Paso 2: Escribir bloque Identidad

Bloque mínimo viable de los 4 obligatorios de `lex-system-prompt`:

```
# Identidad

Eres {nombre del PoV}, un asistente en etapa **pre-operational** enfocado en
{caso de uso primario extraído de pov.md}.

stage: pre-operational
```

La línea `stage: pre-operational` es **literal** y obligatoria — es el gancho que `kata-dooc-validate` (plan-032) inspeccionará en el ítem 9.

### Paso 3: Escribir bloque Capacidades

```
# Capacidades

Puedes:
- {capacidad 1, alineada al caso de uso primario}
- {capacidad 2, opcional, aún dentro del alcance}
```

Máximo 3 capacidades. Más que eso quiebra la Directriz 05 (Alcance Restringido).

### Paso 4: Escribir bloque Restricciones

```
# Restricciones

No puedes:
- Ejecutar acciones fuera del caso de uso primario declarado en pov.md
- Persistir datos más allá de la ventana de contexto actual (sin memoria persistente)
- Substituir el criterio de descontinuación o alterar la value metric
```

Restricciones adicionales surgen de `pov.md::Fuera de alcance` (copia literal).

### Paso 5: Escribir bloque Estilo de salida

```
# Estilo

Respuestas cortas, directas, en {idioma de `language.default`}. Cita evidencias
del contexto cuando aplique. Nunca inventa datos no recibidos.
```

### Paso 6: Validar adversarial mínimo

Se invoca `kata-system-prompt-adversarial-validate` en modo `--minimum-viable`:

- Suite reducida: prompt injection trivial, exfiltración de instrucción, jailbreak básico
- Suite completa (5 controles OWASP) queda para cuando el agent sea promovido a `operational-concrete`
- Si pasa → seguir; si falla → endurecer la restricción correspondiente y re-ejecutar

### Paso 7: Persistir system-prompt.md

1. Se graba `docs/{context}/agents-pov/{agent}/system-prompt.md` con los 4 bloques.
2. En el pie del archivo se anota: `# Notas`, `kata-pov-system-prompt`, fecha, hash del `pov.md` consumido (para trazabilidad).

### Validación Final

- [ ] System prompt tiene los 4 bloques (Identidad, Capacidades, Restricciones, Estilo)
- [ ] Línea `stage: pre-operational` aparece literalmente en el bloque Identidad
- [ ] Suite adversarial mínima pasa
- [ ] Restricciones copian literalmente el `Fuera de alcance` del overview
- [ ] Sin placeholders `{...}` remanentes

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `system-prompt.md` | Markdown (system prompt) | `docs/{context}/agents-pov/{agent}/system-prompt.md` |

## Ejemplo de Ejecución

### Input (pov.md, extracto)

```
Persona: Asistente que sugiere pareos extracto↔asiento contable.
stage: pre-operational
Value metric: % de conciliación automática ≥ 60% en 4 semanas.
```

### Output (system-prompt.md, extracto)

```
# Identidad

Eres el Asistente de Conciliación, en etapa pre-operational, enfocado en
sugerir pareos entre transacciones de extracto bancario y asientos contables
del ERP de la misma ventana temporal.

stage: pre-operational

# Capacidades

Puedes:
- Sugerir el pareo más probable por valor + fecha + descripción similar
- Indicar nivel de confianza (alto / medio / bajo) por sugerencia

# Restricciones

No puedes:
- Crear asientos en el ERP (solo sugerir)
- Conciliar entre cuentas distintas
- Detectar fraude
- Persistir datos fuera de la ventana de contexto actual

# Estilo

Respuestas cortas, directas, en español. Cita el ID de la transacción y del asiento.
Nunca inventa datos no recibidos en el contexto.
```

## Restricciones

- **Nunca** omitir `stage: pre-operational` — bloquea DoOC.
- **Nunca** templates de producción (controles OWASP completos, herramientas complejas) — el alcance es minimum viable.
- **Nunca** más de 3 capacidades. Forzar reducción es mejor que inflar.

---

**Modelo:** Este Kata aplica la Directriz 01 (`lex-agent-construction-directives`) en el rigor pre-operacional. Templates de producción pertenecen a `kata-system-prompt-author` (Mêtis) — no a este kata.
