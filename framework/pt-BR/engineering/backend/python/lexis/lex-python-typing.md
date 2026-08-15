# Lexis: Segurança de Tipos Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: anotações de tipos em código Python

## Purpose

Garantir que todo o código Python no codebase tenha anotações de tipo completas e precisas, habilitando análise estática para detectar bugs antes do runtime, melhorando a legibilidade e servindo como documentação viva. Código sem tipos cria contratos ocultos que quebram silenciosamente e resistem ao refactoring seguro.

## Law

> **Todo o código Python DEVE ter type hints completos. mypy em modo strict DEVE passar com zero erros. Sem uso de `Any` sem justificativa explícita em um comentário.**

## Scope

- **Applies to:** todos os arquivos fonte Python (código de aplicação, testes, scripts, migrações excluídas).
- **Bound agents:** todos os agentes e implementadores que escrevem ou modificam código Python.
- **Exceptions:** stubs de bibliotecas de terceiros não disponíveis; devem ser documentados com `# type: ignore[<code>]` e um comentário de justificativa.

## Consequences of Violation

1. **Bugs silenciosos:** código sem tipos permite incompatibilidades de tipo que aparecem apenas em runtime, frequentemente em produção.
2. **Risco de refactoring:** sem tipos, renomear ou reestruturar não pode ser verificado estaticamente.
3. **Remediação:** código sem tipos deve ser anotado antes do merge; PRs com erros de mypy são bloqueados.

## Examples

### Correct

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    entity_id: UUID
    amount: int
    currency: str
    created_at: datetime


async def get_transaction(transaction_id: UUID) -> TransactionResponse | None:
    ...
```

### Incorrect

```python
# Tipo de retorno ausente, parâmetro sem tipo
async def get_transaction(transaction_id):
    ...

# Usando Any sem justificativa
from typing import Any
def process(data: Any) -> Any:
    ...
```

## Automated Validation

- **Tool:** mypy com o flag `--strict`; integrado em pre-commit hooks e pipeline CI.
- **When:** cada commit (pre-commit) e cada PR (CI).
- **Metric:** 0 erros de mypy em modo strict.

## References

- [mypy documentation — strict mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [PEP 604 — Union syntax X | Y](https://peps.python.org/pep-0604/)
- codex-python-tooling (engineering/backend)
