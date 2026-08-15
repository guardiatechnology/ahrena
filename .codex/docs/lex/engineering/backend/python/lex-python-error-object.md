# Lexis: Estrutura do Objeto de Erro em Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: estrutura do valor de erro usado em falhas de Result e em respostas de erro em código Python

## Law

> **Todo valor de erro usado como payload do `Failure` de um `Result` (conforme `lex-python-result-type`) ou retornado como erro em respostas de API DEVE ser instância de um dataclass congelado `Error` com exatamente três campos: `code: str` (no formato `ERR{HTTP_CODE}_{NAME}`, ex.: `ERR400_INVALID_PARAMETER`), `reason: str` (identificador legível por máquina vindo do catálogo de razões conhecidas do projeto) e `message: str` (descrição legível por humanos). Erros específicos de domínio DEVEM herdar de `Error` e fixar `code` e `reason` como defaults a nível de classe; `message` DEVE ser fornecida na instanciação. Adicionar campos além de `code`, `reason`, `message` a `Error` ou suas subclasses é PROIBIDO. Mutar uma instância de erro é PROIBIDO.**

## Examples

### Correct

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Error:
    code: str
    reason: str
    message: str

@dataclass(frozen=True, kw_only=True)
class InvalidIdentifierError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_IDENTIFIER"

@dataclass(frozen=True, kw_only=True)
class InvalidEntityTypeError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_ENTITY_TYPE"

@dataclass(frozen=True, kw_only=True)
class InvalidTaxIdError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_TAX_ID"

# Uso:
err = InvalidTaxIdError(message="CPF '123' tem checksum inválido")
return Failure(err)
```

### Incorrect

```python
# Erro como string — sem code/reason
return Failure("invalid tax id")  # ❌

# Dict sem tipo — sem contrato
return Failure({"code": "INVALID", "msg": "bad"})  # ❌

# Campo extra fora do schema
@dataclass(frozen=True, kw_only=True)
class InvalidTaxIdError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_TAX_ID"
    tax_id: str = ""  # ❌ campo extra viola o contrato Error

# Erro mutável
@dataclass  # falta frozen=True
class MyError(Error):
    ...  # ❌
```

## Automated Validation

- **Tool:** revisão de código e verificação customizada de que todo payload de `Failure(...)` é `Error` ou subclasse; regra de lint contra campos extras em subclasses de `Error`; verificação de que as subclasses usam `frozen=True` e `kw_only=True`.
- **When:** cada PR (CI).
- **Metric:** 0 retornos `Failure` com payloads fora da hierarquia de `Error`; 0 subclasses de `Error` com campos além de `code`, `reason`, `message`; 0 subclasses de `Error` mutáveis.
