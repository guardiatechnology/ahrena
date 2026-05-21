# Lexis: Planejamento Obrigatório para Tarefas de Agentes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Toda tarefa multi-etapa iniciada por qualquer agente ou subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Agentes que executam sem planejamento prévio produzem resultados parciais, deixam arquivos em estados inconsistentes e forçam o usuário a reconstruir contexto manualmente. Esta Lexis elimina esse padrão exigindo que todo agente registre seu plano antes de executar, tornando intenção, escopo e sequência auditáveis por humanos e por outros agentes. Além disso, define um ciclo de vida unificado entre Plan, Issue do GitHub e PR — com owner explícito para cada transição — para eliminar drift e dar visibilidade à "sala de espera" da revisão.

O modelo canônico é hierárquico: cada **Issue** (User Story, Bug ou Tech Task) carrega o problema (Why/What/How/AC); de cada Issue derivam **1..N Plans**, materializados como **sub-issues do GitHub** (Issue Type Task) que encapsulam unidades executáveis de trabalho; de cada Plan derivam **1..N PRs**. Plans nunca existem como arquivo local canônico — o body da sub-issue é a fonte de verdade. Caches locais provider-specific (`.claude/plans/`, `.cursor/plans/`) são derivados regeneráveis, gitignored.

## Lei

> **Todo agente DEVE registrar um plano canônico como sub-issue de GitHub (Issue Type Task) vinculada à Issue parent ANTES de iniciar execução de qualquer tarefa que envolva 2 ou mais etapas, afete múltiplos arquivos, ou produza artefatos permanentes. O plano DEVE ser apresentado ao usuário para confirmação antes da execução começar. Iniciar execução multi-etapa (criar branch, commitar, abrir PR) sem sub-issue Plan criada e confirmada é PROIBIDO. Rascunhar um plano localmente em `.claude/plans/plan-{slug}.md` ou `.cursor/plans/plan-{slug}.md` com `status: draft` no front-matter é PERMITIDO como entry point plan-first, desde que o agente promova o rascunho a sub-issue antes de iniciar execução (transição `draft → todo` via `kata-contributing-issue` + `kata-decompose-issue-into-plans` ou `kata-plan-task`). O `status:` do plano vive como **label canônica** na sub-issue (e no PR, a partir de `to review`); o enum canônico é `todo | development | to review | review | to release | release | done` (mais o terminal alternativo `abandoned`, e o estado local-only `draft` pré-promoção, que não existe como label do GitHub); cada transição DEVE ser executada pelo owner declarado neste Lex. A transição `— → todo` aplica o gate de criação (template + labels + Issue Type + Why/What/How); a transição `todo → development` aplica o gate de início de execução (branch remota + worktree + assignee).**

## Abrangência

- **Aplica-se a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, qualquer AI agent ou subagente que invoque katas, warriors ou cries no contexto Ahrena
- **Agentes vinculados:** todos, sem exceção de papel
- **Exceções permitidas:** operações triviais de etapa única (editar um único arquivo com instrução direta, consulta de leitura pura, comando isolado sem efeito colateral permanente)

## Modelo hierárquico Issue → Plan → PR

```
Issue (User Story | Bug | Tech Task)            ← problema, Why/What/How, AC
   │
   ├─ Plan sub-issue (Task)                     ← unidade executável #1
   │     ├─ status: todo | development | to review | review | done
   │     ├─ branch: {type}/{M}-{slug}
   │     └─ PR(s) que fecham este Plan
   │
   ├─ Plan sub-issue (Task)                     ← unidade executável #2
   │     └─ ...
   │
   └─ Plan sub-issue (Task)                     ← unidade executável #N
         └─ ...
```

| Camada | Localização | Papel | Versionamento |
|---|---|---|---|
| **Issue (parent)** | `https://github.com/{owner}/{repo}/issues/{N}` | Carrega problema, motivação, acceptance criteria. Não tem branch própria | GitHub audit log |
| **Plan sub-issue** | `https://github.com/{owner}/{repo}/issues/{M}`, sub-issue de #{N} | Canonical. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Carrega branch dedicada e PR(s) | GitHub audit log |
| **Provider cache** | `.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`, gitignored | AI working memory + scratch. Superset do body da sub-issue + blocos `<!-- not-flushed -->`. Nomeado pelo número da sub-issue | Cache local regenerável |
| **Phase artifacts** | `.ahrena/issues/issue-{N}/`, committed | `01-brief.md` … `06-quality-report.md` do fluxo Issue-Driven (vinculados à Issue parent) | Git |

