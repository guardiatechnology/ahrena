---
plan_id: "031"
title: "claudionor-preoperational-pov-factory"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#123"
created_at: "2026-05-08T00:00:00Z"
updated_at: "2026-05-12T17:30:00Z"
---

# Plano: warrior-claudionor v2 — Pré-operacional Agent Factory (PoV via stack Anthropic)

## Objetivo

Reposicionar `warrior-claudionor` (criado em [plan-029](plan-029-warrior-claudionor-skill-architect.md) como skill architect) para **Pré-operacional Agent Factory**: fábrica de agents em estágio pré-operacional cujo objetivo único é **provar valor ao cliente de forma rápida e observada**, usando a stack Anthropic (Skills, Subagents) como tooling de baixa fricção. Claudionor instrumenta observability robusta em cada PoV para **aprender o que funciona**, coleta value proof estruturado, e produz `docs/{context}/agents-pov/` consumível por `warrior-mêtis` ([plan-032](plan-032-warrior-metis-apm-agents.md)) via `cry-agent-design --from-pov` quando o agent passa pela DoOC (Definition of Operational Concrete) e migra para produção. **Plugin generation a partir de clades do framework** — capacidade originalmente prevista na v1 deste plano — foi separada para [plan-034](plan-034-claudionor-plugin-compose-anthropic.md): auto-publicação do Ahrena como plugin Anthropic é capability ortogonal ao ciclo PoV.

## Persona

**Claudionor** — especialista da casa Claude no Ahrena, responsável por experimentação rápida com agents usando o ecossistema Anthropic (Skills, Subagents, Plugins). Persona confirmada em plan-029. Mission shift: de "arquiteto do ecossistema Anthropic" para **"fábrica de PoVs com observabilidade nativa"** — Claudionor não é meta-framework, é **product factory**: pega um problema do cliente, sobe um agent leve em horas/dias, instrumenta tudo, mede valor, e entrega evidências concretas de que vale (ou não vale) escalar para produção.

## Estágio cognitivo de aplicação (Piaget)

Claudionor opera **exclusivamente** no estágio "Pré-operacional":

| Estágio Piaget | Equivalente em agents (Notion) | Warrior Ahrena |
|---|---|---|
| Sensório-motor | Reativo puro | (não modelado) |
| **Pré-operacional** | **LLM com tooling leve, sem modelagem profunda de outros** | **Claudionor** (este plano) |
| **Operações Concretas** | Agent com tools + memória, dados reais | **Mêtis** ([plan-032](plan-032-warrior-metis-apm-agents.md)) |
| Operações Formais | Planejamento + auto-reflexão | (futuro) |
| Vygotsky / Zona Proximal | Multi-agent + HITL | Cross-cutting (Diretriz 04) |

**Característica essencial do estágio:** texto rico mas alucina, capacidade limitada de modelagem profunda, sem memória persistente. Aceitável **somente** porque o objetivo é prova de valor — não escala. Quando madurece (DoOC ✅), Mêtis assume.

## As 6 Diretrizes na ótica de Claudionor (rigor mínimo viável)

| # | Diretriz (Notion) | Como Claudionor aplica em PoV |
|---|---|---|
| 01 | **Identidade Clara** | System prompt mínimo viável: propósito + escopo + restrições básicas. **Declara explicitamente `stage: pre-operational`** no prompt — pré-condição da DoOC item 9 |
| 02 | **Memória em Camadas** | **Apenas curto-prazo** (janela de contexto da Anthropic API / Claude Code). Sem memória persistente — aceitável porque PoV é experimental e sessões são curtas |
| 03 | **Ferramentas Concretas** | **Busca + execução simples** (Anthropic Skills nativos: web search, code exec, file write). Tool catalog mínimo viável |
| 04 | **Loop de Feedback Explícito** | **HITL leve OU 1 métrica objetiva** — suficiente para validar se PoV gera valor. Critic agent é opcional nesta fase |
| 05 | **Escopo Restrito** | **Muito estreito** — 1 caso de uso primário. Princípio: "domínio estreito + feedback rápido = curva de aprendizado íngreme". Expansão fica para Mêtis |
| 06 | **Contexto Rico** | Few-shot do domínio + exemplos negativos curados. **Output do PoV alimenta o context-pack de Mêtis** quando agent maturece |

