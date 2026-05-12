# Codex: Directrices para la Construcción de Agentes

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Ingeniería — Construcción de agentes de IA sobre la plataforma Guardia (PoV → Operación Concreta)

## Visión General

Manual de referencia para arquitectar agentes de IA en la plataforma Guardia. Codifica de forma operativa el contenido del manual "Diretrizes para Construção de Agentes" mantenido en Notion (source-of-truth viva). Acompaña a la Lex `lex-agent-construction-directives` y aporta el detalle conceptual, los ejemplos canónicos y el rigor diferencial que la Lex referencia.

Este Codex se consulta al construir, revisar o promover un agente — por humanos, por `warrior-claudionor` (Fábrica de PoV), por `warrior-metis` (APM Operación Concreta), por `warrior-apollo-agents` (implementación) y por `warrior-athena` (Gate 2 cuando la feature toca agentes).

## Contexto

- **Dominio:** construcción de agentes de IA (system prompt, memoria, herramientas, feedback, alcance, contexto) y promoción de PoV a Operación Concreta
- **Público objetivo:** ingenieros de agentes, tech leads, product managers, agentes de IA que orquestan la construcción
- **Actualización:** Notion es la fuente viva; este Codex es el snapshot operativo. Revisión trimestral; en caso de divergencia, **Notion prevalece**.

## Analogía de Piaget (base conceptual)

Jean Piaget describió el desarrollo cognitivo humano por etapas. Guardia aplica esa estructura a los agentes de IA porque aporta un vocabulario compartido para el rigor diferencial: cada etapa tiene expectativas mensurables distintas.

| Etapa de Piaget | Edad | Característica | Equivalente en agentes | Warrior Ahrena |
|-----------------|------|----------------|------------------------|----------------|
| Sensoriomotora | 0–2 años | Reactivo puro, sin representación interna | Agente solo reactivo, responde al contexto inmediato sin herramientas | No modelado (caso degenerado) |
| Preoperacional | 2–7 años | Pensamiento simbólico, sin operación lógica reversible | LLM con tooling ligero, sin modelado profundo del dominio | `warrior-claudionor` (plan-031) |
| Operaciones Concretas | 7–11 años | Lógica aplicada a objetos concretos; reversibilidad; clasificación | Agente con herramientas completas + memoria en capas + datos reales + feedback estructurado | `warrior-metis` (plan-032) |
| Operaciones Formales | 11+ años | Razonamiento abstracto, planificación, hipótesis | Planificación, autorreflexión, multi-step reasoning sobre objetivos abstractos | Frontera — no modelado en 2026 |
| Zona Proximal (Vygotsky) | Transversal | Aprendizaje mediado por par más experimentado | Multi-agent + HITL (humano o agente master en el loop) | Transversal (Directriz 04) |

La elección de operar Guardia entre **preoperacional** y **operaciones concretas** es deliberada: la etapa de Operaciones Formales sigue siendo frontera de investigación en 2026 y producir agentes allí sin fundamento provoca incidentes; la etapa sensoriomotora es insuficiente para los casos de uso de Guardia.

## Las 6 Directrices

Cada Directriz se detalla con (a) qué es, (b) por qué importa, (c) versión mínima viable en `pre-operational`, (d) versión de producción en `operational-concrete`.

### Directriz 01 — Identidad Clara

**Qué es.** Definición explícita del rol, propósito, límites y tono del agente en el system prompt. Incluye: rol (p. ej., "clasificador de transacciones"), dominio (p. ej., "conciliación bancaria PJ Itaú"), qué hace, qué rechaza, tono (formal/informal/técnico) y voz Guardia per `lex-brand-voice`.

**Por qué importa.** Una identidad vaga produce comportamiento errático. Sin identidad declarada, el agente asume los defaults del LLM, que varían por modelo y versión.

**Pre-operacional.** System prompt corto (~10 líneas) cubriendo rol, dominio, 1-2 rechazos explícitos. Aceptable omitir tono detallado.

**Operación Concreta.** Identidad codificada en el `docs/{context}/agents/{agent}/system-prompt.md` canónico per `codex-agent-design-docs` — rol, dominio, rechazos enumerados, tono, escalation matrix, voz Guardia. El system prompt es el artefacto canónico de la Directriz 01 (no hay `identity.md` separado en el template de 13 archivos).

### Directriz 02 — Memoria en Capas

**Qué es.** Tres capas de memoria distintas: **corto plazo** (ventana de la sesión actual), **medio plazo** (histórico del cliente/contexto de N sesiones), **largo plazo** (reglas de dominio, conocimiento institucional, patrones aprendidos).

