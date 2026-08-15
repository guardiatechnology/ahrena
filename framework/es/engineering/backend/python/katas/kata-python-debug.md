# Kata: Diagnóstico de Bugs Python

> **Prefix:** `kata-` | **Type:** Habilidad Repetible | **Scope:** Engineering — Backend: depuración sistemática de aplicaciones Python

## Objective

Esta Kata define el procedimiento para diagnosticar y corregir bugs en aplicaciones Python backend: reproducir el problema con un test fallido, aislar la causa raíz, aplicar la corrección y agregar un test de regresión. Sin suposiciones — cada corrección se prueba con un test que fallaba antes y pasa después.

## When to Use

- Cuando se reporta un bug en un servicio Python backend
- Cuando es invocado por el Warrior Apollo para tareas de depuración
- Cuando un test falla y la causa no es inmediatamente obvia
- Cuando el comportamiento en producción diverge del comportamiento esperado

## Inputs

| Input | Requerido | Descripción |
|-------|:---------:|-------------|
| Descripción del bug | Sí | Qué está ocurriendo vs. qué se espera |
| Pasos de reproducción | No | Cómo disparar el bug (llamada API, datos de entrada, secuencia de eventos) |
| Salida de error | No | Stack trace, entradas de log, mensajes de error |
| Entorno | No | Dónde ocurre el bug (local, staging, producción) |

## Workflow

```
Progress:
- [ ] 1. Reproducir con un test fallido
- [ ] 2. Aislar la causa raíz
- [ ] 3. Aplicar la corrección
- [ ] 4. Verificar la corrección
- [ ] 5. Verificar problemas relacionados
```

### Step 1: Reproducir con un Test Fallido

1. Leer la descripción del bug, el stack trace y cualquier contexto provisto
2. Identificar el **punto de entrada**: ¿qué endpoint, función o evento dispara el bug?
3. Escribir un test que ejercite el escenario exacto y **afirme el comportamiento esperado**
4. Ejecutar el test — DEBE fallar. Si pasa, la reproducción es incorrecta; refinarlo
5. Si la reproducción no es clara, **preguntar al usuario** por más detalles: entrada exacta, secuencia, entorno

**Reglas:**
- Un bug sin un test fallido no está aún comprendido
- El test debe ser mínimo — la entrada más pequeña que dispare el bug
- Marcar el test claramente: `test_<descripción>_regression`

### Step 2: Aislar la Causa Raíz

1. Leer el stack trace para identificar el punto de falla
2. Rastrear el flujo de datos desde el punto de entrada hasta la falla:
   - ¿Qué valor es incorrecto?
   - ¿Dónde fue producido o transformado?
   - ¿Qué condición no se cumplió?
3. Reducir: ¿puede un **test unitario** reproducirlo? (iteración más rápida)
   - Si sí, escribir un test unitario focalizado
   - Si no (dependiente de infraestructura), mantener el test de integración
4. Identificar la causa raíz: ¿es un error de lógica, una validación faltante, una condición de carrera, un problema de mapeo de datos o un problema de infraestructura?

### Step 3: Aplicar la Corrección

1. Corregir la causa raíz — no un síntoma
2. La corrección debe ser **mínima**: cambiar solo lo necesario para que el test fallido pase
3. No refactorizar código circundante en el mismo commit (kata-python-refactor es separado)
4. Asegurarse de que la corrección sigue todos los Lexis aplicables:
   - Type hints completos (lex-python-typing)
   - Manejo de errores específico (lex-python-error-handling)
   - Sin regresiones de seguridad (lex-python-security)

### Step 4: Verificar la Corrección

1. Ejecutar el test de regresión — DEBE pasar ahora
2. Ejecutar la **suite de tests completa** — ningún test existente debe romperse
3. Ejecutar `ruff check .` y `mypy .` — sin nuevos problemas
4. Verificar que la corrección aborda la descripción original del bug, no solo el test

### Step 5: Verificar Problemas Relacionados

1. ¿Está el mismo patrón presente en otro lugar del codebase? (mismo bug en código similar)
2. Si sí, corregir todas las instancias o crear una tarea de seguimiento
3. ¿Podría haberse prevenido este bug con una validación faltante, un tipo más estricto o un mejor test? Considerar agregar una salvaguarda

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Corrección | Cambios en código fuente Python | Archivos afectados |
| Test de regresión | Archivo de test Python | `tests/unit/` o `tests/integration/` |
| Análisis de causa raíz | Breve explicación textual | Mensaje de commit o conversación |

## Execution Example

### Example Input

```
Bug: POST /v1/transactions retorna 500 cuando la moneda está en minúsculas ("brl" en lugar de "BRL").
Stack trace: ValidationError en el modelo Pydantic — el patrón de moneda ^[A-Z]{3}$ rechaza minúsculas.
Expected: 422 con error descriptivo, no 500.
```

### Example Output (summary)

1. **Test de reproducción:** `test_create_transaction_lowercase_currency_returns_422` — envía `{"amount": 1000, "currency": "brl"}`, afirma 422 con código de error `VALIDATION_ERROR`
2. **Causa raíz:** `ValidationError` de Pydantic no es capturado por el exception handler; FastAPI retorna 500 genérico en lugar de la respuesta 422 estructurada
3. **Corrección:** Agregado handler de `RequestValidationError` en `register_exception_handlers()` que mapea errores de validación Pydantic al formato estándar de respuesta 422
4. **Verificación:** el test de regresión pasa; todos los 47 tests existentes pasan; Ruff y mypy limpios
5. **Relacionado:** el mismo handler faltante afectaría todos los endpoints — la corrección es global (un cambio, cobertura completa)

## Constraints

- Nunca adivinar la corrección sin reproducir primero — escribir el test fallido
- Nunca corregir síntomas — encontrar y corregir la causa raíz
- Nunca cambiar código no relacionado en el commit de corrección
- Escalar a un humano si el bug involucra corrupción de datos, brecha de seguridad o problemas entre servicios

## References

- codex-python-testing (engineering/backend)
- lex-python-error-handling, lex-python-testing (engineering/backend)