**Observabilidade é cidadã de primeira classe**: Claudionor instrumenta cada PoV desde o primeiro deploy. O motivo é **aprender** — sem dados reais, não há base para Diretriz 06 (contexto rico) nem para DoOC.

## Mapeamento de fluxo

```
[Problema do cliente]
     │
     ▼
cry-pov --context <name> --kind {skill|subagent|plugin}
  └─→ warrior-claudionor
        ├─→ kata-pov-scope-define              (Diretriz 05 — escopo muito estreito)
        ├─→ kata-pov-system-prompt             (Diretriz 01 — minimum viable + stage:pre-operational)
        ├─→ kata-pov-tools-select              (Diretriz 03 — busca + execução)
        ├─→ kata-pov-context-curate            (Diretriz 06 — few-shot + exemplos negativos)
        ├─→ kata-pov-observability-instrument  (NOVO — observabilidade nativa do PoV)
        ├─→ kata-pov-feedback-attach           (Diretriz 04 — HITL ou métrica objetiva)
        └─→ delega implementação:
              ├─→ kata-skill-implement (plan-029) se kind=skill
              ├─→ kata-agent-author    (NOVO)    se kind=subagent
              └─→ kata-plugin-compose  (Fase D opcional, da v1) se kind=plugin
              
        Output: docs/{context}/agents-pov/
                ├── overview.md                Problema do cliente; escopo PoV; persona; stage:pre-operational explícito
                ├── system-prompt.md           Minimum viable
                ├── tools.md                   Busca + execução; subset Anthropic
                ├── context-pack.md            Few-shot + exemplos negativos curados
                ├── feedback.md                HITL ou métrica objetiva — como validamos valor
                ├── observability/             Instrumentação:
                │   ├── traces-spec.md         Spans esperados (per turn, per tool call)
                │   ├── prompts-log.md         Schema de log de prompts (sem PII)
                │   ├── tool-calls-log.md      Schema de log de tool calls
                │   └── value-metrics.md       Quais métricas leading rastreiam valor
                ├── implementation/            Artefatos da implementação:
                │   ├── (skill/<slug>/)        Se kind=skill — segue lex-skill-project-structure
                │   ├── (agents/<name>.md)     Se kind=subagent
                │   └── (plugins/<slug>/)      Se kind=plugin (Fase D)
                └── value-proof.md             Atualizado durante operação do PoV: dados, observações, decisão go/no-go

[Loop de operação do PoV — semanas]
   ⚙ PoV roda em produção limitada
   📊 observability/ acumula dados reais
   📈 value-metrics atualizadas em value-proof.md
   🔍 Claudionor revisita context-pack à medida que aprende

[Maturação — gatekeep para Operação Concreta]
   value-proof.md mostra tração consistente?
        │
        ├─ NÃO → permanece em PoV; iteração; eventual descontinuação
        │
        └─ SIM → cry-agent-design --context <name> --from-pov docs/{context}/agents-pov/
                    └─→ warrior-mêtis (plan-032)
                           └─→ kata-dooc-validate consome value-proof.md + observability/
```

## Capacidades-chave

1. **Spawn rápido via Anthropic Skill** — usa `kata-skill-implement` (plan-029, já entregue na v1 deste plano)
2. **Spawn rápido via Claude Code Subagent** — `kata-agent-author` (novo, espelhando v1) para casos onde Skill é muita estrutura
3. **Spawn rápido via Plugin Anthropic** — entregue em [plan-034](plan-034-claudionor-plugin-compose-anthropic.md); ativável via `cry-pov --kind plugin` que despacha para `cry-plugin`
4. **Instrumentação de observability nativa** — `kata-pov-observability-instrument` (novo, cidadã de primeira classe)
5. **Coleta estruturada de value proof** — `kata-pov-value-track` (novo)
6. **Ponte para Operação Concreta** — output `docs/{context}/agents-pov/` é input direto de Mêtis via `--from-pov`

## Relação com warriors existentes

