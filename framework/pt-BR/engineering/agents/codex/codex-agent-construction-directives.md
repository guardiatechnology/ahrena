# Codex: Diretrizes para Construção de Agentes

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Engenharia — Construção de agentes de IA sobre a plataforma Guardia (PoV → Operação Concreta)

## Visão Geral

Manual de referência para arquitetar agentes de IA na plataforma Guardia. Codifica em forma operacional o conteúdo do manual "Diretrizes para Construção de Agentes" mantido em Notion (source-of-truth viva). Acompanha a Lex `lex-agent-construction-directives` e fornece o detalhamento conceitual, exemplos canônicos e rigor diferencial que a Lex referencia.

Este Codex é consultado quando se constrói, revisa ou promove um agente — por humanos, por `warrior-claudionor` (Fábrica de PoV), por `warrior-metis` (APM Operação Concreta), por `warrior-apollo-agents` (implementação) e por `warrior-athena` (Gate 2 quando a feature toca agentes).

## Contexto

- **Domínio:** construção de agentes de IA (system prompt, memória, ferramentas, feedback, escopo, contexto) e promoção de PoV para Operação Concreta
- **Público-alvo:** engenheiros de agentes, tech leads, product managers, agentes de IA que orquestram a construção
- **Atualização:** Notion é a fonte viva; este Codex é o snapshot operacional. Revisão trimestral; em caso de divergência, **Notion prevalece**.

## Analogia de Piaget (base conceitual)

Jean Piaget descreveu o desenvolvimento cognitivo humano em estágios. A Guardia aplica essa estrutura aos agentes de IA porque ela fornece um vocabulário compartilhado para o rigor diferencial: cada estágio tem expectativas mensuráveis distintas.

| Fase de Piaget | Idade | Característica | Equivalente em agentes | Warrior Ahrena |
|----------------|-------|----------------|------------------------|----------------|
| Sensório-motor | 0–2 anos | Reativo puro, sem representação interna | Agente apenas reativo, só responde ao contexto imediato sem ferramentas | Não modelado (caso degenerado) |
| Pré-operacional | 2–7 anos | Pensamento simbólico, sem operação lógica reversível | LLM com tooling leve, sem modelagem profunda de domínio | `warrior-claudionor` (plan-031) |
| Operações Concretas | 7–11 anos | Lógica aplicada a objetos concretos; reversibilidade; classificação | Agente com tools completas + memória em camadas + dados reais + feedback estruturado | `warrior-metis` (plan-032) |
| Operações Formais | 11+ anos | Raciocínio abstrato, planejamento, hipóteses | Planejamento, auto-reflexão, multi-step reasoning sobre objetivos abstratos | Fronteira — não modelado em 2026 |
| Zona Proximal (Vygotsky) | Cross-cutting | Aprendizado mediado por par mais experiente | Multi-agent + HITL (humano ou agente master no loop) | Cross-cutting (Diretriz 04) |

A escolha de operar a Guardia entre **pré-operacional** e **operações concretas** é deliberada: o estágio de Operações Formais ainda é fronteira de pesquisa em 2026 e produzir agentes ali sem fundamento causa incidentes; o estágio sensório-motor é insuficiente para casos de uso da Guardia.

## As 6 Diretrizes

Cada Diretriz é detalhada com (a) o que é, (b) por que importa, (c) versão mínima viável em `pre-operational`, (d) versão de produção em `operational-concrete`.

### Diretriz 01 — Identidade Clara

**O que é.** Definição explícita do papel, propósito, limites e tom do agente no system prompt. Inclui: papel (ex: "classificador de transações"), domínio (ex: "reconciliação bancária PJ Itaú"), o que faz, o que recusa, tom (formal/informal/técnico), e voz Guardia per `lex-brand-voice`.

**Por que importa.** Identidade vaga produz comportamento errático. Sem identidade declarada, o agente assume defaults do LLM, que variam por modelo e versão.

**Pré-operacional.** System prompt curto (~10 linhas) cobrindo papel, domínio, 1-2 recusas explícitas. Aceitável omitir tom detalhado.

**Operação Concreta.** Manual de identidade completo em `docs/{context}/agents/{agent}/identity.md` — papel, domínio, recusas enumeradas, tom, escalation matrix, voz Guardia. System prompt referencia o manual.

### Diretriz 02 — Memória em Camadas

