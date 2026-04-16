# Codex: Estrategia de Pruebas

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Estrategia de pruebas aplicada en el framework Ahrena — niveles, alcances, herramientas, cuándo usar cada una, anti-patterns

## Visión general

Este Codex es la referencia operacional para **decisiones de estrategia de pruebas** en proyectos Ahrena. Consultado por `warrior-hera` al diseñar plan de pruebas para una feature, por `warrior-apollo` y `warrior-hephaestus` durante la implementación cuando hay duda sobre en qué nivel probar algo, y por revisores de código en el Gate 2.

## Contexto

- **Dominio:** estrategia de pruebas (qué probar, dónde probar, cómo probar, cuándo NO probar)
- **Público objetivo:** `warrior-hera`, agentes que implementan código de producción, revisores
- **Actualización:** cuando nuevos frameworks de prueba emergen, cuando patrones de arquitectura cambian (ej.: microservicios alteran lo que es "integración")

## Contenido

### Los 4 niveles

| Nivel | Alcance | Herramientas | Tiempo objetivo por prueba |
|---|---|---|---|
| **Unit** | Función pura, clase aislada, componente sin I/O | pytest, Jest, Vitest, Go testing | < 100ms |
| **Integration** | Múltiples componentes + infra real (BD, cola) | pytest + testcontainers, Jest + MSW + Postgres | < 10s |
| **E2E (API)** | Request HTTP real → sistema → response | pytest + httpx, Supertest, Pact | < 30s |
| **E2E (UI)** | Navegador real → UI → backend → UI | Playwright, Cypress | < 2min |

### Cuándo usar cada nivel

**Unit**: lógica de dominio, utilities, funciones puras, componentes de presentación sin I/O.
- Regla: si escribir la prueba requiere mockear más de 1 colaborador, probablemente es integration, no unit.

**Integration**: cualquier camino que toca persistencia, cola, caché, API externa (incluso en contenedor).
- Regla: probar lo que producción realmente usa (Postgres 16, no SQLite; Redis real, no in-memory).

**E2E (API)**: contrato externo visible al consumidor; flujos entre múltiples endpoints.
- Regla: uno por endpoint principal; uno más por flujo multi-endpoint (ej.: create + list + delete).

**E2E (UI)**: jornadas críticas de negocio; comportamientos que solo se manifiestan en el navegador (ruteo, autenticación end-to-end, eventos del DOM).
- Regla: ≤ 1 E2E UI por jornada (login, checkout, onboarding); NO uno por pantalla.

### Decision tree

```
¿Algo nuevo para probar?
│
├── ¿Es función pura / lógica de dominio?
│   → Unit test
│
├── ¿Involucra BD, cola, caché o integración real?
│   ├── ¿Cross-service o requiere deploy completo?
│   │   → E2E (API)
│   └── ¿Aislable con contenedor?
│       → Integration
│
├── ¿Es jornada de usuario crítica y visual?
│   → E2E (UI), 1 por jornada
│
└── ¿Es variación estética o CSS?
    → Visual regression test (o inspección manual)
```

### Herramientas por stack

**Python (Apollo):**
- Unit: `pytest` + `pytest-mock`
- Property-based: `hypothesis`
- Integration: `pytest` + `testcontainers-python` + Postgres real
- E2E API: `pytest` + `httpx` o `requests-mock` para externos
- Benchmarks: `pytest-benchmark`
- Coverage: `pytest-cov`

**Frontend (Hephaestus):**
- Unit/Component: `vitest` o `jest` + `@testing-library/react`
- Integration: `vitest` + `msw` (mock de API)
- E2E: `playwright` (preferido) o `cypress`
- Visual regression: `chromatic` (Storybook) o `playwright-visual`
- Accesibilidad: `jest-axe`, `@axe-core/playwright`

**Backend infra (IaC):**
- Unit: validación de módulo Terraform (`terraform validate`, `terraform test`)
- Integration: aplicar en account sandbox + assert vía AWS SDK
- Policy: `opa test`, `conftest`

### Estrategias para fronteras

**APIs externas pagas (Stripe, Twilio):**
- Unit: mock completo.
- Integration: sandbox del proveedor cuando esté disponible + contract test (Pact).
- Producción: prueba de smoke canary post-deploy.

**Webhooks recibidos:**
- Integration: enviar payload real del proveedor (capturado en VCR) al endpoint.
- Validar idempotencia: enviar 2x, esperar 1 efecto.

**Eventos asíncronos:**
- Integration: publicar evento, esperar que el consumer procese (timeout controlado).
- Validar side effects (BD actualizada, evento downstream publicado).

### Anti-patterns a evitar

| Anti-pattern | Por qué es malo |
|---|---|
| Mockear BD en prueba de repositorio | Enmascara bugs de query/migration; la prueba no demuestra nada real |
| Snapshot gigante sin revisión | Diff aceptado a ciegas; el snapshot se vuelve noise |
| Un E2E por endpoint | La suite explota; el CI se vuelve maratón; el ROI cae |
| Retry en prueba flaky | No cura; enmascara; enseña a ignorar señales |
| `test.only` commiteado | Corremos solo 1 prueba en el CI sin notarlo; la cobertura cae sin warning |
| Assert sobre implementación (`expect(foo.state).toBe(...)`)| Se rompe en cada refactor sin regresión real |

### Cobertura

- **Cobertura ≥ threshold** (80% default) es condición necesaria, no suficiente.
- Cobertura 100% de línea **no** significa probado: puede ser "se ejecutó pero sin assertion".
- Preferir `branch coverage` sobre `line coverage` cuando esté disponible.
- La cobertura es **señal**, no métrica objetivo. Features críticas (pago, auth) deben tener cobertura de hecho (mutation testing con `mutmut`, `stryker` para validar calidad de los asserts).

### Cuándo NO probar

- **Código trivial sin lógica** (getter/setter puro, `return x + 1`): la prueba agrega ruido sin valor.
- **Wrappers finos de biblioteca** (`def create_uuid(): return uuid.uuid4()`): prueba la biblioteca, no el código.
- **Configuración estática** (constantes, labels): probar solo si cambia frecuentemente.
- **Código generado**: confiar en el generador (OpenAPI client, Prisma schema).

Registrar decisión de "no probar" en comentario local o en review — documentación > ausencia silenciosa.

## Referencias

- `lex-test-pyramid` — distribución 70/20/10
- `lex-test-isolation` — determinismo y paralelismo
- `lex-python-testing`, `lex-frontend-testing` — reglas por stack
- `warrior-hera` — ejecuta estrategia
- `kata-test-plan-design` — procedimiento de diseño
- `kata-quality-gate` — valida en el Gate 2
- [Growing Object-Oriented Software, Guided by Tests (GOOS)](http://www.growing-object-oriented-software.com/)
