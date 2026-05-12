---
plan_id: "037"
title: "discovery-triage-component-delivery-chain"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-09T00:00:00Z"
updated_at: "2026-05-09T12:00:00Z"
---

# Plano: Cadeia Discovery → Triagem → Component → Development → Delivery

## Objetivo

Costurar os três fluxos hoje isolados (Discovery, Development, Delivery) em uma cadeia única e auditável, introduzindo o estágio de **Triagem humana** (PO/PM/CEO) entre Idea aprovada e qualquer trabalho de engenharia. A triagem decide approve/reject, calcula score com fórmula refatorada (multiplicador inverso de esforço), mapeia para Component(s) existente(s) ou cria Component novo. Issues de feature passam a exigir Idea triada + Component identificado como Definition of Ready. Pós-merge, features tocando Components tier-1/2 só sobem com SLO + runbook publicados, com handoff automático para Hestia.

## Contexto

### Estado atual mapeado

**Discovery — fluxo fechado em si mesmo:**
- `warrior-pitia` → `docs/discovery/{topic}/insights/`
- `warrior-phanes` → `docs/discovery/{topic}/ideas/` (status `promoted`)
- `cry-ideation` aponta para `warrior-prometheus` mas Prometheus não é invocado em nenhum fluxo seguinte. Idea fica órfã.

**Development — Issue-Driven via Athena:**
- `/cry-implement-issue` lê issue do GitHub diretamente.
- 7 fases + 2 gates (escopo e qualidade).
- Não exige referência a Idea nem a Component. Issue pode existir ad-hoc.

**Delivery — quase inexistente:**
- `warrior-hestia` define SLO/runbooks de forma reativa (entra "quando há incidente").
- `warrior-janus` (release orchestrator) só planejado em plan-027.
- Pós-merge é silêncio: nada dispara Hestia, nada valida SLO em primeiro deploy, nada amarra incidente de volta à Idea de origem.

### Decisões já alinhadas com o usuário

1. **Triagem é humana** — PO/PM/CEO conduz; agentes preparam material mas não decidem.
2. **Saídas obrigatórias da triagem**: decisão (approve/reject), score (impacto × valor × esforço), Component(s) afetado(s) ou novo, tier herdado.
3. **Fórmula refatorada** (substitui a atual subtração linear):
   ```
   benefit        = (0.4 × valorCliente) + (0.6 × impactoNegocio)   // 1–5
   costMultiplier = (6 − esforco) / 5                               // 0.2–1.0
   finalScore     = round(benefit × costMultiplier × 20)            // 4–100
   ```
   Comportamento: (5,5,1) → 100, (5,5,5) → 20, (1,1,5) → 4, (3,3,3) → 36.
4. **Esforço (1–5) mede atrito não-IA**: surface area (Components/contratos), incerteza/exploração, coordenação humana, reversibilidade, bloqueios externos. Tempo deixou de ser proxy.
5. **Faixas de feedback** mantidas:
   - <25 → ❌ rejeitar
   - 25–50 → 🧐 revisitar
   - 51–75 → ⭐ aprovar
   - >75 → ↗️ priorizar
6. **Component vive no repo de produto** (ex: `financial-context`, `accounting-context`, `tax-context`), com doc em `{repo}/docs/components/{name}.md`. Ahrena governa só a metodologia.
7. **Plano único** (este) costura os três fluxos. Plans 011–014 (Components físicos) e plan-027 (Janus) são dependências paralelas, não bloqueantes.

### Cadeia desenhada

```
Insight (proposed → under_review → approved)
  └─→ kata-ideation-from-insight (warrior-phanes)
        └─→ Idea (status: promoted)                                     [hoje termina aqui]
              └─→ kata-triage-idea (humano + warrior preparador)        ← NOVO ESTÁGIO
                    ├─ Decisão: approved | rejected
                    ├─ Score = (0.4×VC + 0.6×IN) × (6−E)/5 × 20
                    ├─ Component(s): existente(s) ou novo
                    └─→ Idea (status: triaged | rejected)
                    └─→ Epic GitHub Issue (Issue Type `Epic`, body: Idea + Component(s) + Tier)
                          └─→ Component (em repo de produto)            ← {repo}/docs/components/{name}.md
                                └─→ [decomposição em US/Bug/Tech-task]   ← plan-038
                                      └─→ child Issue (Tracked by Epic + Idea + Component)  ← lex-feature-dor
                                            └─→ warrior-athena (Phase 1–7)
                                                  └─→ Plano com sub-issues GitHub
                                                        └─→ PR
                                                  └─→ Pós-merge:
                                                        ├─ kata-delivery-readiness (Hestia)  ← NOVO
                                                        ├─ warrior-janus (release tag)       ← plan-027
                                                        └─→ Idea (status: delivered)
```

