# Lexis: Tipo Result para Manejo de Errores en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: manejo de errores mediante el tipo Result en código Python

## Purpose

Hacer explícitos, tipados y componibles los caminos de fallo. Las excepciones ocultan el flujo de control y obligan a quien llama a recordar qué funciones pueden lanzar. Los errores como valor de retorno exponen cada operación falible en la firma, se propagan limpios por pipelines y permiten que el verificador de tipos exija el manejo de fallos.

## Law

> **Toda función Python que puede fallar de forma esperada y recuperable DEBE retornar un valor `Result[T, E]` del paquete `returns` en lugar de lanzar una excepción. El lado `Failure` DEBE llevar una instancia del tipo `Error` del proyecto (ver `lex-python-error-object`). Lanzar excepciones se permite SOLO para: (a) errores de programación que indican un bug (fallas de aserción, violaciones de contrato); (b) fallos de infraestructura que no pueden manejarse localmente y DEBEN cruzar hasta un handler de frontera de nivel superior; (c) integración con bibliotecas o frameworks cuyo contrato exige excepciones.**

## Scope

- **Applies to:** todo código Python de aplicación, dominio y servicio con modos de fallo esperados (validación, persistencia, parsing, llamadas externas, reglas de negocio).
- **Bound agents:** todos los agentes e implementadores que escriben o modifican código Python.
- **Exceptions:** Ninguna. Los casos (a), (b), (c) anteriores no son excepciones a esta Ley — son la frontera definida por la propia Ley.

## Consequences of Violation

1. **Flujo de control oculto:** las excepciones para fallos esperados obligan a quien llama a conocer detalles de implementación.
2. **Fallos sin tipo:** los errores pierden lugar en la firma; el verificador de tipos no ayuda.
3. **Composición rota:** los pipelines funcionales (`bind`, `map`) no pueden esquivar excepciones de manera limpia.
4. **Remediación:** reescribir la función para que retorne `Result[T, Error]`; sustituir `raise` por `Failure(error)` y ajustar a quienes llaman.

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

# Composición: los errores desvían el flujo de manera limpia
result = await get_transaction(raw_id)
match result:
    case Success(transaction):
        return TransactionResponse.from_entity(transaction)
    case Failure(error):
        return error_response(error)
```

```python
# Error de programación — la aserción es uso correcto de excepción
def compute_fee(amount: int, rate: Decimal) -> int:
    assert amount >= 0, "amount must be non-negative"  # violación de contrato
    return int(amount * rate)
```

### Incorrect

```python
# Fallo esperado lanzado como excepción — viola la Ley
def parse_uuid(raw: str) -> UUID:
    try:
        return UUID(raw)
    except ValueError:
        raise InvalidIdentifierError(f"'{raw}' is not a valid UUID")  # ❌

# Quien llama no ve por la firma que esto falla
async def get_transaction(transaction_id: str) -> Transaction:
    parsed = parse_uuid(transaction_id)  # ❌ puede lanzar
    return await repository.get_by_id(parsed)  # ❌ puede lanzar
```

## Automated Validation

- **Tool:** mypy en modo estricto detecta el uso incorrecto de `Result`; regla Ruff personalizada o revisión de código señala `raise` de errores de dominio fuera de las fronteras permitidas.
- **When:** cada commit (pre-commit) y cada PR (CI).
- **Metric:** 0 funciones de dominio falibles que lancen excepciones fuera de las fronteras permitidas; 100% de las firmas falibles usando `Result[T, Error]`.

## References

- [Documentación returns — Quickstart](https://returns.readthedocs.io/en/latest/pages/quickstart.html)
- [returns — Contenedor Result](https://returns.readthedocs.io/en/latest/pages/result.html)
- lex-python-error-object (engineering/backend)
- lex-python-error-handling (engineering/backend)
