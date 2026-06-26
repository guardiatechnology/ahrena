# Lexis: Input-DTO (Parameter Object para Superfícies de Construção)

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Engenharia — Backend: assinaturas de funções, métodos, factories, commands de use-case e inputs de construção de entidade em código Python

## Propósito

Superfícies de construção grandes — uma factory de domínio com 19 kwargs, um par `provision()`/`adjust()` repetindo os mesmos 14 argumentos — são um smell estrutural distinto da duplicação de conhecimento de domínio. `lex-dry` governa a regra de negócio (a fórmula, a validação, o mapeamento); ela não cobre o *shape de construção* — o conjunto de parâmetros que sempre viajam juntos e se re-listam entre assinaturas irmãs. Esse shape, quando não nomeado, dispersa: cada chamador reordena argumentos posicionais, cada assinatura irmã copia o grupo, e adicionar um campo obriga editar N pontos. O Parameter Object (input-DTO) torna o contrato de construção um tipo único, tipado e imutável, ligado à camada do hexágono onde nasce. Esta Lei impõe o agrupamento onde o custo é real (superfície ampla ou grupo repetido) sem cair no smell inverso — um DTO para uma função de dois argumentos é cerimônia, não coesão.

## Lei

> **Toda função, método ou factory que (1) recebe ≥ 5 parâmetros de domínio, (2) compartilha o mesmo grupo de parâmetros com ≥ 2 assinaturas irmãs (regra dos três do shape de parâmetro), ou (3) representa um command de use-case ou input de birth/factory de entidade DEVE agrupar esses parâmetros em um tipo de input dedicado e imutável (frozen). O tipo DEVE respeitar a camada do hexágono em que vive — Pydantic request model em `adapters/api`, `Command` frozen em `application`, Value Object de construção frozen em `domain` — sem reutilizar o tipo de uma camada em outra. Input-DTO mutável, anêmico (espelha todo argumento sem coesão) ou reusado entre camadas (boundary leak) é PROIBIDO. Métodos de 1–3 parâmetros e transições single-arg (ex.: `settle(on: datetime)`) NÃO exigem agrupamento.**

```
<HARD-GATE>
warrior-apollo, warrior-athena (Gate 2) e qualquer agente que implemente
ou revise código Python NÃO PODEM aprovar assinatura de construção que
dispare um gatilho objetivo de superfície sem que os parâmetros estejam
agrupados em um tipo de input dedicado.

Pré-condições obrigatórias (basta UMA disparar para obrigar o agrupamento):
  (a) a assinatura recebe ≥ 5 parâmetros de domínio
      (gatilho de contagem — ruff PLR0913 com max-args=4)
  (b) o mesmo grupo de parâmetros se repete em ≥ 2 assinaturas irmãs
      (regra dos três do shape de parâmetro)

Esta regra aplica-se a TODA assinatura de construção, independentemente de:
  - tamanho percebido ("é só um argumento a mais")
  - intenção futura ("viro DTO depois")
  - visibilidade ("a função é interna, ninguém chama de fora")

Exceção única declarada: métodos de 1–3 parâmetros e transições single-arg
(ex.: `settle(on: datetime)`) estão fora do escopo do gatilho e não exigem
agrupamento.
</HARD-GATE>
```

## Abrangência

- **Aplica-se a:**
  - Código de aplicação Python: funções, métodos, factories, commands de use-case e inputs de construção (birth-params) de entidade
  - As três camadas do hexágono: `adapters/api` (request model Pydantic), `application` (`Command` frozen), `domain` (Value Object de construção frozen)
  - Detecção de shape de parâmetro repetido entre assinaturas irmãs (ex.: `provision()`/`adjust()` da mesma agregada)
- **Fora do objeto desta Lei (referenciar, não duplicar):**
  - Duplicação de conhecimento de domínio (regra, fórmula, mapeamento) → `lex-dry`
  - Imutabilidade do tipo (`frozen=True`) → `lex-python-immutability`
  - Anotações de tipo completas no DTO → `lex-python-typing`
  - Validação de input externo no boundary (Pydantic na borda) → `lex-python-security`
  - Higiene de comentário e dead-code → `lex-clean-code`
  - Métodos de 1–3 parâmetros e transições single-arg (não são violação por construção)