O cache local é provider-específico: agentes Claude usam `.claude/plans/plan-{M}-{slug}.md`; agentes Cursor usam `.cursor/plans/plan-{M}-{slug}.md`. Não há cache compartilhado entre providers — cada um carrega seu working memory independentemente, regenerado a partir da sub-issue via `kata-load-plan-from-subissue`.

## Schema do body da sub-issue Plan (canonical)

```markdown
## Summary

{2-4 frases descrevendo o objetivo executável deste Plan. Tipicamente uma fatia do escopo da Issue parent.}

Parent: #{N}

## Plan

### Objective
{Por que esta unidade existe e o que entrega ao final — 1 a 3 frases.}

### Steps
- [ ] Step 1
- [ ] Step 2
...

### Dependencies
{Outros Plans, Issues ou PRs de que esta tarefa depende; "None" se não houver.}

### Risks
{Riscos conhecidos e mitigações; "None identified" se não houver.}

### Open Questions
{Perguntas em aberto que precisam de decisão antes/durante execução; "None" se não houver.}
```

Schema do cache local `.claude/plans/plan-{M}-{slug}.md` (ou `.cursor/plans/plan-{M}-{slug}.md`): **superset** do body da sub-issue. Carrega front-matter YAML para metadados de sessão + o body completo espelhado + seções locais marcadas.

**Front-matter** (canonical):

```yaml
---
plan_id: "{M}"              # número da sub-issue Plan; "draft" pré-promoção
title: "{slug}"             # slug usado na branch (e no nome do arquivo enquanto draft)
status: todo | development | to review | review | done | abandoned
                            # | draft (estado local-only, pré-promoção)
                            # | to release | release (eixo release)
agent: claude | cursor
issue: "{owner/repo#M}"     # "TBD" enquanto draft
parent: "{owner/repo#N}"    # Issue parent (User Story | Bug | Tech Task)
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
promoted_at: "YYYY-MM-DDTHH:MM:SSZ"   # OPCIONAL — preenchido na transição draft → todo
---
```

Os campos `merge_commit:` e `closed_at:` NÃO aparecem no front-matter — são derivados das APIs do GitHub no audit pós-merge (ver §Auditoria de fechamento). O campo `promoted_at:` registra o timestamp UTC da promoção plan-first (transição `draft → todo`); preencher apenas para planos que nasceram em `draft`.

**Body**: superset do body da sub-issue + seções locais marcadas com blocos `<!-- not-flushed -->`:

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

`kata-flush-plan-to-subissue` filtra blocos `<!-- not-flushed -->` antes de gravar no body da sub-issue. O front-matter NUNCA é flushado para o GitHub — vive apenas no cache local.

## Ciclo de vida do Plan

O ciclo opera sobre **dois eixos disjuntos**:

### Eixo A — Dev cycle (Plan derivado de User Story / Bug / Tech Task)

```
(draft, local-only) ⇢ — → todo → development → to review → review → done
                                                       ↘
                                                       abandoned (terminal alternativo, qualquer estágio)
```

- `(draft)` — estado **local-only** pré-`todo`. Vive no front-matter do plan-arquivo (`.claude/plans/plan-{slug}.md` ou `.cursor/plans/plan-{slug}.md`) com `status: draft, issue: TBD`. Não existe como label canônica no GitHub. A transição `draft → todo` é a **promoção plan-first** (ver Guardrail plan-first abaixo).
- `— → todo` — sub-issue Plan criada com template + labels + Issue Type + Why/What/How; sem branch, sem worktree, sem assignee ainda.
- `todo → development` — Plan picado para execução: branch remota criada via `gh issue develop`; worktree per `lex-git-worktrees`; assignee aplicado (quem se compromete a executar); primeiro commit iminente.
- `development → to review` — implementação concluída; PR aberto; flush prévio do cache local via `kata-flush-plan-to-subissue`.
- `to review ↔ review` — reviewer (humano ou Argos) entra e sai do ciclo de revisão ativa.
- `to review → done` — PR mergeado; sub-issue Plan fechada via `Closes #{M}`.
- `abandoned` — terminal alternativo; Plan descartado em qualquer estágio.

