# Codex: Notion MCP Server

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Ferramentas e autenticação do servidor MCP do Notion para Cursor e Claude Code

## Visão Geral

Este Codex é a referência para usar o **servidor MCP do Notion** em projetos Ahrena. Define as ferramentas disponíveis, seus parâmetros principais, autenticação e casos de uso típicos: sincronizar documentação do framework para o Notion, criar wikis, notas de reunião e páginas de projeto.

## Contexto

- **Domínio:** Operações de criação, leitura e atualização de conteúdo no Notion via MCP (páginas, blocos, databases, buscas).
- **Público-alvo:** Agentes IA que gerenciam documentação ou conhecimento no Notion em projetos Ahrena com o servidor MCP ativo.
- **Atualização:** Quando novas ferramentas forem adicionadas ao servidor MCP do Notion ou quando o schema de databases mudar.

## Conteúdo

### Configuração por plataforma

**Cursor (`.cursor/mcp.json`):**
```json
"notion": {
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": { "NOTION_API_KEY": "${env:NOTION_API_KEY}" }
}
```

**Claude Code (`.claude/settings.json`):**
```json
"notion": {
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": { "NOTION_API_KEY": "${NOTION_API_KEY}" }
}
```

> A variável `NOTION_API_KEY` deve estar definida no ambiente. Obtenha uma integration key em [notion.so/my-integrations](https://www.notion.so/my-integrations). A integration DEVE ter acesso às páginas/databases alvo (share explícito no Notion). Nunca hardcode tokens em arquivos rastreados (ver `lex-mcp`).

### Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `search` | Busca páginas e databases por título ou conteúdo |
| `get_page` | Obtém metadados e propriedades de uma página |
| `create_page` | Cria uma nova página em um parent (page ou database) |
| `update_page` | Atualiza propriedades de uma página existente |
| `get_block_children` | Lista os blocos filhos de uma página ou bloco |
| `append_block_children` | Adiciona blocos ao final de uma página ou bloco |
| `delete_block` | Remove um bloco específico |
| `list_databases` | Lista databases acessíveis pela integration |
| `query_database` | Consulta um database com filtros e ordenação |
| `get_database` | Obtém metadados e schema de um database |
| `create_database` | Cria um novo database em uma página |

### Parâmetros das ferramentas mais usadas

**`create_page`**
```
parent        (object, obrigatório) — {"page_id": "..."} ou {"database_id": "..."}
properties    (object, obrigatório) — propriedades da página; para page simples: {"title": [{"text": {"content": "Título"}}]}
children      (array, opcional)     — lista de blocos de conteúdo inicial
icon          (object, opcional)    — ícone da página (emoji ou file)
cover         (object, opcional)    — imagem de capa
```

**`append_block_children`**
```
block_id      (string, obrigatório) — ID da página ou bloco pai
children      (array, obrigatório)  — lista de blocos a adicionar
```

Tipos de bloco comuns em `children`:
```json
{ "type": "paragraph", "paragraph": { "rich_text": [{"text": {"content": "Texto"}}] } }
{ "type": "heading_2", "heading_2": { "rich_text": [{"text": {"content": "Seção"}}] } }
{ "type": "bulleted_list_item", "bulleted_list_item": { "rich_text": [{"text": {"content": "Item"}}] } }
{ "type": "code", "code": { "language": "python", "rich_text": [{"text": {"content": "print('hello')"}}] } }
```

**`query_database`**
```
database_id   (string, obrigatório) — ID do database
filter        (object, opcional)    — filtro por propriedade
sorts         (array, opcional)     — ordenação [{property, direction}]
page_size     (integer, opcional)   — máximo de resultados (default: 100)
```

**`search`**
```
query         (string, opcional)    — texto a buscar (vazio retorna todos)
filter        (object, opcional)    — {"property": "object", "value": "page"} ou "database"
sort          (object, opcional)    — {"direction": "descending", "timestamp": "last_edited_time"}
```

### Casos de uso típicos

| Caso | Ferramentas |
|---|---|
| Sincronizar doc do framework para Notion | `search` → `create_page` ou `update_page` + `append_block_children` |
| Criar nota de reunião estruturada | `create_page` com `children` pré-formatados |
| Atualizar wiki do projeto | `search` → `get_page` → `append_block_children` |
| Consultar database de tarefas | `query_database` com filtros de status |
| Listar databases disponíveis | `list_databases` |

### Exemplo de uso: criar página de documentação

```
# 1. Verificar se página já existe
search(query="Lexis: MCP Tools", filter={"property": "object", "value": "page"})

# 2. Se não existir, criar na wiki do projeto
create_page(
  parent={"page_id": "ID-DA-WIKI"},
  properties={"title": [{"text": {"content": "Lexis: MCP Tools"}}]},
  children=[
    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Propósito"}}]}},
    {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Esta Lexis define..."}}]}}
  ]
)
```

## Referências

- `lex-mcp` — Leis de uso de ferramentas MCP
- `kata-mcp-notion-sync` — Kata de sincronização de documentação para Notion
- [Notion MCP Server — repositório oficial](https://github.com/makenotion/notion-mcp-server)
- [Notion API — Block types](https://developers.notion.com/reference/block)
