---
plan_id: "046"
title: "issue-as-plan-and-issues-folder"
status: todo
agent: claude
issue: "guardiatechnology/ahrena#TBD"
created_at: "2026-05-11T00:00:00Z"
updated_at: "2026-05-11T00:00:00Z"
---

# Plan: Issue-as-plan + `.issues/` folder + `.plans/` como working memory da IA

## Objective

Refatorar a camada de armazenamento do plano introduzida por **plan-043** para que o conteúdo do plano não seja mais um arquivo markdown committed em `.claude/plans/`, mas viva em três camadas com papéis claros:

1. **GitHub Issue body** (canonical) — resumo + plano (Steps, Risks, Dependencies). Editado via `gh issue edit --body-file` sem commit git. Audit log canônico via GitHub.
2. **`.plans/{N}.md`** (gitignored, AI working memory) — cache local + scratch livre. Edit direto pela IA, zero cerimônia de commit. Materializado a partir do Issue body via `kata-load-plan-from-issue` no início da sessão; flushed de volta via `kata-flush-plan-to-issue` em transições significativas.
3. **`.issues/{N}/`** (committed, na raiz do repo) — artefatos profundos das Phases do fluxo Issue-Driven (`01-brief.md`, `02-requirements.md`, `03-architecture.md`, `05-security-review.md`, `06-quality-report.md`). Movido de `docs/issues/issue-{N}/` (que era posição errada — `docs/` é produto, não operacional).

Constrói por cima de plan-043, **não substitui**. Tudo que plan-043 entregou continua válido: 7-status enum, owners por transição (Eunomia/Athena/Argos/Janus), 7 labels canônicas com mutex, notifications provider-agnósticas, session tracking, loop 3×15min, sub-ciclo Argos. O que muda é só o **meio de armazenamento** do plano.

Padrão inspirado em https://github.com/guardiatechnology/documents-context/tree/main/docs/issues/issue-3 — Victor já produz `01-brief.md` ... `06-quality-report.md` em `docs/issues/issue-{N}/`. Plan-046 oficializa a posição (`.issues/`), o nome canônico (Issue number, sem prefix `issue-`), e elimina o arquivo de plano separado.

## Scope

### Framework (3 línguas — pt-BR, es, en)

*Storage layer (plano = Issue body + `.plans/` cache + `.issues/` deep artifacts):*

- `framework/{lang}/_foundation/process/lexis/lex-agent-planning.md` — reescrita: "Plano = body da Issue + `.plans/{N}.md` cache local + `.issues/{N}/` deep artifacts". HARD-GATE passo (e) muda de "front-matter do plano atualizado com issue, branch, worktree" para "body da Issue preenchido com plano canônico". Remove campos de front-matter `status:`, `claude_session`, `session_entrypoint` (deixam de existir; label na Issue/PR é a única fonte de truth).
- `framework/{lang}/_foundation/process/codex/codex-agent-planning.md` — reescrita do manual operacional para o modelo de 3 camadas. Novo fluxo: load → edit → flush. Documentar `gh issue edit --body-file`. Atualizar exemplos.
- `framework/{lang}/engineering/workflow/lexis/lex-issue-driven.md` — path move `docs/issues/issue-{N}/` → `.issues/{N}/` em todas as referências.
- `framework/{lang}/engineering/workflow/codex/codex-issue-workflow.md` — espelha a mudança de path.

*Katas (3 línguas):*

- `framework/{lang}/_foundation/process/katas/kata-plan-task.md` — reescrita: não cria arquivo em `.plans/`; preenche body da Issue via `gh issue edit --body-file`. Os 5 passos canônicos do HARD-GATE permanecem (1–4 idênticos; passo 5 troca para "preencher Issue body").
- **NOVO** `framework/{lang}/_foundation/process/katas/kata-load-plan-from-issue.md` — procedimento que materializa `.plans/{N}.md` a partir do body da Issue via `gh issue view {N} --json body --jq .body > .plans/{N}.md`. Idempotente. Roda no início de cada sessão e em handoffs.
- **NOVO** `framework/{lang}/_foundation/process/katas/kata-flush-plan-to-issue.md` — procedimento inverso: lê `.plans/{N}.md` e atualiza Issue body via `gh issue edit {N} --body-file .plans/{N}.md`. Idempotente. Invocado em transições de `status:`, em handoffs, e no fim da sessão.
- `framework/{lang}/engineering/workflow/katas/kata-pr-prepare.md` — Passo 6b mantém sync de label PR+Issue (per `lex-issue-status` mutex), remove "atualizar front-matter do plano". Session Trace (Passo 5b) continua intacto. Adiciona chamada a `kata-flush-plan-to-issue` antes de abrir o PR.

