# Kata: Refactoring Seguro Python

> **Prefix:** `kata-` | **Type:** Habilidad Repetible | **Scope:** Engineering — Backend: refactoring seguro de código Python con cobertura de tests como red de seguridad

## Objective

Esta Kata define el procedimiento para refactorizar código Python de manera segura: verificar que existe cobertura de tests antes de cambiar nada, realizar pequeñas transformaciones incrementales, validar en cada paso y nunca cambiar comportamiento e interfaz en el mismo commit.

## When to Use

- Cuando se mejora la estructura del código, legibilidad o rendimiento sin cambiar el comportamiento
- Cuando es invocado por el Warrior Apollo para tareas de refactoring
- Cuando se necesita abordar deuda técnica en un módulo existente
- Cuando se migra a un nuevo patrón (p. ej., sync a async, SQL crudo a SQLAlchemy)

## Inputs

| Input | Requerido | Descripción |
|-------|:---------:|-------------|
| Objetivo del refactoring | Sí | Archivos, módulos o patrones a refactorizar |
| Motivación | No | Por qué se necesita este refactoring (rendimiento, legibilidad, alineación de patrones) |
| Restricciones | No | Qué no debe cambiar (interfaces públicas, contratos API, comportamiento) |

## Workflow

```
Progress:
- [ ] 1. Evaluar cobertura de tests actual
- [ ] 2. Agregar cobertura faltante si es necesario
- [ ] 3. Planificar pasos de refactoring
- [ ] 4. Ejecutar transformaciones incrementales
- [ ] 5. Validación final
```

### Step 1: Evaluar Cobertura de Tests Actual

1. Ejecutar la suite de tests para el módulo objetivo: `pytest tests/ -v --cov=<module>`
2. Identificar qué comportamientos están cubiertos y cuáles no
3. Si la cobertura es insuficiente para refactorizar con seguridad, **detenerse y agregar tests primero** (Paso 2)
4. Si la cobertura es adecuada, continuar al Paso 3

### Step 2: Agregar Cobertura Faltante

1. Escribir tests para el comportamiento existente **antes** de cambiarlo — estos son tests de caracterización
2. Testear el comportamiento actual, no el comportamiento deseado
3. Ejecutar la suite para confirmar que todos los nuevos tests pasan contra el código actual
4. Commitear los nuevos tests por separado: "test: add coverage for <module> before refactoring"

### Step 3: Planificar Pasos de Refactoring

1. Dividir el refactoring en **pequeñas transformaciones independientes**
2. Cada paso debe ser:
   - Un único cambio lógico (renombrar, extraer, mover, simplificar)
   - Commitable de forma independiente
   - Verificable ejecutando la suite de tests
3. Ordenar los pasos para minimizar el riesgo: renombramientos antes de reestructuración, internos antes de externos

### Step 4: Ejecutar Transformaciones Incrementales

Para cada paso:

1. Realizar el cambio
2. Ejecutar `ruff check .` y `ruff format .`
3. Ejecutar `mypy .`
4. Ejecutar `pytest` — todos los tests deben pasar
5. Si los tests fallan, el refactoring introdujo un cambio de comportamiento — corregir o revertir
6. Commitear con un mensaje descriptivo: "refactor: <qué cambió>"

**Reglas:**
- **Nunca** cambiar comportamiento e interfaz en el mismo commit
- **Nunca** saltarse la ejecución de tests entre pasos
- Si un paso es demasiado grande para verificarlo con confianza, dividirlo en pasos más pequeños
- Si los tests comienzan a fallar inesperadamente, revertir y reevaluar

### Step 5: Validación Final

Después de todas las transformaciones:

- [ ] Todos los tests pasan (`pytest`)
- [ ] Ruff pasa (`ruff check .` y `ruff format --check .`)
- [ ] mypy strict pasa (`mypy .`)
- [ ] El comportamiento no cambió (los mismos tests pasan, los mismos contratos API, los mismos outputs)
- [ ] El código es más limpio, legible o mejor estructurado que antes
- [ ] Sin nuevas abstracciones a menos que estén justificadas por 3+ usos concretos

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Código refactorizado | Archivos fuente Python | Mismas ubicaciones de archivo (o nuevas ubicaciones si se movieron) |
| Tests de caracterización (si se agregan) | Archivos de test Python | `tests/` |
| Historial de commits | Commits de Git | Un commit por transformación lógica |

## Execution Example

### Example Input

```
Target: Clase TransactionService — actualmente una god class con 15 métodos mezclando lógica de dominio e infraestructura.
Motivation: Separar lógica de dominio de infraestructura según codex-python-architecture.
Constraint: Todos los endpoints existentes deben continuar funcionando de manera idéntica.
```

### Example Output (summary)

1. Agregados 22 tests de caracterización cubriendo el comportamiento existente (commit separado)
2. Extraída la lógica de dominio en `TransactionUseCase` (3 commits: extract, wire, cleanup)
3. Movidos los métodos de repositorio a `SqlAlchemyTransactionRepository` implementando el Protocol `TransactionRepository` (2 commits)
4. Actualizadas las dependencias de FastAPI para usar el nuevo grafo de inyección (1 commit)
5. Todos los 47 tests pasan; mypy y Ruff limpios

## Constraints

- Nunca cambiar comportamiento durante el refactoring — si el comportamiento necesita cambiar, esa es una tarea separada
- Nunca refactorizar sin cobertura de tests — agregar tests primero
- Nunca realizar commits de refactoring grandes y monolíticos — pasos pequeños con validación
- Escalar a un humano si el refactoring revela decisiones arquitectónicas que necesitan alineación

## References

- [Refactoring — Martin Fowler](https://refactoring.com/)
- codex-python-architecture, codex-python-testing (engineering/backend)
- lex-python-typing, lex-python-testing (engineering/backend)
