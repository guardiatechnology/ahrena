# Kata: Refactorización Segura

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Mejorar diseño interno sin cambiar comportamiento observable

## Objetivo

Producir una refactorización pequeña, reversible y protegida por evidencia, con decisión explícita sobre el smell, el pattern elegido y su costo.

## Cuándo Usar

- Cuando complejidad, duplicación, acoplamiento o nombres dificultan un cambio
- Antes de introducir un pattern estructural
- Cuando código legacy debe prepararse para una alteración funcional

## Inputs

| Input | Obligatorio | Descripción |
|---|:---:|---|
| Objetivo | Sí | Archivos, componente o comportamiento a mejorar |
| Motivación | Sí | Cambio bloqueado, defecto recurrente o riesgo observado |
| Restricciones | No | Contratos, performance, datos y compatibilidad a preservar |

## Workflow

```
Progreso:
- [ ] 1. Delimitar comportamiento y riesgo
- [ ] 2. Crear baseline y protección
- [ ] 3. Elegir la menor transformación
- [ ] 4. Ejecutar pasos reversibles
- [ ] 5. Validar comportamiento y operación
- [ ] 6. Validación final
```

### Paso 1: Delimitar Comportamiento y Riesgo

Describir comportamiento observable, consumidores, invariantes, contratos y modos de fallo. Clasificar cada afirmación como confirmada, hipótesis o decisión propuesta.

### Paso 2: Crear Baseline y Protección

Ejecutar pruebas y análisis estático. Si falta protección, agregar caracterización en el nivel más económico que capture el riesgo. Medir performance solo si motiva el trabajo.

### Paso 3: Elegir la Menor Transformación

Consultar `codex-code-design` y, para dominio, `codex-domain-driven-design`. Registrar problema, elección, **cuándo no usarla**, trade-offs y criterio de reversión.

### Paso 4: Ejecutar Pasos Reversibles

Separar cambio estructural de cambio de comportamiento, preservar interfaces y ejecutar verificaciones focalizadas. No ampliar el alcance a limpiezas adyacentes.

### Paso 5: Validar Comportamiento y Operación

Repetir baseline y pruebas de integración/contrato aplicables. Verificar logs, métricas, migraciones, concurrencia y seguridad cuando correspondan.

### Paso 6: Validación Final

- [ ] Comportamiento observable y contratos preservados
- [ ] El smell inicial se redujo y no solo cambió de lugar
- [ ] La abstracción tiene evidencia y criterio de retiro
- [ ] Pasan `lex-clean-code`, `lex-dry` y las Lexis de la stack
- [ ] Riesgos residuales y verificaciones están en el handoff

## Outputs

| Output | Formato | Destino |
|---|---|---|
| Código refactorizado | Código de la stack | Archivos originales |
| Protección de comportamiento | Pruebas | Suite apropiada |
| Registro de decisión | Resumen/ADR si hace falta | Handoff o ruta canónica |

## Ejemplo de Ejecución

`PaymentService` mezcla autorización, gateway y retry. Pruebas de caracterización preservan respuestas e idempotencia; la política variable pasa a Strategy; retry queda en el adapter; no se crea Factory porque la construcción es simple.

## Restricciones

- No llamar refactorización a cambios de comportamiento, contrato o schema.
- No aplicar un pattern solo para satisfacer una métrica.
- No retirar telemetría o tratamiento de fallos durante la reorganización.
