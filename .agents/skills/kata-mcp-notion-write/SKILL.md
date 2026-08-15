---
name: kata-mcp-notion-write
description: "Escrever conteúdo no Notion via MCP. Criação e atualização de páginas, blocos e propriedades no Notion via servidor MCP"
---

# Kata: Escrever conteúdo no Notion via MCP

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação e atualização de páginas, blocos e propriedades no Notion via servidor MCP

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Verificar pré-condições e diretivas do MCP
- [ ] 2. Identificar operação e alvo
- [ ] 3. Verificar conteúdo existente (create / append)
- [ ] 4. Executar operação de escrita
- [ ] 5. Confirmar e retornar resultado
```

### Passo 1: Verificar Pré-condições e Diretivas do MCP

1. Consultar `.ahrena/.directives` conforme `lex-directives`
2. Verificar se `notion` está listado em `mcp.servers` conforme `lex-mcp`. Se não estiver, informar o usuário e parar
3. Confirmar que `NOTION_API_KEY` está definida no ambiente. Se não estiver, informar ao usuário qual variável configurar e parar
4. Consultar `codex-mcp-notion` para identificar as ferramentas e parâmetros corretos para a operação solicitada

### Passo 2: Identificar Operação e Alvo

1. Confirmar a operação: `create`, `append`, `update-props` ou `delete-block`
2. Se o alvo for uma URL, extrair o ID (últimos 32 caracteres da URL do Notion, formatados como UUID)
3. Se o alvo não foi fornecido:
   - Para `create`: perguntar ao usuário a página pai ou banco de dados onde a nova página deve ser criada
   - Para `append` e `update-props`: perguntar ao usuário o ID ou URL da página
   - Para `delete-block`: perguntar ao usuário o ID do bloco a excluir
4. Se o conteúdo não foi fornecido para `create` ou `append`, perguntar ao usuário o que escrever

### Passo 3: Verificar Conteúdo Existente (apenas create / append)

Para `create`:
1. Chamar `search(query="{título}", filter={"property": "object", "value": "page"})` para verificar se já existe uma página com o mesmo título no Notion
2. Aplicar tratamento de duplicatas:
   - `skip` — se uma página correspondente for encontrada, informar o usuário e parar; retornar a URL da página existente
   - `update` — se uma página correspondente for encontrada, mudar para o modo `append` usando o ID da página encontrada
   - `create-new` — prosseguir independentemente de páginas existentes

Para `append`:
1. Chamar `get_page(page_id="{id}")` para confirmar que a página existe e recuperar seu título atual
2. Se a página não existir, alertar o usuário e parar

Para `update-props` e `delete-block`: prosseguir diretamente para o Passo 4 (o alvo é explícito).

### Passo 4: Executar Operação de Escrita

**Operação `create`:**
1. Construir o objeto `properties` com o título da página:
   ```json
   {"title": [{"text": {"content": "{título}"}}]}
   ```
2. Construir o array `children` com os blocos de conteúdo iniciais (ver formatos de blocos em `codex-mcp-notion`)
3. Chamar `create_page(parent={...}, properties={...}, children=[...])`
4. Registrar o `id` e a `url` retornados da nova página

**Operação `append`:**
1. Construir o array `children` com os blocos a adicionar
2. Chamar `append_block_children(block_id="{page_id}", children=[...])`
3. Para conteúdos extensos (mais de 20 blocos), dividir em múltiplas chamadas `append_block_children` para respeitar os limites da API

**Operação `update-props`:**
1. Construir o objeto `properties` apenas com os campos a atualizar (não incluir propriedades inalteradas)
2. Chamar `update_page(page_id="{id}", properties={...})`

**Operação `delete-block`:**
1. **Confirmar com o usuário** antes de excluir — declarar claramente qual bloco será removido (incluir ID do bloco e qualquer texto visível se recuperável)
2. Após confirmação, chamar `delete_block(block_id="{id}")`

### Passo 5: Confirmar e Retornar Resultado

1. Reportar o resultado ao usuário:
   - `create`: "Página '{título}' criada em {url}"
   - `append`: "Conteúdo adicionado a '{título da página}' ({url})"
   - `update-props`: "Propriedades atualizadas em '{título da página}' ({url})"
   - `delete-block`: "Bloco {id} excluído de '{título da página}'"
2. Incluir a URL da página em toda confirmação para que o usuário possa navegar diretamente
3. Se a operação falhar, reportar o erro claramente e sugerir os próximos passos (verificar acesso, confirmar ID, verificar se a integração tem acesso à página ou banco de dados alvo)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Nova página | Página Notion | Página pai ou banco de dados especificado pelo usuário |
| Conteúdo adicionado | Blocos na página existente | Página especificada pelo usuário |
| Propriedades atualizadas | Campos da entrada do banco de dados | Página/entrada especificada pelo usuário |
| Confirmação | Texto com URL da página | Resposta ao usuário |

## Exemplo de Execução

### Exemplo — Criar uma página estruturada

```
Operação: create
Pai: https://notion.so/WIKI-PAGE-ID
Título: Event Storm — Módulo Plataforma
Conteúdo: heading "Transferências Agendadas", tabela de eventos com 5 eventos
Tratamento de duplicatas: skip
```

Passos executados:
1. `search(query="Event Storm — Módulo Plataforma", filter={"property": "object", "value": "page"})` — nenhuma página existente encontrada
2. `create_page(parent={"page_id": "WIKI-PAGE-ID"}, properties={title...}, children=[heading_2, table...])`
3. Resultado: "Página 'Event Storm — Módulo Plataforma' criada em https://notion.so/..."

### Exemplo — Adicionar conteúdo a página existente

```
Operação: append
Alvo: https://notion.so/EXISTING-PAGE-ID
Conteúdo: parágrafo "Atualizado em 26/04/2026 — evento cancelado adicionado"
```

Passos executados:
1. `get_page(page_id="EXISTING-PAGE-ID")` — página confirmada
2. `append_block_children(block_id="EXISTING-PAGE-ID", children=[paragraph...])`
3. Resultado: "Conteúdo adicionado a 'Event Storm — Módulo Plataforma' (https://notion.so/...)"

## Restrições

- **Usar apenas MCP:** nunca chamar a API REST do Notion diretamente; sempre usar ferramentas do servidor MCP conforme `lex-mcp`
- **Sem credenciais hardcoded:** autenticação exclusivamente via variável de ambiente `NOTION_API_KEY`
- **Verificar antes de criar:** sempre executar `search` para detectar duplicatas antes de `create`, a menos que `create-new` seja explicitamente definido
- **Confirmar antes de excluir:** sempre pedir confirmação ao usuário antes de executar `delete-block`
- **Não sobrescrever sem instrução:** `append` adiciona ao conteúdo existente; para substituir conteúdo, o usuário deve solicitar explicitamente a exclusão do bloco primeiro
- **Acesso da integração:** se o Notion retornar erro 403 ou "object not found", significa que a integração não recebeu acesso à página ou banco de dados alvo — instruir o usuário a compartilhá-lo com a integração no Notion
