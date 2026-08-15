# Codex: Slack MCP Server

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Ferramentas e autenticação do servidor MCP do Slack para Cursor e Claude Code

## Conteúdo

### Configuração por plataforma

As duas plataformas consomem o **servidor remoto oficial do Slack** em `https://mcp.slack.com/mcp` (degrau 1 da preferência de transporte definida em `lex-mcp` §5 — zero dependência local). Auth é **OAuth 2.0 confidencial**: na primeira chamada, o usuário autentica via browser usando o `client_id` + `client_secret` do app Slack; o token é gerenciado pela plataforma.

> Fonte: "Slack supports JSON-RPC 2.0 over Streamable HTTP. All requests should be sent to: `https://mcp.slack.com/mcp`" e "Slack supports confidential OAuth for MCP clients. You'll need to use your app's `client_id` and `client_secret`."

**Cursor (`.cursor/mcp.json`):**
```json
"slack": {
  "url": "https://mcp.slack.com/mcp"
}
```

**Claude Code (`.mcp.json`):**
```json
"slack": {
  "type": "http",
  "url": "https://mcp.slack.com/mcp"
}
```

Não há variáveis de ambiente em `.directives` ou no JSON. Não há fallback via npx ou binário porque o Slack expõe **somente** HTTP no momento (oficial: "We do not support SSE-based connections or Dynamic Client Registration at this time"). Caso o time precise de um caminho alternativo (CI sem browser, integração programática), abrir ADR registrando a exceção.

### Ativação

```bash
# 1. Listar mcp.servers em .ahrena/.directives e descomentar "slack"
# 2. Habilitar via make:
make mcp-enable SERVER=slack

# 3. Reabrir Cursor / Claude Code; na primeira invocação, fluxo OAuth abre no browser.
```

### Ferramentas expostas

Categorias documentadas no overview oficial:

| Categoria | Tools (nomes representativos) | Uso típico no framework |
|---|---|---|
| **Search** | `slack_search_messages`, `slack_search_files`, `slack_search_channels`, `slack_search_users` | Buscar discussão prévia de um tópico antes de notificar |
| **Messages** | `slack_send_message`, `slack_send_message_draft`, `slack_read_channel`, `slack_read_thread`, `slack_schedule_message` | Athena, Janus, Eunomia publicam notificações via `slack_send_message` |
| **Canvas** | `slack_create_canvas`, `slack_read_canvas`, `slack_update_canvas` | Eunomia publica digest periódico como canvas atualizado |
| **Profiles** | `slack_read_user_profile` | Resolver `@login` para nome real em alertas |

> Os nomes exatos podem variar conforme o cliente; o servidor MCP do Slack expõe a lista via `tools/list` na primeira conexão. Consulte sempre a doc oficial para o nome canônico em uso.

### `slack_send_message` — invocação canônica

Ferramenta primária consumida por `codex-notifications`. Parâmetros relevantes:

| Parâmetro | Origem | Exemplo |
|---|---|---|
| `channel` | `notifications.channels.{evento}` de `.ahrena/.directives` | `"notifications-gh-pull-request"` (sem `#`) |
| `text` | Construído pelo agente per template de `codex-notifications` §5 | Multiline com link do PR/Release |
| `thread_ts` | (opcional) Para responder a um thread existente | — |

O agente lê o valor lógico de `.directives` e passa **diretamente** como `channel`. Nomes no Slack workspace devem coincidir com os canais lógicos. Se o canal não existir, o MCP retorna erro estruturado — per `lex-mcp` §4, retry único + log + prossegue.

### Resolução de canal lógico → canal real do Slack

A convenção do framework Ahrena:

| Chave lógica em `.directives` | Nome esperado no Slack workspace |
|---|---|
| `notifications.channels.pr_review_timeout` | `notifications-gh-pull-request` |
| `notifications.channels.release_notify` | `notifications-gh-releases` |
| `notifications.channels.plans_status` | `notifications-plans-status` |

Times podem renomear os canais lógicos para coincidir com sua nomenclatura interna (ex.: `eng-pr-alerts`), desde que atualizem `.ahrena/.directives` no mesmo passo.

### Autenticação OAuth — primeira execução

1. Agente invoca uma tool do Slack pela primeira vez (ex.: `slack_send_message`).
2. Cursor / Claude Code abre o browser no fluxo OAuth do Slack.
3. Usuário autoriza o app no workspace correspondente (escopos: leitura de mensagens, envio em canais, leitura de perfis — conforme app registrado).
4. Token armazenado pela plataforma (não toca `.directives`).
5. Próximas chamadas usam o token automaticamente.

Per `lex-mcp` §2, **nenhum** token, `client_id` ou `client_secret` vai para `.ahrena/.directives` ou para arquivo versionado. Configuração do app Slack é feita uma vez no workspace, pelo admin.

### Fallback quando MCP indisponível

Para notificações, o `codex-notifications` §4 define o comportamento:

1. Retry único (5s).
2. Se ainda falha, log estruturado + prossegue. O fluxo principal (Athena terminando o loop de revisão, Janus terminando a release, etc.) NÃO falha por isso.

Para leitura de contexto via Slack (uso menos comum), aplica-se `lex-mcp` §4 padrão: apresentar 3 opções ao usuário (fallback CLI quando aplicável — não existe para Slack hoje; pausar; abortar).

## Restrições

- **Sem stdio/npx**: o Slack MCP é HTTP-only no momento. Não tentar inventar fallback npx sem ADR.
- **Sem credenciais em código/.directives**: per `lex-mcp` §2.
- **Não confundir canais lógicos com IDs**: o agente passa **nome** do canal (sem `#`), não ID `C0123...`. Slack MCP resolve internamente.
