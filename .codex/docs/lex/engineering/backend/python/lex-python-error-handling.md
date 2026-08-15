# Lexis: Tratamento de Erros em Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: padrões de tratamento de erros para código Python, complementar a `lex-python-result-type` e `lex-python-error-object`

## Law

> **`except:` nu e `except Exception:` são PROIBIDOS, exceto quando combinados com logging via `logger.exception(...)` e com re-lançamento ou tradução em um `Error` tipado (conforme `lex-python-error-object`). Exceções customizadas lançadas nos casos permitidos (conforme `lex-python-result-type`) DEVEM ser específicas ao modo de falha e DEVEM herdar de uma exceção base do projeto. Mensagens de exceção NÃO DEVEM expor dados sensíveis (credenciais, tokens, PII). Handlers de fronteira de nível superior (exception handlers do FastAPI, entry points de CLI, entry points de consumidor de mensagens) DEVEM logar a exceção original com contexto completo e traduzi-la em um `Error` antes de produzir o payload de resposta.**

## Examples

### Correct

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import Error, InternalError

logger = logging.getLogger(__name__)
app = FastAPI()

# Handler de fronteira de nível superior — loga original, traduz em Error
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    error = InternalError(message="An unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content={"errors": [{"code": error.code, "reason": error.reason, "message": error.message}]},
    )

# Exceção específica, except estreito, sem vazar PII
async def load_external_payload(url: str) -> bytes:
    try:
        return await http_client.get_bytes(url)
    except TimeoutError:
        logger.warning("External call timed out", extra={"url": url})
        raise  # propaga até a fronteira; será logada + traduzida
```

### Incorrect

```python
# Except nu — engole tudo
try:
    await process_payment()
except:
    pass  # ❌

# Catch genérico sem logging nem tradução
try:
    result = await repository.save(entity)
except Exception:
    return None  # ❌ quem chama não sabe que o save falhou

# Vazando dados sensíveis
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail=f"Auth failed for token {e.token}")  # ❌ token na mensagem
```

## Automated Validation

- **Tool:** Regras Ruff (E722 bare except, BLE001 blind exception); revisão de código exigindo logging + tradução para `Error` nos handlers de fronteira.
- **When:** cada commit (pre-commit) e cada PR (CI).
- **Metric:** 0 exceções nuas; 0 catches genéricos sem logging; 0 handlers de fronteira retornando payload que não seja construído a partir de uma instância de `Error`.
