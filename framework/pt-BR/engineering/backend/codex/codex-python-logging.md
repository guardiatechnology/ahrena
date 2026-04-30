# Codex: Logging Python com Loguru e Decorator

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: padrão de logging em aplicações Python

## Overview

Especialização Python da `lex-logging-decorator`. Aplicações usam `loguru` configurado uma vez no boot e um decorator `@logged` que envelopa funções e emite, automaticamente, eventos de entrada, saída, duração e exceção. Chamadas `logger.info` e equivalentes não aparecem no corpo das funções.

## Context

- **Domain:** logging operacional de serviços Python — APIs, workers, jobs e CLIs.
- **Target audience:** implementadores e agentes de IA que escrevem ou mantêm código Python (warrior-apollo).
- **Update trigger:** evolução de formato, novos campos de correlação, capacidades novas no decorator.

## Content

### Princípios

1. Configuração centralizada — `loguru` configurado uma única vez no boot.
2. Logging por decorator — instrumentação na fronteira; corpo da função é regra de negócio.
3. Estrutura JSON — logs consumidos por máquinas (CloudWatch, Datadog, ELK).
4. Correlação obrigatória — `trace_id`, `span_id`, `correlation_id` via `loguru.contextualize`.
5. Redação na fronteira — allowlist/denylist aplicada antes da serialização.
6. Sucesso é evento — toda execução decorada emite `enter`+`exit` (ou `error`); falhas são re-lançadas.

### Stack

| Componente | Biblioteca | Propósito |
|------------|-----------|-----------|
| Logger | `loguru` | API única; sinks, formatação, captura de exceção |
| Decorator | `app.shared.logging.decorator` | Instrumentação de entrada/saída/erro com redação |
| Correlação | `loguru.contextualize` + `opentelemetry-instrumentation-logging` | `trace_id`, `span_id`, `correlation_id` |
| Serialização | `orjson` | Sink JSON rápido para produção |

`logging` (stdlib), `structlog` e `print` não são permitidos em código de aplicação.

### Boot

```python
# app/shared/logging/setup.py
import sys
from loguru import logger
from app.shared.logging.serializer import json_sink


def setup_logging(service_name: str, level: str = "INFO") -> None:
    logger.remove()
    logger.configure(extra={"service": service_name})
    logger.add(sys.stdout, level=level, backtrace=False, diagnose=False,
               format="<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green> "
                      "<level>{level: <8}</level> trace_id={extra[trace_id]} {message}",
               filter=lambda r: r["extra"].setdefault("trace_id", "-") or True)
    logger.add(json_sink, level=level)
```

`backtrace=False` e `diagnose=False` em produção (tracebacks do `loguru` podem expor variáveis com PII). `setup_logging` é chamada uma vez no entrypoint.

### Sink JSON

```python
# app/shared/logging/serializer.py
import orjson

DENY = {"password", "token", "secret", "api_key", "authorization", "cookie", "cpf", "ssn"}


def _redact(d: dict) -> dict:
    return {k: ("[REDACTED]" if k.lower() in DENY else v) for k, v in d.items()}


def json_sink(message) -> None:
    r = message.record
    payload = {
        "timestamp": r["time"].isoformat(),
        "level": r["level"].name,
        "service": r["extra"].get("service", "unknown"),
        "logger": r["name"],
        "message": r["message"],
        "trace_id": r["extra"].get("trace_id"),
        "span_id": r["extra"].get("span_id"),
        "correlation_id": r["extra"].get("correlation_id"),
        "operation": r["extra"].get("operation"),
        "outcome": r["extra"].get("outcome"),
        "duration_ms": r["extra"].get("duration_ms"),
        "args": _redact(r["extra"].get("args", {})),
    }
    if r["exception"] is not None:
        payload["exception"] = {"type": r["exception"].type.__name__, "value": str(r["exception"].value)}
    print(orjson.dumps(payload).decode())
```

Apenas tipo + valor da exceção; o traceback completo vai ao trace via `span.record_exception`. `print` aqui é a fronteira de saída do logger, não logging de aplicação.

### Decorator

