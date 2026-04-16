# Lexis: Inmutabilidad por Defecto en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: mutabilidad de estructuras de datos en código Python

## Purpose

Garantizar que las estructuras de datos sean inmutables por defecto, reduciendo efectos secundarios no intencionados, condiciones de carrera y corrupción de estado. El estado mutable es la principal fuente de bugs sutiles en sistemas concurrentes y asíncronos. La mutación debe ser una decisión consciente y justificada — no el valor por defecto.

## Law

> **Los dataclasses DEBEN usar `frozen=True` por defecto. Los modelos Pydantic son inmutables por defecto (`model_config = ConfigDict(frozen=True)`) a menos que la mutación sea explícitamente requerida y justificada. Los argumentos de función NO DEBEN mutarse. Los argumentos mutables por defecto están PROHIBIDOS.**

## Scope

- **Applies to:** todos los modelos de dominio Python, value objects, DTOs y estructuras de transferencia de datos.
- **Bound agents:** todos los agentes e implementadores que definen estructuras de datos.
- **Exceptions:** modelos ORM (clases mapeadas de SQLAlchemy) y patrones builder donde la mutación es inherente al patrón; deben estar confinados a la capa de infraestructura.

## Consequences of Violation

1. **Efectos secundarios:** los objetos mutables compartidos entre límites de llamada causan bugs de acción a distancia.
2. **Concurrencia:** el estado mutable compartido en código async causa condiciones de carrera.
3. **Costo de depuración:** rastrear dónde y cuándo cambió el estado es costoso sin garantías de inmutabilidad.
4. **Remediación:** los dataclasses mutables deben convertirse a frozen o justificarse con un comentario.

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


# Modelo Pydantic — inmutable por defecto
from pydantic import BaseModel, ConfigDict

class TransferResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    entity_id: str
    amount: int
    status: str
```

### Incorrect

```python
# Dataclass mutable sin justificación
@dataclass
class Money:
    amount: int
    currency: str

# Argumento mutable por defecto
def process_items(items: list[str] = []):  # BUG: default mutable compartido
    items.append("new")
    return items

# Mutando argumento de función
def enrich(transaction: Transaction) -> Transaction:
    transaction.metadata["enriched"] = True  # muta el objeto del caller
    return transaction
```

## Automated Validation

- **Tool:** Reglas de Ruff (B006 mutable default argument); revisión de código para frozen dataclasses.
- **When:** cada commit (pre-commit) y cada PR (CI).
- **Metric:** 0 argumentos mutables por defecto; todos los dataclasses de dominio usan `frozen=True`.

## References

- [Python dataclasses — frozen](https://docs.python.org/3/library/dataclasses.html#frozen-instances)
- [Pydantic ConfigDict — frozen](https://docs.pydantic.dev/latest/concepts/config/#frozen)
- [Ruff B006](https://docs.astral.sh/ruff/rules/mutable-argument-default/)
- codex-python-architecture (engineering/backend)
