---
plan_id: "044"
title: "warrior-eunomia-plan-and-subtask-creator"
status: todo
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-10T00:00:00Z"
updated_at: "2026-05-10T00:00:00Z"
---

# Plan: warrior-eunomia — owner único da inicialização de trabalho rastreável + PM/Scrum master

## Objective

Criar `warrior-eunomia` (Εὐνομία, deusa do bom ordenamento, filha de Themis) como **owner único da transição `— → todo`** definida em plan-043 e como **gerente de projeto / scrum master** dos planos ativos. Eunomia opera em três modos complementares:

- **Modo 1 — Top-level (criação):** invocada por humano via `cry-plan-task "descrição do trabalho"` → cria o plano `.claude/plans/plan-{NNN}-{slug}.md`, abre a Issue GitHub, verifica Issue Type, executa `gh issue develop` para vincular branch remota, cria worktree.
- **Modo 2 — Subtask (decomposição):** invocada por Athena Phase 4 via `cry-create-subtasks <child#>` → decompõe child Issue em subtask sub-issues executáveis, cada uma com seu plano (inline ≤50 linhas ou anexo), Issue Type Task, `Tracked by`, branch vinculada via `gh issue develop`.
- **Modo 3 — PM/Scrum master (monitoramento contínuo):** ao concluir um plano em modo 1 ou 2, Eunomia agenda um loop de monitoramento (`pm.loop_interval_minutes`, default 15min, via `ScheduleWakeup`). A cada tick, executa `kata-plans-status-digest`: varre planos ativos (status ≠ `done|abandoned`), agrupa por assignee da Issue, e publica resumo via **MCP de notificação configurado em `.ahrena/.directives`** (chave `notifications.provider` — Slack hoje; Discord/Teams/outros amanhã) no canal `notifications.channels.plans_status`, com @mention do humano responsável por cada plano. Anti-spam: pula publicação se nada mudou desde o último tick **e** nenhum plano está stalled (>`pm.stalled_threshold_hours`). Loop encerra automaticamente quando todos os planos tracked atingem `done` ou `abandoned`. **Nenhuma referência a provider específico em warrior/kata** — só ao MCP genérico + chaves de canal abstratas.

Plan-044 absorve integralmente a especificação originalmente desenhada em plan-038 (Steps 19–23) — agora plan-038 fica reduzido a Calliope + PM topology + specs por Component, sem Eunomia. Introduz também `lex-issue-type-verified` (HARD-GATE para criação programática de Issue, com retry e bloqueio definitivo após 3 tentativas) como Lex fundacional usada por Eunomia, Calliope (plan-038), e qualquer agente que crie Issues programaticamente.

## Scope

**Framework (3 línguas — `pt-BR`, `es`, `en`):**

*Lexis (HARD-GATE):*
- `framework/{lang}/_foundation/contributing/lexis/lex-issue-type-verified.md` — toda criação programática de Issue DEVE executar `gh api repos/{owner}/{repo}/issues/{N}` confirmando `type` populado e correto; retry 3× com backoff exponencial (1s, 2s, 4s); falha persistente bloqueia o fluxo da kata invocadora.

*Warrior:*
- `framework/{lang}/engineering/workflow/warriors/warrior-eunomia.md` — persona, responsabilidades, dois modos (top-level + subtask), bound katas, HARD-GATE de não marcar `status: todo` definitivo sem completar os 5 passos.

