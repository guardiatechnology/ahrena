---
plan_id: "043"
title: "workflow-status-and-review-loop"
status: development
agent: claude
issue: "guardiatechnology/ahrena#90"
branch: "feat/90-workflow-status-review-loop"
worktree: ".worktrees/90-workflow-status-review-loop"
created_at: "2026-05-10T00:00:00Z"
updated_at: "2026-05-11T22:28:15Z"
---

# Plan: Workflow status alignment + review loop + notification provider

## Objective

Alinhar o ciclo de vida do plano (`lex-agent-planning`) e da Issue do GitHub a um único conjunto de status — `todo → development → to review → review → to release → release → done` — eliminando `pending`, `in-progress` e `archived`. Os estados intermediários `to review` e `to release` separam fila (esperando alguém começar) de execução (em andamento), tornando o workflow auditável e as notificações mais precisas. Atribuir transições a agentes específicos: **`warrior-eunomia`** (entregue em **plan-044**) é a owner de `— → todo`; `warrior-athena` move `todo → development` (Phase 4, invocando Eunomia) → `to review` (abre PR) → `to release` (PR aprovado por humano); `warrior-argos` move `to review → review` ao iniciar e devolve para `to review` ou avança ao terminar; **`warrior-janus`** (entregue em **plan-027**, wiring com ciclo via **plan-045**) move `to release → release → done` com gate humano. Adicionar um loop de auto-cobrança em 3 ciclos de 15 min para PRs em `to review` aguardando aprovação humana, com **notificação via MCP de notificação configurado em `.directives`** (`notifications.provider`) no canal `notifications.channels.pr_review_timeout` ao final. Habilitar o primeiro MCP de notificação (Slack como provider inicial; outros providers via implementações futuras) no framework per `lex-mcp` regra 5.

**Decomposição realizada em 2026-05-10:** plan-043 foi reduzido a este escopo (status core + wiring Athena/Argos + MCP de notificação + loops + migração de planos existentes). Eunomia + suas katas + `lex-issue-type-verified` saíram para **plan-044**. Wiring Janus + notificação de release saíram para **plan-045** (pointer a plan-027). Lexis/Codex/Warriors **não citam o provider concreto (Slack/Discord/Teams) por nome** — referenciam apenas o MCP de notificação abstrato lido de `.directives`.

## Scope

**Framework (3 línguas — `pt-BR`, `es`, `en`):**

*Ciclo de status + loops + notificações:*
- `framework/{lang}/_foundation/process/lexis/lex-agent-planning.md` — enum de status, diagrama de lifecycle, regras de transição, owner do `— → todo` (Eunomia)
- `framework/{lang}/_foundation/process/codex/codex-agent-planning.md` — manual operacional alinhado
- `framework/{lang}/engineering/workflow/warriors/warrior-athena.md` — responsabilidades de transição + gatilho de loop de revisão + invocação de Eunomia na Phase 4
- `framework/{lang}/engineering/quality/warriors/warrior-argos.md` — entrada/saída do estado `review` + loop intercalado com Athena
- `framework/{lang}/_foundation/contributing/lexis/lex-issue-quality.md` (avaliar) ou novo `lex-issue-status` — labels canônicos de status na issue
- `framework/{lang}/_foundation/tooling/codex/codex-mcp-slack.md` — novo manual do MCP Slack
- `framework/{lang}/_foundation/tooling/lexis/lex-mcp.md` — adicionar Slack à lista de servidores conhecidos (se aplicável)
- `framework/{lang}/_foundation/contributing/lexis/lex-pr-quality.md` (avaliar) — referência ao loop de revisão e canais de notificação (`notifications.channels.pr_review_timeout`)
- `framework/mcp/slack.json` — declaração do MCP (transporte HTTP remoto se disponível; fallback npx documentado com `_comment`)
- `framework/platforms.yaml` — entry de `cursor.rules` para qualquer novo Lexis/Codex (per `lex-platforms-rules`)

*Eunomia — plan + subtask creator (absorvida de plan-038 por decisão do usuário em 2026-05-10):*
- `framework/{lang}/engineering/workflow/warriors/warrior-eunomia.md` — **novo warrior** (Εὐνομία, deusa do bom ordenamento, filha de Themis). Owner único de `— → todo`. Dois modos:
  - **Top-level:** invocada por humano via `cry-plan-task`; cria plano `.claude/plans/plan-{NNN}-{slug}.md` + Issue + branch + worktree.
  - **Subtask:** invocada por Athena Phase 4 via `cry-create-subtasks`; decompõe child Issue em sub-issues executáveis (cada uma com seu próprio plano + Issue + branch).
- `framework/{lang}/engineering/workflow/katas/kata-create-subtasks.md` — **novo kata**. Procedimento Eunomia em modo subtask: lê child Issue + spec do PM (`docs/{context}/{tipo}/*` quando plan-038 mergeada), decompõe em subtasks, escreve plano (body inline ≤50 linhas OU resumo no body + anexo `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md` para >50 linhas), cria sub-issue GitHub via template `subtask.yml` (Issue Type Task + `Tracked by #<child Issue>` + labels herdados), verifica pós-criação per `lex-issue-type-verified`, atualiza child Issue com seção `## Subtasks` listando filhos.
- `framework/{lang}/_foundation/process/katas/kata-plan-task.md` — **atualizar kata existente**. Reformular para ser o procedimento que Eunomia executa em modo top-level: lê pedido do humano → propõe esqueleto do plano → humano aprova → Eunomia executa os 5 passos (Issue + verify type + `gh issue develop` + worktree + plano final em `status: todo`). Hoje é genérico (qualquer agente); passa a ter Eunomia como executora preferencial, mantendo fallback "agente da sessão" quando Eunomia indisponível.
- `framework/{lang}/engineering/workflow/cries/cry-create-subtasks.md` — **novo cry**. `/cry-create-subtasks <child#>` — invocação manual quando Athena não orquestrou (ex: re-criação após mudança de escopo). Caminho primário é Athena Phase 4 → Eunomia interno.
- `framework/{lang}/_foundation/process/cries/cry-plan-task.md` — **novo cry**. `/cry-plan-task "descrição do trabalho"` — entrypoint top-level. Invoca `warrior-eunomia` em modo top-level via `kata-plan-task`.
- `framework/{lang}/_foundation/contributing_templates/subtask.yml` — **novo template GitHub Issue**. Campos: parent (`Tracked by #<N>`, obrigatório), summary, plan inline (textarea — pequena) OU plan link (file path — anexo), acceptance criteria (numerados, mapeam para `AC-N` nos testes), dependencies. Issue Type Task auto-aplicado.
- `framework/{lang}/_foundation/contributing/lexis/lex-issue-type-verified.md` — **novo Lexis HARD-GATE**. Toda criação programática de Issue (por Eunomia, Calliope-em-plan-038, ou qualquer agente via `kata-contributing-issue`) DEVE executar passo terminal `gh api repos/{owner}/{repo}/issues/{N}` confirmando `type` populado e correto. Falha de verificação bloqueia o fluxo da kata invocadora (retry automático até 3 tentativas com backoff antes de falhar definitivamente).
- `framework/{lang}/_foundation/contributing/katas/kata-contributing-issue.md` — **atualizar kata existente**. Adicionar passo terminal de verificação per `lex-issue-type-verified` (`gh api` GET issue, valida `type`).
- `framework/{lang}/_foundation/contributing/lexis/lex-issue-quality.md` — **atualizar Lexis existente**. Adicionar `subtask` na tabela de templates aprovados (Issue Type Task). Reforçar HARD-GATE existente referenciando `lex-issue-type-verified` para criação programática.

