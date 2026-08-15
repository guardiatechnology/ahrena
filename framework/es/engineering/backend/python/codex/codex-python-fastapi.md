# Codex: Patrones FastAPI

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: patrones de aplicación FastAPI

## Visión General

Este manual define los patrones para construir aplicaciones FastAPI. FastAPI es la capa de transporte HTTP — recibe requests, valida entradas, delega a casos de uso y serializa responses. NO DEBE contener lógica de negocio.

## Contexto

- **Dominio:** capa HTTP FastAPI dentro de Clean Architecture.
- **Audiencia objetivo:** implementadores y agentes de IA que construyen endpoints FastAPI.
- **Disparador de actualización:** cuando los patrones FastAPI evolucionan o se adopta nuevo middleware.

## Contenido

### Estructura de Router

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

**Reglas:**
- Los routers son delgados — validar, delegar, serializar
- Un archivo de router por recurso o contexto delimitado
- Usar `Depends()` para inyección de dependencias de casos de uso y servicios
- Nunca instanciar repositorios ni sesiones de BD directamente en funciones de ruta

### Schemas Pydantic

```python
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class CreateTransactionRequest(BaseModel):
    """Cuerpo del request — valida entrada externa."""
    amount: int = Field(gt=0, le=999_999_999)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class TransactionResponse(BaseModel):
    """Cuerpo del response — serializa entidad de dominio."""
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

**Reglas:**
- Los modelos de request validan la entrada en el límite (lex-python-security)
- Los modelos de response son frozen (lex-python-immutability)
- Usar métodos de clase `from_domain()` para mapear desde entidades de dominio — sin modelos ORM en responses
- Los schemas de request y response viven en `infrastructure/http/schemas/`

### Inyección de Dependencias

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

**Reglas:**
- Encadenar `Depends()` para componer el grafo de dependencias
- La sesión de BD tiene alcance al ciclo de vida del request mediante `yield`
- Las fábricas de casos de uso conectan puertos con implementaciones concretas

### Manejo de Errores

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

**Reglas:**
- Mapear excepciones de dominio a responses HTTP en los manejadores de excepciones
- Nunca lanzar `HTTPException` desde la capa de dominio o de casos de uso
- La estructura de response de error sigue codex-error-handling cuando aplica
- Nunca exponer detalles internos (stack traces, SQL, credenciales) en los responses

### Middleware

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Instrumentar en main.py
FastAPIInstrumentor.instrument_app(app)
```

- Auto-instrumentación OpenTelemetry para trazabilidad (ver codex-python-observability)
- Middleware personalizado para propagación de ID de request, contexto de logging

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

- Usar patrón de fábrica de aplicación para testeabilidad
- Registrar routers, manejadores de excepciones y middleware en un solo lugar
- Testeable: crear instancia de la app con dependencias de test

## Glosario

| Término | Definición |
|---------|------------|
| Router | `APIRouter` de FastAPI que agrupa endpoints relacionados |
| Depends | Mecanismo de inyección de dependencias de FastAPI |
| Schema | Modelo Pydantic para serialización de request/response |

## Referencias

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Pydantic V2](https://docs.pydantic.dev/latest/)
- lex-python-security, lex-python-typing (engineering/backend)
- codex-python-architecture (engineering/backend)
