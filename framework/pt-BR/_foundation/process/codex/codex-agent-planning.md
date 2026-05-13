# Codex: Planejamento de Tarefas por Agentes

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação, manutenção e ciclo de vida de planos de tarefas por agentes no contexto Ahrena

## Visão Geral

Este Codex é o manual canônico de planejamento de tarefas por agentes per ADR-002 (modelo Issue-as-plan em três camadas). Complementa `lex-agent-planning` (a Lei) com templates, exemplos de preenchimento, cadência de load/flush, owners de cada transição e diretrizes para casos-limite. Todo agente que cria ou mantém planos DEVE consultar este Codex.

## Contexto

- **Domínio:** disciplina de execução de tarefas por agentes AI
- **Público-alvo:** todos os agentes (Claude, Cursor, warriors, katas) e revisores humanos
- **Atualização:** quando o template, o enum de status, a tabela de owners ou a cadência de sync mudam (ADR recomendado para mudanças estruturais)

---

## 1. Modelo de armazenamento em três camadas (per ADR-002)

| Camada | Localização | Papel | Versionamento |
|---|---|---|---|
| **Issue body** | `https://github.com/{owner}/{repo}/issues/{N}` | Canonical. Summary + Plan section (Objective, Steps, Risks, Dependencies, Open Questions) | Audit log nativo do GitHub (timestamp + autor por edição) |
| **`.plans/{N}.md`** | Raiz do repo, gitignored | AI working memory + scratch. Superset do body da Issue + blocos `<!-- not-flushed -->` | Cache local regenerável |
| **`.ahrena/issues/{N}/`** | Raiz do repo, committed | Phase artifacts (`01-brief.md` … `06-quality-report.md`) | Git |

### Resolução do path do cache local

```
1. Ler .ahrena/.directives
2. Se paths.plans existir → usar esse valor
3. Caso contrário → usar default `.plans/` (raiz do repo, gitignored)
```

Exemplo de override:
```yaml
# .ahrena/.directives
paths:
  plans: ".cache/ai-plans/"
```

> **Modelo legado (pré-ADR-002, deprecated):** arquivos `plan-{NNN}-{slug}.md` em `.claude/plans/` foram migrados para `.ahrena/issues/_legacy/` no PR de plan-046. Não criar arquivos novos nesse formato — o body da Issue é canonical agora; `.plans/{N}.md` é cache local nomeado pelo número da Issue.

---

## 2. Nomeação do cache local

```
.plans/{N}.md
```

| Campo | Regra |
|---|---|
| `{N}` | Número da Issue do GitHub correspondente. Sem padding, sem prefix — `.plans/96.md`, não `.plans/plan-096.md` ou `.plans/96-slug.md` |

Exemplos:
- `.plans/42.md` — cache do plano da Issue #42
- `.plans/96.md` — cache do plano da Issue #96
- `.plans/100.md` — cache do plano da release Issue #100 (Eixo B)

O cache é gitignored — não aparece em `git status` nem em `git log`. Para inspecionar planos sem clonar:

```bash
gh issue view {N} --json body --jq .body
```

Para sincronizar localmente: `kata-load-plan-from-issue {N}`.

---

## 3. Template do body da Issue (canonical) e do cache local

### 3a. Body da Issue (canonical per ADR-002)

```markdown
## Summary

**As** {user_role},
**I want** {specific_objective},
**So that** {benefit_and_value}.

(ou texto livre 2-4 frases descrevendo o objetivo de alto nível)

## Plan

### Objective
Alinhar o ciclo de vida do plano e da Issue do GitHub a um único enum
de status (todo → development → to review → review → done para Eixo A;
to release → release → done para Eixo B), com owner explícito para
cada transição e notificações provider-agnósticas via MCP.

### Steps
- [x] 1. Issue + branch + worktree (Eunomia ou fallback)
- [x] 2. ADR-002 (MADR simplificado)
- [x] 3. lex-agent-planning (pt-BR)
- [ ] 4. codex-agent-planning (pt-BR)
- [ ] 5. lex-issue-status split (pt-BR)
- ...

### Dependencies
- plan-043 (PR #93) — merged
- plan-044 (Eunomia) — absorvido por plan-046 Step 10
- plan-045 (Janus pointer) — absorvido por plan-046 Step 3.5

### Risks
- .plans/ perdida em fresh clone — mitigado por kata-load-plan-from-issue
- Flush conflitante entre sessões — preflight de drift detecta
- Loop 3×15min pode ser curto fora de horário comercial — mitigar via .directives

### Open Questions
Todas resolvidas em 2026-05-11.
```

