# Lexis: Corrección y Seguridad de Memoria .NET

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Código C# asíncrono, nullability y ownership de recursos

## Propósito

Evitar deadlocks, operaciones huérfanas, `NullReferenceException` previsibles, fuga de recursos, estados inválidos y presión innecesaria sobre el garbage collector en servicios .NET.

## Ley

> **Todo código C# de producción DEBE permanecer memory-safe por defecto, explicitar ownership y estados inválidos, mantener nullable reference types habilitado, propagar cancelación, evitar sync-over-async y cumplir budgets medidos de asignación en hot paths.**

## Alcance

- **Se aplica a:** proyectos C# de producción, workers, APIs, bibliotecas y adapters
- **Agentes vinculados:** Apollo-.NET y cualquier agente que cambie código C#
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Reglas Verificables

1. Los proyectos nuevos usan `<Nullable>enable</Nullable>`; no se suprimen warnings de nullability sin justificación local verificable.
2. Los métodos asíncronos cancelables reciben y propagan `CancellationToken`, incluso en HTTP, base de datos, colas y delays.
3. `.Result`, `.Wait()` y `.GetAwaiter().GetResult()` están prohibidos en flujos asíncronos de aplicación.
4. Quien crea un recurso `IDisposable`/`IAsyncDisposable` ejecuta su liberación; el consumidor no descarta recursos inyectados.
5. `async void` se restringe a event handlers exigidos por el framework.
6. Código de dominio y aplicación no usa `unsafe`, punteros o acceso no verificado a memoria. Interop inevitable queda aislado en un adapter mínimo, con justificación, pruebas de bounds/lifetime y review explícito.
7. Hot paths tienen budget de asignación y evidencia de profiler/benchmark. Loops por elemento no crean colecciones, strings, closures, boxing o tasks descartables sin necesidad medida.
8. `Span<T>`, `Memory<T>`, `stackalloc` y `ArrayPool<T>` solo se usan cuando reducen asignación medida y el lifetime es demostrablemente correcto; buffers sensibles se limpian antes de devolverlos.
9. Value Objects pequeños e inmutables pueden usar `readonly record struct`; se evitan structs grandes o mutables por costo de copia y aliasing confuso.
10. Aritmética cuyo overflow cambia dinero, versión, secuencia o límite usa `checked` o tipo de dominio validado. Estados de dominio son cerrados y tratados exhaustivamente cuando lo permite el lenguaje.

## Consecuencias de Incumplimiento

1. **Bloqueo:** falla build, análisis o quality gate.
2. **Diagnóstico:** identificar símbolo, flujo de cancelación o recurso sin ownership.
3. **Remediación:** corregir firma y propagación, reemplazar bloqueo síncrono o definir lifetime.

## Ejemplos

### Correcto

```csharp
public Task<Card?> FindAsync(Guid id, CancellationToken cancellationToken) =>
    db.Cards.SingleOrDefaultAsync(card => card.Id == id, cancellationToken);
```

### Incorrecto

```csharp
public Card Find(Guid id) => FindAsync(id, CancellationToken.None).Result!;
```

## Validación Automatizada

- **Herramienta:** `dotnet build`, .NET/Roslyn analyzers y pruebas
- **Momento:** pre-commit y CI
- **Métrica:** 0 warnings nuevos de nullability/analyzers; 0 sync-over-async; 100% de llamadas cancelables cambiadas propagan token; 0 `unsafe` en dominio/aplicación; hot paths cambiados sin regresión del budget de asignación

## Referencias

- `.references/topicos/01-csharp-runtime-e-biblioteca-padrao.md`
- Fuentes oficiales catalogadas en `.references/fontes/dotnet-oficial.md`