## Escopo

### Artefatos a criar (todos em pt-BR + es + en por `lex-framework-language`)

| # | Tipo | Nome | Path | Função |
|---|------|------|------|--------|
| 1 | Lexis | `lex-triage-required` | `framework/{lang}/product/discovery/lexis/lex-triage-required.md` | HARD-GATE: Idea `promoted` MUST passar por triagem humana antes de virar Issue |
| 2 | Codex | `codex-triage-scoring` | `framework/{lang}/product/discovery/codex/codex-triage-scoring.md` | Manual da fórmula, faixas, definição operacional dos níveis 1–5 |
| 3 | Kata | `kata-triage-idea` | `framework/{lang}/product/discovery/katas/kata-triage-idea.md` | Procedimento triagem (AI prep + humano decide) |
| 4 | Cry | `cry-triage` | `framework/{lang}/product/discovery/cries/cry-triage.md` | Shortcut `/cry-triage <idea-ref>` |
| 5 | Warrior | `warrior-themis` (nome a confirmar) | `framework/{lang}/product/discovery/warriors/warrior-themis.md` | Prepara material da triagem (histórico de Ideas similares, sugestão de Components, projeção de impacto) — humano decide |
| 6 | Lexis | `lex-component-as-source-of-truth` | `framework/{lang}/_foundation/process/lexis/lex-component-as-source-of-truth.md` | Component é artefato canônico no repo de produto; Issue de feature MUST referenciar ≥1 Component |
| 7 | Codex | `codex-component-anatomy` | `framework/{lang}/_foundation/process/codex/codex-component-anatomy.md` | Estrutura de `{repo}/docs/components/{name}.md`: metadata, tier, owners, contratos públicos, runbook, SLO |
| 8 | Kata | `kata-component-create` | `framework/{lang}/_foundation/process/katas/kata-component-create.md` | Scaffold de Component novo no repo de produto + entrada no manifest |
| 9 | Lexis | `lex-feature-dor` | `framework/{lang}/engineering/workflow/lexis/lex-feature-dor.md` | HARD-GATE: warrior-athena MUST validar Idea triada + Component(s) referenciados antes de Phase 1 |
| 10 | Lexis | `lex-delivery-readiness` | `framework/{lang}/engineering/sre/lexis/lex-delivery-readiness.md` | HARD-GATE: feature tier-1/2 MUST ter SLO + runbook publicados antes de PR merge |
| 11 | Kata | `kata-delivery-readiness` | `framework/{lang}/engineering/sre/katas/kata-delivery-readiness.md` | Hestia revalida SLO, runbook, dashboards; produz report; pode bloquear merge |
| 12 | Cry | `cry-delivery-handoff` | `framework/{lang}/engineering/sre/cries/cry-delivery-handoff.md` | Shortcut `/cry-delivery-handoff <issue#>` invocado após merge |

### Artefatos a atualizar (cross-references e fluxo)

| # | Tipo | Nome | Mudança |
|---|------|------|---------|
| 13 | Warrior | `warrior-phanes` | Output muda: handoff explícito para `cry-triage` (substitui menção a Prometheus) |
| 14 | Cry | `cry-ideation` | Mensagem final: "Idea pronta para triagem via /cry-triage" |
| 15 | Lexis | `lex-discovery-flow` | Adicionar HARD-GATE 3: transição `promoted → triaged \| rejected` exclusiva de `kata-triage-idea` |
| 16 | Codex | `codex-discovery-artifacts` | State machine completa: `proposed → under_review → approved → promoted → triaged → delivered`; ramo `rejected` em qualquer ponto após `promoted` |
| 17 | Lexis | `lex-issue-driven` | Phase 1 ganha sub-passo: validar `lex-feature-dor`; bloqueia se issue não referencia Idea triada ou Component |
| 18 | Kata | `kata-issue-analysis` | Verificar campos `Idea:`, `Component:`, `Tier:` no body da issue |
| 19 | Kata | `kata-quality-gate` | Adicionar Check 8: `lex-delivery-readiness` (skip se tier-3/4; bloqueante se tier-1/2) |
| 20 | Warrior | `warrior-athena` | Adicionar Phase 8 pós-merge: invoca `cry-delivery-handoff` automaticamente quando feature toca Component tier-1/2 |
| 21 | Warrior | `warrior-hestia` | Phase 0 explícita: receber handoff via `cry-delivery-handoff`; produzir readiness report; ownership pós-deploy |

