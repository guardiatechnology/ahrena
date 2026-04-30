# Codex: Logging Python com Loguru e Decorator

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: padrão de logging em aplicações Python

## Overview

Este manual define como aplicações Python backend produzem, formatam e correlacionam logs. É a especialização Python da `lex-logging-decorator` (regra agnóstica de linguagem). O padrão consiste em duas peças que vivem juntas: (1) `loguru` configurado uma única vez no boot da aplicação (sinks, formato JSON, nível, integração com OpenTelemetry); (2) um decorator `@logged` que envelopa funções e métodos e emite, automaticamente, eventos de entrada, saída, duração e exceção. Chamadas `logger.info` e equivalentes não aparecem no corpo das funções.

## Context

- **Domain:** logging operacional de serviços Python — APIs, workers, jobs e CLIs.
- **Target audience:** implementadores e agentes de IA que escrevem ou mantêm código Python (warrior-apollo).
- **Update trigger:** quando o formato de log evolui, quando novos campos de correlação são adotados, quando o decorator ganha capacidades novas (sampling, redação extra, eventos de domínio).

## Content

### Princípios

1. **Configuração centralizada:** `loguru` é configurado uma única vez no boot da aplicação. Nenhum outro arquivo redefine sinks, formato ou nível.
2. **Logging por decorator:** instrumentação vive na fronteira da função. O corpo da função é regra de negócio, não trilha de auditoria.
3. **Estrutura JSON:** logs são consumidos por máquinas (CloudWatch, Datadog, ELK). Texto livre é complemento, não chave.
4. **Correlação obrigatória:** `trace_id`, `span_id` e `correlation_id` são propagados via `loguru.contextualize` e injetados em cada registro.
5. **Redação na fronteira:** o decorator aplica allowlist/denylist de campos antes de serializar argumentos; PII e segredos nunca chegam ao sink.
6. **Sucesso é evento, não silêncio:** toda execução de função decorada emite ao menos `enter` e `exit` (ou `error`); falhas são logadas com `exception` e re-lançadas.

### Stack

| Componente | Biblioteca | Propósito |
|------------|-----------|-----------|
| Logger | `loguru` | API única de logging; sinks, formatação, captura de exceção |
| Decorator | `app.shared.logging.decorator` (interno) | Instrumentação de entrada/saída/erro com redação |
| Correlação | `loguru.contextualize` + `opentelemetry-instrumentation-logging` | Propaga `trace_id`, `span_id`, `correlation_id` |
| Serialização | `orjson` (opcional) | Sink JSON rápido para produção |

`logging` (stdlib), `structlog` e `print` não fazem parte do stack permitido em código de aplicação.

### Configuração de Boot

```python
# app/shared/logging/setup.py
import sys
from loguru import logger

from app.shared.logging.serializer import json_sink


def setup_logging(service_name: str, level: str = "INFO") -> None:
    logger.remove()
    logger.configure(extra={"service": service_name})
    logger.add(
        sys.stdout,
        level=level,
        serialize=False,
        backtrace=False,
        diagnose=False,
        format=(
            "<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green> "
            "<level>{level: <8}</level> "
            "trace_id={extra[trace_id]} "
            "{message}"
        ),
        filter=lambda record: record["extra"].setdefault("trace_id", "-") or True,
    )
    logger.add(json_sink, level=level)
```

**Regras:**

- `setup_logging` é chamada uma vez no entrypoint (`main.py`, `app.py`, `lambda_handler.py`).
- `backtrace=False` e `diagnose=False` em produção: tracebacks de `loguru` podem expor variáveis com PII.
- O sink de stdout serve dev local; o sink JSON (`json_sink`) é o canal real em produção.
- Nível default `INFO`; `DEBUG` apenas via variável de ambiente em ambientes não-prod.

### Sink JSON