*Katas:*
- `framework/{lang}/engineering/workflow/katas/kata-create-subtasks.md` — **novo**. Procedimento Eunomia modo subtask (decomposição, granularidade 1 PR, plano inline/anexo, sub-issue + `Tracked by` + Issue Type Task, `gh issue develop` por sub-issue, verificação per `lex-issue-type-verified`, atualização do child com `## Subtasks`).
- `framework/{lang}/_foundation/process/katas/kata-plan-task.md` — **atualizar existente**. Reformular para procedimento Eunomia modo top-level: lê pedido do humano → propõe esqueleto do plano → humano aprova → Eunomia executa os 5 passos. Manter compatibilidade: agentes da sessão (sem Eunomia ativa) seguem o mesmo procedimento — kata é genérico, Eunomia é a executora preferencial.
- `framework/{lang}/engineering/workflow/katas/kata-plans-status-digest.md` — **novo**. Procedimento Eunomia modo 3 (PM/Scrum master). A cada tick (`pm.loop_interval_minutes`):
  - (a) Lista planos em `.claude/plans/**/*.md` (ou `paths.plans` do `.ahrena/.directives`) com `status:` ≠ `done|abandoned`.
  - (a.bis) **Lê heartbeat files** em `.ahrena/workflow/sessions/*.json` (path canônico de plan-043 Step 7). Para cada plano em movimento, associa as sessões ativas (filtra por `plan_id` no JSON; ordena por `started_at`). Marca sessão como `offline` quando `last_heartbeat` > `session_tracking.stale_threshold_minutes` (default 30min).
  - (a.ter) **Refresha o próprio heartbeat** (via `kata-session-heartbeat`, plan-043 Step 7.2) antes de prosseguir — marca `last_activity: "kata-plans-status-digest:tick"`.
  - (b) Para cada plano: extrai título, status, assignee da Issue vinculada (via `gh issue view --json assignees`), nº de PR aberto (via `gh pr list --search "in:body Closes #{issue}"` ou label heuristic), `updated_at`, e flags ("stalled" se ≥ `pm.stalled_threshold_hours` em estado não-terminal).
  - (c) Agrupa por assignee.
  - (d) Renderiza payload de notificação compatível com o provider configurado (markdown / mrkdwn / equivalente do provider em `notifications.provider`). Conteúdo:
    ```
    📋 Plans Status Digest — 2026-05-10 14:30 UTC

    @fernando.seguim
      • plan-043 (workflow-status) — `to review` — PR #84 (loop tick 2/3)
        sessão: `85846253` (claude-vscode) ✓ online, last_hb 2min atrás
      • plan-044 (eunomia) — `development` — sem PR ainda ⚠️ stalled 5h
        sessão: `abc12345` (claude-cli) ⚠️ offline (last_hb 42min atrás)

    @other.assignee
      • plan-027 (janus) — `review` — PR #92 (Argos rodando)
        sessão: `def67890` (claude-vscode) ✓ online, last_hb 8min atrás
    ```
    A renderização final (`mrkdwn` Slack, embeds Discord, Adaptive Cards Teams, etc.) é responsabilidade do **`codex-notifications`** que mapeia o provider para tool MCP + formato. Eunomia produz o conteúdo lógico (incluindo a linha de sessão por plano); o codex faz o transporte.
  - (e) Verifica anti-spam: se `digest == último digest` E nenhum plano `stalled`, pula publicação. Caso contrário, envia via **MCP de notificação** invocando a abstração de `codex-notifications` → o codex resolve `notifications.provider` para a tool correta (ex.: `slack_send_message` quando provider=slack) e o canal lido de `notifications.channels.plans_status`.
  - (f) Verifica horário útil lendo `.ahrena/.directives` (`notifications.working_hours.{start,end,timezone}`; defaults `07:00`, `22:00`, `America/Sao_Paulo`). Skip publish fora da janela. Stalled crítico (≥ `pm.critical_stalled_hours`) ignora horário útil e publica mesmo assim.
  - (g) Se todos planos tracked atingem `done|abandoned`, cancela o próximo `ScheduleWakeup` e loga "PM loop encerrado".
  - (h) **Provider-agnóstico:** o texto deste kata nunca cita Slack/Discord/Teams por nome — só "MCP de notificação configurado". Specifics ficam em `codex-notifications` + `codex-mcp-{provider}`.
- `framework/{lang}/_foundation/contributing/katas/kata-contributing-issue.md` — **atualizar existente**. Adicionar passo terminal de verificação per `lex-issue-type-verified` (`gh api` GET issue, valida `type`).

*Cries:*
- `framework/{lang}/engineering/workflow/cries/cry-create-subtasks.md` — **novo**. `/cry-create-subtasks <child#>`. Invocação manual quando Athena não orquestrou (re-criação após mudança de escopo). Caminho primário: Athena Phase 4 → Eunomia interno.
- `framework/{lang}/_foundation/process/cries/cry-plan-task.md` — **novo**. `/cry-plan-task "descrição"`. Entrypoint top-level humano → Eunomia.
- `framework/{lang}/engineering/workflow/cries/cry-status-digest.md` — **novo**. `/cry-status-digest` — invocação manual do modo 3 (fora do loop automático). Útil para gerar digest sob demanda (ex.: humano pede "como tá tudo?" via chat). Roda `kata-plans-status-digest` uma única vez sem agendar próximo tick.

