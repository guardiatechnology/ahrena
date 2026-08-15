# Codex: Ferramentas de Desenvolvimento Python

> **Prefix:** `codex-` | **Type:** Manual de Referência | **Scope:** Engineering — Backend: ferramentas de desenvolvimento para projetos Python

## Content

### Tool Stack

| Ferramenta | Propósito | Substitui |
|------------|----------|-----------|
| **Ruff** | Linting + formatação | flake8, black, isort, pylint, pyflakes |
| **mypy** | Verificação estática de tipos | — |
| **pytest** | Executor de testes | unittest |
| **pytest-asyncio** | Suporte a testes async | — |
| **pytest-cov** | Relatório de cobertura | coverage |
| **Hypothesis** | Testes baseados em propriedades | — |
| **pip-audit** | Varredura de vulnerabilidades em dependências | safety |
| **pre-commit** | Automação de git hooks | verificações manuais |

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

**Regras:**
- Ruff é o único linter e formatador — sem necessidade de ferramentas separadas
- Regras de segurança (S) habilitadas para detecção automática de vulnerabilidades
- `T20` bloqueia instruções `print()` — usar `logging` em vez disso
- Testes podem usar `assert` (S101 ignorado)

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

**Regras:**
- Modo strict é obrigatório (lex-python-typing)
- Testes podem ter tipagem mais relaxada (trade-off prático)
- Adicionar `# type: ignore[<code>]` com comentário de justificativa para casos inevitáveis

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

**Regras:**
- Usar markers para categorizar testes para execução seletiva
- `asyncio_mode = "auto"` elimina a decoração manual com `@pytest.mark.asyncio`
- `--strict-markers` previne erros tipográficos em nomes de markers

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

**Regras:**
- pre-commit executa em cada commit — sem etapas manuais
- Ruff corrige problemas auto-corrigíveis; mypy bloqueia erros de tipo; pip-audit bloqueia dependências vulneráveis
- Manter versões de hooks fixadas e atualizá-las periodicamente

### Dependency Management

```toml
# pyproject.toml — dependências com versões mínimas
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

**Regras:**
- Usar `pyproject.toml` como única fonte para metadados do projeto e dependências
- Fixar versões mínimas com `>=`; bloquear versões exatas no lock file
- Separar dependências de desenvolvimento em optional-dependencies
- Auditar dependências antes de adicionar (licença, manutenção, segurança)
- Commitar lock files no repositório

### CI Pipeline Checks

```yaml
# Verificações mínimas de CI (representação agnóstica de ferramenta)
steps:
  - ruff check .
  - ruff format --check .
  - mypy .
  - pytest tests/unit -m unit
  - pytest tests/integration -m integration
  - pip-audit
```

**Regras:**
- Todas as ferramentas executam no CI — pre-commit é uma conveniência, CI é o portão
- Testes unitários executam primeiro (feedback rápido); testes de integração executam depois
- Pipeline falha em qualquer erro de ferramenta — sem modo somente-avisos
