# Lexis: Estructura Obligatoria de los Documentos de Diseño de Agente

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — eje Agent Design (documentos producidos por `warrior-metis` para promover y operar agentes)

## Propósito

La construcción de agentes en la plataforma Guardia exige rigor de forma para que el resultado sea revisable, comparable entre agentes y gobernable en producción. Sin una estructura única para los archivos de diseño, cada agente termina descrito en un lugar distinto, con secciones distintas, y la promoción de `pre-operational` a `operational-concrete` se vuelve subjetiva. Esta Lexis fija la ubicación física de los artefactos, el snapshot de gobernanza de la DoOC y la reciprocidad obligatoria con el eje Feature Design.

Esta Lexis complementa — pero no sustituye — `lex-agent-construction-directives`: aquella gobierna **qué** DEBE tener un agente (6 Directrices + 9 ítems de la DoOC); esta gobierna **dónde** y **en qué forma** DEBE documentarse para que la promoción y la operación sean auditables.

## Ley

> **Todo agente en estado `operational-concrete` en la plataforma Guardia DEBE tener (a) los 13 archivos canónicos en `docs/{context}/agents/{agent}/` según `codex-agent-design-docs` (Hub & Spoke), (b) `docs/{context}/dooc/{agent}.md` completado según el HARD-GATE de `lex-agent-construction-directives`, (c) `overview.md` con el campo `serves_features` poblado, (d) reciprocidad en `docs/{context}/feature-agent-map.md` (forward y reverse mapping consistentes entre features y agentes), (e) `warrior-metis` declarada como autora (PR ref, session-id o firma `authored_by: warrior-metis` en el header de `overview.md`).**

