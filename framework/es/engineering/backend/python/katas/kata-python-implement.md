# Kata: Implementación de Features Python

> **Prefix:** `kata-` | **Type:** Habilidad Repetible | **Scope:** Engineering — Backend: implementación end-to-end de un feature Python desde el requisito hasta código testeado, tipado y revisado

## Objective

Esta Kata define el procedimiento para implementar un feature en una aplicación Python backend: entender el requisito, identificar capas afectadas, diseñar interfaces, implementar lógica de dominio con tests, construir adaptadores de infraestructura, validar con la cadena de calidad completa y entregar.

## When to Use

- Cuando un nuevo feature requiere implementación en un servicio Python backend
- Cuando es invocado por `cry-python-implement` o por el Warrior Apollo
- Cuando se agrega un nuevo endpoint, caso de uso, repositorio o entidad de dominio

## Inputs

| Input | Requerido | Descripción |
|-------|:---------:|-------------|
| Descripción del feature | Sí | Descripción textual del feature, comportamiento esperado y criterios de aceptación |
| Contexto o alcance | No | Restricciones (p. ej., patrones existentes a seguir, requisitos de rendimiento, spec OAS relacionada) |
| Capas afectadas | No | Qué capas están involucradas (dominio, infraestructura, HTTP). Si se omite, el agente las identifica |

## Workflow

```
Progress:
- [ ] 1. Entender el requisito y clarificar ambigüedades
- [ ] 2. Identificar capas y archivos afectados
- [ ] 3. Diseñar interfaces (Protocols) y modelos de datos
- [ ] 4. Implementar lógica de dominio con tests unitarios
- [ ] 5. Implementar adaptadores de infraestructura con tests de integración
- [ ] 6. Implementar capa HTTP con tests de endpoint
- [ ] 7. Validación final (lint, tipos, tests)
```

### Step 1: Entender el Requisito y Clarificar Ambigüedades

1. Leer la descripción del feature y cualquier spec OAS o documento de diseño referenciado
2. Identificar ambigüedades, casos límite y supuestos no declarados
3. **Hacer preguntas aclaratorias al usuario** — p. ej., ¿comportamiento esperado en error? ¿se necesita paginación? ¿requisitos de idempotencia? ¿patrones existentes a seguir?
4. Esperar respuestas antes de continuar. Repetir si surgen nuevas ambigüedades
5. Resumir el requisito entendido en 2-3 oraciones para confirmación

### Step 2: Identificar Capas y Archivos Afectados

1. Mapear el feature a la arquitectura (codex-python-architecture):
   - **Domain:** ¿nuevas entidades, value objects, excepciones, puertos, casos de uso?
   - **Infrastructure/Database:** ¿nuevos modelos ORM, métodos de repositorio, migraciones?
   - **Infrastructure/HTTP:** ¿nuevas rutas, schemas Pydantic, dependencias?
   - **Shared:** ¿nueva instrumentación de telemetría?
2. Listar archivos existentes que serán modificados y nuevos archivos que serán creados
3. Verificar patrones existentes en el codebase que este feature debe seguir

### Step 3: Diseñar Interfaces y Modelos de Datos

1. Definir o actualizar **entidades de dominio** como frozen dataclasses (lex-python-immutability)
2. Definir o actualizar interfaces **Protocol** para cualquier nuevo puerto (repositorios, servicios externos)
3. Definir **modelos Pydantic** para schemas de request/response en el límite HTTP
4. Todas las definiciones DEBEN tener type hints completos (lex-python-typing)
5. Presentar el diseño de interfaz al usuario si el feature es complejo; de lo contrario, continuar

### Step 4: Implementar Lógica de Dominio con Tests Unitarios

