# Codex: Padrões de Testes Python

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: padrões de testes com pytest, pytest-asyncio e Hypothesis

## Overview

Este manual define os padrões de testes para aplicações Python backend. Testes são a prova de que o código funciona. Habilitam refactoring seguro, previnem regressões e documentam o comportamento esperado. A estratégia de testes segue a pirâmide de testes: muitos testes unitários rápidos, poucos testes de integração, mínimos testes end-to-end.

## Context

- **Domain:** testes automatizados para aplicações Python.
- **Target audience:** implementadores e agentes de IA que escrevem ou mantêm testes.
- **Update trigger:** quando os padrões de testes evoluem ou novas ferramentas de teste são adotadas.

## Content

### Test Structure

```
tests/
├── unit/                    # Rápidos, sem I/O, sem dependências externas
│   ├── domain/
│   │   ├── test_entities.py
│   │   └── test_use_cases.py
│   └── conftest.py
├── integration/             # Banco de dados real, serviços reais (conteinerizados)
│   ├── database/
│   │   ├── test_repositories.py
│   │   └── test_migrations.py
│   ├── http/
│   │   └── test_routes.py
│   └── conftest.py
├── property/                # Testes baseados em propriedades com Hypothesis
│   └── test_domain_invariants.py
└── conftest.py              # Fixtures compartilhados
```

### Unit Tests

Testar lógica de domínio pura sem nenhum I/O ou dependência de framework.

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

**Regras:**
- Sem mocks, sem I/O, sem banco de dados, sem rede
- Testar comportamento, não detalhes de implementação
- Usar `parametrize` para múltiplos cenários sobre a mesma lógica
- Afirmar um conceito lógico por teste

### Integration Tests

Testar implementações de infraestrutura contra dependências reais.

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

**Regras:**
- Usar PostgreSQL real (via testcontainers ou banco de dados fornecido pelo CI)
- Fazer rollback de transações após cada teste para isolamento
- Testar o SQL real, não comportamento mockado (lex-python-testing)
- Marcar testes async com `@pytest.mark.asyncio`

### HTTP Tests

Testar endpoints FastAPI com `TestClient` ou `httpx.AsyncClient`.

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

**Regras:**
- Testar o ciclo HTTP completo: request → route → use case → repository → response
- Verificar códigos de status, estrutura de response e payloads de erro
- Usar fixtures para fornecer um `AsyncClient` configurado

### Property-Based Tests (Hypothesis)

Testar invariantes de domínio sobre entradas aleatórias.

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

**Regras:**
- Usar para invariantes de domínio que devem ser válidos para todas as entradas válidas
- Definir estratégias que correspondam às restrições do domínio
- Complementar, não substituir, testes baseados em exemplos

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

**Regras:**
- Usar fixtures de fábrica para dados de teste — valores padrão razoáveis, sobrescrever o que importa
- Fixtures compartilhados em `conftest.py` no escopo apropriado
- Preferir fixtures de escopo função para isolamento; escopo sessão para setup custoso (DB engine)

### Async Testing Configuration

```ini
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- Usar `asyncio_mode = "auto"` para evitar decorar cada teste async com `@pytest.mark.asyncio`
- Usar `pytest-asyncio` para suporte a fixtures async

## Glossary

| Termo | Definição |
|-------|-----------|
| Unit test | Testa lógica pura sem I/O ou dependências externas |
| Integration test | Testa infraestrutura contra dependências reais |
| Property-based test | Testa invariantes sobre entradas geradas aleatoriamente |
| Fixture | Mecanismo do pytest para setup de testes e injeção de dependências |
| Factory fixture | Fixture que retorna um callable que produz dados de teste com valores padrão |

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- lex-python-testing (engineering/backend)
- codex-python-architecture (engineering/backend)
