# Lexis: Pirámide de Pruebas

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Distribución de pruebas entre niveles (unit, integración, E2E) en cualquier stack para garantizar retroalimentación rápida, cobertura adecuada y costo sostenible

## Propósito

Pipelines dominados por pruebas E2E lentas matan el ciclo de dev (retroalimentación en minutos en vez de segundos); suites dominadas por mocks unit dan falsa seguridad (las pruebas pasan, la integración explota en prod). La pirámide de pruebas distribuye el rigor por los niveles donde cada tipo funciona mejor — unit rápido y barato en la base, E2E caro pero esencial en la cima.

Esta Lexis existe para garantizar que **cada proyecto tenga distribución de pruebas proporcional a la pirámide**, que **las pruebas E2E estén restringidas a jornadas críticas**, y que **las pruebas de integración cubran las fronteras reales (BD, cola, API externa)**.

## Ley

> **Toda suite de pruebas DEBE respetar la proporción aproximada 70% unit / 20% integración / 10% E2E. Las pruebas E2E DEBEN cubrir solo jornadas críticas declaradas (login, checkout, onboarding) — nunca CRUD exhaustivo. Las pruebas de integración DEBEN usar fronteras reales (base de datos real, colas reales en contenedor) y los mocks DEBEN estar limitados a servicios externos no gratuitos o no determinísticos.**

## Reglas

### 1. Proporción 70/20/10

Medida por **número de pruebas** (no por tiempo). Tolerancia: ±10 puntos porcentuales en proyectos pequeños (<50 pruebas totales).

Si la proporción se invierte (ej.: 30% unit / 60% E2E) → **la suite está desbalanceada**; refactorizar antes de agregar más pruebas.

### 2. E2E solo para jornadas críticas

Una jornada E2E:
- Representa una transacción de valor real al usuario final (pagar, reservar, enviar).
- Cruza múltiples bounded contexts o UI + backend + datos.
- Tiene costo real de fallo (ingresos perdidos, datos corruptos).

Casos que **NO** merecen E2E:
- Validación de formulario (una prueba unitaria de componente basta).
- CRUD estándar (prueba de integración en el endpoint + unit en el dominio).
- Variaciones estéticas o de layout.

### 3. La integración usa fronteras reales

El agente **DEBE**:

- Usar **base de datos real** en contenedor (PostgreSQL, MySQL) — no SQLite in-memory en proyectos que corren PostgreSQL en prod.
- Usar **colas reales** en contenedor (Redis, RabbitMQ, Kafka) — no mocks de biblioteca.
- Usar **contenedores con versión igual a la de producción** (`postgres:16` no `postgres:latest`).

El agente **PUEDE** mockear:
- APIs externas pagas (Stripe, proveedores de SMS).
- Servicios que no tienen sandbox público.
- Tiempo/reloj para pruebas determinísticas.

### 4. Aislamiento entre pruebas

Las pruebas del mismo nivel **NO DEBEN** compartir estado mutable. Cada prueba:
- Comienza desde un estado conocido (fixtures, truncate, transacción aislada).
- No depende del orden de ejecución.
- Puede correr en paralelo sin race condition.

Pruebas flaky = bug: o en la prueba, o en el sistema. Nunca tolerar retry como solución.

### 5. Pirámide adaptada por contexto

Excepciones al 70/20/10 permitidas con justificación documentada:

- **Proyectos de integración puros** (ETL, glue code): pirámide invertida natural (más integración); documentar.
- **Bibliotecas puras** (sin I/O): 90%+ unit es aceptable.
- **Apps mobile**: los UI tests (Espresso/XCUITest) reemplazan parcialmente E2E; proporción ajustada.

Documentar desviación en ADR cuando sea estructural.

## Alcance

- **Aplica a:** toda suite de pruebas en todos los proyectos Ahrena.
- **Agentes vinculados:** `warrior-hera`, `warrior-apollo`, `warrior-hephaestus`.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones (las desviaciones documentadas son contextuales, no violaciones).

## Consecuencias de Violación

1. **Pipeline lento:** 80% E2E = build de 30+ min; el dev apaga el CI local, las regresiones escapan.
2. **Falsa seguridad:** 90% unit con mocks = prod se rompe en producción en integraciones no probadas.
3. **Pruebas flaky toleradas:** el equipo aprende a ignorar red builds; la cobertura se vuelve teatro.
4. **Remediación:** auditar distribución; migrar pruebas en el nivel equivocado (E2E → integración cuando sea posible); declarar jornadas E2E legítimas explícitamente.

## Validación Automatizada

- **Herramienta:** conteo de pruebas por directorio convencional (`tests/unit`, `tests/integration`, `tests/e2e`); lint que marca pruebas E2E fuera del directorio declarado.
- **Momento:** mensualmente en CI como reporte; en el Gate 2 (vía `kata-quality-gate` Check 3) para nuevas features.
- **Métrica:** distribución ≈ 70/20/10 ±10pp; 0 pruebas flaky activas; tiempo de suite unit < 60s.

## Referencias

- `lex-frontend-testing`, `lex-python-testing` — reglas por stack
- `codex-test-strategy` — estrategia detallada (niveles, alcances)
- `warrior-hera` — QA/Test Strategy specialist
- [Test Pyramid — Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)