- **Agentes vinculados:** `warrior-apollo` (e os especialistas `warrior-apollo-api`, `warrior-apollo-jobs`, `warrior-apollo-agents`), `warrior-athena` (Gate 2 do fluxo Issue-Driven), `warrior-argos` (revisão multi-eixo)
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Bloqueio automático:** `ruff PLR0913` reprova no pre-commit/CI a assinatura que excede o teto de parâmetros; Gate 2 (`kata-quality-gate`) e `warrior-argos` reprovam o grupo de parâmetros repetido em ≥ 2 assinaturas irmãs e o vazamento de camada (Pydantic da api reusado como VO de domínio, DTO não-frozen).
2. **Alerta:** notifica o autor do PR e o owner do bounded context afetado.
3. **Remediação:** o autor extrai o grupo para o tipo de input da camada correta — request model Pydantic em `adapters/api`, `Command` frozen em `application`, ou Value Object de construção frozen em `domain` — e ajusta os chamadores para passar o objeto agrupado.

## Exemplos

### Correto

```python
# domain — Value Object de construção frozen; uma assinatura, um shape nomeado
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
        ...  # irmãs compartilham o MESMO shape via o tipo, sem re-listar 14 args
```

```python
# application — Command frozen como input do use-case
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
# adapters/api — request model Pydantic na borda (lex-python-security)
from pydantic import BaseModel, ConfigDict, Field

class CreateTransferRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_account_id: str = Field(min_length=1, max_length=36)
    target_account_id: str = Field(min_length=1, max_length=36)
    amount: int = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")

# transição single-arg — fora do escopo, NÃO exige DTO
def settle(self, on: datetime) -> None:
    ...
```

### Incorreto

```python
# domain — superfície ampla sem agrupamento; grupo de 14 args re-listado nas irmãs
class Account:
    @classmethod
    def provision(                                     # ❌ ≥ 5 params, sem input-DTO
        cls, holder_id, currency, opening_balance, credit_limit,
        risk_tier, branch_code, manager_id, opened_at, segment,
        kyc_level, tax_regime, statement_day, overdraft, notes,
    ): ...

    def adjust(                                        # ❌ mesmo shape duplicado (regra dos três)
        self, holder_id, currency, opening_balance, credit_limit,
        risk_tier, branch_code, manager_id, opened_at, segment,
        kyc_level, tax_regime, statement_day, overdraft, notes,
    ): ...
```

```python
# boundary leak — Pydantic da api reusado como VO de domínio
from app.adapters.api.schemas import CreateTransferRequest

class CreateTransferUseCase:
    async def execute(self, req: CreateTransferRequest) -> TransferId:  # ❌ tipo de api vaza p/ application
        ...

# DTO mutável — viola o contrato (deve ser frozen, lex-python-immutability)
@dataclass                                             # ❌ falta frozen=True
class ProvisionInput:
    holder_id: str
    currency: str
```

## Validação Automatizada

- **Ferramenta:**
  - **Contagem de parâmetros:** `ruff` regra `PLR0913` (too-many-arguments) configurada com `max-args = 4` em `pyproject.toml` — dispara no 5º parâmetro de domínio.
  - **Grupo repetido / shape duplicado:** revisão por `warrior-apollo` e auditoria por `warrior-argos` detectando o mesmo grupo de parâmetros em ≥ 2 assinaturas irmãs (não capturável só por contagem).
  - **Taxonomia de camada / boundary leak:** `warrior-argos` verifica que o request model Pydantic de `adapters/api` não é importado/reusado como input em `application` ou `domain`, e que `Command` e VO de construção são `frozen` (compõe com `lex-python-immutability`).
- **Momento:** pre-commit (`ruff PLR0913` local), CI em todo PR, Gate 2 do fluxo Issue-Driven.
- **Métrica:** 0 funções/factories acima do teto sem input agrupado; 0 grupos de parâmetros repetidos em ≥ 2 assinaturas irmãs sem extração; 0 tipos de input reusados entre camadas (boundary leak); 100% dos commands e VOs de construção `frozen`.
