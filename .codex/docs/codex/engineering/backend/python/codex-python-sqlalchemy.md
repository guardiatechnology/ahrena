# Codex: Padrões de SQLAlchemy e Banco de Dados

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: padrões async do SQLAlchemy 2.0, implementação de repositório e migrações Alembic

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

**Regras:**
- Usar anotações de tipo `Mapped` do SQLAlchemy 2.0 para todas as colunas
- Modelos ORM ficam em `infrastructure/database/models/`
- Modelos ORM NÃO são entidades de domínio — são representações de persistência
- Usar tipos específicos do PostgreSQL (PG_UUID, JSONB) quando apropriado

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

**Regras:**
- Usar driver `asyncpg` para suporte async ao PostgreSQL
- `expire_on_commit=False` para evitar problemas de lazy loading em contexto async
- `pool_pre_ping=True` para detectar conexões obsoletas
- String de conexão a partir de variáveis de ambiente (lex-python-security)

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

**Regras:**
- O repositório implementa o Protocol de domínio (port)
- Mapeia entre modelo ORM e entidade de domínio via métodos privados
- Usa `flush()` em vez de `commit()` — gerenciamento de transação no nível do caso de uso
- Somente queries parametrizadas — nunca interpolação de strings (lex-python-security)
- Paginação baseada em cursor para operações de lista

### Alembic Migrations

```
alembic/
├── env.py
├── versions/
│   ├── 001_create_transactions.py
│   └── 002_add_status_index.py
└── alembic.ini
```

**Regras:**
- Uma migração por mudança lógica de schema
- Nomes descritivos de migração: `{number}_{description}.py`
- Sempre fornecer funções `upgrade()` e `downgrade()`
- Testar migrações contra banco de dados real (não SQLite) em CI
- Migrações destrutivas (drop column, drop table) requerem revisão humana
- Nunca auto-gerar migrações às cegas — revisar o SQL gerado

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

**Regras:**
- Fronteiras de transação no nível do caso de uso / request handler
- Repositórios usam `flush()`, não `commit()`
- Ciclo de vida da sessão gerenciado pela dependência FastAPI (veja codex-python-fastapi)
- O context manager `session.begin()` gerencia commit/rollback
