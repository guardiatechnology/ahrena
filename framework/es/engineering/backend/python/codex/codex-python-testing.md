# Codex: Patrones de Testing en Python

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: patrones de testing con pytest, pytest-asyncio e Hypothesis

## Overview

Este manual define los patrones de testing para aplicaciones Python backend. Los tests son la prueba de que el código funciona. Habilitan refactoring seguro, previenen regresiones y documentan el comportamiento esperado. La estrategia de testing sigue la pirámide de testing: muchos tests unitarios rápidos, menos tests de integración, mínimos tests end-to-end.

## Context

- **Domain:** testing automatizado para aplicaciones Python.
- **Target audience:** implementadores y agentes de IA que escriben o mantienen tests.
- **Update trigger:** cuando los patrones de testing evolucionan o se adoptan nuevas herramientas de testing.

## Content

### Test Structure

```
tests/
├── unit/                    # Rápidos, sin I/O, sin dependencias externas
│   ├── domain/
│   │   ├── test_entities.py
│   │   └── test_use_cases.py
│   └── conftest.py
├── integration/             # Base de datos real, servicios reales (contenedorizados)
│   ├── database/
│   │   ├── test_repositories.py
│   │   └── test_migrations.py
│   ├── http/
│   │   └── test_routes.py
│   └── conftest.py
├── property/                # Tests basados en propiedades con Hypothesis
│   └── test_domain_invariants.py
└── conftest.py              # Fixtures compartidos
```

### Unit Tests

Testear lógica de dominio pura sin ningún I/O ni dependencia de framework.

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

**Reglas:**
- Sin mocks, sin I/O, sin base de datos, sin red
- Testear comportamiento, no detalles de implementación
- Usar `parametrize` para múltiples escenarios sobre la misma lógica
- Afirmar un concepto lógico por test

### Integration Tests

Testear implementaciones de infraestructura contra dependencias reales.

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

**Reglas:**
- Usar PostgreSQL real (via testcontainers o base de datos provista por CI)
- Revertir transacciones después de cada test para aislamiento
- Testear el SQL real, no comportamiento mockeado (lex-python-testing)
- Marcar tests async con `@pytest.mark.asyncio`

### HTTP Tests

Testear endpoints de FastAPI con `TestClient` o `httpx.AsyncClient`.

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

**Reglas:**
- Testear el ciclo HTTP completo: request → route → use case → repository → response
- Verificar códigos de estado, estructura de respuesta y payloads de error
- Usar fixtures para proveer un `AsyncClient` configurado

### Property-Based Tests (Hypothesis)

Testear invariantes de dominio sobre entradas aleatorias.

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

**Reglas:**
- Usar para invariantes de dominio que deben cumplirse para todas las entradas válidas
- Definir estrategias que coincidan con las restricciones del dominio
- Complementar, no reemplazar, los tests basados en ejemplos

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

**Reglas:**
- Usar fixtures de fábrica para datos de test — valores por defecto razonables, sobrescribir lo que importa
- Fixtures compartidos en `conftest.py` en el scope apropiado
- Preferir fixtures de scope función para aislamiento; scope sesión para setup costoso (DB engine)

### Async Testing Configuration

```ini
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- Usar `asyncio_mode = "auto"` para evitar decorar cada test async con `@pytest.mark.asyncio`
- Usar `pytest-asyncio` para soporte de fixtures async

## Glossary

| Término | Definición |
|---------|-----------|
| Unit test | Testea lógica pura sin I/O ni dependencias externas |
| Integration test | Testea infraestructura contra dependencias reales |
| Property-based test | Testea invariantes sobre entradas generadas aleatoriamente |
| Fixture | Mecanismo de pytest para setup de tests e inyección de dependencias |
| Factory fixture | Fixture que retorna un callable que produce datos de test con valores por defecto |

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- lex-python-testing (engineering/backend)
- codex-python-architecture (engineering/backend)
