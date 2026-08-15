# Lexis: Fluxo de Product Discovery — Insight a Idea

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Product Discovery — produção de insights, transição de status, e promoção de insight aprovado a Idea no Ahrena

## Lei

> **Toda Idea no Ahrena (`docs/discovery/{topic}/ideas/{NNN}-{slug}.md`) DEVE ter sido criada por `warrior-phanes` exclusivamente a partir de um ou mais insights cujo `status` é `approved`, com os 5 campos de conteúdo obrigatórios (`problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate`) preenchidos, e o insight de origem DEVE ser atualizado para `status: promoted` com `idea_ref` apontando para a Idea criada. Toda mudança de `status` de um insight para qualquer valor diferente de `proposed` DEVE ser conduzida por decisão humana explícita registrada (mensagem na sessão, comentário em PR, ou instrução literal); `warrior-pitia` NÃO DEVE alterar status por iniciativa própria, exceto a criação inicial em `proposed`.**

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