```python
# app/shared/logging/decorator.py
import asyncio, functools, inspect, time
from typing import Any, Callable, ParamSpec, TypeVar
from loguru import logger

P = ParamSpec("P"); R = TypeVar("R")


def logged(operation: str, *, level: str = "INFO",
           capture_args: bool = True, redact: tuple[str, ...] = ()) -> Callable:
    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        is_async = asyncio.iscoroutinefunction(fn)

        def _bound(args, kwargs) -> dict:
            if not capture_args:
                return {}
            try:
                b = inspect.signature(fn).bind_partial(*args, **kwargs)
            except TypeError:
                return {}
            raw = dict(b.arguments); raw.pop("self", None); raw.pop("cls", None)
            return {k: ("[REDACTED]" if k in redact else _safe(v)) for k, v in raw.items()}

        def _emit(outcome: str, args_dict: dict, duration_ms: float | None, exc: bool = False) -> None:
            ctx = {"operation": operation, "args": args_dict, "outcome": outcome}
            if duration_ms is not None:
                ctx["duration_ms"] = duration_ms
            with logger.contextualize(**ctx):
                if exc:
                    logger.opt(exception=True).error("{} error", operation)
                else:
                    logger.log(level if outcome != "error" else "ERROR", "{} {}", operation, outcome)

        @functools.wraps(fn)
        async def aw(*args: P.args, **kwargs: P.kwargs) -> R:
            bound, t0 = _bound(args, kwargs), time.perf_counter()
            _emit("enter", bound, None)
            try:
                result = await fn(*args, **kwargs)
            except Exception:
                _emit("error", bound, (time.perf_counter() - t0) * 1000, exc=True); raise
            _emit("exit", bound, (time.perf_counter() - t0) * 1000); return result

        @functools.wraps(fn)
        def sw(*args: P.args, **kwargs: P.kwargs) -> R:
            bound, t0 = _bound(args, kwargs), time.perf_counter()
            _emit("enter", bound, None)
            try:
                result = fn(*args, **kwargs)
            except Exception:
                _emit("error", bound, (time.perf_counter() - t0) * 1000, exc=True); raise
            _emit("exit", bound, (time.perf_counter() - t0) * 1000); return result

        return aw if is_async else sw  # type: ignore[return-value]
    return deco


def _safe(v: Any) -> Any:
    return v if isinstance(v, (str, int, float, bool, type(None))) else repr(v)[:200]
```

Suporta sync e async; `operation` é obrigatório no formato `domain.action`; `capture_args=False` em fronteiras com payload livre; `redact` complementa o denylist global do sink. O decorator não engole exceções — loga `error` e re-lança.

### Uso

```python
from app.shared.logging import logged


class CreateTransferUseCase:
    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

Em router HTTP, usar `capture_args=False` quando o payload pode conter dados livres não filtrados.

### Correlação trace ↔ log

`opentelemetry-instrumentation-logging` injeta `otelTraceID` e `otelSpanID` em cada record. Um middleware FastAPI propaga `correlation_id` por request:

```python
from uuid import uuid4
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cid = request.headers.get("x-correlation-id") or str(uuid4())
        with logger.contextualize(correlation_id=cid):
            response = await call_next(request)
        response.headers["x-correlation-id"] = cid
        return response
```

### Níveis

| Nível | Quando | Quem emite |
|-------|--------|------------|
| `DEBUG` | Apenas dev; instrumentação detalhada | Decorator com `level="DEBUG"` |
| `INFO` | Eventos operacionais (default) | Decorator |
| `WARNING` | Comportamento degradado recuperável (retry, fallback) | Decorator com `level="WARNING"` |
| `ERROR` | Exceção não tratada que aborta a operação | Decorator (automático em `except`) |
| `CRITICAL` | Falha que afeta o serviço inteiro | Handler global |

`SUCCESS` e `TRACE` (do loguru) não são usados.

### Onde `logger` aparece diretamente

A regra inviolável (`lex-logging-decorator`) lista três casos. Eles vivem em três módulos previsíveis:

| Módulo | Papel |
|--------|-------|
| `app/shared/logging/setup.py` | Configura `loguru` no boot |
| `app/shared/logging/decorator.py` | Implementa `@logged` |
| `app/infrastructure/http/exception_handlers.py` (ou worker/Lambda) | Loga exceções não capturadas no topo |

Qualquer outro arquivo que importe `from loguru import logger` para chamar `logger.<level>` é violação.

### Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| `operation` | `domain.action` em snake_case | `transfer.create`, `ledger.post_entry` |
| Chaves JSON | snake_case | `trace_id`, `correlation_id`, `duration_ms` |
| Captura de args | Default `True`; `False` em fronteiras com payload livre | `capture_args=False` em router HTTP |
| Redação | Por nome de campo (sink) e por argumento (decorator) | `redact=("password", "card_number")` |
| Re-raise | Sempre | Decorator nunca engole |

## Glossary

| Termo | Definição |
|-------|-----------|
| Sink | Destino do log no `loguru` |
| Operation | Identificador estável do evento; chave para busca e dashboards |
| Outcome | Status do evento: `enter`, `exit`, `error` |
| Redação | Substituição de valores sensíveis por `[REDACTED]` |
| Correlation ID | UUID por request, propagado em logs e response headers |

## References

- [Loguru](https://loguru.readthedocs.io/) — [orjson](https://github.com/ijl/orjson)
- lex-logging-decorator (_foundation/quality) — lei agnóstica de linguagem
- kata-python-logging-setup (engineering/backend) — procedimento de configuração
- codex-python-observability (engineering/backend) — traces e métricas
- lex-python-security, lex-python-error-handling (engineering/backend)
