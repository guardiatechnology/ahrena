# Lexis: Logs por Bootstrap Centralizado e Decorator

> **Prefix:** `lex-` | **Type:** Lei Inquebrantável | **Scope:** Todo código que produz logs — backend, frontend, mobile, workers, jobs, scripts, infraestrutura — em qualquer linguagem

## Law

> **Todo registro de log produzido por código de aplicação DEVE vir de (a) configuração de boot única e centralizada do logger e (b) decorator (ou wrapper equivalente da linguagem) aplicado à função, método ou handler. Chamadas diretas a métodos do logger (`logger.info`, `logger.debug`, `logger.warning`, `logger.error`, `logger.exception`, `logger.critical`, `logger.success`, `console.log`, `print`, `fmt.Println`, ou qualquer outra primitiva de logging) DENTRO do corpo de funções de aplicação são PROIBIDAS. As únicas exceções permitidas são: (1) o módulo de bootstrap que configura o logger; (2) o próprio decorator/wrapper de logging; (3) handlers globais de exceção no topo da aplicação (HTTP exception handler, Lambda handler, worker entrypoint, error boundary).**

## Examples

### Correct

```python
# Python — corpo limpo, instrumentação no decorator
from app.shared.logging import logged

class CreateTransferUseCase:
    @logged(operation="transfer.create")
    async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
        transfer = await self._repository.create(source_id, target_id, amount)
        return transfer.entity_id
```

```typescript
// TypeScript — wrapper centralizado, corpo sem chamadas de log
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
# Handler global de exceção — exceção permitida pela Lei
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.opt(exception=exc).error("unhandled_exception path={}", request.url.path)
    return JSONResponse(status_code=500, content={"errors": [{"code": "INTERNAL_ERROR"}]})
```

### Incorrect

```python
# Chamada inline no meio da regra de negócio — VIOLA A LEI
from loguru import logger

async def execute(self, source_id: UUID, target_id: UUID, amount: int) -> UUID:
    logger.info("creating transfer source={} target={}", source_id, target_id)  # ❌
    transfer = await self._repository.create(source_id, target_id, amount)
    logger.info("transfer created {}", transfer.entity_id)  # ❌
    return transfer.entity_id
```

```typescript
// console.log em código de aplicação — VIOLA A LEI
export async function createTransfer(input: CreateTransferInput): Promise<TransferId> {
  console.log("creating transfer", input); // ❌
  const transfer = await repository.create(input);
  return transfer.entityId;
}
```

```python
# print() em produção — VIOLA A LEI
def calculate_fee(amount: int) -> int:
    print(f"calculating fee for {amount}")  # ❌
    return int(amount * 0.015)
```

```go
// fmt.Println usado para log — VIOLA A LEI
func CreateTransfer(ctx context.Context, in CreateTransferInput) (TransferID, error) {
    fmt.Println("creating transfer", in) // ❌
    return repository.Create(ctx, in)
}
```

## Automated Validation

- **Tool:**
  - **Python:** Ruff (`flake8-print` para `T201/T203`) + AST check no pre-commit detectando `logger.<level>(` em arquivos fora de uma allowlist lida de `pyproject.toml`.
  - **TypeScript/JavaScript:** ESLint com `no-console` (erro) e regra customizada que bloqueia imports diretos de loggers fora dos módulos permitidos.
  - **Go:** lint customizado (golangci-lint + `forbidigo`) bloqueando `fmt.Print*`, `log.Print*`, e chamadas de logger fora dos pacotes permitidos.
  - Allowlist por linguagem é declarada em arquivo de configuração do projeto (ex.: `pyproject.toml`, `.eslintrc`, `.golangci.yaml`) sob a chave `ahrena.logging.allowed_modules`.
- **When:** cada commit (pre-commit) e cada PR (CI).
- **Metric:** 0 chamadas a primitiva de log fora dos módulos permitidos; 0 supressões de lint relacionadas a logging sem ADR.