O body da Issue é gravado por:
- `kata-plan-task` na criação inicial (Passo 5 do HARD-GATE de `— → todo`)
- `kata-flush-plan-to-issue` em cada gatilho de sync (transição, Step concluído, fim de sessão)

### 3b. Cache local `.plans/{N}.md` (working memory)

```markdown
## Summary
... (espelha o body da Issue)

## Plan
... (espelha o body da Issue)

<!-- not-flushed -->
## Working notes
- 23:30 — terminou Step 3
- Decision: usar git mv para preservar history em Step 14

## Next actions
1. Step 4 — codex-agent-planning
2. Step 5 — path move
3. Step 17 — abrir PR draft

## Scratch
gh issue develop registra branch como "Development" na sidebar.
Limite do body da Issue: ~65KB (testado com plan-046).
<!-- /not-flushed -->
```

O cache **não tem front-matter YAML** — o GitHub Issue já carrega toda a metadata (assignees, labels `status:*`, milestones, dates). Blocos `<!-- not-flushed -->` são filtrados antes do flush para a Issue.

> **Front-matter legacy:** planos em `.ahrena/issues/_legacy/` (pré-ADR-002) mantêm YAML front-matter histórico (`plan_id`, `status`, `claude_session`, `merge_commit`, `closed_at`). Esse formato é reconhecido para audit, mas NÃO replicar em novos planos.

---

## 4. Estados do ciclo de vida (enum unificado)

```
todo → development → to review → review → to release → release → done
                          ↘            ↘            ↘
                          abandoned (terminal alternativo, qualquer estágio)
```

| Status | Quando usar | Owner que transiciona |
|---|---|---|
| `todo` | Plano criado, Issue aberta, branch remota vinculada, worktree pronto, ainda não começou | Quem cria: `warrior-eunomia` (fallback: agente da sessão) |
| `development` | Implementação em curso (Athena Phase 4) | `warrior-athena` |
| `to review` | PR aberto, esperando reviewer pegar | `warrior-athena` (entrada); `warrior-argos` (retorno do `review`) |
| `review` | Argos ou humano revisando ativamente | `warrior-argos` (entrada e saída) |
| `to release` | Review aprovado, esperando release iniciar | `warrior-athena` (detecta `APPROVED`) |
| `release` | Release em execução (tag/build/deploy) | `warrior-janus` |
| `done` | Release concluído, PR mergeado, ciclo encerrado | `warrior-janus` |
| `abandoned` | Plano descartado (qualquer estágio) | Criador ou owner atual |

**Estado canônico per ADR-002:** o `status:` vive como **label** na Issue do GitHub (e no PR, a partir de `to review`). Não há mais "front-matter do plano" — o body da Issue é canonical; `.plans/{N}.md` é cache regenerável. Planos legados em `.ahrena/issues/_legacy/` mantêm front-matter histórico para audit, sem retrofit.

### Split em dois eixos (per ADR-002 / plan-045 absorvido)

- **Eixo A — Dev cycle** (feature/fix/chore Issues/PRs): `todo → development → to review → review → done` + `abandoned`. Owners: Eunomia/Athena/Argos.
- **Eixo B — Release cycle** (release Issue exclusivamente): `to release → release → done` + `abandoned`. Owner: Janus.

Mutex é **intra-artefato** (dentro de cada Issue/PR), não cross-artifact. Aplicar label do Eixo B em Issue/PR de feature (ou vice-versa) é proibido per HARD-GATE em `lex-issue-status`.

---

## 5. Owners de cada transição (visão de fluxo)

### Eixo A — Dev cycle (Eunomia/Athena/Argos)

```
Eunomia: — ──→ todo                                                  [feature Issue + PR]
                 │
                 ▼
Athena:  todo ──→ development ──→ to review
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ done   (humano aprova; merge fecha Issue)
                                       │
                  qualquer ──→ abandoned (terminal alternativo)
```

### Eixo B — Release cycle (Janus)

```
Janus:   — ──→ to release ──→ release ──→ done                      [release Issue dedicada]
                  │
                  qualquer ──→ abandoned (release abortada antes do tag)
```

Cada owner atualiza simultaneamente:

