# Codex: Ingeniería .NET

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Desarrollo, datos, operación y entrega de aplicaciones .NET

## Resumen

Este Codex es la referencia principal de Apollo-.NET. Cubre C#, ASP.NET Core, EF Core, pruebas, resiliencia, observabilidad y delivery, tratando Clean Code y DDD como criterios de decisión y no estructuras impuestas.

## Contexto

- **Dominio:** aplicaciones y bibliotecas .NET modernas
- **Público objetivo:** Apollo-.NET, desarrolladores y revisores de backend
- **Actualización:** ante cambios del SDK soportado, target framework, analyzers, contratos operativos o ADR de arquitectura
- **Baseline local observado:** SDK 10.0.400 y runtime 10.0.11 el 2026-08-14; cada proyecto declara su `global.json`/TFM y no hereda esta versión por accidente

## Contenido

### 1. Descubrimiento Antes de Implementar

Inspeccionar `global.json`, `*.sln`/`*.slnx`, `*.csproj`, `Directory.Build.*`, `Directory.Packages.props`, locks, analyzers y CI. Registrar versión confirmada, comandos del repositorio y diferencias local/pipeline.

### 2. C# y Runtime

| Decisión | Directriz |
|---|---|
| Nullability | Habilitar y modelar ausencia; no propagar `!` |
| Async | Async end-to-end, cancelación propagada, sin sync-over-async |
| Recursos | Ownership explícito; `await using` para recursos asíncronos |
| Excepciones | Excepciones para fallos excepcionales; resultados tipados para outcomes esperados cuando aclaren el contrato |
| LINQ | Considerar ejecución diferida, enumeración repetida y traducción del provider |
| Tiempo/IDs | Inyectar `TimeProvider` y generadores cuando importe el determinismo |

### 2.1. Disciplina Inspirada en Rust

El objetivo no es simular un borrow checker en C#, sino importar propiedades que aumentan la corrección:

| Propiedad | Aplicación idiomática en .NET |
|---|---|
| Memory safety | Permanecer en safe code; aislar interop; nunca exponer punteros/lifetimes al dominio |
| Ownership | Quien crea descarta; lifetimes de DI explícitos; buffers alquilados vuelven en `finally` |
| Inmutabilidad | `record`, `readonly` y colecciones inmutables/read-only en fronteras de dominio |
| Estados válidos | Factories/constructores protegen invariantes; jerarquías cerradas y pattern matching exhaustivo |
| Errores esperados | Result/union tipado cuando el caller decide; exceptions para fallos excepcionales |
| Corrección aritmética | `checked`, tipos monetarios/de dominio y pruebas de boundary/overflow |
| Zero-cost cuando se demuestra | `Span<T>`, `Memory<T>`, structs y pooling solo con benchmark y lifetimes simples |

#### Estrategia de Asignación

1. Medir con `dotnet-counters`, `dotnet-trace`, profiler y BenchmarkDotNet antes de optimizar.
2. Reducir primero trabajo evitable: materialización, enumeración repetida, closures, boxing, strings intermedias y buffers por elemento.
3. Preferir streaming y buffers del caller en hot paths; conservar APIs comunes donde asignación no afecta SLO/costo.
4. Usar pooling al final: cambia GC por ownership manual, retención de memoria y riesgo de datos residuales.
5. Registrar throughput, bytes/op, Gen0/1/2 y memoria retenida; menos allocations sin impacto medible no justifica complejidad.

### 3. Arquitectura, Clean Code y DDD

Las dependencias apuntan hacia políticas estables; el dominio no importa ASP.NET Core, EF Core o SDK de provider. Esto no exige cantidad fija de proyectos. Separar por fronteras reales de cambio, prueba, deploy u ownership. Consultar `codex-code-design` y `codex-domain-driven-design`.

### 4. ASP.NET Core

| Tema | Directriz |
|---|---|
| Pipeline | El orden de middleware es comportamiento; probar auth, authorization, errores y observabilidad |
| Contratos | Validar en la frontera y mantener domain models fuera del wire format |
| DI/options | Lifetimes explícitos; validar options al iniciar; evitar service locator |
| HTTP clients | Usar `IHttpClientFactory`, timeout budget, cancelación y política por dependencia |
| Health | Liveness verifica proceso; readiness capacidad de servir sin cascada |
| Pruebas | `WebApplicationFactory` para el pipeline real cuando corresponda |

