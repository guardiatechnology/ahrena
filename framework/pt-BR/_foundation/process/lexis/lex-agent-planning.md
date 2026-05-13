# Lexis: Planejamento Obrigatório para Tarefas de Agentes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Toda tarefa multi-etapa iniciada por qualquer agente ou subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Agentes que executam sem planejamento prévio produzem resultados parciais, deixam arquivos em estados inconsistentes e forçam o usuário a reconstruir contexto manualmente. Esta Lexis elimina esse padrão exigindo que todo agente registre seu plano antes de executar, tornando intenção, escopo e sequência auditáveis por humanos e por outros agentes. Além disso, define um ciclo de vida unificado entre plano, Issue do GitHub e PR — com owner explícito para cada transição — para eliminar drift e dar visibilidade à "sala de espera" da revisão.

Esta versão (per ADR-002) muda o **meio de armazenamento** do plano: o conteúdo canônico vive no **body da Issue** do GitHub; `.plans/{N}.md` é cache local da IA (gitignored); `.ahrena/issues/{N}/` guarda os Phase artifacts do fluxo Issue-Driven (committed). Arquivo de plano dedicado em `.claude/plans/*.md` deixa de ser o canônico.

## Lei

> **Todo agente DEVE registrar um plano canônico no **body da Issue do GitHub** correspondente ANTES de iniciar qualquer tarefa que envolva 2 ou mais etapas, afete múltiplos arquivos, ou produza artefatos permanentes. O plano DEVE ser apresentado ao usuário para confirmação antes da execução começar. Iniciar execução multi-etapa sem plano registrado e confirmado é PROIBIDO. O `status:` do plano vive como **label canônica** na Issue (e no PR, a partir de `to review`); o enum unificado é `todo | development | to review | review | to release | release | done` (mais o terminal alternativo `abandoned`); cada transição DEVE ser executada pelo owner declarado neste Lex.**

## Abrangência

- **Aplica-se a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, qualquer AI agent ou subagente que invoque katas, warriors ou cries no contexto Ahrena
- **Agentes vinculados:** todos, sem exceção de papel
- **Exceções permitidas:** operações triviais de etapa única (editar um único arquivo com instrução direta, consulta de leitura pura, comando isolado sem efeito colateral permanente)

## Modelo de armazenamento em três camadas (per ADR-002)

| Camada | Localização | Papel | Versionamento |
|---|---|---|---|
| **Issue body** | `https://github.com/{owner}/{repo}/issues/{N}` | Canonical. Summary + Plan section com Objective, Steps, Risks, Dependencies, Open Questions | Audit log nativo do GitHub (timestamp + autor por edição) |
| **`.plans/{N}.md`** | Raiz do repo, gitignored | AI working memory + scratch. Superset do body da Issue + seções `<!-- not-flushed -->` | Cache local regenerável; `kata-load-plan-from-issue` materializa, `kata-flush-plan-to-issue` flusha |
| **`.ahrena/issues/{N}/`** | Raiz do repo, committed | Phase artifacts do fluxo Issue-Driven (`01-brief.md` … `06-quality-report.md`) | Git |

Path de `.plans/` é configurável via `paths.plans` em `.ahrena/.directives` (default: `.plans/`). Não confundir com `paths.plans` legado que apontava para `.claude/plans/` — o novo default é `.plans/` na raiz, agente-agnóstico.

## Schema do body da Issue (plano canônico)

```markdown
## Summary

{2-4 frases descrevendo o objetivo. Tipicamente herda do template (feature-request "Objective" / tech-task "Why").}

## Plan

### Objective
{Por que esta tarefa está sendo feita — 1 a 3 frases.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{Planos, Issues ou PRs de que esta tarefa depende; "None" se não houver.}

### Risks
{Riscos conhecidos e mitigações; "None identified" se não houver.}

### Open Questions
{Perguntas em aberto que precisam de decisão antes/durante execução; "None" se não houver.}
```