**Repo Ahrena (artefatos diretos do projeto):**
- `.claude/plans/**/*.md` — migração de campo `status:` (`pending` → `todo`; `in-progress` → `development`)
- `.claude/plans/pending/` — decidir rename para `.claude/plans/todo/` ou manter pasta com nome legado (ver Risks)
- `.claude/plans/archived/` — manter como organização de filesystem para planos concluídos pós-merge (não é mais um status)
- `scripts/install.py` e/ou `scripts/preflight.py` — distribuir `slack.json` para `.ahrena/mcp/` no install
- `Makefile` — não muda; `make mcp-enable SERVER=slack` já é coberto pelo plan-042

**Labels no GitHub (aplicado por automação ou pelos agentes via `gh`):**
- `status: todo`, `status: development`, `status: to review`, `status: review`, `status: to release`, `status: release`, `status: done`
- Cores sugeridas (gradiente progresso): cinza → azul-claro → amarelo-claro → amarelo → laranja-claro → laranja → verde
- Espaços no nome da label são suportados por `gh label`; manter o nome legível ("to review" em vez de `to-review`) preserva paridade com o `status:` do plano.

## Steps

- [x] **Step 1 — Issue + branch remota vinculada + worktree (executado por `warrior-eunomia`; se Eunomia ainda não shipada, pelo agente da sessão corrente seguindo o contrato que ela vai absorver).** Sequência obrigatória:

  **Concluído em 2026-05-11 (Claude Code / agente da sessão; Eunomia ainda não shipada — fallback documentado).**
  - Issue `#90` — `feat: unify workflow status (todo → development → to review → review → to release → release → done) with PR review loop and provider-agnostic notifications`
  - Issue Type aplicado via `gh api -X PATCH ... -f type=Feature` (verificado: `type: Feature` populado)
  - Labels: `feature request ➕`; assignee: `fernandoseguim`
  - Branch remota vinculada via `gh issue develop 90 --base main --name feat/90-workflow-status-review-loop`
  - Worktree: `.worktrees/90-workflow-status-review-loop/` (tracking `origin/feat/90-workflow-status-review-loop`)
  - Front-matter deste plano atualizado com `issue:`, `branch:`, `worktree:`, `status: in-progress`, `updated_at`

  1. **Abrir issue** `feature-request` per `lex-issue-quality` (template, label `feature request ➕`, type `Feature`, assignee `@me`, Why/What/How). Aplicar label inicial `status: todo` (após Step 5 criar a label).
  2. **Verificar Issue Type pós-criação** via `gh api repos/{owner}/{repo}/issues/{N}` confirmando `type: Feature` populado (per `lex-issue-type-verified` — agora criado neste plano, ver Step novo dedicado a Eunomia + Lex). Se `type` ausente, aplicar via `gh api -X PATCH .../issues/{N} -f type=Feature` e re-verificar (até 3 tentativas com backoff).
  3. **Criar a branch remota e vincular à Issue** via `gh issue develop {N} --base main --name feat/{N}-workflow-status-review-loop --checkout` — esse comando cria o branch no remote E registra o linkage "Development" na issue do GitHub (aparece como branch linkada na sidebar da issue). Empurrar imediatamente para `origin` se o `--checkout` local for usado (`git push -u origin feat/...`).
  4. **Criar worktree** `.worktrees/{N}-workflow-status-review-loop/` apontando para a branch já criada (per `lex-git-worktrees`).
  5. **Atualizar este plano** com o número da issue no front-matter (`issue: "guardiatechnology/ahrena#{N}"`) + `updated_at`.

  Essa sequência (issue → verificar type → branch remota vinculada → worktree → atualizar plano) é o que o **Step 3 vai codificar como regra em `lex-agent-planning`** e que **Eunomia vai operacionalizar** via novos steps deste plano. Top-level (este plano) e subtask (Athena Phase 4) reusam o mesmo procedimento.

  > **Nota:** Eunomia é criada neste plano (Steps Eunomia-1 a Eunomia-7 abaixo). Como Eunomia ainda não existe quando este Step 1 é executado, a sessão corrente (Claude Code) realiza os 5 passos manualmente seguindo o contrato que Eunomia depois vai herdar. A partir do Step Eunomia-1, futuros planos invocam Eunomia diretamente via `/cry-plan-task`.

- [x] **Step 2 — Decisão de design registrada em ADR.** Abrir `docs/adr/ADR-{N}-workflow-status-unified-plan-and-issue.md` (formato MADR simplificado, per `lex-issue-driven`) capturando: (a) razão para colapsar 5 status no plano e na issue; (b) por que `abandoned` permanece fora do happy path (sai dos 5 para o terminal alternativo); (c) cadência do loop (3×15min) e justificativa do tradeoff humano vs. ruído; (d) chaves de canal de notificação por evento (`notifications.channels.{pr_review_timeout,release_notify,plans_status}`) e estratégia provider-agnóstica (Lexis/Codex não citam provider concreto). ADR é referência obrigatória nos commits dos Steps 3 e 4.

  **Concluído em 2026-05-11.** `docs/adr/ADR-001-workflow-status-unified-plan-and-issue.md` criado em status `proposed`, MADR simplificado per `kata-adr-write`, vinculado à Issue #90. Cobre os 4 pontos exigidos (collapse de status, abandoned terminal alternativo, cadência 3×15min, notificações provider-agnósticas) + alternativas A–E rejeitadas com justificativa.

