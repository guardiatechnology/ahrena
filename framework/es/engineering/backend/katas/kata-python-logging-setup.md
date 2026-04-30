# Kata: Configuración de Logging Python con Loguru y Decorator

> **Prefix:** `kata-` | **Type:** Habilidad Repetible | **Scope:** Engineering — Backend: instalación y configuración del patrón de logging en una aplicación Python

## Objective

Esta Kata define el procedimiento para dejar una aplicación Python lista para registrar logs según `lex-logging-decorator`: instalar `loguru`, crear el módulo de bootstrap, implementar el decorator `@logged`, integrar con OpenTelemetry y FastAPI, activar el lint que bloquea llamadas inline, y validar punta a punta.

## When to Use

- En un servicio Python que aún no adoptó el patrón de logging (sin `loguru` configurado o usando `logging`/`structlog`/`print` en el cuerpo del código).
- Al iniciar un nuevo servicio Python desde el template estándar.
- Al remediar una violación detectada en PR review (llamada inline o import directo de logger).
- Cuando es invocado por `cry-python-implement` con alcance de observabilidad o por el Warrior Apollo.

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Ruta del paquete raíz de la aplicación | Sí | Ej.: `app/`, `src/myservice/` |
| Nombre del servicio | Sí | Identificador estable (ej.: `transfer-api`); se usa en el campo `service` |
| Nivel de log default | No | `INFO` por defecto; `DEBUG` solo en ambientes no-prod |
| Lista de campos sensibles adicionales | No | Complementa el denylist global del sink (ej.: `card_number`, `tax_id`) |

## Workflow

```
Progress:
- [ ] 1. Agregar dependencias (loguru, orjson) y remover competidoras
- [ ] 2. Crear módulo de bootstrap (setup_logging) y sink JSON
- [ ] 3. Implementar el decorator @logged (sync y async)
- [ ] 4. Integrar con OpenTelemetry y middleware de correlación
- [ ] 5. Refactorizar llamadas inline existentes para usar @logged
- [ ] 6. Configurar lint (Ruff + AST check) bloqueando llamadas inline
- [ ] 7. Validación final (tests, lint, smoke de log estructurado)
```

### Step 1: Agregar Dependencias y Remover Competidoras

1. Agregar al `pyproject.toml`:
   ```toml
   [project]
   dependencies = [
     "loguru>=0.7",
     "orjson>=3.10",
     "opentelemetry-instrumentation-logging>=0.46b0",
   ]
   ```
2. Remover `structlog`, `python-json-logger` y cualquier wrapper sobre `logging` (stdlib) de las dependencias de la aplicación.
3. Ejecutar `uv sync` (o equivalente) y confirmar que el lockfile fue actualizado.
4. Buscar en el codebase usos remanentes:
   ```powershell
   Select-String -Path "**/*.py" -Pattern "import logging|import structlog|from structlog"
   ```
5. Listar los archivos encontrados; serán tratados en el Paso 5.

### Step 2: Crear el Módulo de Bootstrap y el Sink JSON

1. Crear la estructura:
   ```
   <package_root>/shared/logging/
   ├── __init__.py
   ├── setup.py
   ├── serializer.py
   └── decorator.py
   ```
2. `__init__.py` exporta solo `logger`, `logged` y `setup_logging`.
3. `setup.py` define `setup_logging(service_name, level)`:
   - Remueve sinks default (`logger.remove()`)
   - Configura `extra={"service": service_name}`
   - Agrega sink stdout (formato legible) y sink JSON (`json_sink` de `serializer.py`)
   - `backtrace=False`, `diagnose=False` (seguridad)
4. `serializer.py` define:
   - `DENY` set con nombres de campo sensibles default (`password`, `token`, `secret`, `api_key`, `authorization`, `cookie`, `cpf`, `ssn`)
   - Función `_redact(payload)` aplicando sustitución por `[REDACTED]`
   - Función `json_sink(message)` que extrae `record`, monta payload con `timestamp`, `level`, `service`, `logger`, `message`, `trace_id`, `span_id`, `correlation_id`, `operation`, `outcome`, `duration_ms`, `args` redactados, y excepción (solo tipo + valor) — ver `codex-python-logging` para implementación completa.
5. Concatenar el allowlist del proyecto con el `DENY` global (Input 4).

### Step 3: Implementar el Decorator @logged

