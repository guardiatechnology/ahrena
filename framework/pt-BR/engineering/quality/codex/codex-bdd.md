# Codex: Behavior-Driven Development na Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Metodologia de BDD usada em projetos Guardia — quando, por que e como cenários são redigidos a partir de fontes de negócio, mapeados a testes e mantidos ao longo do tempo

## Visão Geral

Este Codex é a referência operacional para **redação de cenários BDD e cobertura** na Guardia. Consultado por `warrior-hera` ao desenhar planos de teste, por agentes que executam `kata-bdd-create-scenarios` e `kata-bdd-validate-scenarios`, e por revisores de código que verificam se cenários e testes seguem alinhados.

BDD aqui é **opcional e independente**. Não é uma fase do fluxo Issue-Driven. Times o adotam em features cuja intenção de negócio se beneficia de ser capturada em linguagem de domínio antes do início da implementação. Quando adotado, `lex-bdd-scenarios` e `lex-bdd-coverage` se aplicam.

## Contexto

- **Domínio:** especificação de comportamento via cenários Gherkin derivados de fontes de negócio (issue + Notion), com mapeamento a testes em qualquer nível através de marcadores canônicos.
- **Público-alvo:** `warrior-hera`, agentes que redigem ou validam cenários, revisores de código.
- **Atualização:** quando o stack de testes muda (novo framework adotado), quando a convenção de marcador canônico evolui, quando um projeto opta por adotar um runner Gherkin (adendo no nível do projeto, não default do framework).

## Conteúdo

### Por que BDD aqui, por que independente

O fluxo Issue-Driven já obriga critérios de aceite numerados com rastreabilidade AC↔teste. BDD acrescenta uma **camada em linguagem de negócio** entre a issue e os testes. É útil quando a distância entre os ACs técnicos e a intenção de negócio é grande o suficiente para que cenários capturem a intenção com mais clareza do que ACs em Given/When/Then. Para a maior parte das issues, isso é overhead. Para features tier-1, regras de domínio complexas e processos regulados (pagamento, reembolso, ledger), compensa.

Independente, porque não bloqueia times que não usam. `/cry-bdd-create-scenarios` e `/cry-bdd-validate-scenarios` são pontos de entrada autônomos que rodam antes, depois ou totalmente fora do fluxo Issue-Driven.

### Foco em negócio vs foco em API/UI — a diferença

Os templates de contribuição `user-story-for-api.md` e `user-story-for-frontend.md` já carregam cenários Gherkin, mas esses cenários codificam o **contrato** (HTTP, superfície de UI). São úteis para teste de contrato e permanecem na issue. Cenários focados em negócio codificam a **intenção** por trás do contrato.

| Aspecto | Cenário API/UI (template) | Cenário de negócio (BDD) |
|---|---|---|
| Sujeito | A superfície API/UI | A operação de domínio |
| Vocabulário | Verbo/caminho HTTP, status code, campo de payload, seletor DOM | Ator, entidade, resultado de negócio |
| Público | Revisores de backend/frontend, integradores | Produto, especialistas de domínio, todo o time de engenharia |
| Estabilidade | Muda quando o contrato muda | Muda quando a regra de negócio muda |
| Alvo de teste | Teste de contrato (E2E API, E2E UI) | Qualquer nível, onde quer que a regra viva |

Ambas as formas coexistem. A cry duplica o cenário API/UI em forma de negócio; ela não o substitui.

### Convenções Gherkin usadas aqui

Use apenas `Scenario`, `Given`, `When`, `Then`, `And`. Não use `Background`, `Scenario Outline` ou tabelas `Examples` — incentivam drift técnico e mapeamentos mais difíceis. Um comportamento observável por cenário. Titule cada cenário com uma frase que o time de produto reconheceria.

```gherkin
Scenario: Customer requests a refund for an eligible payment
  Given a captured payment of 1000 BRL made by the customer in the last 30 days
  When the customer requests a refund for that payment
  Then a refund is recorded against the payment in pending state
  And the audit trail records the refund attempt with the requesting customer
```

Cenários vivem no corpo da issue, entre marcadores dedicados:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...

Scenario: ...
<!-- bdd:scenarios:end -->
```

Reexecuções da kata de redação substituem somente esse bloco, nunca qualquer outra parte do corpo.

### Fonte da verdade

| Fonte | Papel |
|---|---|
| Corpo da issue do GitHub (bloco `bdd:scenarios`) | O registro canônico e mutável. |
| Páginas do Notion | Contexto de enriquecimento (estratégia de produto, decisões anteriores). Não é onde os cenários vivem. |
| Código (services, tests, OAS) | Fonte proibida. Código reflete o que foi construído; cenários refletem o que se quer. |

### Convenções de mapeamento de testes (tabela completa)

`<scenario-slug>` é a forma kebab-case de `Scenario: <título>`. Exemplo: `Customer requests a refund for an eligible payment` → `customer-requests-a-refund-for-an-eligible-payment`.

| Stack | Marcador canônico | Fallback (nome do teste ou docstring) |
|---|---|---|
| Python / pytest | decorador `@bdd_scenario("scenario-slug")` | `BDD: <título>` na docstring |
| JS/TS (Jest, Vitest) | tag JSDoc `// @bdd_scenario scenario-slug` ou wrapper `bddScenario("scenario-slug", () => { ... })` | `BDD: <título>` no nome do teste |
| Go | `// bdd_scenario: scenario-slug` acima de `func TestXxx` | `BDD<Slug>` no nome da função |
| Genérico | docstring ou nome de teste que casa com `BDD:\s*<título-ou-slug>` | — |