| Warrior | Papel no ciclo PoV → Operação Concreta |
|---------|----------------------------------------|
| `warrior-claudionor` (este plano) | Pré-operacional Agent Factory — produz PoV + observability + value proof |
| `warrior-metis` ([plan-032](plan-032-warrior-metis-apm-agents.md)) | APM Operação Concreta — consome `--from-pov`, projeta produção |
| `warrior-apollo-agents` ([plan-013](plan-013-split-apollo-api-jobs-agents.md)) | Não envolvido em PoV (overhead alto); entra quando Mêtis define produção |
| `warrior-hephaestus` (existente) | Delegação: widgets em Skills (continuação de v1) |
| `warrior-apollo` (router, existente) | Delegação: Python tools em Skills (continuação de v1) |
| `warrior-prometheus` (existente) | Não envolvido — Prometheus é feature design de plataforma (API + eventos) |
| `warrior-theseus` (existente) | Não envolvido em PoV — domain modeling profundo é Mêtis |

## Pré-requisitos

### Bloqueantes

- **plan-029 mergeado:** `warrior-claudionor` v1 existe com `kata-skill-implement`, `kata-skill-validate`, `kata-skill-package`. Este plano expande, não recria
- **plan-033 mergeado:** `lex-agent-construction-directives` + `codex-agent-construction-directives` (também bloqueante de plan-032). Sem este Lex, Claudionor não tem como impor Diretriz 01 item "stage: pre-operational explícito" em todo PoV

### Recomendado (não bloqueante)

- **plan-030 (analytics)**: `kata-pov-observability-instrument` reusa `check_posthog.py` quando PoV tem widgets UI

## Escopo (deste plano)

### Artefatos a criar (todos em pt-BR + es + en)

| #  | Tipo  | Nome                                | Path                                                                              |
|----|-------|-------------------------------------|-----------------------------------------------------------------------------------|
| 1  | Kata  | `kata-pov-scope-define`             | `framework/{lang}/engineering/agents/katas/kata-pov-scope-define.md`             |
| 2  | Kata  | `kata-pov-system-prompt`            | `framework/{lang}/engineering/agents/katas/kata-pov-system-prompt.md`            |
| 3  | Kata  | `kata-pov-tools-select`             | `framework/{lang}/engineering/agents/katas/kata-pov-tools-select.md`             |
| 4  | Kata  | `kata-pov-context-curate`           | `framework/{lang}/engineering/agents/katas/kata-pov-context-curate.md`           |
| 5  | Kata  | `kata-pov-observability-instrument` | `framework/{lang}/engineering/agents/katas/kata-pov-observability-instrument.md` |
| 6  | Kata  | `kata-pov-feedback-attach`          | `framework/{lang}/engineering/agents/katas/kata-pov-feedback-attach.md`          |
| 7  | Kata  | `kata-pov-value-track`              | `framework/{lang}/engineering/agents/katas/kata-pov-value-track.md`              |
| 8  | Kata  | `kata-agent-author`                 | `framework/{lang}/engineering/agents/katas/kata-agent-author.md`                 |
| 9  | Cry   | `cry-pov`                           | `framework/{lang}/engineering/agents/cries/cry-pov.md`                           |
| 10 | Cry   | `cry-agent` (subagent isolado)      | `framework/{lang}/engineering/agents/cries/cry-agent.md`                         |

**Subclade compartilhada com Mêtis:** `engineering/agents/`. As duas pernas do ciclo (PoV e Operação Concreta) habitam o mesmo lugar — facilita navegação e reforça a unidade conceitual.

### Artefatos a atualizar (de plan-029 v1)

| #  | Tipo    | Nome                            | Mudança                                                                                  |
|----|---------|---------------------------------|------------------------------------------------------------------------------------------|
| 11 | Warrior | `warrior-claudionor`             | Persona reframada: "Pré-operacional Agent Factory". Lexis carregadas adicionam `lex-agent-construction-directives`, `lex-observability-required`. Bound katas crescem para 7 katas POV + 1 agent-author + 3 katas de v1 (skill-implement/validate/package) |
| 12 | Cry     | `cry-skill` (plan-029)          | Mantém-se igual; sugere `cry-pov` como entry point preferencial quando o objetivo é "agent product PoV" e não "skill empacotada"                                       |
| 13 | Lexis   | `lex-skill-project-structure`   | Cross-link para `lex-agent-construction-directives` (skills usadas em PoV declaram `stage: pre-operational`)                                                          |

