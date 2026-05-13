# Codex: Notificações Provider-Agnósticas via MCP

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Envio de notificações por agentes (Athena, Argos, Janus, Eunomia) via o servidor MCP de notificação configurado em `.ahrena/.directives`

## Visão Geral

Este Codex é o manual canônico de notificações no framework Ahrena. Define o contrato entre os agentes que publicam alertas (Athena no PR review timeout, Janus na release publicada, Eunomia no digest de planos) e o provider concreto (Slack, Discord, Teams) — sem amarrar Lexis, Codex ou Warriors a um vendor específico.

A regra é simples: agentes referenciam **chaves abstratas** (`notifications.provider` + `notifications.channels.{evento}`) lidas de `.ahrena/.directives`; este Codex traduz essas chaves para a tool MCP correspondente, em tempo de execução.

## Contexto

- **Domínio:** envio de notificações para canais de comunicação corporativa (Slack/Discord/Teams) por agentes IA do framework.
- **Público-alvo:** Athena, Argos, Janus, Eunomia, e qualquer agente que tenha gatilho de notificação no fluxo Issue-Driven.
- **Atualização:** quando um novo provider for adicionado ao framework, ou quando uma nova chave de canal lógico (`notifications.channels.*`) for definida.

## Conteúdo

### 1. Chaves abstratas em `.ahrena/.directives`

A seção `notifications:` em `.directives` (per `lex-directives`) declara:

```yaml
notifications:
  provider: slack                # slack | discord | teams | none
  channels:
    pr_review_timeout: "notifications-gh-pull-request"
    release_notify:    "notifications-gh-releases"
    plans_status:      "notifications-plans-status"
  working_hours:
    start: "07:00"
    end:   "22:00"
    timezone: "America/Sao_Paulo"
```

| Chave | Consumidor | Quando dispara |
|---|---|---|
| `notifications.channels.pr_review_timeout` | `warrior-athena` | Esgotamento dos 3 ciclos de 15 min sem aprovação humana em PR `to review` |
| `notifications.channels.release_notify` | `warrior-janus` | Release publicada (tag empurrada, `validate-tag.yml` passou, GitHub Release criada) |
| `notifications.channels.plans_status` | `warrior-eunomia` | Digest periódico de planos ativos no loop PM |

### 2. Mapeamento provider → tool MCP

Cada provider expõe um conjunto próprio de tools MCP. O agente lê `notifications.provider` e seleciona a tool correspondente:

| `provider` | Tool MCP usada | Manual do provider |
|---|---|---|
| `slack` | `slack_send_message` | `codex-mcp-slack` |
| `discord` | (futuro — `discord_post_message`) | (futuro `codex-mcp-discord`) |
| `teams` | (futuro — `teams_post_message`) | (futuro `codex-mcp-teams`) |
| `none` | nenhuma — agente loga warning e prossegue | — |

Quando um provider novo entra no framework, este Codex ganha uma linha; nenhum Lex/Warrior/Kata muda.

### 3. Resolução de canal lógico → canal real

A chave `notifications.channels.pr_review_timeout` carrega o **nome lógico** ("notifications-gh-pull-request" no exemplo). O agente passa esse valor diretamente para o parâmetro `channel` da tool MCP correspondente. Mapeamentos provider-específicos (ex.: Slack aceita nome do canal sem `#`; Discord usa ID numérico) ficam documentados em `codex-mcp-{provider}`.

### 4. Fluxo canônico de publicação

```
1. Agente decide notificar (Athena após 3º ciclo, Janus na release, etc.)
2. Agente lê notifications.provider de .ahrena/.directives
3. Se provider == "none" → log warning + prossegue (sem falhar)
4. Verifica que provider está em mcp.servers e MCP está ativo
5. Lê notifications.channels.{evento} (canal lógico)
6. Invoca tool MCP do provider com (channel=<lógico>, text=<msg>)
7. Em caso de erro do MCP: retry único (5s), depois log + prossegue
```

Princípios:

- **Provider == none**: agente NÃO falha o fluxo principal por causa da notificação. Loga warning estruturado e segue.
- **MCP indisponível**: per `lex-mcp` §4, retry único; se ainda falhar, apresenta as 3 opções (fallback CLI quando aplicável, pausar, abortar). Para notificações, o default é "log + prossegue" porque o fluxo principal já completou.
- **Janela útil**: `notifications.working_hours` aplica-se a digests não-críticos (Eunomia). Notificações de evento (PR timeout, release) ignoram a janela.

### 5. Conteúdo da mensagem

O payload mínimo inclui contexto suficiente para o canal agir sem necessidade de abrir o GitHub:

**PR review timeout (Athena):**

```
🟡 PR aguardando revisão há 45min sem aprovação humana
Repo: {owner/repo}  •  PR: #{N}  •  Autor: @{login}
Reviewers solicitados: @{a}, @{b}
Status: {gh pr view --json reviewDecision}
Link: https://github.com/{owner/repo}/pull/{N}
```

**Release publicada (Janus):**

```
🚀 Release {tag} publicada em {repo}
Tipo: {patch|minor|major}
Highlights: {top 3 entries do CHANGELOG}
Link: https://github.com/{owner/repo}/releases/tag/{tag}
```

**Plans status digest (Eunomia):**

```
📋 Digest de planos ativos — {date}
 stalled  ⚠️  3 planos sem heartbeat há >4h
 healthy 🟢 12 planos em movimento (last_activity < 30min)
 blocked 🚫 1 plano em changes-requested há >24h
[ver detalhes no anexo / link]
```

Mensagens devem ser **diretas**, **acionáveis** e **autocontidas** — per `lex-brand-voice`.

### 6. Trocar de provider

Mudança de provider é **3 passos** (zero edição de Lex/Codex/Warrior/Kata):

1. Adicionar `framework/mcp/{novo}.json` per `lex-mcp` §5 (preferir HTTP > binário > npx).
2. Habilitar via `make mcp-enable SERVER={novo}`.
3. Editar `notifications.provider` em `.ahrena/.directives` para o novo valor.

Os canais lógicos (`notifications.channels.*`) podem ser mantidos ou renomeados para corresponder à convenção do novo provider.

## Restrições

- **Não citar provider concreto em Lexis/Warriors/Katas.** Apenas `notifications.provider` e `notifications.channels.{key}`.
- **Não armazenar credenciais em `.directives`.** Per `lex-mcp` §2, credenciais vão em variáveis de ambiente.
- **Não tentar notificações antes do MCP estar listado em `mcp.servers`.** Per `lex-mcp` §3.

## Referências

- `lex-mcp` — regras de uso de MCP (preferência de transporte, fallback, autenticação)
- `lex-directives` — schema da seção `notifications:` em `.ahrena/.directives`
- `codex-mcp-common` — padrões compartilhados de MCP
- `codex-mcp-slack` — provider inicial (Slack)
- `lex-agent-planning` — owners das transições que disparam notificações
- `lex-brand-voice` — tom das mensagens
- `warrior-athena`, `warrior-janus`, `warrior-eunomia` — consumidores deste Codex
