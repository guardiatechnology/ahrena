# Kata: Rastrear Valor del PoV (value-proof.md)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): captura estructurada de datos durante la operación del PoV para sustentar decisión go/no-go de promoción a `operational-concrete`

## Objetivo

Producir y mantener `docs/{context}/agents-pov/value-proof.md` — documento **vivo** durante toda la operación del PoV. Define el schema canónico (campos obligatorios + SHA de la telemetría), criterio go/no-go para promoción (insumo directo de la DoOC), y cadencia de revisión (`tier-1/2 semanal`; `tier-3/4 quincenal`). Sin `value-proof.md` consistente, Mêtis no puede ejecutar `kata-dooc-validate` ítems 2 (leading probada) y 5 (observability ≥ 7 días).

## Cuándo Usar

- Inmediatamente después de `kata-pov-feedback-attach` (template inicial)
- En cada ciclo de revisión (semanal o quincenal, según tier) — actualización
- Cuando el pivot trigger de `feedback.md` se alcanza
- Antes de que Mêtis invoque `cry-agent-design --from-pov`

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `docs/{context}/agents-pov/overview.md` | Sí | Value metric leading + criterio de descontinuación |
| `docs/{context}/agents-pov/observability/value-metrics.md` | Sí | Definiciones y thresholds |
| `docs/{context}/agents-pov/feedback.md` | Sí | Mecanismo de captura + pivot trigger |
| `--tier <1\|2\|3\|4>` | No | Default 3. Determina la cadencia |
| `--cycle <N>` | No | Número de la ronda de revisión (1, 2, 3...) |

## Workflow

```
Progreso:
- [ ] 1. Inicializar value-proof.md con schema canónico (primera ejecución)
- [ ] 2. En cada ciclo, registrar lectura de la métrica primaria con SHA de la telemetría
- [ ] 3. Registrar observaciones cualitativas del ciclo
- [ ] 4. Evaluar criterio de descontinuación y pivot trigger
- [ ] 5. Actualizar status del PoV (continuar / pivotar / descontinuar / promover)
- [ ] 6. Persistir el documento actualizado
```

### Paso 1: Inicializar value-proof.md (primera ejecución)

Schema canónico (campos obligatorios):

```markdown
# value-proof.md — PoV {context}

> Cadencia: {semanal | quincenal} (tier-{N})
> Stage: pre-operational

## Identificación

- context: {context}
- iniciado en: {ISO date}
- responsable: {persona / equipo}
- métrica primaria: {nombre} (referencia: observability/value-metrics.md)
- threshold leading: {valor + ventana}
- criterio de descontinuación: {literal de overview.md}
- pivot trigger: {literal de feedback.md}

## Registro de ciclos

(sección viva — una entrada por ciclo)

### Ciclo 1 — {ISO date}

- período observado: {start} → {end}
- valor de la métrica primaria: {número}
- SHA de la telemetría de origen: {hash del snapshot de observability}
- observaciones cualitativas: {texto libre, 3-5 frases}
- decisión del ciclo: continuar | pivotar | descontinuar | promover
- justificación: {texto libre}

## Decisión actual

- status: activo | pivotando | cerrado | listo-para-DoOC
- actualizado en: {ISO date}
- próximo ciclo agendado: {ISO date}
```

### Paso 2: Registrar lectura de la métrica con SHA

En cada ejecución del kata en un ciclo:

1. Se lee el snapshot de la telemetría (export de `observability/value-metrics.md` agregado).
2. Se calcula SHA256 del snapshot (trazabilidad — Riesgo 5 de plan-031 mitiga "value-proof de fachada").
3. Se anexa al registro del ciclo: valor de la métrica + SHA + período observado.

### Paso 3: Registrar observaciones cualitativas

3-5 frases cortas por ciclo:

- Lo que funcionó (caso concreto, sin inventar)
- Lo que falló (anti-patrón observado, link al context-pack si aplica)
- Sorpresas (caso fuera de lo esperado)

Sin PII. Si un caso depende de detalle sensible, anonimícese o cítese por ID opaco.

### Paso 4: Evaluar criterio de descontinuación y pivot trigger

1. **Criterio de descontinuación** (de `overview.md`): si se alcanza, status → `cerrado`.
2. **Pivot trigger** (de `feedback.md`): si se alcanza, status → `pivotando` y se recomienda re-ejecutar `kata-pov-scope-define`.
3. **Éxito continuado** (métrica ≥ threshold por ≥ 7 días y alcance estabilizado por 2 semanas): el status puede avanzar a `listo-para-DoOC` — Mêtis puede ejecutar `cry-agent-design --from-pov`.

### Paso 5: Actualizar status del PoV

Se actualiza el bloque "Decisión actual" con:

- status (vocabulario cerrado: `activo`, `pivotando`, `cerrado`, `listo-para-DoOC`)
- timestamp
- próximo ciclo agendado (cadencia: semanal para tier-1/2, quincenal para tier-3/4)

### Paso 6: Persistir el documento

1. Se graba `docs/{context}/agents-pov/value-proof.md` con el ciclo actual añadido.
2. Se registra el commit en el historial del PoV (responsable + cycle number).
3. Si status = `listo-para-DoOC`, se emite log diciendo "Listo para que Mêtis consuma vía `cry-agent-design --from-pov docs/{context}/agents-pov/`".

### Validación Final

- [ ] Todos los campos obligatorios del schema presentes
- [ ] Al menos 1 ciclo registrado (en la ejecución inicial es el ciclo cero — bootstrap)
- [ ] SHA de la telemetría presente en cada ciclo (trazabilidad)
- [ ] Sin PII
- [ ] Status actual coherente con la lectura de la métrica

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `value-proof.md` | Markdown (vivo) | `docs/{context}/agents-pov/value-proof.md` |

## Cadencia (referencia rápida)

| Tier del PoV | Cadencia de revisión | Crítico para |
|---|---|---|
| 1, 2 | Semanal | PoV impacta ingresos o compliance |
| 3, 4 (default) | Quincenal | PoV consultivo / interno |

## Restricciones

- **Nunca** valor de métrica sin SHA de la telemetría — value-proof sin evidencia es fachada.
- **Nunca** ciclo sin decisión explícita (`continuar | pivotar | descontinuar | promover`).
- **Nunca** PII en observaciones.
- **Nunca** status fuera del vocabulario cerrado.
- **Siempre** el documento es vivo: cada ciclo **añade** una entrada; el historial se preserva.

---

**Modelo:** Este Kata es el insumo directo de la DoOC (`lex-agent-construction-directives`). El schema es el contrato consumido por `kata-dooc-validate` (plan-032).
