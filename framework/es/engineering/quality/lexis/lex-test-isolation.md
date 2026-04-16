# Lexis: Aislamiento de Pruebas

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Garantía de que cada prueba corre desde un estado conocido, independiente del orden y paralelizable sin race condition

## Propósito

Las pruebas que dependen del orden, estado global mutable o tiempo real se convierten en bombas de tiempo: pasan localmente, fallan en el CI; pasan en una máquina, fallan en otra. El equipo pierde horas depurando la prueba en vez del código. Peor: tolerar retry como solución enseña a ignorar señales — el próximo bug real queda enterrado en el ruido.

Esta Lexis existe para garantizar que **cada prueba sea determinística, independiente y paralelizable**, y que **las pruebas flaky sean tratadas como bugs críticos** — no como inconveniencias.

## Ley

> **Toda prueba DEBE comenzar desde un estado conocido, NO DEBE depender del orden de ejecución, y DEBE ser capaz de correr en paralelo con otras del mismo tipo sin race condition. Las dependencias externas no determinísticas (reloj, red, random, UUID) DEBEN ser parametrizadas o mockeadas. Las pruebas flaky DEBEN ser corregidas inmediatamente o deshabilitadas — nunca ignoradas con retry.**

## Reglas

### 1. Estado inicial conocido

Cada prueba **DEBE**:

- Comenzar con fixtures/factories explícitas — nunca depender de datos de una prueba anterior.
- Limpiar estado después de la ejecución (truncate de tablas, reset de cachés, unmount de componentes).
- Usar transacciones + rollback cuando sea posible (la prueba confirma, el framework revierte).

**Antipattern:** `test_create_user` confía en que `test_delete_user` no corrió todavía.

### 2. Independencia de orden

Correr la suite en orden **aleatorio** (`pytest --randomly`, Jest `testSequencer: 'random'`) **DEBE** producir el mismo resultado. Los fallos que aparecen solo en orden específico indican acoplamiento vía estado compartido.

### 3. Paralelismo seguro

Las pruebas del mismo nivel **DEBEN** ser paralelizables (`pytest -n auto`, Jest default). Si las pruebas comparten un recurso (base de datos, puerto, archivo), **DEBEN** usar identificador único por worker (`pytest-xdist` worker id, schema por worker).

### 4. Mocks para no determinismo

| Fuente de no determinismo | Estrategia |
|---|---|
| Reloj (`datetime.now()`, `Date.now()`) | Inyectar clock; fijar en la prueba con `freeze_time` |
| UUID / random | Seed fijo o inyección |
| Red externa (APIs pagas, servicios sin sandbox) | VCR / MSW / fixture; validar contrato por separado |
| Filesystem compartido | `tempfile` / contenedor por prueba |
| Variables de entorno | Set/unset en fixture setup/teardown |

### 5. Flaky = bug crítico

Una prueba flaky:
- **DEBE** ser corregida en el sprint en que fue detectada.
- Mientras esté abierta, **DEBE** estar marcada (`@pytest.mark.flaky` con motivo + ticket) y tener visibilidad.
- Nunca "tratar con retry" (`pytest-rerunfailures`) sin investigar causa raíz — el retry es anestesia, no cura.

Excepciones válidas para retry:
- Prueba E2E contra servicio externo con latencia real y acuerdo de SLA conocido.
- Documentar el retry con comentario justificando.

### 6. Tiempo de suite monitoreado

- **Unit**: cada prueba < 1s; suite total < 60s en máquina dev.
- **Integration**: cada prueba < 10s; suite total < 5min en CI.
- **E2E**: cada jornada < 2min; suite total < 15min en CI.

Las pruebas que exceden el budget del nivel **DEBEN** moverse al nivel superior (unit → integration) u optimizarse.

## Alcance

- **Aplica a:** toda suite de pruebas en todos los proyectos.
- **Agentes vinculados:** `warrior-hera`, `warrior-apollo`, `warrior-hephaestus`.
- **Excepciones:** Ninguna. Las pruebas lentas pero estables son aceptables en el nivel correcto; la flakiness nunca.

## Consecuencias de Violación

1. **Debug wasteful:** los ingenieros pasan horas encontrando por qué la prueba falla el lunes y pasa el martes.
2. **Pérdida de confianza en el CI:** los red builds se vuelven ruido; se aprueban merges con pruebas rojas "porque es flaky".
3. **Incidentes en prod:** race conditions no detectadas en prueba (porque las pruebas enmascaraban) explotan en producción.
4. **Remediación:**
   - Identificar flaky tests (reporte histórico: tasa de fallo).
   - Cada flaky se convierte en ticket con prioridad P1; fix o disable.
   - Reforzar paralelismo + orden aleatorio en el CI.

## Validación Automatizada

- **Herramienta:**
  - `pytest --randomly-seed=random` (detecta dependencia de orden)
  - `pytest -n auto` / Jest paralelismo (detecta race conditions)
  - Rastreo histórico de flakes en el CI (GitHub Actions, CircleCI insights).
- **Momento:** toda ejecución de CI; reporte semanal de flakes.
- **Métrica:** 0 flaky activos (sin ticket); >99% de determinismo en la suite.

## Referencias

- `lex-test-pyramid` — distribución por nivel
- `lex-frontend-testing`, `lex-python-testing`
- `warrior-hera` — conduce estrategia de pruebas