**Por qué importa.** Sin memoria, el agente recomienza en cada turno; con toda la memoria junta, el contexto se vuelve sopa y la latencia explota. Las 3 capas separan volatilidad y responsabilidad.

**Pre-operacional.** Corto plazo es suficiente. Persistencia opcional; es aceptable que el histórico del cliente se pierda entre sesiones durante el PoV.

**Operación Concreta.** Tres capas obligatorias con responsable claro: corto vía ventana del LLM; medio vía store (Redis/DynamoDB) con TTL declarado; largo vía vector store o knowledge base + revisión humana. Cada capa tiene retención declarada per `lex-data-retention`.

### Directriz 03 — Herramientas Concretas

**Qué es.** Capacidades estructuradas que el agente invoca para actuar más allá de generar texto. Catálogo tripartito: (a) **deterministic** (funciones puras, validaciones, cálculos), (b) **ML** (clasificadores, embeddings, otras inferencias), (c) **MCP** (servers externos per `lex-mcp`).

**Por qué importa.** Un agente sin herramientas es solo un chatbot; herramientas mal diseñadas se vuelven superficie de ataque y punto de fallo no determinístico.

**Pre-operacional.** Búsqueda + ejecución simple; 1-3 herramientas son suficientes. Las herramientas pueden estar hardcoded en el PoV; observability mínima (log estructurado).

**Operación Concreta.** Catálogo tripartito completo con schema explícito (OpenAPI/JSON Schema), idempotencia donde aplique per `lex-idempotency`, observability completa (trace + metric + log) per `lex-observability-required`, validación de input en frontera per `lex-python-security`.

### Directriz 04 — Bucle de Feedback Explícito

**Qué es.** Mecanismo declarado para que el agente sepa si su respuesta fue útil. Tres modalidades complementarias: (a) **HITL** (humano en el loop — un analista valida la salida), (b) **critic** (LLM crítico revisa la salida del agente), (c) **métricas objetivas** (signal de negocio — tasa de adopción, reversión, tiempo hasta acción).

**Por qué importa.** Sin feedback, el agente no aprende y el equipo no sabe si el producto funciona. Feedback implícito ("el cliente no se quejó") es placebo.

**Pre-operacional.** HITL ligero O 1 métrica objetiva. Es aceptable un feedback asíncrono (revisión semanal manual).

**Operación Concreta.** HITL para acciones irreversibles (per `codex-ai-first-experience`) + critic LLM para acciones reversibles + ≥3 métricas objetivas en dashboard con alarmas (per `lex-slo-required` cuando tier-1/2).

### Directriz 05 — Alcance Restringido

**Qué es.** Dominio de actuación estrecho, declarado y respetado. El agente rechaza explícitamente salirse del alcance (p. ej., "no respondo preguntas fuera de conciliación bancaria").

**Por qué importa.** Un alcance amplio expone al agente a casos para los que no fue entrenado, validado u observado. Restringir el alcance es la palanca más fuerte de calidad.

**Pre-operacional.** Muy estrecho — 1 caso de uso, 1 cliente piloto, 1 escenario. Es aceptable que el alcance evolucione durante el PoV (con cambio rastreado).

**Operación Concreta.** Alcance probado y estabilizado (sin cambio en las últimas 2 semanas antes de la DoOC) + playbook documentado de expansión (cómo agregar un escenario sin degradar el agente a `pre-operational`).

### Directriz 06 — Contexto Rico

**Qué es.** Material que orienta al agente más allá del system prompt — few-shot, documentación de dominio, ejemplos negativos curados, histórico de interacciones observadas. Es el puente de aprendizaje entre etapas: un contexto rico en `pre-operational` acelera el logro de la DoOC.

**Por qué importa.** Los LLMs razonan por analogía con ejemplos. Los ejemplos negativos (lo que NO hacer) son tan importantes como los positivos. Sin contexto rico, el agente generaliza mal.

**Pre-operacional.** Few-shot curado (5-15 ejemplos) + 3-5 ejemplos negativos. Documentación opcional.

**Operación Concreta.** Few-shot curado + documentación de dominio + ≥10 ejemplos negativos cubriendo modos de fallo observados + histórico de los últimos 30-90 días usado como contexto dinámico (RAG cuando aplique).

## Rigor diferencial por etapa (cross-tab)

