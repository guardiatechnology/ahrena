---
name: kata-session-heartbeat
description: "Atualizar Heartbeat de Sessão Claude Code. Registro/atualização do heartbeat da sessão Claude Code corrente para um plano ativo"
---

# Kata: Atualizar Heartbeat de Sessão Claude Code

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Registro/atualização do heartbeat da sessão Claude Code corrente para um plano ativo

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

## Suporte a tags

A kata aceita uma entrada opcional `tags` (ou a forma equivalente de CLI `--set-tags <kind> [topic1] [topic2]`) regida por `lex-session-tags`.

**Formas de invocação:**

```bash
# Posicional (ergonomia de CLI): kind primeiro, depois 0-2 topics
kata-session-heartbeat --set-tags tech-task reconciliation api

# Programática (invocação por outra kata ou warrior):
kata-session-heartbeat tags='{"kind":"tech-task","topics":["reconciliation","api"]}'
```

**Semântica de merge:**

- Quando `tags` é fornecido: valida contra `session_tracking.tags.*` em `.directives` (kind está em `kinds`; topics ≤ 2; total de slots ≤ 3); substitui o objeto `tags` do heartbeat atomicamente.
- Quando `tags` é omitido: preserva o objeto `tags` existente no heartbeat em disco (junto com `started_at`).
- Para limpar as tags: passe um objeto vazio explícito `tags={}` (renderizado no JSON como `"tags": {}` — ou remova a chave com `tags=null`).

**Merge atômico:**

A escrita atômica das Etapas 6+7 (`mktemp` → `mv`) já preserva o restante do JSON. O ramo de tags segue o mesmo caminho:

```bash
EXISTING=$(cat ".ahrena/workflow/sessions/${SESSION_ID}.json" 2>/dev/null || echo '{}')
NEW=$(echo "$EXISTING" | jq --argjson tags "$TAGS_JSON" '.tags = $tags')
TMP=$(mktemp)
echo "$NEW" > "$TMP"
mv "$TMP" ".ahrena/workflow/sessions/${SESSION_ID}.json"
```

**Erros de validação:**

Quando a validação em `lex-session-tags` falha (kind fora do vocabulário, > 2 topics, formato malformado), a kata sai com código 2 e imprime no stderr um erro de uma linha listando o vocabulário configurado. O arquivo de heartbeat fica intacto.

**Interação com auto-sugestão:**

`kata-session-tag-suggest` é a kata upstream que produz um objeto `tags` válido a partir do primeiro prompt do usuário. Esta kata NÃO a invoca — apenas escreve o que recebe. A orquestração (chamar-sugestão-depois-chamar-heartbeat) vive no hook do Plan B ou no `cry-tags --auto-suggest` invocado pelo usuário.
