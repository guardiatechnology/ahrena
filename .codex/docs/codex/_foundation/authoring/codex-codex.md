# Codex: Como Escrever Bons Codex

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação de Codex (manuais de referência)

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

- A seção **Visão Geral** deve descrever o escopo em no máximo dois parágrafos
- A seção **Contexto** deve incluir **Atualização** com gatilho concreto (quando o Codex precisa ser revisado)
- O **Conteúdo** deve incluir: Princípios, Padrões e Convenções, Decisões Vigentes (se aplicável), Restrições Técnicas
- Tabelas são preferíveis a parágrafos longos para informação estruturada
- O nome do arquivo deve usar o prefixo definido em `naming.prefixes.codex` (consultar `.ahrena/.directives`) e kebab-case: `{prefixo}-{nome-descritivo}.md`
- A estrutura deve seguir o template oficial: consultar `paths.samples.codex` em `.directives` (ex.: `templates/codex-sample.md`)