### Entradas em `framework/platforms.yaml`

Por `lex-platforms-rules`, cada Lexis e Codex novo precisa entrada em `cursor.rules`:
- `product/discovery/lexis/lex-triage-required`
- `product/discovery/codex/codex-triage-scoring`
- `_foundation/process/lexis/lex-component-as-source-of-truth`
- `_foundation/process/codex/codex-component-anatomy`
- `engineering/workflow/lexis/lex-feature-dor`
- `engineering/sre/lexis/lex-delivery-readiness`

### Não escopo deste plano

- Implementação técnica de `warrior-janus` (fica em plan-027).
- Estrutura física de Components nos repos de produto (`components/api`, `components/jobs`, etc.) — fica em plans 011–014.
- Automação CI pós-merge (webhook GitHub → Hestia automático). Esta rodada documenta o handoff manual via `/cry-delivery-handoff`; automação fica para plano futuro.
- Migração das Ideas existentes (status `promoted`) para o novo estado `triaged`. Migração one-shot fora do plano (`lex-feature-dor` não retroage — decisão 3).
- Criação física do manifest (`docs/components/manifest.yaml`) em cada repo de produto. Próxima execução (post-merge), em cada repo: `financial-context`, `accounting-context`, `tax-context`, etc. — registrar Components existentes hoje conforme `codex-component-anatomy`.
- Decomposição do Epic em filhos (US/Bug/Tech-task), warrior-calliope (decompositor), warrior-aglaea (UI PM), warrior-eos (Jobs PM), narrowing de Prometheus para API-only, integração de Metis (plan-032). Toda essa topologia de PMs por Component fica em **plan-038**.

## Decisões fechadas com o usuário (2026-05-09)

1. **Warrior preparador da triagem**: ✅ **Opção B** — `warrior-themis` (deusa do julgamento) prepara material (coleta Ideas similares triadas, sugere Components afetados a partir do problema descrito, projeta impacto consultando insights vizinhos). Humano homologa com HARD-GATE.

2. **Component novo: em qual repo de produto**: ✅ Cada repo de produto mantém `docs/components/manifest.yaml` listando seus Components. `kata-component-create` executa dentro do repo identificado pela triagem (warrior-themis sugere, humano confirma). **Próxima execução** (fora do escopo de plan-037): criar o manifest físico em cada repo de produto após merge — registrado em "Não escopo".

3. **Issues legacy sem Idea/Component**: ✅ `lex-feature-dor` **não retroage**. Issues criadas antes do merge deste plano seguem o fluxo antigo. Após merge, novas issues exigem DoR. Migration scope: zero. Flag de data em `kata-issue-analysis`.

4. **Tier classification**: ✅ Tier herda do(s) Component(s) afetado(s). `codex-component-anatomy` exige campo `tier: 1|2|3|4` no doc do Component. Quando feature toca múltiplos Components, `tier = max(tiers)`.

5. **Score de Idea**: ✅ Imutável após triagem. Re-triagem cria nova entrada em `triage_history` no front-matter da Idea, preservando histórico. Score atual prevalece; histórico é auditável.

## Steps

