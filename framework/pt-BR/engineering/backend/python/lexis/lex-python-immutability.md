# Lexis: Imutabilidade por Padrão em Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: mutabilidade de estruturas de dados em código Python

## Purpose

Garantir que as estruturas de dados sejam imutáveis por padrão, reduzindo efeitos colaterais não intencionais, condições de corrida e corrupção de estado. Estado mutável é a principal fonte de bugs sutis em sistemas concorrentes e assíncronos. Mutação deve ser uma decisão consciente e justificada — não o padrão.

## Law

> **Dataclasses DEVEM usar `frozen=True` por padrão. Modelos Pydantic são imutáveis por padrão (`model_config = ConfigDict(frozen=True)`) a menos que a mutação seja explicitamente necessária e justificada. Argumentos de função NÃO DEVEM ser mutados. Argumentos mutáveis padrão são PROIBIDOS.**

## Scope

- **Applies to:** todos os modelos de domínio Python, value objects, DTOs e estruturas de transferência de dados.
- **Bound agents:** todos os agentes e implementadores que definem estruturas de dados.
- **Exceptions:** modelos ORM (classes mapeadas pelo SQLAlchemy) e padrões builder onde a mutação é inerente ao padrão; devem ser confinados à camada de infraestrutura.

## Consequences of Violation

1. **Efeitos colaterais:** objetos mutáveis compartilhados entre fronteiras de chamada causam bugs de ação à distância.
2. **Concorrência:** estado mutável compartilhado em código async causa condições de corrida.
3. **Custo de depuração:** rastrear onde e quando o estado mudou é caro sem garantias de imutabilidade.
4. **Remediação:** dataclasses mutáveis devem ser convertidos para frozen ou justificados com um comentário.

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

## References

- [Python dataclasses — frozen](https://docs.python.org/3/library/dataclasses.html#frozen-instances)
- [Pydantic ConfigDict — frozen](https://docs.pydantic.dev/latest/concepts/config/#frozen)
- [Ruff B006](https://docs.astral.sh/ruff/rules/mutable-argument-default/)
- codex-python-architecture (engineering/backend)
