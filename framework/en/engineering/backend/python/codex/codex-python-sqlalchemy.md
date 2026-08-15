# Codex: SQLAlchemy & Database Patterns

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: SQLAlchemy 2.0 async patterns, repository implementation, and Alembic migrations

## Overview

This manual defines the patterns for database access using SQLAlchemy 2.0 async API with asyncpg, the repository pattern for data access abstraction, and Alembic for schema migrations. The database layer is infrastructure — it implements domain ports and MUST NOT leak ORM concerns into domain logic.

## Context

- **Domain:** database access layer within Clean Architecture.
- **Target audience:** implementers and AI agents building database repositories and migrations.
- **Update trigger:** when SQLAlchemy patterns evolve or new database patterns are adopted.

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

**Rules:**
- Use SQLAlchemy 2.0 `Mapped` type annotations for all columns
- ORM models live in `infrastructure/database/models/`
- ORM models are NOT domain entities — they are persistence representations
- Use PostgreSQL-specific types (PG_UUID, JSONB) when appropriate

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

**Rules:**
- Use `asyncpg` driver for PostgreSQL async support
- `expire_on_commit=False` to avoid lazy loading issues in async context
- `pool_pre_ping=True` to detect stale connections
- Connection string from environment variables (lex-python-security)

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

**Rules:**
- Repository implements the domain Protocol (port)
- Maps between ORM model and domain entity via private methods
- Uses `flush()` instead of `commit()` — transaction management at use case level
- Parameterized queries only — never string interpolation (lex-python-security)
- Cursor-based pagination for list operations

### Alembic Migrations

```
alembic/
├── env.py
├── versions/
│   ├── 001_create_transactions.py
│   └── 002_add_status_index.py
└── alembic.ini
```

**Rules:**
- One migration per logical schema change
- Descriptive migration names: `{number}_{description}.py`
- Always provide `upgrade()` and `downgrade()` functions
- Test migrations against a real database (not SQLite) in CI
- Destructive migrations (drop column, drop table) require human review
- Never auto-generate migrations blindly — review the generated SQL

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

**Rules:**
- Transaction boundaries at the use case / request handler level
- Repositories use `flush()`, not `commit()`
- Session lifecycle managed by FastAPI dependency (see codex-python-fastapi)
- `session.begin()` context manager handles commit/rollback

## Glossary

| Term | Definition |
|------|------------|
| ORM Model | SQLAlchemy mapped class representing a database table |
| Repository | Data access abstraction implementing a domain port |
| Migration | Alembic version script for schema changes |
| Flush | Write pending changes to DB without committing the transaction |

## References

- [SQLAlchemy 2.0 documentation](https://docs.sqlalchemy.org/en/20/)
- [asyncpg documentation](https://magicstack.github.io/asyncpg/)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- lex-python-security, lex-python-typing (engineering/backend)
- codex-python-architecture (engineering/backend)