- [ ] **1.** Abrir Issue de epic (`lex-issue-first`, `lex-issue-quality`) com template `epic`, labels (`epic`, `feature request ➕`, `process`), Issue Type `Epic`, assignee, Why/What/How preenchidos. Atualizar front-matter deste plano com `issue: "guardiatechnology/ahrena#<N>"`.
- [ ] **2.** Criar worktree e branch `feat/<N>-discovery-triage-delivery-chain` (`lex-git-worktrees`, `lex-git-branches`) em `.worktrees/<N>-discovery-triage-delivery-chain/`.
- [x] **3.** Decisões fechadas com o usuário em 2026-05-09 (ver seção "Decisões fechadas com o usuário").
- [ ] **4.** Criar `lex-triage-required` (3 línguas) — HARD-GATE: Idea com status `promoted` MUST passar por `kata-triage-idea` antes de virar Issue. Trava: inputs canônicos (VC, IN, E em 1–5), decisão (approved | rejected), persistência de score, mapping para Component(s).
- [ ] **5.** Criar `codex-triage-scoring` (3 línguas) — fórmula: `(0.4×VC + 0.6×IN) × (6−E)/5 × 20`. Tabela de exemplos (5,5,1)→100, (5,5,5)→20, (3,3,3)→36, (1,1,5)→4. Faixas <25/25–50/51–75/>75. Definição operacional dos níveis 1–5 de cada eixo, com ênfase em Esforço como atrito não-IA.
- [ ] **6.** Criar `kata-triage-idea` (3 línguas) — procedimento:
  - (a) **Pre-fase IA** (warrior-themis): coleta Ideas similares já triadas, sugere Components afetados, projeta impacto, sugere score inicial baseado em histórico.
  - (b) **Decisão humana**: PO/PM/CEO atribui VC/IN/E definitivos, decide approve/reject, confirma ou ajusta Component mapping.
  - (c) **Outputs (quando approved)**:
    - Idea atualizada: status `triaged`, score persistido, `triage_history` no front-matter, Components linkados.
    - **Epic GitHub Issue** criado (Issue Type `Epic`, label `epic`) com body referenciando `Idea:`, `Component(s):`, `Tier:`, e o score. Epic é o ponto de partida da decomposição em US/Bug/Tech-task (plan-038).
  - (d) **Output (quando rejected)**: Idea atualizada com status `rejected` + justificativa em `triage_history`. Não cria Epic.
- [ ] **7.** Criar `cry-triage` (3 línguas) — `/cry-triage <idea-ref>`. Invoca warrior-themis + kata-triage-idea.
- [ ] **8.** Criar `warrior-themis` (3 línguas) — orquestra pre-fase de triagem (decisão 1 = Opção B). Bound katas: `kata-mcp-notion-read` (consultar Ideas vizinhas), `kata-discovery-synthesis` (referência), prep de score sugerido.
- [ ] **9.** Criar `lex-component-as-source-of-truth` (3 línguas) — Component é artefato canônico no repo de produto. Toda Issue de feature MUST referenciar pelo menos 1 Component existente. Issue que cria Component novo MUST passar por `kata-component-create` antes.
- [ ] **10.** Criar `codex-component-anatomy` (3 línguas) — estrutura mínima de `{repo}/docs/components/{name}.md`:
  ```yaml
  ---
  name: {component-name}
  tier: 1 | 2 | 3 | 4
  owner_team: {team-name}
  escalation: {@handle | slack-channel}
  bounded_context: {context-name}
  status: active | deprecated
  ---
  ```
  Seções: Responsabilidades, Contratos públicos (APIs + eventos), Lexis aplicáveis, Runbooks linkados, SLO linkado, Components dependentes.
- [ ] **11.** Criar `kata-component-create` (3 línguas) — scaffold:
  - (a) Cria `{repo}/docs/components/{name}.md` a partir do template em `codex-component-anatomy`.
  - (b) Atualiza `{repo}/docs/components/manifest.yaml` adicionando entrada.
  - (c) Abre PR no repo de produto.
- [ ] **12.** Criar `lex-feature-dor` (3 línguas) — HARD-GATE em duas camadas:
  - **Epic-level** (validado na criação do Epic pela triagem): Epic Issue MUST conter `Idea: docs/discovery/{topic}/ideas/{NNN}-{slug}.md`, `Component(s): {repo}/docs/components/{name}.md` (≥1), `Tier: 1|2|3|4` (max dos Components quando múltiplos).
  - **Child-level** (validado por Athena no Phase 1): Issue child (US/Bug/Tech-task) MUST conter `Tracked by #<EPIC>`. Atributos do Epic (Idea, Component, Tier) são herdados via Epic. Detalhamento da DoR de child fica em plan-038.
