# Lexis: Tipo Result para Tratamento de Erros em Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: tratamento de erros via tipo Result em código Python

## Law

> **Toda função Python que pode falhar de forma esperada e recuperável DEVE retornar um valor `Result[T, E]` do pacote `returns` em vez de lançar exceção. O lado `Failure` DEVE carregar uma instância do tipo `Error` do projeto (ver `lex-python-error-object`). Lançar exceções é permitido APENAS para: (a) erros de programação que indicam bug (falhas de asserção, violações de contrato); (b) falhas de infraestrutura que não podem ser tratadas localmente e DEVEM atravessar até um handler de fronteira de nível superior; (c) integração com bibliotecas ou frameworks cujo contrato exige exceções.**

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

# Composição: erros desviam o fluxo limpamente
result = await get_transaction(raw_id)
match result:
    case Success(transaction):
        return TransactionResponse.from_entity(transaction)
    case Failure(error):
        return error_response(error)
```

```python
# Erro de programação — asserção é uso correto de exceção
def compute_fee(amount: int, rate: Decimal) -> int:
    assert amount >= 0, "amount must be non-negative"  # violação de contrato
    return int(amount * rate)
```

### Incorrect

```python
# Falha esperada lançada como exceção — viola a Lei
def parse_uuid(raw: str) -> UUID:
    try:
        return UUID(raw)
    except ValueError:
        raise InvalidIdentifierError(f"'{raw}' is not a valid UUID")  # ❌

# Quem chama não vê pela assinatura que isso falha
async def get_transaction(transaction_id: str) -> Transaction:
    parsed = parse_uuid(transaction_id)  # ❌ pode lançar
    return await repository.get_by_id(parsed)  # ❌ pode lançar
```

## Automated Validation

- **Tool:** mypy em modo estrito captura uso incorreto de `Result`; regra Ruff customizada ou revisão de código sinaliza `raise` de erros de domínio fora das fronteiras permitidas.
- **When:** cada commit (pre-commit) e cada PR (CI).
- **Metric:** 0 funções de domínio falíveis lançando exceções fora das fronteiras permitidas; 100% das assinaturas falíveis usando `Result[T, Error]`.
