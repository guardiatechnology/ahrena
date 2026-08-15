# Lexis: Python Testing Requirements

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend: testing standards for Python code

## Purpose

Ensure that all behavior-bearing Python code has automated tests that verify correctness, prevent regressions, and enable safe refactoring. Untested code is unverified code — it works by coincidence, not by proof.

## Law

> **Every behavior change or addition MUST have corresponding tests. Mocks MUST only be used at system boundaries (HTTP clients, databases, filesystems, clocks, external services). Internal collaborators MUST NOT be mocked. Tests MUST pass before merge.**

## Scope

- **Applies to:** all Python application code and library code.
- **Bound agents:** all agents and implementers that create or modify behavior.
- **Exceptions:** pure configuration files, data migrations with integration test coverage at the migration suite level.

## Consequences of Violation

1. **Regressions:** untested code breaks silently during refactoring or dependency updates.
2. **False confidence:** mocking internal collaborators hides integration bugs — tests pass but production fails.
3. **Remediation:** PRs without adequate tests are blocked; missing coverage must be added before merge.

## Examples

### Correct

```python
# Unit test — pure domain logic, no mocks needed
def test_calculate_fee_applies_percentage():
    result = calculate_fee(amount=10000, rate=Decimal("0.015"))
    assert result == 150


# Integration test — real database, no mock
async def test_repository_persists_transaction(db_session: AsyncSession):
    repo = TransactionRepository(db_session)
    tx = Transaction(amount=5000, currency="BRL")
    await repo.save(tx)
    found = await repo.get_by_id(tx.entity_id)
    assert found is not None
    assert found.amount == 5000


# Boundary mock — external HTTP API
async def test_notify_sends_webhook(httpx_mock):
    httpx_mock.add_response(status_code=200)
    await notify_webhook(url="https://example.com/hook", payload={"event": "created"})
```

### Incorrect

```python
# Mocking internal collaborator — hides real integration
def test_service_with_mocked_repository(mocker):
    mock_repo = mocker.Mock()
    mock_repo.get_by_id.return_value = Transaction(amount=5000)
    service = TransactionService(mock_repo)  # BAD: mocking internal
    ...

# No test for new behavior
def calculate_fee(amount: int, rate: Decimal) -> int:
    return int(amount * rate)
# (no test file, no test function)
```

## Automated Validation

- **Tool:** pytest with pytest-asyncio; coverage report via pytest-cov; CI pipeline enforcement.
- **When:** every commit (pre-commit for fast unit tests) and every PR (full suite in CI).
- **Metric:** all tests pass; coverage threshold per project configuration (recommended minimum 80%).

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Hypothesis — property-based testing](https://hypothesis.readthedocs.io/)
- codex-python-testing (engineering/backend)
