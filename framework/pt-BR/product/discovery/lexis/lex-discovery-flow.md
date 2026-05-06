# Lexis: Fluxo de Product Discovery — Insight a Idea

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Product Discovery — produção de insights, transição de status, e promoção de insight aprovado a Idea no Ahrena

## Propósito

Garantir que toda Idea no Ahrena tenha origem rastreável em insights aprovados por humanos, e que a evolução de status de um insight ocorra exclusivamente por decisão humana explícita. Sem essa lei, Ideas nascem sem evidência e insights deslizam de `proposed` a estados terminais sem revisão, quebrando a auditabilidade do Discovery.

## Lei

> **Toda Idea no Ahrena (`docs/discovery/{topic}/ideas/{NNN}-{slug}.md`) DEVE ter sido criada por `warrior-phanes` exclusivamente a partir de um ou mais insights cujo `status` é `approved`, com todos os 5 campos obrigatórios do schema preenchidos, e o insight de origem DEVE ser atualizado para `status: promoted` com `idea_ref` apontando para a Idea criada. Toda mudança de `status` de um insight para qualquer valor diferente de `proposed` DEVE ser conduzida por decisão humana explícita registrada (mensagem na sessão, comentário em PR, ou instrução literal); `warrior-pitia` NÃO PODE alterar status por iniciativa própria, exceto a criação inicial em `proposed`.**

## Abrangência

- **Aplica-se a:** todos os insights e ideas produzidos no contexto Ahrena, em qualquer projeto que adote o framework
- **Agentes vinculados:** `warrior-pitia`, `warrior-phanes`, e qualquer outro agente que crie ou modifique arquivos sob `docs/discovery/`
- **Exceções:** Nenhuma. Lexis não admitem exceções

<HARD-GATE>
warrior-phanes NÃO DEVE promover um insight a Idea sem que TODAS as
pré-condições abaixo sejam atendidas:

  (a) insight.status == approved (decisão humana registrada)
  (b) Idea referencia ≥1 insight em linked_insights[]
  (c) Idea preenche os 5 campos obrigatórios do schema:
      problem, hypothesis, target_user, success_metric, effort_estimate
  (d) Idea.topic coincide com insight.topic em TODOS os linked_insights[]
  (e) Phanes atualiza o insight de origem para status: promoted +
      preenche idea_ref apontando para a Idea criada

Esta regra aplica-se a TODA criação de Idea no Ahrena, independentemente de:
  - tamanho percebido ("é só um experimento")
  - validação verbal ("o stakeholder já aprovou na call")
  - obviedade percebida ("o insight é trivial")
  - urgência declarada ("precisamos da Idea para a sprint que começa amanhã")

Exceção única: nenhuma.
</HARD-GATE>

<HARD-GATE>
warrior-pitia NÃO DEVE alterar o status de um insight para qualquer
valor diferente de "proposed" sem direção humana explícita.

Pré-condições obrigatórias para qualquer transição de status diferente
de `[*] → proposed`:

  (a) Existe instrução humana explícita identificando o insight pelo
      seu `id` ou path canônico
  (b) A transição-alvo é válida na máquina de estados definida em
      codex-discovery-artifacts (tabela de transições)
  (c) Para under_review → refining: humano forneceu feedback acionável
      por escrito
  (d) Para refining → under_review: a v2 do insight foi efetivamente
      redigida, com `updated_at` atualizado

Esta regra aplica-se a TODOS os insights produzidos por warrior-pitia,
independentemente de:
  - obviedade do feedback ("o ajuste é trivial")
  - histórico de casos similares ("Pítia já viu isso antes")
  - urgência declarada
  - confiança da equipe

Exceção única: a criação inicial do insight (`[*] → proposed`) é
da própria warrior-pitia e não exige direção humana — apenas a
existência de pelo menos uma referência em `source_refs[]`.
</HARD-GATE>

## Consequências de Violação

1. **Bloqueio automático:** PR rejeitado quando o reviewer detecta (a) Idea sem `linked_insights[]` válido, (b) Idea com algum dos 5 campos obrigatórios vazio ou nulo, (c) insight cujo status mudou sem evidência humana correspondente, ou (d) `topic` divergente entre Idea e seus insights de origem.
2. **Alerta:** notifica o stakeholder responsável pelo `topic` e o autor humano que conduzia a avaliação.
3. **Remediação:** o autor do PR escolhe entre (a) corrigir a Idea/insight para satisfazer todas as precondições do HARD-GATE aplicável, ou (b) reverter a transição inválida e reabrir o ciclo a partir do estado anterior válido.