### Capability ortogonal: Plugin compose Anthropic

Originalmente prevista como Fase D na v1 deste plano, a capacidade de **gerar plugins Anthropic a partir de clades/subclades do Ahrena** foi separada para [plan-034](plan-034-claudionor-plugin-compose-anthropic.md). Não bloqueia plan-031, e plan-034 declara plan-031 como pré-requisito (precisa do `kata-agent-author` e `cry-pov` que entregamos aqui). Quando plan-034 mergear, `warrior-claudionor` ganha mais 3 katas (`kata-plugin-{compose,validate,package}`) e `cry-pov --kind plugin` passa a despachar para `cry-plugin`.

### Detalhamento dos katas POV

**kata-pov-scope-define** — Diretriz 05
- Input: problema do cliente, contexto de negócio
- Procedimento: 1 caso de uso primário; o que está dentro/fora; critério de descontinuação ("se em N semanas valor < X, encerra")
- Output: `overview.md`

**kata-pov-system-prompt** — Diretriz 01
- Input: `overview.md` + `codex-system-prompt`
- Procedimento: minimum viable per `lex-system-prompt`; **declara `stage: pre-operational`** no prompt
- Output: `system-prompt.md`

**kata-pov-tools-select** — Diretriz 03
- Input: `overview.md` + capabilities
- Procedimento: subset mínimo de tools Anthropic (web_search, str_replace, code execution); zero MCP custom; sem ML especializado
- Output: `tools.md`

**kata-pov-context-curate** — Diretriz 06
- Input: `overview.md` + domain knowledge
- Procedimento: 3-5 few-shot examples reais; 2-3 exemplos negativos curados (anti-padrões observados em LLM básico do domínio)
- Output: `context-pack.md`

**kata-pov-observability-instrument** — Cidadã de primeira classe
- Input: `overview.md`, `tools.md`
- Procedimento:
  1. **Traces:** spans por turn + por tool call (mesmo formato que Mêtis usará — facilita ponte)
  2. **Prompts log:** schema sem PII (`lex-data-retention`)
  3. **Tool calls log:** parâmetros + resultado + latência
  4. **Value metrics:** quais métricas leading rastrear (definidas em conjunto com `kata-pov-value-track`)
  5. Cross-link para `lex-observability-required` (rigor mínimo viável: trace + 1 métrica + structured log)
- Output: `observability/{traces-spec,prompts-log,tool-calls-log,value-metrics}.md`

**kata-pov-feedback-attach** — Diretriz 04
- Input: `overview.md` + tier (PoV é tier-3/4 por default)
- Procedimento: HITL leve (humano aprova outputs críticos) OU 1 métrica objetiva do ambiente (ex.: query retorna resultado válido?). Critic agent opcional
- Output: `feedback.md`

**kata-pov-value-track** — Coleta estruturada
- Input: `overview.md`, métricas leading
- Procedimento: define schema de `value-proof.md` (vivo durante operação do PoV); critério go/no-go para promoção a Operação Concreta; cadência de revisão
- Output: `value-proof.md` (template; preenchido durante operação)

**kata-agent-author** — Subagent isolado
- Input: `--slug <name>`, `--persona <warrior>` (opcional importa persona)
- Procedimento: scaffolda `agents/<name>.md` com frontmatter Anthropic; pode ser standalone (em `.claude/agents/`) ou dentro de plugin (Fase D)
- Output: arquivo `agents/<name>.md`

### Detalhamento do warrior (atualização de plan-029)

**warrior-claudionor** — Pré-operacional Agent Factory
- Persona: Claudionor (especialista da casa Claude)
- Mission: produzir agents PoV via stack Anthropic com observabilidade nativa, provando valor antes de escalar; entregar `docs/{context}/agents-pov/` consumível por Mêtis
- **Pré-condição:** problema do cliente identificado + capacidade de coletar value metric leading
- Lexis carregadas: `lex-agent-construction-directives` (master), `lex-system-prompt`, `lex-skill-project-structure`, `lex-skill-package-structure`, `lex-observability-required`, `lex-data-retention`
- Codex consultados: `codex-agent-construction-directives`, `codex-system-prompt`, `codex-skill-anthropic-agent-skills`, `codex-skill-project-architecture`, `codex-skill-tools-and-widgets`
- Katas que invoca:
  - 7 katas POV (deste plano)
  - `kata-agent-author` (deste plano)
  - `kata-skill-implement`, `kata-skill-validate`, `kata-skill-package` (de plan-029)
  - `kata-plugin-*` (Fase D opcional)
