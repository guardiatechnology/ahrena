# Kata: Preparar Pull Request

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 7 do fluxo Issue-Driven — criação de branch, push dos arquivos e abertura de PR no GitHub via MCP, com body estruturado referenciando todos os artefatos do fluxo

## Objetivo

Após o Gate 2 resultar em `go`, criar a branch, fazer push dos arquivos modificados e abrir um Pull Request no GitHub via MCP. O body do PR é estruturado referenciando a issue original, os ACs numerados, os ADRs criados e os artefatos do fluxo em `.ahrena/issues/{n}/`. O resultado é um PR pronto para revisão humana, com rastreabilidade completa.

## Quando Usar

- Fase 7 (última) do fluxo orquestrado por `warrior-athena`, após `kata-quality-gate` resultar em `go`
- Quando é necessário submeter uma implementação validada para revisão via PR

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Número da issue | Sim | Número da issue original (ex.: `42`) |
| Repositório | Sim | `owner/repo` |
| Base branch | Não | Branch alvo do PR; padrão: `main` |
| Artefatos do fluxo | Sim | `.ahrena/issues/{n}/*` e `docs/adr/ADR-*` criados nas fases anteriores |
| Estratégia do PR | Não | `draft` (padrão: `false`) |

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições MCP e Gate 2
- [ ] 2. Determinar nome da branch e título do PR
- [ ] 3. Criar branch via GitHub MCP
- [ ] 4. Push dos arquivos modificados
- [ ] 5. Compor body do PR com referências
- [ ] 6. Criar PR linkado à issue
- [ ] 7. Atualizar status dos ADRs (proposed → accepted)
- [ ] 8. Atualizar checkpoint final
```

### Passo 1: Verificar pré-condições MCP e Gate 2

1. Confirmar que `github` está em `mcp.servers` (conforme `lex-mcp`). Se não, informar e encerrar.
2. Confirmar `GH_TOKEN` definida.
3. Ler `.ahrena/issues/{n}/06-quality-report.md` e confirmar resultado `go`. Se `no-go`, recusar criar PR e retornar ao orquestrador.
4. Consultar `codex-mcp-github` para identificar ferramentas corretas (`create_branch`, `push_files`, `create_pull_request`).

### Passo 2: Determinar nome da branch e título do PR

**Nome da branch** — convenção:

```
{tipo}/issue-{n}-{slug-curto}
```

Onde:
- `{tipo}` — extrair do brief da Fase 1 (seção "Tipo de trabalho"): `feat`, `fix`, `refactor`, `chore`
- `{slug-curto}` — do título da issue, convertido para kebab-case, limitado a ~40 chars

**Exemplo:** `feat/issue-42-add-refund-endpoint`

**Título do PR** — no formato de Conventional Commits:

```
{tipo}({escopo}): {descrição} (#{n})
```

Onde:
- `{escopo}` — módulo principal afetado (detectado via componentes da Fase 3)
- `{descrição}` — resumo curto da mudança

**Exemplo:** `feat(refunds): add refund creation endpoint (#42)`

### Passo 3: Criar branch via GitHub MCP

1. Invocar `create_branch` com:
   - `owner`, `repo`
   - `branch` — nome gerado no Passo 2
   - `from_branch` — base branch (`main` ou o configurado)
2. Se a branch já existir (de iteração anterior), saltar este passo.

### Passo 4: Push dos arquivos modificados

1. Executar `git diff --name-only {base}...HEAD` para listar arquivos tocados.
2. Para cada arquivo, ler conteúdo do working tree.
3. Invocar `push_files` com:
   - `owner`, `repo`, `branch` (criada no Passo 3)
   - `message` — mensagem de commit no formato Conventional Commits:
     ```
     {tipo}({escopo}): {descrição}

     Refs: #{n}
     ```
   - `files` — array de `{path, content}`
4. Se houver múltiplos commits lógicos (recomendado para PRs grandes), invocar `push_files` múltiplas vezes com mensagens distintas.

### Passo 5: Compor body do PR com referências

Estrutura:

```markdown
## Resumo

{1-2 parágrafos descrevendo a mudança, extraídos do brief e requirements}

Resolves #{n}

## Critérios de Aceitação

<!-- Copiados de .ahrena/issues/{n}/02-requirements.md -->

- [x] **AC-1:** {descrição}
- [x] **AC-2:** {descrição}
- [x] **AC-3:** {descrição}

## Arquitetura

Ver [documento de arquitetura](.ahrena/issues/{n}/03-architecture.md).

### ADRs criados

- [ADR-{n}: {título}](docs/adr/ADR-{n}-{slug}.md)

(omitir se não houve ADR)

## Qualidade

- ✅ Gate 2 aprovado ([relatório](.ahrena/issues/{n}/06-quality-report.md))
- ✅ Revisão de segurança aprovada ([relatório](.ahrena/issues/{n}/05-security-review.md))
- Cobertura: {atual}% (threshold: {threshold}%)

## Como testar

{Instruções extraídas do architecture-brief — como rodar, variáveis necessárias, cenários chave}

## Checklist de revisão

- [ ] ACs atendidos (verificar matriz de rastreabilidade no relatório do Gate 2)
- [ ] ADRs revisados (se aplicável)
- [ ] Testes executam localmente
- [ ] Documentação de uso atualizada (se aplicável)

## Session Trace

<!-- Construído pelo Passo 5b a partir de .ahrena/workflow/sessions/*.json
     filtrados por branch == {branch}. Obrigatório quando session_tracking.enabled
     == true e o branch tem heartbeat files. PRs human-driven podem usar a frase
     "_(human-driven; no session trace)_". Per lex-pr-quality e codex-session-tracking. -->

| Session | Entrypoint | Role | Started | Last Heartbeat |
|---|---|---|---|---|
| `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |

- Plan(s): plan-{M}-{slug}
- Worktree: `.worktrees/{N}-{slug}`
- Cumulative active time: ~Xh Ymin

---

🤖 Gerado pelo fluxo Issue-Driven Development do Ahrena (`warrior-athena`)
```

### Passo 5b: Construir a seção "Session Trace"

Per `lex-pr-quality` (regras 9, j) e `codex-session-tracking` §7, antes de invocar `create_pull_request` agregar todos os heartbeat files da branch corrente:

1. Verificar `session_tracking.enabled` em `.ahrena/.directives` (default `true`). Se `false`, pular este passo.
2. Resolver `session_tracking.heartbeat_dir` (default `.ahrena/workflow/sessions/`).
3. Listar `*.json` no diretório; filtrar pelos cujo `branch` coincide com a branch corrente (`git rev-parse --abbrev-ref HEAD`).
4. Ordenar por `started_at` ascendente.
5. Calcular `cumulative_active_time` = soma de `(last_heartbeat - started_at)` por sessão. Formatar como `~Xh Ymin`.
6. Construir tabela com colunas `Session` (UUID curto — primeiros 8 chars), `Entrypoint`, `Role`, `Started`, `Last Heartbeat`.
7. Inserir a seção no body do PR antes do bloco "🤖 Gerado...".
8. **PR sem heartbeats associados** (humano puro, sem agente Claude Code rodando): substituir a tabela pela frase canônica `_(human-driven; no session trace)_`.

Esta seção é métrica complementar ao `cry-pr-cost-stamp` (que mede tokens/USD). Aqui mede tempo de sessão real.

### Passo 5c: Flush do plano

Antes de invocar `create_pull_request`, garantir que o body da Issue reflete o estado atual do trabalho:

1. Invocar `kata-flush-plan-to-issue` passando o número da Issue.
2. O kata lê `.plans/{N}.md`, filtra blocos `<!-- not-flushed -->`, executa preflight de drift remoto, e grava o conteúdo filtrado no body da Issue via MCP `update_issue` (preferido) ou `gh issue edit --body-file` (fallback).
3. Em caso de drift remoto detectado (default `force=false`), o kata pausa e oferece merge manual — não prosseguir até resolução.

Esse passo substitui a mecânica antiga de "atualizar `status:` no front-matter do plano" (modelo legado pré-): no Issue-as-plan model, o body da Issue é o canonical; o cache local `.plans/{N}.md` é regenerável.

### Passo 6: Criar PR linkado à issue

1. Invocar `create_pull_request` com:
   - `owner`, `repo`
   - `title` — do Passo 2
   - `head` — nome da branch
   - `base` — branch alvo
   - `body` — do Passo 5
   - `draft` — conforme input (padrão `false`)
2. Capturar `html_url` do PR criado.
3. Se `Resolves #{n}` está no body, o GitHub linkará automaticamente a issue.

### Passo 6b: Aplicar `status: to review` (transição `development → to review`)

Per `lex-issue-status` Eixo A e `lex-agent-planning` Tabela A, ao abrir o PR Athena executa a transição `development → to review`:

```bash
# 1. PR — entra em "to review" imediatamente
gh pr edit {pr_number} --add-label "status: to review"

# 2. Issue — sincronizar (mutex intra-artefato)
gh issue edit {issue_number} \
  --remove-label "status: development" \
  --add-label "status: to review"
```

Per `lex-issue-status` Regra 3 (mutex intra-artefato), garantir que cada artefato fica com exatamente um `status:*`. Per Regra 5 (sync Issue↔PR), atualizar simultaneamente.

A label é a única fonte de truth do estado — o body da Issue (canonical do plano) já foi atualizado no Passo 5c.

### Passo 6c: Argos pre-flight cycles (até 3, interativos via AskUserQuestion)

Antes de cobrar reviewer humano, Athena oferece até **3 ciclos de review automatizada por Argos**. Cada ciclo é gateado por AskUserQuestion — Athena nunca invoca Argos sem confirmação do usuário. O propósito é elevar a qualidade do PR (resolver findings P0/P1) antes de tomar tempo do reviewer humano.

**Estado inicial:** PR aberto, label `status: to review` aplicada (per Passo 6b).

**Loop Argos (até 3 ciclos `A1, A2, A3`):**

Para cada ciclo `A{n}`:

1. Athena pergunta via `AskUserQuestion`:

   ```
   Athena: "Cycle A{n}/3 — quer review do Argos no HEAD atual? (PR #{N}, HEAD {sha_curto})"

     (a) sim, invocar Argos agora
     (b) não, pular Argos e ir direto para review humano
     (c) stop — encerrar o fluxo
   ```

2. Comportamento por escolha:
   - **(a)** Athena transiciona `status: to review → review`, invoca subagente `warrior-argos` (via Agent tool com `subagent_type=warrior-argos` ou via `/cry-pr-review` — ver feedback `argos_via_subagent`), aguarda Argos publicar review com marker `argos-review-id:...`, transiciona `status: review → to review`, e segue para passo 3.
   - **(b)** Athena registra a recusa em working notes (`<!-- not-flushed -->` em `.plans/{N}.md`), salta direto para o **Passo 6d**.
   - **(c)** Athena registra "Loop encerrado pelo usuário no Argos cycle A{n}" no body da Issue via `kata-flush-plan-to-issue`, NÃO segue para Passo 6d nem Passo 7. Fluxo termina aqui.

3. Athena lê os findings da review:
   - **P0 BLOCKER** → Athena DEVE address (modificar código) antes de continuar; sem opt-out.
   - **P1 WARNING** → Athena apresenta cada finding ao usuário via `AskUserQuestion` ("Address ou defer pra follow-up Issue?"). Address → modifica código; defer → registra TODO no body da Issue.
   - **P2 SUGGESTION** → Athena registra como nota informativa no body da Issue (sem prompt).

4. Se Athena modificou código no passo 3, ela **DEVE** commitar e fazer push antes do próximo ciclo. Cada commit dispara `kata-flush-plan-to-issue` (per Passo 5c — Step concluído conta como gatilho de flush). A próxima checagem de Argos terá um HEAD novo (não idempotente — Argos roda de fato).

5. Se `n < 3`, voltar para passo 1 (próximo ciclo). Se `n == 3`, sair do loop Argos e ir para **Passo 6d**.

**Critérios de saída antecipada do loop Argos:**
- Argos retorna "Argos approves, awaiting human" sem findings P0/P1 actionable → Athena pode oferecer "Quer mais um ciclo Argos ou ir direto pro review humano?" e sair se o usuário escolher pular.
- Usuário escolhe (c) stop em qualquer ciclo → fluxo termina sem Passo 6d/7.

**Idempotência:** se HEAD não mudou desde a última review de Argos (mesmo commit_id), Athena DEVE alertar o usuário ("HEAD inalterado desde última review — nova review será idempotente; Argos abortará pelo próprio marker"). Sugerir address de pelo menos um finding antes de re-invocar Argos.

#### Sub-passo: AI reviewers paralelos a Argos

Após o usuário escolher (a) no passo 1 do ciclo A{n}, Athena DEVE avaliar se faz sentido invocar **AI reviewers paralelos** (GitHub Apps integrados ao repo), com base no conteúdo do diff:

| Reviewer | Quando faz sentido | Como invocar | Detecção idempotente |
|---|---|---|---|
| **Gemini** (`gemini-code-assist[bot]`) | PR toca código novo de qualquer linguagem; bom em sugestões idiomáticas e segurança | `gh pr comment {N} --body "/gemini review"` | `gh pr view {N} --json reviews --jq '[.reviews[] | select(.author.login == "gemini-code-assist[bot]") | .commit_id] | last'` |
| **Coderabbit** (`coderabbitai[bot]`) | PR multi-arquivo; bom em consistency check e best practices | `gh pr comment {N} --body "@coderabbitai review"` | similar (`.author.login == "coderabbitai[bot]"`) |
| **Qodo-Merge** (`qodo-merge-pro[bot]`) | PR backend (Python, Node) — força em test coverage e edge cases | `gh pr comment {N} --body "/review"` | similar |

**Critério de proposta:** Athena olha `gh pr view {N} --json files --jq '[.files[].path]'` e decide quais reviewers fazem sentido:

- PR só-docs (`docs/**`, `README*`, `*.md`) → nenhum AI reviewer adicional (Argos basta).
- PR com código de produção (`src/**`, `framework/**` no caso do próprio Ahrena) → propor 1-2 reviewers conforme stack.
- PR misto → propor o subset que cobre o stack predominante.

**Apresentação:** Athena reúne os reviewers candidatos numa única `AskUserQuestion`:

```
Athena: "AI reviewers paralelos a Argos para A{n}/3? (multi-select)

  [ ] Gemini (/gemini review)
  [ ] Coderabbit (@coderabbitai review)
  [ ] Qodo-Merge (/review)
  [ ] nenhum — só Argos
```

**Comportamento:**

1. Para cada reviewer marcado, Athena posta o comentário de invocação em sequência (não em paralelo — para reduzir ruído timeline).
2. Athena **NÃO bloqueia** esperando esses reviewers — eles são assíncronos (GitHub App webhook); resultados aparecem como reviews/comments no tempo do app (~30s a alguns min).
3. Athena prossegue para o passo 2 do ciclo A{n} (transição `to review → review` e invocação do Argos subagente). Argos roda sua review em paralelo aos AI reviewers externos.
4. No passo 3 (Athena lê findings), Athena coleta findings de **todos os reviewers** com novos `submittedAt > HEAD push time` (Argos + Gemini + Coderabbit + Qodo). Trata cada finding via o mesmo schema P0/P1/P2:
   - Argos publica explicitamente P0/P1/P2 com marker.
   - Gemini/Coderabbit/Qodo publicam suggestions livre-formato — Athena classifica heuristicamente (palavras: "must", "blocker", "critical" → P0; "should", "consider" → P1; "nit", "optional" → P2).
5. Idempotência: se um AI reviewer já revisou o HEAD atual (via commit_id capturado), Athena NÃO re-invoca esse reviewer no próximo ciclo até que haja novos commits.

**Critério de NÃO propor:** se A{n} é cycle de re-validação após fix de findings de A{n-1} (HEAD novo após address) e Argos foi confirmado, AI reviewers extras podem ser pulados — a re-validação é primariamente sobre fechar findings, não levantar novos. Athena propõe `nenhum` como default nesses casos.

### Passo 6d: Human nudge loop (3 ciclos via ScheduleWakeup, com notificação Slack a cada ciclo)

Após os Argos cycles (Passo 6c), Athena agenda o loop de cobrança ao reviewer humano. Diferente do Argos cycle (interativo), o human nudge loop usa `ScheduleWakeup` para wake-ups periódicos.

**Mecanismo de agendamento:** Athena pergunta via `AskUserQuestion`:

```
Athena: "Pronto para human nudge loop (3×15min). Como agendar?

  (a) /loop 15m — eu reagendo via ScheduleWakeup dentro desta sessão
  (b) cron remoto — skill `schedule` cria rotina */15 que checa e reporta
  (c) manual — sem agendamento; humano avisa quando review acontecer

Qual opção?"
```

**Comportamento por escolha:**

- **(a)** Athena chama `ScheduleWakeup` com `delaySeconds=900` e prompt re-checando `gh pr view {N} --json reviewDecision,mergedAt`. A cada cycle: dispara notificação Slack (per "Notificação Slack por ciclo" abaixo) + checa state.
- **(b)** Athena invoca a skill `schedule` criando rotina cron `*/15 * * * *` com agente que executa o check, dispara notificação Slack, e reporta.
- **(c)** Athena registra "Loop manual" no body da Issue. Sem agendamento; humano avisa.

**Notificação Slack por ciclo:**

A cada ciclo `H1, H2, H3`, Athena dispara uma mensagem via MCP de notificação configurado em `.ahrena/.directives` (`notifications.provider`) no canal `notifications.channels.pr_review_timeout`. O conteúdo escala em urgência:

| Ciclo | Mensagem padrão |
|---|---|
| H1 (start) | `PR #{N} pronto para review — {title}. {url}` |
| H2 (+15min) | `Reminder #1: PR #{N} aguardando review há ~15min. {url}` |
| H3 (+30min) | `Reminder #2: PR #{N} aguardando review há ~30min — segunda cobrança. {url}` |

Após H3, sem aprovação → loop encerra silenciosamente (3 cobranças foi suficiente).

**Estados detectáveis durante o loop:**

| `gh pr view` retorna | Ação de Athena |
|---|---|
| `mergedAt != null` | Transição `status: to review → done` + Issue; captura `mergeCommit.oid`; encerra loop. |
| `reviewDecision == "APPROVED"` e `mergedAt == null` | Comenta "PR aprovado, aguardando merge"; encerra loop. |
| `reviewDecision == "CHANGES_REQUESTED"` | → **Passo 6e** (CHANGES_REQUESTED handler). |
| Caso contrário (`REVIEW_REQUIRED` ou null) | Se `H < 3` → reagenda; se `H == 3` → encerra. |

### Passo 6e: CHANGES_REQUESTED handler (reset do loop)

Se durante o Passo 6d o reviewer humano pede mudanças (`reviewDecision == "CHANGES_REQUESTED"`):

1. Athena lê os comentários de review do humano via `gh pr view {N} --json reviews --jq '.reviews[-1]'`.
2. Athena apresenta o resumo dos requests ao usuário via `AskUserQuestion`:
   ```
   Athena: "Reviewer pediu mudanças. Address agora?

     (a) sim, vou implementar as mudanças
     (b) defer — registro como follow-up Issue e mantém o PR aberto
     (c) stop — encerro o loop e o PR
   ```
3. Comportamento por escolha:
   - **(a)** Athena implementa as mudanças (modifica código, commita, push). Cada commit dispara `kata-flush-plan-to-issue`. O push gera novo HEAD SHA.
   - **(b)** Athena registra TODO no body da Issue + abre follow-up Issue referenciando o request. Mantém `status: to review`.
   - **(c)** Athena fecha o PR (`gh pr close 97`), transiciona Issue para `status: abandoned` com nota explicativa. Fluxo termina.

4. Após (a) ou (b), Athena **reagenda o loop a partir do Passo 6c** (Argos pre-flight cycles 3 novos no HEAD novo) — porque novos commits invalidam a review anterior do Argos. Não pula direto para Passo 6d.

5. Se o usuário escolheu (b) defer (sem novos commits), Athena pode pular Passo 6c e ir direto para Passo 6d (since HEAD não mudou).

**Esse handler garante que CHANGES_REQUESTED reseta o ciclo completo de qualidade, não só o human nudge loop.**

Sem a escolha do humano sobre o agendamento (opções a/b/c do Passo 6d), Athena **NÃO DEVE** prosseguir para Passo 7 — o loop é responsabilidade declarada na Tabela A; assumir uma opção default sem confirmação seria contrário ao princípio AI-First (que exige aprovação explícita em ações com efeito colateral, ver `lex-ai-first-experience`).

### Passo 7: Atualizar status dos ADRs (proposed → accepted)

Para cada ADR criado na Fase 3 (listados no checkpoint):

1. Ler `docs/adr/ADR-{n}-{slug}.md`.
2. Alterar `**Status:** proposed` para `**Status:** accepted`.
3. O ADR foi aprovado no Gate 1 e sobreviveu ao Gate 2 — agora é oficial.
4. Incluir esses arquivos modificados no push (ou fazer um commit adicional se já se fez push).

### Passo 8: Atualizar checkpoint final

1. Atualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase concluída: 7
   - status final: `completed`
   - URL do PR criado
   - branch criada
   - ADRs transicionados para `accepted`
2. Informar ao `warrior-athena` (e ao humano):
   - PR criado em `{URL}`
   - Próximo passo humano: revisar e aprovar

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Branch | Git branch | GitHub (via `create_branch` MCP) |
| Commits | Git commits com mensagens Conventional | GitHub (via `push_files` MCP) |
| Pull Request | PR com body estruturado | GitHub (via `create_pull_request` MCP) |
| URL do PR | String | Retorno ao orquestrador |
| ADRs transicionados | Markdown atualizado | `docs/adr/ADR-*` com `Status: accepted` |
| Checkpoint final | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrições

- **Usar apenas MCP:** não usar `git push` direto nem `gh pr create` quando o MCP GitHub está ativo (conforme `lex-mcp`).
- **Sem credenciais hardcoded:** autenticação exclusivamente via `GH_TOKEN`.
- **Gate 2 `go` é pré-requisito inviolável:** não abrir PR se `06-quality-report.md` resultou `no-go`.
- **Body do PR deve referenciar .ahrena/issues/{n}/:** rastreabilidade desde a issue até o PR exige esses links.
- **Conventional Commits obrigatório:** título do PR e mensagens de commit devem seguir o formato (conforme `lex-conventional-commits`).

## Referências

- `lex-issue-driven` — leis do fluxo
- `codex-issue-workflow` — posição desta kata
- `kata-mcp-github-read` — padrão análogo de uso de GitHub MCP
- `codex-mcp-github` — ferramentas e parâmetros
- `lex-conventional-commits` — formato de commits e título do PR
- `codex-contributing` — fluxo de contribuição do projeto
