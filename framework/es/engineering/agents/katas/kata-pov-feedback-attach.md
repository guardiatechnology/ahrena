# Kata: Anexar Loop de Feedback al PoV

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): definición de HITL ligero O 1 métrica objetiva como loop de feedback del PoV

## Objetivo

Producir `docs/{context}/agents-pov/feedback.md` declarando el loop de feedback del PoV: **HITL ligero** (humano aprueba outputs críticos) **O** **1 métrica objetiva** del ambiente (ej.: "¿la query devuelve resultado válido?"). El critic agent es opcional. Aplica la Directriz 04 de `lex-agent-construction-directives` (Loop de Feedback Explícito) en el rigor mínimo viable: el PoV no necesita el loop completo de producción, pero necesita **alguna señalización objetiva** de si está acertando.

## Cuándo Usar

- Después de `kata-pov-tools-select` y `kata-pov-observability-instrument` (value-metrics referenciadas)
- Cuando el tier del PoV está definido (default: tier-3/4)
- Cuando una ronda de operación revela que el feedback declarado no está siendo capturado (re-ejecución)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `docs/{context}/agents-pov/overview.md` | Sí | Caso de uso primario y value metric |
| `docs/{context}/agents-pov/observability/value-metrics.md` | Sí | Métrica primaria |
| `--tier <1\|2\|3\|4>` | No | Default 3. Tier-1/2 exige loop más rígido |

## Workflow

```
Progreso:
- [ ] 1. Decidir entre HITL ligero o métrica objetiva (o ambos)
- [ ] 2. Especificar mecanismo escogido
- [ ] 3. Definir cadencia de captura
- [ ] 4. Declarar pivot trigger (cuando el feedback cambia el PoV)
- [ ] 5. Persistir feedback.md
```

### Paso 1: Decidir entre HITL ligero o métrica objetiva

Criterio de elección:

| Escenario | Mecanismo |
|---|---|
| Output es decisión consecuente (escribe en sistema externo, envía comunicación) | HITL ligero obligatorio |
| Output es sugerencia consultiva (humano valida antes de aplicar) | Métrica objetiva basta |
| Tier-1/2 declarado | HITL ligero + métrica objetiva (ambos) |
| Tier-3/4 (default PoV) | Al menos 1 de los dos |

Si el caso de uso primario implica **decisión consecuente**, el kata fuerza HITL ligero incluso en tier-3/4.

### Paso 2: Especificar mecanismo escogido

**HITL ligero:**

- Dónde el humano aprueba: UI del PoV (botón "aprobar/rechazar"), comentario en PR, o canal dedicado (Slack thread)
- Qué se captura: input del agent, output del agent, decisión humana (aprobar/rechazar/editar), motivo (texto libre opcional)
- Latencia aceptable: ≤ 24h por default

**Métrica objetiva:**

- Señal binaria del ambiente que indica acierto/error (ej.: "asiento sugerido fue efectivado en el ERP en 7 días")
- Cómo capturar: webhook, polling de DB, log de acción humana
- Ventana de atribución: declarada (default 7 días)

### Paso 3: Definir cadencia de captura

- HITL ligero: agregación diaria + revisión semanal
- Métrica objetiva: agregación continua + lectura semanal en `value-proof.md`
- Resultado de la agregación es input para `kata-pov-value-track`

### Paso 4: Declarar pivot trigger

Condición declarada que, si se alcanza, fuerza revisión del PoV (re-ejecución de `kata-pov-scope-define`):

- Default: "Aprobación humana < 50% por 2 semanas consecutivas" (HITL ligero)
- Default: "Métrica objetiva < 30% del threshold por 2 semanas consecutivas"

El pivot trigger es **distinto** del criterio de descontinuación (`overview.md::Criterio de descontinuación`): el pivot pide revisión; la descontinuación cierra.

### Paso 5: Persistir feedback.md

Se graba `docs/{context}/agents-pov/feedback.md` con secciones: Mecanismo escogido, Especificación técnica, Cadencia, Pivot trigger, Referencia cruzada a `observability/value-metrics.md`.

### Validación Final

- [ ] Al menos 1 mecanismo declarado (HITL ligero O métrica objetiva)
- [ ] Si tier-1/2: ambos declarados
- [ ] Pivot trigger tiene condición cuantificada (ventana + threshold)
- [ ] Cadencia declarada explícitamente
- [ ] Cross-link a `value-metrics.md` activo

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `feedback.md` | Markdown | `docs/{context}/agents-pov/feedback.md` |

## Ejemplo de Ejecución

### Input (overview.md, extracto)

```
Caso de uso: sugerir pareo extracto↔asiento. Sugerencia consultiva (humano confirma antes de grabar).
Tier: 3 (default PoV).
```

### Output (feedback.md, extracto)

```markdown
## Mecanismo

Métrica objetiva (PoV es consultivo, tier-3).

## Especificación técnica

- Señal: "¿el operador aprobó o ajustó la sugerencia dentro de 7 días?"
- Captura: log del botón "Aplicar sugerencia" en el front del PoV
- Ventana: 7 días por sugerencia

## Cadencia

- Agregación continua en observability/value-metrics.md::reconciliation_auto_rate
- Revisión semanal en value-proof.md

## Pivot trigger

reconciliation_auto_rate < 30% por 2 semanas consecutivas → reescopo vía kata-pov-scope-define.
```

## Restricciones

- **Nunca** PoV sin feedback declarado. Sin feedback, value-proof se vuelve documento de fachada.
- **Nunca** HITL latente (> 7 días para captura humana) — invalida el ciclo corto que justifica el PoV.
- **Nunca** pivot trigger cualitativo ("si queda mal"). Siempre ventana + threshold.

---

**Modelo:** Este Kata aplica la Directriz 04 (`lex-agent-construction-directives`) en el rigor pre-operacional. El critic agent es opcional — queda para Mêtis cuando el agent sea promovido.
