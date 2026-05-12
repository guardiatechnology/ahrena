# Codex: Planejamento de Tarefas por Agentes

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação, manutenção e ciclo de vida de planos de tarefas por agentes no contexto Ahrena

## Visão Geral

Este Codex é o manual canônico de planejamento de tarefas por agentes. Complementa `lex-agent-planning` (a Lei) com templates, exemplos de preenchimento, regras de numeração, boas práticas, owners de cada transição e diretrizes para casos-limite. Todo agente que cria ou mantém planos DEVE consultar este Codex.

## Contexto

- **Domínio:** disciplina de execução de tarefas por agentes AI
- **Público-alvo:** todos os agentes (Claude, Cursor, warriors, katas) e revisores humanos
- **Atualização:** quando o template, o enum de status ou a tabela de owners mudam (ADR recomendado para mudanças estruturais)

---

## 1. Resolução do path de planos

O agente resolve o diretório de planos na seguinte ordem:

```
1. Ler .ahrena/.directives
2. Se paths.plans existir → usar esse valor (ex.: ".plans/")
3. Caso contrário → usar padrão por agente:
   - Claude Code (CLI, VSCode, Desktop, claude.ai) → .claude/plans/
   - Cursor                                         → .cursor/plans/
   - Agente desconhecido                            → .plans/
```

Exemplo de override no projeto:
```yaml
# .ahrena/.directives
paths:
  root: ".ahrena/"
  plans: ".plans/"    # override: todos os agentes usam .plans/
```

Subpastas por estado de filesystem (não por estado de enum):

- `{plans}/todo/` — planos com `status: todo` aguardando início (anteriormente `pending/`)
- `{plans}/archived/` — planos com `status: done` ou `abandoned` após o PR correspondente ser mergeado

A pasta de filesystem é convenção de organização. O estado canônico fica no front-matter (`status:`).

---

## 2. Convenção de nomeação de arquivos

```
plan-{NNN}-{slug}.md
```

| Campo | Regra |
|---|---|
| `{NNN}` | Número sequencial de 3 dígitos (001, 002, …). Incrementar a partir do maior número existente no diretório. Sem lacunas quando possível; se houver lacuna (plano abandonado), não reutilizar o número |
| `{slug}` | kebab-case, máximo 60 caracteres, resumo da tarefa |

Exemplos:
- `plan-001-complete-feature-design-docs.md`
- `plan-002-create-warrior-hecate.md`
- `plan-090-workflow-status-and-review-loop.md`

---

## 3. Template completo do plano

```markdown
---
plan_id: "043"
title: "workflow-status-and-review-loop"
status: todo
agent: claude
issue: "guardiatechnology/ahrena#90"
branch: "feat/90-workflow-status-review-loop"
worktree: ".worktrees/90-workflow-status-review-loop"
claude_session: "85846253"            # opcional; preenchido por kata-session-heartbeat
session_entrypoint: "claude-vscode"
created_at: "2026-05-10T00:00:00Z"
updated_at: "2026-05-11T15:30:00Z"
---

# Plano: Workflow status unificado entre plano e Issue

## Objetivo

Alinhar o ciclo de vida do plano e da Issue do GitHub a um único enum de status
(todo → development → to review → review → to release → release → done),
com owner explícito para cada transição e notificações provider-agnósticas
via MCP configurado em .ahrena/.directives.

## Escopo

Arquivos a modificar:
- framework/{pt-BR,es,en}/_foundation/process/lexis/lex-agent-planning.md
- framework/{pt-BR,es,en}/_foundation/process/codex/codex-agent-planning.md
- framework/{pt-BR,es,en}/_foundation/contributing/lexis/lex-issue-status.md (novo)
- framework/{pt-BR,es,en}/engineering/workflow/warriors/warrior-athena.md
- framework/{pt-BR,es,en}/engineering/quality/warriors/warrior-argos.md
- (...)

## Etapas

- [x] 1. Issue + branch + worktree (Eunomia ou fallback)
- [x] 2. ADR-001 (MADR simplificado)
- [x] 3. lex-agent-planning (3 línguas)
- [ ] 4. codex-agent-planning (3 línguas)
- [ ] 5. lex-issue-status novo (3 línguas)
- (...)

## Dependências

- plan-027 (Janus) — merged
- plan-042 (make mcp-enable) — merged
- plan-044 (Eunomia) — depende deste
- plan-045 (Janus pointer/wiring) — depende deste

## Riscos

- Renomear pasta pending/ → todo/ exige grep cruzado por referências
- Loop 3×15min pode ser curto fora de horário comercial — mitigar via .directives
- Notificações via MCP viram ruído se muitos PRs ficarem parados — mitigar com 1 disparo no 3º ciclo
```

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

**Filesystem ≠ estado:** mover o arquivo para `archived/` é convenção de organização após o merge. O estado canônico permanece no front-matter.

---

## 5. Owners de cada transição (visão de fluxo)

```
Eunomia: — ──→ todo
                 │
                 ▼
Athena:  todo ──→ development ──→ to review
                                       │
                                       ▼
Argos:                         to review ⇄ review
                                       │
Athena:           to review ──→ to release  (humano aprova)
                                       │
                                       ▼
Janus:           to release ──→ release ──→ done
                                       │
                  qualquer ──→ abandoned (terminal alternativo)
```

Cada owner atualiza simultaneamente:

1. `status:` no front-matter do plano.
2. Label `status: <name>` na Issue do GitHub (per `lex-issue-status`).
3. Label `status: <name>` no PR (a partir de `to review`).

---

