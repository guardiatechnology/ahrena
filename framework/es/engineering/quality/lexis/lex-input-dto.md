# Lexis: Input-DTO (Parameter Object para Superficies de Construcción)

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ingeniería — Backend: firmas de funciones, métodos, factories, commands de use-case e inputs de construcción de entidad en código Python

## Propósito

Las superficies de construcción grandes — una factory de dominio con 19 kwargs, un par `provision()`/`adjust()` repitiendo los mismos 14 argumentos — son un smell estructural distinto de la duplicación de conocimiento de dominio. `lex-dry` gobierna la regla de negocio (la fórmula, la validación, el mapeo); no cubre el *shape de construcción* — el conjunto de parámetros que siempre viajan juntos y se vuelven a listar entre firmas hermanas. Ese shape, cuando no se nombra, se dispersa: cada llamador reordena argumentos posicionales, cada firma hermana copia el grupo, y agregar un campo obliga a editar N puntos. El Parameter Object (input-DTO) convierte el contrato de construcción en un tipo único, tipado e inmutable, ligado a la capa del hexágono donde nace. Esta Ley impone el agrupamiento donde el costo es real (superficie amplia o grupo repetido) sin caer en el smell inverso — un DTO para una función de dos argumentos es ceremonia, no cohesión.

## Ley

> **Toda función, método o factory que (1) recibe ≥ 5 parámetros de dominio, (2) comparte el mismo grupo de parámetros con ≥ 2 firmas hermanas (regla de los tres del shape de parámetro), o (3) representa un command de use-case o input de birth/factory de entidad DEBE agrupar esos parámetros en un tipo de input dedicado e inmutable (frozen). El tipo DEBE respetar la capa del hexágono en la que vive — Pydantic request model en `adapters/api`, `Command` frozen en `application`, Value Object de construcción frozen en `domain` — sin reutilizar el tipo de una capa en otra. Input-DTO mutable, anémico (refleja todo argumento sin cohesión) o reutilizado entre capas (boundary leak) está PROHIBIDO. Los métodos de 1–3 parámetros y las transiciones single-arg (ej.: `settle(on: datetime)`) NO exigen agrupamiento.**

```
<HARD-GATE>
warrior-apollo, warrior-athena (Gate 2) y cualquier agente que implemente
o revise código Python NO PUEDEN aprobar una firma de construcción que
dispare un disparador objetivo de superficie sin que los parámetros estén
agrupados en un tipo de input dedicado.

Precondiciones obligatorias (basta que UNA dispare para obligar el agrupamiento):
  (a) la firma recibe ≥ 5 parámetros de dominio
      (disparador de conteo — ruff PLR0913 con max-args=4)
  (b) el mismo grupo de parámetros se repite en ≥ 2 firmas hermanas
      (regla de los tres del shape de parámetro)

Esta regla se aplica a TODA firma de construcción, independientemente de:
  - tamaño percibido ("es solo un argumento más")
  - intención futura ("lo convierto en DTO después")
  - visibilidad ("la función es interna, nadie la llama desde afuera")

Excepción única declarada: los métodos de 1–3 parámetros y las transiciones
single-arg (ej.: `settle(on: datetime)`) están fuera del alcance del disparador
y no exigen agrupamiento.
</HARD-GATE>
```

## Alcance

- **Se aplica a:**
  - Código de aplicación Python: funciones, métodos, factories, commands de use-case e inputs de construcción (birth-params) de entidad
  - Las tres capas del hexágono: `adapters/api` (request model Pydantic), `application` (`Command` frozen), `domain` (Value Object de construcción frozen)
  - Detección de shape de parámetro repetido entre firmas hermanas (ej.: `provision()`/`adjust()` del mismo aggregate)
- **Fuera del objeto de esta Ley (referenciar, no duplicar):**
  - Duplicación de conocimiento de dominio (regla, fórmula, mapeo) → `lex-dry`
  - Inmutabilidad del tipo (`frozen=True`) → `lex-python-immutability`
  - Anotaciones de tipo completas en el DTO → `lex-python-typing`
  - Validación de input externo en el boundary (Pydantic en el borde) → `lex-python-security`
  - Higiene de comentario y dead-code → `lex-clean-code`
  - Métodos de 1–3 parámetros y transiciones single-arg (no son violación por construcción)
- **Agentes vinculados:** `warrior-apollo` (y los especialistas `warrior-apollo-api`, `warrior-apollo-jobs`, `warrior-apollo-agents`), `warrior-athena` (Gate 2 del flujo Issue-Driven), `warrior-argos` (revisión multi-eje)
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de la Violación

