# Lexis: Logs por Bootstrap Centralizado y Decorator

> **Prefix:** `lex-` | **Type:** Ley Inquebrantable | **Scope:** Todo código que produce logs — backend, frontend, mobile, workers, jobs, scripts, infraestructura — en cualquier lenguaje

## Purpose

Garantizar que todo registro de log siga un patrón único, observable y auditable, independientemente del lenguaje o stack. Logs dispersos en el código de aplicación producen ruido, divergen en formato, filtran datos sensibles y hacen que la comprensión del flujo dependa de inspección manual. El patrón "bootstrap + decorator" concentra la instrumentación en la frontera de la función, mantiene el cuerpo libre de ruido operativo y produce entradas consistentes (entrada, salida, duración, excepción) en todo el codebase.

## Law

> **Todo registro de log producido por código de aplicación DEBE provenir de (a) una configuración de boot única y centralizada del logger y (b) un decorator (o el wrapper equivalente del lenguaje) aplicado a la función, método o handler. Las llamadas directas a primitivas del logger (`logger.info`, `logger.debug`, `logger.warning`, `logger.error`, `logger.exception`, `logger.critical`, `logger.success`, `console.log`, `print`, `fmt.Println`, o cualquier otra primitiva de logging) DENTRO del cuerpo de funciones de aplicación están PROHIBIDAS. Las únicas excepciones permitidas son: (1) el módulo de bootstrap que configura el logger; (2) el propio decorator/wrapper de logging; (3) handlers globales de excepción en el tope de la aplicación (HTTP exception handler, Lambda handler, worker entrypoint, error boundary).**

## Scope

- **Applies to:** todo código que produce logs en proyectos Guardia, en cualquier lenguaje (Python, TypeScript/JavaScript, Go, Kotlin, Swift, etc.) y en cualquier runtime (servidor, navegador, móvil, edge, scripts).
- **Bound agents:** todos los Warriors que escriben o modifican código (Apollo, Hephaestus, Iris, Atlas cuando produce scripts, etc.).
- **Exceptions:** Ninguna además de las tres listadas en la Ley. Las bibliotecas internas que producen logs DEBEN exponer el decorator/wrapper y NO PUEDEN instruir a los consumidores a llamar primitivas de log en el cuerpo del código.

## Consequences of Violation

1. **Bloqueo de PR:** el linter detecta una llamada directa a primitiva de log fuera de los archivos permitidos; el PR es rechazado en CI.
2. **Logs incoherentes:** dos funciones con instrumentación manual producen formatos divergentes; herramientas de búsqueda, alertas y dashboards se rompen silenciosamente.
3. **Filtración de datos sensibles:** las llamadas inline raramente pasan por redacción consistente; el decorator centraliza el allowlist/denylist de campos.
4. **Remediación:** mover la llamada al decorator (`@logged`, `withLogging(...)`, `LoggingMiddleware`, etc.) en la función; si el evento no cabe en un decorator, aplicarlo en una función auxiliar dedicada; nunca evadir con supresión de lint (`# noqa`, `// eslint-disable`, `//nolint`).

## Examples

### Correct

```python
# Python — cuerpo limpio, instrumentación en el decorator
from app.shared.logging import logged


class CreateTransferUseCase:
    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

```typescript
// TypeScript — wrapper centralizado, cuerpo sin llamadas de log
import { logged } from "@app/shared/logging";

export const createTransfer = logged(
  { operation: "transfer.create" },
  async (input: CreateTransferInput): Promise<TransferId> => {
    const transfer = await repository.create(input);
    return transfer.entityId;
  },
);
```

```python
# Handler global de excepción — excepción permitida por la Ley
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.opt(exception=exc).error("unhandled_exception path={}", request.url.path)
    return JSONResponse(status_code=500, content={"errors": [{"code": "INTERNAL_ERROR"}]})
```

### Incorrect

```python
# Llamada inline en medio de la regla de negocio — VIOLA LA LEY
from loguru import logger


async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
    logger.info("creating transfer source={} target={}", source_id, target_id)  # ❌
    transfer = await self._repository.create(source_id, target_id, amount)
    logger.info("transfer created {}", transfer.entity_id)  # ❌
    return transfer.entity_id
```

```typescript
// console.log en código de aplicación — VIOLA LA LEY
export async function createTransfer(input: CreateTransferInput): Promise<TransferId> {
  console.log("creating transfer", input); // ❌
  const transfer = await repository.create(input);
  return transfer.entityId;
}
```

```python
# print() en producción — VIOLA LA LEY
def calculate_fee(amount: int) -> int:
    print(f"calculating fee for {amount}")  # ❌
    return int(amount * 0.015)
```

```go
// fmt.Println usado para log — VIOLA LA LEY
func CreateTransfer(ctx context.Context, in CreateTransferInput) (TransferID, error) {
    fmt.Println("creating transfer", in) // ❌
    return repository.Create(ctx, in)
}
```

## Automated Validation

- **Tool:**
  - **Python:** Ruff (`flake8-print` para `T201/T203`) + AST check en pre-commit detectando `logger.<level>(` en archivos fuera de un allowlist leído de `pyproject.toml`.
  - **TypeScript/JavaScript:** ESLint con `no-console` (error) y regla personalizada que bloquea imports directos de loggers fuera de los módulos permitidos.
  - **Go:** lint personalizado (golangci-lint + `forbidigo`) bloqueando `fmt.Print*`, `log.Print*`, y llamadas de logger fuera de los paquetes permitidos.
  - El allowlist por lenguaje se declara en el archivo de configuración del proyecto (ej.: `pyproject.toml`, `.eslintrc`, `.golangci.yaml`) bajo la clave `ahrena.logging.allowed_modules`.
- **When:** cada commit (pre-commit) y cada PR (CI).
- **Metric:** 0 llamadas a primitiva de log fuera de los módulos permitidos; 0 supresiones de lint relacionadas con logging sin ADR.

## References

- codex-python-logging (engineering/backend) — implementación para Python con `loguru`
- kata-python-logging-setup (engineering/backend) — procedimiento de configuración para Python
- lex-observability-required (_foundation/quality) — señales (trace, metric, log) por surface runtime
- lex-python-error-handling (engineering/backend) — las excepciones no pueden ser engullidas
- lex-python-security (engineering/backend) — prohibición de loguear PII y secretos
- lex-frontend-security (engineering/frontend) — equivalente para frontend
