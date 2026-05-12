---
plan_id: "038"
title: "pm-topology-per-component-and-epic-decomposition"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-09T13:00:00Z"
updated_at: "2026-05-09T14:00:00Z"
---

# Plano: PM Topology per Component + Decomposição do Epic em US/Bug/Tech-task

## Objetivo

Costurar a etapa entre Epic (output da triagem em plan-037) e Athena (executor por Issue). Introduzir: (a) decomposição do Epic em filhos via `warrior-calliope` (musa da poesia épica — preparador) + humano (homologa); (b) PM warrior por Component criando os faltantes (`warrior-aglaea` para UI, `warrior-eos` para Jobs), narrowing de `warrior-prometheus` para escopo API-only, integração formal de `warrior-metis` (plan-032) como Agents PM. Bug e Tech-task pulam PM e vão direto para Athena. Subtasks da execução do Athena viram sub-issues GitHub nativas via `Tracked by #N`.

## Contexto

### Estado atual

- `warrior-prometheus` é descrito como "Technical Product Manager" e hoje orquestra **todo o design** (domain modeling + API + events). Faz três trabalhos diferentes; precisa narrowizar.
- `warrior-metis` planejado em [plan-032](plan-032-warrior-metis-apm-agents.md) como Agents PM — **não shipado**.
- UI PM = **gap total**.
- Jobs PM = **gap total**.
- Epic decomposition = **gap total**. Hoje Issues nascem ad-hoc na mão do humano sem warrior preparador.
- `warrior-athena` recebe Issue do GitHub e cria `docs/issues/issue-{n}/`, mas não cria sub-issues GitHub para subtasks da implementação.

### Decisões fechadas com o usuário (2026-05-09)

1. **Quem decompõe o Epic**: ✅ warrior preparador + humano homologa (paralelo a Themis em plan-037). Nome confirmado: **Calliope** (Καλλιόπη, musa da poesia épica — literalmente "líder das musas, voz bonita"; decompõe a narrativa épica em capítulos).
2. **Bug/Tech-task**: ✅ pulam PM, vão direto para Athena.
3. **Subtasks da execução**: ✅ sub-issues GitHub nativas (`Tracked by #N` no body do filho).
4. **PM warriors UI e Jobs**: ✅ nomes confirmados:
   - **Aglaea** (Ἀγλαΐα) — UI PM. Uma das três Cárites/Graças; embodies *beauty + adornment*.
   - **Eos** (Ἠώς) — Jobs PM. Deusa da aurora; ciclos diários, renovação — fits batch/scheduled/cron.
5. **Prometheus**: ✅ narrowiza para **API-only**. Theseus, Daedalus, Kronos viram katas bound a Prometheus, com chamada isolada permitida (decisão 1 abaixo).
6. **Metis**: ✅ integrada formalmente como Agents PM via `codex-pm-topology` (artefato deste plano). Plan-032 entrega o warrior; plan-038 entrega a topologia.

### Cadeia desenhada — duas camadas de decomposição

**Layer 1 — Decomposição de produto (Calliope, humano homologa)**: 1 Epic → N child Issues (US/Bug/Tech-task).
**Layer 2 — Decomposição de implementação (Eunomia, invocada por Athena)**: 1 child Issue → N subtask sub-issues executáveis.

```
Epic GitHub Issue (output da triagem em plan-037)
  └─→ /cry-decompose-epic <epic#>                         ← LAYER 1 (produto)
        └─→ warrior-calliope
              ├─ pre-fase IA: lê Epic, identifica Components afetados a partir do body, sugere decomposição inicial
              │   ├─ Para cada Component → ≥1 User Story
              │   ├─ Bugs identificados na triagem → Bug child Issue
              │   └─ Tarefas técnicas (refactor, dep upgrade) → Tech-task child Issue
              └─ humano homologa: confirma/ajusta filhos, prioridade, escopo, dependências
        └─→ Calliope cria os child Issues (Tracked by #<EPIC>, Issue Type correto, verificação pós-criação):
              ├─ US-API     (label pending-spec, Type Feature) → /cry-spec-api    → warrior-prometheus → docs/{context}/api/*    → label spec-ready
              ├─ US-Agents  (label pending-spec, Type Feature) → /cry-spec-agents → warrior-metis      → docs/{context}/agents/* → label spec-ready
              ├─ US-UI      (label pending-spec, Type Feature) → /cry-spec-ui     → warrior-aglaea     → docs/{context}/ui/*     → label spec-ready
              ├─ US-Jobs    (label pending-spec, Type Feature) → /cry-spec-jobs   → warrior-eos        → docs/{context}/jobs/*   → label spec-ready
              ├─ Bug        (Type Bug,  sem label pending-spec — pronto para Athena)
              └─ Tech-task  (Type Task, sem label pending-spec — pronto para Athena)

        └─→ /cry-implement-issue <child#>
              └─→ warrior-athena
                    ├─ Phase 1: valida DoR child (Tracked by Epic + label spec-ready se US)
                    ├─ Phase 2-3: requirements + architecture (consome spec do PM)
                    ├─ Phase 4: implementa via engineer warrior do Component (apollo-api/agents/jobs, hephaestus, iris)
                    │   └─→ invoca warrior-eunomia                                ← LAYER 2 (implementação)
                    │         ├─ Eunomia decompõe child Issue em subtasks executáveis
                    │         ├─ Cria sub-issues GitHub (Tracked by #<child Issue>, Type Task, verificação pós-criação)
                    │         └─ Cada subtask Issue body:
                    │               ├─ Subtask pequena: plano inteiro embutido
                    │               └─ Subtask grande: resumo detalhado + link para `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md`
                    ├─ Phase 5-6: security review + quality gate
                    ├─ Phase 7: PR
                    └─ Phase 8 (de plan-037): delivery handoff para Hestia se tier-1/2
```

