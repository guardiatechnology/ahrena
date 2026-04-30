# Lexis: Python Error Object Structure

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: error value structure used in Result failures and error responses in Python code

## Purpose

Every error must carry a stable identifier, a machine-readable reason, and a human-readable message. This makes errors observable in logs, mappable to HTTP responses (per `lex-error-handling`), and unambiguous to consumers. Ad-hoc strings, untyped tuples, or free-form dicts lose information and cannot be evolved safely.

## Law

> **Every error value used as the `Failure` payload of a `Result` (per `lex-python-result-type`) or returned as an error in API responses MUST be an instance of a frozen dataclass `Error` with exactly three fields: `code: str` (in the format `ERR{HTTP_CODE}_{NAME}`, e.g., `ERR400_INVALID_PARAMETER`), `reason: str` (machine-readable identifier from the project's known reasons catalog), and `message: str` (human-readable description). Domain-specific errors MUST inherit from `Error` and pin `code` and `reason` as class-level defaults; `message` MUST be supplied at instantiation. Adding fields beyond `code`, `reason`, `message` to `Error` or its subclasses is FORBIDDEN. Mutating an error instance is FORBIDDEN.**

## Scope

- **Applies to:** all Python code that produces error values (domain modules, application services, API layer).
- **Bound agents:** all agents and implementers that write or modify Python code.
- **Exceptions:** third-party errors crossing into the application MUST be wrapped into an `Error` at the boundary. Structured logging context that augments observability MUST live outside the error object (in log fields, span attributes), never inside `Error`.

## Consequences of Violation

1. **Observability gap:** errors without a stable `code`/`reason` cannot be correlated across services or alerted on.
2. **API contract drift:** responses without standardized fields break downstream consumers (per `lex-error-handling`).
3. **Loss of typing:** untyped error payloads defeat the purpose of `Result[T, Error]`.
4. **Remediation:** define an `Error` subclass for the failure mode, supply `message` at construction, return via `Failure(...)`.

## Examples

### Correct

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Error:
    code: str
    reason: str
    message: str


@dataclass(frozen=True, kw_only=True)
class InvalidIdentifierError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_IDENTIFIER"


@dataclass(frozen=True, kw_only=True)
class InvalidEntityTypeError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_ENTITY_TYPE"


@dataclass(frozen=True, kw_only=True)
class InvalidTaxIdError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_TAX_ID"


# Use:
err = InvalidTaxIdError(message="CPF '123' has invalid checksum")
return Failure(err)
```

### Incorrect

```python
# String error — no code/reason
return Failure("invalid tax id")  # ❌

# Untyped dict — no contract
return Failure({"code": "INVALID", "msg": "bad"})  # ❌

# Custom field outside the schema
@dataclass(frozen=True, kw_only=True)
class InvalidTaxIdError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_TAX_ID"
    tax_id: str = ""  # ❌ extra field violates the Error contract

# Mutable error
@dataclass  # missing frozen=True
class MyError(Error):
    ...  # ❌
```

## Automated Validation

- **Tool:** code review and a custom check that every `Failure(...)` payload type is `Error` or a subclass; lint rule against extra fields in `Error` subclasses; verification that subclasses use `frozen=True` and `kw_only=True`.
- **When:** every PR (CI).
- **Metric:** 0 `Failure` returns with payloads outside the `Error` hierarchy; 0 `Error` subclasses with fields beyond `code`, `reason`, `message`; 0 mutable `Error` subclasses.

## References

- lex-python-result-type (engineering/backend)
- lex-python-error-handling (engineering/backend)
- lex-error-handling (engineering/platform) — error structure for HTTP responses
- codex-known-errors (engineering/platform) — registry of valid `reason` values
