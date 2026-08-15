# Lexis: Python Security Practices

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: security standards for Python code

## Purpose

Ensure that Python code does not introduce security vulnerabilities. Hardcoded secrets, unvalidated inputs, and unaudited dependencies are attack vectors that compromise the entire system. Security is not an afterthought — it is a constraint on every line of code.

## Law

> **No secrets MUST be hardcoded in source code. All external input MUST be validated at system boundaries using Pydantic models. Dependencies MUST be audited for known vulnerabilities before adoption and periodically thereafter. SQL queries MUST use parameterized statements — never string interpolation.**

## Scope

- **Applies to:** all Python source files, configuration, and dependency manifests.
- **Bound agents:** all agents and implementers that write or modify Python code or manage dependencies.
- **Exceptions:** none. Security laws have no exceptions.

## Consequences of Violation

1. **Credential leak:** hardcoded secrets in repositories are harvested by automated scanners within minutes.
2. **Injection:** unvalidated input enables SQL injection, command injection, and path traversal.
3. **Supply chain:** vulnerable dependencies are actively exploited in the wild.
4. **Remediation:** immediate rotation of leaked credentials; vulnerable code must be patched before merge.

## Examples

### Correct

```python
import os
from pydantic import BaseModel, Field

# Secrets from environment
DATABASE_URL = os.environ["DATABASE_URL"]

# Input validation at boundary
class CreateTransferRequest(BaseModel):
    amount: int = Field(gt=0, le=999_999_999)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    recipient_id: str = Field(min_length=1, max_length=36)

# Parameterized query
stmt = select(Transaction).where(Transaction.entity_id == transaction_id)
```

### Incorrect

```python
# Hardcoded secret
API_KEY = "sk-live-abc123secret"

# Unvalidated input passed to query
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"  # SQL injection
    ...

# String interpolation in SQLAlchemy
stmt = text(f"SELECT * FROM transactions WHERE status = '{status}'")
```

## Automated Validation

- **Tool:** Ruff security rules (S subset); pip-audit or safety for dependency scanning; pre-commit hooks.
- **When:** every commit (pre-commit) and every PR (CI pipeline with dependency audit).
- **Metric:** 0 hardcoded secrets detected; 0 known vulnerabilities in dependencies; 0 SQL injection vectors.

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [pip-audit](https://pypi.org/project/pip-audit/)
- [Bandit / Ruff S rules](https://docs.astral.sh/ruff/rules/#flake8-bandit-s)
- [Pydantic validation](https://docs.pydantic.dev/latest/)
- codex-python-tooling (engineering/backend)