## Escopo

### Artefatos a criar (todos em pt-BR + es + en por `lex-framework-language`)

| # | Tipo | Nome | Path | Função |
|---|------|------|------|--------|
| 1 | Warrior | `warrior-calliope` | `framework/{lang}/product/decomposition/warriors/warrior-calliope.md` | Decompõe Epic em filhos; humano homologa; cria Issue children no GitHub |
| 2 | Kata | `kata-decompose-epic` | `framework/{lang}/product/decomposition/katas/kata-decompose-epic.md` | Procedimento decomposição (IA prep + humano decide + Issue children criados) |
| 3 | Cry | `cry-decompose-epic` | `framework/{lang}/product/decomposition/cries/cry-decompose-epic.md` | `/cry-decompose-epic <epic#>` |
| 4 | Lexis | `lex-epic-decomposition-required` | `framework/{lang}/product/decomposition/lexis/lex-epic-decomposition-required.md` | HARD-GATE: Athena MUST NOT receber Issue Type Epic; Epic MUST passar por `kata-decompose-epic` antes |
| 5 | Codex | `codex-epic-decomposition` | `framework/{lang}/product/decomposition/codex/codex-epic-decomposition.md` | Manual: como decompor (1 US por Component tocado, padrões, exemplos canônicos) |
| 6 | Warrior | `warrior-aglaea` | `framework/{lang}/engineering/frontend/warriors/warrior-aglaea.md` | UI PM — produz `docs/{context}/ui/*` (component contract, design tokens consumidos, interaction model, accessibility, copy) |
| 7 | Kata | `kata-ui-spec-design` | `framework/{lang}/engineering/frontend/katas/kata-ui-spec-design.md` | Procedimento spec UI (Figma extract via MCP → Storybook story scaffold → component contract com props/states/a11y) |
| 8 | Cry | `cry-spec-ui` | `framework/{lang}/engineering/frontend/cries/cry-spec-ui.md` | `/cry-spec-ui <us#>` |
| 9 | Warrior | `warrior-eos` | `framework/{lang}/engineering/backend/warriors/warrior-eos.md` | Jobs PM — produz `docs/{context}/jobs/*` (job contract: trigger, schedule, idempotency key, retry/backoff, dead-letter, timeout, observability) |
| 10 | Kata | `kata-jobs-spec-design` | `framework/{lang}/engineering/backend/katas/kata-jobs-spec-design.md` | Procedimento spec Job (Step Functions / Lambda Powertools) |
| 11 | Cry | `cry-spec-jobs` | `framework/{lang}/engineering/backend/cries/cry-spec-jobs.md` | `/cry-spec-jobs <us#>` |
| 12 | Lexis | `lex-pm-per-component` | `framework/{lang}/_foundation/process/lexis/lex-pm-per-component.md` | HARD-GATE: toda US tocando Component MUST ter passado pelo PM correspondente (label `spec-ready`) antes de Athena receber. Bug/Tech-task isentos. |
| 13 | Codex | `codex-pm-topology` | `framework/{lang}/_foundation/process/codex/codex-pm-topology.md` | Manual canônico: tabela Component → PM → Engineer; outputs esperados de cada PM; pipeline de design |
| 14 | Cry | `cry-spec-api` | `framework/{lang}/engineering/platform/cries/cry-spec-api.md` | `/cry-spec-api <us#>` — invoca Prometheus (narrowizado). Substitui `cry-feature-design` quando contexto é US-API; alias mantido para retrocompatibilidade. |
| 15 | Cry | `cry-spec-agents` | `framework/{lang}/engineering/agents/cries/cry-spec-agents.md` | `/cry-spec-agents <us#>` — invoca Metis (plan-032). Cria caminho oficial paralelo aos outros 3 PMs. |
| 16 | Warrior | `warrior-eunomia` | `framework/{lang}/engineering/workflow/warriors/warrior-eunomia.md` | Subtask creator (Layer 2). Decompõe child Issue (US/Bug/Tech-task) em subtask sub-issues executáveis. Invocada por Athena Phase 4. |
| 17 | Kata | `kata-create-subtasks` | `framework/{lang}/engineering/workflow/katas/kata-create-subtasks.md` | Procedimento Eunomia: lê child Issue + spec do PM, decompõe em subtasks, escreve plano (body inline ou anexo + summary), cria sub-issues GitHub com Issue Type Task e verificação pós-criação. |
| 18 | Cry | `cry-create-subtasks` | `framework/{lang}/engineering/workflow/cries/cry-create-subtasks.md` | `/cry-create-subtasks <child#>` — invocação manual quando Athena não orquestrou (ex: re-criação após mudança de escopo). Caminho primário é Athena → Eunomia interno. |
| 19 | Template | `subtask.yml` | `framework/{lang}/_foundation/contributing_templates/subtask.yml` | GitHub Issue Template para subtask: campos parent (`Tracked by`), summary, plan (inline ou link ao anexo), acceptance criteria, dependencies. Issue Type Task. |
| 20 | Lexis | `lex-issue-type-verified` | `framework/{lang}/_foundation/contributing/lexis/lex-issue-type-verified.md` | HARD-GATE específico: toda criação programática de Issue MUST executar verificação pós-criação via `gh api repos/{owner}/{repo}/issues/{N}` confirmando que `type` está populado e correto. Aplica a Calliope, Eunomia, kata-contributing-issue. |