- [x] **Step 3 — Atualizar `lex-agent-planning` nas 3 línguas.** Substituir enum **e nomear Eunomia como owner do `— → todo`:**

  **Concluído em 2026-05-11.** Os 3 arquivos `framework/{pt-BR,es,en}/_foundation/process/lexis/lex-agent-planning.md` foram reescritos com: (i) enum unificado `todo | development | to review | review | to release | release | done | abandoned`; (ii) lifecycle atualizado com semântica por estado; (iii) seção "Owner do `— → todo`: warrior-eunomia" com os 5 passos canônicos; (iv) HARD-GATE per `lex-hard-gate-pattern` bloqueando marcação de `status: todo` sem os 5 passos; (v) tabela "Owners de cada transição" cobrindo `— → todo` até `release → done`; (vi) referências adicionadas (`lex-issue-status`, `lex-issue-type-verified`, `kata-create-subtasks`, `kata-session-heartbeat`, warriors de release); (vii) front-matter exemplo inclui `branch`, `worktree`, `claude_session`, `session_entrypoint`. Regra antiga `done → archived` removida (pasta `archived/` permanece como convenção de filesystem, não estado).
  - Antes: `status: pending | in-progress | done | archived | abandoned`
  - Depois: `status: todo | development | to review | review | to release | release | done` (com `abandoned` como terminal alternativo documentado fora do happy path; manter como valor aceito para planos descartados)
  - Atualizar diagrama de lifecycle:
    ```
    todo → development → to review → review → to release → release → done
                              ↘                ↘                ↘
                              abandoned (terminal alternativo, qualquer estágio)
    ```
    Semântica de cada estado:
    - `todo` — plano criado, Issue aberta, branch remota vinculada, ainda não começou.
    - `development` — Athena delegou e implementação está em andamento.
    - `to review` — PR aberto, esperando reviewer (humano ou Argos) pegar.
    - `review` — Argos (ou humano) está revisando ativamente.
    - `to release` — review aprovou, esperando o agente de release iniciar.
    - `release` — release em execução (tag/build/deploy).
    - `done` — release completo, PR mergeado, ciclo encerrado.
  - Remover regra "`done` ou `abandoned` plans MUST be moved to `archived`" — a pasta `archived/` vira convenção de organização (filesystem hygiene), não estado.
  - **Adicionar nova Regra "Owner do `— → todo`: warrior-eunomia":** a criação de plano + Issue + branch remota é responsabilidade de `warrior-eunomia` (criada neste plano nos Steps Eunomia-1..7). A regra textual:
    > Todo plano (top-level ou subtask) DEVE ser criado por `warrior-eunomia` via `kata-plan-task` (top-level) ou `kata-create-subtasks` (subtask, downstream de Athena Phase 4). Eunomia executa os 5 passos antes de marcar `status: todo` como definitivo:
    > 1. Abrir a Issue correspondente (per `lex-issue-first` e `lex-issue-quality`).
    > 2. Verificar Issue Type pós-criação (per `lex-issue-type-verified`, criado neste plano).
    > 3. Criar a branch remota e vinculá-la à Issue via `gh issue develop {N} --base main --name {type}/{N}-{slug} --checkout` (registra a branch como "Development" na sidebar do GitHub).
    > 4. Criar a worktree per `lex-git-worktrees`.
    > 5. Registrar o número da Issue no front-matter (`issue:`) e o nome da branch nas Steps. Sem essa amarração, o plano permanece em rascunho — não pode ser apresentado como `todo` ao usuário.

    Fallback: enquanto Eunomia não estiver shipada (este Step 1 inclusive), a responsabilidade recai no agente da sessão corrente (Claude Code) seguindo o mesmo contrato — sem refatoração subsequente.
  - Adicionar tabela "Owner de cada transição":

    | Transição | Owner | Gatilho |
    |---|---|---|
    | `— → todo` | `warrior-eunomia` | Cria plano + abre Issue + `gh issue develop` + worktree (top-level OU subtask via Athena Phase 4) |
    | `todo → development` | `warrior-athena` | Phase 4 (delegação de implementação) |
    | `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR |
    | `to review → review` | `warrior-argos` | Argos inicia ciclo de revisão automatizada |
    | `review → to review` | `warrior-argos` | Argos termina ciclo sem aprovar (changes-requested ou awaiting-human) |
    | `to review → to release` | `warrior-athena` | Humano aprova PR (loop de wake-up detecta `APPROVED`) |
    | `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano de bump/changelog |
    | `release → done` | `warrior-janus` | `kata-release-publish` conclui (tag empurrada, `validate-tag.yml` passa, Release criada); notificação via MCP em `notifications.channels.release_notify` |
    | `qualquer → abandoned` | criador ou owner atual | Plano descartado |

  - Adicionar referência a labels da issue (Step 5).

- [x] **Step 4 — Atualizar `codex-agent-planning` nas 3 línguas.** Refletir todas as mudanças do Lexis no manual operacional. Atualizar exemplos. Sincronizar `.claude/`/`.cursor/` via `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor` (per memory `reference_install_py_self_sync`).

  **Concluído em 2026-05-11 (conteúdo dos 3 manuais reescritos; sync `.claude/` + `.cursor/` será feito após o commit dos Steps 3 + 4 + ADR).** Os 3 arquivos `framework/{pt-BR,es,en}/_foundation/process/codex/codex-agent-planning.md` foram reescritos com: (i) template de plano exemplificado com front-matter completo (issue + branch + worktree + sessão) — plan-043 como exemplo; (ii) seção §4 ciclo de vida unificado com tabela de status × owner; (iii) seção §5 owners por transição em formato de fluxo; (iv) seção §6 detalhando os 5 passos canônicos de `— → todo` com Lex de referência; (v) seção §8 grafo de relação Issue ↔ PR ↔ Plan ↔ ADR ↔ Heartbeat; (vi) seção §9 documentando o loop 3×15min de revisão pendente (sub-ciclo Argos `to review ↔ review`); (vii) §10 boas práticas atualizadas com "sincronizar `status:` em três lugares"; (viii) subpastas filesystem `{plans}/todo/` (antes `pending/`) e `{plans}/archived/` documentadas como convenção de organização, não estado.

- [x] **Step 5 — Labels canônicos no GitHub.** Decidir entre dois caminhos:

  **Concluído em 2026-05-11.** Opção (b) adotada — novo `lex-issue-status` independente (3 línguas). Entry adicionada em `framework/platforms.yaml`. Script idempotente `scripts/bootstrap_status_labels.sh` criado e executado contra `guardiatechnology/ahrena`: as 7 labels (`status: todo`/`development`/`to review`/`review`/`to release`/`release`/`done`) estão presentes no repositório com cores e descrições canônicas. Label `status: todo` aplicada a Issue #90 (validação do contrato). Ortogonalidade explícita com `pending-spec`/`spec-ready` (plan-038) documentada na Regra 4. Epic isento de `status:*` por Regra 5. HARD-GATE per `lex-hard-gate-pattern` com 5 preconditions + mutex enforcement.
  - **(a)** Estender `lex-issue-quality` com seção "Status labels canônicos" + tabela das 7 labels obrigatórias por fase.
  - **(b)** Criar novo `lex-issue-status` independente, mais coeso, e referenciá-lo em `lex-issue-quality` e `lex-pr-quality`.
  - **Recomendado:** (b) — separa o domínio "qualidade do conteúdo da issue" do domínio "ciclo de vida". Manter (a) como referência cruzada.
  - Em ambos os casos: registrar entry em `framework/platforms.yaml` (per `lex-platforms-rules`) e propagar 3 línguas.
  - Documentar criação inicial das labels via `gh label create` (script idempotente em `scripts/` ou kata dedicado — avaliar criar `kata-bootstrap-status-labels`).
  - **Coexistência com labels de plan-038** (`pending-spec`, `spec-ready`): documentar explicitamente que `status:*` é ortogonal a essas labels — `pending-spec`/`spec-ready` controlam entrada no fluxo Athena (US-child); `status:*` controla o ciclo dentro/após Athena. US-child nasce com `pending-spec` **sem** `status:*`; ao receber `spec-ready` (pelo PM), recebe `status: todo`. Bug/Tech-task pulam `pending-spec` e nascem com `status: todo` direto.

