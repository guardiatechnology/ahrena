# Cry: Implementación de Feature Python

> **Prefix:** `cry-` | **Type:** Comando Recurrente | **Scope:** Atajo para implementar un feature Python según Lexis y Codex del backend

## Description

Este comando invoca al Warrior Apollo (o al agente que asume su rol) para implementar un feature Python: consultar Lexis y Codex del backend, diseñar interfaces, implementar lógica de dominio con tests, construir adaptadores de infraestructura y validar con la cadena de calidad completa.

## Usage

```
/cry-python-implement <descripción del feature> [contexto]
```

## Parameters

| Parámetro | Requerido | Descripción | Ejemplo |
|-----------|:---------:|-------------|---------|
| `descripción del feature` | Sí | Descripción del feature, comportamiento esperado y criterios de aceptación | "Agregar endpoint para listar transacciones con paginación y filtro por estado" |
| `contexto` | No | Restricciones, spec OAS relacionada, patrones existentes a seguir | "Seguir patrones existentes de transacciones. Spec OAS en docs/oas/transactions.yaml" |

## What the Command Does

1. Interpreta la descripción del feature y el contexto
2. Asume el rol del Warrior Apollo (Senior Python Engineer)
3. Ejecuta **kata-python-implement** iterativamente:
   - Clarifica ambigüedades con el usuario
   - Identifica capas afectadas (dominio, infraestructura, HTTP)
   - Diseña interfaces y modelos de datos
   - Implementa lógica de dominio con tests unitarios
   - Implementa infraestructura con tests de integración
   - Implementa capa HTTP con tests de endpoint
4. Valida con Ruff, mypy y pytest antes de entregar

## Prompt Template

```
Context:
- Feature description: {{descripción del feature}}
- Additional context: {{contexto}}

Task:
Act as the Apollo Warrior (Senior Python Engineer) and execute **kata-python-implement**. Consult the applicable Lexis (lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability) and Codex (codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-observability, codex-python-tooling). Ask clarifying questions when needed. Implement the feature with tests at every layer. Validate with Ruff, mypy, and pytest before delivering.

Output:
- Implementation files in the appropriate layer directories
- Tests in tests/unit/, tests/integration/
- Alembic migration if schema changes are needed
- Brief summary of what was implemented and why
```

## Invocation Example

**Input:**

```
/cry-python-implement "Agregar soft delete para transacciones: setear discarded_at, retornar 204, emitir evento de cancelación" "Seguir patrones existentes de transacciones. La entidad ya tiene columna discarded_at."
```

**Expected output:**

Apollo implementa el feature iterativamente:
- Domain: caso de uso `cancel_transaction`, `TransactionCancelledEvent`
- Repository: método `soft_delete()`
- Route: `DELETE /v1/transactions/{entity_id}` → 204
- Tests: unitario (lógica de cancelación), integración (BD), HTTP (204, 404, 409)
- Ruff, mypy, pytest todos pasan

## Constraints

- El Cry dispara la implementación — no diseña contratos de API (cry-api-design se encarga de eso)
- La descripción del feature debe ser suficiente para identificar el alcance; si es vaga, Apollo pedirá aclaraciones
- Las excepciones a los Lexis deben documentarse y justificarse

## Cry vs Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida con descripción del feature | Procedimiento completo en 7 pasos |
| **Complejidad** | Baja (1 comando) | Alta (clarificar, diseñar, implementar, testear, validar) |
| **¿Configura agente?** | Sí (asume el rol del Warrior Apollo) | Sí (define todos los pasos de implementación) |
| **Ejemplo** | "/cry-python-implement agregar cancelación de transacción" | Ejecutar kata-python-implement con entradas explícitas por paso |

## Associated Kata and Warrior

- **kata-python-implement** — Procedimiento completo de implementación
- **warrior-apollo** — Senior Python Engineer; ejecuta kata-python-implement

## References

- `kata-python-implement` — Procedimiento ejecutado por el Warrior Apollo
- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-observability, codex-python-tooling (engineering/backend)