- Delega via `Agent`:
  - `warrior-hephaestus` — widgets dentro de Skill (continuação de v1)
  - `warrior-apollo` (router) — Python tools/scripts dentro de Skill
- Contraexemplos:
  - **Não** opera em Operação Concreta (refere ao Mêtis)
  - **Não** projeta arquitetura de produção (escopo de PoV é minimum viable)
  - **Não** implementa memória persistente (estágio não pede)
  - **Não** prossegue PoV sem observability instrumentada

### Detalhamento dos cries

**cry-pov** — Entry point principal
- Args:
  - `--context <name>` (obrigatório)
  - `--kind {skill|subagent|plugin}` (obrigatório) — qual artefato Anthropic spawnar
  - `--problem <description>` (obrigatório) — problema do cliente em 1 frase
  - `--value-metric <description>` (obrigatório) — métrica leading que se quer mover
  - `--dry-run` (opcional)
- Invoca `warrior-claudionor`

**cry-agent** — Subagent isolado standalone
- Args: `--slug <name>`, `--persona <warrior>` (opcional), `--target {.claude/agents/|<plugin-path>/agents/}`
- Invoca `kata-agent-author` direto (uso simples, sem ciclo PoV completo)

## Steps

### Bloco A — Pré-requisitos

- [ ] **A.1.** Aguardar plan-029 mergeado (Claudionor v1 + skill katas)
- [ ] **A.2.** Aguardar plan-033 mergeado (`lex-agent-construction-directives` + codex)

### Bloco B — Setup

- [ ] **B.1.** Issue (`feature-request`, labels `feature request ➕` + `framework` + `agents` + `pov`, Issue Type `Feature`, assignee `@me`)
- [ ] **B.2.** Branch `feat/{N}-claudionor-preoperational-pov-factory` em worktree
- [ ] **B.3.** Status do plan → `in-progress`

### Bloco C — Katas POV (pt-BR; depois replicar es + en)

- [ ] **C.1.** `kata-pov-scope-define.md` (pt-BR)
- [ ] **C.2.** `kata-pov-system-prompt.md` (pt-BR)
- [ ] **C.3.** `kata-pov-tools-select.md` (pt-BR)
- [ ] **C.4.** `kata-pov-context-curate.md` (pt-BR)
- [ ] **C.5.** `kata-pov-observability-instrument.md` (pt-BR) — cidadã de primeira classe
- [ ] **C.6.** `kata-pov-feedback-attach.md` (pt-BR)
- [ ] **C.7.** `kata-pov-value-track.md` (pt-BR)
- [ ] **C.8.** `kata-agent-author.md` (pt-BR)
- [ ] **C.9.** Replicar C.1–C.8 para es e en (16 traduções)

### Bloco D — Cries

- [ ] **D.1.** `cry-pov.md` (pt-BR) — entry point principal
- [ ] **D.2.** `cry-agent.md` (pt-BR) — subagent isolado
- [ ] **D.3.** Replicar es + en

### Bloco E — Reframe Claudionor + cross-links

- [ ] **E.1.** Atualizar `warrior-claudionor` (3 línguas) — persona reframada para "Pré-operacional Agent Factory"; bound katas crescem
- [ ] **E.2.** Atualizar `lex-skill-project-structure` (3 línguas) — cross-link `lex-agent-construction-directives`
- [ ] **E.3.** Atualizar `cry-skill` (plan-029, 3 línguas) — sugere `cry-pov` como entry point preferencial quando o caso é "agent product PoV"
- [ ] **E.4.** Atualizar `framework/platforms.yaml` — entries para 8 katas POV + 2 cries

### Bloco F — Sync e dogfood

