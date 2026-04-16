# Lexis: Requisitos de Testes Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: padrões de testes para código Python

## Purpose

Garantir que todo o código Python que carrega comportamento tenha testes automatizados que verificam corretude, previnem regressões e habilitam refactoring seguro. Código não testado é código não verificado — funciona por coincidência, não por prova.

## Law

> **Toda mudança ou adição de comportamento DEVE ter testes correspondentes. Mocks DEVEM ser usados apenas nas fronteiras do sistema (clientes HTTP, bancos de dados, filesystems, relógios, serviços externos). Colaboradores internos NÃO DEVEM ser mockados. Os testes DEVEM passar antes do merge.**

## Scope

- **Applies to:** todo o código de aplicação Python e código de biblioteca.
- **Bound agents:** todos os agentes e implementadores que criam ou modificam comportamento.
- **Exceptions:** arquivos de configuração puros, migrações de dados com cobertura de testes de integração no nível de suite de migração.

## Consequences of Violation

1. **Regressões:** código não testado quebra silenciosamente durante refactoring ou atualizações de dependências.
2. **Falsa confiança:** mockar colaboradores internos oculta bugs de integração — os testes passam mas a produção falha.
3. **Remediação:** PRs sem testes adequados são bloqueados; cobertura ausente deve ser adicionada antes do merge.

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

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Hypothesis — property-based testing](https://hypothesis.readthedocs.io/)
- codex-python-testing (engineering/backend)
