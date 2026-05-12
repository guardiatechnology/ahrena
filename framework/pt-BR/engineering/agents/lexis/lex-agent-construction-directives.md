# Lexis: Diretrizes para Construção de Agentes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Construção de agentes de IA sobre a plataforma Guardia — system prompt, memória, ferramentas, feedback, escopo, contexto, e ciclo de promoção de estágio cognitivo

## Propósito

A Guardia constrói agentes de IA como produtos (Isac, reconciliação, classificação fiscal, fechamento). Sem fundação compartilhada, PoVs viram produto sem amadurecer, produção é tolerada como PoV, e Claudionor e Mêtis falam de "agente" com expectativas distintas. Esta Lei codifica o critério objetivo de promoção (DoOC) e o vocabulário compartilhado (estágios cognitivos) que tornam a decisão "este PoV está pronto para escala?" verificável, não subjetiva.

## Lei

> **Todo agente de IA construído sobre a plataforma Guardia DEVE declarar explicitamente seu estágio cognitivo (`stage: pre-operational | operational-concrete | legacy-pov`) no system prompt. Agentes em `operational-concrete` DEVEM satisfazer todas as 6 Diretrizes de Construção (Identidade Clara, Memória em Camadas, Ferramentas Concretas, Loop de Feedback Explícito, Escopo Restrito, Contexto Rico) em rigor de produção, conforme `codex-agent-construction-directives` e o manual canônico "Diretrizes para Construção de Agentes" mantido em Notion. Agentes em `pre-operational` PODEM operar com versão mínima viável de cada Diretriz, desde que o estágio esteja declarado e os gaps registrados no PoV. Promover um agente de `pre-operational` para `operational-concrete` sem Definition of Operational Concrete (DoOC) validada nos 9 itens canônicos é PROIBIDO.**

## Abrangência

- **Aplica-se a:** todo agente de IA construído sobre a plataforma Guardia — Isac, agentes de reconciliação, classificação fiscal, fechamento, agentes internos de automação, agentes customer-facing, agentes de suporte. Aplica-se ao prompt do agente, à camada de tooling, à camada de memória e ao ciclo de promoção entre estágios.
- **Agentes vinculados:** `warrior-claudionor` (Fábrica de PoV — plan-031), `warrior-metis` (APM Operação Concreta — plan-032), `warrior-apollo-agents` (implementação — plan-013), `warrior-athena` (Gate 2 do Issue-Driven Flow quando a feature toca `docs/{context}/agents/`).
- **Exceções:** Lexis não admitem exceções. As 3 cláusulas declaradas no HARD-GATE são `legacy-pov`, `direct-entry` e `user-override`; cada uma exige compensação documentada em ADR ou PDR e marcação correspondente no `dooc/{agent}.md` conforme `codex-agent-design-docs`. Sem ADR/PDR válido, as exceções ficam não-conformes.

## Estágios cognitivos

A analogia de Piaget detalhada em `codex-agent-construction-directives` é o framework conceitual; o rigor diferencial expresso aqui é a tradução operacional.

| Tag | Quando usar | Rigor exigido das 6 Diretrizes |
|-----|-------------|--------------------------------|
| `pre-operational` | PoV ativo, provando valor antes de escala | Versão mínima viável de cada Diretriz; gaps declarados em PoV doc/PDR |
| `operational-concrete` | Produção; escopo provado; valor mensurado | Todas as 6 Diretrizes em rigor de produção |
| `legacy-pov` | Agente anterior ao merge desta Lex | Tratado como `pre-operational`; migração obrigatória em 90 dias |

## Definition of Operational Concrete (DoOC)

A DoOC é o checklist canônico de promoção. Detalhamento por critério (formato de evidência, links esperados) está em `codex-agent-construction-directives`. Os 9 itens são:

1. **Origem do PoV declarada** — path em `docs/{context}/agents-pov/` referenciando o PoV original
2. **Métrica leading de valor provada** — número, threshold e janela de observação (mínimo 7 dias)
3. **Métrica lagging de valor declarada** — métrica de negócio que será impactada
4. **Escopo estabilizado** — sem mudança de escopo nas últimas 2 semanas
5. **Observability data disponível** — telemetria mínima de 7 dias do PoV em operação
6. **Stakeholder owner identificado** — nome e papel; canal de escalonamento documentado
7. **Capacidade de implementação confirmada** — `warrior-apollo-agents` disponível OU caminho alternativo declarado
8. **Tier de criticidade declarado** — tier-1/2 dispara SLO obrigatório per `lex-slo-required`
9. **Stage explícito no system prompt** — `stage: pre-operational` declarado no prompt do PoV antes da promoção

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](framework/pt-BR/_foundation/quality/lexis/lex-hard-gate-pattern.md), o bloqueio textual desta Lex é canonicamente expresso como:

```
<HARD-GATE>
warrior-claudionor, warrior-metis, warrior-apollo-agents e qualquer
outro agente NÃO DEVE promover agente de `pre-operational` para
`operational-concrete` sem TODOS os 9 itens da Definition of
Operational Concrete (DoOC) ✅:

  (a) Origem do PoV declarada (path em docs/{context}/agents-pov/)
  (b) Métrica leading de valor provada (número, threshold, janela
      ≥ 7 dias)
  (c) Métrica lagging de valor declarada
  (d) Escopo estabilizado (sem mudança nas últimas 2 semanas)
  (e) Observability data do PoV disponível (≥ 7 dias)
  (f) Stakeholder owner identificado
  (g) Capacidade de implementação confirmada (warrior-apollo-agents
      OU caminho alternativo declarado)
  (h) Tier de criticidade declarado (tier-1/2 dispara SLO obrigatório)
  (i) Stage explícito no system prompt do PoV
      (`stage: pre-operational`)

Esta regra se aplica a TODO agente construído sobre a plataforma
Guardia, independentemente de:
  - tamanho percebido ("é só um agente simples")
  - urgência ("o cliente precisa hoje")
  - quem solicitou ("o CEO pediu")
  - confiança do time ("já testamos bastante")

Exceções declaradas (3):

(1) `legacy-pov` — agentes criados antes do merge desta Lex são
    tratados como `stage: legacy-pov`. Promoção a `operational-concrete`
    exige DoOC retroativa + ADR registrando o gap histórico. A tag
    NÃO É permanente: agentes em `legacy-pov` DEVEM migrar para
    `pre-operational` ou `operational-concrete` em até 90 dias após
    o merge desta Lex; além desse prazo são considerados não-conformes.

(2) `direct-entry` — Mêtis acionada para projetar agente diretamente
    em `operational-concrete` sem PoV prévia (Claudionor não foi
    invocado). Permitido somente com ADR ou PDR declarando:
      (i) razão do bypass do estágio `pre-operational`;
      (ii) leading metric alvo + janela de validação pós-deploy;
      (iii) plano de observability instrumentado desde o dia 0.
    Os itens (a), (b), (d) e (e) da DoOC podem ser preenchidos como
    `N/A — direct-entry` em `dooc/{agent}.md`, sempre referenciando
    o ADR/PDR; os itens (c) e (f)-(i) permanecem mandatórios.

(3) `user-override` — usuário (CEO ou Brand owner designado) promove
    agente com evidências parciais da DoOC. Permitido somente com
    ADR ou PDR declarando:
      (i) quais itens da DoOC estão sendo overrided e por quê;
      (ii) responsabilidade explícita do usuário (`Promoted by` em
           `dooc/{agent}.md` preenchido);
      (iii) compensação retroativa em janela declarada
            (sugerido: 30 dias).
    Os itens overrided aparecem como `N/A — user-override` no `dooc/{agent}.md`.

Em todas as exceções, a Lex permanece inviolada — exceções são
preenchimentos canônicos do `dooc/{agent}.md` com justificativa
auditável em ADR ou PDR, NÃO bypass do gate. Sem ADR/PDR válido,
as exceções declaradas ficam não-conformes.
</HARD-GATE>
```

