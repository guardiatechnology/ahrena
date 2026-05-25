# Kata: Consultar projetos e código no GitHub via MCP

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Leitura de repositórios, issues, pull requests, commits e código no GitHub via servidor MCP

## Objetivo

Buscar e ler informações de repositórios GitHub (código, issues, PRs, commits, branches) via servidor MCP, trazendo os dados para o contexto da sessão para referência, análise ou revisão. Esta kata é estritamente **somente leitura** — nenhum arquivo, issue, PR ou branch é criado ou modificado.

## Quando Usar

- Quando o usuário precisa inspecionar código de um repositório GitHub sem baixá-lo localmente
- Quando é necessário consultar issues ou PRs em aberto para contexto de uma tarefa
- Quando se quer revisar o histórico de commits ou a estrutura de branches de um repositório
- Quando é necessário buscar código em repositórios para referência ou comparação

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Repositório | Sim | `owner/repo` (ex.: `guardiatechnology/ahrena`) |
| Objeto | Sim | O que consultar: `code`, `issues`, `prs`, `commits`, `branches`, `file` |
| Consulta ou caminho | Depende | Termo de busca (para `code`), caminho (para `file`), filtros (para `issues`/`prs`) |
| Branch | Não | Branch de referência; padrão: branch padrão do repositório |

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições MCP e directives
- [ ] 2. Identificar repositório e objeto de consulta
- [ ] 3. Buscar e ler o conteúdo
- [ ] 4. Apresentar resultado ao usuário
```

### Passo 1: Verificar pré-condições MCP e directives

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Verificar que `github` está listado em `mcp.servers` (conforme `lex-mcp`). Se não estiver, informar ao usuário e encerrar.
3. Confirmar que a variável de ambiente `GITHUB_PAT` está definida. Se não estiver, informar ao usuário qual variável configurar e encerrar.
4. Consultar `codex-mcp-github` para identificar as ferramentas e parâmetros corretos.

### Passo 2: Identificar repositório e objeto de consulta

1. Confirmar o repositório (`owner/repo`) com o usuário — solicitar se não foi informado.
2. Identificar o objeto de consulta:
   - **`file`** — conteúdo de um arquivo ou listagem de diretório
   - **`code`** — busca de código por termo ou padrão
   - **`issues`** — lista ou detalhes de issues
   - **`prs`** — lista ou detalhes de pull requests
   - **`commits`** — histórico de commits de uma branch
   - **`branches`** — branches disponíveis no repositório (via listagem de commits por branch)
3. Se o objeto não foi especificado, perguntar ao usuário qual aspecto do repositório deseja consultar.

### Passo 3: Buscar e ler o conteúdo

**Objeto `file`:**
1. Chamar `get_file_contents(owner, repo, path, branch)`.
2. Se `path` for um diretório, listar os itens retornados e perguntar ao usuário qual arquivo expandir.
3. Se `path` for um arquivo, apresentar o conteúdo completo com destaque de linguagem.

**Objeto `code`:**
1. Chamar `search_code(query="{termo} repo:{owner}/{repo}")`.
2. Apresentar os arquivos correspondentes com trechos relevantes.
3. Para cada arquivo de interesse, chamar `get_file_contents` para obter o conteúdo completo se o usuário solicitar.

**Objeto `issues`:**
1. Chamar `list_issues(owner, repo, state, labels, assignee)` com os filtros fornecidos pelo usuário.
2. Apresentar a lista (número, título, estado, labels, assignee, data de abertura).
3. Se o usuário quiser detalhes de uma issue específica, chamar `get_issue(owner, repo, issue_number)`.

**Objeto `prs`:**
1. Chamar `list_pull_requests(owner, repo, state, head, base)` com os filtros fornecidos.
2. Apresentar a lista (número, título, estado, branch de origem/destino, autor, data).
3. Se o usuário quiser detalhes de um PR específico, chamar `get_pull_request(owner, repo, pull_number)`.

**Objeto `commits`:**
1. Chamar `list_commits(owner, repo, branch)`.
2. Apresentar o histórico (hash abreviado, mensagem, autor, data).
3. Limitar a exibição aos 20 commits mais recentes por padrão; perguntar ao usuário se deseja mais.

### Passo 4: Apresentar resultado ao usuário

1. Apresentar o conteúdo recuperado de forma estruturada e legível.
2. Para listas (issues, PRs, commits): usar formato de tabela com os campos mais relevantes.
3. Para arquivos e código: preservar a formatação original com bloco de código e linguagem identificada.
4. Incluir o link direto para o item no GitHub (URL) quando disponível na resposta da ferramenta.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Conteúdo de arquivo | Bloco de código com linguagem identificada | Resposta ao usuário |
| Resultados de busca de código | Lista de arquivos com trechos relevantes | Resposta ao usuário |
| Lista de issues / PRs | Tabela com campos relevantes | Resposta ao usuário |
| Histórico de commits | Tabela (hash, mensagem, autor, data) | Resposta ao usuário |

## Restrições

- **Somente leitura:** esta kata nunca cria branches, issues, PRs, comentários ou faz push de arquivos.
- **Usar apenas MCP:** nunca usar o CLI `gh` ou a API REST do GitHub diretamente quando o servidor MCP estiver ativo (conforme `lex-mcp`).
- **Sem credenciais hardcoded:** autenticação exclusivamente via variável de ambiente `GITHUB_PAT`.
- **Confirmar repositório:** sempre confirmar `owner/repo` com o usuário antes de iniciar a consulta.

## Referências

- `lex-mcp` — Leis de uso de ferramentas MCP
- `codex-mcp-github` — Referência de ferramentas e parâmetros do GitHub MCP
- `lex-directives` — Como ler `.ahrena/.directives`
