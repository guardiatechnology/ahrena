---
name: kata-mcp-notion-read
description: "Consultar conteúdo do Notion via MCP. Leitura de páginas, databases e blocos do Notion via servidor MCP para uso no contexto local"
---

# Kata: Consultar conteúdo do Notion via MCP

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Leitura de páginas, databases e blocos do Notion via servidor MCP para uso no contexto local

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições MCP e directives
- [ ] 2. Identificar o que buscar
- [ ] 3. Buscar e ler o conteúdo
- [ ] 4. Apresentar resultado ao usuário
```

### Passo 1: Verificar pré-condições MCP e directives

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Verificar que `notion` está listado em `mcp.servers` (conforme `lex-mcp`). Se não estiver, informar ao usuário e encerrar.
3. Confirmar que a variável de ambiente `NOTION_API_KEY` está definida. Se não estiver, informar ao usuário qual variável configurar e encerrar.
4. Consultar `codex-mcp-notion` para identificar as ferramentas e parâmetros corretos.

### Passo 2: Identificar o que buscar

1. Se o usuário forneceu um ID ou URL de página: usar no Passo 3 com `get_page`.
2. Se o usuário forneceu um ID de database: usar no Passo 3 com `query_database`.
3. Se o usuário forneceu um termo de busca: usar no Passo 3 com `search`.
4. Se nenhum input foi fornecido, solicitar ao usuário: "Qual página, database ou termo deseja consultar no Notion?"

### Passo 3: Buscar e ler o conteúdo

**Modo `search`:**
1. Chamar `search(query="{termo}")` para localizar páginas e databases correspondentes.
2. Apresentar a lista de resultados (título, tipo, última edição) e confirmar com o usuário qual item detalhar.
3. Para o item selecionado, chamar `get_page(page_id="{id}")`.
4. Se profundidade for `full`: chamar `get_block_children(block_id="{id}")` para obter o conteúdo completo.

**Modo `page`:**
1. Chamar `get_page(page_id="{id}")` para obter metadados e propriedades.
2. Se profundidade for `full`: chamar `get_block_children(block_id="{id}")` para obter os blocos de conteúdo.

**Modo `database`:**
1. Chamar `query_database(database_id="{id}", filter={...})` com filtros opcionais informados pelo usuário.
2. Para cada entrada retornada, registrar: título, propriedades relevantes, ID da página.
3. Se o usuário solicitar detalhes de uma entrada específica, chamar `get_page` e `get_block_children` para essa entrada.

### Passo 4: Apresentar resultado ao usuário

1. Apresentar o conteúdo recuperado de forma estruturada e legível.
2. Para databases: exibir as entradas em formato de tabela com as propriedades mais relevantes.
3. Para páginas: exibir título, metadados (última edição, criador) e conteúdo (resumo ou completo conforme profundidade).
4. Indicar o ID e URL de cada item apresentado para referência futura.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Conteúdo de página | Texto estruturado (título, metadados, blocos) | Resposta ao usuário |
| Entradas de database | Tabela com propriedades relevantes | Resposta ao usuário |
| Resultados de busca | Lista de itens correspondentes com título e tipo | Resposta ao usuário |

## Restrições

- **Somente leitura:** esta kata nunca cria, modifica ou exclui páginas, blocos ou propriedades no Notion.
- **Usar apenas MCP:** nunca usar a API REST do Notion diretamente; sempre usar ferramentas do servidor MCP (conforme `lex-mcp`).
- **Sem credenciais hardcoded:** autenticação exclusivamente via variável de ambiente `NOTION_API_KEY`.
- **Confirmar antes de busca ampla:** se a consulta puder retornar muitos resultados, apresentar amostra e perguntar ao usuário antes de continuar.
