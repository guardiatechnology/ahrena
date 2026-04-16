# Codex: Padrões FastAPI

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: padrões de aplicação FastAPI

## Overview

Este manual define os padrões para construção de aplicações FastAPI. O FastAPI é a camada de transporte HTTP — recebe requests, valida entradas, delega para casos de uso e serializa responses. NÃO DEVE conter lógica de negócio.

## Context

- **Domain:** camada HTTP FastAPI dentro de Clean Architecture.
- **Target audience:** implementadores e agentes de IA que constroem endpoints FastAPI.
- **Update trigger:** quando os padrões FastAPI evoluem ou novo middleware é adotado.

## Content

### Router Structure

```python
from fastapi import APIRouter, Depends, status
from uuid import UUID

router = APIRouter(prefix="/v1/transactions", tags=["transactions"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: CreateTransactionRequest,
    use_case: CreateTransactionUseCase = Depends(get_create_transaction_use_case),
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> TransactionResponse:
    transaction = await use_case.execute(
        CreateTransactionCommand(
            amount=request.amount,
            currency=request.currency,
            idempotency_key=idempotency_key,
        )
    )
    return TransactionResponse.from_domain(transaction)
```

**Regras:**
- Routers são enxutos — validar, delegar, serializar
- Um arquivo de router por recurso ou bounded context
- Usar `Depends()` para injeção de dependências de casos de uso e serviços
- Nunca instanciar repositórios ou sessões de BD diretamente em funções de rota

### Pydantic Schemas

```python
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class CreateTransactionRequest(BaseModel):
    """Request body — valida entrada externa."""
    amount: int = Field(gt=0, le=999_999_999)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class TransactionResponse(BaseModel):
    """Response body — serializa entidade de domínio."""
    model_config = ConfigDict(frozen=True)

    entity_id: UUID
    amount: int
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, entity: Transaction) -> "TransactionResponse":
        return cls(
            entity_id=entity.entity_id,
            amount=entity.amount,
            currency=entity.currency,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
```

**Regras:**
- Modelos de request validam entrada na fronteira (lex-python-security)
- Modelos de response são frozen (lex-python-immutability)
- Usar métodos de classe `from_domain()` para mapear de entidades de domínio — sem modelos ORM nas responses
- Schemas de request e response ficam em `infrastructure/http/schemas/`

### Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


def get_transaction_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TransactionRepository:
    return SqlAlchemyTransactionRepository(session)


def get_create_transaction_use_case(
    repo: TransactionRepository = Depends(get_transaction_repository),
    publisher: EventPublisher = Depends(get_event_publisher),
) -> CreateTransactionUseCase:
    return CreateTransactionUseCase(repository=repo, event_publisher=publisher)
```

**Regras:**
- Encadear `Depends()` para compor o grafo de dependências
- Sessão de BD tem escopo no ciclo de vida do request via `yield`
- Factories de caso de uso conectam ports a implementações concretas

### Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "errors": [
                {
                    "code": exc.error_code,
                    "reason": exc.reason,
                    "message": exc.message,
                }
            ]
        },
    )
```

**Regras:**
- Mapear exceções de domínio para responses HTTP em exception handlers
- Nunca lançar `HTTPException` da camada de domínio ou caso de uso
- A estrutura de response de erro segue codex-error-handling quando aplicável
- Nunca expor detalhes internos (stack traces, SQL, credenciais) nas responses

### Middleware

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Instrumentar em main.py
FastAPIInstrumentor.instrument_app(app)
```

- Auto-instrumentação OpenTelemetry para tracing (veja codex-python-observability)
- Middleware customizado para propagação de request ID, contexto de logging

### Application Factory

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Service Name", version="1.0.0")
    app.include_router(transaction_router)
    app.include_router(health_router)
    register_exception_handlers(app)
    setup_telemetry(app)
    return app
```

- Usar o padrão de application factory para testabilidade
- Registrar routers, exception handlers e middleware em um só lugar
- Testável: criar instância da app com dependências de teste

## Glossary

| Termo | Definição |
|-------|-----------|
| Router | `APIRouter` do FastAPI agrupando endpoints relacionados |
| Depends | Mecanismo de injeção de dependências do FastAPI |
| Schema | Modelo Pydantic para serialização de request/response |

## References

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 documentation](https://docs.pydantic.dev/latest/)
- lex-python-security, lex-python-typing (engineering/backend)
- codex-python-architecture (engineering/backend)
