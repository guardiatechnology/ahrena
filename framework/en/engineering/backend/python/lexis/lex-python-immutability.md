# Lexis: Python Immutability by Default

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: data structure mutability in Python code

## Purpose

Ensure that data structures are immutable by default, reducing unintended side effects, race conditions, and state corruption. Mutable state is the primary source of subtle bugs in concurrent and asynchronous systems. Mutation must be a conscious, justified decision — not the default.

## Law

> **Dataclasses MUST use `frozen=True` by default. Pydantic models are immutable by default (`model_config = ConfigDict(frozen=True)`) unless mutation is explicitly required and justified. Function arguments MUST NOT be mutated. Mutable default arguments are FORBIDDEN.**

## Scope

- **Applies to:** all Python domain models, value objects, DTOs, and data transfer structures.
- **Bound agents:** all agents and implementers that define data structures.
- **Exceptions:** ORM models (SQLAlchemy mapped classes) and builder patterns where mutation is inherent to the pattern; must be confined to the infrastructure layer.

## Consequences of Violation

1. **Side effects:** mutable objects shared across call boundaries cause action-at-a-distance bugs.
2. **Concurrency:** mutable shared state in async code causes race conditions.
3. **Debugging cost:** tracing where and when state changed is expensive without immutability guarantees.
4. **Remediation:** mutable dataclasses must be converted to frozen or justified with a comment.

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


# Pydantic model — immutable by default
from pydantic import BaseModel, ConfigDict

class TransferResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    entity_id: str
    amount: int
    status: str
```

### Incorrect

```python
# Mutable dataclass without justification
@dataclass
class Money:
    amount: int
    currency: str

# Mutable default argument
def process_items(items: list[str] = []):  # BUG: shared mutable default
    items.append("new")
    return items

# Mutating function argument
def enrich(transaction: Transaction) -> Transaction:
    transaction.metadata["enriched"] = True  # mutates caller's object
    return transaction
```

## Automated Validation

- **Tool:** Ruff rules (B006 mutable default argument); code review for frozen dataclasses.
- **When:** every commit (pre-commit) and every PR (CI).
- **Metric:** 0 mutable default arguments; all domain dataclasses use `frozen=True`.

## References

- [Python dataclasses — frozen](https://docs.python.org/3/library/dataclasses.html#frozen-instances)
- [Pydantic ConfigDict — frozen](https://docs.pydantic.dev/latest/concepts/config/#frozen)
- [Ruff B006](https://docs.astral.sh/ruff/rules/mutable-argument-default/)
- codex-python-architecture (engineering/backend)
