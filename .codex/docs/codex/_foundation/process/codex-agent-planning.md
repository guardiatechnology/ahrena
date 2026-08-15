# Codex: Planejamento de Tarefas por Agentes

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação, manutenção e ciclo de vida de Plans no contexto Ahrena

## 1. Modelo hierárquico Issue → Plan → PR

```
Issue (User Story | Bug | Tech Task)            ← problema, Why/What/How, AC
   │
   ├─ Plan sub-issue #M1 (Task)                  ← unidade executável #1
   │     ├─ status: todo | development | to review | review | done
   │     ├─ branch: {type}/{M1}-{slug}
   │     └─ PR(s) que fecham este Plan
   │
   ├─ Plan sub-issue #M2 (Task)
   │     └─ ...
   │
   └─ Plan sub-issue #M3 (Task)
         └─ ...
```

| Camada | Localização | Papel | Versionamento |
|---|---|---|---|
| **Issue parent** | `https://github.com/{owner}/{repo}/issues/{N}` | Problema, AC, motivação. Não tem branch própria | GitHub audit log |
| **Plan sub-issue** | `https://github.com/{owner}/{repo}/issues/{M}`, sub-issue de #{N} | Canonical. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Carrega branch e PR(s) | GitHub audit log |
| **Provider cache** | `.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`, gitignored | AI working memory + scratch. Superset do body + blocos `<!-- not-flushed -->`. Nomeado pelo número da sub-issue | Cache local regenerável |
| **Phase artifacts** | `.ahrena/issues/issue-{N}/`, committed | `01-brief.md` … `06-quality-report.md` do fluxo Issue-Driven (vinculados à Issue parent) | Git |

### Resolução do path do cache local

```
1. Determinar o provider (Claude Code → .claude/plans/, Cursor → .cursor/plans/)
2. Nomear o arquivo como plan-{M}-{slug}.md, onde {M} é o número da sub-issue
3. Confirmar via .gitignore que o diretório do provider está excluído
```

> **Modelo legado (deprecated):** arquivos em `.claude/plans/` **sem sub-issue Plan correspondente no GitHub** são considerados zombies (independente do pattern do nome — o novo canônico `plan-{M}-{slug}.md` sempre mapeia 1:1 com `{M}` = número da sub-issue). Não criar arquivos novos sem sub-issue Plan aberta no GitHub. Caches existentes que não mapeiam para uma sub-issue devem ser triados em `.ahrena/issues/_legacy/` ou descartados.

---

## 2. Nomeação do cache local

```
.claude/plans/plan-{M}-{slug}.md      (agente Claude)
.cursor/plans/plan-{M}-{slug}.md      (agente Cursor)
```

| Campo | Regra |
|---|---|
| `{M}` | Número da sub-issue Plan no GitHub. Sem padding, sem prefix — `plan-201.md`, não `plan-0201.md` nem `plan-201-slug.md` |

Exemplos:
- `.claude/plans/plan-201.md` — cache do Plan da sub-issue #201
- `.cursor/plans/plan-222.md` — cache do Plan da sub-issue #222

O cache é gitignored — não aparece em `git status` nem em `git log`. Para inspecionar Plans sem clonar:

```bash
gh issue view {M} --json body --jq .body
```

Para sincronizar localmente: `kata-load-plan-from-subissue {M}`.

---

## 3. Template do body da sub-issue Plan (canonical) e do cache local

### 3a. Body da sub-issue Plan (canonical)

```markdown
## Summary

{2-4 frases descrevendo o objetivo executável deste Plan — tipicamente uma
fatia do escopo da Issue parent.}

Parent: #{N}

## Plan

### Objective
Refatorar o aggregate Ledger para event sourcing — substituir CRUD direto
em PostgreSQL por append-only event store + projection write-side.

### Steps
- [x] 1. Mapear comandos atuais do Ledger
- [x] 2. Modelar eventos canônicos (LedgerEntryRecorded, LedgerEntryReversed)
- [ ] 3. Implementar EventStore com optimistic concurrency
- [ ] 4. Migrar handlers para emit-only
- [ ] 5. Testes de invariante (saldo nunca negativo)

### Dependencies
- Plan #202 (projection write-side) — pode rodar em paralelo
- Plan #203 (read-side) — bloqueado por este Plan

### Risks
- Migration de dados existentes — mitigado por shadow-write durante cutover
- Optimistic concurrency em alta contenção — benchmark em staging primeiro

### Open Questions
- None
```

