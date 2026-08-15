# Codex: Guia Transversal de Tradução

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Orientações gerais para tradução de documentação técnica

## Conteúdo

### Como Identificar Idioma-Fonte e Idioma-Alvo

1. **Idioma-fonte:** determinado pelo caminho do arquivo. O primeiro segmento após `framework/` indica o idioma (ex: `framework/pt-BR/...` → fonte é pt-BR).
2. **Idioma-alvo:** definido pelo parâmetro da solicitação ou por `language.i18n` no `.ahrena/.directives`.
3. **Idioma padrão:** definido em `language.default` — é a fonte da verdade quando há divergência.

### Preservação de Estrutura Markdown

Ao traduzir, preservar rigorosamente:

| Elemento | Ação |
|----------|------|
| Headings (`#`, `##`, `###`) | Traduzir o texto, manter a hierarquia |
| Tabelas | Traduzir conteúdo das células, manter estrutura |
| Listas (ordenadas e não-ordenadas) | Traduzir itens, manter ordem |
| Blocos de código (`` ``` ``) | **Nunca** traduzir conteúdo |
| Blockquotes (`>`) | Traduzir texto, manter formatação |
| Links e URLs | **Nunca** alterar URLs. Traduzir texto do link se necessário |
| Imagens | **Nunca** alterar caminhos. Traduzir alt text se existir |
| Frontmatter YAML | **Nunca** traduzir chaves. Traduzir valores de `description` |

### Glossário de Termos Intraduzíveis

Estes termos **NUNCA** são traduzidos, em nenhuma circunstância:

**Termos do Ahrena:**
- Lexis, Codex, Katas, Warriors, Cries
- Ahrena, Clade, Subclade, Pilar
- Nomes de Warriors (Hermes, etc.)

**Termos técnicos universais:**
- commit, merge, branch, pull request, push, pull
- deploy, rollback, hotfix
- framework, middleware, API, SDK, CLI
- Markdown, YAML, JSON, HTML, CSS

### Exemplos de Boas e Más Traduções

#### Boa tradução (pt-BR → en)

**Original (pt-BR):**
> O agente **DEVE** ler o `.ahrena/.directives` antes de iniciar qualquer atividade.

**Tradução (en):**
> The agent **MUST** read `.ahrena/.directives` before starting any activity.

- Sentido preservado
- Força do modal mantida (DEVE → MUST)
- Caminho do arquivo preservado

#### Má tradução (pt-BR → en)

**Original (pt-BR):**
> O agente **DEVE** ler o `.ahrena/.directives` antes de iniciar qualquer atividade.

**Tradução (en):**
> The agent should check the Ahrena directives file before it begins.

- "DEVE" (obrigatório) rebaixado para "should" (recomendação)
- Caminho `.ahrena/.directives` substituído por texto genérico
- Perda de precisão técnica

### Fluxo de Consulta por Tradução

Para cada tradução, o agente deve consultar na seguinte ordem:

1. `lex-language` — regras transversais obrigatórias
2. `lex-language-{lang}` — regras do idioma-alvo
3. `codex-language` — este guia transversal
4. `codex-language-{lang}` — guia específico do idioma-alvo