- [ ] **F.1.** Sync — `python3 scripts/install.py --self --target . --platform {claude-code,cursor}`
- [ ] **F.2.** **Dogfood do ciclo PoV completo:**
  1. Eleger problema real do cliente (proposta: **reconciliação contábil PoV** — alinha com Isac roadmap; será a contraparte do dogfood de Mêtis em plan-032)
  2. Rodar `cry-pov --context reconciliation --kind skill --problem "automatizar reconciliação de extrato bancário com lançamentos contábeis" --value-metric "% de reconciliação automática em janela de 4 semanas"`
  3. Verificar `docs/reconciliation/agents-pov/` produzido com 7+ arquivos (overview, system-prompt, tools, context-pack, observability/, feedback, value-proof)
  4. Skill implementada via `kata-skill-implement` (delegação para v1)
  5. **Operar PoV por janela curta** (mesmo simulada em sandbox) — preencher `value-proof.md` com dados reais ou fixtures
- [ ] **F.3.** **Validar ponte com Mêtis (cross-plan):**
  1. Rodar `cry-agent-design --context reconciliation --from-pov docs/reconciliation/agents-pov/`
  2. Verificar que `kata-dooc-validate` (plan-032) consome corretamente os 9 itens (especialmente `value-proof.md` e `observability/`)
  3. Cenário negativo: PoV sem `observability/` → DoOC item 5 ❌; Mêtis bloqueia
- [ ] **F.4.** `kata-artifact-self-review` em cada arquivo gerado em F.2

### Bloco G — Fechamento

- [ ] **G.1.** Commits atômicos:
  1. `feat(agents): add 7 POV katas + kata-agent-author`
  2. `feat(agents): add cry-pov + cry-agent entry points`
  3. `chore(agents): reframe warrior-claudionor as Pre-operational Agent Factory`
  4. `chore: cross-link with lex-agent-construction-directives and update cry-skill`
  5. `chore: sync .claude and .cursor`
- [ ] **G.2.** PR via `kata-contributing-pr` — `Closes #{N}`, mirroring + `agents` + `pov`, size, CODEOWNERS; body referencia plan-031, plan-029, plan-033 (pre-req-D), plan-032 (ponte downstream), plan-034 (capability ortogonal)
- [ ] **G.3.** Pós-merge — status `done` → `archived`, remover worktree

## Dependências

### Bloqueantes

- **plan-029:** `warrior-claudionor` v1 + skill katas
- **plan-033:** `lex-agent-construction-directives` + `codex-agent-construction-directives` (também bloqueante de plan-032)

### Recomendado (não bloqueante)

- **plan-030:** `kata-pov-observability-instrument` reusa `check_posthog.py` quando PoV tem widgets UI

### Acoplamento

- **plan-032 (Mêtis):** consumidor downstream do output `docs/{context}/agents-pov/`. Os dois plans podem ser desenvolvidos em paralelo após pre-req-D mergeado; dogfood end-to-end exige ambos prontos
- **plan-013:** independente — Apollo-Agents só entra quando Mêtis projeta produção

## Riscos

