# Lexis: Tratamento de Erros em Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: padrões de tratamento de erros para código Python, complementar a `lex-python-result-type` e `lex-python-error-object`

## Purpose

Falhas esperadas e recuperáveis trafegam como valores via `Result[T, Error]` (`lex-python-result-type`). Esta Lei governa os casos residuais em que exceções continuam em jogo: erros de programação, falhas de infraestrutura que atravessam até handlers de fronteira de nível superior, e integrações que exigem contratos baseados em exceção. Nesses casos, as exceções DEVEM ser específicas, nunca silenciadas, nunca devem vazar dados sensíveis e DEVEM sempre ser traduzidas em um `Error` na fronteira para que o payload de resposta permaneça estável.

## Law

> **`except:` nu e `except Exception:` são PROIBIDOS, exceto quando combinados com logging via `logger.exception(...)` e com re-lançamento ou tradução em um `Error` tipado (conforme `lex-python-error-object`). Exceções customizadas lançadas nos casos permitidos (conforme `lex-python-result-type`) DEVEM ser específicas ao modo de falha e DEVEM herdar de uma exceção base do projeto. Mensagens de exceção NÃO DEVEM expor dados sensíveis (credenciais, tokens, PII). Handlers de fronteira de nível superior (exception handlers do FastAPI, entry points de CLI, entry points de consumidor de mensagens) DEVEM logar a exceção original com contexto completo e traduzi-la em um `Error` antes de produzir o payload de resposta.**

## Scope

- **Applies to:** todos os arquivos fonte Python — código de aplicação, infraestrutura e scripts — nos casos residuais em que exceções são permitidas por `lex-python-result-type`.
- **Bound agents:** todos os agentes e implementadores que escrevem ou modificam código Python.
- **Exceptions:** Nenhuma. Handlers de fronteira que capturam exceções amplas para degradação elegante não são exceção a esta Lei — são a fronteira definida pela própria Lei e DEVEM logar + traduzir.

## Consequences of Violation

1. **Corrupção silenciosa:** exceções engolidas permitem que estado inválido se propague.
2. **Custo de depuração:** catches genéricos sem contexto tornam impossível a análise de causa raiz.
3. **Vazamento de segurança:** mensagens de exceção contendo credenciais ou PII são vulnerabilidade de divulgação de informação.
4. **Quebra de contrato:** exceções que chegam à resposta sem tradução produzem payloads de erro fora do padrão (conforme `lex-error-handling`).
5. **Remediação:** converter o caminho de exceção em `Result[T, Error]` quando esperado; caso contrário, adicionar cláusulas `except` específicas com logging e tradução em `Error`.

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

## References

- lex-python-result-type (engineering/backend)
- lex-python-error-object (engineering/backend)
- lex-error-handling (engineering/platform)
- [Ruff E722](https://docs.astral.sh/ruff/rules/bare-except/)
- [Ruff BLE001](https://docs.astral.sh/ruff/rules/blind-except/)