1. Body da Issue via `kata-flush-plan-to-issue` (canonical per ADR-002 — apenas se houve edição no cache local).
2. Label `status: <name>` na Issue do GitHub (per `lex-issue-status` mutex intra-artefato).
3. Label `status: <name>` no PR (a partir de `to review`, apenas no Eixo A).

---

## 6. Owner do `— → todo`: 5 passos canônicos

Eunomia (ou fallback) executa em sequência antes de marcar `status: todo`:

| Passo | Ação | Lex de referência |
|---|---|---|
| 1 | Abrir Issue (template, label, type, assignee, Why/What/How) | `lex-issue-first`, `lex-issue-quality` |
| 2 | Verificar Issue Type pós-criação | `lex-issue-type-verified` |
| 3 | Criar branch remota e vincular à Issue: `gh issue develop {N} --base main --name {type}/{N}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 4 | Criar worktree em `.worktrees/{N}-{slug}/` | `lex-git-worktrees` |
| 5 | Preencher body da Issue com plano canônico (Summary + Plan: Objective, Steps, Risks, Dependencies, Open Questions) via MCP `update_issue` (preferido) ou `gh issue edit --body-file` (fallback) | `lex-agent-planning`, `lex-mcp` |

A falha em qualquer passo deixa o plano em rascunho (não pode ser apresentado como `todo`). Per HARD-GATE em `lex-agent-planning`, mesmo em hotfix os 5 passos são obrigatórios.

---

## 7. Quando um plano é obrigatório (e quando não é)

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

### Zona cinzenta — usar plano por precaução

- Tarefa aparentemente simples que pode se ramificar (ex.: "corrigir o bug" sem saber o escopo)
- Operação irreversível mesmo que de etapa única (ex.: deletar arquivos)

---

## 8. Relação entre planos e outros artefatos

```
Issue GitHub                                    canonical (per ADR-002)
    ├── body: plano canônico (Summary + Plan)
    ├── label: status: <name> (Eixo A ou Eixo B)
    │
    ├── PR (label: status: <name>, a partir de "to review")        [só Eixo A]
    │
    ├── .plans/{N}.md (gitignored)                                  cache local da IA
    │   └── superset do body + blocos <!-- not-flushed -->
    │
    ├── .ahrena/issues/{N}/ (committed)                                    Phase artifacts
    │   ├── 01-brief.md
    │   ├── 02-requirements.md
    │   ├── 03-architecture.md
    │   ├── 05-security-review.md
    │   └── 06-quality-report.md
    │
    ├── docs/adr/ADR-{n}-*.md (committed)                           se decisão arquitetural
    │
    ├── Heartbeat de sessão (.ahrena/workflow/sessions/<uuid>.json, gitignored)
    │
    └── ─ ─ ─ não confundir com ─ ─ ─
        Checkpoint (.checkpoint — gitignored, sessão)
