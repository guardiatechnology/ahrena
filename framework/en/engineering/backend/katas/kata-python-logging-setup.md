# Kata: Python Logging Setup with Loguru and Decorator

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Backend: installation and setup of the logging pattern in a Python application

## Objective

This Kata defines the procedure to make a Python application ready to record logs per `lex-logging-decorator`: install `loguru`, create the bootstrap module, implement the `@logged` decorator, integrate with OpenTelemetry and FastAPI, enable lint that blocks inline calls, and validate end-to-end.

## When to Use

- In a Python service that has not adopted the logging pattern yet (no `loguru` configured, or using `logging`/`structlog`/`print` in code body).
- When starting a new Python service from the standard template.
- When remediating a violation detected in PR review (inline call or direct logger import).
- When invoked by `cry-python-implement` with observability scope or by Warrior Apollo.

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Application root package path | Yes | E.g., `app/`, `src/myservice/` |
| Service name | Yes | Stable identifier (e.g., `transfer-api`); used in `service` field |
| Default log level | No | `INFO` by default; `DEBUG` only in non-prod environments |
| Additional sensitive fields | No | Complements the sink's global denylist (e.g., `card_number`, `tax_id`) |

## Workflow

```
Progress:
- [ ] 1. Add dependencies (loguru, orjson) and remove competitors
- [ ] 2. Create the bootstrap module (setup_logging) and JSON sink
- [ ] 3. Implement the @logged decorator (sync and async)
- [ ] 4. Integrate with OpenTelemetry and correlation middleware
- [ ] 5. Refactor existing inline calls to use @logged
- [ ] 6. Configure lint (Ruff + AST check) blocking inline calls
- [ ] 7. Final validation (tests, lint, structured-log smoke)
```

### Step 1: Add Dependencies and Remove Competitors

1. Add to `pyproject.toml`:
   ```toml
   [project]
   dependencies = [
     "loguru>=0.7",
     "orjson>=3.10",
     "opentelemetry-instrumentation-logging>=0.46b0",
   ]
   ```
2. Remove `structlog`, `python-json-logger`, and any wrapper around stdlib `logging` from application dependencies.
3. Run `uv sync` (or equivalent) and confirm the lockfile updated.
4. Search the codebase for remaining usages:
   ```powershell
   Select-String -Path "**/*.py" -Pattern "import logging|import structlog|from structlog"
   ```
5. List the files found; they will be handled in Step 5.

### Step 2: Create the Bootstrap Module and JSON Sink

1. Create the structure:
   ```
   <package_root>/shared/logging/
   ├── __init__.py
   ├── setup.py
   ├── serializer.py
   └── decorator.py
   ```
2. `__init__.py` exports only `logger`, `logged`, and `setup_logging`.
3. `setup.py` defines `setup_logging(service_name, level)`:
   - Removes default sinks (`logger.remove()`)
   - Configures `extra={"service": service_name}`
   - Adds stdout sink (readable format) and JSON sink (`json_sink` from `serializer.py`)
   - `backtrace=False`, `diagnose=False` (security)
4. `serializer.py` defines:
   - `DENY` set with default sensitive field names (`password`, `token`, `secret`, `api_key`, `authorization`, `cookie`, `cpf`, `ssn`)
   - `_redact(payload)` function applying replacement with `[REDACTED]`
   - `json_sink(message)` function that extracts `record`, builds the payload with `timestamp`, `level`, `service`, `logger`, `message`, `trace_id`, `span_id`, `correlation_id`, `operation`, `outcome`, `duration_ms`, redacted `args`, and exception (type + value only) — see `codex-python-logging` for full implementation.
5. Concatenate the project allowlist with the global `DENY` (Input 4).

### Step 3: Implement the @logged Decorator

