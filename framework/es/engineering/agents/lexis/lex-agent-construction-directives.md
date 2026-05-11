# Lexis: Directrices para la Construcción de Agentes

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Construcción de agentes de IA sobre la plataforma Guardia — system prompt, memoria, herramientas, feedback, alcance, contexto y ciclo de promoción de etapa cognitiva

## Ley

> **Todo agente de IA construido sobre la plataforma Guardia DEBE declarar explícitamente su etapa cognitiva (`stage: pre-operational | operational-concrete | legacy-pov`) en el system prompt. Los agentes en `operational-concrete` DEBEN satisfacer todas las 6 Directrices de Construcción (Identidad Clara, Memoria en Capas, Herramientas Concretas, Bucle de Feedback Explícito, Alcance Restringido, Contexto Rico) en rigor de producción, conforme a `codex-agent-construction-directives` y al manual canónico "Diretrizes para Construção de Agentes" mantenido en Notion. Los agentes en `pre-operational` PUEDEN operar con una versión mínima viable de cada Directriz, siempre que la etapa esté declarada y los gaps registrados en el PoV. Promover un agente de `pre-operational` a `operational-concrete` sin Definition of Operational Concrete (DoOC) validada en los 9 ítems canónicos está PROHIBIDO.**

## Alcance

- **Se aplica a:** todo agente de IA construido sobre la plataforma Guardia — Isac, agentes de conciliación, clasificación fiscal, cierre contable, agentes internos de automatización, agentes customer-facing, agentes de soporte. Se aplica al prompt del agente, a la capa de tooling, a la capa de memoria y al ciclo de promoción entre etapas.
- **Agentes vinculados:** `warrior-claudionor` (Fábrica de PoV — plan-031), `warrior-metis` (APM Operación Concreta — plan-032), `warrior-apollo-agents` (implementación — plan-013), `warrior-athena` (Gate 2 del Issue-Driven Flow cuando la feature toca `docs/{context}/agents/`).
- **Excepciones:** las Lexis no admiten excepciones. La única cláusula declarada es la transición `legacy-pov` descrita abajo: los agentes creados antes del merge de esta Lex son tratados como `stage: legacy-pov` y DEBEN migrar a `pre-operational` u `operational-concrete` en hasta 90 días, mediante DoOC retroactiva + ADR registrando el gap histórico.

## Etapas cognitivas

La analogía de Piaget detallada en `codex-agent-construction-directives` es el marco conceptual; el rigor diferencial expresado aquí es la traducción operativa.

| Tag | Cuándo usar | Rigor exigido a las 6 Directrices |
|-----|-------------|-----------------------------------|
| `pre-operational` | PoV activo, probando valor antes de la escala | Versión mínima viable de cada Directriz; gaps declarados en doc del PoV/PDR |
| `operational-concrete` | Producción; alcance probado; valor medido | Todas las 6 Directrices en rigor de producción |
| `legacy-pov` | Agente anterior al merge de esta Lex | Tratado como `pre-operational`; migración obligatoria en 90 días |

## Definition of Operational Concrete (DoOC)

La DoOC es el checklist canónico de promoción. El detalle por criterio (formato de evidencia, links esperados) está en `codex-agent-construction-directives`. Los 9 ítems son:

1. **Origen del PoV declarado** — path en `docs/{context}/agents-pov/` que referencia al PoV original
2. **Métrica leading de valor probada** — número, threshold y ventana de observación (mínimo 7 días)
3. **Métrica lagging de valor declarada** — métrica de negocio que será impactada
4. **Alcance estabilizado** — sin cambio de alcance en las últimas 2 semanas
5. **Observability data disponible** — telemetría mínima de 7 días del PoV en operación
6. **Stakeholder owner identificado** — nombre y rol; canal de escalado documentado
7. **Capacidad de implementación confirmada** — `warrior-apollo-agents` disponible O camino alternativo declarado
8. **Tier de criticidad declarado** — tier-1/2 dispara SLO obligatorio per `lex-slo-required`
9. **Stage explícito en el system prompt** — `stage: pre-operational` declarado en el prompt del PoV antes de la promoción

## HARD-GATE

Conforme a [`lex-hard-gate-pattern`](framework/es/_foundation/quality/lexis/lex-hard-gate-pattern.md), el bloqueo textual de esta Lex se expresa canónicamente como:

```
<HARD-GATE>
warrior-claudionor, warrior-metis, warrior-apollo-agents y cualquier
otro agente NO DEBE promover un agente de `pre-operational` a
`operational-concrete` sin TODOS los 9 ítems de la Definition of
Operational Concrete (DoOC) ✅:

  (a) Origen del PoV declarado (path en docs/{context}/agents-pov/)
  (b) Métrica leading de valor probada (número, threshold, ventana
      ≥ 7 días)
  (c) Métrica lagging de valor declarada
  (d) Alcance estabilizado (sin cambio en las últimas 2 semanas)
  (e) Observability data del PoV disponible (≥ 7 días)
  (f) Stakeholder owner identificado
  (g) Capacidad de implementación confirmada (warrior-apollo-agents
      O camino alternativo declarado)
  (h) Tier de criticidad declarado (tier-1/2 dispara SLO obligatorio)
  (i) Stage explícito en el system prompt del PoV
      (`stage: pre-operational`)

Esta regla se aplica a TODO agente construido sobre la plataforma
Guardia, independientemente de:
  - tamaño percibido ("es solo un agente simple")
  - urgencia ("el cliente lo necesita hoy")
  - quién solicitó ("lo pidió el CEO")
  - confianza del equipo ("ya probamos bastante")

Excepción única declarada: los agentes creados antes del merge de
esta Lex son tratados como `stage: legacy-pov`. La promoción a
`operational-concrete` exige DoOC retroactiva + ADR registrando el
gap histórico. La tag `legacy-pov` NO es permanente: los agentes en
esa etapa DEBEN migrar a `pre-operational` u `operational-concrete`
en hasta 90 días tras el merge de esta Lex; los agentes en
`legacy-pov` más allá de ese plazo se consideran no conformes.
</HARD-GATE>
```

## Ejemplos

### Correcto

System prompt de PoV declarando la etapa:

```
# Agente: rec-pov-classifier
# stage: pre-operational
# DoOC gaps: leading metric aún en recolección; observability < 7 días
# Identidad: clasificador de transacciones para conciliación
# Memoria: corto plazo (ventana de la sesión)
# Herramientas: search en el histórico de clasificaciones + ejecución simple
# Feedback: HITL ligero (un analista valida cada clasificación)
# Alcance: 1 caso de uso — extractos de Itaú PJ
# Contexto: 12 few-shot + 4 ejemplos negativos curados
```

System prompt de agente en producción:

```
# Agente: rec-classifier
# stage: operational-concrete
# DoOC: ✅ (validada el 2026-04-12, ADR-018)
# tier: tier-2
# SLO: docs/reconciliation/metrics/slo-rec-classifier.yaml
# Identidad: per docs/reconciliation/agents/rec-classifier/identity.md (manual completo)
# Memoria: corto + medio (sesión + histórico del cliente) + largo (reglas de clasificación)
# Herramientas: catálogo tripartito — deterministic + ML + MCP
# Feedback: HITL + critic LLM + 3 métricas objetivas en CloudWatch
# Alcance: clasificación de transacciones para conciliación bancaria
# Contexto: few-shot curado + docs + histórico observado de los últimos 90 días
```

### Incorrecto

Agente sin etapa declarada:

```
# Agente: rec-classifier
# Identidad: clasificador
# (sin stage:, sin DoOC, sin tier, sin referencia al manual)
```

Resultado: `warrior-athena` en el Gate 2 bloquea el PR; `warrior-metis` no promueve el PoV; el agente entra a producción como caja negra.

Promoción sin DoOC:

```
# Antes: stage: pre-operational
# Después: stage: operational-concrete
# (sin los 9 ítems de la DoOC validados, sin ADR de promoción)
```

Resultado: `warrior-metis` rechaza la promoción; el commit que cambia `stage:` sin checklist DoOC adjunto es bloqueado en el Gate 2.

## Validación Automatizada

- **Herramienta:** `kata-dooc-validate` (entregado en plan-032 junto a `warrior-metis`) ejecuta el checklist de los 9 ítems DoOC programáticamente; un lint en la pipeline detecta system prompts en `docs/{context}/agents/` sin `stage:` declarado; `warrior-athena` aplica este Gate cuando la feature toca artefactos de agentes.
- **Cuándo:** al promover un agente (transición `pre-operational` → `operational-concrete`); en el Gate 2 del Issue-Driven Flow cuando la feature toca `docs/{context}/agents/`; en auditoría periódica de agentes `legacy-pov` (90 días tras el merge).
- **Métrica:** 0 agentes en `operational-concrete` sin DoOC ✅; 100 % de los system prompts de la plataforma con `stage:` declarado; 0 agentes en `legacy-pov` más allá de 90 días tras el merge de esta Lex.
