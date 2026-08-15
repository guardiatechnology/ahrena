# Lexis: Regras Transversais de Tradução

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Toda tradução de documentação técnica

## Lei

> **Toda tradução DEVE preservar a equivalência estrutural e semântica do documento original, respeitando as regras transversais definidas nesta Lexis E as regras específicas do idioma-alvo definidas em `lex-language-{lang}`.**

## Regras

### 1. Equivalência estrutural

A tradução **DEVE** manter exatamente a mesma estrutura do original:
- Mesmas seções e headings (traduzidos, mas na mesma ordem e hierarquia)
- Mesma formatação Markdown (tabelas, listas, blocos de código, blockquotes)
- Mesma quantidade de seções — nunca omitir, fundir ou reordenar

### 2. Fidelidade semântica

A tradução **DEVE** preservar o sentido original do texto. Não é paráfrase livre — é tradução técnica:
- O significado de cada frase deve ser equivalente ao original
- Nuances técnicas devem ser preservadas
- Instruções imperativos ("DEVE", "NÃO PODE") devem manter a mesma força no idioma-alvo

### 3. Preservação de elementos técnicos

Os seguintes elementos **NUNCA** devem ser traduzidos ou alterados:
- Blocos de código e seus conteúdos
- Caminhos de arquivo (ex: `framework/pt-BR/`, `.ahrena/.directives`)
- URLs e links
- Nomes de variáveis, funções e comandos
- Nomes de arquivos (ex: `lex-framework-language.md`)

### 4. Termos canônicos do Ahrena

Nomes próprios do framework **NUNCA** são traduzidos:
- **Lexis**, **Codex**, **Katas**, **Warriors**, **Cries**
- **Ahrena**, **Clade**, **Subclade**, **Pilar**
- Nomes de Warriors (ex: **Hermes**)

### 5. Hierarquia de regras

Para cada tradução, o agente **DEVE** consultar:
1. Esta `lex-language` (regras transversais — aplicam-se sempre)
2. `lex-language-{lang}` do idioma-alvo (regras específicas — complementam as transversais)
3. `codex-language` (guia transversal de referência)
4. `codex-language-{lang}` do idioma-alvo (guia específico)

Regras específicas do idioma **complementam** as transversais, mas **não as contradizem**.

### 6. Idioma-fonte agnóstico

O tradutor **NÃO** assume qual é o idioma-fonte. O idioma padrão é determinado por `language.default` no `.ahrena/.directives`. O tradutor sabe traduzir **para** idiomas, não **de** um idioma fixo.

### 7. Completude da tradução

Toda tradução **DEVE** ser completa. Não é permitido:
- Deixar trechos no idioma original
- Usar marcadores como "TODO: traduzir"
- Omitir seções por complexidade
