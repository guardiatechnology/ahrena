# Kata: Sincronizar documentação para o Notion via MCP

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Sincronização de documentos do framework Ahrena para páginas ou databases do Notion via servidor MCP

## Objetivo

Sincronizar documentos do framework Ahrena (Lexis, Codex, Katas, Warriors, Cries) para o Notion via servidor MCP, criando novas páginas para documentos ausentes e atualizando páginas existentes para documentos modificados. O resultado é um espelho navegável da documentação do framework no Notion.

## Quando Usar

- Quando o usuário solicita sincronização de documentação do framework para o Notion
- Após adicionar ou atualizar artefatos significativos no framework
- Quando uma nova clade ou subclade é criada e precisa ser documentada no Notion

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Página ou database de destino no Notion | Sim | ID ou URL da página/database raiz no Notion onde os documentos serão criados |
| Escopo | Não | Clade ou subclade específico (ex.: `engineering/platform`); padrão: todos |
| Idioma | Não | Idioma dos documentos a sincronizar; padrão: `language.default` em `.ahrena/.directives` |

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições MCP e directives
- [ ] 2. Determinar escopo e coletar documentos
- [ ] 3. Localizar destino no Notion
- [ ] 4. Para cada documento: criar ou atualizar página
- [ ] 5. Reportar resultado
```

### Passo 1: Verificar pré-condições MCP e directives

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Verificar que `notion` está listado em `mcp.servers` (conforme `lex-mcp`). Se não estiver, informar ao usuário e encerrar.
3. Confirmar que a variável de ambiente `NOTION_API_KEY` está definida. Se não estiver, informar ao usuário qual variável configurar e encerrar.
4. Consultar `codex-mcp-notion` para identificar as ferramentas e parâmetros corretos.

### Passo 2: Determinar escopo e coletar documentos

1. Identificar o idioma: ler `language.default` de `.ahrena/.directives`.
2. Determinar o diretório de origem: `.ahrena/framework/{lang}/{escopo}/` (ou `.ahrena/framework/{lang}/` para todos).
3. Listar recursivamente os arquivos `.md` com prefixo de Pilar (`lex-`, `codex-`, `kata-`, `warrior-`, `cry-`).
4. Para cada arquivo, registrar: caminho relativo, título (primeira linha H1), tipo de Pilar, data de modificação.

### Passo 3: Localizar destino no Notion

1. Usar `search` do Notion MCP para verificar se a página ou database de destino existe e é acessível.
2. Se o destino for um database, confirmar que tem uma propriedade `title` para o nome da página.
3. Se o destino não for encontrado ou não for acessível, informar ao usuário e encerrar.

### Passo 4: Para cada documento — criar ou atualizar página

Para cada documento coletado no Passo 2:

1. Usar `search` com o título do documento para verificar se já existe uma página correspondente no Notion.
2. **Se não existir:** usar `create_page` com o título e conteúdo inicial. Converter o Markdown para blocos Notion (parágrafos, headings, code blocks, listas).
3. **Se já existir:**
   - Comparar a data de modificação do arquivo com `last_edited_time` da página Notion.
   - Se o arquivo for mais recente: usar `append_block_children` para adicionar uma seção com o conteúdo atualizado e registrar data de sincronização.
   - Se a página Notion for mais recente: **não sobrescrever**. Registrar como conflito e informar ao usuário.
4. Registrar o resultado de cada documento (criado, atualizado, conflito, ignorado).

### Passo 5: Reportar resultado

1. Apresentar resumo: total de documentos processados, criados, atualizados, conflitos (páginas mais novas no Notion), ignorados.
2. Listar os conflitos identificados com nome e URL da página Notion, para que o usuário decida a ação.
3. Em caso de falha parcial, listar quais documentos falharam e o motivo.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Páginas criadas | Páginas Notion com conteúdo do documento | Notion — parent especificado |
| Páginas atualizadas | Blocos adicionados à página Notion existente | Notion — página existente |
| Relatório de sincronização | Texto estruturado (criados, atualizados, conflitos, ignorados) | Resposta ao usuário |

## Restrições

- **Não sobrescrever páginas mais novas:** se a página Notion foi editada após a última modificação do arquivo, registrar como conflito e aguardar decisão do usuário.
- **Usar apenas MCP:** nunca usar a API REST do Notion diretamente; sempre usar ferramentas do servidor MCP (conforme `lex-mcp`).
- **Sem credenciais hardcoded:** autenticação exclusivamente via variável de ambiente `NOTION_API_KEY`.
- **Respeitar o escopo declarado:** não sincronizar clades ou subclades fora do escopo especificado pelo usuário.

## Referências

- `lex-mcp` — Leis de uso de ferramentas MCP
- `codex-mcp-notion` — Referência de ferramentas e parâmetros do Notion MCP
- `lex-directives` — Como ler `.ahrena/.directives`