*Warriors (3 línguas):*

- `framework/{lang}/engineering/workflow/warriors/warrior-athena.md` — substituir todas as menções a "atualizar status: no front-matter do plano" por "atualizar body da Issue + label". Bullets das transições mantidos; tabela de Lexis inclui `lex-issue-driven` atualizado. Adiciona `kata-load-plan-from-issue` e `kata-flush-plan-to-issue` na tabela de katas. Phase 1 passa a invocar `kata-load-plan-from-issue` antes de qualquer ação.
- `framework/{lang}/engineering/quality/warriors/warrior-argos.md` — idem (load no início do sub-ciclo, flush no fim).
- `framework/{lang}/engineering/workflow/warriors/warrior-eunomia.md` — **(co-criado por plan-046)**: reescrever plan-044 para o novo modelo desde o dia 1. Eunomia cria Issue + branch + worktree + preenche Issue body (sem arquivo em `.plans/`). Plan-044 fica subordinado a plan-046 — se 046 ship antes (recomendado), 044 nasce limpo.

*Repo Ahrena (artefatos diretos):*

- `.gitignore` — adicionar `.plans/`.
- `.gitignore.sample` (framework) — adicionar `.plans/` no boilerplate distribuído pelo install para projetos consumidores.
- `framework/platforms.yaml` — entries para as 2 novas katas e os artefatos atualizados.
- `framework/.directives.sample` — opcionalmente declarar `plans.local_cache: ".plans"` se quiser path configurável (default fica fixo).

### Migration

- **Arquivos de plano legados** (`.claude/plans/*.md`) — não migrar conteúdo; o histórico vive nos Issues fechados que já existem (ou no PR de plan-043 que migrou os `status:`). Opções:
  - (a) **Deletar `.claude/plans/`** com README apontando "histórico em Issues fechadas e archived/" — mais limpo.
  - (b) **Mover `.claude/plans/archived/`** para `.issues/_legacy/` mantendo como histórico imutável — preserva audit.
  - **Recomendado:** (b) com tag explícita "este diretório é histórico anterior a plan-046 — novos planos vivem em Issues".
- **`docs/issues/issue-{N}/` legados** (Phase artifacts já produzidos) — `git mv docs/issues/ .issues/` em cada repo consumidor; preserva history. Renomear arquivos de `docs/issues/issue-3/` para `.issues/3/`.
- **Plan-046 e plan-044/045 dentro deste PR/follow-up** — eles próprios serão os primeiros do modelo novo: criar Issues correspondentes, preencher body, deletar os arquivos `plan-04x.md` em `.claude/plans/`.

## Steps