```python
# app/shared/logging/serializer.py
import orjson

REDACTED = "[REDACTED]"
DENY = {"password", "token", "secret", "api_key", "authorization", "cookie", "cpf", "ssn"}


def _redact(payload: dict) -> dict:
    return {k: (REDACTED if k.lower() in DENY else v) for k, v in payload.items()}


def json_sink(message) -> None:
    record = message.record
    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "service": record["extra"].get("service", "unknown"),
        "logger": record["name"],
        "message": record["message"],
        "trace_id": record["extra"].get("trace_id"),
        "span_id": record["extra"].get("span_id"),
        "correlation_id": record["extra"].get("correlation_id"),
        "operation": record["extra"].get("operation"),
        "outcome": record["extra"].get("outcome"),
        "duration_ms": record["extra"].get("duration_ms"),
        "args": _redact(record["extra"].get("args", {})),
    }
    if record["exception"] is not None:
        payload["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
        }
    print(orjson.dumps(payload).decode())
```

**Regras:**

- Redação aplicada antes da serialização. Allowlist de campos seguros é definida pelo time; o que não está na allowlist é tratado como sensível por padrão para campos com nomes em `DENY`.
- Nada de tracebacks completos no JSON: apenas tipo e mensagem; o traceback completo vai para o trace via `span.record_exception`.
- `print` aparece **apenas** dentro deste sink — é a fronteira de saída do logger, não logging de aplicação.

### Decorator

```python
# app/shared/logging/decorator.py
import asyncio
import functools
import time
from typing import Any, Callable, ParamSpec, TypeVar

from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")


def logged(
    operation: str,
    *,
    level: str = "INFO",
    capture_args: bool = True,
    redact: tuple[str, ...] = (),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                bound = _bound_args(fn, args, kwargs, capture_args, redact)
                start = time.perf_counter()
                with logger.contextualize(operation=operation, args=bound, outcome="enter"):
                    logger.log(level, "{} enter", operation)
                try:
                    result = await fn(*args, **kwargs)
                except Exception:
                    duration_ms = (time.perf_counter() - start) * 1000
                    with logger.contextualize(
                        operation=operation, args=bound, outcome="error", duration_ms=duration_ms
                    ):
                        logger.opt(exception=True).error("{} error", operation)
                    raise
                duration_ms = (time.perf_counter() - start) * 1000
                with logger.contextualize(
                    operation=operation, args=bound, outcome="exit", duration_ms=duration_ms
                ):
                    logger.log(level, "{} exit", operation)
                return result

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = _bound_args(fn, args, kwargs, capture_args, redact)
            start = time.perf_counter()
            with logger.contextualize(operation=operation, args=bound, outcome="enter"):
                logger.log(level, "{} enter", operation)
            try:
                result = fn(*args, **kwargs)
            except Exception:
                duration_ms = (time.perf_counter() - start) * 1000
                with logger.contextualize(
                    operation=operation, args=bound, outcome="error", duration_ms=duration_ms
                ):
                    logger.opt(exception=True).error("{} error", operation)
                raise
            duration_ms = (time.perf_counter() - start) * 1000
            with logger.contextualize(
                operation=operation, args=bound, outcome="exit", duration_ms=duration_ms
            ):
                logger.log(level, "{} exit", operation)
            return result

        return sync_wrapper

    return decorator


def _bound_args(fn: Callable[..., Any], args: tuple, kwargs: dict, capture: bool, redact: tuple[str, ...]) -> dict:
    if not capture:
        return {}
    import inspect

    sig = inspect.signature(fn)
    try:
        bound = sig.bind_partial(*args, **kwargs)
    except TypeError:
        return {}
    raw = dict(bound.arguments)
    raw.pop("self", None)
    raw.pop("cls", None)
    return {k: ("[REDACTED]" if k in redact else _safe(v)) for k, v in raw.items()}


def _safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return repr(value)[:200]
```

**Regras:**

- O decorator suporta funções síncronas e assíncronas. Nunca duas versões manuais — `@logged` decide.
- `operation` é obrigatório e usa o formato `domain.action` (ex.: `transfer.create`, `reconciliation.run`).
- `capture_args=True` por padrão; `False` em fronteiras com input não-confiável (ex.: webhook payload).
- `redact=("password", "card_number", ...)` aplica redação por nome de argumento, complementando a denylist global do sink.
- O decorator NÃO engole exceções: loga `error` e re-lança. Tratamento de erro é responsabilidade do handler global (lex-python-error-handling).

### Uso

```python
# app/application/transfers/use_cases.py
from uuid import UUID

from app.application.transfers.ports import TransferRepository
from app.shared.logging import logged


class CreateTransferUseCase:
    def __init__(self, repository: TransferRepository) -> None:
        self._repository = repository

    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

```python
# app/infrastructure/http/routers/transfers.py
from fastapi import APIRouter, Depends

