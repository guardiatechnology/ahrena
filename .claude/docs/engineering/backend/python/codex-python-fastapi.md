# Codex: FastAPI Patterns

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: FastAPI application patterns

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

**Rules:**
- Routers are thin — validate, delegate, serialize
- One router file per resource or bounded context
- Use `Depends()` for dependency injection of use cases and services
- Never instantiate repositories or DB sessions directly in route functions

### Pydantic Schemas

```python
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID

class CreateTransactionRequest(BaseModel):
    """Request body — validates external input."""
    amount: int = Field(gt=0, le=999_999_999)
    currency: str = Field(pattern=r"^[A-Z]{3}$")

class TransactionResponse(BaseModel):
    """Response body — serializes domain entity."""
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

**Rules:**
- Request models validate input at the boundary (lex-python-security)
- Response models are frozen (lex-python-immutability)
- Use `from_domain()` class methods to map from domain entities — no ORM models in responses
- Request and response schemas live in `infrastructure/http/schemas/`

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

**Rules:**
- Chain `Depends()` to compose the dependency graph
- DB session is scoped to the request lifecycle via `yield`
- Use case factories wire ports to concrete implementations

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

**Rules:**
- Map domain exceptions to HTTP responses in exception handlers
- Never raise `HTTPException` from domain or use case layer
- Error response structure follows codex-error-handling when applicable
- Never expose internal details (stack traces, SQL, credentials) in responses

### Middleware

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Instrument in main.py
FastAPIInstrumentor.instrument_app(app)
```

- OpenTelemetry auto-instrumentation for tracing (see codex-python-observability)
- Custom middleware for request ID propagation, logging context

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

- Use application factory pattern for testability
- Register routers, exception handlers, and middleware in one place
- Testable: create app instance with test dependencies
