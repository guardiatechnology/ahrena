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

As duas plataformas consomem o **servidor remoto oficial da GitHub** em `https://api.githubcopilot.com/mcp/` (degrau 1 da preferência de transporte definida em `lex-mcp` §5 — zero dependência local).

**Cursor (`.cursor/mcp.json`):**
```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${env:GH_TOKEN}" }
}
```

**Claude Code (`.mcp.json`):**
```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": { "Authorization": "Bearer ${GH_TOKEN}" }
}
```

> A variável `GH_TOKEN` deve estar definida no ambiente (token clássico ou fine-grained). O nome casa com a convenção do CLI `gh` e com a variável documentada do servidor MCP do GitHub. Nunca hardcode tokens em arquivos rastreados (ver `lex-mcp`).
>
> Diferença sintática proposital: Cursor usa `${env:VAR}` para interpolar variáveis de ambiente; Claude Code usa `${VAR}`. Ambas as formas resolvem para o mesmo valor de runtime.

#### Escopos OAuth requeridos

Um PAT clássico usado com o MCP do GitHub DEVE conceder os seguintes escopos para a superfície completa de ferramentas (issues, PRs, branches, workflows, lookups de usuário):

| Escopo | Por quê |
|---|---|
| `repo` | Leitura/escrita em issues, PRs, branches, arquivos, commits |
| `read:org` | Listar times, membros e code owners da organização |
| `workflow` | Ler execuções de workflow, disparar reruns (usado por katas de release/CI) |
| `read:user` | Resolver `@me` e identidades de assignees |

O `scripts/install.py` verifica esses escopos no momento do install quando `GH_TOKEN` está definida e emite uma linha de aviso (apenas warn, nunca bloqueia) por escopo faltante, com a sugestão pronta para colar: `gh auth refresh -s <escopo>`. Falhas de rede ou PATs fine-grained (que não expõem o cabeçalho `X-OAuth-Scopes`) caem para uma única linha consultiva.

#### Override para o caminho npx legacy

A versão npx (`@modelcontextprotocol/server-github`) está deprecated, mas continua funcional. Times que precisam dela (ambiente air-gapped, cobertura de ferramentas que ainda não chegou ao endpoint hosted) podem sobrescrever o JSON do servidor em `.ahrena/mcp/github.json` com um desvio justificado por `_comment`, conforme `lex-mcp` §5:

```json
{
  "_comment": "Override: usando o pacote npx @modelcontextprotocol/server-github por <razão>. Decisão registrada em ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GH_TOKEN}" }
  },
  "claude-code": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GH_TOKEN}" }
  }
}
```

O override exige Node.js no ambiente; rode `make mcp-enable SERVER=github PLATFORM=...` que o preflight oferece instalar quando faltar.

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
- [GitHub MCP Server — repositório oficial em Go](https://github.com/github/github-mcp-server) (binário/HTTP mantido pela GitHub)
- [Claude Code — documentação MCP](https://code.claude.com/docs/en/mcp)
- `_foundation/contributing/katas/kata-contribute` — Kata de contribuição que usa GitHub MCP
