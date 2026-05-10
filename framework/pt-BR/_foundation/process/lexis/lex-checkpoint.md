# Lexis: Checkpoint de Sessão

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Contexto de sessão entre conversas com agentes IA, complementar a `lex-agent-planning`

## Propósito

Sessões com agentes IA são efêmeras — quando encerradas, o contexto acumulado fora do plano (threads paralelas, scratchpad pré-plano, hand-off entre múltiplos planos ativos, anotações de retomada) é perdido. `lex-agent-planning` cobre a fonte de verdade da **task** (committed, com Steps `[x]`, Decisões fechadas, Riscos). O checkpoint cobre a **sessão** — o que não cabe em um plano único.

Esta Lexis existe para garantir que **o contexto de sessão fora do plano** seja recuperável entre conversas, sem duplicar o que o plano já registra. O checkpoint é scratchpad de janela de trabalho, não duplicata de plano.

## Lei

> **Todo agente DEVE verificar o arquivo `.checkpoint` ao iniciar uma sessão e DEVE salvar o checkpoint sob demanda do usuário ou ao encerrar a sessão quando houve mudança de contexto. O conteúdo do `.checkpoint` MUST seguir o schema canônico (Session focus, Active plans, Open threads, Notes) e NÃO DEVE duplicar o que vive no plano (Activity, Steps, Decisões fechadas, Riscos, Artifacts). Sobreposição com `lex-agent-planning` é PROIBIDA.**

## Regras

### 1. Verificação obrigatória ao iniciar

Ao iniciar uma sessão, o agente **DEVE**:

1. Verificar se existe um arquivo `.checkpoint` na raiz do workspace.
2. Se existir e estiver no schema novo (4 seções canônicas): ler e apresentar ao usuário um resumo (Session focus + Active plans + Open threads).
3. Se existir e estiver no schema antigo (Activity/Status/Progress/Decisions made/Next steps/Artifacts produced): emitir warning de deprecation, prosseguir como se não houvesse checkpoint, e marcar para sobrescrita na próxima invocação de save.
4. Perguntar ao usuário se deseja **retomar** o contexto salvo ou **iniciar uma nova janela** (descartando o checkpoint anterior).
5. Se não existir, prosseguir normalmente. A ausência de `.checkpoint` é cenário válido — não é violação.

### 2. Salvamento sob demanda + fim de sessão

O agente **DEVE** persistir o checkpoint:

1. **Sob demanda** — quando o usuário invocar `cry-checkpoint` ou solicitar explicitamente.
2. **Ao encerrar a sessão** — somente se houve mudança real de contexto (novo Session focus, novo Active plan, novo Open thread, novas Notes). Encerrar sessão sem mudança de contexto NÃO requer save.

A obrigação automática de salvar após cada activity foi removida — a granularidade de activity já vive no plano (`lex-agent-planning`).

### 3. Schema canônico

O arquivo `.checkpoint` **DEVE** conter exatamente as 4 seções abaixo, em qualquer ordem:

```markdown
# Session checkpoint

- **Last update:** YYYY-MM-DDTHH:MM:SSZ
- **Session id:** {chat/session id ou commit short SHA do HEAD}

## Session focus

{1-3 frases descrevendo o foco geral da janela de trabalho. Não é Activity formal — é o ponteiro mental que ajuda o agente a se reorientar ao retomar. Exemplo: "Reposicionando lex-checkpoint em paralelo com revisão de plan-026."}

## Active plans

{Lista de plan-IDs ativos na sessão, com 1 linha de contexto cada. Não duplicar conteúdo do plano — só ponteiros.}

- `plan-026` — commit-readiness-observer; aguardando ajuste de dependência de `.checkpoint`
- `plan-040` — reposicionamento do `.checkpoint`; em redação dos artefatos pt-BR

## Open threads

{Threads de conversa que não viraram plano formal mas devem ser retomadas. Cada thread em 1-2 linhas. Cobre o que escapa de um plano único — decisões pendentes transversais, ideias paralelas que merecem retorno.}

- Avaliar se `lex-agent-planning` deveria absorver "Risks da sessão" como categoria não-bloqueante
- Decidir se Brand-related cries devem viver em `_foundation` ou em `design/`

## Notes

{Texto livre. Pensamentos, links, referências, snippets, lembretes. Sem schema obrigatório. É o scratchpad puro.}
```