```
<HARD-GATE>
warrior-metis, warrior-apollo-agents y cualquier otro agente NO DEBE promover un agente a `operational-concrete` (merge en main, deploy en producción) sin TODAS las 5 preconditions:

  (a) 13 archivos presentes en `docs/{context}/agents/{agent}/`: `overview.md`, `orchestrator.md`, `specialists/{name}.md` (≥1), `tools.md`, `memory.md`, `reasoning-loop.md`, `feedback.md`, `context-pack.md`, `system-prompt.md`, `metrics.md`, `guardrails.md`, `authorization.md`, `escalation.md`
  (b) `docs/{context}/dooc/{agent}.md` existe y satisface el HARD-GATE de `lex-agent-construction-directives` (9 ítems de la DoOC con evidence o N/A justificado por ADR/PDR cuando `entry_mode` ≠ `with-pov`)
  (c) `agents/{agent}/overview.md` campo `serves_features` poblado con una lista válida de features existentes en `docs/{context}/features/`
  (d) `docs/{context}/feature-agent-map.md` refleja la relación: forward (feature → agentes) y reverse (agente → features) consistentes; ningún agente listado en una feature sin reciprocidad en `serves_features` del agente, y ninguna feature listada en `serves_features` sin reciprocidad en `served_by_agents`
  (e) `warrior-metis` declarada como autora — PR ref en el header de `overview.md` (campo `PR ref: {owner/repo#NNN}`) O `authored_by: warrior-metis` en el header O session-id canónico en el commit message

Esta regla se aplica a TODO agente en promoción a `operational-concrete`, sin importar:
  - tamaño percibido ("es solo un agente simple")
  - urgencia declarada ("el cliente lo necesita hoy")
  - quién lo solicitó ("el CEO pidió")
  - confianza del equipo ("ya probamos bastante")

Excepciones declaradas:
  - Agentes en `pre-operational` (PoV producida por `warrior-claudionor`) quedan FUERA de este HARD-GATE — su estructura mínima viable se define en `codex-agent-construction-directives` (rigor diferencial por etapa).
  - Agentes en `legacy-pov` (anteriores al merge de esta Lexis) PUEDEN ser promovidos con DoOC retroactiva + ADR según la cláusula de transición de `lex-agent-construction-directives` (90 días tras el merge). La reciprocidad en `feature-agent-map.md` sigue siendo obligatoria.
</HARD-GATE>
```

## Alcance

- **Se aplica a:** todo agente que sirve features de producción en la plataforma Guardia (Isac, agentes de reconciliación, clasificación fiscal/contable, cierre, futuros agentes). Incluye agentes que cubren un solo caso de uso (1..1) y agentes que cubren múltiples features (1..N).
- **Agentes vinculados:** `warrior-metis` (autora de los 13 archivos + `dooc/{agent}.md`), `warrior-apollo-agents` (consumidor durante la implementación), `warrior-athena` (Gate 2 cuando la feature toca `docs/**/agents/**`), `warrior-prometheus` (coordina la reciprocidad Feature ↔ Agent).
- **Excepciones:** solo las dos declaradas en el `<HARD-GATE>` (agentes en `pre-operational` y `legacy-pov`).

## Consecuencias de la Violación

1. **Bloqueo automático:** Gate 2 (`kata-quality-gate`) rechaza los PRs de promoción que no satisfagan las 5 preconditions. Los PRs con `serves_features` inconsistente con `served_by_agents` (reciprocidad rota) son bloqueados.
2. **Alerta:** notifica a `warrior-metis`, `warrior-prometheus` (eje Feature) y al owner del agent (campo `Owner` en `overview.md`).
3. **Remediación:** completar los 13 archivos, llenar `dooc/{agent}.md`, actualizar `feature-agent-map.md` para reflejar la reciprocidad y volver a publicar el PR de promoción. En despliegue de emergencia, el rollback es obligatorio hasta la remediación.

## Ejemplos

### Correcto

Agente `rec-classifier` en capability `reconciliation` promovido en el PR #543:

```
docs/
└── reconciliation/
    ├── agents/
    │   └── rec-classifier/
    │       ├── overview.md            # authored_by: warrior-metis; PR ref: guardiatechnology/ahrena#543
    │       │                          # serves_features: [transaction-classification, monthly-close-acceleration]
    │       ├── orchestrator.md
    │       ├── specialists/
    │       │   ├── statement-parser.md
    │       │   └── category-matcher.md
    │       ├── tools.md
    │       ├── memory.md
    │       ├── reasoning-loop.md
    │       ├── feedback.md
    │       ├── context-pack.md
    │       ├── system-prompt.md
    │       ├── metrics.md
    │       ├── guardrails.md
    │       ├── authorization.md
    │       └── escalation.md
    ├── dooc/
    │   └── rec-classifier.md          # 9 ítems con evidence; entry_mode: with-pov
    ├── features/
    │   ├── transaction-classification.md   # served_by_agents: [rec-classifier]
    │   └── monthly-close-acceleration.md   # served_by_agents: [rec-classifier]
    └── feature-agent-map.md           # forward: transaction-classification → rec-classifier
                                       # reverse: rec-classifier → transaction-classification, monthly-close-acceleration
```

Reciprocidad verificada: `serves_features` en `rec-classifier/overview.md` lista las dos features y cada feature lista al agente en `served_by_agents`. Promoción aprobada en Gate 2.

### Incorrecto

```
docs/
└── reconciliation/
    ├── agents/
    │   └── rec-classifier/
    │       ├── overview.md            # serves_features: [transaction-classification, refund-detection]
    │       └── ... (13 archivos)
    ├── features/
    │   └── transaction-classification.md   # served_by_agents: [rec-classifier]
    │                                       # ❌ refund-detection no existe
    └── feature-agent-map.md           # ❌ forward no incluye refund-detection
```

Reciprocidad rota: `serves_features` apunta a una feature inexistente (`refund-detection`) y `feature-agent-map.md` no la refleja. **Gate 2 rechaza** — preconditions (c) y (d) violadas.

Otro caso incorrecto: agente promovido sin `dooc/{agent}.md` ("lo completamos después"). Sin un snapshot validado según `lex-agent-construction-directives`, la precondition (b) se viola; promoción bloqueada.

## Validación Automatizada

- **Herramienta:** verificación por el propio agente (`warrior-metis`) antes de la promoción + lint en el Gate 2 (`kata-quality-gate`) detectando: ausencia de los 13 archivos, `dooc/{agent}.md` faltante, campo `serves_features` vacío en `operational-concrete`, desincronía entre `serves_features` ↔ `served_by_agents` (reciprocidad), ausencia de `authored_by` o PR ref en el header de `overview.md`. En el futuro: `kata-agent-design-validate` formalizando los 5 checks.
- **Momento:** Gate 2 del flujo Issue-Driven; revisión de PR de la promoción; pre-despliegue de cualquier agente en `operational-concrete`; auditoría periódica de agentes en producción.
- **Métrica:** 0 agentes en `operational-concrete` sin las 5 preconditions ✅; 0 features con `served_by_agents` apuntando a un agente inexistente; 0 agentes con `serves_features` apuntando a una feature inexistente; 100% de las promociones con `warrior-metis` rastreada como autora.

## Referencias

- `codex-agent-design-docs` — manual con los 15 templates (13 archivos del agent + dooc + feature-agent-map)
- `lex-agent-construction-directives` — Ley maestra (6 Directrices + HARD-GATE de la DoOC)
- `codex-agent-construction-directives` — fundación conceptual (Piaget, stage tags, rigor diferencial, formato de evidencias)
- `lex-feature-design-docs`, `codex-feature-design-docs` — eje paralelo Feature Design (reciprocidad `serves_features` ↔ `served_by_agents`)
- `lex-hard-gate-pattern` — formato del bloque `<HARD-GATE>` utilizado en esta Lexis
- `warrior-metis` — autora de los artefactos del eje Agent
- `warrior-apollo-agents` — consumidor de implementación
- `warrior-athena` — orquesta el Gate 2 cuando una feature toca `docs/**/agents/**`
- `warrior-prometheus` — coordina la reciprocidad Feature ↔ Agent
