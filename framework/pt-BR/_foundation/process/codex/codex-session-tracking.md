# Codex: Tracking de Sessão Claude Code

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Registro da sessão Claude Code que opera em cada plano e da trilha de sessões que tocou cada PR

## Visão Geral

Este Codex define o sistema de heartbeat que permite ao framework rastrear qual sessão Claude Code está operando em cada plano e qual sequência de sessões produziu cada PR. Sem isso, o digest de planos de Eunomia não consegue distinguir "plano em movimento agora" de "plano esquecido"; o body do PR perde a auditoria de tempo de implementação; e handoffs entre sessões viram lacunas inexplicáveis no histórico.

O contrato é simples: cada agente que toca um plano executa `kata-session-heartbeat` em pontos significativos, escrevendo/atualizando `.ahrena/workflow/sessions/<session-id>.json`. A persistência canônica vai para o body do PR (seção "Session Trace") via `kata-pr-prepare`; o diretório local é runtime-only e gitignored.

## Contexto

- **Domínio:** rastreamento operacional de sessões Claude Code no fluxo Issue-Driven.
- **Público-alvo:** todo agente que opera num plano (Eunomia na criação, Athena nas transições, Argos na revisão, Janus na release).
- **Atualização:** quando o schema do heartbeat mudar ou quando uma nova variável de ambiente do Claude Code for adicionada.

## Conteúdo

### 1. Variáveis de ambiente do Claude Code

O Claude Code expõe três variáveis estáveis em cada sessão. O agente lê e propaga:

| Variável | Conteúdo | Origem |
|---|---|---|
| `CLAUDE_CODE_SESSION_ID` | UUID estável da sessão (ex.: `85846253-4edf-443d-b294-187ef287d1bb`) | Claude Code injeta no shell |
| `CLAUDE_CODE_ENTRYPOINT` | Onde a sessão roda: `claude-vscode`, `claude-cli`, `claude-desktop`, `claude-web` | Idem |
| `AI_AGENT` | Versão do agente (ex.: `claude-code_2-1-138_agent`) | Idem |

Quando o agente roda fora do Claude Code (CI, Cursor sem env), trata as variáveis como ausentes e o heartbeat é pulado sem erro — `kata-session-heartbeat` é idempotente nesse caso.

### 2. Schema do heartbeat file

Cada sessão escreve um arquivo JSON em `.ahrena/workflow/sessions/<session-id>.json`:

