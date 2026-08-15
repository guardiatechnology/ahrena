# Lexis: Imutabilidade por Padrão em Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: mutabilidade de estruturas de dados em código Python

## Law

> **Dataclasses DEVEM usar `frozen=True` por padrão. Modelos Pydantic são imutáveis por padrão (`model_config = ConfigDict(frozen=True)`) a menos que a mutação seja explicitamente necessária e justificada. Argumentos de função NÃO DEVEM ser mutados. Argumentos mutáveis padrão são PROIBIDOS.**

## Examples

### Correct

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: "Money") -> "Money":
        assert self.currency == other.currency
        return Money(amount=self.amount + other.amount, currency=self.currency)

# Modelo Pydantic — imutável por padrão
from pydantic import BaseModel, ConfigDict

class TransferResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    entity_id: str
    amount: int
    status: str
```

### Incorrect

```python
# Dataclass mutável sem justificativa
@dataclass
class Money:
    amount: int
    currency: str

# Argumento mutável padrão
def process_items(items: list[str] = []):  # BUG: padrão mutável compartilhado
    items.append("new")
    return items

# Mutando argumento de função
def enrich(transaction: Transaction) -> Transaction:
    transaction.metadata["enriched"] = True  # muta o objeto do caller
    return transaction
```

## Automated Validation

- **Tool:** Regras Ruff (B006 mutable default argument); revisão de código para frozen dataclasses.
- **When:** cada commit (pre-commit) e cada PR (CI).
- **Metric:** 0 argumentos mutáveis padrão; todos os dataclasses de domínio usam `frozen=True`.