### Artefatos a atualizar (cross-references e narrowing)

| # | Tipo | Nome | Mudança |
|---|------|------|---------|
| 21 | Warrior | `warrior-prometheus` | Narrowing: persona/escopo de "Technical Product Manager" → **"API Product Manager"**. Bound katas explícitas: `kata-domain-model`, `kata-api-design-oas`, `kata-api-design-doc`, `kata-event-storm`, `kata-events-doc`. Output exclusivo: `docs/{context}/api/*` (e `docs/{context}/events/*` quando API publica eventos). |
| 22 | Cry | `cry-feature-design` | Marca como **alias** de `cry-spec-api`. Mantém retrocompatibilidade por 1 release. Adiciona deprecation notice. |
| 23 | Kata | `kata-api-design-oas` | Adicionar referência a `lex-pm-per-component` em *Referências*. |
| 24 | Lexis | `lex-feature-dor` (criado em plan-037) | Estender child-level: child Issue MUST conter `Tracked by #<EPIC>`. Atributos Idea/Components/Tier herdados via Epic. US child MUST ter label `spec-ready` antes de Athena Phase 1 (`lex-pm-per-component`). Bug/Tech-task isentos. |
| 25 | Kata | `kata-issue-analysis` (de plan-037) | Distinguir Issue Type no Phase 1: (a) Epic → bloqueia Athena, manda para `cry-decompose-epic`; (b) child sem label `spec-ready` quando US → bloqueia, manda para `cry-spec-{tipo}`; (c) child Bug/Tech-task ou US com `spec-ready` → prossegue. |
| 26 | Warrior | `warrior-athena` | Phase 4 **invoca warrior-eunomia** (não cria sub-issues diretamente — Athena é orquestrador). Phase 1 rejeita Epic explicitamente. |
| 27 | Lexis | `lex-issue-driven` (de plan-037) | Reflete: Athena MUST NOT receber Issue Type Epic; só child Issues (US com spec-ready, Bug, Tech-task). |
| 28 | Lexis | `lex-issue-quality` (existente) | Adicionar `subtask` na lista de templates aprovados; mapear para Issue Type Task. Reforçar HARD-GATE existente apontando para `lex-issue-type-verified` quando criação for programática. |
| 29 | Kata | `kata-contributing-issue` (existente) | Incluir verificação pós-criação per `lex-issue-type-verified` (passo terminal: `gh api` GET issue, valida `type`). |
| 30 | Warrior | `warrior-metis` (criado em plan-032) | Cross-ref para `codex-pm-topology` e `cry-spec-agents`; alinhar output `docs/{context}/agents/` ao padrão `docs/{context}/{tipo}/*` da topologia. |
| 31 | Plan | `plan-013` (apollo split) | Adicionar nota no Contexto: cada `apollo-{api,agents,jobs}` é o engineer pair do PM correspondente desta topologia (Prometheus/Metis/Eos). |