*Template GitHub Issue:*
- `framework/{lang}/_foundation/contributing_templates/subtask.yml` — **novo**. Campos:
  - `parent` (obrigatório, textarea): "Tracked by #<N>".
  - `summary` (obrigatório): 1-3 frases.
  - `plan_mode` (dropdown: `inline` | `attachment`).
  - `plan_inline` (textarea, condicional `plan_mode == inline`): plano markdown completo, ≤50 linhas / ≤5 steps.
  - `plan_attachment_path` (text, condicional `plan_mode == attachment`): `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md`.
  - `acceptance_criteria` (textarea): numerados `AC-1`, `AC-2`, ... para mapear nos testes.
  - `dependencies` (textarea, opcional): sub-issues bloqueantes.
  - Type: `Task` (auto via `type:` no template).
  - Labels iniciais: `feature request ➕` (ou herdada do parent), `status: todo`.

*Update de Lexis existente:*
- `framework/{lang}/_foundation/contributing/lexis/lex-issue-quality.md` — adicionar `subtask` na tabela de templates aprovados (Issue Type Task); reforçar HARD-GATE existente referenciando `lex-issue-type-verified` para criação programática.

*Config:*
- `framework/platforms.yaml` — entry de `cursor.rules` para `_foundation/contributing/lexis/lex-issue-type-verified` (per `lex-platforms-rules`).

**Não escopo deste plano:**
- Definição do enum de status e dos labels — feita em plan-043.
- Lógica de transição de status pelos agentes (Athena, Argos, Janus) — feita em plan-043.
- Decomposição de Epic em child Issues — Calliope, em plan-038.
- PM topology (Aglaea, Eos, Prometheus narrowing) — em plan-038.

## Steps

- [ ] **Step 1 — Issue + branch remota vinculada + worktree.** Sequência obrigatória (executada manualmente pelo agente da sessão, já que Eunomia é o artefato sendo criado — chicken-and-egg justificado):
  1. **Abrir issue** `feature-request` per `lex-issue-quality` (template, label `feature request ➕`, type `Feature`, assignee `@me`, Why/What/How). Aplicar label inicial `status: todo` (assume plan-043 mergeada — se não, criar a label manualmente via `gh label create`).
  2. **Verificar Issue Type pós-criação** via `gh api repos/{owner}/{repo}/issues/{N}` confirmando `type: Feature`. Se ausente, `gh api -X PATCH .../issues/{N} -f type=Feature` e re-verificar.
  3. **Criar branch remota vinculada** via `gh issue develop {N} --base main --name feat/{N}-warrior-eunomia-plan-and-subtask-creator --checkout`.
  4. **Criar worktree** `.worktrees/{N}-warrior-eunomia-plan-and-subtask-creator/` (per `lex-git-worktrees`).
  5. **Atualizar este plano** com `issue: "guardiatechnology/ahrena#{N}"` + `updated_at`.

- [ ] **Step 2 — ADR.** Abrir `docs/adr/ADR-{N}-warrior-eunomia-unified-plan-and-subtask-creation.md` (MADR simplificado) capturando: (a) por que Eunomia consolida plan creation + subtask creation num único warrior (em vez de dois — Eunomia top-level e outro warrior subtask); (b) critério de granularidade da decomposição (1 PR por subtask, per `lex-small-commits`); (c) critério "plano grande" (>50 linhas ou >5 steps) que força anexo em vez de body inline; (d) por que `lex-issue-type-verified` nasce neste plano e não como Lex isolada (acoplamento natural com criação programática que Eunomia opera).

- [ ] **Step 3 — Criar `lex-issue-type-verified` (3 línguas).** Path: `framework/{lang}/_foundation/contributing/lexis/lex-issue-type-verified.md`. Conteúdo:
  - HARD-GATE per `lex-hard-gate-pattern`: nenhum agente PODE prosseguir após criação programática de Issue sem verificar `type` via `gh api`. Counter-pretexts: "GitHub API tá lenta hoje" (retry resolve transitório; persistente é bug), "vou aplicar type depois manualmente" (não — fluxo bloqueia). Exception: nenhuma.
  - Retry policy: até 3 tentativas com backoff exponencial (1s, 2s, 4s).
  - Falha definitiva: bloqueia kata invocadora; exige intervenção humana.
  - Aplica a: Eunomia (este plano), Calliope (plan-038), `kata-contributing-issue` (atualizada neste plano).
  - Registrar em `framework/platforms.yaml` (`cursor.rules`).

