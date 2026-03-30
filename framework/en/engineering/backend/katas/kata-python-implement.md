# Kata: Python Feature Implementation

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Backend: end-to-end implementation of a Python feature from requirement to tested, typed, reviewed code

## Objective

This Kata defines the procedure to implement a feature in a Python backend application: understand the requirement, identify affected layers, design interfaces, implement domain logic with tests, build infrastructure adapters, validate with the full quality toolchain, and deliver.

## When to Use

- When a new feature requires implementation in a Python backend service
- When invoked by `cry-python-implement` or by the Apollo Warrior
- When adding a new endpoint, use case, repository, or domain entity

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Feature description | Yes | Textual description of the feature, expected behavior, and acceptance criteria |
| Context or scope | No | Constraints (e.g., existing patterns to follow, performance requirements, related OAS spec) |
| Affected layers | No | Which layers are involved (domain, infrastructure, HTTP). If omitted, the agent identifies them |

## Workflow

```
Progress:
- [ ] 1. Understand requirement and clarify ambiguities
- [ ] 2. Identify affected layers and files
- [ ] 3. Design interfaces (Protocols) and data models
- [ ] 4. Implement domain logic with unit tests
- [ ] 5. Implement infrastructure adapters with integration tests
- [ ] 6. Implement HTTP layer with endpoint tests
- [ ] 7. Final validation (lint, types, tests)
```

### Step 1: Understand Requirement and Clarify Ambiguities

1. Read the feature description and any referenced OAS spec or design document
2. Identify ambiguities, edge cases, and unstated assumptions
3. **Ask the user clarifying questions** — e.g., expected behavior on error? pagination needed? idempotency requirements? existing patterns to follow?
4. Wait for answers before proceeding. Repeat if new ambiguities emerge
5. Summarize the understood requirement in 2-3 sentences for confirmation

### Step 2: Identify Affected Layers and Files

1. Map the feature to the architecture (codex-python-architecture):
   - **Domain:** new entities, value objects, exceptions, ports, use cases?
   - **Infrastructure/Database:** new ORM models, repository methods, migrations?
   - **Infrastructure/HTTP:** new routes, Pydantic schemas, dependencies?
   - **Shared:** new telemetry instrumentation?
2. List existing files that will be modified and new files that will be created
3. Check for existing patterns in the codebase that this feature should follow

### Step 3: Design Interfaces and Data Models

1. Define or update **domain entities** as frozen dataclasses (lex-python-immutability)
2. Define or update **Protocol** interfaces for any new ports (repositories, external services)
3. Define **Pydantic models** for request/response schemas at the HTTP boundary
4. All definitions MUST have complete type hints (lex-python-typing)
5. Present the interface design to the user if the feature is complex; otherwise proceed

### Step 4: Implement Domain Logic with Unit Tests

1. Implement **use case** classes that orchestrate domain logic
2. Write **unit tests** for every behavior path: happy path, edge cases, error cases
3. Use `pytest.parametrize` for multiple scenarios on the same logic
4. Use **Hypothesis** for domain invariants when applicable
5. Domain code MUST NOT import from infrastructure (codex-python-architecture)
6. Run unit tests to confirm they pass

### Step 5: Implement Infrastructure Adapters with Integration Tests

1. Implement **repository** methods using SQLAlchemy 2.0 async patterns (codex-python-sqlalchemy)
2. Create **Alembic migration** if schema changes are needed
3. Write **integration tests** against a real database — no mocks for DB (lex-python-testing)
4. Implement any external service clients with proper error handling
5. Map between ORM models and domain entities in the repository
6. Run integration tests to confirm they pass

### Step 6: Implement HTTP Layer with Endpoint Tests

1. Create or update **FastAPI router** with the new endpoint (codex-python-fastapi)
2. Wire **dependency injection** for use cases and repositories
3. Add **exception handlers** if new domain exceptions were introduced
4. Write **HTTP tests** verifying status codes, response structure, error payloads
5. Add **OpenTelemetry** custom spans for business-critical operations if needed (codex-python-observability)
6. Run HTTP tests to confirm they pass

### Step 7: Final Validation

Before delivering, verify:

- [ ] Ruff passes with no errors (`ruff check .` and `ruff format --check .`)
- [ ] mypy strict passes with no errors (`mypy .`)
- [ ] All tests pass (`pytest`)
- [ ] New code has complete type hints (lex-python-typing)
- [ ] No hardcoded secrets or unvalidated input (lex-python-security)
- [ ] Error handling uses specific exceptions (lex-python-error-handling)
- [ ] Domain dataclasses are frozen (lex-python-immutability)
- [ ] Mocks used only at system boundaries (lex-python-testing)
- [ ] Migration is reversible (has `downgrade()`)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Implementation | Python source files | Appropriate layer directories per codex-python-architecture |
| Tests | Python test files | `tests/unit/`, `tests/integration/`, `tests/property/` |
| Migration | Alembic migration file | `alembic/versions/` (if schema changes) |

## Execution Example

### Example Input

```
Feature: Add endpoint to cancel a transaction (soft delete). Set discarded_at, emit cancellation event.
Context: Follow existing transaction patterns. OAS spec exists at docs/oas/transactions.yaml.
```

### Example Output (summary)

1. Domain: `TransactionCancelledError` exception; `cancel()` method on `TransactionService` use case
2. Repository: `SqlAlchemyTransactionRepository.soft_delete()` — sets `discarded_at` and increments `version`
3. Route: `DELETE /v1/transactions/{entity_id}` → 204; 404 if not found; 409 if already cancelled
4. Tests: 8 tests (unit: cancel logic, already cancelled, not found; integration: DB soft delete; HTTP: 204, 404, 409, missing auth)
5. Migration: none (no schema change — `discarded_at` column already exists)

## Constraints

- This Kata produces implementation code with tests — not API design (kata-api-design-oas handles that)
- Follow existing codebase patterns over theoretical ideals
- Do not refactor unrelated code during feature implementation
- Escalate to human when architectural decisions are needed (new bounded context, new service boundary)

## References

- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-observability, codex-python-tooling (engineering/backend)
