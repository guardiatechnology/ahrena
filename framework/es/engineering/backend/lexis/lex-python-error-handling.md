# Lexis: Manejo de Errores en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: estándares de manejo de errores para código Python

## Purpose

Garantizar que el código Python maneje los errores de manera explícita, específica y trazable. Las excepciones desnudas engullen bugs. Los catches genéricos enmascaran causas raíz. Los fallos silenciosos corrompen datos. Cada error debe ser manejado con intención o propagado con contexto.

## Law

> **NUNCA usar `except:` desnudo o `except Exception:` sin re-lanzar o loguear con contexto completo. Todas las excepciones DEBEN ser específicas al modo de falla. Las excepciones de dominio personalizadas DEBEN heredar de una excepción base del proyecto. Los mensajes de error NO DEBEN exponer datos sensibles (credenciales, tokens, PII).**

## Scope

- **Applies to:** todos los archivos fuente Python — código de aplicación, código de infraestructura, scripts.
- **Bound agents:** todos los agentes e implementadores que escriben o modifican código Python.
- **Exceptions:** los handlers de error de nivel superior (exception handlers de FastAPI, entry points de CLI) pueden capturar excepciones amplias para degradación elegante, pero DEBEN loguear la excepción original.

## Consequences of Violation

1. **Corrupción silenciosa:** las excepciones engullidas permiten que el estado inválido se propague.
2. **Costo de depuración:** los catches genéricos sin contexto hacen imposible el análisis de causa raíz.
3. **Filtración de seguridad:** los mensajes de error con credenciales o PII son una vulnerabilidad de divulgación de información.
4. **Remediación:** las excepciones desnudas deben reemplazarse con handlers específicos antes del merge.

## Examples

### Correct

```python
from app.exceptions import TransactionNotFoundError, InsufficientFundsError

# Excepción específica con contexto
async def transfer(source_id: UUID, target_id: UUID, amount: int) -> Transfer:
    source = await repository.get_by_id(source_id)
    if source is None:
        raise TransactionNotFoundError(entity_id=source_id)
    if source.balance < amount:
        raise InsufficientFundsError(
            available=source.balance, requested=amount
        )
    ...

# Handler de nivel superior — captura amplio, loguea el original
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"errors": [{"code": "INTERNAL_ERROR"}]})
```

### Incorrect

```python
# Except desnudo — engulle todo
try:
    await process_payment()
except:
    pass

# Catch genérico sin re-lanzar ni loguear
try:
    result = await repository.save(entity)
except Exception:
    return None  # retorna None silenciosamente, el caller no sabe que el save falló

# Filtrando datos sensibles
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail=f"Auth failed for token {e.token}")
```

## Automated Validation

- **Tool:** Reglas de Ruff (E722 bare except, BLE001 blind exception); revisión de código.
- **When:** cada commit (pre-commit) y cada PR (CI).
- **Metric:** 0 excepciones desnudas; 0 catches genéricos sin logging/re-raise.

## References

- [PEP 8 — Programming Recommendations (exceptions)](https://peps.python.org/pep-0008/#programming-recommendations)
- [Ruff E722](https://docs.astral.sh/ruff/rules/bare-except/)
- codex-python-architecture (engineering/backend)
