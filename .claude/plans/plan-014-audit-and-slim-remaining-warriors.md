---
plan_id: "014"
title: "audit-and-slim-remaining-warriors"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:00:00Z"
updated_at: "2026-05-07T22:00:00Z"
---

# Plano: Audit e enxugamento dos warriors remanescentes (Hephaestus, Iris, Atlas e demais)

## Objetivo

Aplicar a mesma disciplina do plan-013 (componentização) aos demais warriors do framework — Hephaestus (frontend), Iris (mobile), Atlas (deployment), Daedalus, Kronos, Theseus, Prometheus, Hera, Hestia, Demeter, Athena, e os de tradução/discovery. Para cada um: medir footprint, identificar inflação, decidir entre `manter` / `enxugar in-place` / `split em especialistas`. Implementar apenas as decisões `enxugar` e `split`. Plan **deliberadamente cauteloso**: split é exceção, não regra.

## Contexto

### Lições aprendidas no plan-013 (Apollo)

- Split só compensa quando o warrior carrega **stacks de dependências mutuamente exclusivas** que correspondem a **components separados** com `pyproject.toml`/`package.json` próprios.
- Split sem essa propriedade é inflação reversa (ganha 3 warriors, mas cada um precisa carregar quase tudo do original).
- Lazy-load via `paths:` em `platforms.yaml` resolve a maioria dos casos sem precisar de split.
- Token budget alvo (< 80 linhas) é métrica útil, mas não absoluta — alguns warriors legítimos passam disso (Athena tem 189 linhas de protocolo, irredutível sem perder semântica).

### Critérios de decisão por warrior (audit checklist)

Para cada warrior, aplicar o seguinte filtro em ordem:

1. **O warrior cobre múltiplos components do `bounded-context-template`?** → candidato a split (caminho Apollo)
2. **O warrior tem > 130 linhas e cobre uma única surface coesa?** → candidato a enxugamento in-place (extrair para codex referenciado, manter warrior < 100 linhas)
3. **O warrior tem ≤ 130 linhas e descreve uma única surface coesa?** → manter como está
4. **O warrior tem responsabilidades duplicadas com outro warrior?** → candidato a fusão ou clarificação de fronteira (não split)

### Diagnóstico inicial (a refinar no audit step 5)

| Warrior | Linhas | Cobre múltiplos components? | Surface | Decisão tentativa |
|---|--:|---|---|---|
| `warrior-hephaestus` (frontend) | 132 | Hoje só `ui/` (widget library). Web app ainda não é component separado | Web UI | **Manter** — surface coesa. Reavaliar quando bounded-context-template tiver `web-app/` separado de `ui/` (widget lib) |
| `warrior-iris` (mobile) | 146 | Mobile (iOS+Android), parity obrigatório | iOS+Android | **Manter** — `lex-mobile-platform-parity` exige uma persona única que pensa em ambos |
| `warrior-atlas` (devops/cloud) | 170 | `deployment/` (CDK) + arquitetura geral AWS | AWS architecture + IaC | **Enxugar** — extrair "review de IaC existente" para `kata-aws-review` (já existe; verificar se Atlas pode reduzir overlap); manter Atlas como arquiteto. Alvo < 130 linhas |
| `warrior-daedalus` (api design) | 138 | Não — designer de contrato | OAS spec | **Manter** — designer puro |
| `warrior-kronos` (event storming) | 156 | Não — designer de domínio | CloudEvents docs | **Enxugar** — possível extração para `kata-event-storm` + `kata-events-doc` (já existem). Alvo < 130 linhas |
| `warrior-theseus` (DDD) | 142 | Não — designer de domínio | Domain model | **Manter** — surface coesa |
| `warrior-prometheus` (orquestrador de design) | 172 | Coordena Theseus + Daedalus + Kronos | Orquestração | **Manter como está** ou **enxugar** se a coordenação puder ser mais declarativa. Alvo < 130 linhas |
| `warrior-hera` (QA / test strategy) | 133 | Não — estratégia de testes cross-stack | Test strategy | **Manter** |
| `warrior-hestia` (SRE) | 135 | Não — SRE/on-call | Runtime ops | **Manter** |
| `warrior-demeter` (data) | 150 | DB schema + retention + migrations | Data architecture | **Manter** ou **enxugar leve** se houver overlap com Atlas em IaC de RDS |
| `warrior-athena` (issue-driven orchestrator) | 189 | É **o orquestrador** de todo o fluxo issue-driven | Cross-cutting orchestration | **Manter** — protocolo grande é intrínseco. Não cortar |
| `warrior-translator` (i18n) | ~? | Não — tradutor | Translation | **Manter** |
| `warrior-pitia` (discovery) | ~? | Não — discovery | Discovery | **Manter** |
| `warrior-phanes` (ideation) | ~? | Não — ideation | Ideation | **Manter** |

Esse diagnóstico vira o input do step 5 (audit formal) — onde os números reais e overlaps são confirmados.

### Decisões fechadas (assumidas — sujeitas a override no Gate 1)

