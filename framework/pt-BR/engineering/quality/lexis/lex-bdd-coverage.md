# Lexis: Cobertura BDD por Mapeamento de Testes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Relação de cobertura entre cenários BDD na issue do GitHub e a suite de testes

## Propósito

Quando cenários BDD são redigidos para uma feature, eles passam a ser a declaração canônica da intenção de negócio. Essa declaração não vale nada se a suite de testes não se conecta a ela. Sem um mapeamento aplicável, cenários decaem para documentação obsoleta enquanto os testes evoluem em outra direção.

Esta Lexis define o mapeamento (cenários são referenciados pelo seu slug a partir do próprio código de teste), proíbe drift em qualquer direção (cenários sem cobertura, marcadores órfãos) e mantém-se neutra quanto ao nível de teste (qualquer nível pode cobrir um cenário, regido por `lex-test-pyramid` e `codex-test-strategy`).

## Lei

> **Todo cenário BDD de negócio publicado na issue do GitHub (no bloco `bdd:scenarios`) DEVE ser coberto por pelo menos um teste de qualquer nível (unit, integração, E2E). O mapeamento DEVE ser detectável a partir do próprio teste, via marcador canônico `@bdd_scenario` (decorador Python, tag JSDoc/JS-TS, comentário Go) carregando o slug do cenário, ou via fallback (`BDD: <título-ou-slug>` no nome ou docstring do teste). O framework NÃO obriga o uso de um runner Gherkin — cenários permanecem documentação, testes permanecem o artefato executável. Cenários sem teste de cobertura são gaps; marcadores apontando para cenários ausentes da issue são drift; ambos são violações.**

## Abrangência

- **Aplica-se a:** features que tenham cenários BDD redigidos via `/cry-bdd-create-scenarios` (ou de outra forma presentes na issue dentro dos marcadores `bdd:scenarios`).
- **Agentes vinculados:** `warrior-hera`, `kata-bdd-validate-scenarios`, revisores de código.
- **Exceções:** features sem cenários BDD permanecem regidas pelas suas próprias regras de qualidade (rastreabilidade AC↔teste do Issue-Driven, Gate 2). Esta Lexis fica dormente para elas.

## Regras

### 1. Um cenário, ao menos um teste de cobertura

Para cada `Scenario: <título>` no corpo da issue, ao menos um teste o referencia explicitamente.

### 2. O mapeamento é detectável a partir do teste

Mecânica do mapeamento, em ordem de preferência:

| Stack | Marcador canônico | Fallback |
|---|---|---|
| Python (pytest) | decorador `@bdd_scenario("scenario-slug")` na função de teste | docstring contém `BDD: <título-do-cenário>` |
| JS/TS (Jest, Vitest) | tag JSDoc `// @bdd_scenario scenario-slug` imediatamente acima do teste, ou wrapper `bddScenario("scenario-slug", () => { ... })` | nome do teste contém `BDD: <título-do-cenário>` |
| Go | comentário `// bdd_scenario: scenario-slug` imediatamente acima de `func TestXxx` | nome da função contém o slug em CamelCase |
| Outros | nome do teste ou docstring que casa com `BDD:\s*<título-ou-slug>` | — |

`<scenario-slug>` é a derivação em kebab-case de `Scenario: <título>` (lowercase, não-alfanuméricos substituídos por `-`, `-` repetidos colapsados, `-` final removido). Exemplo: `Customer requests a refund` → `customer-requests-a-refund`.

O identificador `bdd_scenario` é o token canônico entre stacks. O framework não distribui o decorador Python nem o wrapper JS/TS; projetos que adotam BDD definem um helper local fino (`bdd_scenario` / `bddScenario`) para que o marcador seja estável em grep. A kata de validação reconhece o token canônico independentemente da implementação subjacente, desde que ele carregue o slug do cenário.

### 3. O nível de teste é aberto

O teste de cobertura PODE viver em qualquer nível (unit, integração, E2E). Cenários são agnósticos quanto ao nível. Decisões de nível seguem `lex-test-pyramid` e `codex-test-strategy`.

### 4. Nenhum runner Gherkin é exigido

O framework não exige nem recomenda um runner Gherkin (Behave, Cucumber, SpecFlow). Cenários são documentação; testes são o artefato executável. Projetos que optarem por adotar um runner PODEM fazê-lo, mas testes gerados pelo runner ainda assim devem expor o mapeamento conforme a Regra 2.

### 5. Integridade bidirecional

Um marcador de teste apontando para um cenário ausente da issue é drift. A causa é uma de: o cenário foi renomeado (renomeie o marcador), o cenário foi removido (remova o teste ou ajuste seu escopo), o cenário nunca existiu (corrija o teste). Drift é violação, não aviso.

### 6. Renomear é mudança quebrante para o mapeamento

Quando um cenário é renomeado na issue, o slug muda; os marcadores DEVEM ser atualizados na mesma mudança. Renomeação sem atualização do marcador produz drift na próxima execução de validação.

## Exemplos

### Correto

```python
# Issue body has: Scenario: Customer requests a refund for an eligible payment
@bdd_scenario("customer-requests-a-refund-for-an-eligible-payment")
def test_creates_pending_refund_and_audit_entry():
    """BDD: Customer requests a refund for an eligible payment."""
    ...
```

```typescript
// Issue body has: Scenario: Concurrent refunds deduplicate by idempotency key
// @bdd_scenario concurrent-refunds-deduplicate-by-idempotency-key
test("only one refund persists when two requests share an idempotency key", () => { ... });
```

### Incorreto

```python
# Cenário existe na issue mas nenhum teste o referencia (violação da Regra 1)
def test_creates_refund(): ...
```

```python
# Marcador referencia um cenário ausente da issue (violação da Regra 5)
@bdd_scenario("legacy-scenario-removed-2-sprints-ago")
def test_legacy(): ...
```

## Validação Automatizada

- **Ferramenta:** `kata-bdd-validate-scenarios` faz parsing do bloco `bdd:scenarios` da issue, escaneia a suite de testes em busca de marcadores canônicos e fallbacks por stack, e emite um relatório bidirecional de cobertura (covered, gaps, drift).
- **Momento:** sob demanda (`/cry-bdd-validate-scenarios <issue>`); recomendado na revisão de PR para qualquer feature com cenários BDD.
- **Métrica:** 100% dos cenários têm ≥1 teste de cobertura; 0 marcadores apontando para cenários ausentes da issue.
