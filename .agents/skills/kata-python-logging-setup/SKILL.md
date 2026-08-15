---
name: kata-python-logging-setup
description: "Configuração de Logging Python com Loguru e Decorator. Engineering — Backend: instalação e configuração do padrão de logging em uma aplicação Python"
---

# Kata: Configuração de Logging Python com Loguru e Decorator

> **Prefix:** `kata-` | **Type:** Habilidade Repetível | **Scope:** Engineering — Backend: instalação e configuração do padrão de logging em uma aplicação Python

## Workflow

```
Progress:
- [ ] 1. Adicionar dependências (loguru, orjson) e remover concorrentes
- [ ] 2. Criar módulo de bootstrap (setup_logging) e sink JSON
- [ ] 3. Implementar o decorator @logged (sync e async)
- [ ] 4. Integrar com OpenTelemetry e middleware de correlação
- [ ] 5. Refatorar chamadas inline existentes para usar @logged
- [ ] 6. Configurar lint (Ruff + AST check) bloqueando chamadas inline
- [ ] 7. Validação final (testes, lint, smoke de log estruturado)
```

### Step 1: Adicionar Dependências e Remover Concorrentes

1. Adicionar ao `pyproject.toml`:
   ```toml
   [project]
   dependencies = [
     "loguru>=0.7",
     "orjson>=3.10",
     "opentelemetry-instrumentation-logging>=0.46b0",
   ]
   ```
2. Remover `structlog`, `python-json-logger` e qualquer wrapper de `logging` (stdlib) das dependências da aplicação.
3. Rodar `uv sync` (ou equivalente) e confirmar que o lockfile foi atualizado.
4. Buscar no codebase usos remanescentes:
   ```powershell
   Select-String -Path "**/*.py" -Pattern "import logging|import structlog|from structlog"
   ```
5. Listar arquivos encontrados; eles serão tratados no Passo 5.

### Step 2: Criar o Módulo de Bootstrap e o Sink JSON

1. Criar a estrutura:
   ```
   <package_root>/shared/logging/
   ├── __init__.py
   ├── setup.py
   ├── serializer.py
   └── decorator.py
   ```
2. `__init__.py` exporta apenas `logger`, `logged` e `setup_logging`.
3. `setup.py` define `setup_logging(service_name, level)`:
   - Remove sinks default (`logger.remove()`)
   - Configura `extra={"service": service_name}`
   - Adiciona sink stdout (formato legível) e sink JSON (`json_sink` do `serializer.py`)
   - `backtrace=False`, `diagnose=False` (segurança)
4. `serializer.py` define:
   - `DENY` set com nomes de campo sensíveis padrão (`password`, `token`, `secret`, `api_key`, `authorization`, `cookie`, `cpf`, `ssn`)
   - Função `_redact(payload)` aplicando substituição por `[REDACTED]`
   - Função `json_sink(message)` que extrai `record`, monta payload com `timestamp`, `level`, `service`, `logger`, `message`, `trace_id`, `span_id`, `correlation_id`, `operation`, `outcome`, `duration_ms`, `args` redatados, e exceção (apenas tipo + valor) — vide `codex-python-logging` para implementação completa.
5. Concatenar a allowlist do projeto com a `DENY` global (Input 4).

### Step 3: Implementar o Decorator @logged

1. Em `decorator.py`, implementar `logged(operation, level="INFO", capture_args=True, redact=())`. Usar `asyncio.iscoroutinefunction` para escolher wrapper sync/async.
2. Para cada chamada, o wrapper:
   - Vincula args com `inspect.signature.bind_partial`
   - Remove `self` e `cls`
   - Aplica redação por nome (parâmetro `redact`)
   - Mede `time.perf_counter()` antes/depois
   - Loga `enter` antes da execução (nível parametrizado)
   - Em sucesso, loga `exit` com `duration_ms`
   - Em exceção, loga `error` com `logger.opt(exception=True)` e re-lança
   - Usa `logger.contextualize(operation=..., args=..., outcome=..., duration_ms=...)` em cada emissão
