# Lexis: Logs via Centralized Bootstrap and Decorator

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All code that produces logs — backend, frontend, mobile, workers, jobs, scripts, infrastructure — in any language

## Purpose

Ensure every log entry follows a single, observable, and auditable pattern, regardless of language or stack. Logs scattered across application code produce noise, diverge in format, leak sensitive data, and make flow understanding dependent on manual inspection. The "bootstrap + decorator" pattern concentrates instrumentation at the function boundary, keeps the body free of operational noise, and produces consistent entries (enter, exit, duration, exception) across the entire codebase.

## Law

> **Every log entry produced by application code MUST come from (a) a single centralized boot configuration of the logger and (b) a decorator (or the language's equivalent wrapper) applied to the function, method, or handler. Direct calls to logger primitives (`logger.info`, `logger.debug`, `logger.warning`, `logger.error`, `logger.exception`, `logger.critical`, `logger.success`, `console.log`, `print`, `fmt.Println`, or any other logging primitive) INSIDE the body of application functions are FORBIDDEN. The only allowed exceptions are: (1) the bootstrap module that configures the logger; (2) the logging decorator/wrapper itself; (3) global exception handlers at the top of the application (HTTP exception handler, Lambda handler, worker entrypoint, error boundary).**

## Scope

- **Applies to:** all code that produces logs in Guardia projects, in any language (Python, TypeScript/JavaScript, Go, Kotlin, Swift, etc.) and any runtime (server, browser, mobile, edge, scripts).
- **Bound agents:** all Warriors that write or modify code (Apollo, Hephaestus, Iris, Atlas when producing scripts, etc.).
- **Exceptions:** None beyond the three listed in the Law. Internal libraries that emit logs MUST expose the decorator/wrapper and MUST NOT instruct consumers to call log primitives in their code body.

## Consequences of Violation

1. **PR block:** lint detects a direct call to a log primitive outside the allowed files; the PR is rejected in CI.
2. **Inconsistent logs:** two functions with manual instrumentation produce divergent formats; search tools, alerts, and dashboards break silently.
3. **Sensitive data leakage:** inline calls rarely go through consistent redaction; the decorator centralizes the field allowlist/denylist.
4. **Remediation:** move the call into the decorator (`@logged`, `withLogging(...)`, `LoggingMiddleware`, etc.) on the function; if the event does not fit a decorator, apply it on a dedicated helper function; never bypass with lint suppression (`# noqa`, `// eslint-disable`, `//nolint`).

## Examples

### Correct

```python
# Python — clean body, instrumentation in the decorator
from app.shared.logging import logged


class CreateTransferUseCase:
    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

```typescript
// TypeScript — centralized wrapper, body without log calls
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
# Global exception handler — exception allowed by the Law
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.opt(exception=exc).error("unhandled_exception path={}", request.url.path)
    return JSONResponse(status_code=500, content={"errors": [{"code": "INTERNAL_ERROR"}]})
```

### Incorrect

```python
# Inline call inside business rule — VIOLATES THE LAW
from loguru import logger


async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
    logger.info("creating transfer source={} target={}", source_id, target_id)  # ❌
    transfer = await self._repository.create(source_id, target_id, amount)
    logger.info("transfer created {}", transfer.entity_id)  # ❌
    return transfer.entity_id
```

```typescript
// console.log in application code — VIOLATES THE LAW
export async function createTransfer(input: CreateTransferInput): Promise<TransferId> {
  console.log("creating transfer", input); // ❌
  const transfer = await repository.create(input);
  return transfer.entityId;
}
```

```python
# print() in production — VIOLATES THE LAW
def calculate_fee(amount: int) -> int:
    print(f"calculating fee for {amount}")  # ❌
    return int(amount * 0.015)
```

```go
// fmt.Println used for logging — VIOLATES THE LAW
func CreateTransfer(ctx context.Context, in CreateTransferInput) (TransferID, error) {
    fmt.Println("creating transfer", in) // ❌
    return repository.Create(ctx, in)
}
```

## Automated Validation

- **Tool:**
  - **Python:** Ruff (`flake8-print` for `T201/T203`) + pre-commit AST check detecting `logger.<level>(` in files outside an allowlist read from `pyproject.toml`.
  - **TypeScript/JavaScript:** ESLint with `no-console` (error) and a custom rule blocking direct logger imports outside the allowed modules.
  - **Go:** custom lint (golangci-lint + `forbidigo`) blocking `fmt.Print*`, `log.Print*`, and logger calls outside allowed packages.
  - The per-language allowlist is declared in the project configuration file (e.g., `pyproject.toml`, `.eslintrc`, `.golangci.yaml`) under `ahrena.logging.allowed_modules`.
- **When:** every commit (pre-commit) and every PR (CI).
- **Metric:** 0 calls to log primitives outside allowed modules; 0 logging-related lint suppressions without an ADR.

## References

- codex-python-logging (engineering/backend) — Python implementation with `loguru`
- kata-python-logging-setup (engineering/backend) — setup procedure for Python
- lex-observability-required (_foundation/quality) — signals (trace, metric, log) per runtime surface
- lex-python-error-handling (engineering/backend) — exceptions must not be swallowed
- lex-python-security (engineering/backend) — no PII or secrets in logs
- lex-frontend-security (engineering/frontend) — equivalent for frontend