- [ ] **Step 4 — Criar `warrior-eunomia` (3 línguas).** Path: `framework/{lang}/engineering/workflow/warriors/warrior-eunomia.md`. Persona: Εὐνομία, deusa do bom ordenamento, filha de Themis (continuidade temática da família triagem→decomposição→ordenação que envolve Themis em plan-037 e Calliope em plan-038). Responsabilidades:
  - Owner único de `— → todo` (definido em plan-043).
  - **Modo 1 — top-level** (humano via `cry-plan-task`):
    1. Lê pedido + propõe esqueleto do plano (Objective + Scope + Steps draft).
    2. **Gate humano explícito:** humano aprova o esqueleto antes de Eunomia abrir Issue ou criar branch.
    3. Executa os 5 passos: Issue + verify type + `gh issue develop` + worktree + plano final em `status: todo`.
    4. **Escreve front-matter completo** incluindo `claude_session` + `session_entrypoint` (per plan-043 Step 7.3) lidos das env vars.
    5. **Cria heartbeat file** via `kata-session-heartbeat` (plan-043 Step 7.2) marcando `last_activity: "kata-plan-task:plan_created"`.
    6. **Agenda automaticamente o loop de monitoramento (Modo 3)** se ainda não estiver ativo na sessão.
  - **Modo 2 — subtask** (Athena Phase 4 via `cry-create-subtasks`):
    1. Lê child Issue + spec do PM em `docs/{context}/{tipo}/*` quando plan-038 mergeada.
    2. Decompõe em subtasks executáveis (granularidade: 1 PR/subtask).
    3. Para cada subtask: gera plano (≤50 linhas inline / >50 linhas anexo).
    4. Cria sub-issue via template `subtask.yml`, executa `gh issue develop` por subtask, verifica per `lex-issue-type-verified`.
    5. **Em cada plano de subtask**: escreve `claude_session` + `session_entrypoint` no front-matter; cria heartbeat file via `kata-session-heartbeat`.
    6. Atualiza child Issue com `## Subtasks`.
    7. **Agenda o loop de monitoramento (Modo 3)** se ainda não estiver ativo — cobre as sub-issues recém-criadas.
  - **Modo 3 — PM/Scrum master** (automático após Modos 1/2; manual via `cry-status-digest`):
    1. Loop via `ScheduleWakeup`, intervalo `pm.loop_interval_minutes` (default 15min, lido de `.directives`).
    2. A cada tick: invoca `kata-plans-status-digest` → lista planos ativos → agrupa por assignee → publica via **MCP de notificação configurado em `.directives`** (`notifications.provider`) no canal `notifications.channels.plans_status` com @mention.
    3. Anti-spam: pula se digest idêntico ao anterior E nenhum plano `stalled` (`pm.stalled_threshold_hours`, default 4h).
    4. Horário útil: skip publish entre `notifications.working_hours.end` e `notifications.working_hours.start` (defaults 22:00 e 07:00, timezone `notifications.working_hours.timezone` default `America/Sao_Paulo`); exceção para stalled crítico (`pm.critical_stalled_hours`, default 24h).
    5. Auto-encerramento: cancela próximo wake-up quando todos planos tracked atingem `done|abandoned`.
    6. Não cria, não move, não orquestra — apenas observa e reporta. Mover planos é trabalho de Athena/Argos/Janus.
    7. **Provider-agnóstico:** Eunomia nunca chama `slack_send_message` diretamente em seu próprio texto. Invoca a abstração genérica do `codex-notifications` (definido em plan-043 Step 6d), que mapeia `notifications.provider` para a tool MCP correta.
  - Bound katas: `kata-plan-task`, `kata-create-subtasks`, `kata-plans-status-digest`, `kata-mcp-github-read`, `kata-contributing-issue`.
  - HARD-GATE: NÃO marca `status: todo` definitivo sem completar os 5 passos do modo 1 ou 2.

