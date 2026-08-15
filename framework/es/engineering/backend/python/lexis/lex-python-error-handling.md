# Lexis: Manejo de Errores en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: estándares de manejo de errores para código Python, complementario a `lex-python-result-type` y `lex-python-error-object`

## Purpose

Los fallos esperados y recuperables viajan como valores vía `Result[T, Error]` (`lex-python-result-type`). Esta Ley gobierna los casos residuales en que las excepciones siguen en juego: errores de programación, fallos de infraestructura que cruzan hasta handlers de frontera de nivel superior e integraciones que exigen contratos basados en excepción. En esos casos, las excepciones DEBEN ser específicas, nunca silenciadas, nunca deben filtrar datos sensibles y DEBEN traducirse siempre en un `Error` en la frontera para que el payload de respuesta permanezca estable.

## Law

> **`except:` desnudo y `except Exception:` están PROHIBIDOS, salvo cuando se combinan con logging vía `logger.exception(...)` y con re-lanzamiento o traducción a un `Error` tipado (conforme `lex-python-error-object`). Las excepciones personalizadas lanzadas en los casos permitidos (conforme `lex-python-result-type`) DEBEN ser específicas al modo de fallo y DEBEN heredar de una excepción base del proyecto. Los mensajes de excepción NO DEBEN exponer datos sensibles (credenciales, tokens, PII). Los handlers de frontera de nivel superior (exception handlers de FastAPI, entry points de CLI, entry points de consumidor de mensajes) DEBEN loguear la excepción original con contexto completo y traducirla en un `Error` antes de producir el payload de respuesta.**

## Scope

- **Applies to:** todos los archivos fuente Python — código de aplicación, infraestructura y scripts — en los casos residuales donde las excepciones se permiten por `lex-python-result-type`.
- **Bound agents:** todos los agentes e implementadores que escriben o modifican código Python.
- **Exceptions:** Ninguna. Los handlers de frontera que capturan excepciones amplias para degradación elegante no son una excepción a esta Ley — son la frontera definida por la propia Ley y DEBEN loguear + traducir.

## Consequences of Violation

1. **Corrupción silenciosa:** las excepciones engullidas permiten que el estado inválido se propague.
2. **Costo de depuración:** los catches genéricos sin contexto hacen imposible el análisis de causa raíz.
3. **Filtración de seguridad:** los mensajes de excepción con credenciales o PII son una vulnerabilidad de divulgación de información.
4. **Quiebre de contrato:** las excepciones que llegan a la respuesta sin traducir producen payloads de error fuera del estándar (conforme `lex-error-handling`).
5. **Remediación:** convertir el camino de excepción en `Result[T, Error]` cuando es esperado; en caso contrario, agregar cláusulas `except` específicas con logging y traducción a `Error`.

## Examples

### Correct

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import Error, InternalError

logger = logging.getLogger(__name__)
app = FastAPI()

# Handler de frontera de nivel superior — loguea original, traduce a Error
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    error = InternalError(message="An unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content={"errors": [{"code": error.code, "reason": error.reason, "message": error.message}]},
    )


# Excepción específica, except estrecho, sin filtrar PII
async def load_external_payload(url: str) -> bytes:
    try:
        return await http_client.get_bytes(url)
    except TimeoutError:
        logger.warning("External call timed out", extra={"url": url})
        raise  # propaga hasta la frontera; será logueada + traducida
```

### Incorrect

```python
# Except desnudo — engulle todo
try:
    await process_payment()
except:
    pass  # ❌

# Catch genérico sin logging ni traducción
try:
    result = await repository.save(entity)
except Exception:
    return None  # ❌ quien llama no sabe que el save falló

# Filtrando datos sensibles
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail=f"Auth failed for token {e.token}")  # ❌ token en el mensaje
```

## Automated Validation

- **Tool:** Reglas de Ruff (E722 bare except, BLE001 blind exception); revisión de código exigiendo logging + traducción a `Error` en los handlers de frontera.
- **When:** cada commit (pre-commit) y cada PR (CI).
- **Metric:** 0 excepciones desnudas; 0 catches genéricos sin logging; 0 handlers de frontera que retornen un payload no construido a partir de una instancia de `Error`.

## References

- lex-python-result-type (engineering/backend)
- lex-python-error-object (engineering/backend)
- lex-error-handling (engineering/platform)
- [Ruff E722](https://docs.astral.sh/ruff/rules/bare-except/)
- [Ruff BLE001](https://docs.astral.sh/ruff/rules/blind-except/)
