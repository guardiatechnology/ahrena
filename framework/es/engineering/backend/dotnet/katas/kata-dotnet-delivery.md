# Kata: Entrega .NET

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Implementar, revisar, refactorizar o diagnosticar aplicaciones .NET

## Objetivo

Ejecutar trabajo .NET descubriendo el contrato del repositorio, modelando de forma proporcional, probando por riesgo y completando validación operativa.

## Cuándo Usar

- Para implementar una feature o corrección en C#/.NET
- Para revisar o refactorizar código .NET
- Para diagnosticar fallos de build, runtime, datos o producción

## Inputs

| Input | Obligatorio | Descripción |
|---|:---:|---|
| Modo | Sí | `implement`, `review`, `refactor` o `debug` |
| Objetivo | Sí | Comportamiento, diff o fallo en alcance |
| Evidencia | No | Issue, logs, stack trace, contrato, métricas o reproducción |

## Workflow

```
Progreso:
- [ ] 1. Descubrir el contrato del repositorio
- [ ] 2. Delimitar dominio, riesgo y fronteras
- [ ] 3. Construir baseline reproducible
- [ ] 4. Diseñar o diagnosticar el menor cambio
- [ ] 5. Implementar o registrar findings
- [ ] 6. Validar calidad, integración y operación
- [ ] 7. Validación final
```

### Paso 1: Descubrir el Contrato del Repositorio

Leer instrucciones, `global.json`, solution/project files, propiedades centrales, paquetes, analyzers, CI y comandos. Confirmar SDK/TFM; no cambiar versión por conveniencia.

### Paso 2: Delimitar Dominio, Riesgo y Fronteras

Identificar lenguaje, invariantes, consumidores, contrato público, datos, concurrencia, autorización e impacto operativo. Consultar `codex-domain-driven-design` para decisiones de dominio.

### Paso 3: Construir Baseline Reproducible

Ejecutar restore/build/test del repositorio y reproducir fallos en modo `debug`. Registrar fallos preexistentes aparte. Agregar caracterización antes de refactorizar si falta protección.

### Paso 4: Diseñar o Diagnosticar el Menor Cambio

Consultar `codex-dotnet-engineering` y `codex-code-design`. Listar opciones, trade-offs, `use_when`/`avoid_when` de patterns y modos de fallo. Elegir la menor solución que preserve contratos.

### Paso 5: Implementar o Registrar Findings

- `implement`: código y pruebas según riesgo.
- `refactor`: pasos reversibles sin cambio de comportamiento oculto.
- `debug`: corregir solo si está autorizado; si no, entregar causa y evidencia.
- `review`: findings priorizados con archivo/línea, impacto y corrección verificable.

### Paso 6: Validar Calidad, Integración y Operación

Ejecutar format/analyzers, build y pruebas. Cuando corresponda, validar autorización negativa, SQL real, concurrencia, migraciones, idempotencia, timeout, telemetría, health, container y rollback. Para hot paths, comparar baseline de throughput, bytes/op, colecciones Gen0/1/2 y memoria retenida; revisar ownership de buffers y disposables.

### Paso 7: Validación Final

- [ ] SDK/TFM y comandos reportados pertenecen al repositorio
- [ ] Pasan `lex-clean-code` y las tres `lex-dotnet-*`
- [ ] Resultados de build y pruebas son explícitos
- [ ] Contratos, schema y semántica de errores no cambiaron silenciosamente
- [ ] El código permanece memory-safe; `unsafe`/interop está aislado y justificado
- [ ] Hot paths cambiados cumplen el budget de asignación con evidencia, sin pooling especulativo
- [ ] Overflow, estados inválidos y outcomes esperados tienen representación y pruebas explícitas
- [ ] Riesgos, fallos preexistentes y validaciones omitidas están declarados

## Outputs

| Modo | Output |
|---|---|
| implement/refactor | Código, pruebas y resumen de decisiones |
| review | Findings priorizados o declaración explícita sin findings |
| debug | Reproducción, causa raíz, evidencia y corrección si está autorizada |

## Ejemplo de Ejecución

`implement`: agregar autorización idempotente de tarjeta en ASP.NET Core con PostgreSQL. El output incluye validación de frontera, invariante, prueba con provider real, cancelación y telemetría sin PAN.

## Restricciones

- No instalar o migrar SDK/paquetes sin necesidad del proyecto.
- No sustituir semántica relacional por EF Core InMemory.
- No repetir efectos financieros automáticamente sin idempotencia y reconciliación.
