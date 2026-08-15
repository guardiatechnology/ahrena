# Codex: Patrones de SQLAlchemy y Base de Datos

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: patrones async de SQLAlchemy 2.0, implementación del repositorio y migraciones con Alembic

## Overview

Este manual define los patrones para acceso a base de datos usando la API async de SQLAlchemy 2.0 con asyncpg, el patrón repositorio para abstracción de acceso a datos, y Alembic para migraciones de esquema. La capa de base de datos es infraestructura — implementa puertos de dominio y NO DEBE filtrar preocupaciones ORM hacia la lógica de dominio.

## Context

- **Domain:** capa de acceso a base de datos dentro de Clean Architecture.
- **Target audience:** implementadores y agentes de IA que construyen repositorios de base de datos y migraciones.
- **Update trigger:** cuando los patrones de SQLAlchemy evolucionan o se adoptan nuevos patrones de base de datos.

## Content

### ORM Model Definition

```python
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from uuid import UUID


class Base(DeclarativeBase):
    pass


class TransactionModel(Base):
    __tablename__ = "transactions"

    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50), default="transaction")
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    discarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
```

**Reglas:**
- Usar anotaciones de tipo `Mapped` de SQLAlchemy 2.0 para todas las columnas
- Los modelos ORM viven en `infrastructure/database/models/`
- Los modelos ORM NO son entidades de dominio — son representaciones de persistencia
- Usar tipos específicos de PostgreSQL (PG_UUID, JSONB) cuando corresponda

### Async Session Factory

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

**Reglas:**
- Usar el driver `asyncpg` para soporte async de PostgreSQL
- `expire_on_commit=False` para evitar problemas de lazy loading en contexto async
- `pool_pre_ping=True` para detectar conexiones obsoletas
- Cadena de conexión desde variables de entorno (lex-python-security)

### Repository Implementation

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, transaction: Transaction) -> None:
        model = self._to_model(transaction)
        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, entity_id: UUID) -> Transaction | None:
        stmt = select(TransactionModel).where(
            TransactionModel.entity_id == entity_id,
            TransactionModel.discarded_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_status(
        self,
        status: TransactionStatus,
        limit: int,
        cursor: UUID | None,
    ) -> list[Transaction]:
        stmt = select(TransactionModel).where(
            TransactionModel.status == status.value,
            TransactionModel.discarded_at.is_(None),
        )
        if cursor:
            stmt = stmt.where(TransactionModel.entity_id > cursor)
        stmt = stmt.order_by(TransactionModel.entity_id).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars()]

    def _to_model(self, entity: Transaction) -> TransactionModel:
        return TransactionModel(
            entity_id=entity.entity_id,
            amount=entity.amount,
            currency=entity.currency,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            version=entity.version,
        )

    def _to_domain(self, model: TransactionModel) -> Transaction:
        return Transaction(
            entity_id=model.entity_id,
            amount=model.amount,
            currency=model.currency,
            status=TransactionStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
        )
```

**Reglas:**
- El repositorio implementa el Protocol de dominio (puerto)
- Mapea entre modelo ORM y entidad de dominio mediante métodos privados
- Usa `flush()` en lugar de `commit()` — la gestión de transacciones ocurre a nivel de caso de uso
- Solo consultas parametrizadas — nunca interpolación de strings (lex-python-security)
- Paginación basada en cursor para operaciones de lista

### Alembic Migrations

```
alembic/
├── env.py
├── versions/
│   ├── 001_create_transactions.py
│   └── 002_add_status_index.py
└── alembic.ini
```

**Reglas:**
- Una migración por cambio lógico de esquema
- Nombres descriptivos de migración: `{number}_{description}.py`
- Siempre proveer funciones `upgrade()` y `downgrade()`
- Probar migraciones contra una base de datos real (no SQLite) en CI
- Las migraciones destructivas (drop column, drop table) requieren revisión humana
- Nunca auto-generar migraciones a ciegas — revisar el SQL generado

### Transaction Management

```python
async def create_transaction_handler(
    session: AsyncSession,
    use_case: CreateTransactionUseCase,
    command: CreateTransactionCommand,
) -> Transaction:
    async with session.begin():
        return await use_case.execute(command)
```

**Reglas:**
- Límites de transacción a nivel del caso de uso / request handler
- Los repositorios usan `flush()`, no `commit()`
- El ciclo de vida de la sesión es gestionado por la dependencia de FastAPI (ver codex-python-fastapi)
- El context manager `session.begin()` gestiona commit/rollback

## Glossary

| Término | Definición |
|---------|-----------|
| ORM Model | Clase mapeada de SQLAlchemy que representa una tabla de base de datos |
| Repository | Abstracción de acceso a datos que implementa un puerto de dominio |
| Migration | Script de versión de Alembic para cambios de esquema |
| Flush | Escribir cambios pendientes en la BD sin confirmar la transacción |

## References

- [SQLAlchemy 2.0 documentation](https://docs.sqlalchemy.org/en/20/)
- [asyncpg documentation](https://magicstack.github.io/asyncpg/)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- lex-python-security, lex-python-typing (engineering/backend)
- codex-python-architecture (engineering/backend)