- [ ] **Step 5 — Criar `kata-create-subtasks` (3 línguas).** Path: `framework/{lang}/engineering/workflow/katas/kata-create-subtasks.md`. Procedimento Eunomia modo subtask:
  - (a) Lê child Issue (body, ACs, label `spec-ready` quando aplicável — gate de plan-038).
  - (b) Lê spec do PM em `docs/{context}/{tipo}/*` se existir; sem 038 mergeada, opera só com body da Issue.
  - (c) Decompõe em subtasks executáveis. **Critério de granularidade:** cada subtask cabe em 1 PR (per `lex-small-commits`) e tem entrega independente. Athena revisa lista antes de iniciar implementação; rejeita decomposição imprópria e re-invoca Eunomia.
  - (d) Para cada subtask: plano ≤50 linhas → body inline; plano >50 linhas OU >5 steps → resumo no body + arquivo `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md`.
  - (e) Cria sub-issue via template `subtask.yml` (Step 8), Issue Type Task, `Tracked by #<child Issue>`, labels herdados do child exceto `status:*` (sub-issue nasce `status: todo` próprio).
  - (f) Executa `gh issue develop` para cada sub-issue, vinculando branch remota.
  - (g) Verifica pós-criação per `lex-issue-type-verified`.
  - (h) Atualiza child Issue com seção `## Subtasks` listando filhos.

- [ ] **Step 6 — Atualizar `kata-plan-task` (3 línguas).** Path: `framework/{lang}/_foundation/process/katas/kata-plan-task.md`. Reformular para procedimento Eunomia modo top-level:
  - Lê pedido do humano.
  - Propõe esqueleto (Objective + Scope + Steps draft).
  - **Gate humano:** humano aprova antes de qualquer ação destrutiva (criar Issue, branch, etc.).
  - Executa: Issue + verify type per `lex-issue-type-verified` + `gh issue develop` + worktree + plano final em `status: todo`.
  - Manter fallback compatível: agentes da sessão (sem Eunomia ativa) seguem o mesmo procedimento — kata é genérico, Eunomia é a executora preferencial.

- [ ] **Step 7 — Criar `kata-plans-status-digest` (3 línguas).** Path: `framework/{lang}/engineering/workflow/katas/kata-plans-status-digest.md`. Procedimento Eunomia modo 3 (PM/Scrum master), **provider-agnóstico**:
  - **Configuração via `.ahrena/.directives`:** lê `notifications.provider`, `notifications.channels.plans_status`, `notifications.working_hours.{start,end,timezone}`, `pm.loop_interval_minutes` (default 15), `pm.stalled_threshold_hours` (default 4), `pm.critical_stalled_hours` (default 24). Schema definido em plan-043 Step 6.
  - **Coleta:** lista `.claude/plans/**/*.md` (ou `paths.plans`); para cada arquivo lê front-matter `status`, `issue`, `updated_at`, `title`. Filtra `status ≠ done|abandoned`.
  - **Enriquecimento via `gh`:** para cada plano, `gh issue view {issue} --json assignees,state` + `gh pr list --search "in:body Closes #{issue}" --json number,url,labels` (heurística para descobrir PR ativo).
  - **Análise:** marca cada plano com flag `stalled` (≥ threshold), `progressing`, ou `idle-recent`.
  - **Renderização do conteúdo lógico:** tabela agrupada por assignee com @mention, título + status + PR link + flag. Cabeçalho com timestamp UTC. **Formato de saída (mrkdwn Slack, embed Discord, Adaptive Card Teams, etc.) é resolvido pelo `codex-notifications` no momento do envio** — Eunomia produz só a representação canônica.
  - **Anti-spam:** mantém cache local em `.ahrena/workflow/eunomia-pm-cache.json` (gitignored) com hash do último digest. Se hash atual == anterior E nenhum `stalled` novo, skip publish.
  - **Horário útil:** se fora da janela `notifications.working_hours`, skip publish. Se algum plano tem stalled ≥ `pm.critical_stalled_hours`, ignora janela e publica.
  - **Publicação:** invoca a abstração genérica do `codex-notifications` passando (canal_lógico=`plans_status`, conteúdo). O codex resolve `notifications.provider` para a tool MCP correta (ex.: `slack_send_message` quando provider=slack) e o canal real (`notifications.channels.plans_status`).
  - **Auto-encerramento:** se todos planos coletados estão `done|abandoned`, loga "PM loop encerrado" e NÃO reagenda próximo `ScheduleWakeup`. Caso contrário, agenda próximo tick em `pm.loop_interval_minutes`.
  - **Lock anti-duplicação:** antes de cada tick, checa `.ahrena/workflow/eunomia-pm.lock` (PID + timestamp). Se lock existe e <`pm.loop_interval_minutes`, abdica (segunda instância detectada). Limpa lock no fim.

