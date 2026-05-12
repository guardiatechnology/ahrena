---
plan_id: "045"
title: "warrior-janus-pointer-and-status-wiring"
status: todo
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-10T00:00:00Z"
updated_at: "2026-05-10T00:00:00Z"
---

# Plan: warrior-janus — wiring com ciclo de status e notificação (ponteiro para plan-027)

## Objective

Plan-045 é majoritariamente um **ponteiro para plan-027** (`warrior-janus-release-orchestrator`), que entrega Janus + `kata-release-prepare` + `kata-release-publish` + `cry-release` + `lex-annotated-tags` + workflow `validate-tag.yml`. Plan-045 não duplica o conteúdo de plan-027 — apenas garante que **plan-027 absorva 3 acréscimos pequenos antes do merge** para amarrar Janus ao ciclo de status definido em plan-043 (transições `to release → release → done`) e ao **MCP de notificação configurado em `.ahrena/.directives`** (`notifications.provider`) para anunciar a release no canal `notifications.channels.release_notify`.

Existem dois cenários:

- **Cenário A — plan-027 ainda não foi mergeado:** plan-045 funciona como **spec extension** para o PR de plan-027. Plan-027 vira o PR único que entrega Janus já wired ao ciclo de status; plan-045 fica como acta de coordenação (não tem PR próprio, ou tem PR só com o ADR + atualização do `lex-agent-planning` que cita Janus).
- **Cenário B — plan-027 já mergeado sem as extensões:** plan-045 vira um PR follow-up que adiciona E1/E2/E3 aos artefatos já mergeados de plan-027.

A decisão entre A/B se resolve quando o Step 1 deste plano roda (verifica status atual de plan-027).

## Scope

**Cenário A (plan-027 ainda não mergeado):**
- Coordenação: garantir que o PR de plan-027 inclua as 3 extensões E1/E2/E3 listadas em "Extensões obrigatórias a plan-027" abaixo.
- Atualizar `lex-agent-planning` (3 línguas) — tabela "Owner de cada transição" cita `warrior-janus` em `to release → release` e `release → done`. **Se plan-043 já cobre essa atualização**, plan-045 só verifica/valida.
- ADR opcional: registrar a decisão de fazer Janus owner único do release-side do ciclo (em vez de humano + Janus parcial).

**Cenário B (plan-027 já mergeado):**
- PR follow-up: adicionar E1/E2/E3 aos artefatos `kata-release-prepare`, `kata-release-publish` (3 línguas cada) sem refazer o resto de Janus.
- Sync `.claude/`/`.cursor/`.

**Não escopo (fica em plan-027):**
- Criação de `warrior-janus`, `kata-release-prepare`, `kata-release-publish`, `cry-release`, `lex-annotated-tags`, workflow `validate-tag.yml`. Tudo isso é plan-027.

**Não escopo (fica em plan-043):**
- Definição do enum de status, label `status: release`, label `status: done`, schema `notifications:` em `.directives`, `codex-notifications`, primeiro MCP de notificação (Slack como provider inicial: `framework/mcp/slack.json` + `codex-mcp-slack`).

## Extensões obrigatórias a plan-027 (E1/E2/E3)

Estes são os 3 acréscimos que plan-027 absorve para fechar o contrato com plan-043:

