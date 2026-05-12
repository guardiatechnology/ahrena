# Codex: Agent Construction Directives

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Construction of AI agents on the Guardia platform (PoV → Operational Concrete)

## Piaget Analogy (conceptual base)

Jean Piaget described human cognitive development in stages. Guardia applies that structure to AI agents because it provides a shared vocabulary for differential rigor: each stage has distinct, measurable expectations.

| Piaget stage | Age | Trait | Equivalent in agents | Ahrena Warrior |
|--------------|-----|-------|----------------------|----------------|
| Sensorimotor | 0–2 years | Pure reactive, no internal representation | Reactive-only agent, responds to immediate context without tools | Not modeled (degenerate case) |
| Pre-operational | 2–7 years | Symbolic thinking, no reversible logical operation | LLM with light tooling, no deep domain modeling | `warrior-claudionor` (plan-031) |
| Concrete Operations | 7–11 years | Logic applied to concrete objects; reversibility; classification | Agent with full tools + layered memory + real data + structured feedback | `warrior-metis` (plan-032) |
| Formal Operations | 11+ years | Abstract reasoning, planning, hypotheses | Planning, self-reflection, multi-step reasoning over abstract goals | Frontier — not modeled in 2026 |
| Zone of Proximal Development (Vygotsky) | Cross-cutting | Learning mediated by a more experienced peer | Multi-agent + HITL (human or master agent in the loop) | Cross-cutting (Directive 04) |

The choice to operate Guardia between **pre-operational** and **concrete operations** is deliberate: the Formal Operations stage is still a research frontier in 2026 and producing agents there without foundation causes incidents; the sensorimotor stage is insufficient for Guardia's use cases.

## The 6 Directives

Each Directive is detailed with (a) what it is, (b) why it matters, (c) minimum viable version in `pre-operational`, (d) production version in `operational-concrete`.

### Directive 01 — Clear Identity

**What it is.** Explicit definition of the agent's role, purpose, boundaries, and tone in the system prompt. Includes: role (e.g., "transaction classifier"), domain (e.g., "Itaú PJ bank reconciliation"), what it does, what it refuses, tone (formal/informal/technical), and Guardia voice per `lex-brand-voice`.

**Why it matters.** Vague identity produces erratic behavior. Without a declared identity, the agent assumes LLM defaults, which vary by model and version.

**Pre-operational.** Short system prompt (~10 lines) covering role, domain, 1-2 explicit refusals. Acceptable to omit detailed tone.

**Operational Concrete.** Identity encoded in the canonical `docs/{context}/agents/{agent}/system-prompt.md` per `codex-agent-design-docs` — role, domain, enumerated refusals, tone, escalation matrix, Guardia voice. The system prompt is the canonical artifact for Directive 01 (no separate `identity.md` exists in the 13-file template).

### Directive 02 — Layered Memory

**What it is.** Three distinct memory layers: **short-term** (current session window), **medium-term** (customer history / context across N sessions), **long-term** (domain rules, institutional knowledge, learned patterns).

**Why it matters.** Without memory, the agent starts over every turn; with all memory blended together, the context becomes soup and latency explodes. The 3 layers separate volatility and responsibility.

**Pre-operational.** Short-term alone is sufficient. Persistence is optional; acceptable for customer history to be lost between sessions during the PoV.

**Operational Concrete.** Three mandatory layers with a clear owner: short via the LLM window; medium via a store (Redis/DynamoDB) with declared TTL; long via vector store or knowledge base + human review. Each layer has retention declared per `lex-data-retention`.

### Directive 03 — Concrete Tools

**What it is.** Structured capabilities the agent invokes to act beyond text generation. Tripartite catalog: (a) **deterministic** (pure functions, validations, calculations), (b) **ML** (classifiers, embeddings, other inferences), (c) **MCP** (external servers per `lex-mcp`).

**Why it matters.** An agent without tools is just a chatbot; poorly designed tools become attack surface and a source of non-deterministic failure.

**Pre-operational.** Search + simple execution; 1-3 tools are enough. Tools may be hardcoded in the PoV; minimal observability (structured log).

**Operational Concrete.** Full tripartite catalog with explicit schema (OpenAPI/JSON Schema), idempotency where applicable per `lex-idempotency`, full observability (trace + metric + log) per `lex-observability-required`, input validation at boundaries per `lex-python-security`.

### Directive 04 — Explicit Feedback Loop