- [ ] **Step 8 — Atualizar `kata-contributing-issue` (3 línguas).** Adicionar passo terminal de verificação per `lex-issue-type-verified` (`gh api` GET issue, valida `type`; retry 3× com backoff). Path: `framework/{lang}/_foundation/contributing/katas/kata-contributing-issue.md`.

- [ ] **Step 9 — Criar template GitHub `subtask.yml` (3 línguas).** Path: `framework/{lang}/_foundation/contributing_templates/subtask.yml`. Campos detalhados no Scope. Aplicar Issue Type `Task` via `type:` no template. Labels iniciais herdadas do parent + `status: todo`.

- [ ] **Step 10 — Atualizar `lex-issue-quality` (3 línguas).** Adicionar `subtask` na tabela de templates aprovados (Issue Type Task). Reforçar HARD-GATE existente referenciando `lex-issue-type-verified` para criação programática. Path: `framework/{lang}/_foundation/contributing/lexis/lex-issue-quality.md`.

- [ ] **Step 11 — Criar `cry-create-subtasks` (3 línguas).** Path: `framework/{lang}/engineering/workflow/cries/cry-create-subtasks.md`. `/cry-create-subtasks <child#>`. Invocação manual quando Athena não orquestrou. Invoca `warrior-eunomia` em modo subtask via `kata-create-subtasks`.

- [ ] **Step 12 — Criar `cry-plan-task` (3 línguas).** Path: `framework/{lang}/_foundation/process/cries/cry-plan-task.md`. `/cry-plan-task "descrição do trabalho"`. Entrypoint top-level humano. Invoca `warrior-eunomia` em modo top-level via `kata-plan-task`.

- [ ] **Step 13 — Criar `cry-status-digest` (3 línguas).** Path: `framework/{lang}/engineering/workflow/cries/cry-status-digest.md`. `/cry-status-digest` — invocação manual do modo 3 (one-shot, fora do loop). Útil para gerar digest sob demanda. Roda `kata-plans-status-digest` uma única vez sem agendar próximo tick.

- [ ] **Step 14 — Sync local.** `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor` (per memory `reference_install_py_self_sync`).

- [ ] **Step 15 — Smoke test conceitual.** Em um repo de teste:
  - (a) `/cry-plan-task "task de validação Eunomia top-level"` → Eunomia propõe esqueleto, humano aprova, 5 passos executam, plano em `status: todo` criado, **loop PM agendado**.
  - (b) `/cry-create-subtasks <child#>` (child fictício) → Eunomia decompõe em 3 subtasks (1 inline + 2 anexos), cada uma com sub-issue + `Tracked by` + branch vinculada, **loop PM cobre as sub-issues**.
  - (c) Forçar falha de verificação Issue Type (`gh api` retornando type vazio) → confirmar retry 3× + bloqueio definitivo per `lex-issue-type-verified`.
  - (d) `/cry-status-digest` → confirma digest one-shot publicado no canal de notificação lido de `.directives` (`notifications.channels.plans_status`).
  - (e) Avançar simulado de `updated_at` de um plano para >4h atrás → confirmar flag `stalled` no próximo digest.
  - (f) Forçar horário fora da janela útil (mock de timezone) → confirmar skip publish, exceto se houver stalled crítico (>24h).
  - (g) Marcar todos planos tracked como `done` → confirmar auto-encerramento do loop (sem próximo `ScheduleWakeup`).
  - Documentar em `docs/issues/issue-{N}/smoke-test.md`.

- [ ] **Step 16 — Auto-revisão.** Aplicar `kata-artifact-self-review` a cada artefato novo. Endereçar findings 🔴.

- [ ] **Step 17 — Commits + PR.** Commits atômicos (per `lex-small-commits`, `lex-conventional-commits`, `lex-commit-language`, `lex-signed-commits`) agrupados por área:
  - `feat(contributing): add lex-issue-type-verified hard-gate for programmatic Issue creation`
  - `feat(workflow): add warrior-eunomia as owner of plan + subtask creation + PM digest`
  - `feat(workflow): add kata-create-subtasks for subtask decomposition`
  - `refactor(process): rework kata-plan-task as Eunomia top-level entry`
  - `feat(workflow): add kata-plans-status-digest for Eunomia PM/scrum-master mode`
  - `feat(workflow): add cry-create-subtasks, cry-plan-task, and cry-status-digest entrypoints`
  - `feat(contributing): add subtask.yml issue template`
  - `docs(contributing): extend lex-issue-quality with subtask template and Issue Type verification`
  - `chore(framework): register lex-issue-type-verified in platforms.yaml`
  - `chore(claude): regenerate .claude/ and .cursor/ via install.py --self`
  - Abrir PR per `kata-contributing-pr` + `lex-pr-quality` (label `status: review` ao abrir, per plan-043).

