# Lexis: Estrutura Mandatória dos Documentos de Design de Agent

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma Guardia — eixo Agent Design (documentos produzidos por `warrior-metis` para promover e operar agentes)

## Propósito

A construção de agentes na plataforma Guardia exige rigor de forma para que o resultado seja revisável, comparável entre agentes e governável em produção. Sem uma estrutura única para os arquivos de design, cada agente acaba descrito em local diferente, com seções diferentes, e a promoção de `pre-operational` para `operational-concrete` torna-se subjetiva. Esta Lexis fixa o local físico dos artefatos, o snapshot de governança da DoOC e a reciprocidade obrigatória com o eixo Feature Design.

A Lexis complementa — mas não substitui — `lex-agent-construction-directives`: aquela governa **o quê** um agente DEVE ter (6 Diretrizes + 9 itens da DoOC); esta governa **onde** e **em que forma** isso DEVE estar documentado para que a promoção e a operação sejam auditáveis.

## Lei

> **Todo agent em estado `operational-concrete` na plataforma Guardia DEVE ter (a) os 13 arquivos canônicos em `docs/{context}/agents/{agent}/` per `codex-agent-design-docs` (Hub & Spoke), (b) `docs/{context}/dooc/{agent}.md` preenchido per `lex-agent-construction-directives` HARD-GATE, (c) `overview.md` com campo `serves_features` populado, (d) reciprocidade em `docs/{context}/feature-agent-map.md` (forward e reverse mapping consistentes entre features e agents), (e) `warrior-metis` declarada como autora (PR ref, session-id ou assinatura `authored_by: warrior-metis` no header de `overview.md`).**

