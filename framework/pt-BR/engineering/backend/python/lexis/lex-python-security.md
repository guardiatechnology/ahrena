# Lexis: Práticas de Segurança Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: padrões de segurança para código Python

## Purpose

Garantir que o código Python não introduza vulnerabilidades de segurança. Segredos hardcoded, entradas não validadas e dependências não auditadas são vetores de ataque que comprometem todo o sistema. Segurança não é uma consideração posterior — é uma restrição em cada linha de código.

## Law

> **Nenhum segredo DEVE estar hardcoded no código fonte. Toda entrada externa DEVE ser validada nas fronteiras do sistema usando modelos Pydantic. As dependências DEVEM ser auditadas por vulnerabilidades conhecidas antes da adoção e periodicamente depois. Queries SQL DEVEM usar instruções parametrizadas — nunca interpolação de strings.**

## Scope

- **Applies to:** todos os arquivos fonte Python, configuração e manifests de dependências.
- **Bound agents:** todos os agentes e implementadores que escrevem ou modificam código Python ou gerenciam dependências.
- **Exceptions:** nenhuma. Leis de segurança não têm exceções.

## Consequences of Violation

1. **Vazamento de credenciais:** segredos hardcoded em repositórios são coletados por scanners automatizados em minutos.
2. **Injeção:** entrada não validada habilita injeção SQL, injeção de comandos e path traversal.
3. **Supply chain:** dependências vulneráveis são ativamente exploradas.
4. **Remediação:** rotação imediata de credenciais vazadas; código vulnerável deve ser corrigido antes do merge.

## Examples

### Correct

```python
import os
from pydantic import BaseModel, Field

# Segredos do ambiente
DATABASE_URL = os.environ["DATABASE_URL"]

# Validação de entrada na fronteira
class CreateTransferRequest(BaseModel):
    amount: int = Field(gt=0, le=999_999_999)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    recipient_id: str = Field(min_length=1, max_length=36)

# Query parametrizada
stmt = select(Transaction).where(Transaction.entity_id == transaction_id)
```

### Incorrect

```python
# Segredo hardcoded
API_KEY = "sk-live-abc123secret"

# Entrada não validada passada para query
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"  # Injeção SQL
    ...

# Interpolação de strings no SQLAlchemy
stmt = text(f"SELECT * FROM transactions WHERE status = '{status}'")
```

## Automated Validation

- **Tool:** Regras de segurança do Ruff (subconjunto S); pip-audit ou safety para varredura de dependências; pre-commit hooks.
- **When:** cada commit (pre-commit) e cada PR (pipeline CI com auditoria de dependências).
- **Metric:** 0 segredos hardcoded detectados; 0 vulnerabilidades conhecidas em dependências; 0 vetores de injeção SQL.

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [pip-audit](https://pypi.org/project/pip-audit/)
- [Bandit / Ruff S rules](https://docs.astral.sh/ruff/rules/#flake8-bandit-s)
- [Pydantic validation](https://docs.pydantic.dev/latest/)
- codex-python-tooling (engineering/backend)
