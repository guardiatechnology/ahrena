# Codex: Figma MCP Server

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Ferramentas e autenticação do servidor MCP do Figma para Cursor e Claude Code

## Visão Geral

Este Codex é a referência para usar o **servidor MCP do Figma** em projetos Ahrena. Define as ferramentas disponíveis, seus parâmetros principais, autenticação e casos de uso típicos: extrair tokens de design, ler specs de componentes, obter dimensões de frames para implementação.

## Contexto

- **Domínio:** Leitura de arquivos Figma via MCP — componentes, frames, variáveis (design tokens), estilos e metadados de nós.
- **Público-alvo:** Agentes IA que extraem especificações de design do Figma para implementação ou documentação em projetos Ahrena.
- **Atualização:** Quando novas ferramentas forem adicionadas ao servidor MCP do Figma ou quando a estrutura de variáveis/tokens mudar.

## Conteúdo

### Configuração por plataforma

**Cursor (`.cursor/mcp.json`):**
```json
"figma": {
  "command": "npx",
  "args": ["-y", "figma-developer-mcp", "--stdio"],
  "env": { "FIGMA_API_KEY": "${env:FIGMA_API_KEY}" }
}
```

**Claude Code (`.claude/settings.json`):**
```json
"figma": {
  "command": "npx",
  "args": ["-y", "figma-developer-mcp", "--stdio"],
  "env": { "FIGMA_API_KEY": "${FIGMA_API_KEY}" }
}
```

> A variável `FIGMA_API_KEY` deve estar definida no ambiente. Gere um Personal Access Token em Figma → Settings → Account → Personal access tokens. O token precisa de acesso de leitura ao arquivo alvo. Nunca hardcode tokens em arquivos rastreados (ver `lex-mcp`).

### Como obter o File ID do Figma

O File ID é a string alfanumérica na URL do arquivo Figma:
```
https://www.figma.com/file/{FILE_ID}/Nome-do-arquivo
```

O Node ID é o identificador de um frame, componente ou nó específico, visível ao inspecionar o elemento no Figma.

### Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `get_file` | Obtém o documento completo do arquivo Figma (estrutura de nós) |
| `get_node` | Obtém um nó específico pelo ID (frame, componente, grupo, etc.) |
| `get_component` | Obtém metadados de um componente pelo ID |
| `get_component_set` | Obtém um conjunto de variantes de componente |
| `get_team_components` | Lista componentes publicados de um time |
| `get_file_components` | Lista todos os componentes de um arquivo |
| `get_local_variables` | Obtém todas as variáveis locais do arquivo (design tokens) |
| `get_published_variables` | Obtém variáveis publicadas de uma biblioteca |
| `export_node` | Exporta um nó como imagem (PNG, SVG, PDF, JPEG) |
| `get_file_styles` | Obtém estilos definidos no arquivo (cores, tipografia, efeitos) |
| `get_comments` | Lista comentários de um arquivo |

### Parâmetros das ferramentas mais usadas

**`get_file`**
```
file_key      (string, obrigatório) — File ID do arquivo Figma
depth         (integer, opcional)   — profundidade da árvore de nós (default: profundidade total)
```

**`get_node`**
```
file_key      (string, obrigatório) — File ID do arquivo Figma
node_id       (string, obrigatório) — ID do nó (ex.: "1:23")
```

**`get_local_variables`**
```
file_key      (string, obrigatório) — File ID do arquivo Figma
```
Retorna: coleções de variáveis com tipos (`COLOR`, `FLOAT`, `STRING`, `BOOLEAN`), modos e valores.

**`export_node`**
```
file_key      (string, obrigatório) — File ID do arquivo Figma
node_id       (string, obrigatório) — ID do nó a exportar
format        (string, opcional)    — "PNG" | "SVG" | "PDF" | "JPEG" (default: "PNG")
scale         (float, opcional)     — escala do export (default: 1)
```

### Mapeamento de variáveis para tokens de design

O retorno de `get_local_variables` segue esta estrutura:
```json
{
  "variables": {
    "{variable_id}": {
      "name": "Color/Primary/500",
      "resolvedType": "COLOR",
      "valuesByMode": {
        "{mode_id}": { "r": 0.2, "g": 0.5, "b": 1.0, "a": 1.0 }
      }
    }
  },
  "variableCollections": {
    "{collection_id}": {
      "name": "Design Tokens",
      "modes": [{ "modeId": "{mode_id}", "name": "Light" }]
    }
  }
}
```

Converter `r/g/b` (0–1) para hex: `#RRGGBB` = `round(r*255)`, `round(g*255)`, `round(b*255)`.

### Casos de uso típicos

| Caso | Ferramentas |
|---|---|
| Extrair design tokens (cores, espaçamentos, tipografia) | `get_local_variables` |
| Ler spec de um componente específico | `get_component` ou `get_node` |
| Obter todas as variantes de um botão | `get_component_set` |
| Exportar ícone como SVG | `export_node` com `format="SVG"` |
| Inspecionar estrutura de um frame | `get_node` + `get_file` com `depth` limitado |
| Listar estilos de cor do arquivo | `get_file_styles` |

### Exemplo de uso: extrair tokens de cor

```
# 1. Obter variáveis do arquivo
vars = get_local_variables(file_key="ABC123XYZ")

# 2. Filtrar por tipo COLOR e coleção "Design Tokens"
# 3. Converter valores rgba para hex e gerar tokens.json:
{
  "color": {
    "primary": { "500": { "value": "#3380FF", "type": "color" } },
    "neutral": { "900": { "value": "#1A1A1A", "type": "color" } }
  }
}
# 4. Salvar em docs/design/tokens.json (ver kata-mcp-figma-extract)
```

## Referências

- `lex-mcp` — Leis de uso de ferramentas MCP
- `kata-mcp-figma-extract` — Kata para extração de tokens e specs do Figma
- [figma-developer-mcp — repositório do servidor](https://github.com/figma/figma-developer-mcp)
- [Figma API — Variables](https://www.figma.com/developers/api#variables)
