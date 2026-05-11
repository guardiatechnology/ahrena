# Lexis: Planejamento Obrigatório para Tarefas de Agentes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Toda tarefa multi-etapa iniciada por qualquer agente ou subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Agentes que executam sem planejamento prévio produzem resultados parciais, deixam arquivos em estados inconsistentes e forçam o usuário a reconstruir contexto manualmente. Esta Lexis elimina esse padrão exigindo que todo agente documente seu plano antes de executar, tornando intenção, escopo e sequência auditáveis por humanos e por outros agentes. Além disso, define um ciclo de vida unificado entre plano, Issue do GitHub e PR — com owner explícito para cada transição — para eliminar drift e dar visibilidade à "sala de espera" da revisão.

## Lei

> **Todo agente DEVE criar um documento de plano em `./{agent_dir}/plans/plan-{NNN}-{slug}.md` (ou no path definido em `paths.plans` de `.ahrena/.directives`) ANTES de iniciar qualquer tarefa que envolva 2 ou mais etapas, afete múltiplos arquivos, ou produza artefatos permanentes. O plano DEVE ser apresentado ao usuário para confirmação antes da execução começar. Iniciar execução multi-etapa sem plano documentado e confirmado é PROIBIDO. O `status:` do plano DEVE pertencer ao enum unificado `todo | development | to review | review | to release | release | done` (mais o terminal alternativo `abandoned`); cada transição DEVE ser executada pelo owner declarado neste Lex.**

## Abrangência

- **Aplica-se a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, qualquer AI agent ou subagente que invoque katas, warriors ou cries no contexto Ahrena
- **Agentes vinculados:** todos, sem exceção de papel
- **Exceções permitidas:** operações triviais de etapa única (editar um único arquivo com instrução direta, consulta de leitura pura, comando isolado sem efeito colateral permanente)

## Resolução do path do plano (precedência)

| Prioridade | Fonte | Valor |
|:---:|---|---|
| 1 | `paths.plans` em `.ahrena/.directives` | Override de projeto — substitui todo o restante |
| 2 | Padrão por agente | `.claude/plans/` para Claude Code; `.cursor/plans/` para Cursor; `.plans/` para agente desconhecido |

Nome do arquivo: `plan-{NNN}-{slug}.md` onde `{NNN}` é sequencial por diretório (001, 002, …), sem lacunas.

## Estrutura mínima obrigatória do plano

```markdown
---
plan_id: "{NNN}"
title: "{slug}"
status: todo | development | to review | review | to release | release | done | abandoned
agent: claude | cursor | unknown
issue: "{owner/repo#N}"
branch: "{type}/{N}-{slug}"
worktree: ".worktrees/{N}-{slug}"
claude_session: "{short-uuid}"        # opcional; preenchido por kata-session-heartbeat
session_entrypoint: "claude-vscode | claude-cli | claude-desktop | claude-web"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Plano: {título legível}

## Objetivo
{Por que esta tarefa está sendo feita — 1 a 3 frases}

## Escopo
{O que será modificado: arquivos, sistemas, artefatos afetados}

## Etapas
- [ ] Etapa 1
- [ ] Etapa 2
...

## Dependências
{Planos ou issues de que esta tarefa depende; "Nenhuma" se não houver}

## Riscos
{Riscos conhecidos e mitigações; "Nenhum identificado" se não houver}
```