### Entradas em `framework/platforms.yaml`

Por `lex-platforms-rules`, cada Lexis e Codex novo precisa entrada em `cursor.rules`:
- `product/decomposition/lexis/lex-epic-decomposition-required`
- `product/decomposition/codex/codex-epic-decomposition`
- `_foundation/process/lexis/lex-pm-per-component`
- `_foundation/process/codex/codex-pm-topology`
- `_foundation/contributing/lexis/lex-issue-type-verified`

### Não escopo deste plano

- Implementação dos engineers (`apollo-api/agents/jobs`) — plan-013.
- Conteúdo das specs em si (apenas a topologia + outputs documentais, não o código gerado a partir delas).
- `warrior-claudionor` (PoV agent design) — plan-031.
- Estrutura física de Components (`components/api/`, `components/jobs/`, etc.) nos repos de produto — plans 011–012.
- Migração de Issues legacy para nova topologia. Não retroage (igual plan-037).
- Templates de UI spec / Jobs spec totalmente desenvolvidos. v1 desses katas tem template mínimo; refinamento iterativo em planos subsequentes.

## Decisões fechadas com o usuário (2026-05-09)

1. **Theseus/Daedalus/Kronos**: ✅ Opção A — mantêm-se como warriors disponíveis; no fluxo da topologia são invocados como katas (`kata-domain-model`, `kata-api-design-oas`, `kata-event-storm`) bound a Prometheus. Outros PMs podem invocar isoladamente quando o Component tem domínio próprio.

2. **Calliope cria Issue children**: ✅ Opção A — Calliope cria os children no GitHub (`gh issue create`) com `Tracked by #<EPIC>`, Issue Type correto, label `pending-spec` (US) ou pronto (Bug/Tech-task). Humano homologa antes da criação.

3. **kata-domain-model invocável por todos PMs**: ✅ Sim, knowledge reutilizável. **Aditivo HARD-GATE**: toda criação programática de Issue (por Calliope, Eunomia ou qualquer agente) MUST verificar pós-criação via `gh api` que o Issue Type foi efetivamente atribuído. Verificação em `kata-decompose-epic`, `kata-create-subtasks`, `kata-contributing-issue`. Lex-issue-quality já obriga; este plano reforça enforcement programático.

4. **Subtasks: plano no corpo + anexo**: ✅ Padrão definido:
   - Subtask **pequena** (escopo cabe no body): plano inteiro embutido no body da Issue.
   - Subtask **grande**: resumo detalhado no body + link para arquivo `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md` (anexo).
   - Critério "grande": plano > 50 linhas markdown ou >5 steps.
   - **Ação adicional**: criar novo template GitHub `.github/ISSUE_TEMPLATE/subtask.yml` para padronizar criação manual e por Eunomia. Template entra na lista de templates aprovados em `lex-issue-quality`.

5. **Athena invoca agente especializado para criar subtasks**: ✅ Confirmado — Athena é orquestrador, não cria subtasks diretamente. Novo warrior **Eunomia** (Εὐνομία, deusa do bom ordenamento, filha de Themis) decompõe child Issue em subtasks executáveis e cria as sub-issues. Athena Phase 4 invoca Eunomia.

### Bugs e Tech-tasks: Issue Types

- Bug → Issue Type **Bug** (template `bug-report` a criar se não existir).
- Tech-task → Issue Type **Task** (template `simple-task` ou novo `tech-task` se justificar).
- Subtask → Issue Type **Task** (template `subtask` novo, decisão 4 acima).

## Steps

- [ ] **1.** Abrir Issue de epic (`lex-issue-first`, `lex-issue-quality`) com template `epic`, labels (`epic`, `feature request ➕`, `process`), Issue Type `Epic`, assignee, Why/What/How preenchidos. Atualizar front-matter com `issue: "guardiatechnology/ahrena#<N>"`.
- [ ] **2.** Criar worktree e branch `feat/<N>-pm-topology-and-epic-decomposition` em `.worktrees/<N>-pm-topology-and-epic-decomposition/`.
- [x] **3.** Decisões fechadas com o usuário em 2026-05-09 (ver seção "Decisões fechadas com o usuário").
- [ ] **4.** Criar `lex-epic-decomposition-required` (3 línguas) — HARD-GATE: Athena MUST NOT receber Issue Type Epic; Epic MUST passar por `kata-decompose-epic` antes; gerou-se ≥1 child com `Tracked by #<EPIC>`.
- [ ] **5.** Criar `codex-epic-decomposition` (3 línguas) — manual:
  - Padrão: 1 US por Component tocado (mínimo).
  - Quando split em múltiplas US no mesmo Component: scope > 5 dias-IA, partes independentes do contrato público, ou time diferente.
  - Bug: cada bug identificado na triagem vira 1 Bug child.
  - Tech-task: cada chore técnico (refactor, dep upgrade, infra) vira 1 Tech-task child.
  - Exemplos canônicos.
