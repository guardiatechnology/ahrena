# Lexis: Flujo de Product Discovery — Insight a Idea

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Ámbito:** Product Discovery — producción de insights, transición de status, y promoción de insight aprobado a Idea en Ahrena

## Propósito

Garantizar que toda Idea en Ahrena tenga origen rastreable en insights aprobados por humanos, y que la evolución de status de un insight ocurra exclusivamente por decisión humana explícita. Sin esta ley, las Ideas nacen sin evidencia y los insights se deslizan de `proposed` a estados terminales sin revisión, rompiendo la auditabilidad del Discovery.

## Ley

> **Toda Idea en Ahrena (`docs/discovery/{topic}/ideas/{NNN}-{slug}.md`) DEBE haber sido creada por `warrior-phanes` exclusivamente a partir de uno o más insights cuyo `status` sea `approved`, con los 5 campos de contenido obligatorios (`problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate`) completados, y el insight de origen DEBE ser actualizado a `status: promoted` con `idea_ref` apuntando a la Idea creada. Todo cambio de `status` de un insight a cualquier valor distinto de `proposed` DEBE ser conducido por decisión humana explícita registrada (mensaje en la sesión, comentario en PR, o instrucción literal); `warrior-pitia` NO DEBE alterar status por iniciativa propia, excepto la creación inicial en `proposed`.**

## Cobertura

- **Se aplica a:** todos los insights e ideas producidos en el contexto Ahrena, en cualquier proyecto que adopte el framework
- **Agentes vinculados:** `warrior-pitia`, `warrior-phanes`, y cualquier otro agente que cree o modifique archivos bajo `docs/discovery/`
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones. (Los HARD-GATEs abajo declaran *carve-outs de precondición* — no excepciones de la Ley. El carve-out del HG2 — creación inicial en `proposed` — es parte integral de la regla, no derogación.)

```
<HARD-GATE>
warrior-phanes NO DEBE promover un insight a Idea sin que TODAS las
precondiciones abajo sean atendidas:

  (a) insight.status == approved (decisión humana registrada)
  (b) Idea referencia ≥1 insight en linked_insights[]
  (c) Idea completa los 5 campos obligatorios del schema:
      problem, hypothesis, target_user, success_metric, effort_estimate
  (d) Idea.topic coincide con insight.topic en TODOS los linked_insights[]
  (e) Phanes actualiza el insight de origen a status: promoted +
      completa idea_ref apuntando a la Idea creada

Esta regla se aplica a TODA creación de Idea en Ahrena, independientemente de:
  - tamaño percibido ("es solo un experimento")
  - validación verbal ("el stakeholder ya aprobó en la call")
  - obviedad percibida ("el insight es trivial")
  - urgencia declarada ("necesitamos la Idea para el sprint que empieza mañana")

Excepción única: ninguna.
</HARD-GATE>
```

```
<HARD-GATE>
warrior-pitia NO DEBE alterar el status de un insight a cualquier
valor distinto de "proposed" sin dirección humana explícita.

Precondiciones obligatorias para cualquier transición de status distinta
de `[*] → proposed`:

  (a) Existe instrucción humana explícita identificando el insight por
      su `id` o path canónico
  (b) La transición-objetivo es válida en la máquina de estados definida en
      codex-discovery-artifacts (tabla de transiciones)
  (c) Para under_review → refining: el humano proporcionó feedback accionable
      por escrito
  (d) Para refining → under_review: la v2 del insight fue efectivamente
      redactada, con `updated_at` actualizado

Esta regla se aplica a TODOS los insights producidos por warrior-pitia,
independientemente de:
  - obviedad del feedback ("el ajuste es trivial")
  - histórico de casos similares ("Pitia ya vio esto antes")
  - urgencia declarada
  - confianza del equipo

Excepción única: la creación inicial del insight (`[*] → proposed`) es
de la propia warrior-pitia y no exige dirección humana — solo la
existencia de al menos una referencia en `source_refs[]`.
</HARD-GATE>
```

## Consecuencias de Violación