| # | Onde em plan-027 | Acréscimo |
|---|---|---|
| E1 | `kata-release-prepare` (Step 6/7 de plan-027) | Adicionar passo inicial de **descoberta da fila**: identificar PRs em `status: to release` via `gh pr list --label "status: to release" --state open --json number,title,headRefName,labels,baseRefName`. Se `cry-release` foi chamada sem argumento → escolher PR mais antigo da fila (FIFO). Se chamada com `[PR#]` → operar nesse específico. Falhar com mensagem clara se a label não existir (orienta a rodar bootstrap de labels de plan-043). |
| E2 | `kata-release-publish` (Step 8/9 de plan-027) | Adicionar **transições de label**:<br>- Ao iniciar publish: `gh issue edit / gh pr edit --remove-label "status: to release" --add-label "status: release"` em plano, Issue e PR.<br>- Ao concluir publish (após `validate-tag.yml` passar e Release ser criada/editada): idem para `release → done`.<br>- Se publish falhar: manter `status: release` (não regredir) e disparar alerta diferenciado via MCP de notificação (ver E3) sinalizando intervenção humana. **Sem retry automático** — release falha é evento raro e crítico. |
| E3 | `kata-release-publish` (Step 8/9 de plan-027) | Adicionar **notificação final** via **MCP de notificação configurado em `.ahrena/.directives`** (`notifications.provider`) no canal `notifications.channels.release_notify`. Janus invoca a abstração genérica do `codex-notifications` (plan-043 Step 6d), que mapeia o provider para a tool MCP correta. Payload (resolvido pelo codex para o formato do provider):<br>- Link da Release (`https://github.com/{owner}/{repo}/releases/tag/{tag}`).<br>- Versão (`{tag}`).<br>- Nº do PR (`#{N}`), nº da Issue (`#{M}`).<br>- Tipo de bump (`major\|minor\|patch`).<br>- Changelog resumido (primeiras N linhas ou bullets de `feat:`/`fix:`).<br>- Autor humano que aprovou o gate.<br>- Pré-requisito: MCP de notificação ativo per plan-043 Step 6. Fallback se MCP indisponível: Janus prossegue com release e loga warning; não bloqueia. **Texto do kata nunca menciona Slack/Discord/Teams diretamente** — só "MCP de notificação". |
| E4 | `kata-release-publish` (Step 8/9 de plan-027) | Adicionar **session trace na GitHub Release body** (em paralelo ao trace já obrigatório no PR body via plan-043 Step 7.4). Lê heartbeat files de `.ahrena/workflow/sessions/*.json` filtrados pelo branch do PR mergeado + heartbeat do próprio Janus, monta seção "Session Trace" no fim do body da Release (após o changelog auto-gerado ou customizado). Persistência canônica: PR body já tem o trace ao abrir; Release body herda + adiciona a sessão de Janus que executou o publish. Quando preserva auto-Release (caminho default per plan-027 lição da v0.11.0), Janus invoca `gh release edit --notes` somente para anexar a Session Trace ao final, sem reescrever o auto-gerado. |

## Steps

- [ ] **Step 1 — Determinar cenário (A ou B).** Verificar status atual de plan-027:
  - Rodar `ls .claude/plans/archived/ | grep plan-027` para ver se já foi arquivado.
  - Rodar `gh pr list --search "plan-027" --state all` para checar PR.
  - Se plan-027 está em `.claude/plans/pending/` e sem PR aberto → **Cenário A**.
  - Se plan-027 já mergeou → **Cenário B**.
  - Documentar a decisão neste plano (atualizar Scope: marcar qual cenário vale).

- [ ] **Step 2 (Cenário A) — Garantir absorção de E1/E2/E3 no PR de plan-027.**
  - Abrir Issue + branch + worktree per `lex-issue-first`/`lex-git-branches`/`lex-git-worktrees` (usando Eunomia se já shipada por plan-044, senão manualmente).
  - Atualizar plan-027 incorporando E1/E2/E3 nos seus Steps existentes.
  - Coordenar com quem está executando plan-027: garantir que o PR já inclui as extensões antes do merge.
  - Se houver lacuna de timing (plan-027 vai mergear antes da Eunomia ou do MCP de notificação existirem), documentar no PR de plan-027 que as extensões usarão fallback (log + gh CLI puro até MCP de notificação ativar).
  - **NÃO criar PR separado para plan-045 neste cenário** — plan-045 fica apenas como acta de coordenação.

- [ ] **Step 3 (Cenário B) — Abrir PR follow-up.**
  - Abrir Issue + branch + worktree.
  - Editar `kata-release-prepare` (3 línguas) para incorporar E1.
  - Editar `kata-release-publish` (3 línguas) para incorporar E2 + E3.
  - Sync `.claude/`/`.cursor/` via `install.py --self`.
  - Smoke test: rodar `/cry-release` num PR de teste com label `status: to release` → confirmar que Janus consome a fila + aplica transições + publica notificação via MCP no canal `notifications.channels.release_notify`.
  - Commits atômicos:
    - `feat(release): janus consumes status:to-release queue (E1)`
    - `feat(release): janus updates status labels on publish (E2)`
    - `feat(release): janus notifies #notifications-gh-releases on success (E3)`
    - `chore(claude): regenerate .claude/ and .cursor/ via install.py --self`
  - Abrir PR per `kata-contributing-pr` + `lex-pr-quality`.