- [ ] **Step 1 — Issue + branch + worktree** per `lex-agent-planning` HARD-GATE (5 passos). Eunomia ainda não shipada nesta data → agente da sessão como fallback.
- [ ] **Step 2 — ADR-002** registrando a decisão de migrar para o modelo de 3 camadas. Cobre: (a) razão de tirar plano de `.claude/plans/`, (b) por que `.plans/` é gitignored mas `.issues/` é committed, (c) por que Issue body é canonical em vez de arquivo, (d) cadência de load/flush, (e) compatibilidade com plan-043.
- [ ] **Step 3 — Reescrever `lex-agent-planning` (3 línguas).** HARD-GATE passo (e) atualizado; front-matter do plano simplificado (sem status:, sem session keys — ou plano vira só arquivo de scratch); novo template do body da Issue (Summary + Plan section com Steps/Risks/Deps).
- [ ] **Step 4 — Reescrever `codex-agent-planning` (3 línguas).** Manual operacional do 3-layer model. Fluxo load → edit → flush. Examples. Conventional location de `.plans/` e `.issues/`.
- [ ] **Step 5 — Path move `docs/issues/issue-{N}/` → `.issues/{N}/`.** Atualizar `lex-issue-driven` + `codex-issue-workflow` (3 línguas). Em repos consumidores (ex.: `documents-context`), `git mv docs/issues/ .issues/` preserva history. Adicionar nota de migration no codex.
- [ ] **Step 6 — Reescrever `kata-plan-task` (3 línguas).** Não cria arquivo; preenche body da Issue. Os 5 passos canônicos do HARD-GATE permanecem (passo 5 troca de file → Issue body).
- [ ] **Step 7 — Criar `kata-load-plan-from-issue` (3 línguas).** Procedimento idempotente: `gh issue view {N} --json body --jq .body > .plans/{N}.md`. Invocado no início de cada sessão de qualquer agente que opera no plano.
- [ ] **Step 8 — Criar `kata-flush-plan-to-issue` (3 línguas).** Inverso: `gh issue edit {N} --body-file .plans/{N}.md`. Invocado em cada transição de `status:`, em handoffs, e no fim da sessão.
- [ ] **Step 9 — Atualizar `kata-pr-prepare` (3 línguas).** Passo 6b mantém sync de label; remove "atualizar front-matter do plano"; adiciona chamada a `kata-flush-plan-to-issue` antes de `create_pull_request` (garante que Issue body reflete o estado final).
- [ ] **Step 10 — Reescrever plan-044 (Eunomia) para o modelo novo.** Eunomia em modo top-level: cria Issue + branch + worktree + Issue body (sem criar arquivo `.plans/{N}.md` — esse é gerado on-demand pelo primeiro `kata-load-plan-from-issue`). Eunomia em modo subtask: idem, cria sub-Issue com Tracked by + body preenchido.
- [ ] **Step 11 — Atualizar warriors Athena, Argos, Janus (3 línguas).** Substituir referências a "atualizar status: no front-matter do plano" por "atualizar body da Issue + label". Adicionar bullets sobre load/flush no fluxo de atuação.
- [ ] **Step 12 — `.gitignore` + `.gitignore.sample`.** Adicionar `.plans/` em ambos.
- [ ] **Step 13 — `framework/platforms.yaml`.** Entries para `kata-load-plan-from-issue` e `kata-flush-plan-to-issue` (mas katas não são listadas em platforms.yaml hoje — só Lex e Codex — então só atualizar entries de Lexis/Codex tocados).
- [ ] **Step 14 — Migration de `.claude/plans/archived/` para `.issues/_legacy/`.** `git mv` preserva history; README explica que esse diretório é congelado, novo trabalho vive em Issues.
- [ ] **Step 15 — Atualizar READMEs (3 línguas).** Seção "Workflow Status" reescrita pro 3-layer model. Explicar `gh issue edit` como UX padrão.
- [ ] **Step 16 — Sync `.claude/` + `.cursor/`** via `python3 scripts/install.py --self`.
- [ ] **Step 17 — Commit, push, PR.** Commits atômicos: (a) ADR-002, (b) Lexis/Codex (3 línguas), (c) Katas novas + atualizadas, (d) Warriors, (e) path moves + .gitignore, (f) plan-044 atualizada, (g) sync. PR contra main com `Closes #{N}`.
- [ ] **Step 18 — Self-host:** abrir Issue do plan-046, preencher body com este conteúdo, deletar este arquivo `.claude/plans/plan-046-*.md`. Plan-046 é o primeiro plano a viver no modelo novo.

## Dependencies

- **plan-043** — merge obrigatório antes. Plan-046 consome 7-status enum, owners, labels, notifications, sessions de 043. Conflitos de merge minimizados se sequencial.
- **plan-044** (Eunomia) — *absorvido* por plan-046 Step 10. Plan-044 standalone vira opcional ou cancelado.
- **plan-045** (Janus pointer) — inalterado. Janus opera em labels Issue/PR, não toca plano.
- **plan-038** (reduzido) — depende de plan-046. Calliope cria Issues; sob modelo novo, zero arquivo de plano envolvido.

## Risks