### 5. EF Core y Consistencia

- `DbContext` es corto, representa unidad de trabajo y no es thread-safe.
- Inspeccionar SQL/traducción de queries críticas; evitar N+1, tracking innecesario y materialización temprana.
- Constraints del banco protegen invariantes persistentes; validación de aplicación mejora feedback, no las reemplaza.
- Concurrencia optimista necesita token, respuesta de conflicto y política consciente de retry.
- Transacción local no cubre HTTP/colas. Evaluar outbox/inbox y consumers idempotentes.
- Migraciones usan expand/contract cuando coexisten versiones; definir backup, duración, locks, rollback y compatibilidad.
- Un commit con timeout puede haber confirmado: reconciliar antes de repetir un efecto financiero.

### 6. Resiliencia y Observabilidad

Definir timeout budget por dependencia. Retry solo para fallos transitorios y operaciones idempotentes, con límite y jitter. Circuit breaker y bulkhead protegen recursos, no corrigen contratos. Correlacionar logs, métricas y traces sin datos sensibles ni cardinalidad sin control. Alertas apuntan a impacto/SLO y runbook.

### 7. Pruebas

Elegir nivel por riesgo: unidad para reglas, integración para adapters/providers, contrato para fronteras y pocos end-to-end para flujos críticos. Usar xUnit/NUnit del repositorio. Usar Testcontainers o infraestructura aislada cuando importe la semántica externa. Cobertura muestra huecos; no prueba calidad.

### 8. Build, Dependencias y Delivery

| Tema | Directriz |
|---|---|
| SDK/TFM | Fijar política con `global.json`; declarar TFMs soportados |
| Paquetes | Gestión central cuando se adopte; lock y auditoría de vulnerabilidades |
| Build | Warnings relevantes como errores; analyzers versionados; artefacto reproducible |
| Publicación | Elegir framework-dependent/self-contained conscientemente |
| Trimming/AOT | Solo tras probar reflexión, serialización, compatibilidad y startup |
| Container | Imagen mínima soportada, usuario no-root, health, shutdown ordenado |
| Deploy | Promover el mismo artefacto; schema compatible; rollback/reconciliación explícitos |

### Decisiones Vigentes

| Decisión | Estado | Consecuencia |
|---|---|---|
| Referencia independiente de versión con baseline registrado | Confirmada | Reglas de versión requieren verificar proyecto y docs oficiales |
| Arquitectura guiada por fronteras, no template fijo | Confirmada | Proyectos pequeños pueden seguir simples |
| Patterns declaran cuándo usar y evitar | Propuesta para Ahrena v2 | Apollo-.NET justifica un pattern antes de crear estructura |

### Restricciones Técnicas

- No asumir que el SDK instalado es el soportado por el repositorio.
- No repetir operaciones no idempotentes o commits inciertos sin reconciliación.
- No usar `DbContext` en paralelo ni ocultar su lifetime en singleton.
- No incluir PII, tokens, PAN o secrets en logs/traces.
- No usar `unsafe` en dominio/aplicación ni introducir pooling/`stackalloc` sin benchmark, bounds claros y pruebas de lifetime.
- No adoptar Native AOT, CQRS, Event Sourcing o microservices sin evidencia y plan operativo.

## Glosario

| Término | Definición |
|---|---|
| TFM | Target Framework Moniker del proyecto |
| Timeout budget | Tiempo total repartido entre llamadas e intentos |
| Expand/contract | Migración compatible por etapas para versiones coexistentes |
| Commit incierto | Fallo de comunicación cuyo resultado transaccional es desconocido |

## Referencias

- `lex-dotnet-runtime-safety`, `lex-dotnet-boundary-security`, `lex-dotnet-testing`
- `codex-code-design`, `codex-domain-driven-design`, `codex-test-strategy`
- `.references/TRILHA-DOTNET.md`, `.references/topicos/01-10` y `.references/fontes/dotnet-oficial.md`