```

- Body da Issue, label da Issue e label do PR são sincronizados pelo owner em cada transição.
- ADR é aberto quando o plano identifica uma decisão arquitetural relevante (mora em `docs/adr/`, não `.ahrena/issues/`).
- Heartbeat de sessão (`codex-session-tracking`) registra qual sessão Claude Code opera no plano agora.
- Checkpoint NÃO é subordinado ao plano; é artefato paralelo de **sessão**, não de **task**.

### Plano vs `.checkpoint` — delimitação canônica

Plano cobre **task**: Objetivo, Escopo, Steps `[x]`, Decisões fechadas, Riscos, Verificação. Committed.
Checkpoint cobre **sessão**: Session focus, Active plans (ponteiros), Open threads, Notes. Gitignored.

| Conteúdo | Body da Issue (plano canônico) | `.plans/{N}.md` (cache + scratch) | `.checkpoint` (sessão) |
|---|:---:|:---:|:---:|
| Steps `[x]` | ✅ | ✅ (espelhado) | ❌ |
| Decisões fechadas da task | ✅ (ou ADR) | ✅ (espelhado) | ❌ |
| Riscos da task | ✅ | ✅ (espelhado) | ❌ |
| Working notes / debugging diary | ❌ | ✅ (bloco `<!-- not-flushed -->`) | ❌ |
| Foco geral da janela de trabalho | ❌ | ❌ | ✅ |
| Lista de planos ativos na sessão | ❌ | ❌ | ✅ |
| Threads paralelas que não viraram plano | ❌ | ❌ | ✅ |
| Scratchpad livre, links, lembretes | ❌ | ❌ | ✅ |

Se o conteúdo se repete em ambos, há sobreposição — plano vence (committed). Sobreposição é PROIBIDA por `lex-checkpoint` regra 5 e por `lex-agent-planning`.

---

## 9. Cadência de load/flush (per ADR-002)

Sincronização entre o body da Issue (canonical) e o cache local `.plans/{N}.md` ocorre em **3 gatilhos canônicos** (per Open Question #3 de plan-046):

| Gatilho | Operação | Quem dispara |
|---|---|---|
| Início de sessão / handoff entre agentes | `kata-load-plan-from-issue` | Athena, Argos, Janus (no início de cada sessão de trabalho num plano) |
| Transição de label `status:` na Issue/PR | `kata-flush-plan-to-issue` | Eunomia, Athena, Argos, Janus (no momento da transição) |
| Step do plano marcado como concluído (`[ ]` → `[x]`) | `kata-flush-plan-to-issue` | Agente que conclui o Step |
| Fim de sessão (heartbeat conclui ou agente sai) | `kata-flush-plan-to-issue` | `kata-session-heartbeat` no shutdown |

Toggles intermediários, edições de scratch (blocos `<!-- not-flushed -->`) e working notes são **livres** — não disparam flush. A regra é: o body da Issue deve refletir o estado **estável** (entre transições e Steps), não o estado **transiente** (durante working).

### Fluxo típico de uma sessão de trabalho

```
1. Athena entra (recebe handoff de Eunomia):
   → kata-load-plan-from-issue {N}    (materializa .plans/{N}.md)
   → aplica label status: development na Issue + PR
   → kata-flush-plan-to-issue {N}     (registra a transição)

2. Athena trabalha:
   → edita arquivos
   → registra notas em .plans/{N}.md (blocos <!-- not-flushed -->)
   → marca Step [x] no .plans/{N}.md
   → kata-flush-plan-to-issue {N}     (Step concluído)

3. Athena abre PR via kata-pr-prepare:
   → Passo 5c: kata-flush-plan-to-issue {N}  (estado final pré-PR)
   → Passo 6: create_pull_request
   → Passo 6b: aplica status: to review na Issue + PR
   → kata-flush-plan-to-issue {N}     (transição registrada)

4. Athena sai:
   → kata-session-heartbeat no shutdown dispara
   → kata-flush-plan-to-issue {N}     (cleanup final)

5. Argos entra:
   → kata-load-plan-from-issue {N}    (refresh do cache local)
   → ...
