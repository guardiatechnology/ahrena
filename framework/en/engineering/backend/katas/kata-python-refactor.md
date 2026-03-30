# Kata: Python Safe Refactoring

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Backend: safe refactoring of Python code with test coverage as a safety net

## Objective

This Kata defines the procedure to refactor Python code safely: verify test coverage exists before changing anything, make small incremental transformations, validate at each step, and never change behavior and interface in the same commit.

## When to Use

- When improving code structure, readability, or performance without changing behavior
- When invoked by the Apollo Warrior for refactoring tasks
- When tech debt needs to be addressed in an existing module
- When migrating to a new pattern (e.g., sync to async, raw SQL to SQLAlchemy)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Refactoring target | Yes | Files, modules, or patterns to refactor |
| Motivation | No | Why this refactoring is needed (performance, readability, pattern alignment) |
| Constraints | No | What must not change (public interfaces, API contracts, behavior) |

## Workflow

```
Progress:
- [ ] 1. Assess current test coverage
- [ ] 2. Add missing coverage if needed
- [ ] 3. Plan refactoring steps
- [ ] 4. Execute incremental transformations
- [ ] 5. Final validation
```

### Step 1: Assess Current Test Coverage

1. Run the test suite for the target module: `pytest tests/ -v --cov=<module>`
2. Identify which behaviors are covered and which are not
3. If coverage is insufficient to safely refactor, **stop and add tests first** (Step 2)
4. If coverage is adequate, proceed to Step 3

### Step 2: Add Missing Coverage

1. Write tests for existing behavior **before** changing it — these are characterization tests
2. Test the current behavior, not the desired behavior
3. Run the suite to confirm all new tests pass against the current code
4. Commit the new tests separately: "test: add coverage for <module> before refactoring"

### Step 3: Plan Refactoring Steps

1. Break the refactoring into **small, independent transformations**
2. Each step should be:
   - A single logical change (rename, extract, move, simplify)
   - Independently committable
   - Verifiable by running the test suite
3. Order steps to minimize risk: renames before restructuring, internal before external

### Step 4: Execute Incremental Transformations

For each step:

1. Make the change
2. Run `ruff check .` and `ruff format .`
3. Run `mypy .`
4. Run `pytest` — all tests must pass
5. If tests fail, the refactoring introduced a behavior change — fix or revert
6. Commit with a descriptive message: "refactor: <what changed>"

**Rules:**
- **Never** change behavior and interface in the same commit
- **Never** skip running tests between steps
- If a step is too large to verify confidently, break it into smaller steps
- If tests start failing unexpectedly, revert and reassess

### Step 5: Final Validation

After all transformations:

- [ ] All tests pass (`pytest`)
- [ ] Ruff passes (`ruff check .` and `ruff format --check .`)
- [ ] mypy strict passes (`mypy .`)
- [ ] Behavior is unchanged (same tests pass, same API contracts, same outputs)
- [ ] Code is cleaner, more readable, or better structured than before
- [ ] No new abstractions unless justified by 3+ concrete uses

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Refactored code | Python source files | Same file locations (or new locations if moved) |
| Characterization tests (if added) | Python test files | `tests/` |
| Commit history | Git commits | One commit per logical transformation |

## Execution Example

### Example Input

```
Target: TransactionService class — currently a god class with 15 methods mixing domain logic and infrastructure.
Motivation: Separate domain logic from infrastructure per codex-python-architecture.
Constraint: All existing endpoints must continue working identically.
```

### Example Output (summary)

1. Added 22 characterization tests covering existing behavior (separate commit)
2. Extracted domain logic into `TransactionUseCase` (3 commits: extract, wire, cleanup)
3. Moved repository methods to `SqlAlchemyTransactionRepository` implementing `TransactionRepository` Protocol (2 commits)
4. Updated FastAPI dependencies to use new injection graph (1 commit)
5. All 47 tests pass; mypy and Ruff clean

## Constraints

- Never change behavior during refactoring — if behavior needs to change, that's a separate task
- Never refactor without test coverage — add tests first
- Never make large, monolithic refactoring commits — small steps with validation
- Escalate to human if refactoring reveals architectural decisions that need alignment

## References

- [Refactoring — Martin Fowler](https://refactoring.com/)
- codex-python-architecture, codex-python-testing (engineering/backend)
- lex-python-typing, lex-python-testing (engineering/backend)
