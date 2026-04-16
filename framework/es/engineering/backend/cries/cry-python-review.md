# Cry: Revisión de Código Python

> **Prefix:** `cry-` | **Type:** Comando Recurrente | **Scope:** Atajo para revisar código Python según Lexis y Codex del backend

## Description

Este comando invoca al Warrior Apollo (o al agente que asume su rol) para realizar una revisión de código sistemática: verificar correctitud, seguridad de tipos, cobertura de tests, seguridad, manejo de errores y cumplimiento de arquitectura según los Lexis y Codex del backend.

## Usage

```
/cry-python-review <objetivo> [contexto]
```

## Parameters

| Parámetro | Requerido | Descripción | Ejemplo |
|-----------|:---------:|-------------|---------|
| `objetivo` | Sí | Qué revisar: rutas de archivos, diff, número de PR o "last commit" | "src/transactions/", "PR #42", "last commit" |
| `contexto` | No | De qué trata el cambio, issue o spec relacionada | "Implementa cancelación de transacción según issue #15" |

## What the Command Does

1. Lee el código o diff objetivo
2. Asume el rol del Warrior Apollo (Senior Python Engineer)
3. Ejecuta **kata-python-review** sistemáticamente:
   - Comprende la intención del cambio
   - Verifica correctitud, tipos, tests, seguridad, manejo de errores, arquitectura
4. Entrega revisión estructurada: resumen, problemas críticos, sugerencias, notas positivas

## Prompt Template

```
Context:
- Review target: {{objetivo}}
- Additional context: {{contexto}}

Task:
Act as the Apollo Warrior (Senior Python Engineer) and execute **kata-python-review**. Review the code against all applicable Lexis (lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability) and Codex (codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing). Focus on correctness, security, and test coverage — not style (Ruff handles that).

Output format:
1. **Summary:** one-sentence assessment (approve / request changes / comment)
2. **Critical issues:** bugs, security vulnerabilities, missing tests (must fix)
3. **Suggestions:** improvements that would strengthen the code (optional)
4. **Positive notes:** what was done well
```

## Invocation Example

**Input:**

```
/cry-python-review "src/transactions/" "Nuevo feature de cancelación de transacción según issue #15"
```

**Expected output:**

Apollo revisa el código y entrega:

**Summary:** Solicitar cambios — falta test para condición de carrera de cancelación concurrente.

**Critical:**
- `repository.soft_delete()` en `src/transactions/infrastructure/database/repositories/transaction_repo.py:45` no verifica `version` para bloqueo optimista — las cancelaciones concurrentes podrían corromper el estado (lex-python-error-handling)
- No hay test para el caso de conflicto 409 al cancelar una transacción ya cancelada (lex-python-testing)

**Suggestions:**
- Considerar agregar un test de propiedad Hypothesis para el invariante "una transacción cancelada no puede cancelarse de nuevo" (codex-python-testing)

**Positive:**
- Separación limpia entre dominio e infraestructura (codex-python-architecture)
- El modelo de respuesta Pydantic con el patrón `from_domain()` está bien implementado

## Constraints

- El Cry dispara una revisión — no implementa correcciones (cry-python-implement se encarga de eso)
- Enfocarse en sustancia sobre estilo — Ruff maneja el formateo
- No bloquear por sugerencias no críticas

## Cry vs Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida con objetivo y contexto | Procedimiento completo en 8 pasos |
| **Complejidad** | Baja (1 comando) | Alta (entender, verificar, revisar tipos/tests/seguridad/arquitectura, entregar) |
| **¿Configura agente?** | Sí (asume el rol del Warrior Apollo) | Sí (define todos los pasos de revisión) |
| **Ejemplo** | "/cry-python-review src/transactions/" | Ejecutar kata-python-review con pasos explícitos |

## Associated Kata and Warrior

- **kata-python-review** — Procedimiento completo de revisión de código
- **warrior-apollo** — Senior Python Engineer; ejecuta kata-python-review

## References

- `kata-python-review` — Procedimiento ejecutado por el Warrior Apollo
- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-tooling (engineering/backend)