- **`.plans/` perdida em fresh clone.** Mitigado: `kata-load-plan-from-issue` na primeira invocação da sessão regenera o cache local a partir do body da Issue. Source of truth é o GitHub.
- **Flush conflitante entre sessões.** Se 2 sessões editam `.plans/{N}.md` simultaneamente, flush sobrescreve. Mitigação: `kata-flush-plan-to-issue` lê o body atual antes de gravar; se houve mudança remota desconhecida, alerta e oferece merge manual. Heartbeat de sessão (codex-session-tracking) já permite detectar sessões ativas concorrentes.
- **Histórico granular dos toggles perdido em git.** Sim. Em troca: audit log do GitHub Issue mostra cada edit no body com timestamp e autor. Para a maioria dos casos, suficiente.
- **Repos consumidores quebram com path move `docs/issues/` → `.issues/`.** Mitigação: migration documentada em `codex-issue-workflow` com `git mv`; ferramentas (kata-pull-issues futura, kata-quality-gate) precisam aceitar ambos caminhos durante transition window de 1 release ciclo.
- **Eunomia (plan-044) retrofit.** Se 044 ship antes de 046 (improvável), 046 retrofita o warrior. Mitigação: pedir que plan-044 não saia até 046 estar mergeada, OU absorver plan-044 inteira em plan-046 (Step 10).
- **`.plans/` polui pesquisa local.** `grep -r` agora ignora plano canônico (que está no GitHub). Mitigação: kata `kata-pull-issues` opcional que cacheia bodies de Issues ativas em `.plans/_index.md` para grep local.
- **Plan-046 ele mesmo é arquivo em `.claude/plans/` até Step 18.** Aceito como inconsistência transient — Step 18 fecha o ciclo.

## Open Questions

1. **Deletar `.claude/plans/archived/` ou mover para `.issues/_legacy/`?** Recomendação: mover. Preserva audit, sinaliza congelamento.
2. **`.issues/{N}/` numbering sem prefix `issue-`?** Recomendação: sim, `.issues/3/` (não `.issues/issue-3/`). O `.issues/` já implica.
3. **Cache local sync cadence (`kata-flush-plan-to-issue`):** sincronizar a cada toggle? a cada Step? a cada 5min? Recomendação: a cada transição de `status:` + a cada Step concluído + no fim da sessão. Toggles intermediários são scratch livre.
4. **Schema do `.plans/{N}.md`:** estritamente espelho do body da Issue, ou superset com "## Working notes" e "## Next actions" locais que não saem no flush?** Recomendação: superset, com marcadores `<!-- not-flushed -->` que `kata-flush-plan-to-issue` filtra.
5. **`gh issue edit` sem MCP**: se `mcp.servers` lista github MCP, o `gh` CLI ainda é OK? Recomendação: per `lex-mcp` regra 1, usar MCP `update_issue` quando disponível; `gh issue edit` é fallback CLI documentado.
6. **Eunomia em plan-046 vs plan-044 standalone:** absorver totalmente em 046 ou manter 044 separado? Recomendação: absorver em 046 — Eunomia nasce no modelo novo sem retrofit. Cancela plan-044 ou converte em "Eunomia subtask creator" focado só em decomposição de child Issues (sem o lado de plan-as-file).
7. **Janela de transição path move:** quanto tempo `docs/issues/` legado fica aceito antes do enforcement? Recomendação: 1 release após plan-046 mergear; depois Gate 2 falha se encontrar `docs/issues/`.

## Coordinação com plan-043

Plan-043 (PR #93) merges **antes** de plan-046. Plan-046 abre Issue própria, branch própria, worktree próprio per HARD-GATE de plan-043 (Eunomia/fallback). Plan-046 herda:

- Enum unificado de status — usado idêntico.
- Owners por transição — owners idênticos; só muda *o que* eles tocam (Issue body em vez de arquivo).
- 7 labels canônicas — inalteradas.
- `lex-issue-status` — inalterada.
- Notifications + Slack MCP — inalterados.
- `codex-session-tracking` + heartbeats — inalterados.

Plan-046 reescreve:

- `lex-agent-planning` — passo (e) do HARD-GATE + remoção de front-matter `status:`.
- `codex-agent-planning` — manual operacional.
- `kata-plan-task` — body da Issue como destino.
- `kata-pr-prepare` — Passo 6b sem update de front-matter.
- Plan-044 (Eunomia) — modelo novo desde o dia 1.

Plan-046 cria:

- `kata-load-plan-from-issue` + `kata-flush-plan-to-issue`.
- `.issues/{N}/` como diretório canônico de Phase artifacts.
- ADR-002.

## Notes for Eunomia (ou fallback) quando abrir Issue para plan-046

- Title sugerido: `feat: migrate plan storage to Issue-as-plan model (3-layer: Issue body + .plans/ cache + .issues/ artifacts)`
- Labels: `feature request ➕`, `evolvability ♻️`
- Issue Type: Feature
- Body deve referenciar plan-043 PR #93 como dependência (precedente merged).
- Apontar para este arquivo `.claude/plans/plan-046-issue-as-plan-and-issues-folder.md` como o rascunho original (Step 18 deleta esse arquivo).