**O que é.** Três camadas de memória distintas: **curto-prazo** (janela da sessão atual), **médio-prazo** (histórico do cliente/contexto de N sessões), **longo-prazo** (regras de domínio, conhecimento institucional, padrões aprendidos).

**Por que importa.** Sem memória, o agente recomeça a cada turno; com toda memória junta, o contexto vira sopa e a latência explode. As 3 camadas separam volatilidade e responsabilidade.

**Pré-operacional.** Curto-prazo suficiente. Persistência opcional; aceitável que o histórico do cliente seja perdido entre sessões durante o PoV.

**Operação Concreta.** Três camadas mandatórias com responsável claro: curto via janela do LLM; médio via store (Redis/DynamoDB) com TTL declarado; longo via vector store ou knowledge base + revisão humana. Cada camada tem retenção declarada per `lex-data-retention`.

### Diretriz 03 — Ferramentas Concretas

**O que é.** Capacidades estruturadas que o agente invoca para agir além de gerar texto. Catálogo tripartido: (a) **deterministic** (funções puras, validações, cálculos), (b) **ML** (classificadores, embeddings, outras inferências), (c) **MCP** (servers externos per `lex-mcp`).

**Por que importa.** Agente sem ferramentas é só um chatbot; ferramentas mal projetadas viram superfície de ataque e ponto de falha não-determinística.

**Pré-operacional.** Busca + execução simples; 1-3 ferramentas suficientes. Ferramentas podem ser hardcoded no PoV; observability mínima (log estruturado).

**Operação Concreta.** Catálogo tripartido completo com schema explícito (OpenAPI/JSON Schema), idempotência onde aplicável per `lex-idempotency`, observability completa (trace + metric + log) per `lex-observability-required`, validação de input em fronteira per `lex-python-security`.

### Diretriz 04 — Loop de Feedback Explícito

**O que é.** Mecanismo declarado para o agente saber se sua resposta foi útil. Três modalidades complementares: (a) **HITL** (humano no loop — analista valida output), (b) **critic** (LLM crítico revisa output do agente), (c) **métricas objetivas** (signal de negócio — taxa de adoção, reversão, tempo até ação).

**Por que importa.** Sem feedback, o agente não aprende e a equipe não sabe se o produto está funcionando. Feedback implícito ("o cliente não reclamou") é placebo.

**Pré-operacional.** HITL leve OU 1 métrica objetiva. Aceitável feedback assíncrono (revisão semanal manual).

**Operação Concreta.** HITL para ações irreversíveis (per `codex-ai-first-experience`) + critic LLM para ações reversíveis + ≥3 métricas objetivas em dashboard com alarmes (per `lex-slo-required` quando tier-1/2).

### Diretriz 05 — Escopo Restrito

**O que é.** Domínio de atuação estreito, declarado e respeitado. O agente recusa explicitamente sair do escopo (ex: "não respondo a perguntas fora de reconciliação bancária").

**Por que importa.** Escopo amplo expõe o agente a casos para os quais não foi treinado, validado ou observado. Restringir escopo é a alavanca mais forte de qualidade.

**Pré-operacional.** Muito estreito — 1 caso de uso, 1 cliente piloto, 1 cenário. Aceitável que escopo evolua durante o PoV (com mudança rastreada).

**Operação Concreta.** Escopo provado e estabilizado (sem mudança nas últimas 2 semanas antes da DoOC) + playbook documentado de expansão (como adicionar um cenário sem rebaixar o agente para `pre-operational`).

### Diretriz 06 — Contexto Rico

**O que é.** Material que orienta o agente além do system prompt — few-shot, documentação de domínio, exemplos negativos curados, histórico de interações observadas. É a ponte de aprendizado entre estágios: contexto rico no `pre-operational` acelera o atingimento de DoOC.

**Por que importa.** LLMs raciocinam por analogia com exemplos. Exemplos negativos (o que NÃO fazer) são tão importantes quanto positivos. Sem contexto rico, o agente generaliza mal.

**Pré-operacional.** Few-shot curado (5-15 exemplos) + 3-5 exemplos negativos. Documentação opcional.

**Operação Concreta.** Few-shot curado + documentação de domínio + ≥10 exemplos negativos cobrindo modos de falha observados + histórico de últimos 30-90 dias usado como contexto dinâmico (RAG quando aplicável).

## Rigor diferencial por estágio (cross-tab)