| Decisão | Valor | Por quê |
|---|---|---|
| Esperar plan-013 mergeado antes de começar | Sim | Lições aprendidas; consistência da abordagem; medição de baseline disponível |
| Auditar **todos** os warriors antes de modificar **algum** | Sim | Evita decisão isolada que cria inconsistência |
| Splits adicionais permitidos | Apenas se critério (1) bate (múltiplos components) | Critério rígido para evitar bikeshedding |
| Enxugamento in-place | Caminho preferido para warriors > 130 linhas em surface coesa | Ganho real, baixo risco |
| Tradução em 3 idiomas | Mantida sempre | `lex-framework-language` |
| PRs separados por warrior modificado | Sim, **stacked** quando possível (plan-004/005 viabiliza) | Reviews independentes, rollback seletivo |

## Escopo

### Fase 1 — Audit (step 5)

Produz `docs/internal/warrior-audit-2026.md` (apenas pt-BR, doc interno) com:

- Por warrior: linhas, Lexis listadas, Codex listados, Katas listados, dependências entre warriors (quem delega para quem), surface coberta
- Tabela "decisão por warrior" preenchida com `manter` / `enxugar` / `split`
- Token footprint medido por sessão simulada para os 3-5 warriors mais usados
- Lista de overlaps (e.g., Atlas vs Demeter em IaC de DB; Kronos vs Theseus em domain modeling) com proposta de fronteira clara

### Fase 2 — Implementação (steps 6-N)

Apenas para warriors com decisão `enxugar` ou `split`. Cada warrior tocado vira um sub-PR:

| Sub-PR (potencial — confirmar no audit) | Escopo | Idiomas |
|---|---|---|
| `enxugar Atlas` | Reduzir Atlas para `< 130 linhas`, redirecionando "review" para `kata-aws-review`; clarificar fronteira com Demeter | 3 |
| `enxugar Kronos` | Reduzir Kronos para `< 130 linhas`, redirecionando passos de modelagem para katas existentes | 3 |
| `enxugar Prometheus` | Reduzir Prometheus para `< 130 linhas`, transformando coordenação em pointer para warriors+katas | 3 |
| `clarificar fronteira Atlas vs Demeter` | Atualizar ambas descrições para eliminar overlap em decisões de RDS/DynamoDB | 3 |
| `clarificar fronteira Kronos vs Theseus` | Atualizar ambas para eliminar overlap em modelagem (Theseus = aggregate/entity; Kronos = events/lifecycle) | 3 |
| `splits adicionais` | **Provavelmente nenhum** — se algum surgir, vira sub-PR próprio com mesma estrutura do plan-013 | 3 cada |

### Fase 3 — Validação cruzada (steps finais)

- Smoke test de cada warrior modificado (`kata-artifact-self-review` + sessão simulada)
- Re-medição do token footprint comparando com baseline do plan-011/013
- Atualização do `docs/internal/warrior-topology-2026.md` (criado no plan-011) com a topologia final

### Atualizações em artefatos existentes (3 idiomas, conforme decisão por warrior)

| Arquivo | Mudança potencial |
|---|---|
| Cada warrior auditado com decisão `enxugar` ou `split` | Reescrita ou criação de novos especialistas (raro) |
| `framework/platforms.yaml` | Atualizar entries dos warriors modificados; adicionar entries de novos warriors caso splits surjam |
| `docs/internal/warrior-topology-2026.md` | Atualização final (versão pós-implementação) |
| **Sem alteração esperada em:** Lexis, Codex (excepto referências), katas (excepto referências), cries, `.directives.sample` | — |

## Fora de escopo

- **Apollo (já tratado em plan-013).** Este plan ignora o trio `apollo-api/jobs/agents`.
- **Criar novas Lexis** ou novos Codex — todos os enxugamentos referenciam artefatos existentes.
- **Refactor da estrutura `framework/{lang}/<clade>/<subclade>/<pilar>/`** — taxonomia preservada.
- **Mudança em Athena, no fluxo issue-driven, em katas de quality gate** — fluxo permanece.
- **Audit de katas e cries** — fora de escopo (este plan é sobre warriors). Caso o audit detecte kata/cry inflado, abre-se issue separada.
- **Audit do `warrior-translator` quanto a qualidade da tradução** — só footprint/responsabilidade, não qualidade do output.

## Steps

