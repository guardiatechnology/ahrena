---
plan_id: "033"
title: "lex-codex-agent-construction-directives"
status: done
agent: claude
issue: "guardiatechnology/ahrena#91"
branch: "feat/91-lex-codex-agent-construction-directives"
worktree: ".worktrees/91-lex-codex-agent-construction-directives"
created_at: "2026-05-09T13:35:00Z"
updated_at: "2026-05-12T11:36:00Z"
merge_commit: "132bca6d555ece782d4dc8a64b052241bd1ed0d4"
closed_at: "2026-05-12T02:07:19Z"
---

# Plano: Lex e Codex de Diretrizes para Construção de Agentes (pre-req-D)

## Objetivo

Criar `lex-agent-construction-directives` + `codex-agent-construction-directives` em `engineering/agents/`, derivados do manual oficial Guardia ["Diretrizes para Construção de Agentes"](https://www.notion.so/Diretrizes-para-Constru-o-de-Agentes-35b36f91ebd281c8a65de122b7234b5d) (Notion). Estabelece o **fundamento** do ciclo de construção de agentes na plataforma: 6 Diretrizes (Identidade, Memória, Ferramentas, Feedback, Escopo, Contexto) ancoradas na analogia Piaget (Sensório-motor, Pré-operacional, Operações Concretas, Operações Formais, Vygotsky/ZDP). É **bloqueante** de [plan-031](plan-031-claudionor-anthropic-ecosystem.md) (Claudionor PoV Factory) e [plan-032](plan-032-warrior-metis-apm-agents.md) (Mêtis APM Operação Concreta) — sem este Lex, não há critério objetivo para promover agent de pré-operacional para Operação Concreta nem para validar DoOC.

## Contexto

### Por que este Lex/Codex existe

A Guardia constrói agentes de IA como produtos (Isac, futuros agents de reconciliação/classificação fiscal/fechamento). Sem fundação compartilhada:

1. **Sem critério de "pronto para escala":** PoV vira produto sem amadurecer, ou amadurece sem nunca virar produto
2. **Sem rigor diferencial por estágio:** PoV é cobrado como produção (mata velocidade) ou produção é tolerada como PoV (gera incidente)
3. **Sem vocabulário comum entre Claudionor e Mêtis:** os dois warriors falam de "agent" mas com expectativas distintas
4. **Sem ancoragem cognitiva:** decisões de arquitetura sem framework conceitual viram debate subjetivo

A analogia Piaget no manual Notion fornece esse framework: **cada estágio cognitivo tem rigor diferencial mensurável** — pré-operacional aceita memória curta, ferramentas limitadas, feedback leve; Operações Concretas exige tudo isso em rigor de produção.

### Decisões alinhadas com o usuário (Gates anteriores)

1. **1 Lex + 1 Codex** — não múltiplas Lexis por seção. Lex enxuta com HARD-GATE; Codex referencia Notion como source-of-truth viva
2. **Subclade `engineering/agents/`** — separada de skills/plugins
3. **Bloqueante de plan-031 e plan-032** — caminho crítico

## Escopo

### Artefatos a criar (pt-BR + es + en por `lex-framework-language`)

| # | Tipo  | Path                                                                                | Conteúdo                                                                       |
|---|-------|-------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1 | Lexis | `framework/{lang}/engineering/agents/lexis/lex-agent-construction-directives.md`    | HARD-GATE + 6 Diretrizes + stage tags + cláusula de transição (vide abaixo)    |
| 2 | Codex | `framework/{lang}/engineering/agents/codex/codex-agent-construction-directives.md`  | Analogia Piaget + 6 Diretrizes detalhadas + rigor por estágio + exemplos       |

### Conteúdo da Lex (estrutura)

```markdown
# Lexis: Diretrizes para Construção de Agentes

## Law

> **Todo agent construído sobre a plataforma Guardia MUST declarar explicitamente
> seu estágio cognitivo (`stage: pre-operational | operational-concrete | legacy-pov`)
> no system prompt. Agent em estágio `operational-concrete` MUST satisfazer todas
> as 6 Diretrizes (Identidade, Memória em Camadas, Ferramentas Concretas, Loop de
> Feedback, Escopo Restrito, Contexto Rico) per "Diretrizes para Construção de
> Agentes" (Notion). Agent em estágio `pre-operational` PODE operar com versão
> mínima viável de cada Diretriz, mas o estágio MUST estar declarado explicitamente
> e gaps MUST estar registrados. Promover agent de `pre-operational` para
> `operational-concrete` sem Definition of Operational Concrete (DoOC) validada
> é FORBIDDEN.**

## HARD-GATE per `lex-hard-gate-pattern`

<HARD-GATE>
warrior-claudionor, warrior-metis, warrior-apollo-agents e qualquer outro agente
MUST NOT promover agent de `pre-operational` para `operational-concrete` sem
ALL 9 itens da Definition of Operational Concrete (DoOC) ✅:

  (a) Origem do PoV declarada (path em docs/{context}/agents-pov/)
  (b) Métrica leading de valor provada (número, threshold, janela)
  (c) Métrica lagging de valor declarada
  (d) Escopo estabilizado (sem mudança nas últimas 2 semanas)
  (e) Observability data do PoV disponível (mínimo 7 dias)
  (f) Stakeholder owner identificado
  (g) Capacidade de implementação confirmada (warrior-apollo-agents OU
      caminho alternativo declarado)
  (h) Tier de criticidade declarado (tier-1/2 dispara SLO obrigatório)
  (i) Stage explícito no system prompt do PoV (`stage: pre-operational`)

This rule applies to EVERY agent na plataforma Guardia, regardless of:
  - perceived size ("é só um agent simples")
  - urgency ("o cliente precisa hoje")
  - quem solicitou ("o CEO pediu")
  - team confidence ("já testamos bastante")

Single declared exception: agentes criados antes do merge desta Lex são tratados
como `stage: legacy-pov`; promoção a `operational-concrete` requer DoOC retroativa
+ ADR registrando o gap histórico.
</HARD-GATE>

## Stage tags

| Tag | Quando usar | Rigor das 6 Diretrizes |
|---|---|---|
| `pre-operational` | PoV ativo, provando valor | Mínimo viável; gaps declarados em ADR/PDR |
| `operational-concrete` | Produção; escopo provado | Todas as 6 Diretrizes em rigor de produção |
| `legacy-pov` | Agent anterior ao merge desta Lex | Promoção exige DoOC retroativa |

## Aplicabilidade

- **Aplica-se a:** todo agent construído sobre a plataforma Guardia, incluindo Isac,
  agents internos, agents customer-facing, agents de automação operacional
- **Bound agents:** warrior-claudionor (PoV), warrior-metis (Operação Concreta),
  warrior-apollo-agents (implementação), warrior-athena (Gate 2 — quando flow é
  agent-driven)
- **Exceções:** apenas a cláusula `legacy-pov` declarada acima

## Validação Automatizada

- **Tool:** `kata-dooc-validate` (entregue em plan-032) verifica 9 itens da DoOC
  programaticamente; lint na pipeline detecta system prompts sem `stage:` declarado
- **Quando:** ao promover agent (transição `pre-operational` → `operational-concrete`);
  no Gate 2 do Issue-Driven flow quando feature toca docs/{context}/agents/
- **Métrica:** 0 agents em `operational-concrete` sem DoOC ✅; 100% dos system
  prompts com `stage:` declarado
```

### Conteúdo do Codex (estrutura)

```markdown
# Codex: Diretrizes para Construção de Agentes

## Visão geral

Manual de referência para arquitetar agents na plataforma Guardia, derivado de
"Diretrizes para Construção de Agentes" (Notion — source-of-truth viva).
Aplica analogia Piaget como framework conceitual e diferencia rigor por estágio.

## Analogia Piaget (base conceitual)

| Fase Cognitiva | Equivalente em Agentes | Warrior Ahrena |
|---|---|---|
| Sensório-motor (0–2a) | Reativo puro — só contexto imediato | (não modelado) |
| Pré-operacional (2–7a) | LLM com tooling leve, sem modelagem profunda | warrior-claudionor (plan-031) |
| Operações Concretas (7–11a) | Agent com tools + memória, dados reais | warrior-metis (plan-032) |
| Operações Formais (11a+) | Planejamento + auto-reflexão | (futuro — fronteira) |
| Vygotsky / Zona Proximal | Multi-agent + HITL | Cross-cutting (Diretriz 04) |

## As 6 Diretrizes

### Diretriz 01 — Identidade Clara
[Detalhamento do Notion + rigor por estágio]

### Diretriz 02 — Memória em Camadas
[Curto + médio + longo; rigor por estágio]

### Diretriz 03 — Ferramentas Concretas
[Busca + execução + escrita estruturada; rigor por estágio]

### Diretriz 04 — Loop de Feedback Explícito
[HITL + critic + métricas; rigor por estágio]

### Diretriz 05 — Escopo Restrito
[Domínio estreito; rigor por estágio]

### Diretriz 06 — Contexto Rico
[Few-shot + docs + exemplos negativos + histórico; ponte de aprendizado entre estágios]

## Rigor diferencial por estágio (cross-tab)

| # | Diretriz | pre-operational (Claudionor) | operational-concrete (Mêtis) |
|---|---|---|---|
| 01 | Identidade | System prompt mínimo viável + `stage:` declarado | Full per `lex-system-prompt` (manual completo do Notion) |
| 02 | Memória | Curto-prazo OK | 3 camadas mandatórias (curto + médio + longo) |
| 03 | Ferramentas | Busca + execução simples | Catálogo tripartido completo (deterministic + ML + MCP) |
| 04 | Feedback | HITL leve OU 1 métrica objetiva | HITL + critic + métricas objetivas |
| 05 | Escopo | Muito estreito (1 caso de uso) | Escopo provado + playbook de expansão |
| 06 | Contexto | Few-shot + exemplos negativos curados | Few-shot + docs + exemplos negativos + histórico observado |

## Stage tags em system prompt (exemplos canônicos)

[Exemplos de blocos `stage: pre-operational`, `stage: operational-concrete`,
`stage: legacy-pov` em system prompts reais]

## Definition of Operational Concrete (DoOC)

[Detalhamento dos 9 itens, com critério de evidência por item]

## Anti-padrões observados

[Lista de armadilhas comuns: "É só PoV então não preciso de identidade clara";
"Vamos amadurecer depois"; "O escopo expande conforme aprendemos"]

## Referências externas

- Notion (source-of-truth viva): https://www.notion.so/Diretrizes-para-Constru-o-de-Agentes-35b36f91ebd281c8a65de122b7234b5d
- Piaget, J. (1936). La naissance de l'intelligence chez l'enfant
- Vygotsky, L.S. (1978). Mind in Society: The Development of Higher Psychological Processes
- OWASP LLM Top 10 (consultado por `codex-system-prompt`)
```

### Atualizações em artefatos existentes

| # | Tipo | Nome | Mudança |
|---|------|------|---------|
| 3 | Config | `framework/platforms.yaml` | Registrar lex-agent-construction-directives e codex-agent-construction-directives em `cursor.rules` (per `lex-platforms-rules`) |
| 4 | Sync | `.claude/` e `.cursor/` | `python3 scripts/install.py --self --target . --platform {claude-code,cursor}` |

## Steps

### Bloco A — Setup

- [ ] **A.1.** Issue (`feature-request`, labels `feature request ➕` + `framework` + `agents`, Issue Type `Feature`, assignee `@me`) per `lex-issue-first` + `lex-issue-quality`
- [ ] **A.2.** Branch `feat/{N}-lex-codex-agent-construction-directives` em worktree per `lex-git-worktrees` + `lex-git-branches`
- [ ] **A.3.** Status do plan → `in-progress`

### Bloco B — Lex

- [ ] **B.1.** `lex-agent-construction-directives.md` (pt-BR) — `templates/lex-sample.md`. HARD-GATE com 9 itens DoOC; stage tags; cláusula `legacy-pov`; counter-pretextos
- [ ] **B.2.** Tradução para es e en

### Bloco C — Codex

- [ ] **C.1.** `codex-agent-construction-directives.md` (pt-BR) — `templates/codex-sample.md`. Analogia Piaget; 6 Diretrizes detalhadas; cross-tab pre-operational vs operational-concrete; exemplos canônicos; anti-padrões; link literal Notion
- [ ] **C.2.** Tradução para es e en

### Bloco D — Sync e self-review

- [ ] **D.1.** Atualizar `framework/platforms.yaml` com 2 entries em `cursor.rules`
- [ ] **D.2.** Sync — `python3 scripts/install.py --self --target . --platform {claude-code,cursor}`
- [ ] **D.3.** `kata-artifact-self-review` em cada Lex/Codex (pt-BR + es + en)

### Bloco E — Fechamento

- [ ] **E.1.** Commits atômicos:
  1. `feat(agents): add lex-agent-construction-directives with DoOC HARD-GATE`
  2. `feat(agents): add codex-agent-construction-directives (Piaget + 6 directives)`
  3. `chore: register in platforms.yaml and sync .claude/.cursor`
- [ ] **E.2.** PR via `kata-contributing-pr` — `Closes #{N}`, mirroring + `agents`, size, CODEOWNERS; body referencia plan-033 e Notion fonte
- [ ] **E.3.** Pós-merge — status `done` → `archived`, remover worktree

## Dependências

### Bloqueantes

- Nenhum bloqueante interno — Lex/Codex puros derivados do Notion. Pode rodar em paralelo com pre-req-A/B/C, plan-013, plan-029

### Pré-existentes

- `lex-template-usage`, `lex-pilars`, `lex-framework-language`, `lex-hard-gate-pattern`, `lex-platforms-rules`
- Templates: `lex-sample.md`, `codex-sample.md`

### Bloqueia (downstream)

- **plan-031** (Claudionor PoV Factory) — usa Lex para impor `stage: pre-operational` em todo PoV
- **plan-032** (Mêtis APM) — usa Lex como master + DoOC HARD-GATE
- **plan-013** (Apollo split) — apollo-agents carrega esta Lex ao implementar

## Riscos

| # | Risco | Probab. | Mitigação |
|---|---|:------:|---|
| 1 | Lex acaba grande demais ao codificar Diretrizes + Piaget + DoOC | Média | Lex enxuta (HARD-GATE + 9 itens DoOC + stage tags); Codex carrega contexto Piaget + exemplos |
| 2 | Manual Notion atualiza e Codex fica desatualizado | Alta | Codex referencia Notion como source-of-truth viva; review trimestral; cláusula "Codex é snapshot indicativo, Notion prevalece em divergência" |
| 3 | Cláusula `legacy-pov` vira escape hatch perpétuo | Média | Lex declara: agents `legacy-pov` MUST migrar para `pre-operational` ou `operational-concrete` em prazo definido (sugestão: 90 dias após merge da Lex); Mnemosyne (plan-028) flagaria agentes antigos |
| 4 | Multilingue incompleto: 2 artefatos × 3 línguas = 6 arquivos | Baixa | Steps separados por língua; tamanho manejável |
| 5 | Notion source-of-truth muda estrutura (6 sub-páginas viram 4) e Codex quebra link semântico | Baixa | Codex referencia Notion por título e não por ordem; revisão pós-merge |

## Decisões em aberto

- **Prazo da cláusula `legacy-pov`:** proposta 90 dias para migração obrigatória. Confirmar
- **Onde declarar `stage:` no system prompt:** proposta no header (primeira linha após docstring); pode ser convenção em Codex sem ser regra rígida na Lex
- **Critério de "evidência" para cada item DoOC:** Codex sugere formato (link, número, SHA), mas pode evoluir conforme uso real

## Verificação

1. **Estrutura entregue:** 2 artefatos × 3 línguas = 6 arquivos em `framework/{lang}/engineering/agents/`
2. **Atualizações:** `platforms.yaml`, `.claude/`, `.cursor/`
3. **HARD-GATE da Lex:** atende `lex-hard-gate-pattern` (subject, ação, preconditions, scope, counter-pretextos, exceção)
4. **Coerência:** Codex contém analogia Piaget completa; cross-tab rigor por estágio; ≥3 exemplos canônicos de stage tag
5. **PR final:** body referencia plan-033 e Notion source; lista plan-031 e plan-032 como downstream que ficam desbloqueados