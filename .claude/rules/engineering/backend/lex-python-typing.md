# Lexis: Python Type Safety

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: type annotations in Python code

## Law

> **All Python code MUST have complete type hints. mypy in strict mode MUST pass with zero errors. No use of `Any` without explicit justification in a comment.**

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
# Missing return type, untyped parameter
async def get_transaction(transaction_id):
    ...

# Using Any without justification
from typing import Any
def process(data: Any) -> Any:
    ...
```

## Automated Validation

- **Tool:** mypy with `--strict` flag; integrated in pre-commit hooks and CI pipeline.
- **When:** every commit (pre-commit) and every PR (CI).
- **Metric:** 0 mypy errors in strict mode.