```json
{
  "session_id": "85846253-4edf-443d-b294-187ef287d1bb",
  "entrypoint": "claude-vscode",
  "agent_version": "claude-code_2-1-138_agent",
  "plan_id": "043",
  "branch": "feat/90-workflow-status-review-loop",
  "cwd": "/Users/.../worktrees/90-workflow-status-review-loop",
  "started_at": "2026-05-11T12:30:00Z",
  "last_heartbeat": "2026-05-11T14:00:00Z",
  "last_activity": "kata-pr-prepare:step3",
  "role": "creator",
  "previous_session": null
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `session_id` | UUID string | Valor de `CLAUDE_CODE_SESSION_ID` |
| `entrypoint` | enum | Valor de `CLAUDE_CODE_ENTRYPOINT` |
| `agent_version` | string | Valor de `AI_AGENT` |
| `plan_id` | string `NNN` | Lido do front-matter do plano em uso |
| `branch` | string | `git rev-parse --abbrev-ref HEAD` no worktree |
| `cwd` | string | Working directory atual |
| `started_at` | ISO 8601 | Primeira escrita do heartbeat |
| `last_heartbeat` | ISO 8601 | Última atualização (sobrescrita a cada chamada) |
| `last_activity` | string | Nome do step/kata/cry corrente (formato `kata-name:stepN` ou `cry-name`) |
| `role` | enum | `creator`, `executor`, `reviewer`, `releaser` (depende de quem está escrevendo) |
| `previous_session` | UUID ou null | Em handoff, aponta para a sessão anterior |

### 3. Cadência

Heartbeat atualizado:

- **Início**: quando o agente entra no plano (Eunomia ao criar; Athena ao herdar; Argos ao iniciar revisão; Janus ao iniciar release).
- **Em pontos significativos**: ao concluir cada Step do plano, ao concluir cada kata invocada, ao mudar de status.
- **Mínimo**: a cada 5–10 minutos de atividade ativa.
- **Stale threshold**: 30 min sem heartbeat → Eunomia considera offline no digest. Configurável via `session_tracking.stale_threshold_minutes`.

Idempotência: chamar `kata-session-heartbeat` 100×/dia é seguro — sobrescreve `last_heartbeat` e `last_activity` sem efeito colateral.

### 4. Limpeza

- Ao mover plano para `done` ou `abandoned`: remover o heartbeat file da sessão (não precisa mais).
- Ao reiniciar sessão com mesmo `session_id` (entrypoint detecta heartbeat pré-existente): continuar do existente, não recriar.

### 5. Multi-sessão por plano (handoff)

Quando uma sessão cede o trabalho a outra (ex.: sessão A começou, sessão B continuou):

1. Sessão B escreve novo heartbeat com `previous_session: <UUID da sessão A>`.
2. Heartbeat antigo de A permanece até ser limpo no final do ciclo.
3. Digest de Eunomia mostra a cadeia: "sessão B (atual, herdou de A)".

### 6. Diretório gitignored

`.ahrena/workflow/sessions/` é runtime-only:

```gitignore
# .ahrena/workflow/sessions/ — runtime heartbeat dir (codex-session-tracking)
.ahrena/workflow/sessions/
```

Histórico canônico das sessões que tocaram um trabalho persiste no body do PR (seção "Session Trace"), não no filesystem.

### 7. Session Trace no body do PR

`kata-pr-prepare` constrói a seção "Session Trace" agregando todos os heartbeat files cujo `branch` coincide com a branch atual:

```markdown
## Session Trace

| Session | Entrypoint | Role | Started | Last Heartbeat |
|---|---|---|---|---|
| `85846253` | claude-vscode | creator + executor | 2026-05-11T12:30Z | 2026-05-11T14:00Z |
| `abc12345` | claude-cli | reviewer (Argos) | 2026-05-11T13:45Z | 2026-05-11T13:55Z |

- Worktree: `.worktrees/90-workflow-status-review-loop`
- Cumulative active time: ~1h30min
```

Cálculo de **cumulative active time**: soma dos intervalos `started_at → last_heartbeat` por sessão. Esta métrica é complementar a `cry-pr-cost-stamp` (que mede tokens/USD); aqui mede tempo de sessão real.

PRs sem `Session Trace`, quando o branch tem heartbeat files associados, são rejeitados em Gate 2 (per `lex-pr-quality`).

### 8. PRs sem agente (humano puro)

Em hotfixes manuais ou PRs feitos por humano sem agente Claude Code, a seção pode ser:

```markdown
## Session Trace

_(human-driven; no session trace)_
```

Aceito em Gate 2.

## Restrições

- **Não persistir credenciais ou dados sensíveis** no heartbeat file — `cwd`, `branch`, `plan_id`, IDs e timestamps são o limite.
- **Não criar o diretório `.ahrena/workflow/sessions/` em commit** — sempre gitignored.
- **Não confundir `previous_session` com merge de sessões** — handoff é sequencial; não há múltiplas sessões `running` ao mesmo tempo no mesmo plano.

## Referências

- `lex-agent-planning` — front-matter do plano referencia `claude_session` + `session_entrypoint`
- `lex-pr-quality` — exige seção "Session Trace" no body do PR
- `kata-session-heartbeat` — procedimento operacional canônico
- `kata-pr-prepare` — constrói a seção "Session Trace" antes de abrir o PR
- `lex-directives` — chaves `session_tracking.*` em `.ahrena/.directives`
- `codex-pr-cost-tracking` — métrica de custo (tokens/USD), complementar à métrica de tempo aqui
