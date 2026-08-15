# Lexis: Uso Obrigatório de Ferramentas MCP

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Uso de servidores MCP por agentes IA em projetos Ahrena

## Lei

> **Todo agente DEVE usar a ferramenta MCP disponível quando um servidor MCP ativo provê uma capacidade para a operação atual. Credenciais de autenticação DEVEM ser fornecidas exclusivamente via variáveis de ambiente. O agente NÃO PODE usar servidores MCP não listados em `mcp.servers` em `.ahrena/.directives`.**

## Regras

### 1. Preferência por ferramentas MCP

Ao executar uma operação suportada por um servidor MCP ativo, o agente **DEVE**:

1. Verificar se o servidor MCP correspondente está listado em `mcp.servers` em `.ahrena/.directives`.
2. Usar a ferramenta MCP em vez do equivalente de CLI (ex.: usar `create_pull_request` do GitHub MCP em vez de `gh pr create`).
3. Consultar o Codex do servidor MCP correspondente (`codex-mcp-github`, `codex-mcp-notion`, `codex-mcp-figma`) para identificar a ferramenta e os parâmetros corretos.

### 2. Autenticação exclusivamente via variáveis de ambiente

O agente **DEVE** garantir que:

1. Credenciais (tokens, API keys) são fornecidas apenas via variáveis de ambiente referenciadas nos arquivos de configuração MCP (`mcp.json`, `settings.json`).
2. Nenhum token, API key ou segredo é escrito em `.ahrena/.directives`, em arquivos rastreados pelo git ou em qualquer artefato gerado.
3. Caso a variável de ambiente necessária não esteja definida, o agente informa ao usuário qual variável configurar antes de prosseguir.

### 3. Uso restrito aos servidores declarados

O agente **NÃO PODE**:

1. Ativar ou usar um servidor MCP não declarado em `mcp.servers` em `.ahrena/.directives`.
2. Adicionar servidores MCP à configuração de plataforma (`.cursor/mcp.json`, `.claude/settings.json`) sem instrução explícita do usuário.
3. Alterar a seção `mcp.servers` em `.ahrena/.directives` sem solicitação explícita do usuário.

### 4. Comportamento de fallback quando MCP indisponível

Se o servidor MCP necessário está indisponível no meio da operação (servidor desligado, variável de ambiente ausente, ferramenta não suportada, rate-limit, timeout):

1. **Retry uma vez** com backoff breve (padrão: 5 segundos). Falhas transientes acontecem; um retry evita escalação espúria.
2. Se o retry ainda falha, o agente **DEVE** informar o usuário com contexto estruturado:
   - Qual servidor (`github`, `notion`, `figma`).
   - Qual ferramenta foi tentada.
   - Erro observado (status HTTP, mensagem).
3. O agente **DEVE** então oferecer escolhas explícitas — não escolher silenciosamente:
   - **(a)** Usar o CLI equivalente como fallback (quando existe e é seguro), claramente rotulado como fallback.
   - **(b)** Pausar o fluxo até o usuário restaurar conectividade (credenciais, restart do servidor).
   - **(c)** Abortar a operação com mensagem clara.
4. O agente **NÃO PODE** silenciosamente cair para CLI sem a escolha apresentada no Passo 3.
5. O agente **NÃO PODE** entrar em loop de retry além do Passo 1 — falha persistente exige decisão humana.

Sinais comuns de falha e suas causas típicas estão listados em `codex-mcp-common` — consultar antes de apresentar ao usuário.

### 5. Preferência de transporte na escolha do servidor MCP

Ao declarar um servidor MCP em `framework/mcp/{nome}.json` (ou override em `.ahrena/mcp/{nome}.json`), o agente **DEVE** escolher o transporte na seguinte ordem de preferência:

1. **HTTP remoto** — servidor hospedado pelo fornecedor, acessado via URL HTTPS. Preferido quando o fornecedor oferece endpoint oficial.
2. **Binário nativo** stdio — executável distribuído pelo fornecedor (ex.: `github-mcp-server`). Segunda escolha quando não há HTTP remoto.
3. **npx** (pacote npm) — apenas quando o servidor não tem HTTP remoto nem binário oficial.

Cada degrau adiciona uma classe de dependência local: HTTP remoto exige zero runtime; binário exige só o executável; npx exige Node.js. A ordem minimiza a superfície de instalação no ambiente de desenvolvimento.

Desvios à ordem **DEVEM** ser justificados em comentário (`_comment`) no JSON do servidor. Justificativas legítimas incluem: (a) o degrau preferido não existe para o fornecedor; (b) o time precisa de uma característica específica do degrau inferior (ex.: configuração compartilhada via variável de ambiente em vez de OAuth-per-user). Justificativas como "preferência pessoal" ou "já estou acostumado" não são legítimas.

A racional dos trade-offs por degrau (latência, controle de versão, atualização, dep local) está em `codex-mcp-common`. Docker não faz parte da hierarquia hoje; quando um servidor MCP em Docker for adotado, o degrau correspondente **DEVE** ser definido por ADR.

## Exemplos

### Correto

```
# mcp.servers em .ahrena/.directives lista "github"
# Agente cria PR via MCP:
create_pull_request(
  owner="acme",
  repo="meu-projeto",
  title="feat: nova funcionalidade",
  head="feat/nova",
  base="main"
)
```

```
# Variável de ambiente configurada externamente:
# export NOTION_API_KEY="secret_..."
# Agente cria página no Notion via MCP:
create_page(parent={"database_id": "..."}, properties={...})
```

### Incorreto

```
# ❌ Hardcoding de token em .directives ou em qualquer arquivo rastreado:
# mcp_token: "ghp_abc123..."

# ❌ Usando gh CLI quando MCP GitHub está disponível e listado:
# gh pr create --title "feat: nova" --base main

# ❌ Usando servidor MCP não listado em mcp.servers:
# (usando servidor MCP de um sistema não declarado nas diretivas)
```

## Validação Automatizada

- **Ferramenta:** verificação pelo próprio agente antes de executar operações cobertas por MCP; `validate.py` verifica que `mcp.servers` está presente no `.directives` quando arquivos de configuração MCP existem.
- **Momento:** ao iniciar qualquer operação que envolva GitHub, Notion ou Figma.
- **Métrica:** 100% das operações cobertas por MCP ativo devem usar a ferramenta MCP; 0 credenciais em arquivos rastreados.
