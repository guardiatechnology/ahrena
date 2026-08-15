# Codex: Arquitectura de Aplicaciones Python

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: patrones de arquitectura para aplicaciones Python

## Visión General

Este manual define los patrones de arquitectura para aplicaciones Python de backend. El objetivo es garantizar una estructura consistente entre servicios, separación clara de responsabilidades, testeabilidad en cada capa, y una base de código que escale con el equipo sin acumular complejidad accidental.

La arquitectura sigue los principios de **Clean Architecture** (Hexagonal / Ports & Adapters): la lógica de dominio es independiente de frameworks, bases de datos y mecanismos de transporte. Las dependencias apuntan hacia adentro — la infraestructura depende del dominio, nunca al revés.

## Contexto

- **Dominio:** aplicaciones Python de backend usando FastAPI, SQLAlchemy, Pydantic.
- **Audiencia objetivo:** implementadores, arquitectos y agentes de IA que construyen o mantienen servicios Python.
- **Disparador de actualización:** cuando los patrones arquitectónicos evolucionan o se adoptan nuevos patrones de infraestructura.

## Contenido

### Estructura de Capas

```
src/<service_name>/
├── domain/                  # Lógica de negocio pura — sin importaciones de framework
│   ├── entities/            # Entidades de dominio (frozen dataclasses)
│   ├── value_objects/       # Tipos de valor inmutables
│   ├── exceptions/          # Excepciones específicas del dominio
│   ├── ports/               # Interfaces abstractas (clases Protocol)
│   │   ├── repositories/    # Protocolos de repositorio
│   │   └── services/        # Protocolos de servicios externos
│   └── use_cases/           # Casos de uso de la aplicación (orquestación)
├── infrastructure/          # Implementaciones de framework y E/S
│   ├── database/            # Modelos SQLAlchemy, repositorios, migraciones
│   │   ├── models/          # Clases mapeadas del ORM
│   │   ├── repositories/    # Implementaciones de repositorio
│   │   └── migrations/      # Migraciones Alembic
│   ├── http/                # Routers FastAPI, dependencias, middleware
│   │   ├── routers/         # Definiciones de rutas
│   │   ├── dependencies/    # Fábricas de FastAPI Depends
│   │   ├── middleware/       # Middleware HTTP
│   │   └── schemas/         # Modelos Pydantic de request/response
│   ├── clients/             # Clientes HTTP/gRPC externos
│   ├── events/              # Publicadores/consumidores de eventos
│   └── config/              # Configuración, entorno, cableado de DI
├── shared/                  # Utilidades transversales (logging, telemetría)
└── main.py                  # Punto de entrada de la aplicación
```

### Dirección de Dependencias

```
infrastructure → domain ← (nada)
     │               │
     ▼               ▼
  frameworks     Python puro
  (FastAPI,      (dataclasses,
   SQLAlchemy,    Protocol,
   Pydantic)      exceptions)
```

**Reglas:**
- `domain/` NO DEBE importar desde `infrastructure/` ni de ningún framework
- `infrastructure/` implementa las interfaces de `domain/ports/`
- `use_cases/` dependen solo de puertos (Protocol), nunca de implementaciones concretas
- La inyección de dependencias conecta las implementaciones concretas en la raíz de composición (`config/` o `main.py`)

### Patrones de la Capa de Dominio

#### Entidades

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

- DEBEN ser frozen dataclasses (lex-python-immutability)
- NO DEBEN contener E/S ni código específico de frameworks
- Los cambios de estado retornan nuevas instancias

#### Puertos (Interfaces)

```python
from typing import Protocol

class TransactionRepository(Protocol):
    async def save(self, transaction: Transaction) -> None: ...
    async def get_by_id(self, entity_id: UUID) -> Transaction | None: ...
    async def list_by_status(
        self, status: TransactionStatus, limit: int, cursor: str | None
    ) -> list[Transaction]: ...
```

- DEBEN usar `typing.Protocol` (subtipado estructural)
- NO DEBEN importar tipos de infraestructura
- Definen el contrato que la infraestructura implementa

#### Casos de Uso

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

- Orquestan la lógica de dominio; un caso de uso por operación de negocio
- Reciben dependencias por constructor (inyección de dependencias)
- NO DEBEN importar FastAPI, SQLAlchemy u otra infraestructura

### Patrones de la Capa de Infraestructura

#### Implementaciones de Repositorio

- Implementan los protocolos de `domain/ports/repositories/`
- Usan sesión async de SQLAlchemy 2.0
- Mapean entre modelos ORM y entidades de dominio
- Ver codex-python-sqlalchemy para más detalles

#### Capa HTTP

- Los routers FastAPI invocan casos de uso, nunca repositorios directamente
- Schemas Pydantic para validación de requests y serialización de responses
- Ver codex-python-fastapi para más detalles

### Cuándo NO Abstraer

- NO crear un puerto/interfaz para algo con una única implementación y sin necesidad de testing
- NO crear una clase de caso de uso para CRUD simple sin lógica de negocio — una función de servicio directa es aceptable
- NO añadir capas "para extensibilidad futura" — añadirlas cuando llegue el segundo caso de uso
- Tres líneas de código similares son mejores que una abstracción prematura

## Glosario

| Término | Definición |
|---------|------------|
| Port | Interfaz abstracta (Protocol) que define un contrato entre capas |
| Adapter | Implementación concreta de un puerto (ej., repositorio SQLAlchemy) |
| Use Case | Orquestación a nivel de aplicación de operaciones de dominio |
| Composition Root | Donde las implementaciones concretas se conectan a los puertos (DI) |

## Referencias

- [Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [typing.Protocol — PEP 544](https://peps.python.org/pep-0544/)
- lex-python-typing, lex-python-immutability (engineering/backend)
- codex-python-fastapi, codex-python-sqlalchemy (engineering/backend)
