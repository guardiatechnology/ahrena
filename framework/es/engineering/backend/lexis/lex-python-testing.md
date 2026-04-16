# Lexis: Requisitos de Testing en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: estándares de testing para código Python

## Purpose

Garantizar que todo el código Python que contiene comportamiento tenga tests automatizados que verifiquen correctitud, prevengan regresiones y habiliten refactoring seguro. El código no testeado es código no verificado — funciona por coincidencia, no por prueba.

## Law

> **Todo cambio o adición de comportamiento DEBE tener tests correspondientes. Los mocks DEBEN usarse solo en los límites del sistema (clientes HTTP, bases de datos, filesystems, relojes, servicios externos). Los colaboradores internos NO DEBEN ser mockeados. Los tests DEBEN pasar antes del merge.**

## Scope

- **Applies to:** todo el código de aplicación Python y código de biblioteca.
- **Bound agents:** todos los agentes e implementadores que crean o modifican comportamiento.
- **Exceptions:** archivos de configuración puros, migraciones de datos con cobertura de tests de integración a nivel de suite de migración.

## Consequences of Violation

1. **Regresiones:** el código no testeado se rompe silenciosamente durante el refactoring o las actualizaciones de dependencias.
2. **Falsa confianza:** mockear colaboradores internos oculta bugs de integración — los tests pasan pero producción falla.
3. **Remediación:** los PRs sin tests adecuados son bloqueados; la cobertura faltante debe agregarse antes del merge.

## Examples

### Correct

```python
# Test unitario — lógica de dominio pura, sin mocks necesarios
def test_calculate_fee_applies_percentage():
    result = calculate_fee(amount=10000, rate=Decimal("0.015"))
    assert result == 150


# Test de integración — base de datos real, sin mock
async def test_repository_persists_transaction(db_session: AsyncSession):
    repo = TransactionRepository(db_session)
    tx = Transaction(amount=5000, currency="BRL")
    await repo.save(tx)
    found = await repo.get_by_id(tx.entity_id)
    assert found is not None
    assert found.amount == 5000


# Mock de límite — API HTTP externa
async def test_notify_sends_webhook(httpx_mock):
    httpx_mock.add_response(status_code=200)
    await notify_webhook(url="https://example.com/hook", payload={"event": "created"})
```

### Incorrect

```python
# Mockear colaborador interno — oculta la integración real
def test_service_with_mocked_repository(mocker):
    mock_repo = mocker.Mock()
    mock_repo.get_by_id.return_value = Transaction(amount=5000)
    service = TransactionService(mock_repo)  # MAL: mockear interno
    ...

# Sin test para nuevo comportamiento
def calculate_fee(amount: int, rate: Decimal) -> int:
    return int(amount * rate)
# (sin archivo de test, sin función de test)
```

## Automated Validation

- **Tool:** pytest con pytest-asyncio; reporte de cobertura via pytest-cov; aplicación en pipeline CI.
- **When:** cada commit (pre-commit para tests unitarios rápidos) y cada PR (suite completa en CI).
- **Metric:** todos los tests pasan; umbral de cobertura según configuración del proyecto (mínimo recomendado 80%).

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Hypothesis — property-based testing](https://hypothesis.readthedocs.io/)
- codex-python-testing (engineering/backend)