1. In `decorator.py`, implement `logged(operation, level="INFO", capture_args=True, redact=())`. Use `asyncio.iscoroutinefunction` to pick the sync/async wrapper.
2. For each call, the wrapper:
   - Binds args with `inspect.signature.bind_partial`
   - Removes `self` and `cls`
   - Applies redaction by name (`redact` parameter)
   - Measures `time.perf_counter()` before/after
   - Logs `enter` before execution (parameterized level)
   - On success, logs `exit` with `duration_ms`
   - On exception, logs `error` with `logger.opt(exception=True)` and re-raises
   - Uses `logger.contextualize(operation=..., args=..., outcome=..., duration_ms=...)` on each emission
3. Full reference implementation: `codex-python-logging`.
4. Write unit tests for the decorator:
   - Sync function: emits enter+exit on success; emits enter+error on exception; re-raises the exception.
   - Async function: same.
   - Sensitive arguments in `redact` are replaced with `[REDACTED]`.
   - `capture_args=False` produces `args={}`.
   - `duration_ms` is present in the exit record.

### Step 4: Integrate with OpenTelemetry and Correlation Middleware

1. In the application's `setup.py` (entrypoint), after `setup_logging`, instrument logging:
   ```python
   from opentelemetry.instrumentation.logging import LoggingInstrumentor
   LoggingInstrumentor().instrument(set_logging_format=True)
   ```
2. Create `CorrelationMiddleware` in `infrastructure/http/middleware/correlation.py`:
   - Reads `x-correlation-id` header; generates UUID if missing
   - Wraps `call_next` in `logger.contextualize(correlation_id=...)`
   - Mirrors the header on the response
3. Register the middleware on the FastAPI app **before** any router.
4. For workers/Lambda: the handler entrypoint opens `logger.contextualize` with `correlation_id` extracted from the event (`requestContext.requestId`, `messageAttributes.correlationId`, etc.).

### Step 5: Refactor Existing Inline Calls

1. For each file identified in Step 1.4 and any file with `logger.info(`, `logger.debug(`, `logger.warning(`, `logger.error(`, `logger.exception(`, `logger.critical(`, `logger.success(`, or `print(`:
   - Identify the function where the call lives.
   - Apply `@logged(operation="<domain>.<action>")` to the function.
   - Remove the inline calls.
   - If the call logs an intermediate variable that the decorator cannot capture, extract the operation into a dedicated helper function and decorate it — do not keep the inline call.
2. For global handlers (FastAPI exception handler, outer Lambda handler, worker entrypoint exception block), keep the direct `loguru` call (allowed by the Law).
3. Confirm via grep that `logger.<level>(` and `print(` appear only in:
   - `<package_root>/shared/logging/setup.py`
   - `<package_root>/shared/logging/decorator.py`
   - `<package_root>/shared/logging/serializer.py`
   - Globally listed handler files.

### Step 6: Configure Lint Blocking Inline Calls

1. In `pyproject.toml`, add Ruff configuration:
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
2. Add an AST check on pre-commit (`scripts/check_logging.py`) that:
   - Walks `*.py` in the application
   - Reads `[tool.ahrena.logging.allowed_modules]`
   - Fails if it finds an `Attribute` named in `{info, debug, warning, error, exception, critical, success, trace}` whose object resolves to `logger` (loguru or stdlib) outside the allowlist
   - Fails on `Call` to `print` in non-allowlist files
3. Wire the script into `.pre-commit-config.yaml`:
   ```yaml
   - repo: local
     hooks:
       - id: check-logging
         name: Check logging policy
         entry: python scripts/check_logging.py
         language: system
         types: [python]
   ```
4. Run `pre-commit run --all-files` to validate.

### Step 7: Final Validation

Before finishing, verify:

- [ ] `loguru` and `orjson` appear in `pyproject.toml`; `structlog` and `python-json-logger` do not appear.
- [ ] `setup_logging("<service-name>")` is called once in the entrypoint.
- [ ] `@logged(operation="...")` is applied to all use cases, repositories, and HTTP endpoints.
- [ ] `grep -rn "logger\.\(info\|debug\|warning\|error\|exception\|critical\|success\)" <package_root>` returns only allowlist files.
- [ ] `grep -rn "^[^#]*print(" <package_root>` returns only `serializer.py`.
- [ ] Decorator tests pass (`pytest tests/shared/logging/`).
- [ ] Smoke: run the service locally, hit a request, verify a JSON entry on stdout with `operation`, `outcome=exit`, `duration_ms`, `trace_id`, `correlation_id`.
- [ ] Negative smoke: trigger an exception in an endpoint, verify JSON with `outcome=error`, `exception.type`, `exception.value`, and no full traceback.
- [ ] `pre-commit run --all-files` passes with no logging warnings.
- [ ] PR links to the Issue (lex-issue-first) and the body references `lex-logging-decorator` and `codex-python-logging`.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Bootstrap module | Python code | `<package_root>/shared/logging/setup.py` |
| JSON sink with redaction | Python code | `<package_root>/shared/logging/serializer.py` |
| `@logged` decorator | Python code | `<package_root>/shared/logging/decorator.py` |
| Correlation middleware | Python code | `<package_root>/infrastructure/http/middleware/correlation.py` |
| Lint configuration | TOML block | `pyproject.toml` (`[tool.ruff.lint]`, `[tool.ahrena.logging]`) |
| AST check | Python script | `scripts/check_logging.py` |
| Pre-commit hook | YAML | `.pre-commit-config.yaml` |
| Decorator tests | Python code | `tests/shared/logging/test_decorator.py` |

## Execution Example

### Sample Input

```
Root package: app/
Service: transfer-api
Default level: INFO
Additional sensitive fields: card_number, account_number
```

### Sample Output

```
✓ pyproject.toml: loguru, orjson, opentelemetry-instrumentation-logging added
✓ Removed: structlog, python-json-logger
✓ Created:
  - app/shared/logging/setup.py
  - app/shared/logging/serializer.py (DENY extended with card_number, account_number)
  - app/shared/logging/decorator.py
  - app/shared/logging/__init__.py
  - app/infrastructure/http/middleware/correlation.py
  - scripts/check_logging.py
  - tests/shared/logging/test_decorator.py
✓ Refactored (inline calls removed):
  - app/application/transfers/use_cases.py
  - app/application/reconciliation/runner.py
  - app/infrastructure/http/routers/transfers.py
✓ Lint configured: pre-commit detects logger.* and print() outside the allowlist
✓ Local smoke:
  {"timestamp":"2026-04-29T18:12:03.412+00:00","level":"INFO","service":"transfer-api","operation":"transfer.create","outcome":"exit","duration_ms":42.81,"trace_id":"4bf92f3577b34da6...","correlation_id":"a1b2-..."}
```

## Restrictions

- Do not introduce custom wrappers over `loguru` that re-export `logger.info`/`logger.error` to the rest of the code — that bypasses the Law. Only `setup_logging`, `logged`, and (in allowlist files) direct `logger` are exported.
- Do not use `logger.bind(...)` in the function body to "tag context" — `bind` creates a coupled logger but still requires inline calls. Use `logger.contextualize` only inside the decorator/middleware.
- Do not disable `backtrace`/`diagnose` only on some sinks — they stay `False` on every production sink. In dev, they may be enabled via an explicit environment-variable flag.
- Do not add `# noqa: T201` or equivalent suppressions to keep `print` or inline calls. If a real case exists, open an ADR before creating the exception.
- The allowlist in `[tool.ahrena.logging.allowed_modules]` is part of the project contract. Changes require a dedicated PR and review by the maintainer of the logging module.

## References

- lex-logging-decorator (_foundation/quality) — language-agnostic Law
- codex-python-logging (engineering/backend) — Python implementation manual
- codex-python-observability (engineering/backend) — traces and metrics via OpenTelemetry
- lex-python-security (engineering/backend) — no secrets or PII in logs
- lex-python-error-handling (engineering/backend) — exceptions and re-raise