1. Implementar clases de **caso de uso** que orquestan la lógica de dominio
2. Escribir **tests unitarios** para cada camino de comportamiento: happy path, casos límite, casos de error
3. Usar `pytest.parametrize` para múltiples escenarios sobre la misma lógica
4. Usar **Hypothesis** para invariantes de dominio cuando sea aplicable
5. El código de dominio NO DEBE importar desde infraestructura (codex-python-architecture)
6. Ejecutar tests unitarios para confirmar que pasan

### Step 5: Implementar Adaptadores de Infraestructura con Tests de Integración

1. Implementar métodos de **repositorio** usando patrones async de SQLAlchemy 2.0 (codex-python-sqlalchemy)
2. Crear **migración Alembic** si se necesitan cambios de esquema
3. Escribir **tests de integración** contra una base de datos real — sin mocks para BD (lex-python-testing)
4. Implementar cualquier cliente de servicio externo con manejo adecuado de errores
5. Mapear entre modelos ORM y entidades de dominio en el repositorio
6. Ejecutar tests de integración para confirmar que pasan

### Step 6: Implementar Capa HTTP con Tests de Endpoint

1. Crear o actualizar **router FastAPI** con el nuevo endpoint (codex-python-fastapi)
2. Conectar **inyección de dependencias** para casos de uso y repositorios
3. Agregar **exception handlers** si se introdujeron nuevas excepciones de dominio
4. Escribir **tests HTTP** verificando códigos de estado, estructura de respuesta, payloads de error
5. Agregar spans personalizados de **OpenTelemetry** para operaciones críticas del negocio si es necesario (codex-python-observability)
6. Ejecutar tests HTTP para confirmar que pasan

### Step 7: Validación Final

Antes de entregar, verificar:

- [ ] Ruff pasa sin errores (`ruff check .` y `ruff format --check .`)
- [ ] mypy strict pasa sin errores (`mypy .`)
- [ ] Todos los tests pasan (`pytest`)
- [ ] El nuevo código tiene type hints completos (lex-python-typing)
- [ ] Sin secretos hardcodeados ni entrada no validada (lex-python-security)
- [ ] El manejo de errores usa excepciones específicas (lex-python-error-handling)
- [ ] Los dataclasses de dominio son frozen (lex-python-immutability)
- [ ] Los mocks se usan solo en límites del sistema (lex-python-testing)
- [ ] La migración es reversible (tiene `downgrade()`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Implementación | Archivos fuente Python | Directorios de capa apropiados según codex-python-architecture |
| Tests | Archivos de test Python | `tests/unit/`, `tests/integration/`, `tests/property/` |
| Migración | Archivo de migración Alembic | `alembic/versions/` (si hay cambios de esquema) |

## Execution Example

### Example Input

```
Feature: Agregar endpoint para cancelar una transacción (soft delete). Setear discarded_at, emitir evento de cancelación.
Context: Seguir patrones existentes de transacciones. Existe spec OAS en docs/oas/transactions.yaml.
```

### Example Output (summary)

1. Domain: excepción `TransactionCancelledError`; método `cancel()` en el caso de uso `TransactionService`
2. Repository: `SqlAlchemyTransactionRepository.soft_delete()` — setea `discarded_at` e incrementa `version`
3. Route: `DELETE /v1/transactions/{entity_id}` → 204; 404 si no se encuentra; 409 si ya fue cancelada
4. Tests: 8 tests (unitario: lógica de cancelación, ya cancelada, no encontrada; integración: soft delete en BD; HTTP: 204, 404, 409, auth faltante)
5. Migration: ninguna (sin cambio de esquema — columna `discarded_at` ya existe)

## Constraints

- Esta Kata produce código de implementación con tests — no diseño de API (kata-api-design-oas se encarga de eso)
- Seguir patrones del codebase existente sobre ideales teóricos
- No refactorizar código no relacionado durante la implementación del feature
- Escalar a un humano cuando se necesiten decisiones arquitectónicas (nuevo bounded context, nuevo límite de servicio)

## References

- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-observability, codex-python-tooling (engineering/backend)