Schema do `.plans/{N}.md` (per Open Question #4 de plan-046): **superset** do body da Issue. Carrega o body completo espelhado + seções locais marcadas:

```markdown
<!-- not-flushed -->
## Working notes
- decisão de debugging X às 14:32
- erro Y reproduzido em test-Z

## Next actions
1. tentar abordagem A; se falhar, B

## Scratch
qualquer texto livre que a IA queira manter como contexto local
<!-- /not-flushed -->
```

`kata-flush-plan-to-issue` filtra blocos `<!-- not-flushed -->` antes de gravar no body da Issue.

## Ciclo de vida do plano

O ciclo opera sobre **dois eixos disjuntos** (per ADR-002 / plan-045 absorvido):

### Eixo A — Dev cycle (Issue de feature/fix/chore/refactor)

```
todo → development → to review → review → done
                           ↘
                           abandoned (terminal alternativo, qualquer estágio)
```

- `todo` — plano criado, Issue aberta, branch remota vinculada, worktree pronto.
- `development` — Athena delegou e implementação está em andamento.
- `to review` — PR aberto, esperando reviewer (humano ou Argos) pegar.
- `review` — Argos (ou humano) está revisando ativamente.
- `done` — PR mergeado; Issue fechada via `Closes #N`.
- `abandoned` — terminal alternativo; plano descartado.

### Eixo B — Release cycle (Issue de release dedicada)

```
to release → release → done
                  ↘
                  abandoned (terminal alternativo, qualquer estágio)
```

- `to release` — release Issue criada por Janus; `Tracks: #N1, #N2, ...` listando PRs mergeados desde o último tag.
- `release` — release em execução (`kata-release-prepare` rodando; humano aprovou bump/changelog).
- `done` — tag empurrada, `validate-tag.yml` passou, Release publicada no GitHub.
- `abandoned` — release abortada antes de tag.

A mutex de labels é **intra-artefato** (dentro de cada Issue/PR), não cross-artifact: uma Issue carrega exatamente uma label `status: <name>` por vez. HARD-GATE em `lex-issue-status` proíbe aplicar labels do Eixo B em Issue/PR de feature, e vice-versa.

A pasta `.ahrena/issues/_legacy/` (histórico anterior a ADR-002) preserva planos em formato antigo — **não é mais um estado** do enum.

## Owner do `— → todo`: warrior-eunomia

Todo plano (top-level ou subtask) DEVE ser criado por `warrior-eunomia` via `kata-plan-task` (top-level) ou `kata-create-subtasks` (subtask, downstream de Athena Phase 4). Eunomia executa os 5 passos abaixo antes de marcar a label `status: todo` como definitiva:

1. Abrir a Issue correspondente (per `lex-issue-first` e `lex-issue-quality`).
2. Verificar Issue Type pós-criação (per `lex-issue-type-verified`).
3. Criar a branch remota e vinculá-la à Issue via `gh issue develop {N} --base main --name {type}/{N}-{slug}` (registra a branch como "Development" na sidebar do GitHub).
4. Criar a worktree per `lex-git-worktrees`.
5. **Preencher o body da Issue com o plano canônico** (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) via MCP `update_issue` (GitHub MCP) — ou fallback CLI `gh issue edit {N} --body-file <path>` (per `lex-mcp` regra 4). Sem body preenchido, o plano permanece em rascunho — não pode ser apresentado como `todo` ao usuário.

**Fallback enquanto Eunomia não estiver shipada:** a responsabilidade recai no agente da sessão corrente, seguindo o mesmo contrato — sem refatoração subsequente quando Eunomia entrar em produção.

<HARD-GATE>
warrior-eunomia (ou o agente da sessão atuando como fallback enquanto Eunomia
não estiver shipada) MUST NOT aplicar a label `status: todo` em uma Issue
sem satisfazer TODOS os 5 passos canônicos:

  (a) Issue aberta per lex-issue-first e lex-issue-quality
      (template, label, Issue Type, assignee, Why/What/How)
  (b) Issue Type verificado per lex-issue-type-verified (entregue
      em plan-044; absorvido por plan-046). Enquanto não shipa,
      satisfazer via `gh api repos/{owner}/{repo}/issues/{N}` retornando
      `type` populado e compatível com o template — mesmo contrato
  (c) Branch remota criada e vinculada à Issue via
      gh issue develop {N} --base main --name {type}/{N}-{slug}
  (d) Worktree criado per lex-git-worktrees em
      `.worktrees/{N}-{slug}/`
  (e) Body da Issue preenchido com plano canônico (Summary +
      Plan section contendo Objective, Steps, Risks, Dependencies,
      Open Questions) via MCP `update_issue` (preferido) ou
      `gh issue edit {N} --body-file <path>` (fallback)

Esta regra aplica-se a TODO plano (top-level ou subtask), independente de:
  - tamanho percebido ("é só um chore")
  - urgência ("incêndio em produção")
  - quem pediu ("o CEO solicitou")
  - confiança da equipe ("já testamos muito")

Exceção declarada: nenhuma. Mesmo em hotfix, os 5 passos são executados
em sequência — Eunomia (ou fallback) não pula a amarração
Issue↔branch↔worktree↔body.
</HARD-GATE>

## Owners de cada transição

### Tabela A — Dev cycle (Eunomia / Athena / Argos)

| Transição | Owner | Gatilho |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente da sessão) | Cria plano + abre Issue + `gh issue develop` + worktree + body preenchido |
| `todo → development` | `warrior-athena` | Phase 4 (delegação de implementação) |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR; flush prévio do `.plans/{N}.md` via `kata-flush-plan-to-issue` |
| `to review → review` | `warrior-argos` | Argos inicia ciclo de revisão automatizada |
| `review → to review` | `warrior-argos` | Argos termina ciclo sem aprovar (changes-requested ou awaiting-human) |
| `to review → done` | `warrior-athena` | Humano aprova PR; merge fecha Issue via `Closes #N` |
| `qualquer → abandoned` | criador ou owner atual | Plano descartado |

