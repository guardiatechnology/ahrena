# Codex: Herramientas de Desarrollo Python

> **Prefix:** `codex-` | **Type:** Manual de Referencia | **Scope:** Engineering — Backend: herramientas de desarrollo para proyectos Python

## Overview

Este manual define las herramientas de desarrollo estándar para proyectos Python backend. Las herramientas consistentes en todo el equipo eliminan debates de estilo, detectan bugs tempranamente y automatizan la aplicación de calidad. Cada herramienta se configura una vez y se ejecuta automáticamente — los desarrolladores se concentran en la lógica, no en el formateo.

## Context

- **Domain:** herramientas de desarrollo y automatización de calidad para proyectos Python.
- **Target audience:** implementadores y agentes de IA que configuran o mantienen las herramientas de proyectos Python.
- **Update trigger:** cuando se actualizan herramientas o se adoptan nuevas.

## Content

### Tool Stack

| Herramienta | Propósito | Reemplaza |
|-------------|----------|-----------|
| **Ruff** | Linting + formateo | flake8, black, isort, pylint, pyflakes |
| **mypy** | Verificación estática de tipos | — |
| **pytest** | Ejecutor de tests | unittest |
| **pytest-asyncio** | Soporte de tests async | — |
| **pytest-cov** | Reporte de cobertura | coverage |
| **Hypothesis** | Testing basado en propiedades | — |
| **pip-audit** | Escaneo de vulnerabilidades en dependencias | safety |
| **pre-commit** | Automatización de git hooks | verificaciones manuales |

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

**Reglas:**
- Ruff es el único linter y formateador — no se necesitan herramientas separadas
- Reglas de seguridad (S) habilitadas para detección automática de vulnerabilidades
- `T20` bloquea sentencias `print()` — usar `logging` en su lugar
- Los tests pueden usar `assert` (S101 ignorado)

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

**Reglas:**
- El modo strict es obligatorio (lex-python-typing)
- Los tests pueden tener tipado más relajado (trade-off práctico)
- Agregar `# type: ignore[<code>]` con comentario de justificación para casos inevitables

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

**Reglas:**
- Usar markers para categorizar tests para ejecución selectiva
- `asyncio_mode = "auto"` elimina la decoración manual con `@pytest.mark.asyncio`
- `--strict-markers` previene errores tipográficos en nombres de markers

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

**Reglas:**
- pre-commit se ejecuta en cada commit — sin pasos manuales
- Ruff corrige problemas auto-corregibles; mypy bloquea errores de tipo; pip-audit bloquea dependencias vulnerables
- Mantener versiones de hooks fijadas y actualizarlas periódicamente

### Dependency Management

```toml
# pyproject.toml — dependencias con versiones mínimas
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

**Reglas:**
- Usar `pyproject.toml` como única fuente de metadatos del proyecto y dependencias
- Fijar versiones mínimas con `>=`; bloquear versiones exactas en el lock file
- Separar dependencias de desarrollo en optional-dependencies
- Auditar dependencias antes de agregar (licencia, mantenimiento, seguridad)
- Commitear lock files al repositorio

### CI Pipeline Checks

```yaml
# Verificaciones mínimas de CI (representación agnóstica de herramienta)
steps:
  - ruff check .
  - ruff format --check .
  - mypy .
  - pytest tests/unit -m unit
  - pytest tests/integration -m integration
  - pip-audit
```

**Reglas:**
- Todas las herramientas se ejecutan en CI — pre-commit es una conveniencia, CI es la puerta
- Los tests unitarios se ejecutan primero (feedback rápido); los tests de integración después
- El pipeline falla ante cualquier error de herramienta — sin modo solo-advertencias

## Glossary

| Término | Definición |
|---------|-----------|
| Ruff | Linter y formateador Python extremadamente rápido escrito en Rust |
| mypy | Verificador estático de tipos para Python |
| pre-commit | Framework para gestionar git pre-commit hooks |
| pip-audit | Herramienta para escanear dependencias Python en busca de vulnerabilidades conocidas |

## References

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [pre-commit documentation](https://pre-commit.com/)
- [pip-audit documentation](https://pypi.org/project/pip-audit/)
- lex-python-typing, lex-python-security (engineering/backend)