O body da sub-issue é gravado por:
- `kata-decompose-issue-into-plans` na criação (downstream da Issue parent)
- `kata-plan-task` quando o Plan é avulso (top-level vinculado a uma Issue existente)
- `kata-flush-plan-to-subissue` em cada gatilho de sync (transição, Step concluído, fim de sessão)

### 3b. Cache local `.claude/plans/plan-{M}-{slug}.md` (working memory)

```markdown
## Summary
... (espelha o body da sub-issue)

## Plan
... (espelha o body da sub-issue)

<!-- not-flushed -->
## Working notes
- 23:30 — terminou Step 2; eventos modelados em src/ledger/events.py
- Decision: usar UUID v7 como event_id (per lex-entities)
- Bug encontrado em EventStore: retry sem idempotency key — escrever
  test reproduzindo antes de fixar

## Next actions
1. Step 3 — EventStore com optimistic concurrency
2. Step 4 — handlers emit-only
3. Step 5 — testes de invariante

## Scratch
gh issue develop registra branch como "Development" na sidebar.
Limite do body da Issue: ~65KB.
<!-- /not-flushed -->
```

O cache **não tem front-matter YAML** — a sub-issue do GitHub já carrega toda a metadata (assignees, labels `status:*`, milestones, dates). Blocos `<!-- not-flushed -->` são filtrados antes do flush para a sub-issue.

> **Front-matter legacy:** arquivos em `.ahrena/issues/_legacy/` (deprecated) mantêm YAML front-matter histórico (`plan_id`, `status`, `claude_session`, `merge_commit`, `closed_at`). Esse formato é reconhecido para audit, mas NÃO replicar em novos Plans.

---

## 4. Estados do ciclo de vida (enum unificado)

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, qualquer estágio)
```

| Status | Quando usar | Owner que transiciona |
|---|---|---|
| `todo` | Sub-issue Plan criada com body canônico, sem branch nem worktree, ainda não começou | Quem cria: `warrior-eunomia` (fallback: agente da sessão) |
| `development` | Implementação em curso (Athena Phase 4); branch + worktree + assignee aplicados | `warrior-athena` |
| `to review` | PR aberto, esperando reviewer pegar | `warrior-athena` (entrada); `warrior-argos` (retorno do `review`) |
| `review` | Argos ou humano revisando ativamente | `warrior-argos` (entrada e saída) |
| `to release` | (Eixo B apenas) Release sub-issue criada, esperando release iniciar | `warrior-janus` |
| `release` | (Eixo B apenas) Release em execução (tag/build/publish) | `warrior-janus` |
| `done` | PR mergeado e sub-issue Plan fechada via `Closes #{M}` (Eixo A) OU release publicada (Eixo B) | `warrior-athena` (Eixo A) / `warrior-janus` (Eixo B) |
| `abandoned` | Plan descartado (qualquer estágio) | Criador ou owner atual |

**Estado canônico:** o `status:` vive como **label** na sub-issue Plan no GitHub (e no PR, a partir de `to review`). Não há "front-matter do Plan" — o body da sub-issue é canonical; o cache local é regenerável.

### Split em dois eixos

- **Eixo A — Dev cycle** (Plan derivado de User Story / Bug / Tech Task): `todo → development → to review → review → done` + `abandoned`. Owners: Eunomia/Athena/Argos.
- **Eixo B — Release cycle** (release sub-issue exclusivamente): `to release → release → done` + `abandoned`. Owner: Janus.

Mutex é **intra-artefato** (dentro de cada sub-issue/PR), não cross-artifact. Aplicar label do Eixo B em sub-issue de feature (ou vice-versa) é proibido per HARD-GATE em `lex-issue-status`.

---

## 5. Owners de cada transição (visão de fluxo)

### Eixo A — Dev cycle (Eunomia/Athena/Argos)

```
Eunomia: — ──→ todo                                                  [Plan sub-issue criada]
                 │
                 ▼
Athena:  todo ──→ development ──→ to review                          [branch + worktree + assignee]
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ done   (humano aprova; merge fecha sub-issue)
                                       │
                  qualquer ──→ abandoned (terminal alternativo)
```

### Eixo B — Release cycle (Janus)

```
Janus:   — ──→ to release ──→ release ──→ done                      [release sub-issue dedicada]
                  │
                  qualquer ──→ abandoned (release abortada antes do tag)
```