### Eixo B — Release cycle (Plan dedicada à release)

```
— → to release → release → done
                       ↘
                       abandoned (terminal alternativo, qualquer estágio)
```

- `— → to release` — release sub-issue criada por Janus, listando os PRs mergeados desde o último tag.
- `to release → release` — release em execução; humano aprovou bump/changelog.
- `release → done` — tag empurrada, build de release passou, GitHub Release publicada.
- `abandoned` — release abortada antes do tag.

A mutex de labels é **intra-artefato** (dentro de cada Issue/PR), não cross-artifact: uma sub-issue carrega exatamente uma label `status: <name>` por vez. HARD-GATE em `lex-issue-status` proíbe aplicar labels do Eixo B em sub-issue de feature, e vice-versa.

## Gate 1 — Plan criado (`— → todo`)

Owner: `warrior-eunomia` (fallback: agente da sessão enquanto Eunomia não estiver shipada).

Toda sub-issue Plan DEVE ser criada por Eunomia via `kata-decompose-issue-into-plans` (downstream da análise da Issue parent) ou `kata-plan-task` (Plan avulso top-level vinculado a uma Issue existente). O agente executa os 4 passos abaixo antes de marcar a label `status: todo`:

1. **Confirmar Issue parent existe e está bem formada** (per `lex-issue-first` e `lex-issue-quality`). Sem Issue parent aberta, não há Plan a criar — invocar `kata-contributing-issue` primeiro para abrir a Issue.
2. **Criar a sub-issue Plan** vinculada à Issue parent via MCP `create_issue` (preferido) ou `gh issue create --type Task` (fallback), aplicando o template Plan, labels obrigatórias e Issue Type `Task`.
3. **Preencher o body da sub-issue com o plano canônico** (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) via MCP `update_issue` ou `gh issue edit --body-file <path>` (fallback per `lex-mcp` regra 4).
4. **Verificar Issue Type pós-criação** (per `lex-issue-type-verified`) — Plans são sempre `Task`.

Branch, worktree e assignee **NÃO** são preconditions de `— → todo`. Eles pertencem a `todo → development`.

```
<HARD-GATE>
warrior-eunomia (ou o agente da sessão atuando como fallback enquanto Eunomia
não estiver shipada) MUST NOT aplicar a label `status: todo` em uma sub-issue
Plan sem satisfazer TODOS os 4 passos canônicos:

  (a) Issue parent aberta e em conformidade com lex-issue-first e
      lex-issue-quality (template, labels, Issue Type compatível,
      Why/What/How preenchidos)
  (b) Sub-issue Plan criada vinculada à Issue parent via MCP create_issue
      (preferido) ou gh issue create --type Task (fallback), com template
      Plan e labels obrigatórias aplicadas
  (c) Body da sub-issue preenchido com plano canônico (Summary + Plan
      contendo Objective, Steps, Risks, Dependencies, Open Questions)
      via MCP update_issue ou gh issue edit --body-file (fallback)
  (d) Issue Type verificado como Task per lex-issue-type-verified

Esta regra aplica-se a TODO Plan (top-level ou subtask de decomposição),
independente de:
  - tamanho percebido ("é só um chore")
  - urgência ("incêndio em produção")
  - quem pediu ("o CEO solicitou")
  - confiança da equipe ("já testamos muito")

Exceção declarada: nenhuma. Branch, worktree e assignee NÃO são
preconditions deste gate — pertencem ao gate todo → development.
</HARD-GATE>
```

### Guardrail plan-first

Plan-first é caminho legítimo: o agente (ou humano) PODE rascunhar um plano localmente em `.claude/plans/plan-{slug}.md` ou `.cursor/plans/plan-{slug}.md` carregando `status: draft` no front-matter (e `issue: TBD` enquanto não há sub-issue correspondente). O que é PROIBIDO é iniciar execução (branch, commits, PR) sem antes promover o rascunho a sub-issue Plan no GitHub.

Quando o usuário sinalizar intenção de plano sem referenciar uma Issue (e.g. "vamos planejar X"), o agente PODE seguir um de dois caminhos:

- **Caminho A (issue-first):** invocar `kata-contributing-issue` para abrir a Issue parent imediatamente; em seguida `kata-decompose-issue-into-plans` ou `kata-plan-task` para criar a(s) sub-issue(s) Plan; depois `kata-load-plan-from-subissue` para materializar o cache local. Não há estado `draft` neste caminho.

- **Caminho B (plan-first / draft):** rascunhar o plano direto em `.claude/plans/plan-{slug}.md` (ou `.cursor/plans/...`) com front-matter `status: draft, issue: TBD`. Quando o rascunho estiver maduro, **promover** em passo atômico:
  1. `kata-contributing-issue` cria a Issue parent se ainda não houver.
  2. `kata-decompose-issue-into-plans` ou `kata-plan-task` cria a sub-issue Plan canônica.
  3. Renomear o arquivo de `plan-{slug}.md` para `plan-{M}-{slug}.md` (onde `{M}` é o número da sub-issue criada).
  4. Atualizar front-matter — `status: draft → todo`, `issue: TBD → {owner/repo#M}`, registrar `promoted_at` com timestamp UTC.
  5. Aplicar label canônica `status: todo` na sub-issue recém-criada (Gate 1 de Eunomia).

`status: draft` é estado **puramente local** — vive no front-matter do plan-arquivo, NÃO existe como label canônica no GitHub. A label `status: todo` só aparece após a promoção. `kata-load-plan-from-subissue` retorna `PROMOTION_REQUIRED` (sinal de fluxo, não erro fatal) quando recebe um plan-arquivo orphan com `status: draft` ou `issue: TBD`, orientando o agente invocador a acionar a promoção antes da materialização canônica.

## Gate 2 — Plan iniciado (`todo → development`)

Owner: `warrior-athena`.

Athena assume o Plan quando a execução vai começar (não antes). Em `todo → development`, Athena executa os 3 passos canônicos:

1. **Criar a branch remota** e vinculá-la à sub-issue Plan via `gh issue develop {M} --base main --name {type}/{M}-{slug}` (registra a branch como "Development" na sidebar do GitHub).
2. **Criar a worktree** per `lex-git-worktrees` em `.worktrees/{M}-{slug}/`.
3. **Aplicar assignee** na sub-issue Plan (quem se compromete a executar — humano ou identidade de agente).

Aplicar `status: development` sem os 3 passos completos é PROIBIDO. Athena não inicia Phase 4 da Issue-Driven sem o gate satisfeito.

```
<HARD-GATE>
warrior-athena MUST NOT aplicar a label `status: development` em uma
sub-issue Plan sem satisfazer TODOS os 3 passos canônicos:

  (a) Branch remota criada e vinculada à sub-issue Plan via
      gh issue develop {M} --base main --name {type}/{M}-{slug}
  (b) Worktree criado per lex-git-worktrees em
      `.worktrees/{M}-{slug}/`
  (c) Assignee aplicado na sub-issue Plan (a pessoa ou agente que
      se compromete a executar)

Esta regra aplica-se a TODA transição todo → development, independente de:
  - tamanho percebido ("é só um chore")
  - urgência ("incêndio em produção")
  - quem pediu ("o CEO solicitou")
  - confiança da equipe ("já testamos muito")

Exceção declarada: nenhuma. Athena não inicia execução sem branch,
worktree e assignee — esses três são a amarração mínima para audit
e para evitar trabalho fantasma fora de uma sub-issue Plan.
</HARD-GATE>
```

## Owners de cada transição

### Tabela A — Dev cycle (Eunomia / Athena / Argos)

| Transição | Owner | Gatilho |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente da sessão) | Cria sub-issue Plan + preenche body canônico + verifica Issue Type |
| `todo → development` | `warrior-athena` | Cria branch via `gh issue develop` + worktree + assignee; inicia Phase 4 |
| `development → to review` | `warrior-athena` | `kata-pr-prepare` abre PR; flush prévio do cache via `kata-flush-plan-to-subissue` |
| `to review → review` | `warrior-argos` | Argos inicia ciclo de revisão automatizada |
| `review → to review` | `warrior-argos` | Argos termina ciclo sem aprovar (changes-requested ou awaiting-human) |
| `to review → done` | `warrior-athena` | Humano aprova PR; merge fecha sub-issue Plan via `Closes #{M}` |
| `qualquer → abandoned` | criador ou owner atual | Plan descartado |