- [ ] **6.** Criar `kata-decompose-epic` (3 línguas) — procedimento:
  - (a) Pre-fase IA (warrior-calliope): lê Epic via MCP GitHub, extrai Components do body do Epic, sugere decomposição inicial baseada em padrões de `codex-epic-decomposition`.
  - (b) Decisão humana: PO/PM confirma/ajusta filhos, prioridade, escopo, dependências.
  - (c) Output: Calliope cria Issue children no GitHub (Tracked by #<EPIC>), labels (`pending-spec` para US, sem label de spec para Bug/Tech), Issue Type correspondente. Atualiza Epic com `## Children` listando filhos criados.
- [ ] **7.** Criar `cry-decompose-epic` (3 línguas) — `/cry-decompose-epic <epic#>`. Invoca warrior-calliope.
- [ ] **8.** Criar `warrior-calliope` (3 línguas) — `framework/{lang}/product/decomposition/warriors/warrior-calliope.md`. Persona, bound katas (`kata-decompose-epic`, `kata-mcp-github-read`), HARD-GATE de homologação humana.
- [ ] **9.** Criar `lex-pm-per-component` (3 línguas) — HARD-GATE: toda US tocando Component MUST passar pelo PM correspondente (label `spec-ready` aplicado pelo PM) antes de Athena receber. Bug/Tech-task isentos.
- [ ] **10.** Criar `codex-pm-topology` (3 línguas) — manual canônico:
  - Tabela: Component (api/agents/ui/jobs) → PM warrior → cry de spec → output em docs/{context}/{tipo}/* → Engineer warrior.
  - Pipeline de design por PM: input (US child com Component identificado), procedimento (kata-{tipo}-spec-design), output (`spec-ready` label + docs).
  - Convivência com Theseus/Daedalus/Kronos como katas reutilizáveis.
- [ ] **11.** Criar `warrior-aglaea` (3 línguas) — UI PM. Persona, bound katas (`kata-ui-spec-design`, `kata-mcp-figma-extract`, `kata-domain-model` opcional). Output: `docs/{context}/ui/{component}.md` com props, states, accessibility, copy, design tokens consumidos, interaction model.
- [ ] **12.** Criar `kata-ui-spec-design` (3 línguas) — procedimento: Figma extract via MCP → análise de tokens consumidos vs `@guardia/design-system` → Storybook story scaffold → component contract (props com tipos, states, eventos, a11y).
- [ ] **13.** Criar `cry-spec-ui` (3 línguas) — `/cry-spec-ui <us#>`. Invoca Aglaea.
- [ ] **14.** Criar `warrior-eos` (3 línguas) — Jobs PM. Persona, bound katas (`kata-jobs-spec-design`, `kata-domain-model` opcional). Output: `docs/{context}/jobs/{job-name}.md` com trigger, schedule (cron/event), idempotency key strategy, retry/backoff policy, dead-letter handling, timeout, observability (span/metric/log) per `lex-observability-required`, error taxonomy.
- [ ] **15.** Criar `kata-jobs-spec-design` (3 línguas) — procedimento: trigger/schedule decision tree → idempotency design (`lex-idempotency`) → retry/backoff → dead-letter → SLO consumido (link para `docs/slo/{job}.yaml`).
- [ ] **16.** Criar `cry-spec-jobs` (3 línguas) — `/cry-spec-jobs <us#>`. Invoca Eos.
- [ ] **17.** Criar `cry-spec-api` (3 línguas) — `/cry-spec-api <us#>`. Invoca Prometheus narrowizado.
- [ ] **18.** Criar `cry-spec-agents` (3 línguas) — `/cry-spec-agents <us#>`. Invoca Metis (plan-032). Coexistência: se plan-032 não estiver shipado no merge, cry-spec-agents fica como stub apontando para plan-032; descrição clara da pendência.
- [ ] **19.** Criar `lex-issue-type-verified` (3 línguas) — HARD-GATE: toda criação programática de Issue MUST executar passo terminal `gh api repos/{owner}/{repo}/issues/{N}` confirmando `type` populado e correto. Falha de verificação bloqueia o fluxo da kata invocadora.
- [ ] **20.** Criar `warrior-eunomia` (3 línguas) — `framework/{lang}/engineering/workflow/warriors/warrior-eunomia.md`. Persona (deusa do bom ordenamento, filha de Themis). Bound katas: `kata-create-subtasks`, `kata-mcp-github-read`, `kata-contributing-issue`. Invocada por Athena Phase 4.
- [ ] **21.** Criar `kata-create-subtasks` (3 línguas) — procedimento Eunomia:
  - (a) Lê child Issue (body, spec do PM linkada via `docs/{context}/{tipo}/*`, ACs).
  - (b) Decompõe em subtasks executáveis (granularidade: cada subtask cabe em 1 PR).
  - (c) Para cada subtask: gera plano (≤50 linhas → body inline; >50 linhas → resumo no body + arquivo `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md`).
  - (d) Cria sub-issue GitHub via template `subtask.yml`, Issue Type Task, `Tracked by #<child Issue>`, labels herdados.
  - (e) Verifica pós-criação per `lex-issue-type-verified`.
  - (f) Atualiza child Issue com `## Subtasks` listando sub-issues criadas.
- [ ] **22.** Criar `cry-create-subtasks` (3 línguas) — `/cry-create-subtasks <child#>`. Invocação manual (caminho primário é Athena → Eunomia interno).
- [ ] **23.** Criar template GitHub `subtask.yml` em `framework/{lang}/_foundation/contributing_templates/subtask.yml` — campos: parent (`Tracked by #<N>`), summary, plan inline (textarea — pequena) ou plan link (anexo file path), acceptance criteria, dependencies. Issue Type Task. Adicionar a `lex-issue-quality` na lista de templates aprovados.
- [ ] **24.** Atualizar `warrior-prometheus` (3 línguas) — narrowing para "API Product Manager". Bound katas explícitas: `kata-domain-model`, `kata-api-design-oas`, `kata-api-design-doc`, `kata-event-storm`, `kata-events-doc`. Output: `docs/{context}/api/*` + `docs/{context}/events/*` (eventos publicados pela API).
- [ ] **25.** Atualizar `cry-feature-design` (3 línguas) — marca como **alias** de `cry-spec-api` com deprecation notice. Mantém por 1 release; remoção em plano futuro.
- [ ] **26.** Atualizar `kata-api-design-oas` (3 línguas) — adicionar referência a `lex-pm-per-component` em *Referências*.
- [ ] **27.** Atualizar `lex-feature-dor` (3 línguas, criado em plan-037) — estender com child-level:
  - Child Issue MUST conter `Tracked by #<EPIC>`.
  - US child MUST ter label `spec-ready` (aplicado pelo PM correspondente após a spec).
  - Bug/Tech-task isentos do `spec-ready`.
- [ ] **28.** Atualizar `kata-issue-analysis` (3 línguas, de plan-037) — Phase 1 distingue Issue Type:
  - Epic → bloqueia Athena, manda para `/cry-decompose-epic`.
  - US child sem `spec-ready` → bloqueia, manda para `/cry-spec-{tipo}`.
  - US child com `spec-ready`, ou Bug, ou Tech-task → prossegue.
- [ ] **29.** Atualizar `warrior-athena` (3 línguas) — Phase 4 **invoca warrior-eunomia** (não cria sub-issues diretamente — Athena é orquestrador). Phase 1 rejeita Issue Type Epic.
- [ ] **30.** Atualizar `lex-issue-driven` (3 línguas) — explicita: Athena recebe child Issues (US com spec-ready, Bug, Tech-task); nunca Epic.
- [ ] **31.** Atualizar `lex-issue-quality` (3 línguas, existente) — adicionar `subtask` na tabela de templates aprovados (Issue Type Task); reforçar HARD-GATE referenciando `lex-issue-type-verified` para criação programática.
- [ ] **32.** Atualizar `kata-contributing-issue` (3 línguas, existente) — adicionar passo terminal de verificação per `lex-issue-type-verified` (`gh api` GET issue, valida `type`).
- [ ] **33.** Atualizar `warrior-metis` (3 línguas, criado em plan-032 — só se plan-032 mergeado antes deste) — adicionar cross-ref a `codex-pm-topology` e `cry-spec-agents`; alinhar output `docs/{context}/agents/*` ao padrão da topologia. Se plan-032 não mergeado, criar nota de coordenação.
- [ ] **34.** Atualizar `plan-013` — Contexto: cada `apollo-{api,agents,jobs}` é o engineer pair do PM correspondente (Prometheus/Metis/Eos) desta topologia.
- [ ] **35.** Atualizar `framework/platforms.yaml` com entradas para os 5 novos Lexis/Codex.
- [ ] **36.** Sync local: `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor`.
- [ ] **37.** Auto-revisão de cada artefato com `kata-artifact-self-review`.
- [ ] **38.** Smoke test conceitual: percorrer cadeia ponta-a-ponta com Epic fictício (Epic em accounting-context tocando 4 Components → Calliope decompõe → 4 US + 1 Bug + 1 Tech-task children → Aglaea/Prometheus/Metis/Eos especificam → Athena recebe child → invoca Eunomia → sub-issues criadas com plan no body/anexo). Documentar em `docs/issues/issue-<N>/smoke-test.md`.
- [ ] **39.** Commits atômicos (`lex-small-commits`, `lex-conventional-commits`, `lex-commit-language`, `lex-signed-commits`):
  - `feat(decomposition): add warrior-calliope, kata-decompose-epic, cry-decompose-epic, lex-epic-decomposition-required, codex-epic-decomposition`
  - `feat(frontend): add warrior-aglaea, kata-ui-spec-design, cry-spec-ui as UI Product Manager`
  - `feat(backend): add warrior-eos, kata-jobs-spec-design, cry-spec-jobs as Jobs Product Manager`
  - `feat(process): add lex-pm-per-component and codex-pm-topology`
  - `feat(platform): add cry-spec-api as canonical entry; deprecate cry-feature-design as alias`
  - `feat(agents): add cry-spec-agents wiring metis from plan-032 into pm-topology`
  - `feat(workflow): add warrior-eunomia, kata-create-subtasks, cry-create-subtasks for layer-2 decomposition`
  - `feat(contributing): add subtask.yml template and lex-issue-type-verified for programmatic issue creation`
  - `refactor(prometheus): narrow scope to API Product Manager; bind theseus/daedalus/kronos as katas`
  - `docs(workflow): extend lex-feature-dor and kata-issue-analysis for child-level DoR (Tracked by, spec-ready)`
  - `docs(athena): phase 4 invokes eunomia; phase 1 rejects Epic`
  - `docs(contributing): extend lex-issue-quality with subtask template; kata-contributing-issue with Issue Type verification`
  - `chore(framework): register new Lexis/Codex in platforms.yaml`
  - `chore(claude): regenerate .claude/ and .cursor/ via install.py --self`
- [ ] **40.** Abrir PR (`kata-contributing-pr`, `lex-pr-quality`).
- [ ] **41.** Após merge: marcar plano `status: done`, mover para `archived/`, remover worktree.

## Dependencies

- **Plan-037** (Discovery → Triage → Component → Delivery chain): bloqueante. Plan-038 começa onde plan-037 termina (Epic existe como output da triagem).
- **Plan-013** (apollo split api/jobs/agents): paralelo. Engineer pair de cada PM. Não bloqueante para topologia, mas recomendável estar mergeado antes do smoke test conceitual (Step 31).
- **Plan-032** (warrior-metis APM agents): paralelo. Se mergeado antes, Step 26 atualiza Metis; se depois, Step 18 (cry-spec-agents) fica como stub e Metis é atualizada quando 032 mergear.
- **Plans 011–012** (Components físicos + codex-component-architecture): não bloqueantes; codex-pm-topology referencia o padrão `docs/{context}/{tipo}/*` que é compatível com a estrutura física de plans 011–012.

## Risks

| Risco | Mitigação |
|-------|-----------|
| Calliope cria Issue children "burra" sem entender Components afetados → decomposição ruim | Calliope **prepara**, humano **homologa** com HARD-GATE. Pre-fase IA usa Components do body do Epic + padrões de `codex-epic-decomposition`. Erro do Calliope é corrigido pelo humano antes da criação. |
| Acoplamento forte entre PMs cria gargalo (US-API depende de domain model que depende de events doc...) | kata-domain-model e kata-event-storm são reutilizáveis (decisão 3). Cada PM pode invocar quando necessário; não há linha de produção. Calliope na decomposição já identifica dependências entre filhos. |
| Prometheus narrowing quebra fluxos existentes | `cry-feature-design` mantido como alias por 1 release (Step 20). Deprecation notice. Migração gradual. |
| US tocando múltiplos Components (ex: feature que precisa API + Job + UI) gera 3 PMs invocados em paralelo | Padrão decomposição (`codex-epic-decomposition`): 1 US por Component tocado. Feature cross-Component vira 3+ US filhas, cada uma com PM próprio. Calliope identifica e cria múltiplos children. |
| Aglaea/Eos v1 com katas de spec rasos (template mínimo) | Aceito. v1 é "estrutura primeiro, profundidade depois". Refinamento iterativo via planos subsequentes quando a equipe usar e identificar gaps. |
| Plan-032 (Metis) não mergeado quando este plano executar | cry-spec-agents fica como stub apontando plan-032; warriror-metis update postergado para quando plan-032 mergear. Coordenação por Step 26 condicional. |
| Issue Type Epic vs Issue padrão: GitHub Projects/automações podem assumir Epic é tratável por Athena | `lex-epic-decomposition-required` + atualização do warrior-athena (Phase 1 rejeita Epic) bloqueiam por código. CI check opcional para detectar Epic erroneamente bypassado. |
| Decomposição muda durante execução (humano percebe que faltou US) | Re-invocar `/cry-decompose-epic <epic#>` é idempotente: Calliope detecta children existentes e propõe só novos. Humano homologa apenas o delta. |
| Eunomia gera subtasks excessivamente granulares (1 PR por linha de código) ou grosseiras demais (1 subtask = a US inteira) | Critério de granularidade definido em `kata-create-subtasks`: cada subtask cabe em 1 PR e tem entrega independente. Athena revisa lista de subtasks antes de iniciar implementação; rejeita decomposição imprópria e re-invoca Eunomia. |
| Issue Type não atribuído após criação programática (race condition GitHub API) | `lex-issue-type-verified` força verificação `gh api` pós-criação; retry automático em até 3 tentativas com backoff. Falha persistente bloqueia fluxo da kata e exige intervenção. |
| Subtask plan no body fica grande demais (perde legibilidade) | Critério "grande" definido (>50 linhas markdown ou >5 steps) força anexo + resumo no body. `kata-create-subtasks` aplica regra automaticamente. |

## Critérios de aceitação

- [ ] AC-1: `/cry-decompose-epic <epic#>` invoca Calliope; pre-fase IA gera proposta de decomposição (US por Component + Bug + Tech-task) baseada no body do Epic; humano homologa; children criados no GitHub com `Tracked by #<EPIC>` e labels corretos.
- [ ] AC-2: US child criado pela Calliope tem label `pending-spec`; após `/cry-spec-{tipo}` rodar com sucesso, label troca para `spec-ready`.
- [ ] AC-3: Athena recebendo child sem `spec-ready` (US) bloqueia em Phase 1 com mensagem clara apontando para `/cry-spec-{tipo}`.
- [ ] AC-4: Athena recebendo Issue Type Epic bloqueia em Phase 1 apontando para `/cry-decompose-epic`.
- [ ] AC-5: Athena Phase 4 invoca warrior-eunomia (não cria sub-issues diretamente); Eunomia decompõe child Issue e cria sub-issues GitHub com `Tracked by #<child Issue>`, Issue Type Task, plano no body (≤50 linhas) ou resumo+anexo (>50 linhas).
- [ ] AC-6: warrior-prometheus persona/escopo descreve "API Product Manager"; bound katas explícitas; output `docs/{context}/api/*` + `docs/{context}/events/*`.
- [ ] AC-7: warrior-aglaea produz `docs/{context}/ui/{component}.md` com props/states/a11y/copy/tokens em smoke test.
- [ ] AC-8: warrior-eos produz `docs/{context}/jobs/{job-name}.md` com trigger/schedule/idempotency/retry/DLQ/timeout/observability em smoke test.
- [ ] AC-9: codex-pm-topology lista a tabela completa Component → PM → Engineer e os outputs por PM.
- [ ] AC-10: framework/platforms.yaml tem entradas para os 5 novos Lexis/Codex.
- [ ] AC-11: Todos artefatos existem em pt-BR, es, en (`lex-framework-language`).
- [ ] AC-12: `kata-artifact-self-review` aplicado a cada artefato novo passa sem findings 🔴.
- [ ] AC-13: cry-feature-design mantém retrocompatibilidade como alias de cry-spec-api por 1 release.
- [ ] AC-14: Smoke test conceitual ponta-a-ponta documentado.
- [ ] AC-15: Template `subtask.yml` aprovado e listado em `lex-issue-quality`; subtask criada em smoke test segue template (parent, summary, plan inline ou anexo, ACs, dependencies).
- [ ] AC-16: `lex-issue-type-verified` aplicado: cada criação programática de Issue (Calliope, Eunomia, kata-contributing-issue) verifica `type` populado via `gh api` antes de prosseguir; falha bloqueia o fluxo.
- [ ] AC-17: warrior-eunomia bound a katas (`kata-create-subtasks`, `kata-mcp-github-read`, `kata-contributing-issue`); persona reflete filiação a Themis (família triagem→decomposição→ordenação).