Cada owner atualiza simultaneamente:

1. Body da sub-issue Plan via `kata-flush-plan-to-subissue` (apenas se houve edição no cache local).
2. Label `status: <name>` na sub-issue Plan (per `lex-issue-status` mutex intra-artefato).
3. Label `status: <name>` no PR (a partir de `to review`, apenas no Eixo A).

---

## 6. Walkthrough A — Top-down (Issue parent existe)

Cenário: usuário aponta uma Issue parent existente e pede para decompor em Plans executáveis.

### Passo 1 — Verificar Issue parent

```bash
gh issue view 200 --repo {owner}/{repo} --json title,body,labels,issueType
```

Confirma: Issue Type `Feature` (ou `Bug`/`Task`), template usado, AC numerados, labels obrigatórias, Why/What/How preenchidos. Se algo falta, invocar `kata-contributing-issue` para completar antes.

### Passo 2 — Decomposição em sub-issues Plan

```bash
# Eunomia invoca kata-decompose-issue-into-plans
# Lê Issue parent, propõe N sub-issues Plan, confirma com usuário,
# cria cada sub-issue via MCP create_issue (Issue Type Task) vinculada
# à parent, preenche body canônico (Summary + Plan), aplica labels
# obrigatórias, verifica Issue Type, aplica status: todo
```

Resultado típico:

```
Issue #200 (Feature) — "Event sourcing for ledger"
├── #201 (Task)   — "Refactor Ledger aggregate"
├── #202 (Task)   — "Implement projection write-side"
└── #203 (Task)   — "Migrate read-side via projection"
```

### Passo 3 — Eunomia aplica `status: todo` nas 3 sub-issues (Gate 1 OK)

Cada sub-issue agora tem body canônico, Issue Type `Task`, labels obrigatórias. Branch, worktree, assignee NÃO foram aplicados — pertencem a Athena no Gate 2.

### Passo 4 — Athena pega o primeiro Plan executável (#201)

```bash
# Gate 2 — todo → development
gh issue develop 201 --base main --name refactor/201-ledger-event-sourcing
git worktree add .worktrees/201-ledger-event-sourcing refactor/201-ledger-event-sourcing
gh issue edit 201 --add-assignee fernandoseguim
gh issue edit 201 --add-label "status: development" --remove-label "status: todo"
```

### Passo 5 — Carrega cache local e executa

```bash
kata-load-plan-from-subissue 201   # materializa .claude/plans/plan-201.md
# implementação roda no worktree
# em cada Step concluído: kata-flush-plan-to-subissue 201
# em fim de sessão: kata-flush-plan-to-subissue 201
```

### Passo 6 — Abre PR

```bash
# Athena via kata-pr-prepare:
# - kata-flush-plan-to-subissue 201 (flush final)
# - gh pr create --title "..." --body "Closes #201\nRefs #200" ...
# - aplica status: to review na sub-issue #201 + PR
```

### Passo 7 — Review e merge

Argos entra (`status: review`), sai (`status: to review`); humano aprova; merge fecha sub-issue #201 via `Closes #201`; Athena aplica `status: done`. Repete para #202, #203. Quando o último PR fecha Issue parent #200 (`Closes #200`), tudo encerra.

---

## 7. Walkthrough B — Plan-first (intenção sem Issue parent)

Cenário: usuário diz "vamos planejar a migração do logger pra Loguru" sem referenciar Issue alguma.

### Passo 1 — Agente NÃO materializa arquivo local

Materializar `.claude/plans/plan-XXX.md` agora violaria o guardrail plan-first de `lex-agent-planning`. Agente pausa e segue a sequência canônica.

### Passo 2 — Cria a Issue parent

```bash
# Agente invoca kata-contributing-issue
# Pergunta tipo: User Story, Bug, ou Tech Task?
# Usuário escolhe Tech Task (refator interno sem AC voltado a usuário final)
# Issue #220 criada com template tech-task, Issue Type Task,
# Why/What/How preenchidos, labels obrigatórias, status: todo
```

### Passo 3 — Decomposição em Plans

```bash
# Eunomia invoca kata-decompose-issue-into-plans 220
# Propõe 2 sub-issues:
#   #221 (Task) — "Migrate framework code to loguru"
#   #222 (Task) — "Migrate tooling and scripts to loguru"
# Confirma com usuário; cria sub-issues; preenche body canônico;
# aplica status: todo nas duas
```