### Tabela B — Release cycle (Janus)

| Transição | Owner | Gatilho |
|---|---|---|
| `— → to release` | `warrior-janus` | Abre release sub-issue; popula `Tracks: #N1, #N2, ...` com PRs mergeados desde o último tag |
| `to release → release` | `warrior-janus` | `kata-release-prepare` inicia; gate humano de bump/changelog |
| `release → done` | `warrior-janus` | `kata-release-publish` conclui (tag empurrada, validate-tag passa, Release criada); notificação via MCP em `notifications.channels.release_notify` |
| `qualquer → abandoned` | `warrior-janus` | Release abortada antes do tag |

Cada owner DEVE:

- Aplicar a label `status: <name>` correspondente na sub-issue Plan no GitHub (per `lex-issue-status`).
- Aplicar a label `status: <name>` correspondente no PR (a partir de `to review`).
- Disparar `kata-flush-plan-to-subissue` se o cache local estiver à frente do body da sub-issue.

## Auditoria de fechamento

Para audit pós-merge, dois campos são derivados de APIs nativas do GitHub (sem front-matter dedicado no Plan):

| Campo lógico | Fonte canônica | Comando |
|---|---|---|
| `closed_at` | `Issue.closedAt` | `gh issue view {M} --json closedAt --jq .closedAt` |
| `merge_commit` | `PullRequest.mergeCommit.oid` | `gh pr view {PR} --json mergeCommit --jq .mergeCommit.oid` |

Para arquivos legados em `.ahrena/issues/_legacy/` que mantêm YAML front-matter histórico, `merge_commit:` e `closed_at:` são reconhecidos como front-matter opcional aceito — preserva o audit sem retrofit.

## Cadência de load/flush

Sincronização entre o cache local e o body da sub-issue Plan ocorre em **4 gatilhos canônicos** (não em cada toggle):

| Gatilho | Operação |
|---|---|
| Início de sessão / handoff entre agentes | `kata-load-plan-from-subissue` |
| Transição de label `status:` na sub-issue/PR | `kata-flush-plan-to-subissue` |
| Step do plano marcado como concluído (`[ ]` → `[x]`) | `kata-flush-plan-to-subissue` |
| Fim de sessão (heartbeat conclui ou owner sai) | `kata-flush-plan-to-subissue` |

Toggles intermediários, edições de scratch (`<!-- not-flushed -->`) e working notes são **livres** — não disparam flush. Documentação operacional em `codex-agent-planning` §9.

## Relação com outros artefatos

- **Issue parent (User Story / Bug / Tech Task):** carrega problema, motivação, AC. Não tem branch própria. Geralmente fecha via `Closes #{N}` no último PR da última sub-issue Plan.
- **Sub-issue Plan:** carrega o plano canônico no body; a label `status: <name>` é a única fonte de verdade para o estado.
- **PR:** a partir de `to review`, o PR carrega a label `status: <name>` correspondente, atualizada por Athena/Argos/Janus conforme o estado avança. Sync da label é responsabilidade do owner da transição.
- **`.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`:** cache local provider-specific regenerável; nunca commitado; reconstruído por `kata-load-plan-from-subissue` em fresh clone.
- **`.ahrena/issues/issue-{N}/`:** committed; recebe Phase artifacts do fluxo Issue-Driven da Issue parent #{N} (per `lex-issue-driven`).
- **Checkpoint (`.checkpoint`):** o Plan cobre **task** (Steps, Decisões, Riscos no body da sub-issue); o checkpoint cobre **sessão** (foco da janela, hand-off entre Plans, threads paralelas). Sobreposição é PROIBIDA — ver `lex-checkpoint` regra 5.
- **ADR:** quando um Plan identifica uma decisão arquitetural relevante, um ADR DEVE ser aberto conforme `lex-issue-driven`. Exemplos de nome de arquivo: `ADR-008-use-event-sourcing-for-refund-audit-trail.md`, `ADR-007-use-fastapi-routers.md`, `ADR-001-use-event-sourcing-for-ledger.md`, `ADR-002-migrate-to-fastapi.md`.
- **Heartbeat de sessão:** sessão Claude Code que opera no Plan é registrada em `.ahrena/workflow/sessions/<session-id>.json` (per `codex-session-tracking`); não vive no body da sub-issue.