## Consequências de Violação

1. **Bloqueio automático:** `kata-dooc-validate` (entregue em plan-032) reprova o checklist quando qualquer item da DoOC está ausente; `warrior-athena` no Gate 2 do Issue-Driven Flow bloqueia o PR quando a feature toca `docs/{context}/agents/` sem `stage:` declarado ou sem DoOC anexada à promoção. Commit que altera `stage:` de `pre-operational` para `operational-concrete` sem ADR de promoção referenciando a DoOC é rejeitado.
2. **Alerta:** notifica o owner do agente (declarado em DoOC item (f)) e o canal `#agents-governance`; agentes em `legacy-pov` além do prazo declarado no HARD-GATE entram em relatório semanal automático até regularização ou desativação.
3. **Remediação:** (a) reverter a promoção (volta para `pre-operational`) e abrir issue para completar os itens DoOC faltantes; OU (b) abrir ADR registrando o caminho alternativo per item (g) da DoOC; OU (c) decomissionar o agente quando o PoV não justifica produção.

## Exemplos

### Correto

System prompt de PoV declarando estágio:

```
# Agente: rec-pov-classifier
# stage: pre-operational
# DoOC gaps: leading metric ainda em coleta; observability < 7 dias
# Identidade: classificador de transações para reconciliação
# Memória: curto-prazo (janela da sessão)
# Ferramentas: search no histórico de classificações + execução simples
# Feedback: HITL leve (analista valida cada classificação)
# Escopo: 1 caso de uso — extratos do Itaú PJ
# Contexto: 12 few-shot + 4 exemplos negativos curados
```

System prompt de agente em produção:

```
# Agente: rec-classifier
# stage: operational-concrete
# DoOC: ✅ (validada em 2026-04-12, ADR-018)
# tier: tier-2
# SLO: docs/reconciliation/metrics/slo-rec-classifier.yaml
# Identidade: per docs/reconciliation/agents/rec-classifier/identity.md (manual completo)
# Memória: curto + médio (sessão + histórico do cliente) + longo (regras de classificação)
# Ferramentas: catálogo tripartido — deterministic + ML + MCP
# Feedback: HITL + critic LLM + 3 métricas objetivas em CloudWatch
# Escopo: classificação de transações para reconciliação bancária
# Contexto: few-shot curado + docs + histórico observado dos últimos 90 dias
```

### Incorreto

Agente sem estágio declarado:

```
# Agente: rec-classifier
# Identidade: classificador
# (sem stage:, sem DoOC, sem tier, sem referência ao manual)
```

Resultado: `warrior-athena` no Gate 2 bloqueia o PR; `warrior-metis` não promove o PoV; o agente entra em produção como caixa-preta.

Promoção sem DoOC:

```
# Antes: stage: pre-operational
# Depois: stage: operational-concrete
# (sem 9 itens da DoOC validados, sem ADR de promoção)
```

Resultado: `warrior-metis` recusa a promoção; commit que altera `stage:` sem checklist DoOC anexado é bloqueado no Gate 2.

## Validação Automatizada

- **Ferramenta:** `kata-dooc-validate` (entregue em plan-032 junto a `warrior-metis`) executa o checklist dos 9 itens DoOC programaticamente; lint na pipeline detecta system prompts em `docs/{context}/agents/` sem `stage:` declarado; `warrior-athena` aplica este Gate quando a feature toca artefatos de agentes.
- **Quando:** ao promover agente (transição `pre-operational` → `operational-concrete`); no Gate 2 do Issue-Driven Flow quando a feature toca `docs/{context}/agents/`; em auditoria periódica de agentes `legacy-pov` (90 dias após merge).
- **Métrica:** 0 agentes em `operational-concrete` sem DoOC ✅; 100% dos system prompts da plataforma com `stage:` declarado; 0 agentes em `legacy-pov` além de 90 dias após o merge desta Lex.