3. Implementação completa de referência: `codex-python-logging`.
4. Escrever testes unitários para o decorator:
   - Função sync: emite enter+exit em sucesso; emite enter+error em exceção; re-lança a exceção.
   - Função async: idem.
   - Argumentos sensíveis em `redact` são substituídos por `[REDACTED]`.
   - `capture_args=False` produz `args={}`.
   - `duration_ms` está presente no record de saída.

### Step 4: Integrar com OpenTelemetry e Middleware de Correlação

1. Em `setup.py` da aplicação (entrypoint), após `setup_logging`, instrumentar logging:
   ```python
   from opentelemetry.instrumentation.logging import LoggingInstrumentor
   LoggingInstrumentor().instrument(set_logging_format=True)
   ```
2. Criar middleware `CorrelationMiddleware` em `infrastructure/http/middleware/correlation.py`:
   - Lê header `x-correlation-id`; gera UUID se ausente
   - Envolve `call_next` em `logger.contextualize(correlation_id=...)`
   - Espelha o header na response
3. Registrar o middleware na app FastAPI **antes** de qualquer router.
4. Para workers/Lambda: o entrypoint do handler abre o `logger.contextualize` com `correlation_id` extraído do evento (`requestContext.requestId`, `messageAttributes.correlationId`, etc.).

### Step 5: Refatorar Chamadas Inline Existentes

1. Para cada arquivo identificado no Passo 1.4 e qualquer arquivo com `logger.info(`, `logger.debug(`, `logger.warning(`, `logger.error(`, `logger.exception(`, `logger.critical(`, `logger.success(`, ou `print(`:
   - Identificar a função onde a chamada vive.
   - Aplicar `@logged(operation="<domain>.<action>")` à função.
   - Remover as chamadas inline.
   - Se a chamada loga uma variável intermediária impossível de capturar via decorator, extrair a operação para uma função auxiliar dedicada e decorá-la — não manter a chamada inline.
2. Para handlers globais (FastAPI exception handler, Lambda outer handler, worker entrypoint exception block), manter a chamada direta a `loguru` (uso permitido pela Lei).
3. Confirmar via grep que `logger.<level>(` e `print(` aparecem apenas em:
   - `<package_root>/shared/logging/setup.py`
   - `<package_root>/shared/logging/decorator.py`
   - `<package_root>/shared/logging/serializer.py`
   - Arquivos de handlers globais explicitamente listados.

### Step 6: Configurar Lint Bloqueando Chamadas Inline

1. Em `pyproject.toml`, adicionar configuração Ruff:
   ```toml
   [tool.ruff.lint]
   select = ["E", "F", "T20", "TID"]  # T20 = flake8-print

   [tool.ahrena.logging]
   allowed_modules = [
     "<package_root>.shared.logging.setup",
     "<package_root>.shared.logging.decorator",
     "<package_root>.shared.logging.serializer",
     "<package_root>.infrastructure.http.exception_handlers",
   ]
   ```
2. Adicionar AST check no pre-commit (`scripts/check_logging.py`) que:
   - Percorre `*.py` na aplicação
   - Lê `[tool.ahrena.logging.allowed_modules]`
   - Falha se encontrar `Attribute` de nome em `{info, debug, warning, error, exception, critical, success, trace}` cujo objeto é resolvido para `logger` (loguru ou stdlib) fora da allowlist
   - Falha em `Call` para `print` em arquivos não-allowlist
3. Plugar o script em `.pre-commit-config.yaml`:
   ```yaml
   - repo: local
     hooks:
       - id: check-logging
         name: Check logging policy
         entry: python scripts/check_logging.py
         language: system
         types: [python]
   ```
4. Rodar `pre-commit run --all-files` para validar.

### Step 7: Validação Final

Antes de concluir, verificar:

- [ ] `loguru` e `orjson` aparecem em `pyproject.toml`; `structlog` e `python-json-logger` não aparecem.
- [ ] `setup_logging("<service-name>")` é chamado uma única vez no entrypoint.
- [ ] `@logged(operation="...")` está aplicado a todos os casos de uso, repositórios e endpoints HTTP.
- [ ] `grep -rn "logger\.\(info\|debug\|warning\|error\|exception\|critical\|success\)" <package_root>` retorna apenas arquivos da allowlist.
- [ ] `grep -rn "^[^#]*print(" <package_root>` retorna apenas o `serializer.py`.
- [ ] Testes do decorator passam (`pytest tests/shared/logging/`).
- [ ] Smoke: subir o serviço local, fazer um request, verificar no stdout um JSON contendo `operation`, `outcome=exit`, `duration_ms`, `trace_id`, `correlation_id`.
- [ ] Smoke negativo: provocar exceção em endpoint, verificar JSON com `outcome=error`, `exception.type`, `exception.value` e ausência de traceback completo.
- [ ] `pre-commit run --all-files` passa sem warnings de logging.
- [ ] PR vincula a Issue (lex-issue-first) e o body referencia `lex-logging-decorator` e `codex-python-logging`.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Módulo de bootstrap | Código Python | `<package_root>/shared/logging/setup.py` |
| Sink JSON com redação | Código Python | `<package_root>/shared/logging/serializer.py` |
| Decorator `@logged` | Código Python | `<package_root>/shared/logging/decorator.py` |
| Middleware de correlação | Código Python | `<package_root>/infrastructure/http/middleware/correlation.py` |
| Configuração de lint | Bloco TOML | `pyproject.toml` (`[tool.ruff.lint]`, `[tool.ahrena.logging]`) |
| AST check | Script Python | `scripts/check_logging.py` |
| Hook pre-commit | YAML | `.pre-commit-config.yaml` |
| Testes do decorator | Código Python | `tests/shared/logging/test_decorator.py` |

## Exemplo de Execução

### Input de Exemplo

```
Pacote raiz: app/
Serviço: transfer-api
Nível default: INFO
Campos sensíveis adicionais: card_number, account_number
```

### Output de Exemplo

```
✓ pyproject.toml: loguru, orjson, opentelemetry-instrumentation-logging adicionados
✓ Removidos: structlog, python-json-logger
✓ Criados:
  - app/shared/logging/setup.py
  - app/shared/logging/serializer.py (DENY estendida com card_number, account_number)
  - app/shared/logging/decorator.py
  - app/shared/logging/__init__.py
  - app/infrastructure/http/middleware/correlation.py
  - scripts/check_logging.py
  - tests/shared/logging/test_decorator.py
✓ Refatorados (chamadas inline removidas):
  - app/application/transfers/use_cases.py
  - app/application/reconciliation/runner.py
  - app/infrastructure/http/routers/transfers.py
✓ Lint configurado: pre-commit detecta logger.* e print() fora da allowlist
✓ Smoke local:
  {"timestamp":"2026-04-29T18:12:03.412+00:00","level":"INFO","service":"transfer-api","operation":"transfer.create","outcome":"exit","duration_ms":42.81,"trace_id":"4bf92f3577b34da6...","correlation_id":"a1b2-..."}
```

## Restrições

- Não introduzir wrappers próprios sobre `loguru` que reexportem `logger.info`/`logger.error` para o restante do código — isso burla a Lei. Apenas `setup_logging`, `logged` e (em arquivos da allowlist) `logger` direto são exportados.
- Não usar `logger.bind(...)` no corpo da função para "marcar contexto" — `bind` cria um logger acoplado mas continua exigindo chamada inline. Usar `logger.contextualize` apenas dentro do decorator/middleware.
- Não desligar `backtrace`/`diagnose` apenas em alguns sinks — eles ficam `False` em todos os sinks de produção. Em dev, podem ser habilitados via flag explícita por variável de ambiente.
- Não adicionar `# noqa: T201` ou supressões equivalentes para manter `print` ou chamadas inline. Se há um caso real, abrir ADR antes de criar exceção.
- A allowlist em `[tool.ahrena.logging.allowed_modules]` é parte do contrato do projeto. Mudanças exigem PR dedicado e revisão de quem mantém o módulo de logging.