## Ciclo de vida do plano

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, qualquer estágio)
```

Semântica de cada estado:

- `todo` — plano criado, Issue aberta, branch remota vinculada, worktree pronto, ainda não começou.
- `development` — Athena delegou e implementação está em andamento.
- `to review` — PR aberto, esperando reviewer (humano ou Argos) pegar.
- `review` — Argos (ou humano) está revisando ativamente.
- `to release` — review aprovou, esperando o agente de release iniciar.
- `release` — release em execução (tag/build/deploy).
- `done` — release completo, PR mergeado, ciclo encerrado.
- `abandoned` — terminal alternativo (qualquer estágio → `abandoned`); plano descartado.

A pasta `archived/` permanece como convenção de organização de filesystem para planos pós-merge — **não é mais um estado** do enum.

## Owner do `— → todo`: warrior-eunomia

Todo plano (top-level ou subtask) DEVE ser criado por `warrior-eunomia` via `kata-plan-task` (top-level) ou `kata-create-subtasks` (subtask, downstream de Athena Phase 4). Eunomia executa os 5 passos abaixo antes de marcar `status: todo` como definitivo:

1. Abrir a Issue correspondente (per `lex-issue-first` e `lex-issue-quality`).
2. Verificar Issue Type pós-criação (per `lex-issue-type-verified`).
3. Criar a branch remota e vinculá-la à Issue via `gh issue develop {N} --base main --name {type}/{N}-{slug}` (registra a branch como "Development" na sidebar do GitHub).
4. Criar a worktree per `lex-git-worktrees`.
5. Registrar o número da Issue, o nome da branch e o path do worktree no front-matter do plano (`issue:`, `branch:`, `worktree:`). Sem essa amarração, o plano permanece em rascunho — não pode ser apresentado como `todo` ao usuário.

**Fallback enquanto Eunomia não estiver shipada:** a responsabilidade recai no agente da sessão corrente, seguindo o mesmo contrato — sem refatoração subsequente quando Eunomia entrar em produção.

<HARD-GATE>
warrior-eunomia (ou o agente da sessão atuando como fallback enquanto Eunomia
não estiver shipada) MUST NOT marcar `status: todo` como definitivo em
um plano sem satisfazer TODOS os 5 passos canônicos:

  (a) Issue aberta per lex-issue-first e lex-issue-quality
      (template, label, Issue Type, assignee, Why/What/How)
  (b) Issue Type verificado per lex-issue-type-verified
      (gh api repos/{owner}/{repo}/issues/{N} confirma type populado)
  (c) Branch remota criada e vinculada à Issue via
      gh issue develop {N} --base main --name {type}/{N}-{slug}
  (d) Worktree criado per lex-git-worktrees em
      `.worktrees/{N}-{slug}/`
  (e) Front-matter do plano atualizado com issue, branch e worktree

Esta regra aplica-se a TODO plano (top-level ou subtask), independente de:
  - tamanho percebido ("é só um chore")
  - urgência ("incêndio em produção")
  - quem pediu ("o CEO solicitou")
  - confiança da equipe ("já testamos muito")

Exceção declarada: nenhuma. Mesmo em hotfix, os 5 passos são executados
em sequência — Eunomia (ou fallback) não pula a amarração Issue↔branch↔worktree.
</HARD-GATE>

## Owners de cada transição

| Transição | Owner | Gatilho |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente da sessão) | Cria plano + abre Issue + `gh issue develop` + worktree |
| `todo → development` | `warrior-athena` | Phase 4 (delegação de implementação) |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR |
| `to review → review` | `warrior-argos` | Argos inicia ciclo de revisão automatizada |
| `review → to review` | `warrior-argos` | Argos termina ciclo sem aprovar (changes-requested ou awaiting-human) |
| `to review → to release` | `warrior-athena` | Humano aprova PR (loop de wake-up detecta `APPROVED`) |
| `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano de bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` conclui (tag empurrada, `validate-tag.yml` passa, Release criada); notificação via MCP em `notifications.channels.release_notify` |
| `qualquer → abandoned` | criador ou owner atual | Plano descartado |

Cada owner DEVE:

- Atualizar o `status:` no front-matter do plano.
- Aplicar a label `status: <name>` correspondente na Issue do GitHub (per `lex-issue-status`).
- Aplicar a label `status: <name>` correspondente no PR (a partir de `to review`).

## Relação com outros artefatos

- **Issue GitHub:** um plano referencia uma issue; uma issue pode ter múltiplos planos (ex.: design, implementação, testes). A label `status: <name>` na Issue espelha o `status:` do plano.
- **PR:** a partir de `to review`, o PR carrega a label `status: <name>` correspondente, atualizada por Athena/Argos/Janus conforme o estado avança.
- **Checkpoint (`.checkpoint`):** o plano cobre **task** (committed, com Steps, Decisões, Riscos); o checkpoint cobre **sessão** (foco da janela, hand-off entre planos, threads paralelas, scratchpad). Sobreposição é PROIBIDA — ver `lex-checkpoint` regra 5
- **ADR:** quando um plano identifica uma decisão arquitetural relevante, um ADR DEVE ser aberto conforme `lex-issue-driven`
- **Heartbeat de sessão:** o front-matter do plano referencia a sessão Claude Code que opera no momento (`claude_session`, `session_entrypoint`); detalhes em `codex-session-tracking`.

### Plano vs `.checkpoint` — o que vai onde

| Conteúdo | Vive em |
|---|---|
| Objetivo, Steps `[x]`, Status (do enum unificado), Decisões fechadas, Riscos, Verificação | Plano — committed |
| Activity, Progress detalhado, Artifacts produced, Next steps de uma task | Plano — committed |
| Foco geral da janela de trabalho (Session focus) | `.checkpoint` — gitignored |
| Ponteiros para múltiplos planos ativos (Active plans) | `.checkpoint` — gitignored |
| Threads paralelas que não viraram plano (Open threads) | `.checkpoint` — gitignored |
| Scratchpad livre, links, lembretes (Notes) | `.checkpoint` — gitignored |

Em caso de dúvida, conteúdo vai para o plano. Plano vence em durabilidade (committed) e em escopo (cobre task; checkpoint cobre sessão).

## Exemplos

### Correto

```
Tarefa: implementar status unificado entre plano e Issue
→ Eunomia abre Issue #90 (template feature-request, Issue Type Feature, labels)
→ Eunomia verifica type via gh api (per lex-issue-type-verified)
→ Eunomia cria branch via gh issue develop 90 --base main --name feat/90-...
→ Eunomia cria worktree em .worktrees/90-.../
→ Eunomia escreve plan-043 com status: todo, issue, branch, worktree no front-matter
→ Athena assume Phase 4: status → development
→ Athena abre PR: status → to review
→ Argos inicia revisão: status → review
→ Argos termina sem mudanças: status → to review (humano cobrado em 3×15min)
→ Humano aprova: status → to release
→ Janus inicia release: status → release
→ Janus conclui: status → done
```

### Incorreto

```
Tarefa: implementar feature X
→ Agente cria branch direto via git checkout -b sem abrir Issue
→ ❌ Viola lex-issue-first; sem Issue, plano não pode ser marcado todo
→ Agente marca status: todo no plano sem branch remota linkada à Issue
→ ❌ Viola HARD-GATE deste Lex (precondição (c) não satisfeita)
```

## Validação Automatizada

- **Ferramenta:** verificação pelo agente antes de qualquer execução multi-etapa; `kata-plan-task` como ponto de entrada canônico; revisão de PR confirma que o `status:` do plano, a label `status:*` da Issue e a label `status:*` do PR estão alinhados.
- **Momento:** antes de qualquer execução de tarefa multi-etapa — sem exceção; e em cada transição de estado.
- **Métrica:** 0 tarefas multi-etapa executadas sem plano documentado em `{agent_dir}/plans/`; 0 PRs mergeados com `status:` divergente entre plano, Issue e PR; 100% das transições executadas pelo owner declarado.

## Referências

- `codex-agent-planning` — manual com template completo, exemplos e boas práticas
- `kata-plan-task` — procedimento operacional para criar e manter planos (modo top-level de Eunomia)
- `kata-create-subtasks` — procedimento de decomposição de child Issue em subtasks (modo subtask de Eunomia)
- `kata-session-heartbeat` — atualização do heartbeat de sessão
- `lex-issue-status` — labels canônicos de status na Issue/PR
- `lex-issue-type-verified` — verificação programática do Issue Type pós-criação
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — preconditions do passo `— → todo`
- `lex-checkpoint` — rastreamento de estado de sessão (complementar)
- `lex-issue-driven` — fluxo de desenvolvimento dirigido por issues
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