- [x] **Step 6 — Notification provider via MCP + schema em `.directives` (provider-agnóstico).**

  **Concluído em 2026-05-11.** (6a) `notifications:`, `pm:` e `session_tracking:` adicionados ao `framework/.directives.sample` (commentados como defaults documentados); chaves listadas em `lex-directives` (3 línguas) na tabela "Aplicação por seção". (6b) `framework/mcp/slack.json` criado com transporte tier-1 HTTP (`https://mcp.slack.com/mcp`) + OAuth 2.0 confidencial; validado contra `https://docs.slack.dev/ai/slack-mcp-server/` (per memory `feedback_validate_via_official_docs`). (6c+6d) `codex-notifications` criado em 3 línguas como manual cross-provider (provider-agnóstico); mapeia `notifications.provider` → tool MCP correspondente; documenta fluxo canônico de publicação, templates de mensagem (PR timeout, release, plans digest), e procedimento de troca de provider em 3 passos. (6e) `codex-mcp-slack` criado em 3 línguas como manual do provider inicial (paralelo a `codex-mcp-{github,notion,figma}`); cita `slack_send_message` como tool primária e mapeamento canal lógico → canal real. Entries adicionadas em `framework/platforms.yaml`.

  **Princípio orientador:** Lexis, Codex, Warriors e Katas **não devem mencionar Slack (ou Discord, Teams, etc.) por nome**. Devem referenciar apenas o **"MCP de notificação"** configurado em `.directives`. O provider concreto (Slack hoje; Discord/Teams/outros amanhã) é detalhe de implementação — vem de configuração + MCP server correspondente.

  **6a — Schema `notifications:` em `.ahrena/.directives`:** adicionar nova seção ao `.directives.sample` (per `lex-directives` regra 5 — extensibilidade):
  ```yaml
  notifications:
    # MCP provider responsável pelo envio das notificações.
    # Valores aceitos: slack | discord | teams | none
    # O servidor MCP correspondente deve estar listado em mcp.servers e ativo.
    provider: slack

    # Canais lógicos por evento. Nome no provider (ex.: "notifications-gh-pull-request" no Slack,
    # ID de canal no Discord, nome de team channel no Teams). Sem prefixo ('#', '@').
    channels:
      pr_review_timeout: "notifications-gh-pull-request"  # Athena: PR sem aprovação após N ciclos
      release_notify: "notifications-gh-releases"          # Janus: release concluída
      plans_status: "notifications-plans-status"           # Eunomia: digest de planos ativos

    # Horário útil para publicação de digests não-críticos (Eunomia modo PM).
    # Stalled crítico bypassa esta janela.
    working_hours:
      start: "07:00"
      end: "22:00"
      timezone: "America/Sao_Paulo"

  pm:
    loop_interval_minutes: 15      # Cadência do loop PM de Eunomia
    stalled_threshold_hours: 4     # Marca plano como stalled
    critical_stalled_hours: 24     # Bypassa horário útil para alertar
  ```
  - **Atualizar `framework/.directives.sample`** com `notifications:` + `pm:` (defaults documentados).
  - **Atualizar `lex-directives`** (3 línguas) na tabela "Application por seção" com entries genéricos: `notifications.provider`, `notifications.channels`, `notifications.working_hours.*`, `pm.*`. **Não mencionar Slack** — só "MCP provider de notificação".

  **6b — MCP server do provider Slack (implementação inicial):** Criar `framework/mcp/slack.json` per `lex-mcp` regra 5 (preferência de transporte: HTTP > binário > npx). Este é o **primeiro provider implementado**; outros (`discord.json`, `teams.json`) entram em planos futuros sem alterar o contrato de Lexis/Codex/Warrior.
  - **Referência oficial:** https://slack.com/intl/pt-br/help/articles/48855576908307 (Guia do servidor MCP do Slack). Validar transporte HTTP nativo + autenticação (provavelmente OAuth-per-user paridade com Notion). Usar como source of truth para tooling names, endpoints e fluxo de auth — sem inferir.
  - Validar transporte HTTP oficial conforme o guia; senão fallback npx + `requires: ["bin:node"]`.
  - **Criar `codex-mcp-slack`** (3 línguas) como manual do **provider específico**, paralelo a `codex-mcp-github`, `codex-mcp-notion`, `codex-mcp-figma`. Esse codex menciona Slack porque é o codex desse provider — paralelo legítimo aos outros codex-mcp-*. Lista as ferramentas (`slack_send_message`, etc. conforme o guia oficial), parâmetros, e como o canal lógico (`notifications.channels.plans_status`) mapeia para nome real Slack. Cita o link oficial como referência primária.
  - Adicionar nota em `codex-mcp-common` sobre o novo provider.
  - Não modificar `mcp.servers` automaticamente — usuário ativa via `make mcp-enable SERVER=slack`.

  **6c — Abstração de envio:** Lexis/Codex genéricos (`lex-agent-planning`, `codex-agent-planning`, warriors Eunomia/Athena/Janus) referenciam apenas:
  - "Publica notificação via MCP de notificação configurado em `notifications.provider`".
  - "Canal `notifications.channels.{plans_status|pr_review_timeout|release_notify}`".
  - Não citam `slack_send_message`, `#notifications-gh-...`, ou nome Slack diretamente. Citam apenas chaves abstratas + a referência genérica ao MCP.

  **6d — Procedimento operacional documentado em codex (não em Lexis):** criar `codex-notifications` (3 línguas) — manual genérico que descreve:
  - Como ler `notifications.provider` + `notifications.channels.{key}` de `.directives`.
  - Como mapear `provider` → tool MCP correspondente (Slack → `slack_send_message`; Discord → `discord_post_message` quando implementado; etc.).
  - Como cair em fallback se `provider == none` ou MCP indisponível (log warning, prosseguir).
  - Lista de canais lógicos disponíveis + qual warrior os consome.
  - Esse codex é o **ponto único** onde Slack-specifics são citados em conjunto com Discord/Teams futuros — `codex-mcp-slack` complementa com profundidade do provider, mas `codex-notifications` é o entrypoint cross-provider.

  **6e — Consumidores:**
  - Athena (Step 8) lê `notifications.channels.pr_review_timeout` ao esgotar N ciclos; envia via MCP de `notifications.provider`.
  - Janus (plan-045 → plan-027) lê `notifications.channels.release_notify` ao concluir publish.
  - Eunomia (plan-044) lê `notifications.channels.plans_status` + `notifications.working_hours.*` + `pm.*` no `kata-plans-status-digest`.

  **Vantagens:**
  - Troca de provider = editar `.directives` + ativar novo MCP server. Zero mudança em Lexis/Codex/Warriors.
  - Lexis/Codex envelhecem bem (não ficam "amarrados" a Slack).
  - Suporta multi-workspace / multi-org sem fork.

