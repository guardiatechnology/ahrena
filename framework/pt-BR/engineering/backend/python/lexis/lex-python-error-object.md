# Lexis: Estrutura do Objeto de Erro em Python

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Engineering — Backend: estrutura do valor de erro usado em falhas de Result e em respostas de erro em código Python

## Purpose

Todo erro precisa carregar um identificador estável, uma razão legível por máquina e uma mensagem legível por humanos. Isso torna os erros observáveis em logs, mapeáveis para respostas HTTP (conforme `lex-error-handling`) e inequívocos para consumidores. Strings ad-hoc, tuplas sem tipo ou dicionários livres perdem informação e não podem evoluir com segurança.

## Law

> **Todo valor de erro usado como payload do `Failure` de um `Result` (conforme `lex-python-result-type`) ou retornado como erro em respostas de API DEVE ser instância de um dataclass congelado `Error` com exatamente três campos: `code: str` (no formato `ERR{HTTP_CODE}_{NAME}`, ex.: `ERR400_INVALID_PARAMETER`), `reason: str` (identificador legível por máquina vindo do catálogo de razões conhecidas do projeto) e `message: str` (descrição legível por humanos). Erros específicos de domínio DEVEM herdar de `Error` e fixar `code` e `reason` como defaults a nível de classe; `message` DEVE ser fornecida na instanciação. Adicionar campos além de `code`, `reason`, `message` a `Error` ou suas subclasses é PROIBIDO. Mutar uma instância de erro é PROIBIDO.**

## Scope

- **Applies to:** todo código Python que produz valores de erro (módulos de domínio, serviços de aplicação, camada de API).
- **Bound agents:** todos os agentes e implementadores que escrevem ou modificam código Python.
- **Exceptions:** erros de terceiros que entram na aplicação DEVEM ser envolvidos em um `Error` na fronteira. Contexto adicional de logging estruturado que enriqueça a observabilidade DEVE viver fora do objeto de erro (em campos de log, atributos de span), nunca dentro de `Error`.

## Consequences of Violation

1. **Lacuna de observabilidade:** erros sem `code`/`reason` estável não podem ser correlacionados entre serviços nem alertados.
2. **Quebra do contrato de API:** respostas sem campos padronizados quebram consumidores downstream (conforme `lex-error-handling`).
3. **Perda de tipagem:** payloads de erro sem tipo invalidam o propósito de `Result[T, Error]`.
4. **Remediação:** definir uma subclasse de `Error` para o modo de falha, fornecer `message` na construção, retornar via `Failure(...)`.

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

## References

- lex-python-result-type (engineering/backend)
- lex-python-error-handling (engineering/backend)
- lex-error-handling (engineering/platform) — estrutura de erro para respostas HTTP
- codex-known-errors (engineering/platform) — registro de valores válidos de `reason`
