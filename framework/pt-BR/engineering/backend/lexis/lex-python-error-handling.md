# Lexis: Tratamento de Erros Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: padrões de tratamento de erros para código Python

## Purpose

Garantir que o código Python trate erros de forma explícita, específica e rastreável. Exceções nuas engolem bugs. Catches genéricos mascaram causas raiz. Falhas silenciosas corrompem dados. Todo erro deve ser tratado com intenção ou propagado com contexto.

## Law

> **NUNCA usar `except:` nu ou `except Exception:` sem re-lançar ou logar com contexto completo. Todas as exceções DEVEM ser específicas ao modo de falha. Exceções de domínio customizadas DEVEM herdar de uma exceção base do projeto. Mensagens de erro NÃO DEVEM expor dados sensíveis (credenciais, tokens, PII).**

## Scope

- **Applies to:** todos os arquivos fonte Python — código de aplicação, código de infraestrutura, scripts.
- **Bound agents:** todos os agentes e implementadores que escrevem ou modificam código Python.
- **Exceptions:** handlers de erro de nível superior (exception handlers do FastAPI, entry points de CLI) podem capturar exceções amplas para degradação elegante, mas DEVEM logar a exceção original.

## Consequences of Violation

1. **Corrupção silenciosa:** exceções engolidas permitem que estado inválido se propague.
2. **Custo de depuração:** catches genéricos sem contexto tornam impossível a análise de causa raiz.
3. **Vazamento de segurança:** mensagens de erro contendo credenciais ou PII são uma vulnerabilidade de divulgação de informação.
4. **Remediação:** exceções nuas devem ser substituídas por handlers específicos antes do merge.

## Examples

### Correct

```python
from app.exceptions import TransactionNotFoundError, InsufficientFundsError

# Exceção específica com contexto
async def transfer(source_id: UUID, target_id: UUID, amount: int) -> Transfer:
    source = await repository.get_by_id(source_id)
    if source is None:
        raise TransactionNotFoundError(entity_id=source_id)
    if source.balance < amount:
        raise InsufficientFundsError(
            available=source.balance, requested=amount
        )
    ...

# Handler de nível superior — captura amplo, loga o original
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"errors": [{"code": "INTERNAL_ERROR"}]})
```

### Incorrect

```python
# Except nu — engole tudo
try:
    await process_payment()
except:
    pass

# Catch genérico sem re-lançar ou logar
try:
    result = await repository.save(entity)
except Exception:
    return None  # retorna None silenciosamente, o caller não sabe que o save falhou

# Vazando dados sensíveis
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail=f"Auth failed for token {e.token}")
```

## Automated Validation

- **Tool:** Regras Ruff (E722 bare except, BLE001 blind exception); revisão de código.
- **When:** cada commit (pre-commit) e cada PR (CI).
- **Metric:** 0 exceções nuas; 0 catches genéricos sem logging/re-raise.

## References

- [PEP 8 — Programming Recommendations (exceptions)](https://peps.python.org/pep-0008/#programming-recommendations)
- [Ruff E722](https://docs.astral.sh/ruff/rules/bare-except/)
- codex-python-architecture (engineering/backend)
