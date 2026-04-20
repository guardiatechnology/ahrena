# Codex: GitHub MCP Server

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Ferramentas e autenticação do servidor MCP do GitHub para Cursor e Claude Code

## Visão Geral

Este Codex é a referência para usar o **servidor MCP do GitHub** em projetos Ahrena. Ver `codex-mcp-common` para padrões MCP compartilhados (autenticação, configuração, fallback). Este documento foca em ferramentas, parâmetros e exemplos específicos do GitHub. Consultado por Warriors e Katas que realizam operações de repositório (issues, pull requests, branches, arquivos, buscas).

## Contexto

- **Domínio:** Operações de repositório GitHub via MCP (issues, PRs, branches, commits, arquivos, buscas, discussions).
- **Público-alvo:** Agentes IA que executam operações GitHub em projetos Ahrena com o servidor MCP ativo.
- **Atualização:** Quando novas ferramentas forem adicionadas ao servidor MCP do GitHub ou quando parâmetros mudarem.

## Conteúdo

### Configuração por plataforma

**Cursor (`.cursor/mcp.json`):**
```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${env:GITHUB_PAT}" }
}
```

**Claude Code (`.claude/settings.json`):**
```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}" }
}
```

> A variável `GITHUB_PAT` deve estar definida no ambiente. Nunca hardcode tokens em arquivos rastreados (ver `lex-mcp`).

### Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `create_issue` | Cria uma issue no repositório |
| `list_issues` | Lista issues com filtros (state, labels, assignee) |
| `get_issue` | Obtém detalhes de uma issue específica |
| `add_issue_comment` | Adiciona comentário a uma issue |
| `create_pull_request` | Cria um pull request |
| `list_pull_requests` | Lista PRs com filtros (state, head, base) |
| `get_pull_request` | Obtém detalhes de um PR específico |
| `merge_pull_request` | Faz merge de um PR |
| `create_branch` | Cria uma nova branch no repositório |
| `push_files` | Faz push de um ou mais arquivos para uma branch |
| `get_file_contents` | Obtém o conteúdo de um arquivo ou diretório |
| `list_commits` | Lista commits de uma branch |
| `search_repositories` | Busca repositórios no GitHub |
| `search_code` | Busca código em repositórios |
| `fork_repository` | Faz fork de um repositório |
| `create_repository` | Cria um novo repositório |

### Parâmetros das ferramentas mais usadas

**`create_pull_request`**
```
owner         (string, obrigatório) — dono do repositório
repo          (string, obrigatório) — nome do repositório
title         (string, obrigatório) — título do PR
head          (string, obrigatório) — branch de origem
base          (string, obrigatório) — branch de destino (ex.: "main")
body          (string, opcional)    — descrição do PR (Markdown)
draft         (boolean, opcional)   — criar como rascunho
```

**`create_issue`**
```
owner         (string, obrigatório) — dono do repositório
repo          (string, obrigatório) — nome do repositório
title         (string, obrigatório) — título da issue
body          (string, opcional)    — descrição (Markdown)
labels        (array, opcional)     — lista de labels
assignees     (array, opcional)     — lista de assignees
```

**`push_files`**
```
owner         (string, obrigatório) — dono do repositório
repo          (string, obrigatório) — nome do repositório
branch        (string, obrigatório) — branch de destino
message       (string, obrigatório) — mensagem de commit
files         (array, obrigatório)  — [{path, content}] — conteúdo em string
```

**`get_file_contents`**
```
owner         (string, obrigatório) — dono do repositório
repo          (string, obrigatório) — nome do repositório
path          (string, obrigatório) — caminho do arquivo ou diretório
branch        (string, opcional)    — branch (default: branch padrão)
```

### Quando usar MCP vs CLI `gh`

| Situação | Usar |
|---|---|
| Servidor MCP do GitHub listado em `mcp.servers` | **MCP** (sempre, conforme `lex-mcp`) |
| Servidor MCP indisponível ou variável não definida | CLI `gh` como fallback (comunicar indisponibilidade) |
| Operação não coberta pelas ferramentas MCP acima | CLI `gh` ou API REST diretamente |

### Exemplo de uso: criar PR com body estruturado

```
create_pull_request(
  owner="acme",
  repo="meu-projeto",
  title="feat(auth): implementar OAuth2",
  head="feat/oauth2",
  base="main",
  body="## Resumo\n\n- Adiciona fluxo OAuth2 com PKCE\n- Integra com provider configurado em `.env`\n\n## Como testar\n\n1. Definir `OAUTH_CLIENT_ID` e `OAUTH_CLIENT_SECRET`\n2. Rodar `make dev` e acessar `/auth/login`",
  draft=False
)
```

## Referências

- `lex-mcp` — Leis de uso de ferramentas MCP
- `kata-mcp-notion-read` — Kata para consulta de conteúdo do Notion (padrão análogo)
- `kata-mcp-github-read` — Kata de consulta de repositórios e código no GitHub (somente leitura)
- [GitHub MCP Server — repositório oficial](https://github.com/modelcontextprotocol/servers)
- `_foundation/contributing/katas/kata-contribute` — Kata de contribuição que usa GitHub MCP
