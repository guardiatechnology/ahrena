# Cry: Implementação de Feature Python

> **Prefix:** `cry-` | **Type:** Comando Recorrente | **Scope:** Atalho para implementar um feature Python conforme Lexis e Codex do backend

## Description

Este comando invoca o Warrior Apollo (ou o agente que assume seu papel) para implementar um feature Python: consultar Lexis e Codex do backend, projetar interfaces, implementar lógica de domínio com testes, construir adaptadores de infraestrutura e validar com a cadeia de qualidade completa.

## Usage

```
/cry-python-implement <descrição do feature> [contexto]
```

## Parameters

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `descrição do feature` | Sim | Descrição do feature, comportamento esperado e critérios de aceitação | "Adicionar endpoint para listar transações com paginação e filtro por status" |
| `contexto` | Não | Restrições, spec OAS relacionada, padrões existentes a seguir | "Seguir padrões existentes de transações. Spec OAS em docs/oas/transactions.yaml" |

## What the Command Does

1. Interpreta a descrição do feature e o contexto
2. Assume o papel do Warrior Apollo (Senior Python Engineer)
3. Executa **kata-python-implement** iterativamente:
   - Clarifica ambiguidades com o usuário
   - Identifica camadas afetadas (domínio, infraestrutura, HTTP)
   - Projeta interfaces e modelos de dados
   - Implementa lógica de domínio com testes unitários
   - Implementa infraestrutura com testes de integração
   - Implementa camada HTTP com testes de endpoint
4. Valida com Ruff, mypy e pytest antes de entregar

## Prompt Template

```
Context:
- Feature description: {{descrição do feature}}
- Additional context: {{contexto}}

Task:
Act as the Apollo Warrior (Senior Python Engineer) and execute **kata-python-implement**. Consult the applicable Lexis (lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability) and Codex (codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-observability, codex-python-tooling). Ask clarifying questions when needed. Implement the feature with tests at every layer. Validate with Ruff, mypy, and pytest before delivering.

Output:
- Implementation files in the appropriate layer directories
- Tests in tests/unit/, tests/integration/
- Alembic migration if schema changes are needed
- Brief summary of what was implemented and why
```

## Invocation Example

**Input:**

```
/cry-python-implement "Adicionar soft delete para transações: setar discarded_at, retornar 204, emitir evento de cancelação" "Seguir padrões existentes de transações. Entidade já tem coluna discarded_at."
```

**Expected output:**

Apollo implementa o feature iterativamente:
- Domain: caso de uso `cancel_transaction`, `TransactionCancelledEvent`
- Repository: método `soft_delete()`
- Route: `DELETE /v1/transactions/{entity_id}` → 204
- Tests: unitário (lógica de cancelação), integração (BD), HTTP (204, 404, 409)
- Ruff, mypy, pytest todos passam

## Constraints

- O Cry dispara a implementação — não projeta contratos de API (cry-api-design cuida disso)
- A descrição do feature deve ser suficiente para identificar o escopo; se vaga, Apollo pedirá esclarecimentos
- Exceções aos Lexis devem ser documentadas e justificadas

## Cry vs Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida com descrição do feature | Procedimento completo em 7 passos |
| **Complexidade** | Baixa (1 comando) | Alta (clarificar, projetar, implementar, testar, validar) |
| **Configura agente?** | Sim (assume o papel do Warrior Apollo) | Sim (define todos os passos de implementação) |
| **Exemplo** | "/cry-python-implement adicionar cancelamento de transação" | Executar kata-python-implement com entradas explícitas por passo |

## Associated Kata and Warrior

- **kata-python-implement** — Procedimento completo de implementação
- **warrior-apollo** — Senior Python Engineer; executa kata-python-implement

## References

- `kata-python-implement` — Procedimento executado pelo Warrior Apollo
- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-observability, codex-python-tooling (engineering/backend)