## Exemplos

### Correto

```yaml
# docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
---
id: "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
topic: "scheduled-payments-research"
status: approved          # <- humano aprovou explicitamente em PR review
source_refs:
  - "docs/transcripts/interview-2026-05-04-accountant-X.md"
created_at: "2026-05-04T10:00:00Z"
updated_at: "2026-05-08T14:30:00Z"
---

# warrior-phanes lê o insight aprovado e produz a Idea:
# docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md
---
id: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
topic: "scheduled-payments-research"          # <- coincide com o topic do insight
problem: "Contadores perdem 4h/semana conciliando ERP e extrato bancário."
hypothesis: "Sugestão automática com confiança ≥90% será aceita em ≥70% dos casos, reduzindo tempo manual em ≥60%."
target_user: "Contador operacional em escritórios com 50–500 clientes"
success_metric: "Tempo médio de conciliação: baseline 4h/cliente/mês → meta 1.5h em 90 dias"
effort_estimate: "M (2–4 sprints)"
linked_insights:
  - "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
created_at: "2026-05-10T15:00:00Z"
updated_at: "2026-05-10T15:00:00Z"
---

# Phanes atualiza o insight de origem:
# status: promoted
# idea_ref: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
```

### Incorreto

```yaml
# Idea sem linked_insights[] — VIOLA HARD-GATE 1, precondição (b)
---
id: "scheduled-payments-research/ideas/002-mobile-receipt-capture"
topic: "scheduled-payments-research"
problem: "Achamos que mobile capture seria útil"
hypothesis: ""              # <- VIOLA HARD-GATE 1, precondição (c) — campo vazio
target_user: "Usuários"     # <- inadequado, mas presente
success_metric: ""          # <- VIOLA HARD-GATE 1, precondição (c)
effort_estimate: "M"
linked_insights: []         # <- VIOLA HARD-GATE 1, precondição (b) — array vazio
---
```

```yaml
# warrior-pitia muda status sem direção humana — VIOLA HARD-GATE 2
# Antes: status: proposed
# Depois (sem instrução humana): status: approved
# ❌ Mesmo se Pítia "achar óbvio", a transição é inválida sem registro humano.
```

```yaml
# Idea com topic divergente do insight — VIOLA HARD-GATE 1, precondição (d)
---
id: "billing/ideas/001-auto-invoice"
topic: "billing"
linked_insights:
  - "scheduled-payments-research/insights/003-erp-divergence"  # topic divergente
---
```

## Validação Automatizada

- **Ferramenta:** revisão humana em PR enquanto linter dedicado não existe; futuramente `kata-design-validation` parametrizado para tipo `discovery-artifacts` deve validar (i) presença e tipo dos campos obrigatórios, (ii) coerência de `topic` entre Idea e `linked_insights[]`, (iii) coerência de `status` + campos condicionais (`merged_into`, `idea_ref`, `rejected_reason`, `awaiting_evidence_reason`), (iv) histórico de transições no git log do arquivo (cada mudança de status acompanhada por commit ou comentário humano).
- **Momento:** PR review em todo PR que toca `docs/discovery/`; auto-check pelo próprio `warrior-phanes` antes de gravar a Idea.
- **Métrica:** 0 Ideas com `linked_insights[]` vazio em `main`; 0 Ideas com qualquer dos 5 campos obrigatórios vazio; 0 transições de status de insight executadas por `warrior-pitia` sem evidência de instrução humana correspondente; 100% dos `topic` de Ideas coincidentes com seus insights de origem.

## Referências

- `codex-discovery-artifacts` — schema completo de insights e ideas, máquina de estados, convenções de endereçamento
- `lex-hard-gate-pattern` — padrão canônico do bloco HARD-GATE
- `kata-discovery-synthesis` — procedimento de produção de insights
- `kata-ideation-from-insight` — procedimento de promoção a Idea
- `warrior-pitia`, `warrior-phanes` — agentes vinculados