### Tabela B — Release cycle (Janus)

| Transição | Owner | Gatilho |
|---|---|---|
| `— → to release` | `warrior-janus` | Abre release Issue; popula `Tracks: #N1, #N2, ...` com PRs mergeados desde o último tag |
| `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano de bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` conclui (tag empurrada, `validate-tag.yml` passa, Release criada); notificação via MCP em `notifications.channels.release_notify` |
| `qualquer → abandoned` | `warrior-janus` | Release abortada antes de tag |

Cada owner DEVE:

- Aplicar a label `status: <name>` correspondente na Issue do GitHub (per `lex-issue-status`).
- Aplicar a label `status: <name>` correspondente no PR (a partir de `to review`).
- Disparar `kata-flush-plan-to-issue` se o cache local `.plans/{N}.md` estiver à frente do body da Issue.

## Auditoria de fechamento

Para audit pós-merge, dois campos são derivados de APIs nativas do GitHub (sem front-matter dedicado no plano):

| Campo lógico | Fonte canônica | Comando |
|---|---|---|
| `closed_at` | `Issue.closedAt` | `gh issue view {N} --json closedAt --jq .closedAt` |
| `merge_commit` | `PullRequest.mergeCommit.oid` | `gh pr view {PR} --json mergeCommit --jq .mergeCommit.oid` |

Para planos legados em `.ahrena/issues/_legacy/` que mantêm YAML front-matter histórico (planos 043-045 e anteriores), `merge_commit:` e `closed_at:` são reconhecidos como front-matter opcional aceito — preserva o audit sem retrofit.

## Cadência de load/flush (per ADR-002 §3)

Sincronização entre `.plans/{N}.md` e o body da Issue ocorre em **3 gatilhos canônicos** (não em cada toggle):

| Gatilho | Operação |
|---|---|
| Início de sessão / handoff entre agentes | `kata-load-plan-from-issue` |
| Transição de label `status:` na Issue/PR | `kata-flush-plan-to-issue` |
| Step do plano marcado como concluído (`[ ]` → `[x]`) | `kata-flush-plan-to-issue` |
| Fim de sessão (heartbeat conclui ou Athena/Argos sai) | `kata-flush-plan-to-issue` |

Toggles intermediários, edições de scratch (`<!-- not-flushed -->`) e working notes são **livres** — não disparam flush. Documentação operacional em `codex-agent-planning` §9.

## Relação com outros artefatos

- **Issue GitHub:** carrega o plano canônico no body; a label `status: <name>` é a única fonte de truth para o estado.
- **PR:** a partir de `to review`, o PR carrega a label `status: <name>` correspondente, atualizada por Athena/Argos/Janus conforme o estado avança. Sync da label é responsabilidade do owner da transição.
- **`.plans/{N}.md`:** cache local regenerável; nunca commitado; reconstruído por `kata-load-plan-from-issue` em fresh clone.
- **`.ahrena/issues/{N}/`:** committed; recebe Phase artifacts do fluxo Issue-Driven (per `lex-issue-driven`).
- **Checkpoint (`.checkpoint`):** o plano cobre **task** (Steps, Decisões, Riscos no body da Issue); o checkpoint cobre **sessão** (foco da janela, hand-off entre planos, threads paralelas). Sobreposição é PROIBIDA — ver `lex-checkpoint` regra 5.
- **ADR:** quando um plano identifica uma decisão arquitetural relevante, um ADR DEVE ser aberto conforme `lex-issue-driven`.
- **Heartbeat de sessão:** sessão Claude Code que opera no plano é registrada em `.ahrena/workflow/sessions/<session-id>.json` (per `codex-session-tracking`); não vive no body da Issue.

### Plano (body da Issue) vs `.plans/` vs `.checkpoint` — o que vai onde