- [ ] 1. **Confirmar plan-013 mergeado** — Apollo split é a fundação. Sem ele, não rodar este plan
- [ ] 2. Abrir issue com template `epic`, Issue Type `Epic`, label `epic`, título "epic: audit and slim remaining warriors aligned with bounded-context-template"
- [ ] 3. Criar branch `chore/{N}-warrior-audit` e worktree (esta branch é só para o audit doc; sub-PRs ganham branches próprias)
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. **Audit:** redigir `docs/internal/warrior-audit-2026.md` (pt-BR-only) com a tabela completa de decisão por warrior; medir footprint de pelo menos 3 warriors em sessão simulada; identificar overlaps; submeter para Gate 1 com o usuário
- [ ] 6. **Gate 1:** apresentar audit doc → usuário aprova/altera decisões por warrior. Travar tabela
- [ ] 7. Para cada warrior com decisão `enxugar`: abrir sub-issue (template `simple-task`, Issue Type `Task`, label `evolvability ♻️`), criar branch `chore/{M}-slim-warrior-{name}`, executar enxugamento em pt-BR, traduzir es+en, atualizar `platforms.yaml` se descrição mudar, abrir PR via `kata-contributing-pr` referenciando este plan-014 e a sub-issue
- [ ] 8. Para cada par com `clarificar fronteira`: abrir sub-issue, criar branch, atualizar os dois warriors envolvidos para que cada um declare explicitamente o que **não faz** e cite o outro warrior, traduzir, abrir PR
- [ ] 9. Caso o audit produza decisão `split` para algum warrior: abrir sub-plan dedicado (`plan-{NNN}-split-{name}`) seguindo o padrão do plan-013 (este plan-014 não executa o split inline — o split exige sua própria fundação codex e merece tratamento de primeira classe)
- [ ] 10. Após cada sub-PR mergeado: re-medir footprint do warrior tocado; registrar resultado em `docs/internal/warrior-topology-2026.md`
- [ ] 11. **Validação cruzada final:** após todos os sub-PRs mergeados, rodar `kata-artifact-self-review` em todos os warriors modificados; rodar uma sessão simulada por warrior; verificar que delegações/fronteiras seguem coerentes
- [ ] 12. Atualizar `docs/internal/warrior-topology-2026.md` com a topologia final pós plan-014; commit final no branch principal deste plan
- [ ] 13. PR principal deste plan-014 (após sub-PRs todos mergeados): contém apenas o doc interno final atualizado e o registro do epic resolvido
- [ ] 14. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-013 mergeado** — fundação (Apollo split + lições aprendidas + métricas baseline) (bloqueante)
- **Plan-011 e plan-012 mergeados** — implícitos via dependência de plan-013
- Plan-007 (token cost stamp) **opcional** mas útil para medições do step 5
- `templates/warrior-sample.md` presente
- `bounded-context-template` PR #1 mergeado

## Riscos

- **Tendência a fazer split desnecessário** ("já dividi Apollo, vou dividir todos"). Mitigação: critério (1) rígido — só split se cobre múltiplos components; demais warriors ficam com `manter` ou `enxugar` por default.
- **Audit gera análise paralela longa** sem entregar implementação. Mitigação: timebox de 5 dias úteis para o step 5; se algum warrior não couber, registrar e seguir.
- **Sub-PRs paralelos geram conflito em `platforms.yaml`.** Mitigação: cada sub-PR só toca a entry do warrior dele; conflitos restritos a ordem das chaves YAML — resolução trivial.
- **Enxugamento perde nuance valiosa do warrior.** Mitigação: `kata-artifact-self-review` step 11; revisão humana antes de mergear; preservação obrigatória de Identity/Mission/Persona; cortes só em "Responsibilities/Does/Does Not" via redirect para katas/codex existentes.
- **Overlaps detectados (Atlas vs Demeter, Kronos vs Theseus) revelam ambiguidade não resolvida no framework.** Mitigação: clarificação de fronteira é caminho preferido; se ambiguidade for de fato profunda, abre-se ADR sob `docs/adr/` em sub-PR dedicado.
- **Hephaestus precisar split** quando bounded-context-template ganhar `web-app/`. Mitigação: este plan não toca Hephaestus; quando o template evoluir, abre-se plan próprio (provável `plan-{NNN}-split-hephaestus-widget-vs-app`).
- **Iris precisar split** se um dia parity for relaxada. Mitigação: idem — abre plan próprio quando o critério for atendido.
- **Athena ficar acima de 130 linhas para sempre.** Aceito. Athena é orquestrador cross-cutting; protocolo é intrínseco; documentado no audit como "exceção justificada".

## Verificação

1. `docs/internal/warrior-audit-2026.md` existe e tem decisão por warrior aprovada pelo usuário (Gate 1 marcado `[x]`)
2. Cada warrior com decisão `enxugar` foi mergeado em sub-PR próprio, com 3 idiomas, < 130 linhas (ou exceção registrada)
3. Cada par com decisão `clarificar fronteira` teve seus dois warriors atualizados em sub-PR
4. Nenhum split foi feito inline neste plan; splits eventuais viraram sub-plans dedicados
5. Footprint medido após enxugamento mostra redução em pelo menos 3 warriors auditados
6. `docs/internal/warrior-topology-2026.md` está atualizado com a topologia pós plan-014
7. **Sem nova Lexis, novo Codex, novo Kata ou novo Cry** criados neste plan (verificação contra inflação)
8. **Sem alteração** em Athena, lex-issue-driven, kata-quality-gate, lex-pr-quality, framework/.directives.sample
9. Cada sub-PR carrega stamp de custo (se plan-007 mergeado) e referencia o epic deste plan-014
10. PR final consolidador deste plan registra "plan-014 done"; epic fechado com `Closes #{N}` resolvendo todas as sub-issues
