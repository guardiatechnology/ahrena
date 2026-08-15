# Lexis: Segurança de Tipos Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: anotações de tipos em código Python

## Law

> **Todo o código Python DEVE ter type hints completos. mypy em modo strict DEVE passar com zero erros. Sem uso de `Any` sem justificativa explícita em um comentário.**

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
