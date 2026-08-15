# Lexis: Requisitos de Testes Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: padrões de testes para código Python

## Law

> **Toda mudança ou adição de comportamento DEVE ter testes correspondentes. Mocks DEVEM ser usados apenas nas fronteiras do sistema (clientes HTTP, bancos de dados, filesystems, relógios, serviços externos). Colaboradores internos NÃO DEVEM ser mockados. Os testes DEVEM passar antes do merge.**

## Examples

### Correct

```python
# Teste unitário — lógica de domínio pura, sem mocks necessários
def test_calculate_fee_applies_percentage():
    result = calculate_fee(amount=10000, rate=Decimal("0.015"))
    assert result == 150

# Teste de integração — banco de dados real, sem mock
async def test_repository_persists_transaction(db_session: AsyncSession):
    repo = TransactionRepository(db_session)
    tx = Transaction(amount=5000, currency="BRL")
    await repo.save(tx)
    found = await repo.get_by_id(tx.entity_id)
    assert found is not None
    assert found.amount == 5000

# Mock de fronteira — API HTTP externa
async def test_notify_sends_webhook(httpx_mock):
    httpx_mock.add_response(status_code=200)
    await notify_webhook(url="https://example.com/hook", payload={"event": "created"})
```

### Incorrect

```python
# Mockando colaborador interno — oculta integração real
def test_service_with_mocked_repository(mocker):
    mock_repo = mocker.Mock()
    mock_repo.get_by_id.return_value = Transaction(amount=5000)
    service = TransactionService(mock_repo)  # RUIM: mockando interno
    ...

# Sem teste para novo comportamento
def calculate_fee(amount: int, rate: Decimal) -> int:
    return int(amount * rate)
# (sem arquivo de teste, sem função de teste)
```

## Automated Validation

- **Tool:** pytest com pytest-asyncio; relatório de cobertura via pytest-cov; aplicação no pipeline CI.
- **When:** cada commit (pre-commit para testes unitários rápidos) e cada PR (suite completa no CI).
- **Metric:** todos os testes passam; limiar de cobertura conforme configuração do projeto (mínimo recomendado 80%).