| # | Directriz | `pre-operational` (Claudionor) | `operational-concrete` (Mêtis) |
|---|-----------|--------------------------------|--------------------------------|
| 01 | Identidad | System prompt mínimo viable (~10 líneas) + `stage:` declarado + 1-2 rechazos | Identidad codificada en `docs/{context}/agents/{agent}/system-prompt.md` (canónico per `codex-agent-design-docs`); tono, voz Guardia, escalation declarados |
| 02 | Memoria | Solo corto plazo | 3 capas obligatorias (corto + medio + largo) con retención declarada per `lex-data-retention` |
| 03 | Herramientas | 1-3 herramientas, búsqueda + ejecución simple, log estructurado | Catálogo tripartito (deterministic + ML + MCP) con schema, idempotencia, observability per `lex-observability-required` |
| 04 | Feedback | HITL ligero O 1 métrica objetiva | HITL para irreversibles + critic LLM + ≥3 métricas objetivas; SLO cuando tier-1/2 |
| 05 | Alcance | 1 caso de uso, 1 cliente piloto | Alcance probado, estabilizado ≥2 semanas + playbook de expansión |
| 06 | Contexto | Few-shot (5-15) + 3-5 ejemplos negativos | Few-shot curado + docs de dominio + ≥10 ejemplos negativos + histórico observado de 30-90 días |

## Stage tags en el system prompt (ejemplos canónicos)

### Ejemplo 1 — `stage: pre-operational`

```
# Agente: rec-pov-classifier
# stage: pre-operational
# DoOC gaps:
#   - leading metric: en recolección (D+12 de operación)
#   - observability: 4 días (objetivo: ≥7)
#   - alcance: aún en ajuste (extractos de Bradesco PJ añadidos ayer)
# Owner: warrior-claudionor
# Manual: docs/reconciliation/agents-pov/rec-pov-classifier/pov.md

Eres un clasificador de transacciones bancarias para conciliación.
Dominio: extractos de Itaú PJ y Bradesco PJ.
Rechazo: cualquier pregunta fuera de clasificación de transacciones.
Tono: técnico, directo, sin adornos.

Herramientas disponibles:
- search_history(query): busca clasificaciones anteriores del mismo cliente
- classify(transaction): devuelve categoría + confianza

Feedback: cada clasificación es revisada por un analista Guardia.
```

### Ejemplo 2 — `stage: operational-concrete`

```
# Agente: rec-classifier
# stage: operational-concrete
# DoOC: ✅ validada el 2026-04-12, ADR-018 (docs/adr/ADR-018-rec-classifier-promotion.md)
# tier: tier-2
# Métricas + SLO: docs/reconciliation/agents/rec-classifier/metrics.md
# Owner: warrior-metis; product owner: @ana.santos
# System prompt canónico: docs/reconciliation/agents/rec-classifier/system-prompt.md (codifica rol, tono, voz, escalation)

Rol, dominio, rechazos, tono, voz Guardia: ver system-prompt.md canónico (linkado en el header).

Memoria:
- Corta: ventana de la sesión actual
- Media: últimas 50 clasificaciones del cliente (Redis, TTL 30d)
- Larga: reglas de clasificación versionadas en docs/reconciliation/rules/

Herramientas (catálogo completo en docs/reconciliation/agents/rec-classifier/tools.md):
- deterministic: validate_account, parse_statement, normalize_currency
- ML: classify_transaction, embed_description
- MCP: github (lectura de reglas versionadas)

Feedback:
- HITL: bloqueo en clasificaciones con confianza < 0.85
- Critic: LLM crítico revisa cada batch de 100 antes de emitir
- Métricas: accuracy, reversal_rate, time_to_classification (CloudWatch)
```

### Ejemplo 3 — `stage: legacy-pov`

```
# Agente: support-bot
# stage: legacy-pov
# Creado: 2025-11-03 (anterior al merge de lex-agent-construction-directives)
# Migración planificada: 2026-08-09 (90 días tras el merge)
# Owner: warrior-metis (evaluación de promoción); @joao.silva (interino)
# Gaps conocidos:
#   - sin manual de identidad
#   - sin catálogo de herramientas declarado
#   - feedback solo vía queja en Slack
#   - alcance no estabilizado

Soy el asistente Guardia para clientes...
(prompt original del PoV preservado hasta la migración)
```

## Definition of Operational Concrete (DoOC) — detalle

Cada ítem de la DoOC declarado en la Lex tiene un formato de evidencia esperado. **Los 9 ítems son obligatorios para todo agente en promoción, independientemente del tier de criticidad.** El tier (ítem h) modula lo que el SLO exige después de la promoción — **no dispensa** los ítems (b) y (c): incluso los agentes tier-3 y tier-4 DEBEN tener una métrica leading probada y una métrica lagging declarada; sin eso, la DoOC se rechaza.

