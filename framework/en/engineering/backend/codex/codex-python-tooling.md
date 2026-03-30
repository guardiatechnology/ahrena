# Codex: Python Tooling

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Engineering — Backend: development tooling for Python projects

## Overview

This manual defines the standard development tooling for Python backend projects. Consistent tooling across the team eliminates style debates, catches bugs early, and automates quality enforcement. Every tool is configured once and runs automatically — developers focus on logic, not formatting.

## Context

- **Domain:** development tooling and quality automation for Python projects.
- **Target audience:** implementers and AI agents that configure or maintain Python project tooling.
- **Update trigger:** when tools are upgraded or new tools are adopted.

## Content

### Tool Stack

| Tool | Purpose | Replaces |
|------|---------|----------|
| **Ruff** | Linting + formatting | flake8, black, isort, pylint, pyflakes |
| **mypy** | Static type checking | — |
| **pytest** | Test runner | unittest |
| **pytest-asyncio** | Async test support | — |
| **pytest-cov** | Coverage reporting | coverage |
| **Hypothesis** | Property-based testing | — |
| **pip-audit** | Dependency vulnerability scanning | safety |
| **pre-commit** | Git hook automation | manual checks |

### Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 120

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "BLE",   # flake8-blind-except
    "S",     # flake8-bandit (security)
    "A",     # flake8-builtins
    "C4",    # flake8-comprehensions
    "DTZ",   # flake8-datetimez
    "T20",   # flake8-print
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "ARG",   # flake8-unused-arguments
    "RUF",   # Ruff-specific rules
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert in tests

[tool.ruff.format]
quote-style = "double"
```

**Rules:**
- Ruff is the single linter and formatter — no need for separate tools
- Security rules (S) enabled for automated vulnerability detection
- `T20` blocks `print()` statements — use `logging` instead
- Tests may use `assert` (S101 ignored)

### mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

**Rules:**
- Strict mode is mandatory (lex-python-typing)
- Tests may have relaxed typing (practical trade-off)
- Add `# type: ignore[<code>]` with justification comment for unavoidable issues

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests (no I/O)",
    "integration: Integration tests (requires database)",
    "property: Property-based tests (Hypothesis)",
]
addopts = "-v --tb=short --strict-markers"
```

**Rules:**
- Use markers to categorize tests for selective execution
- `asyncio_mode = "auto"` eliminates manual `@pytest.mark.asyncio` decoration
- `--strict-markers` prevents typos in marker names

### pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy]

  - repo: https://github.com/pypa/pip-audit
    rev: v2.7.0
    hooks:
      - id: pip-audit
```

**Rules:**
- pre-commit runs on every commit — no manual steps
- Ruff fixes auto-fixable issues; mypy blocks type errors; pip-audit blocks vulnerable deps
- Keep hook versions pinned and update periodically

### Dependency Management

```toml
# pyproject.toml — dependencies with minimum versions
[project]
dependencies = [
    "fastapi[standard]>=0.122.0",
    "sqlalchemy>=2.0.44",
    "pydantic>=2.12.5",
    "asyncpg>=0.31.0",
    "alembic>=1.17.2",
    "opentelemetry-api>=1.38.0",
    "opentelemetry-sdk>=1.38.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-asyncio>=0.21.0",
    "hypothesis>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pre-commit>=4.0.0",
    "pip-audit>=2.7.0",
]
```

**Rules:**
- Use `pyproject.toml` as the single source for project metadata and dependencies
- Pin minimum versions with `>=`; lock exact versions in lock file
- Separate dev dependencies in optional-dependencies
- Audit dependencies before adding (license, maintenance, security)
- Commit lock files to the repository

### CI Pipeline Checks

```yaml
# Minimum CI checks (tool-agnostic representation)
steps:
  - ruff check .
  - ruff format --check .
  - mypy .
  - pytest tests/unit -m unit
  - pytest tests/integration -m integration
  - pip-audit
```

**Rules:**
- All tools run in CI — pre-commit is a convenience, CI is the gate
- Unit tests run first (fast feedback); integration tests run second
- Pipeline fails on any tool error — no warnings-only mode

## Glossary

| Term | Definition |
|------|------------|
| Ruff | Extremely fast Python linter and formatter written in Rust |
| mypy | Static type checker for Python |
| pre-commit | Framework for managing git pre-commit hooks |
| pip-audit | Tool for scanning Python dependencies for known vulnerabilities |

## References

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [pre-commit documentation](https://pre-commit.com/)
- [pip-audit documentation](https://pypi.org/project/pip-audit/)
- lex-python-typing, lex-python-security (engineering/backend)