## Dependencies

- **plan-043** (`workflow-status-and-review-loop`) — pré-requisito hard. Plan-043 define:
  - Enum `status: todo|development|to review|review|to release|release|done`.
  - Label canônica `status: todo` que Eunomia aplica.
  - Regra "Owner do `— → todo`: warrior-eunomia" em `lex-agent-planning`.
  - **Session tracking infrastructure** (Step 7): `codex-session-tracking`, `kata-session-heartbeat`, schema heartbeat file, extensão de `lex-agent-planning` com campo `claude_session`, extensão de `lex-pr-quality` com seção "Session Trace", `kata-pr-prepare` atualizado.
  - **Notification provider abstraction** (Step 6): `notifications.*` em `.directives`, `codex-notifications`, primeiro MCP provider (Slack).
  Sem plan-043 mergeado, Eunomia opera num vácuo conceitual.
- **plan-027** (`warrior-janus-release-orchestrator`) — não bloqueante para 044, mas conceitualmente alinhado: Janus fecha o ciclo que Eunomia abre.
- **plan-038** (`pm-topology-per-component-and-epic-decomposition`) — não bloqueante para 044. Quando 038 sair, Calliope (criada lá) também usa `lex-issue-type-verified` deste plano. Plan-038 perde Steps 19–23 originais (Eunomia + Lex), agora cobertos aqui.
- **`kata-mcp-github-read`** (existente) — Eunomia consulta GitHub via MCP.

## Risks

- **Eunomia gera subtasks excessivamente granulares (1 PR por linha) ou grosseiras demais (1 subtask = US inteira).** Mitigação: critério de granularidade em `kata-create-subtasks` (cada subtask cabe em 1 PR per `lex-small-commits`, tem entrega independente). Athena revisa lista antes de iniciar implementação; rejeita decomposição imprópria e re-invoca Eunomia.
- **Issue Type não atribuído após criação programática** (race condition GitHub API). Mitigação: `lex-issue-type-verified` força verificação `gh api` pós-criação; retry automático até 3 tentativas com backoff exponencial. Falha persistente bloqueia o fluxo e exige intervenção.
- **Subtask plan no body fica grande demais** (perde legibilidade). Mitigação: critério "grande" definido (>50 linhas markdown OU >5 steps) força anexo em `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md` + resumo no body. `kata-create-subtasks` aplica regra automaticamente.
- **Chicken-and-egg no Step 1:** Eunomia é o artefato sendo criado, então não pode criar a si mesma. Mitigação: agente da sessão executa manualmente os 5 passos do Step 1 seguindo exatamente o contrato que Eunomia depois vai herdar — zero refatoração subsequente.
- **Eunomia top-level pode bypass o gate humano** se mal-implementada. Mitigação: HARD-GATE explícito no warrior + `kata-plan-task` força aprovação humana antes de qualquer ação destrutiva; ADR (Step 2) documenta a razão.
- **`gh issue develop` exige permissão de escrita no repo + Issue existir.** Mitigação: ordem do Step 1 (Issue antes de branch); falha de permissão é catchada e reportada ao usuário sem mascarar.
- **Modo 3 (PM) vira ruído** se digest for muito frequente ou redundante. Mitigação: anti-spam por hash (skip se nada mudou + nenhum stalled novo); horário útil (skip fora de `notifications.working_hours`); cadência configurável via `pm.loop_interval_minutes` (default 15min — intervalo mais curto razoável; alinha com loop de Athena).
- **Acoplamento a um provider específico engessa o framework.** Mitigação: `notifications.provider` lido de `.directives`; warrior/kata referem-se a "MCP de notificação" sem citar Slack/Discord/Teams. `codex-notifications` é o único ponto que mapeia provider → tool. Trocar de Slack para Discord = editar `.directives` + ativar novo MCP server, sem mudar código de warrior/kata. Lexis envelhecem bem.
- **Modo 3 publica fora do horário útil indevidamente.** Mitigação: stalled crítico (≥24h) bypassa horário útil — é situação real que merece notificação. Tudo mais respeita janela. Configurável em `.directives`.
- **Cache de anti-spam corrompido leva a digest perdido.** Mitigação: cache `eunomia-pm-cache.json` é gitignored; se corromper, próximo tick recalcula do zero (digest aparece, talvez duplicado). Mal menor que digest perdido.
- **Loop PM continua após plano abandonado/perdido.** Mitigação: auto-encerramento ao detectar todos planos `done|abandoned`. Manual: `/cry-status-digest --stop` (avaliar adicionar flag).
- **Múltiplas instâncias Eunomia rodando** (sessões paralelas) podem agendar loops duplicados. Mitigação: lock file `.ahrena/workflow/eunomia-pm.lock` com PID/timestamp; segunda instância detecta lock recente (<20min) e abdica. Documentar em `kata-plans-status-digest`.