1. En `decorator.py`, implementar `logged(operation, level="INFO", capture_args=True, redact=())`. Usar `asyncio.iscoroutinefunction` para elegir el wrapper sync/async.
2. Para cada llamada, el wrapper:
   - Vincula args con `inspect.signature.bind_partial`
   - Remueve `self` y `cls`
   - Aplica redacción por nombre (parámetro `redact`)
   - Mide `time.perf_counter()` antes/después
   - Loguea `enter` antes de la ejecución (nivel parametrizado)
   - En éxito, loguea `exit` con `duration_ms`
   - En excepción, loguea `error` con `logger.opt(exception=True)` y relanza
   - Usa `logger.contextualize(operation=..., args=..., outcome=..., duration_ms=...)` en cada emisión
3. Implementación de referencia completa: `codex-python-logging`.
4. Escribir tests unitarios para el decorator:
   - Función sync: emite enter+exit en éxito; emite enter+error en excepción; relanza la excepción.
   - Función async: ídem.
   - Argumentos sensibles en `redact` son sustituidos por `[REDACTED]`.
   - `capture_args=False` produce `args={}`.
   - `duration_ms` está presente en el record de salida.

### Step 4: Integrar con OpenTelemetry y Middleware de Correlación

1. En el `setup.py` de la aplicación (entrypoint), después de `setup_logging`, instrumentar logging:
   ```python
   from opentelemetry.instrumentation.logging import LoggingInstrumentor
   LoggingInstrumentor().instrument(set_logging_format=True)
   ```
2. Crear middleware `CorrelationMiddleware` en `infrastructure/http/middleware/correlation.py`:
   - Lee header `x-correlation-id`; genera UUID si está ausente
   - Envuelve `call_next` en `logger.contextualize(correlation_id=...)`
   - Espeja el header en la response
3. Registrar el middleware en la app FastAPI **antes** de cualquier router.
4. Para workers/Lambda: el entrypoint del handler abre el `logger.contextualize` con `correlation_id` extraído del evento (`requestContext.requestId`, `messageAttributes.correlationId`, etc.).

### Step 5: Refactorizar Llamadas Inline Existentes

1. Para cada archivo identificado en el Paso 1.4 y cualquier archivo con `logger.info(`, `logger.debug(`, `logger.warning(`, `logger.error(`, `logger.exception(`, `logger.critical(`, `logger.success(`, o `print(`:
   - Identificar la función donde vive la llamada.
   - Aplicar `@logged(operation="<domain>.<action>")` a la función.
   - Remover las llamadas inline.
   - Si la llamada loguea una variable intermedia imposible de capturar vía decorator, extraer la operación a una función auxiliar dedicada y decorarla — no mantener la llamada inline.
2. Para handlers globales (FastAPI exception handler, Lambda outer handler, worker entrypoint exception block), mantener la llamada directa a `loguru` (uso permitido por la Ley).
3. Confirmar vía grep que `logger.<level>(` y `print(` aparecen solo en:
   - `<package_root>/shared/logging/setup.py`
   - `<package_root>/shared/logging/decorator.py`
   - `<package_root>/shared/logging/serializer.py`
   - Archivos de handlers globales explícitamente listados.

### Step 6: Configurar Lint Bloqueando Llamadas Inline

1. En `pyproject.toml`, agregar configuración Ruff:
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
2. Agregar AST check en pre-commit (`scripts/check_logging.py`) que:
   - Recorre `*.py` en la aplicación
   - Lee `[tool.ahrena.logging.allowed_modules]`
   - Falla si encuentra `Attribute` con nombre en `{info, debug, warning, error, exception, critical, success, trace}` cuyo objeto resuelve a `logger` (loguru o stdlib) fuera del allowlist
   - Falla en `Call` a `print` en archivos no-allowlist
3. Conectar el script a `.pre-commit-config.yaml`:
   ```yaml
   - repo: local
     hooks:
       - id: check-logging
         name: Check logging policy
         entry: python scripts/check_logging.py
         language: system
         types: [python]
   ```
4. Ejecutar `pre-commit run --all-files` para validar.

### Step 7: Validación Final

Antes de concluir, verificar:

- [ ] `loguru` y `orjson` aparecen en `pyproject.toml`; `structlog` y `python-json-logger` no aparecen.
- [ ] `setup_logging("<service-name>")` se llama una sola vez en el entrypoint.
- [ ] `@logged(operation="...")` está aplicado a todos los casos de uso, repositorios y endpoints HTTP.
- [ ] `grep -rn "logger\.\(info\|debug\|warning\|error\|exception\|critical\|success\)" <package_root>` retorna solo archivos del allowlist.
- [ ] `grep -rn "^[^#]*print(" <package_root>` retorna solo el `serializer.py`.
- [ ] Tests del decorator pasan (`pytest tests/shared/logging/`).
- [ ] Smoke: levantar el servicio local, hacer un request, verificar en stdout un JSON conteniendo `operation`, `outcome=exit`, `duration_ms`, `trace_id`, `correlation_id`.
- [ ] Smoke negativo: provocar excepción en endpoint, verificar JSON con `outcome=error`, `exception.type`, `exception.value` y ausencia de traceback completo.
- [ ] `pre-commit run --all-files` pasa sin warnings de logging.
- [ ] El PR vincula a la Issue (lex-issue-first) y el body referencia `lex-logging-decorator` y `codex-python-logging`.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Módulo de bootstrap | Código Python | `<package_root>/shared/logging/setup.py` |
| Sink JSON con redacción | Código Python | `<package_root>/shared/logging/serializer.py` |
| Decorator `@logged` | Código Python | `<package_root>/shared/logging/decorator.py` |
| Middleware de correlación | Código Python | `<package_root>/infrastructure/http/middleware/correlation.py` |
| Configuración de lint | Bloque TOML | `pyproject.toml` (`[tool.ruff.lint]`, `[tool.ahrena.logging]`) |
| AST check | Script Python | `scripts/check_logging.py` |
| Hook pre-commit | YAML | `.pre-commit-config.yaml` |
| Tests del decorator | Código Python | `tests/shared/logging/test_decorator.py` |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Paquete raíz: app/
Servicio: transfer-api
Nivel default: INFO
Campos sensibles adicionales: card_number, account_number
```

### Output de Ejemplo

```
✓ pyproject.toml: loguru, orjson, opentelemetry-instrumentation-logging agregados
✓ Removidos: structlog, python-json-logger
✓ Creados:
  - app/shared/logging/setup.py
  - app/shared/logging/serializer.py (DENY extendido con card_number, account_number)
  - app/shared/logging/decorator.py
  - app/shared/logging/__init__.py
  - app/infrastructure/http/middleware/correlation.py
  - scripts/check_logging.py
  - tests/shared/logging/test_decorator.py
✓ Refactorizados (llamadas inline removidas):
  - app/application/transfers/use_cases.py
  - app/application/reconciliation/runner.py
  - app/infrastructure/http/routers/transfers.py
✓ Lint configurado: pre-commit detecta logger.* y print() fuera del allowlist
✓ Smoke local:
  {"timestamp":"2026-04-29T18:12:03.412+00:00","level":"INFO","service":"transfer-api","operation":"transfer.create","outcome":"exit","duration_ms":42.81,"trace_id":"4bf92f3577b34da6...","correlation_id":"a1b2-..."}
```

## Restricciones

- No introducir wrappers propios sobre `loguru` que reexporten `logger.info`/`logger.error` al resto del código — eso evade la Ley. Solo `setup_logging`, `logged` y (en archivos del allowlist) `logger` directo son exportados.
- No usar `logger.bind(...)` en el cuerpo de la función para "marcar contexto" — `bind` crea un logger acoplado pero sigue exigiendo llamada inline. Usar `logger.contextualize` solo dentro del decorator/middleware.
- No deshabilitar `backtrace`/`diagnose` solo en algunos sinks — quedan `False` en todos los sinks de producción. En dev pueden habilitarse vía flag explícito por variable de entorno.
- No agregar `# noqa: T201` o supresiones equivalentes para mantener `print` o llamadas inline. Si hay un caso real, abrir ADR antes de crear excepción.
- El allowlist en `[tool.ahrena.logging.allowed_modules]` es parte del contrato del proyecto. Cambios exigen PR dedicado y revisión de quien mantiene el módulo de logging.

## References

- lex-logging-decorator (_foundation/quality) — Ley agnóstica al lenguaje
- codex-python-logging (engineering/backend) — manual de implementación Python
- codex-python-observability (engineering/backend) — traces y métricas vía OpenTelemetry
- lex-python-security (engineering/backend) — prohibición de loguear secretos y PII
- lex-python-error-handling (engineering/backend) — excepciones y re-raise