## 6. Owner do `— → todo`: 5 passos canônicos

Eunomia (ou fallback) executa em sequência antes de marcar `status: todo`:

| Passo | Ação | Lex de referência |
|---|---|---|
| 1 | Abrir Issue (template, label, type, assignee, Why/What/How) | `lex-issue-first`, `lex-issue-quality` |
| 2 | Verificar Issue Type pós-criação | `lex-issue-type-verified` |
| 3 | Criar branch remota e vincular à Issue: `gh issue develop {N} --base main --name {type}/{N}-{slug}` | `lex-git-branches`, `lex-issue-first` |
| 4 | Criar worktree em `.worktrees/{N}-{slug}/` | `lex-git-worktrees` |
| 5 | Atualizar front-matter do plano: `issue:`, `branch:`, `worktree:` | `lex-agent-planning` |

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
Issue GitHub (label: status: <name>)
    │
    ├── PR (label: status: <name>, a partir de "to review")
    │
    └── Plan (status: <name> no front-matter, committed)
            ├── ADR (se decisão arquitetural relevante)
            ├── Heartbeat de sessão (.ahrena/workflow/sessions/<uuid>.json, gitignored)
            └── ─ ─ ─ não confundir com ─ ─ ─
                Checkpoint (.checkpoint — gitignored, sessão)
```

- Issue, plano e PR carregam o **mesmo** `status:` em qualquer instante.
- ADR é aberto quando o plano identifica uma decisão arquitetural relevante.
- Heartbeat de sessão (`codex-session-tracking`) registra qual sessão Claude Code opera no plano agora.
- Checkpoint NÃO é subordinado ao plano; é artefato paralelo de **sessão**, não de **task**.

### Plano vs `.checkpoint` — delimitação canônica

Plano cobre **task**: Objetivo, Escopo, Steps `[x]`, Decisões fechadas, Riscos, Verificação. Committed.
Checkpoint cobre **sessão**: Session focus, Active plans (ponteiros), Open threads, Notes. Gitignored.

| Conteúdo | Plano | Checkpoint |
|---|:---:|:---:|
| Steps `[x]` | ✅ | ❌ |
| Decisões fechadas da task | ✅ | ❌ |
| Riscos da task | ✅ | ❌ |
| Artifacts produced | ✅ | ❌ |
| Foco geral da janela de trabalho | ❌ | ✅ |
| Lista de planos ativos na sessão | ❌ | ✅ |
| Threads paralelas que não viraram plano | ❌ | ✅ |
| Scratchpad livre, links, lembretes | ❌ | ✅ |

Se o conteúdo se repete em ambos, há sobreposição — plano vence (committed). Sobreposição é PROIBIDA por `lex-checkpoint` regra 5 e por `lex-agent-planning`.

---

## 9. Loop de revisão pendente (estado `to review`)

Quando Athena abre o PR, agenda 3 ciclos de 15 min via `ScheduleWakeup`. A cada wake-up:

1. Consulta `gh pr view {N} --json reviewDecision,reviews` e `gh pr checks {N}`.
2. Se `reviewDecision == APPROVED` por humano → move para `to release` e sai do loop.
3. Se `reviewDecision == CHANGES_REQUESTED` → atualiza plano com nota, faz ping no PR via `gh pr comment`, mantém em `to review`, sai do loop.
4. Se Argos publicou findings P0/P1 → mantém em `to review` (aguarda autor corrigir); sai do loop e reagenda quando Argos sinalizar nova rodada.
5. Caso contrário (`REVIEW_REQUIRED` / `null`, sem aprovação humana) → conta ciclo; se < 3, reagenda 15 min; se == 3, dispara notificação via MCP em `notifications.channels.pr_review_timeout` (per `codex-notifications`) e encerra o loop.

Argos opera o sub-ciclo `to review ↔ review` em paralelo, intercalado com a janela de espera de Athena. Argos nunca move para `to release`; isso é exclusivo de Athena ao detectar aprovação humana.

---

## 10. Boas práticas

1. **Escrever o plano antes de saber tudo.** O objetivo é tornar a intenção visível, não produzir documentação perfeita. Um plano impreciso que evolui é melhor que nenhum plano.
2. **Manter etapas atômicas.** Cada etapa deve ser verificável: feita ou não feita. Evitar etapas vagas como "cuidar da parte de events".
3. **Atualizar em tempo real.** Marcar `[x]` à medida que cada etapa conclui, não ao final de tudo.
4. **Sincronizar `status:` em três lugares.** Toda transição de owner toca plano + Issue + PR. Skipping qualquer um produz drift que aparece em auditoria.
5. **Não criar planos fantasmas.** Se a tarefa for cancelada antes de começar, marcar `abandoned` com motivo — não deletar o arquivo.
6. **Commitar o plano.** O plano é parte do trabalho; deve ir no mesmo PR que os artefatos que descreve.

---

## Referências

- `lex-agent-planning` — Lei correspondente
- `lex-issue-status` — labels canônicos de status na Issue/PR
- `lex-issue-type-verified` — verificação programática do Issue Type
- `kata-plan-task` — procedimento operacional (modo top-level de Eunomia)
- `kata-create-subtasks` — decomposição de child Issue em subtasks (modo subtask de Eunomia)
- `kata-session-heartbeat` — heartbeat de sessão Claude Code
- `codex-session-tracking` — manual de tracking de sessão
- `codex-notifications` — manual provider-agnóstico de envio via MCP
- `lex-checkpoint` — rastreamento de estado de sessão (complementar)
- `lex-issue-driven` — fluxo Issue-Driven do Athena
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
