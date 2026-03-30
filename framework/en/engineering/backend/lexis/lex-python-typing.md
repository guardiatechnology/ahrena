# Lexis: Python Type Safety

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: type annotations in Python code

## Purpose

Ensure that all Python code in the codebase has complete, accurate type annotations, enabling static analysis to catch bugs before runtime, improving readability, and serving as living documentation. Untyped code creates hidden contracts that break silently and resist safe refactoring.

## Law

> **All Python code MUST have complete type hints. mypy in strict mode MUST pass with zero errors. No use of `Any` without explicit justification in a comment.**

## Scope

- **Applies to:** all Python source files (application code, tests, scripts, migrations excluded).
- **Bound agents:** all agents and implementers that write or modify Python code.
- **Exceptions:** third-party library stubs not available; must be documented with `# type: ignore[<code>]` and a justification comment.

## Consequences of Violation

1. **Silent bugs:** untyped code allows type mismatches that surface only at runtime, often in production.
2. **Refactoring risk:** without types, renaming or restructuring cannot be statically verified.
3. **Remediation:** untyped code must be annotated before merge; PRs with mypy errors are blocked.

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

## References

- [mypy documentation — strict mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [PEP 604 — Union syntax X | Y](https://peps.python.org/pep-0604/)
- codex-python-tooling (engineering/backend)
