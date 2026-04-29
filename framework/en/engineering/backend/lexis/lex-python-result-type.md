# Lexis: Python Result Type for Error Handling

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: error handling using the Result type in Python code

## Purpose

Make failure paths explicit, typed, and composable. Exceptions hide control flow and force callers to remember which functions might raise. Return-based errors expose every fallible operation in the type signature, propagate cleanly through pipelines, and let the type checker enforce that errors are handled.

## Law

> **Every Python function that may fail in an expected, recoverable way MUST return a `Result[T, E]` value from the `returns` package instead of raising an exception. The `Failure` side MUST carry an instance of the project's `Error` type (see `lex-python-error-object`). Raising exceptions is permitted ONLY for: (a) programmer errors that indicate a bug (assertion failures, contract violations); (b) infrastructure failures that cannot be handled locally and MUST cross to a top-level boundary handler; (c) integration with libraries or frameworks whose contract requires exceptions.**

## Scope

- **Applies to:** all Python application, domain, and service code with expected failure modes (validation, persistence, parsing, external calls, business rules).
- **Bound agents:** all agents and implementers that write or modify Python code.
- **Exceptions:** None. Cases (a), (b), (c) above are not exceptions to this law — they are the law's defined boundary.

## Consequences of Violation

1. **Hidden control flow:** raised exceptions for expected failures force callers to know implementation details.
2. **Untyped failures:** errors lose their place in the type signature; the type checker cannot help.
3. **Broken composition:** functional pipelines (`bind`, `map`) cannot route around exceptions cleanly.
4. **Remediation:** rewrite the function to return `Result[T, Error]`; replace `raise` with `Failure(error)` and adjust callers.

## Examples

### Correct

```python
from uuid import UUID
from returns.result import Result, Success, Failure
from app.errors import Error, InvalidIdentifierError

def parse_uuid(raw: str) -> Result[UUID, Error]:
    try:
        return Success(UUID(raw))
    except ValueError:
        return Failure(InvalidIdentifierError(message=f"'{raw}' is not a valid UUID"))

async def get_transaction(transaction_id: str) -> Result[Transaction, Error]:
    parsed = parse_uuid(transaction_id)
    if isinstance(parsed, Failure):
        return parsed
    return await repository.get_by_id(parsed.unwrap())

# Composition: errors short-circuit cleanly
result = await get_transaction(raw_id)
match result:
    case Success(transaction):
        return TransactionResponse.from_entity(transaction)
    case Failure(error):
        return error_response(error)
```

```python
# Programmer error — assertion is correct use of exception
def compute_fee(amount: int, rate: Decimal) -> int:
    assert amount >= 0, "amount must be non-negative"  # contract violation
    return int(amount * rate)
```

### Incorrect

```python
# Expected failure raised as exception — violates the law
def parse_uuid(raw: str) -> UUID:
    try:
        return UUID(raw)
    except ValueError:
        raise InvalidIdentifierError(f"'{raw}' is not a valid UUID")  # ❌

# Caller cannot see from signature that this fails
async def get_transaction(transaction_id: str) -> Transaction:
    parsed = parse_uuid(transaction_id)  # ❌ may raise
    return await repository.get_by_id(parsed)  # ❌ may raise
```

## Automated Validation

- **Tool:** mypy strict mode catches `Result` mishandling; custom Ruff rule or code review flags `raise` of domain errors outside permitted boundaries.
- **When:** every commit (pre-commit) and every PR (CI).
- **Metric:** 0 fallible domain functions raising exceptions outside the permitted boundaries; 100% of fallible signatures using `Result[T, Error]`.

## References

- [returns documentation — Quickstart](https://returns.readthedocs.io/en/latest/pages/quickstart.html)
- [returns — Result container](https://returns.readthedocs.io/en/latest/pages/result.html)
- lex-python-error-object (engineering/backend)
- lex-python-error-handling (engineering/backend)