## Open Questions

1. **`cry-plan-task` nome final.** Alternativas: `cry-plan-task` (recomendado por simetria com `kata-plan-task`), `cry-new-task`, `cry-init-task`. Decidir no Step 11.
2. **Cry top-level argumentos.** `/cry-plan-task "descrição"` aceita também `--type {feat|fix|chore|...}` e `--no-issue` (planos de discussão/discovery sem Issue)? Recomendação: começar minimalista (só descrição); estender se aparecer necessidade real.
3. **Onde guardar logs de retry de `lex-issue-type-verified`?** Stdout (default), arquivo em `.ahrena/workflow/issue-{N}/eunomia.log`, ou notificação via MCP? Recomendação: stdout + arquivo. MCP de notificação só para falha definitiva.
4. **Eunomia decompõe Eunomia?** Recursão infinita. Mitigação implícita: top-level só cria plano; subtask sub-issue não pode ser sub-decomposta automaticamente (cada subtask é o leaf). Documentar explicitamente no warrior.

## Acceptance Criteria

- [ ] AC-1: `/cry-plan-task "descrição"` invoca Eunomia top-level; esqueleto proposto; humano aprova; 5 passos executados; plano em `status: todo` criado com Issue + branch vinculada + worktree.
- [ ] AC-2: `/cry-create-subtasks <child#>` invoca Eunomia subtask; decomposição apresentada; humano aprova; sub-issues criadas com `Tracked by`, Issue Type Task, plano inline/anexo conforme tamanho, branch vinculada via `gh issue develop`.
- [ ] AC-3: `lex-issue-type-verified` bloqueia fluxo se `gh api` retorna `type` vazio após 3 retries; mensagem clara ao humano.
- [ ] AC-4: Sub-issue criada via template `subtask.yml` tem Issue Type Task, `status: todo`, e `Tracked by #<N>` no body.
- [ ] AC-5: `kata-contributing-issue` (atualizado) executa verificação per `lex-issue-type-verified` em criações programáticas.
- [ ] AC-6: `lex-issue-quality` (atualizado) lista `subtask` na tabela de templates aprovados.
- [ ] AC-7: Todos artefatos existem em pt-BR, es, en (per `lex-framework-language`).
- [ ] AC-8: `framework/platforms.yaml` tem entry para `lex-issue-type-verified`.
- [ ] AC-9: `kata-artifact-self-review` aplicado a cada artefato novo passa sem findings 🔴.
- [ ] AC-10: Smoke test conceitual documentado em `docs/issues/issue-{N}/smoke-test.md` cobrindo top-level + subtask + falha de verificação + digest PM + stalled flag + horário útil + auto-encerramento.
- [ ] AC-11: Modo 3 (PM) agendado automaticamente após criação de plano (modos 1 e 2); loop (`pm.loop_interval_minutes`, default 15min) publica digest via MCP de notificação configurado em `notifications.provider`, canal `notifications.channels.plans_status`, agrupado por assignee com @mention. **Nenhuma referência a Slack/Discord/Teams diretamente no warrior/kata** — só ao MCP abstrato.
- [ ] AC-12: `/cry-status-digest` (one-shot) gera digest sob demanda sem agendar próximo tick.
- [ ] AC-13: Anti-spam (skip se digest idêntico + sem stalled novo), horário útil (skip 22:00–07:00 default), e bypass para stalled crítico (>24h) funcionam conforme especificado.
- [ ] AC-14: Loop PM auto-encerra quando todos planos tracked atingem `done|abandoned`.
