# Cry: Validar Cobertura de Cenários BDD na Suite de Testes

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Independente — confirma que cada cenário BDD de negócio em uma issue do GitHub tem ao menos um teste de cobertura (via marcador canônico ou fallback)

## Descrição

Atalho independente para invocar `kata-bdd-validate-scenarios`. Lê o bloco `bdd:scenarios` de uma issue do GitHub, escaneia a suite de testes em busca de marcadores canônicos `@bdd_scenario` (e equivalentes por stack) mais padrões de fallback, e emite um relatório bidirecional de cobertura. Não executa testes, não modifica a issue nem qualquer arquivo-fonte. Independente do fluxo Issue-Driven.

## Uso

```
/cry-bdd-validate-scenarios <issue-number> [<owner>/<repo>]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `issue-number` | Sim | Issue contendo o bloco `bdd:scenarios` | `42` |
| `<owner>/<repo>` | Não | Padrão: repositório atual via git remote | `guardiafinance/ahrena` |

## Pré-requisitos

- `github` listado em `mcp.servers` em `.ahrena/.directives`
- Env: `GITHUB_PAT` (obrigatória)
- Issue existente com um bloco `bdd:scenarios` (caso contrário, a kata reporta "nothing to validate" e para)

## O Que o Comando Faz

1. Invoca `kata-bdd-validate-scenarios`.
2. A kata lê o corpo da issue e extrai os cenários com seus slugs.
3. A kata escaneia a working tree em busca dos marcadores canônicos `bdd_scenario` por stack (decorador Python `@bdd_scenario("slug")`, tag JSDoc `// @bdd_scenario slug` ou wrapper `bddScenario("slug", ...)` em JS/TS, comentário `// bdd_scenario: slug` em Go) e padrões de fallback (`BDD: <título-ou-slug>` no nome ou docstring do teste).
4. A kata emite um relatório de cobertura listando cenários cobertos, gaps e drift, com evidência concreta de arquivo/linha e uma recomendação por achado.

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Run kata-bdd-validate-scenarios for issue #{{issue-number}}. Read the bdd:scenarios block from the issue body. Scan the test suite for canonical `bdd_scenario` markers per stack (`@bdd_scenario("slug")` in Python, `// @bdd_scenario slug` or `bddScenario(...)` in JS/TS, `// bdd_scenario: slug` in Go) and fallback patterns (`BDD: <title-or-slug>` in test name or docstring). Build the bidirectional map. Report `complete`, `gaps`, `drift`, or `gaps+drift` with concrete file/line evidence and a recommendation per finding.

Do not run tests. Do not modify any file. Do not infer scenarios from test code.

Strictly respect lex-bdd-coverage and lex-mcp.
```

## Exemplo de Invocação

**Entrada:**

```
/cry-bdd-validate-scenarios 42
```

**Saída esperada:**

```
BDD Coverage — Issue #42 — Result: gaps

Scenarios in issue: 3
Covered: 2 | Uncovered: 1 | Orphan markers: 0

| Scenario | Slug | Tests | Status |
|---|---|---|:-:|
| Customer requests a refund for an eligible payment | customer-requests-a-refund-for-an-eligible-payment | tests/refunds/test_create.py::test_pending_refund | ✅ |
| Customer cannot refund after 30 days | customer-cannot-refund-after-30-days | tests/refunds/test_eligibility.py::test_30d_window | ✅ |
| Concurrent refunds deduplicate by idempotency key | concurrent-refunds-deduplicate-by-idempotency-key | — | ❌ |

Recommendation:
- `concurrent-refunds-deduplicate-by-idempotency-key` is uncovered. Add a test (any level) marked `@bdd_scenario("concurrent-refunds-deduplicate-by-idempotency-key")` or with `BDD: Concurrent refunds deduplicate by idempotency key` in its docstring.
```

## Restrições

- **Read-only.** Não modifica a issue, os testes nem qualquer outro arquivo.
- **Não executa testes.** Esta é uma checagem estrutural de mapeamento, não comportamental.
- **Independente.** Não bloqueia nem modifica nenhum outro fluxo (Issue-Driven, Gate 2). Rode quando for útil.
- **Sem aprovações silenciosas.** Quando a issue não tem bloco `bdd:scenarios`, o comando diz isso explicitamente.

## Cry vs Kata

| Aspecto | Cry | Kata |
|---|---|---|
| Natureza | Invocação rápida pelo número da issue | Procedimento completo (parsear, escanear, classificar, reportar) |
| Complexidade | Baixa | Alta (8 passos incluindo escaneamento multi-stack) |

## Cries e Katas Associados

- `kata-bdd-validate-scenarios` — invocada por esta cry
- `cry-bdd-create-scenarios` — cry predecessora (redige cenários)
- `kata-quality-gate` — ortogonal; pode rodar junto com esta cry para um panorama mais completo de cobertura, mas não é acoplada

## Referências

- `lex-bdd-coverage` — lei de cobertura
- `codex-bdd` — metodologia e convenções de marcadores
- `kata-bdd-validate-scenarios` — procedimento
- `lex-test-pyramid`, `codex-test-strategy` — decisões de nível de teste para os testes de cobertura