| Conteúdo | Vive em |
|---|---|
| Objective, Steps `[x]`, Risks, Dependencies, Open Questions | Body da Issue (canonical) |
| Decisões arquiteturais relevantes | ADR em `docs/adr/` (referenciado pelo plano) |
| Working notes, debugging diary, scratch | `.plans/{N}.md` em blocos `<!-- not-flushed -->` |
| Foco geral da janela de trabalho (Session focus) | `.checkpoint` — gitignored |
| Ponteiros para múltiplos planos ativos (Active plans) | `.checkpoint` — gitignored |
| Threads paralelas que não viraram plano (Open threads) | `.checkpoint` — gitignored |

Em caso de dúvida: conteúdo estrutural vai para o body da Issue; conteúdo volátil para `.plans/{N}.md` em bloco não-flushed; foco da sessão para `.checkpoint`.

## Exemplos

### Correto

```
Tarefa: migrar armazenamento do plano para o modelo Issue-as-plan
→ Eunomia (fallback: agente da sessão) abre Issue #96
   (template feature-request, Issue Type Feature, labels)
→ Eunomia verifica type via gh api (per lex-issue-type-verified)
→ Eunomia cria branch via gh issue develop 96 --base main
   --name feat/96-issue-as-plan-and-issues-folder
→ Eunomia cria worktree em .worktrees/96-issue-as-plan-and-issues-folder/
→ Eunomia preenche body da Issue #96 com Summary + Plan section
   (Objective, Steps, Risks, Dependencies, Open Questions)
→ Eunomia aplica label `status: todo` na Issue
→ Athena assume Phase 4: aplica `status: development`
→ Athena abre PR; aplica `status: to review` na Issue + PR;
   dispara kata-flush-plan-to-issue
→ Argos inicia revisão: `status: review`
→ Argos termina sem aprovar: `status: to review` (humano cobrado em 3×15min)
→ Humano aprova; merge fecha Issue via Closes #N: `status: done`

Release cycle (separada):
→ Janus abre release Issue (e.g. #100); Tracks: #93, #96, #101
→ Janus aplica `status: to release` na release Issue
→ Janus inicia kata-release-prepare: `status: release`
→ Janus conclui kata-release-publish: `status: done`
```

### Incorreto

```
Tarefa: implementar feature X
→ Agente cria branch direto via git checkout -b sem abrir Issue
→ ❌ Viola lex-issue-first; sem Issue, plano não pode ser registrado

→ Agente aplica label `status: todo` na Issue sem preencher o body
→ ❌ Viola HARD-GATE precondition (e): body precisa carregar
   Summary + Plan section antes de status: todo definitivo

→ Agente cria `.claude/plans/plan-NNN-*.md` como canônico
→ ❌ Modelo legado pré-ADR-002. Plano canônico vive no body da Issue;
   `.plans/{N}.md` é cache local regenerável, não fonte de truth

→ Agente aplica `status: to release` em Issue de feature
→ ❌ Viola mutex intra-artefato de lex-issue-status: `to release`
   pertence ao Eixo B (release Issue), proibido no Eixo A
```

## Validação Automatizada

- **Ferramenta:** verificação pelo agente antes de qualquer execução multi-etapa; `kata-plan-task` como ponto de entrada canônico; revisão de PR confirma que a label `status:*` da Issue e a label `status:*` do PR estão alinhadas, e que o body da Issue carrega Summary + Plan section.
- **Momento:** antes de qualquer execução de tarefa multi-etapa — sem exceção; e em cada transição de estado.
- **Métrica:** 0 tarefas multi-etapa executadas sem body de Issue preenchido; 0 PRs mergeados com `status:` divergente entre Issue e PR; 100% das transições executadas pelo owner declarado; 100% das Issues de release com `Tracks:` listando os PRs mergeados desde o último tag.

## Referências

- ADR-002 — modelo de armazenamento em três camadas
- `lex-issue-status` — labels canônicas de status; split Tabela A (dev) / Tabela B (release)
- `lex-issue-type-verified` — verificação programática do Issue Type pós-criação
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — preconditions do passo `— → todo`
- `lex-mcp` — preferência MCP + fallback CLI para `gh issue edit`
- `lex-checkpoint` — rastreamento de estado de sessão (complementar)
- `lex-issue-driven` — fluxo Issue-Driven; Phase artifacts em `.ahrena/issues/{N}/`
- `codex-agent-planning` — manual operacional do modelo de 3 camadas (load → edit → flush)
- `kata-plan-task` — procedimento operacional para criar planos (preenche body da Issue)
- `kata-load-plan-from-issue` — materializa `.plans/{N}.md` a partir do body da Issue
- `kata-flush-plan-to-issue` — flusha `.plans/{N}.md` (filtrando `<!-- not-flushed -->`) para o body da Issue
- `kata-create-subtasks` — decomposição de child Issue em subtasks
- `kata-session-heartbeat` — atualização do heartbeat de sessão
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