Os campos `Activity`, `Status`, `Progress`, `Decisions made`, `Next steps`, `Artifacts produced` (do schema antigo) **NÃO PODEM** aparecer no checkpoint novo — esse conteúdo vive no plano (`lex-agent-planning`).

### 4. Responsabilidade compartilhada

- Qualquer agente (Warrior) que atue na sessão **herda** esta obrigação.
- O checkpoint é **agnóstico de disciplina** — aplica-se a sessões em qualquer Clade.
- O arquivo `.checkpoint` **não deve ser commitado** no repositório (deve estar no `.gitignore`).

### 5. Relação com `lex-agent-planning`

A delimitação entre plano e checkpoint é categórica:

| Conteúdo | Vive em |
|---|---|
| Objetivo, Steps `[x]`, Status (`pending → in-progress → done`), Decisões fechadas, Riscos, Verificação | Plano (`.claude/plans/plan-NNN-{slug}.md`) — committed |
| Activity, Progress detalhado, Artifacts produced, Next steps de uma task | Plano — committed |
| Foco geral da janela de trabalho (Session focus) | Checkpoint — gitignored |
| Ponteiros para múltiplos planos ativos (Active plans) | Checkpoint — gitignored |
| Threads paralelas que não viraram plano (Open threads) | Checkpoint — gitignored |
| Scratchpad livre, links, lembretes (Notes) | Checkpoint — gitignored |

Quando estiver em dúvida, o conteúdo vai para o plano. Plano vence em durabilidade (committed) e em escopo (cobre task; checkpoint cobre sessão).

## Abrangência

- **Aplica-se a:** todas as sessões com agentes IA em qualquer Clade
- **Agentes vinculados:** todos os Warriors e agentes genéricos
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Sobreposição com plano:** se o checkpoint contém conteúdo do schema antigo (Activity, Progress, Artifacts produced), `kata-checkpoint-read` emite warning e ignora o conteúdo — não há perda de dados real porque a fonte de verdade é o plano.
2. **Perda de contexto de sessão:** sessões sem checkpoint resultam em perda de Open threads e Notes; o plano permanece intacto.
3. **Remediação:** o agente sobrescreve o `.checkpoint` antigo na próxima invocação de save com o schema novo. Conteúdo redundante com plano é descartado.

## Exemplos

### Correto

```
Agente: Encontrei um `.checkpoint` no schema novo:
  - Session focus: Reposicionando lex-checkpoint em paralelo com revisão de plan-026
  - Active plans: plan-026, plan-040
  - Open threads: 2 itens pendentes

  Deseja retomar este contexto ou iniciar uma nova janela?

Usuário: Retomar.

Agente: Continuando. Plan-040 estava em redação dos artefatos pt-BR.
        Open threads pendentes:
          1. Avaliar absorção de "Risks da sessão" em lex-agent-planning
          2. Decidir clade dos Brand-related cries
        Posso seguir com plan-040 ou tratar uma das threads primeiro?
```

### Incorreto

```
Agente: Encontrei um `.checkpoint`:
  ## Activity: Implementação do módulo X
  ## Progress: [x] step 1 [ ] step 2
  ## Artifacts produced: app/foo.py, tests/test_foo.py

# ❌ Schema antigo. Conteúdo já está (ou deveria estar) no plano.
# Agente DEVE emitir warning de deprecation, ignorar o conteúdo,
# e prosseguir como se não houvesse checkpoint.
```

```
# Checkpoint que duplica plano — VIOLA A LEI
# .checkpoint
## Active plans
- plan-040

## Progress
- [x] Reescrever lex-checkpoint
- [ ] Reescrever codex-checkpoint

# ❌ Progress vive no plano. Checkpoint só ponteia (Active plans).
```

## Validação Automatizada

- **Ferramenta:** `kata-checkpoint-read` valida schema canônico ao ler; lint do checkpoint na CI verifica que seções obrigatórias do schema antigo estão ausentes (Activity, Progress, Artifacts produced)
- **Momento:** início de sessão (read) e save (sob demanda + fim de sessão com mudança)
- **Métrica:** 0 ocorrências de seções do schema antigo em `.checkpoint` recém-gravado; 100% de `.checkpoint` aderindo ao schema canônico