- [x] **Step 7 — Session tracking infrastructure (heartbeat + PR trace).** Estabelecer rastreamento de qual sessão Claude Code está executando cada plano, com persistência no body do PR.

  **Concluído em 2026-05-11.** (7.1) `codex-session-tracking` criado nas 3 línguas com schema do heartbeat JSON, cadência, multi-sessão/handoff, limpeza pós-merge. (7.2) `kata-session-heartbeat` criado nas 3 línguas em `_foundation/process/katas/` com workflow idempotente (escrita atômica via `mv`, no-op fora do Claude Code). (7.3) `lex-agent-planning` já carrega `claude_session` + `session_entrypoint` no front-matter exemplo (Step 3). (7.4) `lex-pr-quality` estendida nas 3 línguas com regras (i) label `status: <name>` e (j) seção "Session Trace" obrigatória; HARD-GATE atualizado. (7.5) `kata-pr-prepare` atualizada nas 3 línguas com Passo 5b (construir Session Trace) e Passo 6b (aplicar `status: to review` na transição `development → to review` com sync trifecta plano+Issue+PR). (7.6) `.gitignore` ganha `.ahrena/workflow/sessions/`. (7.7) `session_tracking:` adicionado em `framework/.directives.sample` (Step 6). (7.8) `codex-session-tracking` registrado em `framework/platforms.yaml`. `.claude/` + `.cursor/` regenerados via `scripts/install.py --self`.

  **Princípio:** Claude Code expõe `CLAUDE_CODE_SESSION_ID` (UUID estável por sessão) + `CLAUDE_CODE_ENTRYPOINT` (claude-vscode | claude-cli | claude-desktop | claude-web) + `AI_AGENT` (versão). Eunomia, Athena, Argos, Janus e qualquer agente que opere um plano DEVE escrever/atualizar um heartbeat local + registrar a trilha de sessões no body do PR ao abrir.

  **7.1 — Novo `codex-session-tracking` (3 línguas).** Path: `framework/{lang}/_foundation/process/codex/codex-session-tracking.md`. Manual define:
  - **Schema do heartbeat file:** `.ahrena/workflow/sessions/<session-id>.json`:
    ```json
    {
      "session_id": "85846253-4edf-443d-b294-187ef287d1bb",
      "entrypoint": "claude-vscode",
      "agent_version": "claude-code_2-1-138_agent",
      "plan_id": "043",
      "branch": "feat/N-slug",
      "cwd": "/Users/.../worktrees/N-slug",
      "started_at": "2026-05-11T12:30:00Z",
      "last_heartbeat": "2026-05-11T12:45:00Z",
      "last_activity": "kata-plan-task:step5"
    }
    ```
  - **Cadência:** heartbeat atualizado a cada operação significativa do agente (transição de status, conclusão de Step, fim de kata). Cadência mínima recomendada: a cada 5–10min de atividade. Stale threshold: 30min sem heartbeat → sessão considerada offline.
  - **Limpeza:** ao mover plano para `done|abandoned`, remover heartbeat file. Ao reiniciar sessão (entrypoint detecta heartbeat preexistente com mesmo session_id), continuar do existente (não recriar).
  - **Diretório gitignored:** `.ahrena/workflow/sessions/` em `.gitignore`. Conteúdo é runtime-only; persistência canônica vai para o PR body (item 7.4).
  - **Multi-sessão por plano:** quando uma sessão cede o trabalho (handoff), o sucessor cria novo heartbeat e marca `previous_session: <UUID>` no JSON. PM digest mostra cadeia.

  **7.2 — Novo `kata-session-heartbeat` (3 línguas).** Path: `framework/{lang}/_foundation/process/katas/kata-session-heartbeat.md`. Procedimento:
  - Lê env vars (`CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_ENTRYPOINT`, `AI_AGENT`).
  - Lê plan_id + branch do contexto invocador.
  - Escreve/atualiza `.ahrena/workflow/sessions/<session-id>.json` com timestamp atual.
  - Idempotente: pode rodar 100×/dia sem efeito colateral.
  - **Quem invoca:**
    - Eunomia em `kata-plan-task` (modo top-level) e `kata-create-subtasks` (modo subtask) — registra início.
    - Eunomia em `kata-plans-status-digest` — refresh a cada tick PM.
    - Athena em cada transição de status (`todo → development`, `development → to review`, `to review → to release`) — refresh + last_activity.
    - Argos em `cry-review-pr` — refresh + last_activity.
    - Janus em `kata-release-prepare` / `kata-release-publish` — refresh.

  **7.3 — Extensão de `lex-agent-planning` (3 línguas; já editado em Step 3).** Adicionar à Regra de owner do `— → todo`:
  - Eunomia escreve no front-matter do plano `claude_session: "<short-uuid>"` + `session_entrypoint: "<entrypoint>"` no momento da criação.
  - Athena ao mover `todo → development` atualiza `claude_session` se assumir o trabalho (handoff de Eunomia para Athena).
  - Campo opcional `session_history` no front-matter: lista de objetos `{session, role, started_at}` quando há múltiplos handoffs.

  **7.4 — Extensão de `lex-pr-quality` (3 línguas).** Adicionar nova seção obrigatória ao body do PR: **"Session Trace"**. Formato:
  ```markdown
  ## Session Trace

  | Session | Entrypoint | Role | Started | Last Heartbeat |
  |---|---|---|---|---|
  | `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |
  | `abc12345` | claude-cli | reviewer (Argos) | 2026-05-11T13:45Z | 2026-05-11T13:55Z |

  - Plan(s): plan-043
  - Worktree: `.worktrees/87-...`
  - Cumulative active time: ~1h30min
  ```
  - Seção obrigatória em todo PR aberto pela cadeia Athena/Eunomia/Janus.
  - Em PRs de hotfix manual (humano sem agente), seção pode ser `_(human-driven; no session trace)_`.
  - **HARD-GATE:** PRs sem "Session Trace" são rejeitados em Gate 2 (per `kata-quality-gate`) quando o branch tem heartbeat files associados.

  **7.5 — Atualizar `kata-pr-prepare` (3 línguas).** Adicionar passo:
  - Lê todos `.ahrena/workflow/sessions/*.json` filtrados por `branch == current_branch`.
  - Constrói tabela "Session Trace" ordenada por `started_at`.
  - Calcula `cumulative_active_time` (soma dos intervalos `started_at → last_heartbeat` por sessão).
  - Insere seção no body do PR antes de "Test plan" e depois de "Summary".
  - **Cumulative active time** é uma métrica complementar ao `cry-pr-cost-stamp` (plan-007, archived) — não substitui custo em tokens; mede tempo de sessão real.

  **7.6 — Atualizar `.gitignore`.** Adicionar `.ahrena/workflow/sessions/` (heartbeat dir é runtime-only; histórico persiste no PR body).

  **7.7 — Atualizar `framework/.directives.sample`:** adicionar seção `session_tracking:`:
  ```yaml
  session_tracking:
    enabled: true                          # global on/off
    heartbeat_dir: ".ahrena/workflow/sessions"
    stale_threshold_minutes: 30            # PM considera offline após este intervalo
    pr_trace_required: true                # Gate 2 rejeita PR sem "Session Trace"
  ```

  **7.8 — Registrar em `framework/platforms.yaml`:** entry `cursor.rules` para `_foundation/process/codex/codex-session-tracking` (Codex; Lex não criamos — só extensões a `lex-agent-planning` e `lex-pr-quality`).

- [ ] **Step 8 — Eunomia (delegado a plan-044).** A criação de `warrior-eunomia`, `kata-create-subtasks`, atualização de `kata-plan-task`, novos cries (`cry-create-subtasks`, `cry-plan-task`, `cry-status-digest`), kata `kata-plans-status-digest`, template `subtask.yml`, `lex-issue-type-verified`, e updates de `kata-contributing-issue` + `lex-issue-quality` saíram deste plano e viraram **plan-044** (`warrior-eunomia-plan-and-subtask-creator`). Plan-043 apenas:
  - **Referencia Eunomia** em `lex-agent-planning` (Step 3) e na tabela de owners — sem criar o warrior.
  - **Coordena dependência:** plan-044 depende de plan-043 (status system + label `status: todo` + session tracking infrastructure existem); Athena (Step 9) invoca Eunomia que será criada em plan-044. Enquanto plan-044 não shippar, agente da sessão atua manualmente nos 5 passos seguindo o mesmo contrato (zero refatoração subsequente).
  - Plan-044 absorve o consumo das heartbeat files no `kata-plans-status-digest` (digest enriquecido com sessões ativas).
  - **Não há trabalho de Step 8 a fazer dentro de plan-043** — esta entrada é só um pin documental confirmando a delegação.

- [x] **Step 9 — Atualizar `warrior-athena`.** Adicionar à seção "Responsibilities" e/ou "Workflow":

  **Concluído em 2026-05-11.** Athena (3 línguas) ganhou: (i) 4 novos bullets em "Faz" — transições de status (per `lex-agent-planning`), loop 3×15min, invocação de Eunomia em Phase 4 com max-laggard, heartbeat de sessão; (ii) `lex-agent-planning` + `lex-issue-status` adicionados na tabela Lexis; (iii) `codex-agent-planning` + `codex-notifications` + `codex-session-tracking` adicionados na tabela Codex; (iv) `kata-pr-prepare` anotado com "aplica `status: to review` (Passo 6b)" + `kata-session-heartbeat` adicionado; (v) tabela Warriors delegados ganhou Eunomia, Argos, Janus; (vi) nova subseção "Loop de Revisão Pendente" descrevendo o algoritmo 3×15min canônico (5 ramos de saída).
  - Quando inicia Phase 4 (delegação de implementação): muda `status:` do plano para `development` e aplica label `status: development` na issue via `gh issue edit --remove-label "status: todo" --add-label "status: development"`.
  - **Phase 4 + Eunomia (coordenação com plan-038):** ao entrar em `development`, Athena invoca `warrior-eunomia` para decompor a child Issue em sub-issues. Cada sub-issue criada por Eunomia nasce com seu próprio `status: todo` e roda o ciclo completo independente. O child Issue permanece em `development` enquanto ≥1 sub-issue não atingiu `done`. Cálculo de estado agregado (preferência registrada na Open Question #6):
    - child `status: development` ← ≥1 sub-issue não-`done`.
    - child `status: to review` ← todas sub-issues em `to review`/`to release`/`release`/`done`.
    - child `status: to release` ← todas sub-issues em `to release`/`release`/`done`.
    - child `status: done` ← todas sub-issues em `done`.
    - Athena recalcula a label do child a cada transição de sub-issue.
  - Quando abre PR (Phase 7 — `kata-pr-prepare`): plano → `to review`, issue → `to review`, PR também recebe label `status: to review`. (Para sub-issues: cada PR de subtask carrega a label da sua própria sub-issue, não do child.)
  - Quando recebe sinal de PR aprovado por humano (via `gh pr view --json reviewDecision`): plano → `to release`, issue → `to release`.
  - **Loop de revisão pendente (estado `to review`):** ao abrir o PR, agenda o primeiro check via `ScheduleWakeup` em 15 min. A cada wake-up:
    1. Consulta `gh pr view {N} --json reviewDecision,reviews` e `gh pr checks {N}`.
    2. Se `reviewDecision == APPROVED` por humano → move para `to release` e sai do loop.
    3. Se `reviewDecision == CHANGES_REQUESTED` → atualiza plano com nota, ping no PR via `gh pr comment`, mantém em `to review` (autor entra em ação), sai do loop.
    4. Se Argos publicou comentário com findings P0/P1 → mantém em `to review` (aguarda autor corrigir); sai do loop e re-agenda quando Argos sinalizar nova rodada.
    5. Caso contrário (`REVIEW_REQUIRED` / `null`, sem aprovação humana) → conta ciclo; se < 3, reagenda 15 min; se == 3, dispara notificação via MCP em `notifications.channels.pr_review_timeout` (invocando abstração de `codex-notifications`) com link do PR + lista de reviewers solicitados + nº do PR, e encerra o loop.
  - Documentar contrato com Argos (Step 10) — Athena escuta o sinal humano final; Argos opera o sub-ciclo `to review ↔ review` automatizado, intercalado com a janela de espera do Athena.
  - Phase 1: Athena rejeita Issue Type Epic (regra introduzida por plan-038) e rejeita US-child sem `spec-ready` (também plan-038). Plan-043 estende: Phase 1 aplica `status: todo` se a Issue passa em todos os gates de 038 (Issue Type aceitável, `spec-ready` quando aplicável); rejeita aplicação da label se Issue não passa.

- [x] **Step 10 — Atualizar `warrior-argos`.** Adicionar à seção "Responsibilities":

  **Concluído em 2026-05-11.** Argos (3 línguas) ganhou: (i) novo bullet em "Faz" descrevendo o sub-ciclo `to review ↔ review` (entrada, saída em changes-requested, saída em "approves awaiting human"); (ii) novo bullet "Atualiza heartbeat de sessão" via `kata-session-heartbeat`; (iii) novos bullets em "Não Faz" — não move para `to release` (exclusivo de Athena) e não dispara notificação ao final (exclusivo de Athena ao esgotar 3 ciclos); (iv) `lex-agent-planning` e `lex-issue-status` adicionados na tabela Lexis; (v) descrição de `lex-pr-quality` atualizada para incluir "label `status:*` e seção Session Trace".
  - Quando recebe trigger de revisão (Cry `cry-review-pr` ou invocação pós-Athena): confirma que PR está em `to review`. **Move plano + issue + PR de `to review` → `review`** (label `status: review`) sinalizando que a revisão automatizada está em andamento.
  - **Sub-ciclo `to review ↔ review`:** Argos roda os kata-reviews em sequência (Python review, frontend review, security review, etc.). Ao final de cada ciclo de revisão automatizada:
    1. Publica comentário no PR resumindo achados.
    2. Se há findings P0/P1 → marca o ciclo como `changes-requested`; **move plano + issue + PR de volta para `to review`** (aguarda autor corrigir); encerra o turno.
    3. Caso contrário → emite "Argos approves; awaiting human"; **move plano + issue + PR de volta para `to review`** (Athena retoma o loop de espera por aprovação humana); encerra o turno.
  - Argos nunca move para `to release` — esse passo é exclusivo do Athena ao detectar aprovação humana via `gh pr view`.
  - Argos não dispara notificação final via MCP — quem faz isso é o Athena ao esgotar os 3 ciclos. Argos apenas escreve no PR.

- [ ] **Step 11 — Janus wiring (delegado a plan-045 + plan-027).** As transições `to release → release → done` e a notificação via MCP em `notifications.channels.release_notify` são responsabilidade de `warrior-janus` (entregue por plan-027) com as extensões E1/E2/E3 documentadas em plan-045. Plan-043 apenas:
  - **Referencia Janus** em `lex-agent-planning` (Step 3) e na tabela de owners — sem criar o warrior nem as katas de release.
  - **Coordena dependência:** plan-045 (pointer) garante que plan-027 absorva E1 (queue discovery por label `status: to release`), E2 (transições de label durante publish), E3 (notificação via MCP em `notifications.channels.release_notify`). Plan-043 não duplica o conteúdo.
  - **Não há trabalho de Step 10 a fazer dentro de plan-043** — esta entrada é só um pin documental confirmando a delegação. O contrato Janus↔ciclo de status é detalhado em plan-045.

- [x] **Step 12 — Migrar planos existentes.** Para cada arquivo em `.claude/plans/`, `.claude/plans/pending/` e `.claude/plans/archived/`:

  **Concluído em 2026-05-11.** `scripts/migrate_plan_status.py` criado como script idempotente (Python) com mapping `pending → todo`, `in-progress → development`, `archived → done` (semântica nova: `archived/` vira só convenção de filesystem). Executado contra `.claude/plans/` do worktree: 9 planos migrados (plan-001/002/003/004/009 `archived → done`; plan-021/040/043 `in-progress → development`; plan-026 `pending → todo`); 11 já canônicos (incluindo 9 em `archived/` com `status: done` correto e plan-044/045 já em `status: todo`). Cada migrado teve `updated_at` reescrito para o agora UTC. **Folder rename `pending/ → todo/` é no-op neste worktree** — a pasta `pending/` só existe nos staged changes do checkout `main` (não commitados); o rename canônico acontece num PR de cleanup quando essas movimentações forem commitadas (ou via `git mv` direto no checkout main por quem resolver aquele staged set). Per `codex-agent-planning` §1, a pasta `todo/` é a convenção canônica daqui pra frente.
  - `status: pending` → `status: todo`
  - `status: in-progress` → `status: development` (sem distinção retroativa entre `development` e os intermediários `to review`/`to release` — planos antigos não têm essa granularidade)
  - `status: done` (archived) → mantém `done`
  - `status: abandoned` → mantém `abandoned`
  - Bumpar `updated_at`.
  - **Decisão de filesystem:** renomear pasta `pending/` → `todo/`? Recomendação: **sim** (alinha nome ao status), com `git mv` para preservar histórico. `archived/` permanece (organização pós-merge).
  - Script de migração: criar `scripts/migrate_plan_status.py` (one-shot) que faz os renames de campo e (opcionalmente) o `git mv` da pasta. Rodar em commit dedicado para facilitar review.

- [ ] **Step 13 — Loops e notificações: validação operacional.**
  - Criar PR de teste (pode ser um chore mínimo) e simular: Athena abre PR, ScheduleWakeup dispara em 15 min, sem aprovação após 3 ciclos → notificação publicada via MCP no canal de homologação (`notifications.channels.pr_review_timeout`).
  - Simular release manual: aplicar label `status: done` e disparar notificação via MCP no canal de homologação (`notifications.channels.release_notify`).
  - Validar que Argos consegue rodar review em loop sem colidir com o wake-up do Athena (turnos intercalados).
  - Garantir que `ScheduleWakeup` respeita a janela útil (não acordar 3am).

- [ ] **Step 14 — Docs e exemplos.**
  - README (3 línguas) ganha 1 seção "Workflow status" listando os 7 status e as chaves de canal de notificação (`notifications.channels.*`) sem citar o provider concreto.
  - Atualizar `kata-plan-task` para refletir `todo` como status inicial **e codificar a sequência issue → `gh issue develop` → worktree → registrar issue/branch no plano** (espelha a nova Regra do Step 3).
  - Atualizar `kata-pr-prepare` para aplicar label `status: review` no PR ao abrir.
  - Atualizar `kata-pr-review` / `cry-pr-review` para Argos saber checar/mover labels.
  - Atualizar `cry-implement-issue` (orquestração Athena) documentando o loop.
  - Avaliar atualizar `lex-git-branches` ou `codex-git-workflow` para mencionar `gh issue develop` como caminho canônico de criação de branch (alternativa ao `git checkout -b` puro), garantindo o linkage Issue ↔ branch.

- [ ] **Step 15 — Commit, push, PR.** Commits atômicos (per `lex-small-commits`) agrupados por área: (a) Lexis/Codex framework provider-agnósticos, (b) Warriors Athena/Argos, (c) `.directives` schema + `codex-notifications` + `framework/mcp/slack.json` + `codex-mcp-slack` (provider inicial), (d) migração de planos existentes, (e) sync `.claude/`/`.cursor/`. PR descrevendo o novo ciclo, com `Closes #{N}` e label `status: review` na criação.

## Dependencies

- **plan-042** — `setup-preflight-and-mcp-enable` (concluído): provê `make mcp-enable SERVER=...` para ativar qualquer provider MCP de notificação via degrau correto (Slack como provider inicial; outros futuros).
- **plan-036** — `warrior-argos-pr-reviewer` (archived): Argos já existe; este plano só adiciona contrato de transição.
- **plan-027** — `warrior-janus-release-orchestrator` (pending, **acelerado para virar dependência hard de 043**): Janus é o agente de release. Plan-043 NÃO mergeia sem plan-027 mergeado. Plan-027 absorve 3 acréscimos antes do merge (ver "Extensões a plan-027" abaixo).
- **plan-007** — `pr-token-cost-stamp` (archived): Athena já tem hook pós-merge; não conflita.
- **plan-038** — `pm-topology-per-component-and-epic-decomposition` (pending, **reduzido após absorção de Eunomia em 043**): introduz labels paralelas (`pending-spec`, `spec-ready`), Calliope (Epic decomposition), Aglaea (UI PM), Eos (Jobs PM), Prometheus narrowing, e a regra Athena Phase 1 rejeita Epic. **Não mais bloqueante** para 043 — agora a relação é invertida (038 depende de 043).

## Coordenação com plan-038 (após absorção de Eunomia + lex-issue-type-verified)

Por decisão do usuário (2026-05-10), **Eunomia + `kata-create-subtasks` + `cry-create-subtasks` + template `subtask.yml` + `lex-issue-type-verified` foram absorvidos integralmente neste plano (Step 7)**, saindo do escopo de plan-038. Plan-038 fica reduzido a: Calliope (Epic decomposition), PM topology (Aglaea, Eos, Prometheus narrowing, Metis wiring), e os Lexis/Codex de spec por Component.

As peças de plan-038 que ainda tocam plan-043:

| Peça de plan-038 (reduzido) | Como entra em plan-043 |
|---|---|
| **Calliope** (Epic decomposition) | Plan-043 não toca Epic. Calliope cria child Issues; daí Eunomia (em 043) entra via Athena Phase 4 ou via `cry-plan-task` humano. Calliope referencia `lex-issue-type-verified` (criado em 043) para verificação programática de Issue Type. |
| **Labels `pending-spec` / `spec-ready`** (gating pré-Athena por PM) | Não colidem com `status:*`. Vivem em namespaces diferentes: `pending-spec`/`spec-ready` controlam **entrada** no fluxo Athena (US child ainda precisa de spec do PM); `status:*` controla o **ciclo do plano/Issue durante e depois** do Athena. Coexistem na mesma Issue. **Refinamento explícito (Step 5 deste plano):** US-child criada por Calliope nasce com `pending-spec` **e sem `status:*`** — só recebe `status: todo` quando ganha `spec-ready` (transição feita pelo PM correspondente após produzir a spec). Bug/Tech-task pulam o gate de spec, recebem `status: todo` direto na criação. |
| **Athena Phase 1 rejeita Issue Type Epic** | Step 8 deste plano deixa explícito: Athena só aplica `status: todo → development` em child Issues (US com `spec-ready`, Bug, Tech-task). Epic nunca recebe `status:*` — tem ciclo próprio (Open Question #7). |
| **`kata-issue-analysis` (atualizada por 038)** | Step 13 deste plano evita duplicação: a regra "Athena rejeita Issue Type Epic + valida `spec-ready` em US-child" fica em 038; plan-043 só estende `kata-issue-analysis` para mapear o **estado inicial** da label `status:*` no fim da Phase 1. |
| **`Tracked by #N`** (sub-issue → child → Epic) | Step 8 usa para Athena calcular estado agregado do child a partir das subtasks (criadas por Eunomia em 043). Loop de espera (3×15min) opera no PR do child; subtasks têm loops próprios. |

### Itens que plan-038 deve **remover** do seu escopo (cleanup)

Como Eunomia foi absorvida em 043, o PR de plan-038 deve **NÃO criar** os seguintes artefatos (eles são criados em 043):
- `warrior-eunomia`
- `kata-create-subtasks`
- `cry-create-subtasks`
- Template `subtask.yml`
- `lex-issue-type-verified`

Em plan-038, atualizar:
- Remover Steps 19, 20, 21, 22, 23 (referentes a Eunomia + Lexis).
- Manter Step 29 (atualizar warrior-athena) mas com referência: "Phase 4 invoca Eunomia (criada em plan-043)".
- AC-5, AC-15, AC-16, AC-17 viram referências a plan-043 (não objetivos próprios de 038).
- Calliope (que cria Issues programaticamente) continua referenciando `lex-issue-type-verified` — mas agora a Lex está em 043, não 038.

### Ordem de merge sugerida (após split em 043 + 044 + 045)

1. **plan-027** — Janus + lex-annotated-tags + katas release-prepare/publish + cry-release + workflow validate-tag.yml. Idealmente já com extensões E1/E2/E3 absorvidas (Cenário A de plan-045).
2. **plan-043** — este plano (status core: lex-agent-planning + codex + lex-issue-status + labels + `notifications` schema em `.directives` + `codex-notifications` + primeiro MCP de notificação (Slack como provider inicial) + Athena/Argos wiring + loops + migração).
3. **plan-044** — Eunomia (warrior + katas + cries + template + lex-issue-type-verified + updates de kata-contributing-issue + lex-issue-quality).
4. **plan-045** — Janus pointer/wiring. Cenário A: vira acta de coordenação (sem PR próprio). Cenário B: PR follow-up adicionando E1/E2/E3 a plan-027 já mergeado.
5. **plan-038 (reduzido)** — Calliope + PM topology (Aglaea, Eos, Prometheus narrowing, Metis wiring). Depende de plan-044 (lex-issue-type-verified + Eunomia para Athena Phase 4).

**Inversão em relação à versão anterior do plano:** antes plan-038 vinha antes de plan-043 porque 043 dependia da Lex de 038. Agora plan-043 vem antes porque Eunomia + Lex moveram para cá. 038 (reduzido) consome 043.

## Risks

- **Renomear pasta `pending/` → `todo/` quebra referências.** Mitigação: grep cruzado por `plans/pending` em todo o repo antes do `git mv`; atualizar todas as referências no mesmo commit. Verificar `install.py`, `scripts/`, docs.
- **Argos e Athena podem entrar em conflito de loop** (ambos agendam wake-ups na janela `review`). Mitigação: Athena só agenda quando Argos sinaliza "human-pending"; Argos limpa seu próprio agendamento ao terminar. Documentar explicitamente o contrato no Step 7/8.
- **MCP do provider inicial (Slack) pode não ter HTTP oficial hoje.** Mitigação: validar via guia oficial (https://slack.com/intl/pt-br/help/articles/48855576908307); fallback npx é aceito (Figma já segue esse caminho); decisão registrada no JSON com `_comment` per `lex-mcp` regra 5. Validar antes de codificar (per memory `feedback_validate_via_official_docs`).
- **Aplicar labels via `gh issue edit` exige labels pré-existentes.** Mitigação: Step 5 inclui kata/script idempotente para criar as 5 labels no setup do repo.
- **`abandoned` removido do enum quebra planos legados.** Mitigação: manter `abandoned` como valor terminal aceito (fora do happy path), documentado explicitamente. Migração do Step 10 preserva o valor.
- **3 ciclos de 15 min (=45min) podem ser curtos demais** para revisão humana fora do horário de trabalho. Mitigação: documentar como configurável via `.ahrena/.directives` (chave `workflow.review_loop.cycles` e `workflow.review_loop.interval_minutes`); o padrão são 3×15min, mas o time pode subir para 5×60min.
- **Notificações via MCP podem virar ruído** se muitos PRs ficarem parados. Mitigação: alerta só dispara no esgotamento dos 3 ciclos (não em cada ciclo); inclui contexto suficiente (autor, reviewers, link) para o canal agir; rate-limit implícito pela janela de 45min mínimo. Independe do provider.
- **`gh issue develop` exige permissão de escrita no repo** e que a Issue exista. Mitigação: a ordem do Step 1 garante issue antes de branch; falha de permissão é catchada e reportada ao usuário sem mascarar (não cair em `git checkout -b` silencioso que perderia o linkage).
- **7 estados podem parecer excessivos para PRs triviais.** Mitigação: a transição `to review → review → to review` é toda automatizada por Argos (custo zero para humano); `to release → release → done` é uma sequência de label updates do agente de release. O humano percebe três marcos relevantes: `to review` (aprovar), `to release` (release pendente), `done` (encerrado). Os intermediários `development`/`review`/`release` sinalizam "alguém está trabalhando agora", úteis para auditoria e para evitar dupla-revisão / dupla-release.
- **Eunomia gera subtasks excessivamente granulares (1 PR por linha) ou grosseiras demais (1 subtask = US inteira).** Mitigação: critério de granularidade em `kata-create-subtasks` (cada subtask cabe em 1 PR per `lex-small-commits`, tem entrega independente). Athena revisa lista antes de iniciar implementação; rejeita decomposição imprópria e re-invoca Eunomia.
- **Issue Type não atribuído após criação programática** (race condition GitHub API). Mitigação: `lex-issue-type-verified` força verificação `gh api` pós-criação; retry automático até 3 tentativas com backoff exponencial. Falha persistente bloqueia o fluxo e exige intervenção.
- **Subtask plan no body fica grande demais** (perde legibilidade). Mitigação: critério "grande" definido (>50 linhas markdown OU >5 steps) força anexo em `.ahrena/workflow/issue-{n}/subtasks/sub-{NN}-{slug}.md` + resumo no body. `kata-create-subtasks` aplica regra automaticamente.
- ~~Escopo de plan-043 cresceu significativamente após absorção de Eunomia.~~ **Resolvido após split em plan-044 (Eunomia) e plan-045 (Janus pointer).** Plan-043 ficou focado em status core + Athena/Argos + `.directives` notifications schema + primeiro MCP provider.

## Open Questions (resolver antes de Step 1)

1. **Pasta `pending/` → `todo/`?** Recomendação: sim (alinha nome e status). Custo: 1 `git mv` + grep cruzado.
2. **Novo Lexis `lex-issue-status` ou estender `lex-issue-quality`?** Recomendação: novo Lexis dedicado (Step 5b).
3. **Status `abandoned` permanece?** Recomendação: sim, como terminal alternativo documentado fora do happy path.
4. ~~**Quem move `release → done` enquanto Janus não existe?**~~ **Resolvido:** Janus é o agente de release (plan-027). Wiring com ciclo de status delegado a **plan-045** (pointer/extension de plan-027) — extensões E1/E2/E3 saíram de plan-043 e vivem em plan-045.
5. **Loop configurável?** Recomendação: sim, com defaults `cycles=3, interval=15min` (Risks).
6. **Agregação `status:*` entre child Issue e subtasks** (introduzida pela coordenação com plan-038): cada subtask roda seu ciclo independente; child agrega por estado dos filhos? Recomendação: sim, com regra "max-laggard" (estado do child = pior estado entre os filhos não-`done`). Alternativa simples: child fica em `development` até a última subtask mergear, então pula direto para `done`. Decidir antes do Step 7.
7. **Epic tem `status:*`?** Recomendação: **não**. Epic é decomposto por Calliope (plan-038) e não passa por Athena. Seu ciclo é "open / closed via Tracked-by children". Documentar explicitamente em `lex-issue-status` (Step 5) para evitar duplicação.
8. ~~**Plan-043 depende do merge de plan-038?**~~ **Resolvido pela absorção de Eunomia + Lex em 043:** ordem invertida — 043 sai antes; 038 (reduzido) depende de 043.
9. ~~**`cry-plan-task` nome final.**~~ **Delegado a plan-044** (Eunomia). Decidido lá.
10. ~~**Eunomia opera em modo top-level com confirmação humana ou autonomamente?**~~ **Delegado a plan-044** (Eunomia). Recomendação registrada lá: gate humano obrigatório no modo top-level.