```
<HARD-GATE>
warrior-metis, warrior-apollo-agents e qualquer outro agente NÃO PODE promover agent para `operational-concrete` (merge em main, deploy em produção) sem TODAS as 5 preconditions:

  (a) 13 arquivos presentes em `docs/{context}/agents/{agent}/`: `overview.md`, `orchestrator.md`, `specialists/{name}.md` (≥1), `tools.md`, `memory.md`, `reasoning-loop.md`, `feedback.md`, `context-pack.md`, `system-prompt.md`, `metrics.md`, `guardrails.md`, `authorization.md`, `escalation.md`
  (b) `docs/{context}/dooc/{agent}.md` existe e satisfaz `lex-agent-construction-directives` HARD-GATE (9 itens da DoOC com evidence ou N/A justificado por ADR/PDR quando `entry_mode` ≠ `with-pov`)
  (c) `agents/{agent}/overview.md` campo `serves_features` populado com lista válida de features existentes em `docs/{context}/features/`
  (d) `docs/{context}/feature-agent-map.md` reflete a relação: forward (feature → agents) e reverse (agent → features) consistentes; nenhum agent listado em uma feature sem reciprocidade no `serves_features` do agent, e nenhuma feature listada em `serves_features` sem reciprocidade em `served_by_agents`
  (e) `warrior-metis` declarada como autora — PR ref no header de `overview.md` (campo `PR ref: {owner/repo#NNN}`) OU `authored_by: warrior-metis` no header OU session-id canônico em commit message

Esta regra aplica-se a TODO agent em promoção para `operational-concrete`, independentemente de:
  - tamanho percebido ("é só um agent simples")
  - urgência declarada ("o cliente precisa hoje")
  - quem solicitou ("o CEO pediu")
  - confiança da equipe ("já testamos bastante")

Exceções declaradas:
  - Agents em `pre-operational` (PoV produzida por `warrior-claudionor`) ficam FORA desta HARD-GATE — sua estrutura mínima viável é definida em `codex-agent-construction-directives` (rigor diferencial por estágio).
  - Agents em `legacy-pov` (anteriores ao merge desta Lexis) podem ser promovidos com DoOC retroativa + ADR per a cláusula de transição de `lex-agent-construction-directives` (90 dias após merge). Reciprocidade em `feature-agent-map.md` continua obrigatória.
</HARD-GATE>
```

## Abrangência

- **Aplica-se a:** todo agent que serve features de produção na plataforma Guardia (Isac, agents de reconciliação, classificação fiscal/contábil, fechamento, futuros agents). Inclui agents que cobrem apenas um caso de uso (1..1) e agents que cobrem múltiplas features (1..N).
- **Agentes vinculados:** `warrior-metis` (autora dos 13 arquivos + `dooc/{agent}.md`), `warrior-apollo-agents` (consumidor durante implementação), `warrior-athena` (Gate 2 quando feature toca `docs/**/agents/**`), `warrior-prometheus` (coordena reciprocidade Feature ↔ Agent).
- **Exceções:** apenas as duas declaradas no `<HARD-GATE>` (agents `pre-operational` e `legacy-pov`).

## Consequências de Violação

1. **Bloqueio automático:** Gate 2 (`kata-quality-gate`) rejeita PRs de promoção que não satisfaçam as 5 preconditions. PRs com `serves_features` inconsistente com `served_by_agents` (reciprocidade quebrada) são bloqueados.
2. **Alerta:** notifica `warrior-metis`, `warrior-prometheus` (eixo Feature) e o owner do agent (campo `Owner` em `overview.md`).
3. **Remediação:** completar os 13 arquivos, preencher `dooc/{agent}.md`, atualizar `feature-agent-map.md` para refletir reciprocidade, e republicar o PR de promoção. Em deploy emergencial, rollback é obrigatório até a remediação.

## Exemplos

### Correto

Agent `rec-classifier` em capability `reconciliation` promovido em PR #543:

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
    │   └── rec-classifier.md          # 9 itens com evidence; entry_mode: with-pov
    ├── features/
    │   ├── transaction-classification.md   # served_by_agents: [rec-classifier]
    │   └── monthly-close-acceleration.md   # served_by_agents: [rec-classifier]
    └── feature-agent-map.md           # forward: transaction-classification → rec-classifier
                                       # reverse: rec-classifier → transaction-classification, monthly-close-acceleration
```

Reciprocidade verificada: `serves_features` em `rec-classifier/overview.md` lista as duas features, e cada feature lista o agent em `served_by_agents`. Promoção aprovada em Gate 2.

### Incorreto

```
docs/
└── reconciliation/
    ├── agents/
    │   └── rec-classifier/
    │       ├── overview.md            # serves_features: [transaction-classification, refund-detection]
    │       └── ... (13 arquivos)
    ├── features/
    │   └── transaction-classification.md   # served_by_agents: [rec-classifier]
    │                                       # ❌ refund-detection não existe
    └── feature-agent-map.md           # ❌ forward não inclui refund-detection
```

Reciprocidade quebrada: `serves_features` aponta para feature inexistente (`refund-detection`) e `feature-agent-map.md` não reflete. **Gate 2 reprova** — precondition (c) e (d) violadas.

Outro caso incorreto: agent promovido sem `dooc/{agent}.md` ("vamos preencher depois"). Sem snapshot validado per `lex-agent-construction-directives`, precondition (b) viola; promoção bloqueada.

## Validação Automatizada

- **Ferramenta:** verificação pelo próprio agente (`warrior-metis`) antes da promoção + lint no Gate 2 (`kata-quality-gate`) detectando: ausência dos 13 arquivos, `dooc/{agent}.md` faltante, campo `serves_features` vazio em `operational-concrete`, dessincronia entre `serves_features` ↔ `served_by_agents` (reciprocidade), ausência de `authored_by` ou PR ref no header de `overview.md`. No futuro: `kata-agent-design-validate` formalizando os 5 checks.
- **Momento:** Gate 2 do fluxo Issue-Driven; PR review da promoção; pre-deploy de qualquer agent em `operational-concrete`; auditoria periódica de agents em produção.
- **Métrica:** 0 agents `operational-concrete` sem as 5 preconditions ✅; 0 features com `served_by_agents` apontando para agent inexistente; 0 agents com `serves_features` apontando para feature inexistente; 100% das promoções com `warrior-metis` rastreada como autora.

## Referências

- `codex-agent-design-docs` — manual com os 15 templates (13 arquivos do agent + dooc + feature-agent-map)
- `lex-agent-construction-directives` — Lei mestre (6 Diretrizes + HARD-GATE da DoOC)
- `codex-agent-construction-directives` — fundação conceitual (Piaget, stage tags, rigor diferencial, formato de evidências)
- `lex-feature-design-docs`, `codex-feature-design-docs` — eixo paralelo Feature Design (reciprocidade `serves_features` ↔ `served_by_agents`)
- `lex-hard-gate-pattern` — formato do bloco `<HARD-GATE>` utilizado nesta Lexis
- `warrior-metis` — autora dos artefatos do eixo Agent
- `warrior-apollo-agents` — consumidor de implementação
- `warrior-athena` — orquestra Gate 2 quando feature toca `docs/**/agents/**`
- `warrior-prometheus` — coordena reciprocidade Feature ↔ Agent
