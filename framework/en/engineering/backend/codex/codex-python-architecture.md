# Codex: Python Application Architecture

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: architecture patterns for Python applications

## Overview

This manual defines the architecture patterns for Python backend applications. The goal is to ensure consistent structure across services, clear separation of concerns, testability at every layer, and a codebase that scales with the team without accumulating accidental complexity.

The architecture follows **Clean Architecture** (Hexagonal / Ports & Adapters) principles: domain logic is independent of frameworks, databases, and transport mechanisms. Dependencies point inward — infrastructure depends on domain, never the reverse.

## Context

- **Domain:** Python backend applications using FastAPI, SQLAlchemy, Pydantic.
- **Target audience:** implementers, architects, and AI agents that build or maintain Python services.
- **Update trigger:** when architectural patterns evolve or new infrastructure patterns are adopted.

## Content

### Layer Structure

```
src/<service_name>/
├── domain/                  # Pure business logic — no framework imports
│   ├── entities/            # Domain entities (frozen dataclasses)
│   ├── value_objects/       # Immutable value types
│   ├── exceptions/          # Domain-specific exceptions
│   ├── ports/               # Abstract interfaces (Protocol classes)
│   │   ├── repositories/    # Repository protocols
│   │   └── services/        # External service protocols
│   └── use_cases/           # Application use cases (orchestration)
├── infrastructure/          # Framework and I/O implementations
│   ├── database/            # SQLAlchemy models, repositories, migrations
│   │   ├── models/          # ORM mapped classes
│   │   ├── repositories/    # Repository implementations
│   │   └── migrations/      # Alembic migrations
│   ├── http/                # FastAPI routers, dependencies, middleware
│   │   ├── routers/         # Route definitions
│   │   ├── dependencies/    # FastAPI Depends factories
│   │   ├── middleware/       # HTTP middleware
│   │   └── schemas/         # Pydantic request/response models
│   ├── clients/             # External HTTP/gRPC clients
│   ├── events/              # Event publishers/consumers
│   └── config/              # Settings, environment, DI wiring
├── shared/                  # Cross-cutting utilities (logging, telemetry)
└── main.py                  # Application entry point
```

### Dependency Direction

```
infrastructure → domain ← (nothing)
     │               │
     ▼               ▼
  frameworks     pure Python
  (FastAPI,      (dataclasses,
   SQLAlchemy,    Protocol,
   Pydantic)      exceptions)
```

**Rules:**
- `domain/` MUST NOT import from `infrastructure/` or any framework
- `infrastructure/` implements `domain/ports/` interfaces
- `use_cases/` depend only on ports (Protocol), never on concrete implementations
- Dependency injection wires concrete implementations at the composition root (`config/` or `main.py`)

### Domain Layer Patterns

#### Entities

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Transaction:
    entity_id: UUID
    amount: int
    currency: str
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime
    version: int
```

- MUST be frozen dataclasses (lex-python-immutability)
- MUST NOT contain I/O or framework-specific code
- State changes return new instances

#### Ports (Interfaces)

```python
from typing import Protocol

class TransactionRepository(Protocol):
    async def save(self, transaction: Transaction) -> None: ...
    async def get_by_id(self, entity_id: UUID) -> Transaction | None: ...
    async def list_by_status(
        self, status: TransactionStatus, limit: int, cursor: str | None
    ) -> list[Transaction]: ...
```

- MUST use `typing.Protocol` (structural subtyping)
- MUST NOT import infrastructure types
- Define the contract that infrastructure implements

#### Use Cases

```python
class CreateTransactionUseCase:
    def __init__(
        self,
        repository: TransactionRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher

    async def execute(self, command: CreateTransactionCommand) -> Transaction:
        transaction = Transaction(
            entity_id=uuid7(),
            amount=command.amount,
            currency=command.currency,
            status=TransactionStatus.PENDING,
            created_at=now_utc(),
            updated_at=now_utc(),
            version=1,
        )
        await self._repository.save(transaction)
        await self._event_publisher.publish(
            TransactionCreatedEvent(transaction=transaction)
        )
        return transaction
```

- Orchestrate domain logic; one use case per business operation
- Receive dependencies via constructor (dependency injection)
- MUST NOT import FastAPI, SQLAlchemy, or other infrastructure

### Infrastructure Layer Patterns

#### Repository Implementations

- Implement `domain/ports/repositories/` protocols
- Use SQLAlchemy 2.0 async session
- Map between ORM models and domain entities
- See codex-python-sqlalchemy for details

#### HTTP Layer

- FastAPI routers call use cases, never repositories directly
- Pydantic schemas for request validation and response serialization
- See codex-python-fastapi for details

### When NOT to Abstract

- Do NOT create a port/interface for something with only one implementation and no testing need
- Do NOT create a use case class for simple CRUD with no business logic — a direct service function is acceptable
- Do NOT add layers "for future extensibility" — add them when the second use case arrives
- Three similar lines of code are better than a premature abstraction

## Glossary

| Term | Definition |
|------|------------|
| Port | Abstract interface (Protocol) defining a contract between layers |
| Adapter | Concrete implementation of a port (e.g., SQLAlchemy repository) |
| Use Case | Application-level orchestration of domain operations |
| Composition Root | Where concrete implementations are wired to ports (DI) |

## References

- [Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [typing.Protocol — PEP 544](https://peps.python.org/pep-0544/)
- lex-python-typing, lex-python-immutability (engineering/backend)
- codex-python-fastapi, codex-python-sqlalchemy (engineering/backend)
