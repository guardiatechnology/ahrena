# Codex: Guia para Traduzir para Inglês

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Convenções e orientações para tradução técnica para inglês (en)

## Visão Geral

Este Codex é o guia prático para traduzir documentação técnica **para Inglês (en)**. Complementa a `lex-language-en` (regras obrigatórias) com orientações, exemplos e tabelas de referência.

## Contexto

- **Domínio:** Tradução técnica para inglês
- **Público-alvo:** `warrior-translator` e agentes que traduzam para inglês
- **Atualização:** sempre que novas convenções para inglês forem identificadas

## Conteúdo

### Convenções de Technical Writing em Inglês

1. **Imperative mood** para instruções: "Run the command", "Create the file"
2. **Active voice** sempre que possível: "The agent reads" não "The file is read by the agent"
3. **Present tense** como padrão: "The system validates" não "The system will validate"
4. **One idea per sentence** — frases curtas e focadas

### Escolhas de Vocabulário

| Preferir | Evitar | Motivo |
|----------|--------|--------|
| simple words | complex synonyms | Clareza |
| specific terms | vague language | Precisão |
| "Run X" | "You should run X" | Concisão |
| "Create the file" | "The file needs to be created" | Voz ativa |
| "do not" | "don't" | Formalidade |
| "cannot" | "can't" | Formalidade |

### Padrões de Formatação

| Padrão | Exemplo correto | Exemplo incorreto |
|--------|-----------------|-------------------|
| Instruções | "Run `npm install`." | "You should run `npm install`." |
| Obrigações | "The agent **MUST** validate." | "The agent has to validate." |
| Condições | "If the file exists, read it." | "In the event that the file exists, you should proceed to read it." |
| Listas | Parallelism em items | Estilos mistos |

### Armadilhas Comuns ao Traduzir de pt-BR

| Erro | Correção | Exemplo |
|------|----------|---------|
| "realize" (≠ realizar) | "perform", "carry out" | "Perform the task" não "Realize the task" |
| "actually" (≠ atualmente) | "currently" | "Currently active" não "Actually active" |
| "pretend" (≠ pretender) | "intend" | "Intend to create" não "Pretend to create" |
| "resume" (≠ resumir) | "summarize" | "Summarize the results" não "Resume the results" |
| "assist" (≠ assistir) | "attend", "watch" | "Watch the presentation" não "Assist the presentation" |
| "fabric" (≠ fábrica) | "factory" | "The factory produces..." não "The fabric produces..." |
| Excessive "the" | Omit when generic | "Agents must read directives" não "The agents must read the directives" |

### Armadilhas Comuns ao Traduzir de es

| Erro | Correção | Exemplo |
|------|----------|---------|
| "sensible" (≠ sensible) | "sensitive" | "Sensitive data" não "Sensible data" |
| "actual" (≠ actual) | "current" | "Current version" não "Actual version" |
| "eventual" (≠ eventual) | "possible", "occasional" | "A possible error" não "An eventual error" |

## Referências

- `lex-language-en` — Regras obrigatórias (este Codex complementa)
- `lex-language` — Regras transversais
- `codex-language` — Guia transversal de tradução
