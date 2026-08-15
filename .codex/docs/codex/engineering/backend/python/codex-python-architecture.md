# Codex: Arquitetura de Aplicações Python

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: padrões de arquitetura para aplicações Python

## Content

### Layer Structure

```
src/<service_name>/
├── domain/                  # Lógica de negócio pura — sem imports de framework
│   ├── entities/            # Entidades de domínio (frozen dataclasses)
│   ├── value_objects/       # Tipos de valor imutáveis
│   ├── exceptions/          # Exceções específicas do domínio
│   ├── ports/               # Interfaces abstratas (classes Protocol)
│   │   ├── repositories/    # Protocolos de repositório
│   │   └── services/        # Protocolos de serviços externos
│   └── use_cases/           # Casos de uso da aplicação (orquestração)
├── infrastructure/          # Implementações de framework e I/O
│   ├── database/            # Modelos SQLAlchemy, repositórios, migrações
│   │   ├── models/          # Classes mapeadas pelo ORM
│   │   ├── repositories/    # Implementações de repositório
│   │   └── migrations/      # Migrações Alembic
│   ├── http/                # Routers FastAPI, dependências, middleware
│   │   ├── routers/         # Definições de rotas
│   │   ├── dependencies/    # Factories de Depends do FastAPI
│   │   ├── middleware/       # Middleware HTTP
│   │   └── schemas/         # Modelos Pydantic de request/response
│   ├── clients/             # Clientes HTTP/gRPC externos
│   ├── events/              # Publishers/consumers de eventos
│   └── config/              # Configurações, ambiente, wiring de DI
├── shared/                  # Utilitários transversais (logging, telemetria)
└── main.py                  # Ponto de entrada da aplicação
```

### Dependency Direction

```
infrastructure → domain ← (nada)
     │               │
     ▼               ▼
  frameworks     Python puro
  (FastAPI,      (dataclasses,
   SQLAlchemy,    Protocol,
   Pydantic)      exceptions)
```

**Regras:**
- `domain/` NÃO DEVE importar de `infrastructure/` ou de qualquer framework
- `infrastructure/` implementa as interfaces de `domain/ports/`
- `use_cases/` dependem apenas de ports (Protocol), nunca de implementações concretas
- A injeção de dependências conecta implementações concretas na composition root (`config/` ou `main.py`)

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

- DEVEM ser frozen dataclasses (lex-python-immutability)
- NÃO DEVEM conter I/O ou código específico de framework
- Mudanças de estado retornam novas instâncias

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

- DEVEM usar `typing.Protocol` (subtipagem estrutural)
- NÃO DEVEM importar tipos de infraestrutura
- Definem o contrato que a infraestrutura implementa

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

- Orquestram a lógica de domínio; um caso de uso por operação de negócio
- Recebem dependências via construtor (injeção de dependências)
- NÃO DEVEM importar FastAPI, SQLAlchemy ou outra infraestrutura

### Infrastructure Layer Patterns

#### Repository Implementations

- Implementam os protocolos de `domain/ports/repositories/`
- Usam sessão async do SQLAlchemy 2.0
- Mapeiam entre modelos ORM e entidades de domínio
- Veja codex-python-sqlalchemy para detalhes

#### HTTP Layer

- Routers FastAPI chamam casos de uso, nunca repositórios diretamente
- Schemas Pydantic para validação de request e serialização de response
- Veja codex-python-fastapi para detalhes

### Quando NÃO Abstrair

- NÃO criar um port/interface para algo com apenas uma implementação e sem necessidade de teste
- NÃO criar uma classe de caso de uso para CRUD simples sem lógica de negócio — uma função de serviço direta é aceitável
- NÃO adicionar camadas "para extensibilidade futura" — adicione quando o segundo caso de uso chegar
- Três linhas de código similares são melhores do que uma abstração prematura
