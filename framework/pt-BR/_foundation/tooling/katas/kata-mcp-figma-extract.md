# Kata: Extrair tokens de design e specs do Figma via MCP

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Extração de tokens de design (cores, espaçamentos, tipografia) e especificações de componentes de um arquivo Figma via servidor MCP

## Objetivo

Extrair tokens de design e especificações de componentes de um arquivo Figma via servidor MCP, gerando um arquivo `tokens.json` padronizado e documentação Markdown de specs de componentes. O resultado serve como contrato de design para implementação frontend.

## Quando Usar

- Quando um desenvolvedor precisa implementar um design Figma e solicita os tokens ou specs
- Quando tokens de design mudam no Figma e precisam ser atualizados no projeto
- Quando um novo componente é criado no Figma e precisa ser documentado para implementação

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| File ID do Figma | Sim | ID do arquivo Figma (parte da URL: `figma.com/file/{FILE_ID}/...`) |
| Modo de extração | Não | `tokens` (apenas design tokens), `specs` (apenas specs de componentes) ou `all` (padrão: `all`) |
| Node ID(s) | Não | IDs de frames ou componentes específicos a extrair (padrão: arquivo completo) |
| Destino | Não | Diretório de saída (padrão: `docs/design/`) |

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições MCP e directives
- [ ] 2. Identificar arquivo e escopo
- [ ] 3. Extrair tokens de design (se solicitado)
- [ ] 4. Extrair specs de componentes (se solicitado)
- [ ] 5. Gerar arquivos de saída
- [ ] 6. Reportar resultado
```

### Passo 1: Verificar pré-condições MCP e directives

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Verificar que `figma` está listado em `mcp.servers` (conforme `lex-mcp`). Se não estiver, informar ao usuário e encerrar.
3. Confirmar que a variável de ambiente `FIGMA_API_KEY` está definida. Se não estiver, informar ao usuário qual variável configurar e encerrar.
4. Consultar `codex-mcp-figma` para identificar as ferramentas e parâmetros corretos.

### Passo 2: Identificar arquivo e escopo

1. Confirmar o File ID com o usuário (solicitar se não fornecido).
2. Se Node IDs específicos forem fornecidos, verificar que existem no arquivo via `get_node`.
3. Definir o diretório de destino: `docs/design/` por padrão, ou o valor informado pelo usuário. Criar o diretório se não existir.

### Passo 3: Extrair tokens de design (se solicitado)

1. Chamar `get_local_variables(file_key="{FILE_ID}")` para obter todas as variáveis do arquivo.
2. Organizar as variáveis por tipo: `COLOR`, `FLOAT`, `STRING`, `BOOLEAN`.
3. Para variáveis do tipo `COLOR`: converter valores `r/g/b/a` (0–1) para hexadecimal (`#RRGGBB` ou `#RRGGBBAA`).
4. Mapear os nomes de variáveis para a estrutura de tokens (ex.: `Color/Primary/500` → `color.primary.500`): substituir `/` por `.` e converter para kebab-case.
5. Gerar o objeto JSON de tokens no formato:
   ```json
   {
     "color": { "primary": { "500": { "value": "#3380FF", "type": "color" } } },
     "spacing": { "4": { "value": "16", "type": "spacing" } }
   }
   ```

### Passo 4: Extrair specs de componentes (se solicitado)

1. Se Node IDs específicos foram fornecidos: chamar `get_node` para cada um.
2. Se não foram fornecidos: chamar `get_file_components(file_key="{FILE_ID}")` para listar todos os componentes.
3. Para cada componente relevante, extrair:
   - Nome, descrição (se disponível)
   - Dimensões (width, height)
   - Propriedades de variantes (se for um component set: chamar `get_component_set`)
   - Estilos aplicados (tipografia, cor, efeitos)
4. Estruturar as specs em Markdown com seções por componente.

### Passo 5: Gerar arquivos de saída

1. **Tokens:** salvar o JSON gerado em `{destino}/tokens.json`.
2. **Specs:** salvar o Markdown de especificações em `{destino}/components.md`.
3. Adicionar cabeçalho de metadados nos arquivos gerados:
   ```
   <!-- Gerado automaticamente por kata-mcp-figma-extract -->
   <!-- Arquivo Figma: {FILE_ID} | Data: {ISO-DATE} -->
   ```

### Passo 6: Reportar resultado

1. Apresentar resumo: tokens extraídos por tipo (cores, espaçamentos, tipografia), componentes documentados.
2. Listar os arquivos gerados com seus caminhos relativos.
3. Em caso de falha parcial, indicar quais extrações falharam e o motivo.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Design tokens | JSON (estrutura aninhada por tipo) | `docs/design/tokens.json` |
| Specs de componentes | Markdown | `docs/design/components.md` |
| Relatório de extração | Texto estruturado (tokens por tipo, componentes documentados) | Resposta ao usuário |

## Restrições

- **Usar apenas MCP:** nunca usar a API REST do Figma diretamente; sempre usar ferramentas do servidor MCP (conforme `lex-mcp`).
- **Sem credenciais hardcoded:** autenticação exclusivamente via variável de ambiente `FIGMA_API_KEY`.
- **Não modificar o Figma:** este Kata é read-only; nunca usar ferramentas de escrita no Figma.
- **Destino explícito:** sempre confirmar o diretório de destino com o usuário antes de sobrescrever arquivos existentes.

## Referências

- `lex-mcp` — Leis de uso de ferramentas MCP
- `codex-mcp-figma` — Referência de ferramentas e parâmetros do Figma MCP
- `lex-directives` — Como ler `.ahrena/.directives`