### Plan vs cache local vs `.checkpoint` — o que vai onde

| Conteúdo | Vive em |
|---|---|
| Objective, Steps `[x]`, Risks, Dependencies, Open Questions | Body da sub-issue Plan (canonical) |
| Decisões arquiteturais relevantes | ADR em `docs/adr/` (referenciado pelo Plan) |
| Working notes, debugging diary, scratch | Cache local em blocos `<!-- not-flushed -->` |
| Foco geral da janela de trabalho (Session focus) | `.checkpoint` — gitignored |
| Ponteiros para múltiplos Plans ativos (Active plans) | `.checkpoint` — gitignored |
| Threads paralelas que não viraram Plan (Open threads) | `.checkpoint` — gitignored |

Em caso de dúvida: conteúdo estrutural vai para o body da sub-issue Plan; conteúdo volátil para o cache local em bloco não-flushed; foco da sessão para `.checkpoint`.

## Exemplos

### Correto — fluxo Top-down (Issue first)

```
Usuário: "Precisamos migrar o ledger para event sourcing — abra uma User Story"
→ Agente invoca kata-contributing-issue (template user-story-for-api)
→ Issue #200 criada (Why/What/How, AC numerados, Issue Type Feature, label
  `user story 🎯`, status: todo via Gate 1 de lex-issue-quality)

Próxima sessão, agente decompõe:
→ Eunomia invoca kata-decompose-issue-into-plans 200
→ 3 sub-issues Plan criadas:
   #201 (Task) — refatorar Ledger aggregate para event sourcing
   #202 (Task) — implementar projection write-side
   #203 (Task) — migrar leitura via projection read-side
→ Cada sub-issue carrega Summary + Plan section
→ Eunomia aplica status: todo nas 3 sub-issues (Gate 1 OK)
→ Issue #200 permanece status: todo até o primeiro PR começar

Execução do Plan #201:
→ Athena (Gate 2): gh issue develop 201 --base main --name refactor/201-ledger-event-sourcing
→ Athena cria worktree em .worktrees/201-ledger-event-sourcing/
→ Athena aplica assignee fernandoseguim na sub-issue #201
→ Athena aplica status: development na sub-issue #201
→ kata-load-plan-from-subissue 201 materializa .claude/plans/plan-201.md
→ Implementação roda; kata-flush-plan-to-subissue 201 em cada Step concluído
→ Athena abre PR via kata-pr-prepare: status: to review na #201 + PR
→ Argos entra: status: review; sai sem aprovar: status: to review
→ Humano aprova; merge fecha #201 via Closes #201: status: done

Repete para #202, #203. Quando #203 mergeia com Closes #200 no PR body,
Issue parent #200 fecha automaticamente.

Release cycle (separada):
→ Janus abre release sub-issue (e.g. #210); Tracks: #201-PR, #202-PR, #203-PR
→ Janus aplica status: to release na release sub-issue
→ Janus inicia kata-release-prepare: status: release
→ Janus conclui kata-release-publish: status: done
```

### Correto — fluxo Plan-first, Caminho A (issue-first imediato)

```
Usuário: "vamos planejar a migração do logger pra Loguru"
→ Agente reconhece: não há Issue referenciada
→ Agente invoca kata-contributing-issue (template tech-task ou user-story)
→ Issue parent #220 criada (Why/What/How, AC)
→ Agente invoca kata-decompose-issue-into-plans 220
→ 2 sub-issues Plan #221, #222 criadas
→ Eunomia aplica status: todo nas 2 sub-issues
→ kata-load-plan-from-subissue 221 materializa .claude/plans/plan-221.md
→ Execução segue per Gate 2 (Athena)
```

### Correto — fluxo Plan-first, Caminho B (draft → promoção)