### Passo 4 — A partir daqui, é Walkthrough A

Athena pega #221, executa Gate 2 (`todo → development`), implementa, abre PR, etc.

A diferença entre Walkthrough A e B é apenas o passo inicial. Uma vez que existe Issue parent + sub-issues Plan no GitHub, o fluxo converge.

---

## 8. Gate 1 — checklist completa (`— → todo`)

Eunomia (ou fallback) executa em sequência antes de marcar `status: todo`:

| Passo | Ação | Lex de referência |
|---|---|---|
| 1 | Confirmar Issue parent aberta e em conformidade | `lex-issue-first`, `lex-issue-quality` |
| 2 | Criar sub-issue Plan vinculada à parent via MCP `create_issue` (preferido) ou `gh issue create --type Task` (fallback) | `lex-mcp` |
| 3 | Preencher body da sub-issue com Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions) via MCP `update_issue` ou `gh issue edit --body-file` | `lex-agent-planning` |
| 4 | Verificar Issue Type pós-criação (deve ser `Task`) | `lex-issue-type-verified` |

Branch, worktree e assignee NÃO são preconditions deste gate.

## 9. Gate 2 — checklist completa (`todo → development`)

Athena executa em sequência antes de marcar `status: development`:

| Passo | Ação | Lex de referência |
|---|---|---|
| 1 | Criar branch remota e vincular à sub-issue: `gh issue develop {M} --base main --name {type}/{M}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 2 | Criar worktree em `.worktrees/{M}-{slug}/` per `lex-git-worktrees` | `lex-git-worktrees` |
| 3 | Aplicar assignee na sub-issue Plan (humano ou identidade de agente que se compromete a executar) | `lex-issue-quality` |

Aplicar `status: development` sem os 3 passos é PROIBIDO.

---

## 10. Quando um Plan é obrigatório (e quando não é)

### Obrigatório

- Tarefa com 2+ etapas encadeadas
- Qualquer operação que toque 2+ arquivos
- Toda invocação de warrior ou cry (por definição multi-etapa)
- Qualquer tarefa que produza artefatos permanentes (arquivos, commits, PRs, posts)

### Não obrigatório (etapa única trivial)

- Editar um único arquivo com instrução direta e precisa
- Ler/consultar arquivos sem escrita
- Executar um único comando isolado sem efeito colateral permanente
- Responder uma pergunta factual

### Zona cinzenta — usar Plan por precaução

- Tarefa aparentemente simples que pode se ramificar (ex.: "corrigir o bug" sem saber o escopo)
- Operação irreversível mesmo que de etapa única (ex.: deletar arquivos)

---

## 11. Relação entre Plans e outros artefatos

```
Issue parent (#N) — User Story | Bug | Tech Task
    │
    ├── label: status: <name> (Eixo A ou Eixo B na release sub-issue)
    │
    ├── Plan sub-issues (#M1, #M2, ..., Task)              canonical de cada unidade
    │   ├── body: Summary + Plan
    │   ├── label: status: <name>
    │   │
    │   ├── PR (label: status: <name>, a partir de "to review")    [só Eixo A]
    │   │
    │   ├── .claude/plans/plan-{M}-{slug}.md ou .cursor/plans/plan-{M}-{slug}.md  cache local
    │   │   └── superset do body + blocos <!-- not-flushed -->     gitignored
    │   │
    │   └── docs/adr/ADR-{n}-*.md (committed)                       se decisão arquitetural
    │
    ├── .ahrena/issues/issue-{N}/ (committed)                       Phase artifacts
    │   ├── 01-brief.md
    │   ├── 02-requirements.md
    │   ├── 03-architecture.md
    │   ├── 05-security-review.md
    │   └── 06-quality-report.md
    │
    ├── Heartbeat de sessão (.ahrena/workflow/sessions/<uuid>.json, gitignored)
    │
    └── ─ ─ ─ não confundir com ─ ─ ─
        Checkpoint (.checkpoint — gitignored, sessão)
```

- Body da sub-issue Plan, label da sub-issue e label do PR são sincronizados pelo owner em cada transição.
- ADR é aberto quando o Plan identifica uma decisão arquitetural relevante (mora em `docs/adr/`, não em `.ahrena/issues/`). Exemplos de nome: `ADR-008-use-event-sourcing-for-refund-audit-trail.md`, `ADR-007-use-fastapi-routers.md`, `ADR-001-use-event-sourcing-for-ledger.md`, `ADR-002-migrate-to-fastapi.md`.
- Heartbeat de sessão (`codex-session-tracking`) registra qual sessão Claude Code opera no Plan agora.
- Checkpoint NÃO é subordinado ao Plan; é artefato paralelo de **sessão**, não de **task**.

### Plan vs `.checkpoint` — delimitação canônica

Plan cobre **task**: Objetivo, Escopo, Steps `[x]`, Decisões fechadas, Riscos, Verificação. Vive no GitHub.
Checkpoint cobre **sessão**: Session focus, Active plans (ponteiros), Open threads, Notes. Gitignored.

| Conteúdo | Body da sub-issue Plan (canonical) | Cache local (working memory) | `.checkpoint` (sessão) |
|---|:---:|:---:|:---:|
| Steps `[x]` | ✅ | ✅ (espelhado) | ❌ |
| Decisões fechadas da task | ✅ (ou ADR) | ✅ (espelhado) | ❌ |
| Riscos da task | ✅ | ✅ (espelhado) | ❌ |
| Working notes / debugging diary | ❌ | ✅ (bloco `<!-- not-flushed -->`) | ❌ |
| Foco geral da janela de trabalho | ❌ | ❌ | ✅ |
| Lista de Plans ativos na sessão | ❌ | ❌ | ✅ |
| Threads paralelas que não viraram Plan | ❌ | ❌ | ✅ |
| Scratchpad livre, links, lembretes | ❌ | ❌ | ✅ |

Se o conteúdo se repete em ambos, há sobreposição — Plan vence (canonical). Sobreposição é PROIBIDA por `lex-checkpoint` regra 5 e por `lex-agent-planning`.

---

## 12. Cadência de load/flush

Sincronização entre o body da sub-issue Plan (canonical) e o cache local ocorre em **4 gatilhos canônicos**:

| Gatilho | Operação | Quem dispara |
|---|---|---|
| Início de sessão / handoff entre agentes | `kata-load-plan-from-subissue` | Athena, Argos, Janus (no início de cada sessão de trabalho num Plan) |
| Transição de label `status:` na sub-issue/PR | `kata-flush-plan-to-subissue` | Eunomia, Athena, Argos, Janus (no momento da transição) |
| Step do plano marcado como concluído (`[ ]` → `[x]`) | `kata-flush-plan-to-subissue` | Agente que conclui o Step |
| Fim de sessão (heartbeat conclui ou agente sai) | `kata-flush-plan-to-subissue` | `kata-session-heartbeat` no shutdown |

Toggles intermediários, edições de scratch (blocos `<!-- not-flushed -->`) e working notes são **livres** — não disparam flush. A regra é: o body da sub-issue deve refletir o estado **estável** (entre transições e Steps), não o estado **transiente** (durante working).

### Fluxo típico de uma sessão de trabalho

```
1. Athena entra (recebe handoff de Eunomia):
   → kata-load-plan-from-subissue {M}    (materializa cache local)
   → Gate 2: gh issue develop + worktree + assignee
   → aplica label status: development na sub-issue + PR (se já houver)
   → kata-flush-plan-to-subissue {M}     (registra a transição)

2. Athena trabalha:
   → edita arquivos no worktree
   → registra notas no cache local (blocos <!-- not-flushed -->)
   → marca Step [x] no cache
   → kata-flush-plan-to-subissue {M}     (Step concluído)

3. Athena abre PR via kata-pr-prepare:
   → flush final do cache pré-PR
   → create_pull_request (Closes #{M}, Refs #{N})
   → aplica status: to review na sub-issue + PR
   → kata-flush-plan-to-subissue {M}     (transição registrada)

4. Athena sai:
   → kata-session-heartbeat no shutdown dispara
   → kata-flush-plan-to-subissue {M}     (cleanup final)

5. Argos entra:
   → kata-load-plan-from-subissue {M}    (refresh do cache local)
   → ...
```

### Detecção de drift remoto (preflight)

`kata-flush-plan-to-subissue` por default executa preflight: lê o body atual da sub-issue, compara com o último estado conhecido, e bloqueia se houver edição remota desconhecida (outra sessão, edição via UI do GitHub). Oferece: (a) mostrar diff e abortar, (b) merge manual, (c) overwrite via `force=true`. Heartbeat de sessão permite identificar a sessão concorrente.

---

## 13. Loop de revisão pendente (estado `to review`)

Após Athena abrir o PR, o ciclo de review opera em **duas fases distintas e sequenciais** + um handler para CHANGES_REQUESTED:

### Fase A — Argos pre-flight cycles

Até 3 ciclos interativos `A1, A2, A3`, gateados por `AskUserQuestion` (Athena nunca invoca Argos sem confirmação). Cada ciclo: Athena pergunta "Quer review do Argos no HEAD atual?" — opções (a) sim, (b) pular para human review, (c) stop. Se (a) → Argos roda, publica review com marker idempotente; Athena lê findings; P0 BLOCKER address obrigatório; P1 AskUserQuestion (address ou defer); P2 nota. Commit + push se houve mudanças → HEAD novo. Repete até A3 ou usuário opta por (b)/(c).

### Fase B — Human nudge loop

Após Fase A encerrar, Athena pergunta o modo de agendamento: (a) `/loop` na sessão, (b) cron remoto, (c) manual. Modos (a)/(b) agendam 3 ciclos `H1, H2, H3` com 15 min entre cada. A cada cycle, Athena dispara notificação via MCP em `notifications.channels.pr_review_timeout` — mensagem escala em urgência (H1 "PR pronto", H2 "reminder #1", H3 "reminder #2, 2ª cobrança"). Consulta `gh pr view {N} --json reviewDecision,mergedAt`:

- `mergedAt != null` → transição `status: to review → done`, captura `mergeCommit.oid`, encerra loop.
- `reviewDecision == APPROVED` (sem merge) → comenta "PR aprovado, aguardando merge", encerra loop.
- `reviewDecision == CHANGES_REQUESTED` → **dispara Fase C**.
- Caso contrário → se H<3, reagenda; se H==3, encerra silenciosamente.

### Fase C — CHANGES_REQUESTED handler

Se humano pede mudanças durante Fase B: Athena lê os comentários do reviewer e pergunta via AskUserQuestion: (a) address agora, (b) defer pra follow-up Issue, (c) stop. Se (a) → Athena implementa, commita, push (HEAD novo). Após (a) ou (b) → **reset completo**: Athena reagenda o loop a partir da **Fase A** (3 novos Argos cycles no HEAD novo) — porque novos commits invalidam a review anterior do Argos. Não pula direto para Fase B.

Argos opera o sub-ciclo `to review ↔ review` em Fase A (com mudança de label durante a execução) e em Fase C quando re-invocado. Argos nunca move para `done`; transição `to review → done` é exclusiva de Athena ao detectar merge.

---

## 14. Boas práticas

1. **Escrever o Plan antes de saber tudo.** O objetivo é tornar a intenção visível, não produzir documentação perfeita. Um Plan impreciso que evolui é melhor que nenhum Plan.
2. **Manter Steps atômicos.** Cada Step deve ser verificável: feito ou não feito. Evitar Steps vagos como "cuidar da parte de events".
3. **Atualizar em tempo real.** Marcar `[x]` à medida que cada Step conclui, não ao final de tudo — e disparar `kata-flush-plan-to-subissue` para persistir.
4. **Sincronizar label `status:` em sub-issue + PR.** Toda transição de owner toca a sub-issue Plan e o PR. Skipping qualquer um produz drift que aparece em auditoria.
5. **Não criar Plans fantasmas.** Se a tarefa for cancelada antes de começar, aplicar `status: abandoned` na sub-issue com comentário explicando — não deletar a sub-issue.
6. **Plan canônico vive no GitHub.** Não criar arquivos `.claude/plans/*.md` ou `.cursor/plans/*.md` como canônicos. O body da sub-issue é canonical; o cache local é regenerável; `.ahrena/issues/issue-{N}/` carrega Phase artifacts.
7. **Working notes livres no cache local.** Usar blocos `<!-- not-flushed -->` para registrar decisões em rascunho, debugging notes e próximos passos voláteis — esses blocos são filtrados no flush, então não poluem o body canônico.
8. **Decomposição é parte do Plan.** Antes de pegar uma Issue grande, decompor em sub-issues Plan via `kata-decompose-issue-into-plans`. Um único Plan gigante que cobre toda uma Feature é antipattern — quebra em unidades executáveis.

---