```

### Detecção de drift remoto (preflight)

`kata-flush-plan-to-issue` por default executa preflight: lê o body atual da Issue, compara com o último estado conhecido, e bloqueia se houver edição remota desconhecida (outra sessão, edição via UI do GitHub). Oferece: (a) mostrar diff e abortar, (b) merge manual, (c) overwrite via `force=true`. Heartbeat de sessão permite identificar a sessão concorrente.

---

## 10. Loop de revisão pendente (estado `to review`)

Após Athena abrir o PR (Passo 6/6b de `kata-pr-prepare`), o ciclo de review opera em **duas fases distintas e sequenciais** + um handler para CHANGES_REQUESTED:

### Fase A — Argos pre-flight cycles (Passo 6c de `kata-pr-prepare`)

Até 3 ciclos interativos `A1, A2, A3`, gateados por `AskUserQuestion` (Athena nunca invoca Argos sem confirmação). Cada ciclo: Athena pergunta "Quer review do Argos no HEAD atual?" — opções (a) sim, (b) pular para human review, (c) stop. Se (a) → Argos roda, publica review com marker idempotente; Athena lê findings; P0 BLOCKER address obrigatório; P1 AskUserQuestion (address ou defer); P2 nota. Commit + push se houve mudanças → HEAD novo. Repete até A3 ou usuário opta por (b)/(c). Detalhe completo em `kata-pr-prepare` Passo 6c.

### Fase B — Human nudge loop (Passo 6d de `kata-pr-prepare`)

Após Fase A encerrar, Athena pergunta o modo de agendamento: (a) `/loop` na sessão (`ScheduleWakeup`), (b) cron remoto, (c) manual. Modos (a)/(b) agendam 3 ciclos `H1, H2, H3` com 15 min entre cada. A cada cycle, Athena dispara notificação Slack via MCP em `notifications.channels.pr_review_timeout` — mensagem escala em urgência (H1 "PR pronto", H2 "reminder #1", H3 "reminder #2, 2ª cobrança"). Consulta `gh pr view {N} --json reviewDecision,mergedAt`:

- `mergedAt != null` → transição `status: to review → done`, captura `mergeCommit.oid`, encerra loop.
- `reviewDecision == APPROVED` (sem merge) → comenta "PR aprovado, aguardando merge", encerra loop.
- `reviewDecision == CHANGES_REQUESTED` → **dispara Fase C**.
- Caso contrário → se H<3, reagenda; se H==3, encerra silenciosamente.

### Fase C — CHANGES_REQUESTED handler (Passo 6e de `kata-pr-prepare`)

Se humano pede mudanças durante Fase B: Athena lê os comentários do reviewer e pergunta via AskUserQuestion: (a) address agora, (b) defer pra follow-up Issue, (c) stop. Se (a) → Athena implementa, commita, push (HEAD novo). Após (a) ou (b) → **reset completo**: Athena reagenda o loop a partir da **Fase A** (3 novos Argos cycles no HEAD novo) — porque novos commits invalidam a review anterior do Argos. Não pula direto para Fase B. Esse handler garante que CHANGES_REQUESTED reseta o ciclo completo de qualidade, não só o human nudge loop. Detalhe em `kata-pr-prepare` Passo 6e.

---

Argos opera o sub-ciclo `to review ↔ review` em Fase A (com mudança de label durante a execução) e em Fase C quando re-invocado. Argos nunca move para `done`; transição `to review → done` é exclusiva de Athena ao detectar merge.

---

## 11. Boas práticas

1. **Escrever o plano antes de saber tudo.** O objetivo é tornar a intenção visível, não produzir documentação perfeita. Um plano impreciso que evolui é melhor que nenhum plano.
2. **Manter etapas atômicas.** Cada etapa deve ser verificável: feita ou não feita. Evitar etapas vagas como "cuidar da parte de events".
3. **Atualizar em tempo real.** Marcar `[x]` à medida que cada etapa conclui, não ao final de tudo — e disparar `kata-flush-plan-to-issue` para persistir.
4. **Sincronizar label `status:` em Issue + PR.** Toda transição de owner toca a Issue e o PR. Skipping qualquer um produz drift que aparece em auditoria.
5. **Não criar planos fantasmas.** Se a tarefa for cancelada antes de começar, aplicar `status: abandoned` na Issue com comentário explicando — não deletar a Issue.
6. **Plano canônico vive no GitHub.** Não criar arquivos `.claude/plans/*.md` como canônicos (modelo legado pré-ADR-002). O body da Issue é canonical; `.plans/{N}.md` é cache regenerável; `.ahrena/issues/{N}/` carrega Phase artifacts.
7. **Working notes livres em `.plans/{N}.md`.** Usar blocos `<!-- not-flushed -->` para registrar decisões em rascunho, debugging notes e próximos passos voláteis — esses blocos são filtrados no flush, então não poluem o body canônico.

---

## Referências

- ADR-002 — modelo de armazenamento em três camadas (Issue body + `.plans/` + `.ahrena/issues/`)
- `lex-agent-planning` — Lei correspondente (HARD-GATE de `— → todo` + Tabelas A e B)
- `lex-issue-status` — labels canônicos; split Eixo A (dev) + Eixo B (release)
- `lex-issue-type-verified` — verificação programática do Issue Type
- `lex-mcp` — preferência MCP + fallback CLI
- `kata-plan-task` — procedimento operacional (modo top-level de Eunomia); preenche body da Issue
- `kata-create-subtasks` — decomposição de child Issue em subtasks (modo subtask de Eunomia)
- `kata-load-plan-from-issue` — materializa `.plans/{N}.md` do body canônico
- `kata-flush-plan-to-issue` — flusha `.plans/{N}.md` (filtrando scratch) para o body
- `kata-session-heartbeat` — heartbeat de sessão Claude Code
- `codex-session-tracking` — manual de tracking de sessão
- `codex-notifications` — manual provider-agnóstico de envio via MCP
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
- `lex-checkpoint` — rastreamento de estado de sessão (complementar)
- `lex-issue-driven` — fluxo Issue-Driven do Athena
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
