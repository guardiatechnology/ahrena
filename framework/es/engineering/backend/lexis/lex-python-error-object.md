# Lexis: Estructura del Objeto de Error en Python

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Engineering — Backend: estructura del valor de error usado en fallos de Result y en respuestas de error en código Python

## Purpose

Todo error debe llevar un identificador estable, una razón legible por máquina y un mensaje legible por humanos. Esto hace que los errores sean observables en logs, mapeables a respuestas HTTP (conforme `lex-error-handling`) e inequívocos para los consumidores. Las strings ad-hoc, las tuplas sin tipo o los diccionarios libres pierden información y no pueden evolucionar con seguridad.

## Law

> **Todo valor de error usado como payload del `Failure` de un `Result` (conforme `lex-python-result-type`) o retornado como error en respuestas de API DEBE ser instancia de un dataclass congelado `Error` con exactamente tres campos: `code: str` (en el formato `ERR{HTTP_CODE}_{NAME}`, p. ej., `ERR400_INVALID_PARAMETER`), `reason: str` (identificador legible por máquina del catálogo de razones conocidas del proyecto) y `message: str` (descripción legible por humanos). Los errores específicos de dominio DEBEN heredar de `Error` y fijar `code` y `reason` como valores por defecto a nivel de clase; `message` DEBE proporcionarse en la instanciación. Agregar campos más allá de `code`, `reason`, `message` a `Error` o sus subclases está PROHIBIDO. Mutar una instancia de error está PROHIBIDO.**

## Scope

- **Applies to:** todo código Python que produce valores de error (módulos de dominio, servicios de aplicación, capa de API).
- **Bound agents:** todos los agentes e implementadores que escriben o modifican código Python.
- **Exceptions:** los errores de terceros que entran en la aplicación DEBEN envolverse en un `Error` en la frontera. El contexto adicional de logging estructurado que enriquezca la observabilidad DEBE vivir fuera del objeto de error (en campos de log, atributos de span), nunca dentro de `Error`.

## Consequences of Violation

1. **Brecha de observabilidad:** los errores sin `code`/`reason` estable no pueden correlacionarse entre servicios ni alertarse.
2. **Quiebre del contrato de API:** las respuestas sin campos estandarizados rompen a los consumidores downstream (conforme `lex-error-handling`).
3. **Pérdida de tipado:** los payloads de error sin tipo invalidan el propósito de `Result[T, Error]`.
4. **Remediación:** definir una subclase de `Error` para el modo de fallo, proporcionar `message` en la construcción, retornar vía `Failure(...)`.

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
err = InvalidTaxIdError(message="CPF '123' tiene checksum inválido")
return Failure(err)
```

### Incorrect

```python
# Error como string — sin code/reason
return Failure("invalid tax id")  # ❌

# Dict sin tipo — sin contrato
return Failure({"code": "INVALID", "msg": "bad"})  # ❌

# Campo extra fuera del esquema
@dataclass(frozen=True, kw_only=True)
class InvalidTaxIdError(Error):
    code: str = "ERR400_INVALID_PARAMETER"
    reason: str = "INVALID_TAX_ID"
    tax_id: str = ""  # ❌ campo extra viola el contrato Error

# Error mutable
@dataclass  # falta frozen=True
class MyError(Error):
    ...  # ❌
```

## Automated Validation

- **Tool:** revisión de código y verificación personalizada de que todo payload de `Failure(...)` sea `Error` o subclase; regla de lint contra campos extras en subclases de `Error`; verificación de que las subclases usen `frozen=True` y `kw_only=True`.
- **When:** cada PR (CI).
- **Metric:** 0 retornos `Failure` con payloads fuera de la jerarquía de `Error`; 0 subclases de `Error` con campos más allá de `code`, `reason`, `message`; 0 subclases de `Error` mutables.

## References

- lex-python-result-type (engineering/backend)
- lex-python-error-handling (engineering/backend)
- lex-error-handling (engineering/platform) — estructura de error para respuestas HTTP
- codex-known-errors (engineering/platform) — registro de valores válidos de `reason`
