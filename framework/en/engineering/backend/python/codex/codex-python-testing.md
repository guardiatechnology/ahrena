# Codex: Python Testing Patterns

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: testing patterns with pytest, pytest-asyncio, and Hypothesis

## Overview

This manual defines the testing patterns for Python backend applications. Tests are the proof that code works. They enable safe refactoring, prevent regressions, and document expected behavior. The test strategy follows the testing pyramid: many fast unit tests, fewer integration tests, minimal end-to-end tests.

## Context

- **Domain:** automated testing for Python applications.
- **Target audience:** implementers and AI agents that write or maintain tests.
- **Update trigger:** when testing patterns evolve or new testing tools are adopted.

## Content

### Test Structure

```
tests/
├── unit/                    # Fast, no I/O, no external dependencies
│   ├── domain/
│   │   ├── test_entities.py
│   │   └── test_use_cases.py
│   └── conftest.py
├── integration/             # Real database, real services (containerized)
│   ├── database/
│   │   ├── test_repositories.py
│   │   └── test_migrations.py
│   ├── http/
│   │   └── test_routes.py
│   └── conftest.py
├── property/                # Hypothesis property-based tests
│   └── test_domain_invariants.py
└── conftest.py              # Shared fixtures
```

### Unit Tests

Test pure domain logic without any I/O or framework dependency.

```python
import pytest
from decimal import Decimal


def test_calculate_fee_with_standard_rate():
    result = calculate_fee(amount=10_000, rate=Decimal("0.015"))
    assert result == 150


def test_calculate_fee_rejects_negative_amount():
    with pytest.raises(ValueError, match="amount must be positive"):
        calculate_fee(amount=-100, rate=Decimal("0.015"))


@pytest.mark.parametrize(
    "amount, rate, expected",
    [
        (10_000, Decimal("0.01"), 100),
        (10_000, Decimal("0.05"), 500),
        (0, Decimal("0.05"), 0),
    ],
)
def test_calculate_fee_various_rates(amount: int, rate: Decimal, expected: int):
    assert calculate_fee(amount=amount, rate=rate) == expected
```

**Rules:**
- No mocks, no I/O, no database, no network
- Test behavior, not implementation details
- Use `parametrize` for multiple scenarios on the same logic
- Assert one logical concept per test

### Integration Tests

Test infrastructure implementations against real dependencies.

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        async with session.begin():
            yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_repository_saves_and_retrieves(db_session: AsyncSession):
    repo = SqlAlchemyTransactionRepository(db_session)
    transaction = make_transaction(amount=5000)
    await repo.save(transaction)
    found = await repo.get_by_id(transaction.entity_id)
    assert found is not None
    assert found.amount == 5000
    assert found.entity_id == transaction.entity_id


@pytest.mark.asyncio
async def test_repository_returns_none_for_missing(db_session: AsyncSession):
    repo = SqlAlchemyTransactionRepository(db_session)
    result = await repo.get_by_id(uuid7())
    assert result is None
```

**Rules:**
- Use real PostgreSQL (via testcontainers or CI-provided database)
- Roll back transactions after each test for isolation
- Test the actual SQL, not mocked behavior (lex-python-testing)
- Mark async tests with `@pytest.mark.asyncio`

### HTTP Tests

Test FastAPI endpoints with `TestClient` or `httpx.AsyncClient`.

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_transaction_returns_201(client: AsyncClient):
    response = await client.post(
        "/v1/transactions",
        json={"amount": 5000, "currency": "BRL"},
        headers={"Idempotency-Key": "unique-key-123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 5000
    assert "entity_id" in data


@pytest.mark.asyncio
async def test_create_transaction_rejects_negative_amount(client: AsyncClient):
    response = await client.post(
        "/v1/transactions",
        json={"amount": -100, "currency": "BRL"},
        headers={"Idempotency-Key": "key-456"},
    )
    assert response.status_code == 422
```

**Rules:**
- Test the full HTTP cycle: request → route → use case → repository → response
- Verify status codes, response structure, and error payloads
- Use fixtures to provide a configured `AsyncClient`

### Property-Based Tests (Hypothesis)

Test domain invariants over random inputs.

```python
from hypothesis import given, strategies as st


@given(amount=st.integers(min_value=0, max_value=999_999_999))
def test_fee_is_never_negative(amount: int):
    result = calculate_fee(amount=amount, rate=Decimal("0.015"))
    assert result >= 0


@given(amount=st.integers(min_value=1, max_value=999_999_999))
def test_fee_is_always_less_than_amount(amount: int):
    result = calculate_fee(amount=amount, rate=Decimal("0.015"))
    assert result <= amount
```

**Rules:**
- Use for domain invariants that must hold for all valid inputs
- Define strategies that match your domain constraints
- Complement, don't replace, example-based tests

### Fixtures and Factories

```python
import pytest
from uuid import UUID
from datetime import datetime, timezone


@pytest.fixture
def make_transaction():
    def _factory(
        entity_id: UUID | None = None,
        amount: int = 1000,
        currency: str = "BRL",
        status: TransactionStatus = TransactionStatus.PENDING,
    ) -> Transaction:
        return Transaction(
            entity_id=entity_id or uuid7(),
            amount=amount,
            currency=currency,
            status=status,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version=1,
        )
    return _factory
```

**Rules:**
- Use factory fixtures for test data — sensible defaults, override what matters
- Shared fixtures in `conftest.py` at the appropriate scope
- Prefer function-scoped fixtures for isolation; session-scoped for expensive setup (DB engine)

### Async Testing Configuration

```ini
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- Use `asyncio_mode = "auto"` to avoid decorating every async test with `@pytest.mark.asyncio`
- Use `pytest-asyncio` for async fixture support

## Glossary

| Term | Definition |
|------|------------|
| Unit test | Tests pure logic without I/O or external dependencies |
| Integration test | Tests infrastructure against real dependencies |
| Property-based test | Tests invariants over randomly generated inputs |
| Fixture | pytest mechanism for test setup and dependency injection |
| Factory fixture | Fixture that returns a callable producing test data with defaults |

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- lex-python-testing (engineering/backend)
- codex-python-architecture (engineering/backend)
