# Kata: Revisión de Código Python

> **Prefix:** `kata-` | **Type:** Habilidad Repetible | **Scope:** Engineering — Backend: revisión sistemática de código para PRs Python

## Objective

Esta Kata define el procedimiento para revisar cambios de código Python: verificar correctitud, seguridad de tipos, cobertura de tests, seguridad, manejo de errores y adherencia a los Lexis del proyecto. El objetivo es detectar bugs, aplicar estándares y compartir conocimiento — no hacer de guardián ni criticar el estilo (Ruff se encarga de eso).

## When to Use

- Cuando se revisa un pull request o cambio de código en un servicio Python backend
- Cuando es invocado por `cry-python-review` o por el Warrior Apollo
- Cuando el usuario solicita una revisión de código o evaluación de calidad

## Inputs

| Input | Requerido | Descripción |
|-------|:---------:|-------------|
| Código a revisar | Sí | Diff, rutas de archivos o referencia de PR que contiene los cambios |
| Contexto | No | Descripción del feature, issue relacionada o documento de diseño |

## Workflow

```
Progress:
- [ ] 1. Entender el cambio
- [ ] 2. Verificar correctitud
- [ ] 3. Verificar seguridad de tipos
- [ ] 4. Evaluar cobertura de tests
- [ ] 5. Revisar seguridad
- [ ] 6. Revisar manejo de errores
- [ ] 7. Verificar cumplimiento de arquitectura
- [ ] 8. Entregar revisión
```

### Step 1: Entender el Cambio

1. Leer la descripción del PR, mensajes de commit e issue/spec relacionada
2. Entender la **intención** — ¿qué problema resuelve esto?
3. Identificar el alcance: ¿qué capas están afectadas (dominio, infraestructura, HTTP)?

### Step 2: Verificar Correctitud

1. ¿El código hace lo que dice la descripción?
2. ¿Se manejan los casos límite? (valores nulos, listas vacías, valores de borde, acceso concurrente)
3. ¿La lógica es correcta para todos los caminos de código?
4. ¿Hay errores de off-by-one, condiciones de carrera o fugas de recursos?

### Step 3: Verificar Seguridad de Tipos

1. ¿Todas las funciones, parámetros y valores de retorno están tipados? (lex-python-typing)
2. ¿Los tipos son precisos? (no `Any` sin justificación, no demasiado amplios)
3. ¿Pasaría mypy strict en los cambios?
4. ¿Se usan modelos Pydantic para validación en los límites?

### Step 4: Evaluar Cobertura de Tests

1. ¿Tiene test cada nuevo comportamiento? (lex-python-testing)
2. ¿Los tests están en el nivel correcto? (unitario para lógica, integración para BD, HTTP para endpoints)
3. ¿Los mocks se usan solo en límites del sistema? (no mockear colaboradores internos)
4. ¿Se testean los casos límite y los caminos de error?
5. ¿Son significativas las afirmaciones? (testear comportamiento, no implementación)
6. Para invariantes de dominio: ¿agregarían valor los tests de propiedad con Hypothesis?

### Step 5: Revisar Seguridad

1. ¿Sin secretos hardcodeados? (lex-python-security)
2. ¿Entrada validada en los límites? (modelos Pydantic con restricciones)
3. ¿SQL usa consultas parametrizadas? (sin interpolación de strings)
4. ¿Los mensajes de error no exponen datos sensibles?
5. ¿Las nuevas dependencias fueron auditadas por vulnerabilidades?

### Step 6: Revisar Manejo de Errores

1. ¿Sin `except:` desnudo ni `except Exception:` genérico sin contexto? (lex-python-error-handling)
2. ¿Las excepciones son específicas al modo de falla?
3. ¿Los errores se loguean con suficiente contexto para depuración?
4. ¿Las respuestas de error no filtran detalles internos?

### Step 7: Verificar Cumplimiento de Arquitectura

1. ¿La capa de dominio libre de imports de framework? (codex-python-architecture)
2. ¿Las dependencias apuntan hacia adentro? (infraestructura → dominio, nunca al revés)
3. ¿Los dataclasses son frozen? (lex-python-immutability)
4. ¿Sin abstracciones prematuras? (sin interfaz para una única implementación sin necesidad de testing)
5. ¿Sigue los patrones del codebase existente?

### Step 8: Entregar Revisión

Estructurar la revisión como:

1. **Resumen:** evaluación en una oración (aprobar, solicitar cambios o comentar)
2. **Problemas críticos:** bugs, vulnerabilidades de seguridad, tests faltantes (obligatorio corregir)
3. **Sugerencias:** mejoras que fortalecerían el código (opcional)
4. **Notas positivas:** qué se hizo bien (reconocer buenos patrones)

**Reglas:**
- Ser específico — referenciar archivo, línea y el problema
- Explicar el **porqué**, no solo el qué — citar el Lexis o Codex relevante
- Sugerir una corrección cuando sea posible, no solo señalar problemas
- No comentar sobre estilo — Ruff maneja el formateo
- No solicitar cambios por preferencia personal — solo por violaciones de Lexis, bugs o tests faltantes

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Revisión | Feedback estructurado (resumen, críticos, sugerencias, positivos) | Inline en la conversación o como comentarios de revisión del PR |

## Constraints

- Esta Kata revisa código — no implementa correcciones (kata-python-implement se encarga de eso)
- Enfocarse en sustancia (correctitud, seguridad, tests) sobre estilo (Ruff maneja el estilo)
- No bloquear PRs por sugerencias no críticas
- Escalar a un humano cuando el cambio tiene implicaciones arquitectónicas más allá del alcance del revisor

## References

- lex-python-typing, lex-python-testing, lex-python-security, lex-python-error-handling, lex-python-immutability (engineering/backend)
- codex-python-architecture, codex-python-fastapi, codex-python-sqlalchemy, codex-python-testing, codex-python-tooling (engineering/backend)
