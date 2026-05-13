# Kata: Atualizar Heartbeat de Sessão Claude Code

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Registro/atualização do heartbeat da sessão Claude Code corrente para um plano ativo

## Objetivo

Escrever ou atualizar o arquivo de heartbeat `.ahrena/workflow/sessions/<session-id>.json` da sessão Claude Code corrente. Idempotente, baixo custo, seguro de rodar em qualquer ponto do fluxo. Invocado por Eunomia (criação), Athena (transições), Argos (revisão) e Janus (release) em momentos significativos.

## Quando Usar

- Quando o agente entra num plano (Eunomia ao criar; Athena ao iniciar Phase 4; Argos em `cry-review-pr`; Janus em `kata-release-prepare`/`kata-release-publish`).
- Ao concluir um Step do plano ou uma kata invocada.
- Ao mudar o `status:` do plano.
- Periodicamente (a cada 5–10min) durante atividade prolongada.
- Por Eunomia em cada tick do loop PM antes de processar o digest.

## Inputs

| Input | Obrigatório | Descrição |
|---|:---:|---|
| `plan_id` | Sim | NNN do plano em uso (lido do front-matter do plano no worktree corrente) |
| `last_activity` | Sim | Identificador do passo/kata/cry corrente (ex.: `kata-pr-prepare:step3`, `cry-review-pr`) |
| `role` | Sim | `creator`, `executor`, `reviewer`, `releaser` |
| `previous_session` | Não | UUID da sessão anterior em caso de handoff |

Variáveis de ambiente lidas automaticamente:

| Variável | Origem | Tratamento se ausente |
|---|---|---|
| `CLAUDE_CODE_SESSION_ID` | Claude Code shell env | Pular kata sem erro (rodando fora do Claude Code) |
| `CLAUDE_CODE_ENTRYPOINT` | Claude Code shell env | Pular kata sem erro |
| `AI_AGENT` | Claude Code shell env | Aceitar valor vazio; demais campos seguem |

## Workflow

```
Progresso:
- [ ] 1. Ler variáveis de ambiente; se SESSION_ID/ENTRYPOINT ausentes, pular silenciosamente
- [ ] 2. Resolver heartbeat_dir de .ahrena/.directives (default .ahrena/workflow/sessions/)
- [ ] 3. Criar diretório se inexistente
- [ ] 4. Compor JSON conforme schema de codex-session-tracking §2
- [ ] 5. Se heartbeat file já existe com mesmo session_id, preservar started_at; senão, started_at = now
- [ ] 6. Atualizar last_heartbeat = now e last_activity per input
- [ ] 7. Escrever atomicamente (write + rename)
```

### Passo 1 — Ler variáveis de ambiente

```bash
SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
ENTRYPOINT="${CLAUDE_CODE_ENTRYPOINT:-}"
AGENT_VERSION="${AI_AGENT:-}"

if [[ -z "$SESSION_ID" || -z "$ENTRYPOINT" ]]; then
  # Rodando fora do Claude Code; heartbeat é no-op
  exit 0
fi
```

### Passo 2 — Resolver heartbeat_dir

Ler `session_tracking.heartbeat_dir` de `.ahrena/.directives` (default `.ahrena/workflow/sessions/`). Se `session_tracking.enabled == false`, pular silenciosamente.

### Passo 3 — Garantir diretório

```bash
mkdir -p .ahrena/workflow/sessions
```

(O diretório é gitignored por `.gitignore` — ver `codex-session-tracking` §6.)

### Passo 4 — Compor JSON

```json
{
  "session_id": "<SESSION_ID>",
  "entrypoint": "<ENTRYPOINT>",
  "agent_version": "<AGENT_VERSION>",
  "plan_id": "<plan_id input>",
  "branch": "<git rev-parse --abbrev-ref HEAD>",
  "cwd": "<pwd>",
  "started_at": "<preservado de arquivo existente OU now>",
  "last_heartbeat": "<now em ISO 8601>",
  "last_activity": "<last_activity input>",
  "role": "<role input>",
  "previous_session": "<previous_session input ou null>"
}
```

### Passo 5 — Preservar `started_at` em reescrita

Se `.ahrena/workflow/sessions/<SESSION_ID>.json` já existe, ler `started_at` do arquivo existente e preservar; só `last_heartbeat` e `last_activity` mudam.

### Passo 6+7 — Escrita atômica

```bash
TMP=$(mktemp)
echo "$JSON" > "$TMP"
mv "$TMP" ".ahrena/workflow/sessions/${SESSION_ID}.json"
```

Mover (`mv`) é atômico no mesmo filesystem — evita race quando duas chamadas concorrentes acontecem.

## Saídas

| Saída | Formato | Destino |
|---|---|---|
| Heartbeat file | JSON conforme schema | `.ahrena/workflow/sessions/<session-id>.json` |

Sem stdout obrigatório. Kata é silencioso em sucesso. Em falha (erro de I/O), reportar para stderr e propagar; o agente invocador decide se aborta ou prossegue.

## Restrições

- **Sem efeito colateral além do heartbeat file.** Não modifica plano, Issue, PR, ou git.
- **Sem credenciais ou dados sensíveis no JSON** per `codex-session-tracking`.
- **Idempotente.** Múltiplas chamadas rápidas sucessivas produzem o mesmo arquivo final.
- **No-op fora do Claude Code.** Sem `CLAUDE_CODE_SESSION_ID`, kata sai com código 0 sem erro.

## Referências

- `codex-session-tracking` — manual de referência (schema, cadência, limpeza, handoff)
- `lex-agent-planning` — front-matter do plano referencia `claude_session` + `session_entrypoint`
- `lex-pr-quality` — exige "Session Trace" no body do PR
- `kata-pr-prepare` — consome os heartbeat files na construção do "Session Trace"
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — invocadores
