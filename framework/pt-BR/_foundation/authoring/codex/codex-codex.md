# Codex: Como Escrever Bons Codex

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação de Codex (manuais de referência)

## Visão Geral

Este Codex documenta como estruturar bases de conhecimento eficazes no Ahrena. Aborda como organizar informação de domínio, o que incluir e excluir, e como manter um Codex atualizado ao longo do tempo. É consultado pelo `kata-create-codex` durante a criação de novos Codex.

## Contexto

- **Domínio:** Design de bases de conhecimento estruturadas para agentes de IA
- **Público-alvo:** Agentes de IA executando `kata-create-codex` e mantenedores do framework
- **Atualização:** Quando novos padrões de qualidade forem identificados para Codex

## Conteúdo

### Princípios

1. **Consulta, não leitura:** Um Codex é desenhado para consulta pontual, não para leitura sequencial. Cada seção deve funcionar de forma independente.
2. **Decisão, não informação:** O valor de um Codex está em ajudar o agente a tomar decisões, não em acumular informação. Cada seção deve responder "o que fazer quando...".
3. **Atualidade:** Um Codex desatualizado é pior que nenhum Codex. Cada Codex deve incluir critérios claros de quando precisa ser atualizado.
4. **Escopo delimitado:** Um Codex cobre um domínio. Se o escopo cresce demais, divida em Codex separados.

### Anatomia de um Bom Codex

| Seção | Propósito | Critério de Qualidade |
|-------|-----------|----------------------|
| **Visão Geral** | Orienta se este é o Codex certo a consultar | Uma frase que delimita o escopo |
| **Contexto** | Domínio, público e frequência de atualização | Específico e verificável |
| **Princípios** | Fundamentos que guiam decisões | Princípios acionáveis, não platitudes |
| **Padrões e Convenções** | Regras práticas com exemplos | Tabela com aspecto, padrão e exemplo |
| **Decisões Vigentes** | Estado atual das escolhas técnicas | Rastreável (ADR, data, status) |
| **Restrições Técnicas** | Limites que não devem ser ultrapassados | Concretas e justificadas |
| **Glossário** | Termos do domínio | Definições no contexto deste Codex |

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Granularidade | Um domínio por Codex | `codex-api-patterns` (não `codex-tudo-sobre-backend`) |
| Tom | Técnico e direto | Evitar explicações longas; preferir tabelas e listas |
| Exemplos | Concretos e do projeto | Código real, não pseudocódigo genérico |
| Referências cruzadas | Citar outros artefatos pelo identificador | "Consulte `codex-architecture`" |
| Atualização | Incluir gatilho de atualização no Contexto | "Atualização: a cada ADR aprovado" |

### Armadilhas Comuns

| Armadilha | Problema | Solução |
|-----------|----------|---------|
| Codex enciclopédico | Cobre tudo, consulta impossível | Dividir em Codex menores por domínio |
| Codex narrativo | Escrito como artigo, não como referência | Reestruturar em tabelas, listas e seções independentes |
| Codex estático | Nunca atualizado após criação | Definir gatilho de atualização no Contexto |
| Codex duplicado | Repete informação de outro Codex | Referenciar o outro Codex em vez de duplicar |
| Codex opinativo sem justificativa | "Use X porque é melhor" | Incluir trade-offs e justificativa técnica |

### Codex vs Outros Pilares

| Situação | Pilar correto | Por quê |
|----------|---------------|---------|
| "Nunca faça X" | **Lexis** | Restrição absoluta, não recomendação |
| "Quando fizer X, considere Y e Z" | **Codex** | Conhecimento de domínio para decisão |
| "Para fazer X, siga estes passos" | **Kata** | Procedimento, não conhecimento |
| "Faça X rapidamente" | **Cry** | Atalho, não referência |

### Restrições Técnicas

- A seção "Visão Geral" deve descrever o escopo em no máximo dois parágrafos
- A seção "Contexto" deve incluir "Atualização" com gatilho concreto
- Tabelas são preferíveis a parágrafos longos para informação estruturada
- O nome do arquivo deve seguir o padrão `codex-{nome-descritivo}.md`

## Glossário

| Termo | Definição |
|-------|-----------|
| Domínio | Área de conhecimento delimitada que um Codex cobre |
| Consulta pontual | Acesso a uma seção específica para responder uma dúvida |
| Referência cruzada | Citação a outro artefato do framework pelo seu identificador |
| Gatilho de atualização | Evento que indica que o Codex precisa ser revisado |

## Referências

- `codex-pilars` — Visão geral do sistema de Pilares
- `lex-template-usage` — Lei de uso obrigatório de templates
- `kata-create-codex` — Procedimento para criar novos Codex
- `templates/codex-sample.md` — Template oficial de Codex
