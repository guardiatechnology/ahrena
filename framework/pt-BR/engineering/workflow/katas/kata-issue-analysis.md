# Kata: Análise de Issue

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 1 do fluxo Issue-Driven — leitura da issue do GitHub e busca de contexto relacionado no Notion

## Objetivo

Ler uma issue do GitHub (título, descrição, comentários, labels, metadata) e buscar no Notion documentos de contexto relacionados (specs de produto, ADRs anteriores, regras de negócio), produzindo um brief estruturado em `.ahrena/issues/{n}/01-brief.md`. Este brief é a base para as fases subsequentes do fluxo Issue-Driven.

## Quando Usar

- Fase 1 do fluxo orquestrado por `warrior-athena` após invocação de `/cry-implement-issue`
- Sempre que for necessário consolidar o contexto de uma issue antes de iniciar design ou implementação

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Número da issue | Sim | Número da issue no GitHub (ex.: `42`) |
| Repositório | Sim | `owner/repo` (ex.: `guardiafinance/ahrena`) |
| Raiz Notion | Não | Página/database de contexto; padrão: `knowledge.notion.root_page` em `.ahrena/.directives` |

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições MCP e directives
- [ ] 2. Ler issue do GitHub
- [ ] 3. Buscar contexto relacionado no Notion
- [ ] 4. Consolidar e estruturar o brief
- [ ] 5. Persistir em .ahrena/issues/{n}/01-brief.md
- [ ] 6. Atualizar checkpoint de handoff
```

### Passo 1: Verificar pré-condições MCP e directives

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Confirmar que `github` está em `mcp.servers` (conforme `lex-mcp`). Se não, informar ao usuário e encerrar.
3. Confirmar que `notion` está em `mcp.servers`. Se não, continuar sem contexto Notion (informar ao usuário que o enriquecimento será pulado).
4. Confirmar `GITHUB_PAT` e `NOTION_API_KEY` (se aplicável) definidas no ambiente.

### Passo 2: Ler issue do GitHub

1. Invocar `kata-mcp-github-read` com:
   - objeto: `issues`
   - `owner/repo` e `issue_number` recebidos como input
2. Registrar: título, body, labels, assignees, autor, data de criação, estado, milestone.
3. Invocar `kata-mcp-github-read` novamente para listar comentários da issue (usar `get_issue` se já retorna comments; caso contrário buscar via API da issue).
4. Se a issue não existir ou estiver vazia, informar ao usuário e encerrar.

### Passo 3: Buscar contexto relacionado no Notion

Se `notion` está ativo:

1. Extrair termos-chave do título e body da issue (nomes próprios de features, entidades de domínio, áreas técnicas).
2. Invocar `kata-mcp-notion-read` em modo `search` para cada termo relevante (limite de 3-5 buscas para evitar custo excessivo).
3. Para cada resultado promissor, invocar `kata-mcp-notion-read` em modo `page` com profundidade `full` para obter o conteúdo.
4. Filtrar resultados irrelevantes (desatualizados, tangenciais). Se a `knowledge.notion.root_page` está configurada, priorizar resultados descendentes dessa página.
5. Registrar: título da página, URL, trecho relevante, relação com a issue.

### Passo 4: Consolidar e estruturar o brief

Produzir o brief seguindo a estrutura:

```markdown
# Brief — Issue #{n}: {título}

- **Repositório:** {owner/repo}
- **Autor:** @{autor}
- **Criada em:** {YYYY-MM-DD}
- **Labels:** {lista}
- **Assignees:** {lista}
- **Link:** {URL da issue}

## Problema

{resumo em 2-3 parágrafos do que a issue descreve — problema, motivação, sintomas}

## Contexto adicional

### Da issue (comentários relevantes)

- {comentário 1, autor, data}
- {comentário 2, autor, data}

### Do Notion

- **[{Título da página}]({URL}):** {trecho relevante, 1-3 linhas}
- **[{Título da página}]({URL}):** {trecho relevante, 1-3 linhas}

## Tipo de trabalho

{Feature | Bugfix | Refactor | Chore} — {breve justificativa}

## Riscos e desconhecidos identificados

- {Lista de pontos que requerem esclarecimento antes do design}

## Próxima fase

Fase 2: elicitação de requisitos (`kata-requirements-brief`).
```

### Passo 5: Persistir em `.ahrena/issues/{n}/01-brief.md`

1. Criar o diretório `.ahrena/issues/{n}/` se não existir.
2. Salvar o brief em `.ahrena/issues/{n}/01-brief.md`.
3. Se o arquivo já existir, comparar com o novo conteúdo: se divergente, apresentar diff ao usuário antes de sobrescrever.

### Passo 6: Atualizar checkpoint de handoff

1. Criar/atualizar `.ahrena/workflow/issue-{n}/checkpoint.md` com:
   - fase concluída: 1
   - próxima fase: 2
   - referência: `.ahrena/issues/{n}/01-brief.md`
   - timestamp
2. Informar ao `warrior-athena` (ou usuário) que a Fase 1 foi concluída.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Brief estruturado | Markdown | `.ahrena/issues/{n}/01-brief.md` |
| Checkpoint | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Resumo ao usuário | Texto estruturado | Resposta ao orquestrador |

## Restrições

- **Somente leitura no GitHub:** este kata não cria nem modifica issues, comentários ou labels (conforme `kata-mcp-github-read`).
- **Somente leitura no Notion:** este kata não cria nem modifica páginas (conforme `kata-mcp-notion-read`).
- **Sem inferência de escopo:** o kata consolida o que está na issue e no Notion; não adiciona informação não documentada. Desconhecidos vão para a seção "Riscos e desconhecidos".
- **Destino fixo:** o brief vai em `.ahrena/issues/{n}/01-brief.md`; nunca em outro caminho (conforme `lex-issue-driven`).

## Referências

- `lex-issue-driven` — leis do fluxo Issue-Driven
- `codex-issue-workflow` — estrutura completa do fluxo
- `kata-mcp-github-read` — leitura de issues via MCP
- `kata-mcp-notion-read` — leitura de conteúdo Notion via MCP
- `lex-mcp` — uso obrigatório de MCP