1. **Bloqueo automático:** PR rechazado cuando el reviewer detecta (a) Idea sin `linked_insights[]` válido, (b) Idea con alguno de los 5 campos obligatorios vacío o nulo, (c) insight cuyo status cambió sin evidencia humana correspondiente, o (d) `topic` divergente entre Idea y sus insights de origen.
2. **Alerta:** notifica al stakeholder responsable del `topic` y al autor humano que conducía la evaluación.
3. **Remediación:** el autor del PR elige entre (a) corregir la Idea/insight para satisfacer todas las precondiciones del HARD-GATE aplicable, o (b) revertir la transición inválida y reabrir el ciclo a partir del estado anterior válido.

## Ejemplos

### Correcto

```yaml
# docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
---
id: "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
topic: "scheduled-payments-research"
status: approved          # <- humano aprobó explícitamente en PR review
source_refs:
  - "docs/transcripts/interview-2026-05-04-accountant-X.md"
created_at: "2026-05-04T10:00:00Z"
updated_at: "2026-05-08T14:30:00Z"
---

# warrior-phanes lee el insight aprobado y produce la Idea:
# docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md
---
id: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
topic: "scheduled-payments-research"          # <- coincide con el topic del insight
problem: "Los contadores pierden 4h/semana conciliando ERP y extracto bancario."
hypothesis: "Sugerencia automática con confianza ≥90% será aceptada en ≥70% de los casos, reduciendo el tiempo manual en ≥60%."
target_user: "Contador operacional en oficinas con 50–500 clientes"
success_metric: "Tiempo medio de conciliación: baseline 4h/cliente/mes → meta 1.5h en 90 días"
effort_estimate: "M (2–4 sprints)"
linked_insights:
  - "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
created_at: "2026-05-10T15:00:00Z"
updated_at: "2026-05-10T15:00:00Z"
---

# Phanes actualiza el insight de origen:
# status: promoted
# idea_ref: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
```

### Incorrecto

```yaml
# Idea sin linked_insights[] — VIOLA HARD-GATE 1, precondición (b)
---
id: "scheduled-payments-research/ideas/002-mobile-receipt-capture"
topic: "scheduled-payments-research"
problem: "Creemos que mobile capture sería útil"
hypothesis: ""              # <- VIOLA HARD-GATE 1, precondición (c) — campo vacío
target_user: "Usuarios"     # <- inadecuado, pero presente
success_metric: ""          # <- VIOLA HARD-GATE 1, precondición (c)
effort_estimate: "M"
linked_insights: []         # <- VIOLA HARD-GATE 1, precondición (b) — array vacío
---
```

```yaml
# warrior-pitia cambia status sin dirección humana — VIOLA HARD-GATE 2
# Antes: status: proposed
# Después (sin instrucción humana): status: approved
# ❌ Aunque Pitia "lo considere obvio", la transición es inválida sin registro humano.
```

```yaml
# Idea con topic divergente del insight — VIOLA HARD-GATE 1, precondición (d)
---
id: "billing/ideas/001-auto-invoice"
topic: "billing"
linked_insights:
  - "scheduled-payments-research/insights/003-erp-divergence"  # topic divergente
---
```

## Validación Automatizada

- **Herramienta:** revisión humana en PR mientras no existe linter dedicado; en el futuro `kata-design-validation` parametrizado para tipo `discovery-artifacts` debe validar (i) presencia y tipo de los campos obligatorios, (ii) coherencia de `topic` entre Idea y `linked_insights[]`, (iii) coherencia de `status` + campos condicionales (`merged_into`, `idea_ref`, `rejected_reason`, `awaiting_evidence_reason`), (iv) histórico de transiciones en el git log del archivo (cada cambio de status acompañado por commit o comentario humano).
- **Momento:** PR review en todo PR que toque `docs/discovery/`; auto-check por el propio `warrior-phanes` antes de grabar la Idea.
- **Métrica:** 0 Ideas con `linked_insights[]` vacío en `main`; 0 Ideas con cualquiera de los 5 campos obligatorios vacío; 0 transiciones de status de insight ejecutadas por `warrior-pitia` sin evidencia de instrucción humana correspondiente; 100% de los `topic` de Ideas coincidentes con sus insights de origen.

## Referencias

- `codex-discovery-artifacts` — schema completo de insights e ideas, máquina de estados, convenciones de direccionamiento
- `lex-hard-gate-pattern` — patrón canónico del bloque HARD-GATE
- `kata-discovery-synthesis` — procedimiento de producción de insights
- `kata-ideation-from-insight` — procedimiento de promoción a Idea
- `warrior-pitia`, `warrior-phanes` — agentes vinculados
