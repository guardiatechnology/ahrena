# Kata: Preparar Pull Request

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 7 do fluxo Issue-Driven — criação de branch, push dos arquivos e abertura de PR no GitHub via MCP, com body estruturado referenciando todos os artefatos do fluxo

## Objetivo

Após o Gate 2 resultar em `go`, criar a branch, fazer push dos arquivos modificados e abrir um Pull Request no GitHub via MCP. O body do PR é estruturado referenciando a issue original, os ACs numerados, os ADRs criados e os artefatos do fluxo em `docs/issues/issue-{n}/`. O resultado é um PR pronto para revisão humana, com rastreabilidade completa.

## Quando Usar

- Fase 7 (última) do fluxo orquestrado por `warrior-athena`, após `kata-quality-gate` resultar em `go`
- Quando é necessário submeter uma implementação validada para revisão via PR

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Número da issue | Sim | Número da issue original (ex.: `42`) |
| Repositório | Sim | `owner/repo` |
| Base branch | Não | Branch alvo do PR; padrão: `main` |
| Artefatos do fluxo | Sim | `docs/issues/issue-{n}/*` e `docs/adr/ADR-*` criados nas fases anteriores |
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
2. Confirmar `GITHUB_PAT` definida.
3. Ler `docs/issues/issue-{n}/06-quality-report.md` e confirmar resultado `go`. Se `no-go`, recusar criar PR e retornar ao orquestrador.
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

<!-- Copiados de docs/issues/issue-{n}/02-requirements.md -->

- [x] **AC-1:** {descrição}
- [x] **AC-2:** {descrição}
- [x] **AC-3:** {descrição}

## Arquitetura

Ver [documento de arquitetura](docs/issues/issue-{n}/03-architecture.md).

### ADRs criados

- [ADR-{n}: {título}](docs/adr/ADR-{n}-{slug}.md)

(omitir se não houve ADR)

## Qualidade

- ✅ Gate 2 aprovado ([relatório](docs/issues/issue-{n}/06-quality-report.md))
- ✅ Revisão de segurança aprovada ([relatório](docs/issues/issue-{n}/05-security-review.md))
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

- Plan(s): plan-{NNN}
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

### Passo 5c: Flush do plano (per ADR-002)

Antes de invocar `create_pull_request`, garantir que o body da Issue reflete o estado atual do trabalho:

1. Invocar `kata-flush-plan-to-issue` passando o número da Issue.
2. O kata lê `.plans/{N}.md`, filtra blocos `<!-- not-flushed -->`, executa preflight de drift remoto, e grava o conteúdo filtrado no body da Issue via MCP `update_issue` (preferido) ou `gh issue edit --body-file` (fallback).
3. Em caso de drift remoto detectado (default `force=false`), o kata pausa e oferece merge manual — não prosseguir até resolução.

Esse passo substitui a mecânica antiga de "atualizar `status:` no front-matter do plano" (modelo legado pré-ADR-002): no Issue-as-plan model, o body da Issue é o canonical; o cache local `.plans/{N}.md` é regenerável.

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

A label é a única fonte de truth do estado per ADR-002 — o body da Issue (canonical do plano) já foi atualizado no Passo 5c.

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
- **Sem credenciais hardcoded:** autenticação exclusivamente via `GITHUB_PAT`.
- **Gate 2 `go` é pré-requisito inviolável:** não abrir PR se `06-quality-report.md` resultou `no-go`.
- **Body do PR deve referenciar docs/issues/issue-{n}/:** rastreabilidade desde a issue até o PR exige esses links.
- **Conventional Commits obrigatório:** título do PR e mensagens de commit devem seguir o formato (conforme `lex-conventional-commits`).

## Referências

- `lex-issue-driven` — leis do fluxo
- `codex-issue-workflow` — posição desta kata
- `kata-mcp-github-read` — padrão análogo de uso de GitHub MCP
- `codex-mcp-github` — ferramentas e parâmetros
- `lex-conventional-commits` — formato de commits e título do PR
- `codex-contributing` — fluxo de contribuição do projeto
