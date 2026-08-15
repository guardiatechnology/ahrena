# Lexis: Prácticas de Seguridad en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: estándares de seguridad para código Python

## Purpose

Garantizar que el código Python no introduzca vulnerabilidades de seguridad. Los secretos hardcodeados, las entradas no validadas y las dependencias no auditadas son vectores de ataque que comprometen todo el sistema. La seguridad no es una consideración posterior — es una restricción en cada línea de código.

## Law

> **Ningún secreto DEBE estar hardcodeado en el código fuente. Toda entrada externa DEBE ser validada en los límites del sistema usando modelos Pydantic. Las dependencias DEBEN ser auditadas por vulnerabilidades conocidas antes de su adopción y periódicamente después. Las consultas SQL DEBEN usar sentencias parametrizadas — nunca interpolación de strings.**

## Scope

- **Applies to:** todos los archivos fuente Python, configuración y manifests de dependencias.
- **Bound agents:** todos los agentes e implementadores que escriben o modifican código Python o gestionan dependencias.
- **Exceptions:** ninguna. Las leyes de seguridad no tienen excepciones.

## Consequences of Violation

1. **Filtración de credenciales:** los secretos hardcodeados en repositorios son cosechados por scanners automatizados en minutos.
2. **Inyección:** la entrada no validada habilita inyección SQL, inyección de comandos y path traversal.
3. **Supply chain:** las dependencias vulnerables son activamente explotadas.
4. **Remediación:** rotación inmediata de credenciales filtradas; el código vulnerable debe parchearse antes del merge.

## Examples

### Correct

```python
import os
from pydantic import BaseModel, Field

# Secretos desde el entorno
DATABASE_URL = os.environ["DATABASE_URL"]

# Validación de entrada en el límite
class CreateTransferRequest(BaseModel):
    amount: int = Field(gt=0, le=999_999_999)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    recipient_id: str = Field(min_length=1, max_length=36)

# Consulta parametrizada
stmt = select(Transaction).where(Transaction.entity_id == transaction_id)
```

### Incorrect

```python
# Secreto hardcodeado
API_KEY = "sk-live-abc123secret"

# Entrada no validada pasada a la consulta
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"  # Inyección SQL
    ...

# Interpolación de strings en SQLAlchemy
stmt = text(f"SELECT * FROM transactions WHERE status = '{status}'")
```

## Automated Validation

- **Tool:** Reglas de seguridad de Ruff (subconjunto S); pip-audit o safety para escaneo de dependencias; pre-commit hooks.
- **When:** cada commit (pre-commit) y cada PR (pipeline CI con auditoría de dependencias).
- **Metric:** 0 secretos hardcodeados detectados; 0 vulnerabilidades conocidas en dependencias; 0 vectores de inyección SQL.

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [pip-audit](https://pypi.org/project/pip-audit/)
- [Bandit / Ruff S rules](https://docs.astral.sh/ruff/rules/#flake8-bandit-s)
- [Pydantic validation](https://docs.pydantic.dev/latest/)
- codex-python-tooling (engineering/backend)