| # | Ítem | Formato de evidencia |
|---|------|----------------------|
| (a) | Origen del PoV declarado | Link absoluto a `docs/{context}/agents-pov/{agent}/pov.md` |
| (b) | Métrica leading probada | Número + threshold + ventana (p. ej., `accuracy >= 0.92 en ventana de 7 días con n≥500 clasificaciones`). **Obligatoria en todos los tiers.** |
| (c) | Métrica lagging declarada | Métrica de negocio + baseline (p. ej., `tiempo de cierre mensual: baseline 14d, objetivo 9d`). **Obligatoria en todos los tiers.** |
| (d) | Alcance estabilizado | SHA del commit en `docs/{context}/agents-pov/{agent}/scope.md` + fecha ≥ 2 semanas atrás |
| (e) | Observability data ≥ 7 días | Link al dashboard (CloudWatch, Grafana) + ventana de 7 días cubierta |
| (f) | Stakeholder owner identificado | Nombre, rol, canal de escalado (Slack handle + email) |
| (g) | Capacidad de implementación | Sprint del `warrior-apollo-agents` agendado O ADR justificando el camino alternativo |
| (h) | Tier de criticidad | `tier-1` \| `tier-2` \| `tier-3` \| `tier-4`. Tier-1/2 dispara SLO obligatorio en `docs/{context}/agents/{agent}/metrics.md` per `lex-slo-required` (KPIs + SLI/SLO + dashboards consolidados en el archivo canónico). Tier-3/4 NO dispensa las métricas (b) y (c) — solo dispensa el SLO formal |
| (i) | Stage explícito en el prompt | SHA del commit que añadió `stage: pre-operational` al prompt del PoV |

## Anti-patrones observados

La siguiente lista codifica trampas reales. Cuando aparezcan en revisión, bloquean hasta su resolución.

- **"Es solo un PoV, la identidad clara queda para después."** Identidad ausente en el PoV impide al equipo evaluar si lo que se está probando es lo que se quiere probar.
- **"Vamos a madurarlo después."** Sin checklist y plazo, el "después" nunca llega. La DoOC existe para volver objetivo ese "después".
- **"El alcance se expande conforme aprendemos."** Un alcance móvil impide probar el valor. Cambia el alcance deliberadamente, con SHA, o congélalo.
- **"Confiamos en el agente, no hace falta critic."** Critic no es desconfianza — es un instrumento de observability. Critic es barato y detecta deriva.
- **"Memoria larga = todo el histórico en el contexto."** Mezclar capas dispara latencia y coste. Cada capa tiene una responsabilidad distinta.
- **"Tier-3 no necesita métrica."** El tier define el rigor del SLO, no dispensa de la métrica de valor. Sin métrica no hay DoOC, sin importar el tier.
- **"Legacy-pov es permanente."** No lo es. 90 días tras el merge de esta Lex, los agentes en `legacy-pov` son no conformes per `lex-agent-construction-directives`.

## Referencias

- **Notion (fuente viva — prevalece en divergencia):** "Diretrizes para Construção de Agentes" (`35b36f91ebd281c8a65de122b7234b5d`)
- **Lex correspondiente:** `lex-agent-construction-directives`
- **Lex relacionadas:**
  - `lex-hard-gate-pattern` — formato del bloque HARD-GATE
  - `lex-slo-required` — SLO obligatorio para tier-1/2
  - `lex-observability-required` — trace + metric + log por superficie de runtime
  - `lex-data-retention` — retención por capa de memoria
  - `lex-mcp` — uso correcto de servers MCP en herramientas
  - `lex-idempotency` — idempotencia para herramientas que modifican estado
- **Codex relacionados:**
  - `codex-agent-design-docs` — **manual operacional** del template canónico de 13 archivos (`system-prompt.md`, `tools.md`, `metrics.md`, `memory.md`, `guardrails.md`, etc.); este Codex describe el **rigor conceptual por Directriz**, aquel prescribe la **estructura física**
  - `codex-ai-first-experience` — UX agentic, HITL para irreversibles
  - `codex-incident-response` — ciclo de incidente cuando un agente en producción falla
- **Warriors relacionados (entrega futura):**
  - `warrior-claudionor` (plan-031) — Fábrica de PoV; impone `stage: pre-operational`
  - `warrior-metis` (plan-032) — APM Operación Concreta; valida DoOC y promueve
  - `warrior-apollo-agents` (plan-013) — implementa agentes siguiendo este Codex
- **Externas:**
  - Piaget, J. (1936). *La naissance de l'intelligence chez l'enfant*
  - Vygotsky, L.S. (1978). *Mind in Society: The Development of Higher Psychological Processes*
  - OWASP LLM Top 10 (consultado por `codex-system-prompt` — entrega futura)