- [ ] **Step 4 — Validar wiring de Janus com plan-043 e plan-044.**
  - Confirmar que `lex-agent-planning` (atualizado em plan-043) cita `warrior-janus` na tabela de owners das transições `to release → release` e `release → done`. Se ausente, adicionar.
  - Confirmar que Eunomia (plan-044) cria planos com `status: todo`, Athena (plan-043) move até `to release`, Janus (plan-027+045) fecha em `done` — ciclo completo end-to-end.

- [ ] **Step 5 — Atualizar plan-027 cross-link.** Adicionar referência a plan-043 (status workflow) e plan-045 (este plano) nas seções "Contexto" e "Dependências" de plan-027. Se Cenário B, fazer isso no mesmo PR follow-up.

## Dependencies

- **plan-027** — `warrior-janus-release-orchestrator` (pending). Plan-045 é **pointer/extension** dele. Sem plan-027 não há Janus para amarrar.
- **plan-043** — `workflow-status-and-review-loop`. Define os labels `status: to release`, `status: release`, `status: done` que Janus aplica/lê, o schema `notifications:` em `.directives`, o `codex-notifications`, e o primeiro MCP provider (Slack inicial) que Janus consome via abstração genérica.
- **plan-044** — `warrior-eunomia-plan-and-subtask-creator`. Não bloqueante para 045, mas conceitualmente alinhado (Eunomia abre o ciclo; Janus fecha).

## Risks

- **Confusão de ownership** — quem é dono das E1/E2/E3, plan-027 ou plan-045? Mitigação: este plano deixa explícito que **o conteúdo é de plan-027** (artefatos `kata-release-prepare` + `kata-release-publish` vivem lá); plan-045 só **rastreia** a obrigação de absorvê-las. PR único em Cenário A; PR follow-up em Cenário B.
- **Plan-027 e plan-045 ambos abrem PR separado em Cenário A** (duplicidade). Mitigação: Step 2 explicita que plan-045 NÃO cria PR no Cenário A — fica como acta. Só Cenário B tem PR próprio.
- **MCP de notificação indisponível na hora do release.** Mitigação: E3 explicita fallback (warning + prosseguir). Release acontece; notificação é nice-to-have, não bloqueio. Independe de qual provider está configurado (Slack hoje; Discord/Teams amanhã).
- **`gh pr list --label "status: to release"` retorna múltiplos PRs.** Mitigação: FIFO por data de criação (mais antigo primeiro). Documentado em E1.

## Open Questions

1. **Cenário A ou B?** Resolvido pelo Step 1.
2. **Em Cenário A, plan-045 tem Issue própria?** Recomendação: sim (per `lex-issue-first`), mesmo sem PR — Issue documenta a obrigação de E1/E2/E3 e fecha quando plan-027 mergeie com as extensões. Alternativa: usar a Issue de plan-027 e referenciar plan-045 nos comentários.
3. **Canal alternativo para release falhada** (E2): mesmo canal `notifications.channels.release_notify` (com prefixo `❌`) ou nova chave `notifications.channels.release_failure`? Recomendação: mesmo canal com prefixo distintivo; reduz proliferação de chaves. Documentar em `codex-notifications`.

## Acceptance Criteria

- [ ] AC-1: Decisão Cenário A vs B documentada no Step 1 com evidência (`gh pr list` output, `ls archived/`).
- [ ] AC-2: Plan-027 (mergeado ou em revisão) inclui E1 (queue discovery por label `status: to release`), E2 (label transitions `to release → release → done`), E3 (notificação via MCP de notificação em `notifications.channels.release_notify`, sem citar provider concreto no texto do kata), E4 (Session Trace anexada à GitHub Release body).
- [ ] AC-3: `lex-agent-planning` (atualizado em plan-043) cita `warrior-janus` como owner de `to release → release` e `release → done`.
- [ ] AC-4: Smoke test end-to-end: PR fictício em `status: to release` → `/cry-release` → Janus consome fila → prepare → gate humano → publish → labels transicionam → notificação publicada via MCP de notificação (`notifications.provider`) no canal `notifications.channels.release_notify` com payload completo.
- [ ] AC-5 (Cenário B): commits atômicos + PR aberto + sync `.claude/.cursor/` executado.
