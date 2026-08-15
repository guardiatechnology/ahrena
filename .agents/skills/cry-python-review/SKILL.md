---
name: cry-python-review
description: "Revisão de Código Python. Atalho para revisar código Python conforme Lexis e Codex do backend"
---

# Cry: Revisão de Código Python

> **Prefix:** `cry-` | **Type:** Comando Recorrente | **Scope:** Atalho para revisar código Python conforme Lexis e Codex do backend

## Usage

```
/cry-python-review <alvo> [contexto]
```

## Parameters

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `alvo` | Sim | O que revisar: caminhos de arquivos, diff, número do PR ou "last commit" | "src/transactions/", "PR #42", "last commit" |
| `contexto` | Não | Sobre o que é a mudança, issue ou spec relacionada | "Implementa cancelamento de transação conforme issue #15" |

## What the Command Does

1. Lê o código ou diff alvo
2. Assume o papel do Warrior Apollo (Senior Python Engineer)
3. Executa **kata-python-review** sistematicamente:
   - Entende a intenção da mudança
   - Verifica corretude, tipos, testes, segurança, tratamento de erros, arquitetura
4. Entrega revisão estruturada: resumo, problemas críticos, sugestões, notas positivas

## Prompt Template

```
Context:
- Review target: {{alvo}}
- Additional context: {{contexto}}

Task:
Act as the Apollo Warrior (Senior Python Engineer) and execute **kata-python-review**. Review the code against all applicable Lexis (lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability) and Codex (codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing). Focus on correctness, security, and test coverage — not style (Ruff handles that).

Output format:
1. **Summary:** one-sentence assessment (approve / request changes / comment)
2. **Critical issues:** bugs, security vulnerabilities, missing tests (must fix)
3. **Suggestions:** improvements that would strengthen the code (optional)
4. **Positive notes:** what was done well
```

## Invocation Example

**Input:**

```
/cry-python-review "src/transactions/" "Novo feature de cancelamento de transação conforme issue #15"
```

**Expected output:**

Apollo revisa o código e entrega:

**Summary:** Solicitar mudanças — falta teste para condição de corrida em cancelamento concorrente.

**Critical:**
- `repository.soft_delete()` em `src/transactions/infrastructure/database/repositories/transaction_repo.py:45` não verifica `version` para bloqueio otimista — cancelamentos concorrentes poderiam corromper o estado (lex-python-error-handling)
- Sem teste para o caso de conflito 409 ao cancelar uma transação já cancelada (lex-python-testing)

**Suggestions:**
- Considerar adicionar um teste de propriedade Hypothesis para o invariante "uma transação cancelada não pode ser cancelada novamente" (codex-python-testing)

**Positive:**
- Separação limpa entre domínio e infraestrutura (codex-python-architecture)
- Modelo de response Pydantic com o padrão `from_domain()` está bem implementado

## Constraints

- O Cry dispara uma revisão — não implementa correções (cry-python-implement cuida disso)
- Focar em substância sobre estilo — Ruff cuida da formatação
- Não bloquear por sugestões não críticas

## Associated Kata and Warrior

- **kata-python-review** — Procedimento completo de revisão de código
- **warrior-apollo** — Senior Python Engineer; executa kata-python-review