| # | Risco                                                                                                          | Probab. | Mitigação                                                                                                              |
|---|----------------------------------------------------------------------------------------------------------------|:------:|-------------------------------------------------------------------------------------------------------------------------|
| 1 | Sobreposição com `kata-skill-implement` (v1) — usuário confunde "skill empacotada" e "agent PoV"               | Alta   | `cry-skill` mantém-se para "skill como artefato distribuível"; `cry-pov` é "agent PoV cujo objetivo é provar valor". Documentar nos dois |
| 2 | Claudionor vira gargalo central — cada PoV passa por ela                                                        | Baixa  | Delegação via `Agent` é cheap; Claudionor mantém estado mínimo                                                          |
| 3 | Observability data do PoV vaza PII para `--from-pov` de Mêtis                                                  | Alta   | `kata-pov-observability-instrument` declara contrato sem PII; `lex-data-retention` aplicado; teste em F.3 com fixtures contendo PII (deve sanear) |
| 4 | PoV opera por janela longa demais sem promover/encerrar (zumbi)                                                | Média  | `kata-pov-scope-define` exige critério de descontinuação no início; `value-proof.md` exige cadência de revisão definida |
| 5 | `value-proof.md` vira documento "de fachada" sem dados reais                                                   | Alta   | `kata-pov-value-track` exige schema com campos obrigatórios e SHA do dataset/observabilidade; vazio = inválido            |
| 6 | Multilingue incompleto: 10 artefatos × 3 línguas = 30 arquivos                                                  | Alta   | Steps separados por língua; PR pode ser stacked; Mnemosyne (plan-028) flagaria gap                                       |
| 7 | Ponte `--from-pov` quebra por divergência de schema entre PoV output e DoOC consumer                           | Alta   | Schema declarado em `kata-pov-observability-instrument` é a versão canônica; `kata-dooc-validate` (plan-032) lê esse schema; testes cross-plan em F.3 |
| 8 | DoOC item 9 (`stage: pre-operational` no system prompt) só funciona para PoVs criados após o merge             | Média  | `lex-agent-construction-directives` (plan-033) tem cláusula de transição; PoVs anteriores tratados como `stage: legacy-pov` com warning |
| 9 | Delegação a `kata-skill-implement` confunde usuário sobre quando o output é "skill" vs "PoV agent"             | Média  | `cry-pov --kind skill` produz **PoV agent que usa Skill como tooling de implementação**; `cry-skill` produz **skill como artefato em si**. Documentar |

## Decisões em aberto

- **Naming `cry-pov` vs `cry-agent-pov`:** proposta `cry-pov` (curto); alternativa `cry-agent-pov` é mais explícito mas verboso
- **`docs/{context}/agents-pov/` vs `docs/{context}/agents/pov/`:** proposta sufixo (`agents-pov/`) para deixar `agents/` reservado a Operação Concreta. Validar com pre-req-C
- **Subagent (`kind=subagent`) sem fluxo POV completo:** uso `cry-agent --slug <name>` é OK para casos triviais. Quando precisa do ciclo POV, usar `cry-pov --kind subagent`
- **Stage tag `legacy-pov`:** introduzido pela cláusula de transição de pre-req-D para tratar PoVs anteriores. Quem os promove a `pre-operational` legítimo? Provavelmente uma execução manual de `kata-pov-system-prompt` para retrofitar
- **Cadência de revisão default em `value-proof.md`:** semanal? quinzenal? Diretriz pode ser "tier-1/2 do PoV semanal; tier-3/4 quinzenal"

## Verificação

1. **Estrutura entregue:** 8 katas + 2 cries × 3 línguas = 30 arquivos novos em `framework/{lang}/engineering/agents/`
2. **Atualizações:** `warrior-claudionor` (3), `cry-skill` (3), `lex-skill-project-structure` (3), `platforms.yaml`, `.claude/`, `.cursor/`
3. **Pré-requisitos:** plan-029 + pre-req-D mergeados
4. **Dogfood (F.2 + F.3):** ciclo PoV completo + ponte com Mêtis validados em context real
5. **Coerência cruzada:**
   - 6 Diretrizes presentes no output de PoV (cada uma referenciada em ≥1 documento)
   - `stage: pre-operational` declarado explícito no system prompt
   - `value-proof.md` com schema completo
   - Observability sem PII
   - Output do PoV consumível por `cry-agent-design --from-pov`
6. **HARD-GATE de PR:** atende `lex-pr-quality`
7. **Sem nova Lexis** criada neste plano (Lex está em plan-033)
8. **Body da PR final:** referencia plan-031 + plan-029 + plan-033 + plan-032 (ponte downstream) + plan-034 (capability ortogonal)

## Sinergias futuras (não-bloqueante)

- **plan-028 (Mnemosyne):** par futuro de `lex-doc-coherence` cobrindo "diff toca PoV → value-proof.md atualizado"
- **plan-030 (analytics):** `check_posthog.py` invocado por `kata-pov-observability-instrument` quando PoV tem widget UI
- **plan-021 (Ahrena MCP server):** se entregue, PoVs gerados podem incluir `.mcp.json` apontando para o MCP do Ahrena (via plan-034)
- **Marketplace Ahrena (futuro):** plan-034 + `.claude-plugin/marketplace.json` agregando plugins gerados de clades/subclades — quando tivermos ≥3 plugins maduros