| # | Diretriz | `pre-operational` (Claudionor) | `operational-concrete` (Mêtis) |
|---|----------|--------------------------------|--------------------------------|
| 01 | Identidade | System prompt mínimo viável (~10 linhas) + `stage:` declarado + 1-2 recusas | Manual completo em `docs/{context}/agents/{agent}/identity.md`; system prompt referencia o manual; tom, voz Guardia, escalation declarados |
| 02 | Memória | Curto-prazo apenas | 3 camadas mandatórias (curto + médio + longo) com retenção declarada per `lex-data-retention` |
| 03 | Ferramentas | 1-3 ferramentas, busca + execução simples, log estruturado | Catálogo tripartido (deterministic + ML + MCP) com schema, idempotência, observability per `lex-observability-required` |
| 04 | Feedback | HITL leve OU 1 métrica objetiva | HITL para irreversíveis + critic LLM + ≥3 métricas objetivas; SLO quando tier-1/2 |
| 05 | Escopo | 1 caso de uso, 1 cliente piloto | Escopo provado, estabilizado ≥2 semanas + playbook de expansão |
| 06 | Contexto | Few-shot (5-15) + 3-5 exemplos negativos | Few-shot curado + docs de domínio + ≥10 exemplos negativos + histórico observado de 30-90 dias |

## Stage tags em system prompt (exemplos canônicos)

### Exemplo 1 — `stage: pre-operational`

```
# Agente: rec-pov-classifier
# stage: pre-operational
# DoOC gaps:
#   - leading metric: em coleta (D+12 de operação)
#   - observability: 4 dias (alvo: ≥7)
#   - escopo: ainda em ajuste (extratos do Bradesco PJ adicionados ontem)
# Owner: warrior-claudionor
# Manual: docs/reconciliation/agents-pov/rec-pov-classifier/pov.md

Você é um classificador de transações bancárias para reconciliação.
Domínio: extratos de Itaú PJ e Bradesco PJ.
Recusa: qualquer pergunta fora de classificação de transação.
Tom: técnico, direto, sem floreios.

Ferramentas disponíveis:
- search_history(query): busca classificações anteriores do mesmo cliente
- classify(transaction): retorna categoria + confiança

Feedback: cada classificação é revisada por analista Guardia.
```

### Exemplo 2 — `stage: operational-concrete`

```
# Agente: rec-classifier
# stage: operational-concrete
# DoOC: ✅ validada em 2026-04-12, ADR-018 (docs/adr/ADR-018-rec-classifier-promotion.md)
# tier: tier-2
# SLO: docs/reconciliation/metrics/slo-rec-classifier.yaml
# Owner: warrior-metis; product owner: @ana.santos
# Manual: docs/reconciliation/agents/rec-classifier/identity.md (consulte para tom, voz, escalation)

Papel, domínio, recusas, tom, voz Guardia: ver manual.

Memória:
- Curta: janela da sessão atual
- Média: últimas 50 classificações do cliente (Redis, TTL 30d)
- Longa: regras de classificação versionadas em docs/reconciliation/rules/

Ferramentas (catálogo completo em docs/reconciliation/agents/rec-classifier/tools/):
- deterministic: validate_account, parse_statement, normalize_currency
- ML: classify_transaction, embed_description
- MCP: github (leitura de regras versionadas)

Feedback:
- HITL: bloqueio em classificações com confiança < 0.85
- Critic: LLM crítico revisa cada batch de 100 antes de emitir
- Métricas: accuracy, reversal_rate, time_to_classification (CloudWatch)
```

### Exemplo 3 — `stage: legacy-pov`

```
# Agente: support-bot
# stage: legacy-pov
# Criado: 2025-11-03 (anterior ao merge de lex-agent-construction-directives)
# Migração planejada: 2026-08-09 (90 dias após merge)
# Owner: warrior-metis (avaliação de promoção); @joao.silva (interim)
# Gaps conhecidos:
#   - sem manual de identidade
#   - sem catálogo de ferramentas declarado
#   - feedback apenas via reclamação no Slack
#   - escopo não estabilizado

Sou o assistente Guardia para clientes...
(prompt original do PoV preservado até migração)
```

## Definition of Operational Concrete (DoOC) — detalhamento

Cada item da DoOC declarado na Lex tem formato de evidência esperado. **Os 9 itens são obrigatórios para qualquer agente em promoção, independente do tier de criticidade.** O tier (item h) modula o que o SLO exige depois da promoção — ele **não dispensa** os itens (b) e (c): mesmo agentes tier-3 e tier-4 DEVEM ter métrica leading provada e métrica lagging declarada; sem isso, a DoOC reprova.

