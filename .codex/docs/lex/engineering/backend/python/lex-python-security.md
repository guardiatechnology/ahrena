# Lexis: Práticas de Segurança Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: padrões de segurança para código Python

## Law

> **Nenhum segredo DEVE estar hardcoded no código fonte. Toda entrada externa DEVE ser validada nas fronteiras do sistema usando modelos Pydantic. As dependências DEVEM ser auditadas por vulnerabilidades conhecidas antes da adoção e periodicamente depois. Queries SQL DEVEM usar instruções parametrizadas — nunca interpolação de strings.**

## Examples

### Correct

```python
import os
from pydantic import BaseModel, Field

# Segredos do ambiente
DATABASE_URL = os.environ["DATABASE_URL"]

# Validação de entrada na fronteira
class CreateTransferRequest(BaseModel):
    amount: int = Field(gt=0, le=999_999_999)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    recipient_id: str = Field(min_length=1, max_length=36)

# Query parametrizada
stmt = select(Transaction).where(Transaction.entity_id == transaction_id)
```

### Incorrect

```python
# Segredo hardcoded
API_KEY = "sk-live-abc123secret"

# Entrada não validada passada para query
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"  # Injeção SQL
    ...

# Interpolação de strings no SQLAlchemy
stmt = text(f"SELECT * FROM transactions WHERE status = '{status}'")
```

## Automated Validation

- **Tool:** Regras de segurança do Ruff (subconjunto S); pip-audit ou safety para varredura de dependências; pre-commit hooks.
- **When:** cada commit (pre-commit) e cada PR (pipeline CI com auditoria de dependências).
- **Metric:** 0 segredos hardcoded detectados; 0 vulnerabilidades conhecidas em dependências; 0 vetores de injeção SQL.
