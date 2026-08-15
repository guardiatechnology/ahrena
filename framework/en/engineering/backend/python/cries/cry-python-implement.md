# Cry: Python Feature Implementation

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to implement a Python feature per backend Lexis and Codex

## Description

This command invokes the Apollo Warrior (or the agent assuming its role) to implement a Python feature: consult backend Lexis and Codex, design interfaces, implement domain logic with tests, build infrastructure adapters, and validate with the full quality toolchain.

## Usage

```
/cry-python-implement <feature description> [context]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `feature description` | Yes | Description of the feature, expected behavior, and acceptance criteria | "Add endpoint to list transactions with pagination and status filter" |
| `context` | No | Constraints, related OAS spec, existing patterns to follow | "Follow existing transaction patterns. OAS spec at docs/oas/transactions.yaml" |

## What the Command Does

1. Interprets the feature description and context
2. Assumes the role of the Apollo Warrior (Senior Python Engineer)
3. Executes **kata-python-implement** iteratively:
   - Clarifies ambiguities with the user
   - Identifies affected layers (domain, infrastructure, HTTP)
   - Designs interfaces and data models
   - Implements domain logic with unit tests
   - Implements infrastructure with integration tests
   - Implements HTTP layer with endpoint tests
4. Validates with Ruff, mypy, and pytest before delivering

## Prompt Template

```
Context:
- Feature description: {{feature description}}
- Additional context: {{context}}

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
/cry-python-implement "Add soft delete for transactions: set discarded_at, return 204, emit cancellation event" "Follow existing transaction patterns. Entity already has discarded_at column."
```

**Expected output:**

Apollo implements the feature iteratively:
- Domain: `cancel_transaction` use case, `TransactionCancelledEvent`
- Repository: `soft_delete()` method
- Route: `DELETE /v1/transactions/{entity_id}` → 204
- Tests: unit (cancel logic), integration (DB), HTTP (204, 404, 409)
- Ruff, mypy, pytest all pass

## Constraints

- The Cry triggers implementation — it does not design API contracts (cry-api-design handles that)
- The feature description must be sufficient to identify scope; if vague, Apollo will ask for clarification
- Exceptions to Lexis must be documented and justified

## Cry vs Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Quick invocation with feature description | Full procedure in 7 steps |
| **Complexity** | Low (1 command) | High (clarify, design, implement, test, validate) |
| **Configures agent?** | Yes (assumes Apollo Warrior role) | Yes (defines all implementation steps) |
| **Example** | "/cry-python-implement add transaction cancellation" | Execute kata-python-implement with explicit inputs per step |

## Associated Kata and Warrior

- **kata-python-implement** — Full implementation procedure
- **warrior-apollo** — Senior Python Engineer; executes kata-python-implement

## References

- `kata-python-implement` — Procedure executed by the Apollo Warrior
- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-observability, codex-python-tooling (engineering/backend)
