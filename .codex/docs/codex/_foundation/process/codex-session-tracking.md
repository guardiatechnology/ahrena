# Codex: Tracking de Sessão Claude Code

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Registro da sessão Claude Code que opera em cada plano e da trilha de sessões que tocou cada PR

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

### 9. Tags de sessão

Sessões PODEM carregar até 3 tags curtas escritas no heartbeat sob o objeto `tags`. As tags expõem a intenção da sessão (kind + topics livres) ao humano através do statusline do Claude Code, do sidebar da extensão ahrena-vscode e do digest de planos do Eunomia.

**Formato no heartbeat:**

```json
"tags": {
  "kind": "tech-task",
  "topics": ["session-tracking", "framework"]
}
```

**Schema:**

| Campo | Tipo | Obrigatório | Descrição |
|---|---|:---:|---|
| `tags.kind` | string | Quando `tags` está presente | Um valor de `session_tracking.tags.kinds` em `.directives` |
| `tags.topics` | array de 0–2 strings | Não | Livres, recomendado em letra minúscula kebab-case, ≤ 20 caracteres cada |

O máximo é **3 slots no total** (1 `kind` + até 2 `topics`). O formato é fixo: o objeto `{kind, topics: [...]}`. Arrays planos ou chaves extras são rejeitados.

**Contrato de escrita:**

- As tags são fundidas no heartbeat via `kata-session-heartbeat --set-tags`.
- Escrita atômica (arquivo temporário + `mv`) preserva o restante do JSON (`session_id`, `started_at`, `last_activity`, …).
- Compatível com versões anteriores: heartbeats escritos antes das tags existirem não têm a chave `tags` e cada leitor trata o campo como opcional.

**Contrato de leitura:**

- O script do statusline lê `tags.kind` e `tags.topics[]` e exibe chips após a branch (ex.: `main ahrena · [tech-task] [reconciliation]`).
- A extensão ahrena-vscode observa `.ahrena/workflow/sessions/<id>.json` e renderiza chips na linha da sessão.
- O digest de planos do Eunomia agrega as tags por sessão ativa no relatório periódico de status.

**Sugestão automática:**

Quando `session_tracking.tags.auto_suggest: true` e o heartbeat não tem objeto `tags`, o agente invoca `kata-session-tag-suggest` no primeiro turno do usuário da sessão e escreve o resultado via `kata-session-heartbeat`. Uma nota de visibilidade de uma linha na mesma resposta mostra as tags escolhidas para o usuário corrigir via `/cry-tags set` caso a inferência tenha errado. Re-executar a auto-sugestão quando `tags` já está presente é rejeitado — as tags têm escopo de sessão; apenas o usuário as limpa.

O contrato é regido por `lex-session-tags`.

## Restrições

- **Não persistir credenciais ou dados sensíveis** no heartbeat file — `cwd`, `branch`, `plan_id`, IDs e timestamps são o limite.
- **Não criar o diretório `.ahrena/workflow/sessions/` em commit** — sempre gitignored.
- **Não confundir `previous_session` com merge de sessões** — handoff é sequencial; não há múltiplas sessões `running` ao mesmo tempo no mesmo plano.