Um teste PODE mapear para mais de um cenário quando legitimamente exercita múltiplos comportamentos ao mesmo tempo (raro; prefira um cenário por teste).

### O identificador `bdd_scenario`

`bdd_scenario` é o token canônico, estável em grep, entre os stacks. O framework não distribui o decorador Python nem o wrapper JS/TS. Projetos que adotam BDD definem um pequeno helper local para que o site de chamada permaneça limpo.

Helper de referência em Python:

```python
# project/tests/conftest.py (or a small bdd.py utility)
import pytest

def bdd_scenario(slug: str):
    """Mark a test as covering a BDD scenario by its kebab-case slug."""
    return pytest.mark.bdd_scenario(slug)
```

Helper de referência em JS/TS:

```typescript
// tests/_helpers/bdd.ts
export function bddScenario(slug: string, body: () => void): void {
  // The slug surfaces in test reporting via the test name and via the
  // `// @bdd_scenario <slug>` JSDoc tag; either is sufficient for the
  // validation kata to pick the mapping up.
  body();
}
```

A kata de validação reconhece o token canônico independentemente de como o helper é implementado, desde que o slug do cenário viaje junto.

### O que torna um cenário bom

| Propriedade | Detalhe |
|---|---|
| Comportamento único | Um trio Given/When/Then por cenário; múltiplas linhas `And` para contexto são aceitáveis, mas a asserção é única. |
| Resultado observável | `Then` descreve algo que um stakeholder consegue verificar (um registro existe, uma notificação foi enviada, um saldo mudou). Estado interno ("o cache foi invalidado") é detalhe de implementação e não pertence aqui. |
| Redação estável | Títulos de cenários são estáveis o suficiente para serem mapeados por slug. Renomear é mudança quebrante para a rastreabilidade (Regra 6 de `lex-bdd-coverage`). |
| Vocabulário de domínio | Um product manager entende cada palavra. Se entender exige ler a spec de API, reescreva. |

### Anti-patterns

| Anti-pattern | Por que é ruim |
|---|---|
| Copiar o cenário de API verbatim para o bloco de negócio | Esvazia o propósito; ambas as versões viram ruído. |
| Múltiplos resultados `Then` por cenário | O cenário vira checklist; testes de cobertura ficam desfocados; o mapeamento fica ambíguo. |
| Renomeações casuais de cenário | Quebram o mapeamento por slug. Renomeação = tratar como mudança quebrante de rastreabilidade e atualizar os marcadores na mesma mudança. |
| Redigir cenários a partir do código | Codifica o que o sistema faz, não o que o negócio quer. Esvazia totalmente o BDD. |
| Obrigar o uso de um runner Gherkin | Adiciona peso de ferramenta sem adicionar sinal. Testes são o artefato executável; o mapeamento é o contrato. |
| Asserções sobre estado interno | Cenários falam apenas de resultados observáveis externamente. Estado interno é escolha de implementação. |

### Ciclo de vida de um cenário

1. Redigido a partir da issue e do Notion (`/cry-bdd-create-scenarios`).
2. Persistido no corpo da issue dentro dos marcadores `bdd:scenarios`.
3. Mapeado pelo código de teste durante a implementação (marcador canônico adicionado).
4. Validado quanto à cobertura sob demanda (`/cry-bdd-validate-scenarios`) e na revisão de PR.
5. Quando a regra de negócio muda: reescreva o cenário na issue primeiro, depois atualize os testes de cobertura na mesma mudança. O mapeamento é um contrato; ambos os lados se movem juntos.

### Relação com o fluxo Issue-Driven

| Evento do fluxo | Interação com BDD |
|---|---|
| Fase 2 (`kata-requirements-brief`) produz ACs numerados | Cenários PODEM complementar os ACs; ambos podem coexistir na issue. |
| Fase 4 (implementação) | Testes carregam tanto marcadores `@ac("AC-N")` quanto `@bdd_scenario("...")` quando ambas as camadas existem. |
| Gate 2 (`kata-quality-gate`) | Valida o mapeamento AC↔teste. Cobertura BDD é checada separadamente por `kata-bdd-validate-scenarios`. |

As duas superfícies permanecem ortogonais. Uma não bloqueia a outra.

## Glossário

| Termo | Definição |
|---|---|
| Cenário BDD | Trio Gherkin Given/When/Then redigido em linguagem de negócio e persistido na issue do GitHub. |
| Slug do cenário | Derivação kebab-case do título do cenário, usada como chave canônica de mapeamento. |
| Marcador canônico | Anotação de teste específica do stack que referencia explicitamente um slug de cenário. |
| Marcador de fallback | Nome do teste ou docstring contendo `BDD: <título-ou-slug>`, aceito quando o marcador canônico não está disponível. |
| Bloco `bdd:scenarios` | A seção delimitada por marcadores HTML no corpo da issue que guarda os cenários de negócio. |
| Gap | Cenário na issue sem teste de cobertura. |
| Drift | Marcador de teste apontando para um cenário ausente da issue. |

## Referências

- `lex-bdd-scenarios` — lei de redação (fontes, linguagem, persistência)
- `lex-bdd-coverage` — lei de cobertura (mapeamento, drift, neutralidade de nível)
- `kata-bdd-create-scenarios`, `kata-bdd-validate-scenarios` — procedimentos
- `cry-bdd-create-scenarios`, `cry-bdd-validate-scenarios` — pontos de entrada
- `lex-test-pyramid`, `lex-test-isolation`, `codex-test-strategy` — decisões de nível de teste
- `framework/templates/contributing_templates/user-story-for-api.md`, `user-story-for-frontend.md` — origem dos cenários API/UI que são duplicados