from app.application.transfers.use_cases import CreateTransferUseCase
from app.infrastructure.http.schemas import CreateTransferRequest, TransferResponse
from app.shared.logging import logged

router = APIRouter()


@router.post("/transfers", response_model=TransferResponse)
@logged(operation="http.transfer.create", capture_args=False)
async def create_transfer(
    payload: CreateTransferRequest,
    use_case: CreateTransferUseCase = Depends(),
) -> TransferResponse:
    entity_id = await use_case.execute(payload.source_id, payload.target_id, payload.amount)
    return TransferResponse(entity_id=entity_id)
```

### Correlação trace ↔ log

`opentelemetry-instrumentation-logging` injeta `otelTraceID` e `otelSpanID` em cada record. Um middleware do FastAPI propaga o `correlation_id` por request:

```python
# app/infrastructure/http/middleware/correlation.py
from uuid import uuid4

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("x-correlation-id") or str(uuid4())
        with logger.contextualize(correlation_id=correlation_id):
            response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        return response
```

Cada record carrega `correlation_id` automaticamente — o decorator não precisa propagar à mão.

### Níveis e quando usar

| Nível | Quando emitir | Quem emite |
|-------|---------------|------------|
| `DEBUG` | Apenas em desenvolvimento; instrumentação detalhada de algoritmos | Decorator quando `level="DEBUG"` |
| `INFO` | Eventos operacionais relevantes (entrada/saída de caso de uso, request HTTP atendido) | Decorator (default) |
| `WARNING` | Comportamento degradado recuperável (retry, fallback, circuit aberto) | Decorator com `level="WARNING"` em fronteiras de retry |
| `ERROR` | Exceção não tratada que aborta a operação | Decorator (automático em `except`) |
| `CRITICAL` | Falha que afeta o serviço inteiro (DB indisponível, dependência crítica fora) | Handler global no entrypoint |

`SUCCESS` e `TRACE` (do loguru) não são usados.

### Onde `logger` aparece diretamente (exceções permitidas)

A regra inviolável (lex-logging-decorator) lista três casos. Eles ficam fisicamente em três módulos previsíveis:

| Módulo | Papel |
|--------|-------|
| `app/shared/logging/setup.py` | Configura o `loguru` no boot |
| `app/shared/logging/decorator.py` | Implementa `@logged` |
| `app/infrastructure/http/exception_handlers.py` (ou equivalente em workers/Lambda) | Loga exceções não capturadas no topo |

Qualquer outro arquivo que importe `from loguru import logger` para chamar `logger.<level>` é violação.

### Padrões e convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Formato de `operation` | `domain.action` em snake_case | `transfer.create`, `ledger.post_entry` |
| Estrutura JSON | snake_case em todas as chaves | `trace_id`, `correlation_id`, `duration_ms` |
| Captura de argumentos | Habilitada por padrão; desabilitada em fronteiras com payload livre | `capture_args=False` no router HTTP |
| Redação | Por nome de campo (sink global) e por argumento (decorator) | `redact=("password", "card_number")` |
| Re-lançamento de exceções | Sempre | Decorator nunca engole |

## Glossary

| Termo | Definição |
|-------|-----------|
| Sink | Destino do log no `loguru` (stdout, arquivo, função custom) |
| Operation | Identificador estável do evento de log; chave para busca e dashboards |
| Outcome | Status do evento: `enter`, `exit`, `error` |
| Redação | Substituição de valores sensíveis por `[REDACTED]` antes da serialização |
| Correlation ID | UUID por request, propagado em logs e em response headers |

## References

- [Loguru documentation](https://loguru.readthedocs.io/)
- [orjson](https://github.com/ijl/orjson) — serializador JSON usado no sink
- lex-logging-decorator (_foundation/quality) — lei agnóstica de linguagem que torna o padrão obrigatório
- kata-python-logging-setup (engineering/backend) — procedimento de configuração
- codex-python-observability (engineering/backend) — traces e métricas via OpenTelemetry
- lex-python-security (engineering/backend) — proibição de logar segredos e PII
- lex-python-error-handling (engineering/backend) — exceções e re-raise