1. **Bloqueo automático:** `ruff PLR0913` rechaza en el pre-commit/CI la firma que excede el techo de parámetros; Gate 2 (`kata-quality-gate`) y `warrior-argos` rechazan el grupo de parámetros repetido en ≥ 2 firmas hermanas y la fuga de capa (Pydantic de la api reutilizado como VO de dominio, DTO no-frozen).
2. **Alerta:** notifica al autor del PR y al owner del bounded context afectado.
3. **Remediación:** el autor extrae el grupo al tipo de input de la capa correcta — request model Pydantic en `adapters/api`, `Command` frozen en `application`, o Value Object de construcción frozen en `domain` — y ajusta los llamadores para pasar el objeto agrupado.

## Ejemplos

### Correcto

```python
# domain — Value Object de construcción frozen; una firma, un shape nombrado
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class ProvisionInput:
    holder_id: str
    currency: str
    opening_balance: int
    credit_limit: int
    risk_tier: str

class Account:
    @classmethod
    def provision(cls, params: ProvisionInput) -> "Account":
        ...

    def adjust(self, params: ProvisionInput) -> "Account":
        ...  # las hermanas comparten el MISMO shape vía el tipo, sin volver a listar 14 args
```

```python
# application — Command frozen como input del use-case
@dataclass(frozen=True, kw_only=True)
class CreateTransferCommand:
    source_account_id: str
    target_account_id: str
    amount: int
    currency: str
    idempotency_key: str

class CreateTransferUseCase:
    async def execute(self, cmd: CreateTransferCommand) -> TransferId:
        ...
```

```python
# adapters/api — request model Pydantic en el borde (lex-python-security)
from pydantic import BaseModel, ConfigDict, Field

class CreateTransferRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_account_id: str = Field(min_length=1, max_length=36)
    target_account_id: str = Field(min_length=1, max_length=36)
    amount: int = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")

# transición single-arg — fuera del alcance, NO exige DTO
def settle(self, on: datetime) -> None:
    ...
```

### Incorrecto

```python
# domain — superficie amplia sin agrupamiento; grupo de 14 args vuelto a listar en las hermanas
class Account:
    @classmethod
    def provision(                                     # ❌ ≥ 5 params, sin input-DTO
        cls, holder_id, currency, opening_balance, credit_limit,
        risk_tier, branch_code, manager_id, opened_at, segment,
        kyc_level, tax_regime, statement_day, overdraft, notes,
    ): ...

    def adjust(                                        # ❌ mismo shape duplicado (regla de los tres)
        self, holder_id, currency, opening_balance, credit_limit,
        risk_tier, branch_code, manager_id, opened_at, segment,
        kyc_level, tax_regime, statement_day, overdraft, notes,
    ): ...
```

```python
# boundary leak — Pydantic de la api reutilizado como VO de dominio
from app.adapters.api.schemas import CreateTransferRequest

class CreateTransferUseCase:
    async def execute(self, req: CreateTransferRequest) -> TransferId:  # ❌ tipo de api se fuga a application
        ...

# DTO mutable — viola el contrato (debe ser frozen, lex-python-immutability)
@dataclass                                             # ❌ falta frozen=True
class ProvisionInput:
    holder_id: str
    currency: str
```

## Validación Automatizada

- **Herramienta:**
  - **Conteo de parámetros:** regla `PLR0913` de `ruff` (too-many-arguments) configurada con `max-args = 4` en `pyproject.toml` — dispara en el 5.º parámetro de dominio.
  - **Grupo repetido / shape duplicado:** revisión por `warrior-apollo` y auditoría por `warrior-argos` detectando el mismo grupo de parámetros en ≥ 2 firmas hermanas (no capturable solo por conteo).
  - **Taxonomía de capa / boundary leak:** `warrior-argos` verifica que el request model Pydantic de `adapters/api` no sea importado/reutilizado como input en `application` o `domain`, y que `Command` y el VO de construcción sean `frozen` (compone con `lex-python-immutability`).
- **Momento:** pre-commit (`ruff PLR0913` local), CI en todo PR, Gate 2 del flujo Issue-Driven.
- **Métrica:** 0 funciones/factories por encima del techo sin input agrupado; 0 grupos de parámetros repetidos en ≥ 2 firmas hermanas sin extracción; 0 tipos de input reutilizados entre capas (boundary leak); 100% de los commands y VOs de construcción `frozen`.
