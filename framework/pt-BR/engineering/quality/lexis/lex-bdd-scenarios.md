# Lexis: Cenários BDD Redigidos a partir de Fontes de Negócio

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Redação de cenários BDD para qualquer feature, antes da implementação

## Propósito

Behavior-Driven Development na Guardia é uma disciplina opcional e independente, usada quando a distância entre os critérios de aceite numerados e a intenção de negócio subjacente é grande o suficiente para merecer uma camada separada, em linguagem de negócio. Quando BDD é adotado para uma feature, a fonte da verdade dessa intenção precisa ser inequívoca — caso contrário os cenários começam a descrever o contrato ou o código, e deixam de descrever o negócio.

Esta Lexis fixa a fonte (issue + Notion), a linguagem (apenas domínio) e a persistência (o próprio corpo da issue) para que cada passo posterior (mapeamento de testes, validação, revisões) leia da mesma superfície canônica.

## Lei

> **Cenários BDD DEVEM ser redigidos antes do início da implementação, derivados exclusivamente da issue do GitHub e do Notion (as fontes de verdade do negócio), nunca do código-fonte existente, dos testes ou de diffs de implementação. Cenários DEVEM ser expressos em Gherkin (Given/When/Then) usando linguagem de negócio (atores de domínio, entidades de domínio, resultados de negócio observáveis), nunca linguagem técnica (verbos HTTP, status codes, formatos de payload, seletores de UI). Quando a issue já contém Gherkin focado em API ou em UI (típico dos templates `user-story-for-api` ou `user-story-for-frontend`), esses cenários DEVEM ser duplicados e reescritos em forma de negócio, mantendo os originais inalterados. Os cenários de negócio finais DEVEM ser persistidos de volta no corpo da issue do GitHub, dentro de uma seção delimitada pelos marcadores `<!-- bdd:scenarios:start -->` e `<!-- bdd:scenarios:end -->`.**

## Abrangência

- **Aplica-se a:** qualquer feature, bugfix ou mudança de comportamento para a qual BDD tenha sido adotado (tipicamente invocado via `/cry-bdd-create-scenarios`).
- **Agentes vinculados:** qualquer agente que produza cenários BDD; principalmente `warrior-hera` e `kata-bdd-create-scenarios`.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Regras

### 1. Fonte da verdade

Fontes permitidas para a redação de cenários:

- A issue do GitHub (título, corpo, comentários, labels, assignees).
- Páginas relacionadas no Notion (quando `notion` estiver em `mcp.servers`).

Fontes proibidas durante a redação:

- Código-fonte da aplicação, testes, fixtures, ADRs, specs OpenAPI derivadas da implementação, linhas de log.
- Diffs de pull request.
- Memória do engenheiro sobre "o que o código faz hoje".

O ponto é descrever o que o negócio quer, não o que o sistema casualmente já faz.

### 2. Apenas linguagem de negócio

Cada cenário descreve comportamento observável externamente em termos de domínio.

| Proibido em `Given`, `When`, `Then` | Substituir por |
|---|---|
| Verbos HTTP (`POST`, `GET`, `PUT`, `PATCH`, `DELETE`) | uma ação de domínio ("o cliente solicita um reembolso") |
| Caminhos HTTP (`/v1/refunds`) | a operação de domínio ("uma solicitação de reembolso") |
| Status codes (`201`, `409`, `422`) | o resultado de negócio ("o reembolso é registrado", "o reembolso é rejeitado") |
| Tokens de formato de payload (`{ "data": ... }`) | o efeito observável ("existe um registro de auditoria") |
| Seletores de UI (`.btn-submit`, `[data-testid=...]`) | a ação do usuário ("o operador aprova a liberação") |
| Nomes de framework (`fastapi`, `react`) | omitir |

### 3. Duplicar, nunca substituir

Quando a issue já contém Gherkin do `user-story-for-api` ou `user-story-for-frontend`, esses cenários são mantidos intactos (continuam úteis para validação de contrato). O agente duplica cada um em forma de negócio dentro do bloco dedicado `bdd:scenarios`. Ambas as representações convivem na issue.

### 4. Persistido no corpo da issue

Os cenários finais ficam dentro do corpo da issue, em um bloco delimitado:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...
  Given ...
  When ...
  Then ...
<!-- bdd:scenarios:end -->
```

O bloco é o registro canônico e mutável. O agente usa GitHub MCP `update_issue` (ou equivalente) para escrever ou atualizá-lo. Reexecutar a kata de redação substitui apenas esse bloco, nunca qualquer outra parte do corpo.

### 5. Redigidos antes da implementação

A cry/kata recusa execução se a working tree contiver mudanças de implementação não triviais contra a issue alvo, a menos que o usuário confirme explicitamente um backfill. A premissa padrão é BDD-first.

### 6. Sem regras inventadas

Se uma regra não está presente na issue ou no Notion, ela não entra como `Scenario:`. Regras pendentes são listadas em uma sub-seção `## Pending Questions` dentro do mesmo bloco `bdd:scenarios`, aguardando o usuário.

## Exemplos

### Correto

(Corpo da issue, antes)

```gherkin
Scenario: Successful refund creation
  When I send POST /v1/refunds with body { "payment_id": "p_1", "amount": 1000 }
  Then the API returns 201 with { "id": ..., "status": "pending" }
```

(Corpo da issue, depois de executar `/cry-bdd-create-scenarios`)

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: Customer requests a refund for an eligible payment
  Given a captured payment of 1000 BRL made by the customer in the last 30 days
  When the customer requests a refund for that payment
  Then a refund is recorded against the payment in pending state
  And the audit trail records the refund attempt with the requesting customer
<!-- bdd:scenarios:end -->
```

O cenário original focado em API permanece intocado acima do bloco.

### Incorreto

```gherkin
Scenario: Customer requests a refund
  When the customer sends POST /v1/refunds with payload { ... }
  Then the response is 201
  And the JSON contains "id" and "status"
```

O cenário usa verbos HTTP, status codes e formato de payload (violação da Regra 2).

```
(sem o bloco <!-- bdd:scenarios:start --> no corpo da issue)
```

O bloco está ausente (violação da Regra 4).

```
(cenários derivados a partir da leitura de service.py e test_refund.py)
```

Código foi usado como fonte (violação da Regra 1).

## Validação Automatizada

- **Ferramenta:** `kata-bdd-create-scenarios` aplica a restrição de fonte (apenas leituras via GitHub MCP e Notion MCP), executa um check de linguagem por tokens proibidos e grava o bloco via GitHub MCP somente após confirmação explícita do usuário. `kata-bdd-validate-scenarios` confirma a presença e o formato do bloco.
- **Momento:** na redação dos cenários (invocação da cry); na revisão de PR quando os cenários acompanham uma mudança.
- **Métrica:** 100% das features que usam BDD têm um bloco `bdd:scenarios` na issue; 0 cenários contendo tokens técnicos proibidos.
