# Lexis: Uso Obrigatório de Ferramentas MCP

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Uso de servidores MCP por agentes IA em projetos Ahrena

## Propósito

Servidores MCP (Model Context Protocol) expõem capacidades de sistemas externos — como GitHub, Notion e Figma — diretamente para agentes IA, com autenticação gerenciada e sem necessidade de construir chamadas de API manualmente. Quando um servidor MCP está ativo para uma operação, usá-lo é mais seguro, mais consistente e mais rastreável do que executar o CLI equivalente.

Esta Lexis existe para garantir que **todo agente prefira ferramentas MCP disponíveis sobre equivalentes de CLI**, que **credenciais nunca sejam expostas em arquivos rastreados** e que **apenas os servidores declarados no `.ahrena/.directives` sejam utilizados**.

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

### 4. Fallback quando MCP indisponível

Se o servidor MCP necessário não estiver disponível (servidor desligado, variável de ambiente ausente, ferramenta não suportada):

1. O agente **DEVE** informar ao usuário que o MCP não está disponível e qual é o motivo.
2. O agente **PODE** oferecer o equivalente de CLI como alternativa, identificando claramente que é um fallback.
3. O agente **NÃO DEVE** silenciosamente usar o CLI sem comunicar a indisponibilidade do MCP.

## Abrangência

- **Aplica-se a:** todas as operações em que um servidor MCP ativo provê uma ferramenta equivalente à operação solicitada.
- **Agentes vinculados:** todos os Warriors e agentes genéricos.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Credenciais expostas:** hardcoding de tokens em arquivos rastreados constitui uma violação de segurança grave; requer rotação imediata da credencial afetada.
2. **Servidores não autorizados:** uso de servidores não declarados viola o princípio de menor privilégio e pode expor dados do projeto a sistemas não aprovados.
3. **Inconsistência:** misturar MCP e CLI para a mesma operação sem critério cria resultados imprevisíveis e dificulta auditoria.
4. **Remediação:** o agente deve reler as diretivas, identificar os servidores MCP ativos e o Codex correspondente, e repetir a operação usando a ferramenta MCP correta.

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