- [ ] **13.** Atualizar `lex-issue-driven` (3 línguas) — Phase 1 incorpora validação de `lex-feature-dor` antes de produzir `01-brief.md`. Falha = devolve issue ao autor com checklist de DoR pendente.
- [ ] **14.** Atualizar `kata-issue-analysis` (3 línguas) — incluir verificação dos campos `Idea:`, `Component:`, `Tier:` no body da issue. Flag de data: issues anteriores ao merge deste plano são exemptas (decisão 3).
- [ ] **15.** Criar `lex-delivery-readiness` (3 línguas) — HARD-GATE: feature tocando Component tier-1 ou tier-2 MUST ter (a) `{repo}/docs/slo/{component}.yaml` publicado, (b) `{repo}/docs/runbooks/{component}-{alert-name}.md` para os alertas relevantes, (c) Hestia tendo emitido report de readiness — antes do PR merge.
- [ ] **16.** Criar `kata-delivery-readiness` (3 línguas) — Hestia recebe handoff via `cry-delivery-handoff`, valida SLO, runbook, dashboards, alarms; emite report em `docs/issues/issue-{n}/07-delivery-readiness.md`. Pode bloquear merge.
- [ ] **17.** Criar `cry-delivery-handoff` (3 línguas) — `/cry-delivery-handoff <issue#>` invoca Hestia + `kata-delivery-readiness`.
- [ ] **18.** Atualizar `kata-quality-gate` (3 línguas) — adicionar Check 8: `lex-delivery-readiness` (skip se tier-3/4; bloqueante se tier-1/2).
- [ ] **19.** Atualizar `warrior-athena` (3 línguas) — Phase 8 pós-merge: invoca `cry-delivery-handoff` automaticamente quando feature toca Component tier-1/2. Persiste decisão em checkpoint para auditoria.
- [ ] **20.** Atualizar `warrior-hestia` (3 línguas) — Phase 0 explícita: receber handoff via `cry-delivery-handoff`; produzir readiness report; manter ownership pós-deploy. Linkar de volta à Idea de origem para rastreabilidade.
- [ ] **21.** Atualizar `warrior-phanes` (3 línguas) — output handoff: "Idea pronta para triagem via /cry-triage" (substitui menção a Prometheus).
- [ ] **22.** Atualizar `cry-ideation` (3 línguas) — mensagem final aponta para `cry-triage`.
- [ ] **23.** Atualizar `lex-discovery-flow` (3 línguas) — HARD-GATE 3: transição `promoted → triaged | rejected` exclusiva de `kata-triage-idea`; humano-only; agente não pode mudar status autonomamente.
- [ ] **24.** Atualizar `codex-discovery-artifacts` (3 línguas) — state machine completa com `triaged` e `delivered`; ramo `rejected` documentado.
- [ ] **25.** Atualizar `framework/platforms.yaml` com entradas para os 6 novos Lexis/Codex (`lex-platforms-rules`).
- [ ] **26.** Sync local: `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor`.
- [ ] **27.** Auto-revisão de cada artefato com `kata-artifact-self-review`.
- [ ] **28.** Smoke test conceitual: percorrer cadeia ponta-a-ponta com Idea fictícia (Insight existente → Idea → Triagem com score → Component novo → Issue → Athena DoR → PR → Quality Gate Check 8 → Delivery handoff). Documentar em `docs/issues/issue-<N>/smoke-test.md`.
- [ ] **29.** Commits atômicos (`lex-small-commits`, `lex-conventional-commits`, `lex-commit-language`, `lex-signed-commits`):
  - `feat(discovery): add lex-triage-required, codex-triage-scoring, kata-triage-idea, cry-triage`
  - `feat(discovery): add warrior-themis for triage preparation`
  - `feat(process): add lex-component-as-source-of-truth, codex-component-anatomy, kata-component-create`
  - `feat(workflow): add lex-feature-dor enforcing Idea+Component DoR before Athena`
  - `feat(sre): add lex-delivery-readiness, kata-delivery-readiness, cry-delivery-handoff`
  - `docs(discovery): update lex-discovery-flow, codex-discovery-artifacts state machine`
  - `docs(workflow): update lex-issue-driven, kata-issue-analysis, kata-quality-gate for new gates`
  - `docs(agents): update warrior-athena, warrior-hestia, warrior-phanes, cry-ideation handoffs`
  - `chore(framework): register new Lexis/Codex in platforms.yaml`
  - `chore(claude): regenerate .claude/ and .cursor/ via install.py --self`
- [ ] **30.** Abrir PR (`kata-contributing-pr`, `lex-pr-quality`): mirror labels, size label, assignee `@me`, reviewer via CODEOWNERS, body com `Closes #<N>`.
- [ ] **31.** Após merge: marcar plano `status: done`, mover para `archived/`, remover worktree.

## Dependencies