**What it is.** Declared mechanism for the agent to know whether its response was useful. Three complementary modalities: (a) **HITL** (human in the loop — analyst validates output), (b) **critic** (critic LLM reviews the agent's output), (c) **objective metrics** (business signal — adoption rate, reversal rate, time-to-action).

**Why it matters.** Without feedback, the agent does not learn and the team does not know whether the product is working. Implicit feedback ("the customer didn't complain") is placebo.

**Pre-operational.** Light HITL OR 1 objective metric. Asynchronous feedback is acceptable (weekly manual review).

**Operational Concrete.** HITL for irreversible actions (per `codex-ai-first-experience`) + critic LLM for reversible actions + ≥3 objective metrics on a dashboard with alarms (per `lex-slo-required` when tier-1/2).

### Directive 05 — Restricted Scope

**What it is.** Narrow, declared, and respected operating domain. The agent explicitly refuses to step outside the scope (e.g., "I do not answer questions outside bank reconciliation").

**Why it matters.** A broad scope exposes the agent to cases it was not trained, validated, or observed on. Restricting scope is the strongest quality lever.

**Pre-operational.** Very narrow — 1 use case, 1 pilot customer, 1 scenario. Acceptable for the scope to evolve during the PoV (with tracked changes).

**Operational Concrete.** Scope proven and stabilized (no change in the last 2 weeks before DoOC) + documented expansion playbook (how to add a scenario without downgrading the agent back to `pre-operational`).

### Directive 06 — Rich Context

**What it is.** Material that guides the agent beyond the system prompt — few-shot, domain documentation, curated negative examples, history of observed interactions. It is the learning bridge between stages: rich context in `pre-operational` accelerates reaching DoOC.

**Why it matters.** LLMs reason by analogy with examples. Negative examples (what NOT to do) matter as much as positive ones. Without rich context, the agent generalizes poorly.

**Pre-operational.** Curated few-shot (5-15 examples) + 3-5 negative examples. Documentation optional.

**Operational Concrete.** Curated few-shot + domain documentation + ≥10 negative examples covering observed failure modes + history of the last 30-90 days used as dynamic context (RAG where applicable).

## Differential rigor by stage (cross-tab)

| # | Directive | `pre-operational` (Claudionor) | `operational-concrete` (Mêtis) |
|---|-----------|--------------------------------|--------------------------------|
| 01 | Identity | Minimum viable system prompt (~10 lines) + `stage:` declared + 1-2 refusals | Identity encoded in `docs/{context}/agents/{agent}/system-prompt.md` (canonical per `codex-agent-design-docs`); tone, Guardia voice, escalation declared |
| 02 | Memory | Short-term only | 3 mandatory layers (short + medium + long) with retention declared per `lex-data-retention` |
| 03 | Tools | 1-3 tools, search + simple execution, structured log | Tripartite catalog (deterministic + ML + MCP) with schema, idempotency, observability per `lex-observability-required` |
| 04 | Feedback | Light HITL OR 1 objective metric | HITL for irreversibles + critic LLM + ≥3 objective metrics; SLO when tier-1/2 |
| 05 | Scope | 1 use case, 1 pilot customer | Scope proven, stabilized ≥2 weeks + expansion playbook |
| 06 | Context | Few-shot (5-15) + 3-5 negative examples | Curated few-shot + domain docs + ≥10 negative examples + observed history of 30-90 days |

## Stage tags in the system prompt (canonical examples)

### Example 1 — `stage: pre-operational`

```
# Agent: rec-pov-classifier
# stage: pre-operational
# DoOC gaps:
#   - leading metric: still being collected (D+12 in operation)
#   - observability: 4 days (target: ≥7)
#   - scope: still being tuned (Bradesco PJ statements added yesterday)
# Owner: warrior-claudionor
# Manual: docs/reconciliation/agents-pov/rec-pov-classifier/pov.md

You are a bank transaction classifier for reconciliation.
Domain: Itaú PJ and Bradesco PJ bank statements.
Refusal: any question outside transaction classification.
Tone: technical, direct, no flourishes.

Available tools:
- search_history(query): looks up earlier classifications for the same customer
- classify(transaction): returns category + confidence

Feedback: every classification is reviewed by a Guardia analyst.
```

### Example 2 — `stage: operational-concrete`

```
# Agent: rec-classifier
# stage: operational-concrete
# DoOC: ✅ validated on 2026-04-12, ADR-018 (docs/adr/ADR-018-rec-classifier-promotion.md)
# tier: tier-2
# Metrics + SLO: docs/reconciliation/agents/rec-classifier/metrics.md
# Owner: warrior-metis; product owner: @ana.santos
# Canonical system prompt: docs/reconciliation/agents/rec-classifier/system-prompt.md (encodes role, tone, voice, escalation)

Role, domain, refusals, tone, Guardia voice: see canonical system-prompt.md (linked in the header).

Memory:
- Short: current session window
- Medium: customer's last 50 classifications (Redis, TTL 30d)
- Long: classification rules versioned under docs/reconciliation/rules/

Tools (full catalog at docs/reconciliation/agents/rec-classifier/tools.md):
- deterministic: validate_account, parse_statement, normalize_currency
- ML: classify_transaction, embed_description
- MCP: github (reading versioned rules)

Feedback:
- HITL: hold classifications with confidence < 0.85
- Critic: critic LLM reviews every batch of 100 before emission
- Metrics: accuracy, reversal_rate, time_to_classification (CloudWatch)
```

### Example 3 — `stage: legacy-pov`

```
# Agent: support-bot
# stage: legacy-pov
# Created: 2025-11-03 (before lex-agent-construction-directives merge)
# Migration planned: 2026-08-09 (90 days after merge)
# Owner: warrior-metis (promotion assessment); @joao.silva (interim)
# Known gaps:
#   - no identity manual
#   - no declared tools catalog
#   - feedback only via Slack complaints
#   - scope not stabilized

I am the Guardia assistant for customers...
(original PoV prompt preserved until migration)
```

## Definition of Operational Concrete (DoOC) — detail

Each DoOC item declared in the Lex has an expected evidence format. **All 9 items are mandatory for any agent in promotion, regardless of the criticality tier.** The tier (item h) modulates what the SLO demands after promotion — it does **not** waive items (b) and (c): even tier-3 and tier-4 agents MUST have a proven leading metric and a declared lagging metric; without those, the DoOC fails.

| # | Item | Evidence format |
|---|------|-----------------|
| (a) | Declared PoV origin | Absolute link to `docs/{context}/agents-pov/{agent}/pov.md` |
| (b) | Proven leading metric | Number + threshold + window (e.g., `accuracy >= 0.92 over a 7-day window with n≥500 classifications`). **Mandatory across all tiers.** |
| (c) | Declared lagging metric | Business metric + baseline (e.g., `monthly close time: baseline 14d, target 9d`). **Mandatory across all tiers.** |
| (d) | Stabilized scope | SHA of the commit under `docs/{context}/agents-pov/{agent}/scope.md` + date ≥ 2 weeks ago |
| (e) | Observability data ≥ 7 days | Dashboard link (CloudWatch, Grafana) + a 7-day window covered |
| (f) | Identified stakeholder owner | Name, role, escalation channel (Slack handle + email) |
| (g) | Implementation capacity | Scheduled `warrior-apollo-agents` sprint OR ADR justifying the alternative path |
| (h) | Criticality tier | `tier-1` \| `tier-2` \| `tier-3` \| `tier-4`. Tier-1/2 triggers a mandatory SLO under `docs/{context}/agents/{agent}/metrics.md` per `lex-slo-required` (KPIs + SLI/SLO + dashboards consolidated in the canonical file). Tier-3/4 does NOT waive metrics (b) and (c) — it only waives the formal SLO |
| (i) | Explicit stage in the prompt | SHA of the commit that added `stage: pre-operational` to the PoV prompt |

## Observed anti-patterns

The list below codifies real traps. When they appear in review, they block until resolved.

- **"It's only a PoV, clear identity can wait."** Missing identity in the PoV prevents the team from assessing whether what is being proven is what they want to prove.
- **"We'll mature it later."** Without a checklist and a deadline, "later" never arrives. The DoOC exists to make "later" objective.
- **"Scope expands as we learn."** A moving scope prevents proving value. Change scope deliberately, with a SHA, or freeze it.
- **"We trust the agent, no critic needed."** Critic is not distrust — it is an observability instrument. Critic is cheap and detects drift.
- **"Long memory = all history in context."** Blending layers blows up latency and cost. Each layer has a distinct responsibility.
- **"Tier-3 doesn't need a metric."** Tier defines SLO rigor, not exemption from a value metric. No metric means no DoOC, regardless of tier.
- **"Legacy-pov is permanent."** It is not. 90 days after this Lex's merge, agents in `legacy-pov` are non-compliant per `lex-agent-construction-directives`.