| # | Item | Formato de evidência |
|---|------|----------------------|
| (a) | Origem do PoV declarada | Link absoluto para `docs/{context}/agents-pov/{agent}/pov.md` |
| (b) | Métrica leading provada | Número + threshold + janela (ex: `accuracy >= 0.92 em janela de 7 dias com n≥500 classificações`). **Obrigatória em todos os tiers.** |
| (c) | Métrica lagging declarada | Métrica de negócio + baseline (ex: `tempo de fechamento mensal: baseline 14d, alvo 9d`). **Obrigatória em todos os tiers.** |
| (d) | Escopo estabilizado | SHA do commit em `docs/{context}/agents-pov/{agent}/scope.md` + data ≥ 2 semanas atrás |
| (e) | Observability data ≥ 7 dias | Link para dashboard (CloudWatch, Grafana) + janela de 7 dias coberta |
| (f) | Stakeholder owner identificado | Nome, papel, canal de escalonamento (Slack handle + email) |
| (g) | Capacidade de implementação | Sprint do `warrior-apollo-agents` agendado OU ADR justificando caminho alternativo |
| (h) | Tier de criticidade | `tier-1` \| `tier-2` \| `tier-3` \| `tier-4`. Tier-1/2 dispara SLO obrigatório em `docs/{context}/metrics/slo-{agent}.yaml` per `lex-slo-required`. Tier-3/4 NÃO dispensa as métricas (b) e (c) — apenas dispensa SLO formal |
| (i) | Stage explícito no prompt | SHA do commit que adicionou `stage: pre-operational` ao prompt do PoV |

## Anti-padrões observados

A lista a seguir codifica armadilhas reais. Quando aparecerem em revisão, são bloqueio até resolução.

- **"É só um PoV, identidade clara fica para depois."** Identidade ausente no PoV impede a equipe de avaliar se o que está sendo provado é o que se quer provar.
- **"Vamos amadurecer depois."** Sem checklist e prazo, o "depois" nunca chega. A DoOC existe para tornar "depois" objetivo.
- **"O escopo expande conforme aprendemos."** Escopo móvel impede provar valor. Mude o escopo deliberadamente, com SHA, ou congele.
- **"Confiamos no agente, não precisa de critic."** Critic não é desconfiança — é instrumento de observability. Critic é barato e detecta deriva.
- **"Memória longa = todo histórico no contexto."** Embaralhar camadas explode latência e custo. Cada camada tem responsabilidade distinta.
- **"Tier-3 não precisa de métrica."** Tier define rigor de SLO, não dispensa métrica de valor. Sem métrica não há DoOC, independente do tier.
- **"Legacy-pov é permanente."** Não é. 90 dias após o merge desta Lex, agentes em `legacy-pov` são não-conformes per `lex-agent-construction-directives`.

## Referências

- **Notion (fonte viva — prevalece em divergência):** "Diretrizes para Construção de Agentes" (`35b36f91ebd281c8a65de122b7234b5d`)
- **Lex correspondente:** `lex-agent-construction-directives`
- **Lex relacionadas:**
  - `lex-hard-gate-pattern` — formato do bloco HARD-GATE
  - `lex-slo-required` — SLO obrigatório para tier-1/2
  - `lex-observability-required` — trace + metric + log por superfície de runtime
  - `lex-data-retention` — retenção por camada de memória
  - `lex-mcp` — uso correto de servers MCP em ferramentas
  - `lex-idempotency` — idempotência para ferramentas que modificam estado
- **Codex relacionados:**
  - `codex-ai-first-experience` — UX agentic, HITL para irreversíveis
  - `codex-incident-response` — ciclo de incidente quando agente em produção falha
- **Warriors relacionados (entrega futura):**
  - `warrior-claudionor` (plan-031) — Fábrica de PoV; impõe `stage: pre-operational`
  - `warrior-metis` (plan-032) — APM Operação Concreta; valida DoOC e promove
  - `warrior-apollo-agents` (plan-013) — implementa agentes seguindo este Codex
- **Externas:**
  - Piaget, J. (1936). *La naissance de l'intelligence chez l'enfant*
  - Vygotsky, L.S. (1978). *Mind in Society: The Development of Higher Psychological Processes*
  - OWASP LLM Top 10 (consultado por `codex-system-prompt` — futura entrega)