- **Plans 011–014** (Component-aligned warrior topology): definem Component fisicamente no repo de produto. Este plano (037) governa a **metodologia** de Component como source of truth. Se 011–014 estiverem `pending` no merge de 037, este plano usa `codex-component-anatomy` próprio (mínimo); 011–014 podem depois estender ou absorver. ADR documenta convivência.
- **Plan-027** (warrior-janus release orchestrator): este plano não cria Janus, mas `cry-delivery-handoff` (Step 17) abre o gancho para Janus orquestrar release tagging quando 027 for executado.
- **Plans 030, 032** (analytics, APM): observabilidade reforça `lex-delivery-readiness`; não-bloqueantes.
- **Plan-038** (PM topology per Component): follow-up direto deste plano. plan-037 estabelece o Epic como output da triagem; plan-038 decompõe Epic em US/Bug/Tech-task e cria as PMs por Component (Calliope decompositor, Aglaea UI, Eos Jobs, Metis Agents via plan-032, Prometheus narrowizado para API).

## Risks

| Risco | Mitigação |
|-------|-----------|
| Triagem humana vira gargalo (PO/PM/CEO sobrecarregados) | warrior-themis (decisão 1 Opção B) prepara material; humano só decide. AI cobre 80% da coleta. |
| Issues legacy sem Idea/Component bloqueiam fluxo após merge | `lex-feature-dor` não retroage (decisão 3). Flag de data em `kata-issue-analysis` exempta issues anteriores. |
| Component em repo de produto cria fricção (PR no repo certo) | `kata-component-create` automatiza scaffold + manifest. Sem trabalho manual. |
| Plans 011–014 (`codex-component-architecture`) divergirem de `codex-component-anatomy` deste plano | `codex-component-anatomy` é mínimo (metadata + tier + contratos + owner). 011–014 estendem; não substituem. ADR documenta convivência. |
| Score de triagem fica subjetivo demais (especialmente Esforço) | `codex-triage-scoring` lista exemplos canônicos por nível 1–5. Revisão trimestral dos exemplos. warrior-themis sugere score inicial baseado em histórico para ancorar a decisão. |
| Hestia recebe muito handoff e fica gargalo | `lex-delivery-readiness` aplica só a tier-1/2. Tier-3/4 são best-effort, sem gate. |
| Cadeia inteira fica complexa demais para humano lembrar | Diagrama canônico em `codex-feature-lifecycle` opcional para v2. v1 deste plano confia no fluxo via cries (`/cry-triage`, `/cry-implement-issue`, `/cry-delivery-handoff`). |
| Re-triagem de Idea com contexto novo cria conflito com score original | `triage_history` no front-matter da Idea preserva versões anteriores (decisão 5). Score atual prevalece. |
| Fórmula nova rejeitada pelo Notion (diferente da atual) | Antes do merge, atualizar a fórmula no banco do Notion. Codificar a transição em `codex-triage-scoring` com nota explicativa. |

## Critérios de aceitação

- [ ] AC-1: `/cry-triage <idea-ref>` aceita Idea com status `promoted`, calcula score com fórmula `(0.4×VC + 0.6×IN) × (6−E)/5 × 20`, exige decisão humana, persiste status `triaged | rejected`.
- [ ] AC-2: Score range produz exatamente 4–100; (5,5,1) → 100; (1,1,5) → 4; (3,3,3) → 36.
- [ ] AC-3: Issue de feature aberta sem `Idea:` e `Component:` no body é rejeitada por `lex-feature-dor` em `kata-issue-analysis` com checklist do que falta.
- [ ] AC-4: `kata-component-create` cria `docs/components/{name}.md` no repo de produto e atualiza `manifest.yaml`.
- [ ] AC-5: PR que toca Component tier-1 sem `docs/slo/{component}.yaml` publicado é bloqueada por Check 8 do `kata-quality-gate`.
- [ ] AC-6: PR merge de feature tier-1/2 dispara automaticamente `/cry-delivery-handoff` (warrior-athena Phase 8).
- [ ] AC-7: Hestia produz `docs/issues/issue-<N>/07-delivery-readiness.md` antes do deploy, com SLO/runbook/dashboards validados.
- [ ] AC-8: `cry-ideation` encerra com mensagem "Idea pronta para triagem via /cry-triage" — não menciona Prometheus.
- [ ] AC-9: `lex-discovery-flow` tem HARD-GATE 3 explícito; `codex-discovery-artifacts` tem state machine atualizada.
- [ ] AC-10: `framework/platforms.yaml` tem entradas para os 6 novos Lexis/Codex.
- [ ] AC-11: Todos artefatos existem em pt-BR, es, en (`lex-framework-language`).
- [ ] AC-12: `kata-artifact-self-review` aplicado a cada artefato novo passa sem findings 🔴.
- [ ] AC-13: Smoke test conceitual ponta-a-ponta documentado, mostrando uma feature fictícia atravessando todo o fluxo (Insight → Delivered).
