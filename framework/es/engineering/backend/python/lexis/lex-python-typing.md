# Lexis: Seguridad de Tipos en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: anotaciones de tipos en código Python

## Purpose

Garantizar que todo el código Python en el codebase tenga anotaciones de tipo completas y precisas, habilitando el análisis estático para detectar bugs antes del runtime, mejorando la legibilidad y sirviendo como documentación viva. El código sin tipos crea contratos ocultos que se rompen silenciosamente y resisten el refactoring seguro.

## Law

> **Todo el código Python DEBE tener type hints completos. mypy en modo strict DEBE pasar con cero errores. Sin uso de `Any` sin justificación explícita en un comentario.**

## Scope

- **Applies to:** todos los archivos fuente Python (código de aplicación, tests, scripts, migraciones excluidas).
- **Bound agents:** todos los agentes e implementadores que escriben o modifican código Python.
- **Exceptions:** stubs de bibliotecas de terceros no disponibles; deben documentarse con `# type: ignore[<code>]` y un comentario de justificación.

## Consequences of Violation

1. **Bugs silenciosos:** el código sin tipos permite incompatibilidades de tipo que solo aparecen en runtime, frecuentemente en producción.
2. **Riesgo de refactoring:** sin tipos, renombrar o reestructurar no puede verificarse estáticamente.
3. **Remediación:** el código sin tipos debe anotarse antes del merge; los PRs con errores de mypy son bloqueados.

## Examples

### Correct

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    entity_id: UUID
    amount: int
    currency: str
    created_at: datetime


async def get_transaction(transaction_id: UUID) -> TransactionResponse | None:
    ...
```

### Incorrect

```python
# Tipo de retorno faltante, parámetro sin tipo
async def get_transaction(transaction_id):
    ...

# Usando Any sin justificación
from typing import Any
def process(data: Any) -> Any:
    ...
```

## Automated Validation

- **Tool:** mypy con el flag `--strict`; integrado en pre-commit hooks y pipeline CI.
- **When:** cada commit (pre-commit) y cada PR (CI).
- **Metric:** 0 errores de mypy en modo strict.

## References

- [mypy documentation — strict mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [PEP 604 — Union syntax X | Y](https://peps.python.org/pep-0604/)
- codex-python-tooling (engineering/backend)