```
Usuário: "vamos rascunhar um plano para refatorar o logger"
→ Agente cria .claude/plans/plan-logger-refactor.md com front-matter:
   status: draft, issue: TBD, parent: TBD, plan_id: "draft"
→ Rascunho amadurece em N edições (Objective, Steps, Risks)
→ Usuário aprova: "ok, vamos para execução"
→ Agente promove em passo atômico:
   1. kata-contributing-issue → Issue parent #220 (tech-task)
   2. kata-plan-task → sub-issue Plan #221 (Task), body do rascunho copiado
   3. mv .claude/plans/plan-logger-refactor.md .claude/plans/plan-221.md
   4. front-matter: status: draft → todo, issue: TBD → guardiatechnology/ahrena#221,
      parent: guardiatechnology/ahrena#220, promoted_at: 2026-05-13T19:00:00Z
   5. Eunomia aplica label "status: todo" em #221 (Gate 1 OK)
→ Execução segue per Gate 2 (Athena)
```

### Incorreto

```
Tarefa: implementar feature X
→ Agente cria branch direto via git checkout -b sem abrir Issue parent
→ ❌ Viola lex-issue-first; sem Issue parent, não há Plan a criar

→ Agente cria arquivo .claude/plans/plan-feature-x.md com status: draft
  e em seguida cria branch via git checkout -b feat/x sem promover o
  rascunho a sub-issue Plan no GitHub
→ ❌ Viola guardrail plan-first; rascunho local com status: draft é
  permitido, mas iniciar execução (branch, commits, PR) sem antes
  promover o rascunho via kata-contributing-issue +
  kata-decompose-issue-into-plans (Caminho B) é proibido

→ Agente aplica label status: todo na sub-issue Plan sem preencher o body
→ ❌ Viola Gate 1 precondition (c): body precisa carregar Summary +
   Plan section antes de status: todo definitivo

→ Agente aplica label status: development na sub-issue sem criar a branch
  remota nem o worktree
→ ❌ Viola Gate 2 preconditions (a), (b) e (c): branch via gh issue develop,
  worktree em .worktrees/, e assignee aplicado são os três passos mínimos

→ Agente aplica label status: to release em sub-issue de feature
→ ❌ Viola mutex intra-artefato de lex-issue-status: `to release`
   pertence ao Eixo B (release sub-issue), proibido no Eixo A
```

## Validação Automatizada

- **Ferramenta:** verificação pelo agente antes de qualquer execução multi-etapa; `kata-plan-task` e `kata-decompose-issue-into-plans` como pontos de entrada canônicos; revisão de PR confirma que a label `status:*` da sub-issue Plan e a label `status:*` do PR estão alinhadas, e que o body da sub-issue carrega Summary + Plan section. Argos enumera `.claude/plans/*.md` e `.cursor/plans/*.md` na revisão; para cada `plan_id` no cache, verifica que existe uma sub-issue correspondente no GitHub (orphans são bloqueio).
- **Momento:** antes de qualquer execução de tarefa multi-etapa — sem exceção; e em cada transição de estado.
- **Métrica:** 0 tarefas multi-etapa executadas sem sub-issue Plan aberta; 0 arquivos em `.claude/plans/` ou `.cursor/plans/` sem sub-issue correspondente; 0 PRs mergeados com `status:` divergente entre sub-issue e PR; 100% das transições executadas pelo owner declarado; 100% das release sub-issues com `Tracks:` listando os PRs mergeados desde o último tag.

## Referências

- `lex-issue-status` — labels canônicas de status; split Tabela A (dev) / Tabela B (release)
- `lex-issue-type-verified` — verificação programática do Issue Type pós-criação
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-git-worktrees` — preconditions dos gates
- `lex-mcp` — preferência MCP + fallback CLI para `gh issue edit`
- `lex-checkpoint` — rastreamento de estado de sessão (complementar)
- `lex-issue-driven` — fluxo Issue-Driven; Phase artifacts em `.ahrena/issues/issue-{N}/`
- `codex-agent-planning` — manual operacional do modelo hierárquico (load → edit → flush)
- `kata-plan-task` — procedimento operacional para criar Plan avulso top-level
- `kata-decompose-issue-into-plans` — decomposição de Issue parent em sub-issues Plan
- `kata-contributing-issue` — criação de Issue parent (precondition do Gate 1)
- `kata-load-plan-from-subissue` — materializa cache local a partir do body da sub-issue Plan
- `kata-flush-plan-to-subissue` — flusha cache local (filtrando `<!-- not-flushed -->`) para o body da sub-issue
- `kata-session-heartbeat` — atualização do heartbeat de sessão
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
