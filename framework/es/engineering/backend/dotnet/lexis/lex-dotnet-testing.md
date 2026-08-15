# Lexis: Pruebas de Cambios .NET

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Cambios de comportamiento y correcciones en proyectos .NET

## Propósito

Garantizar que el comportamiento cambiado esté protegido en el nivel que detecta su riesgo real, incluida semántica relacional y contratos de frontera.

## Ley

> **Todo cambio de comportamiento .NET DEBE incluir una prueba determinista que falle sin el cambio y use infraestructura real cuando el riesgo dependa de la semántica del provider.**

## Alcance

- **Se aplica a:** features, correcciones, migraciones, contratos y refactorizaciones con comportamiento nuevo
- **Agentes vinculados:** Apollo-.NET y cualquier agente que produzca código .NET
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Reglas Verificables

1. La regla de dominio usa prueba unitaria; la frontera HTTP/evento usa contrato o integración; persistence relacional usa el provider real en container o ambiente aislado.
2. EF Core InMemory no valida traducción SQL, constraints, transacciones o concurrencia relacional.
3. Las pruebas no dependen de reloj, aleatoriedad, red u orden global sin control explícito.
4. Los mocks representan fronteras controladas; no reimplementan EF Core, ASP.NET Core o provider externo.
5. Una prueba flaky es un defecto: corregirla, aislarla con responsable y plazo, o bloquear la entrega.

## Consecuencias de Incumplimiento

1. **Bloqueo:** un cambio funcional sin protección no pasa el quality gate.
2. **Diagnóstico:** indicar riesgo sin cobertura o double inadecuado.
3. **Remediación:** agregar prueba en el nivel correcto y evidencia de fallo anterior cuando sea reproducible.

## Ejemplos

### Correcto

```csharp
[Fact]
public async Task Rejects_second_authorization_with_same_idempotency_key() { /* real database */ }
```

### Incorrecto

```csharp
[Fact]
public void Always_passes() => Assert.True(true);
```

## Validación Automatizada

- **Herramienta:** `dotnet test`, test runner del repositorio, Coverlet si está configurado y Testcontainers para semántica externa
- **Momento:** CI del pull request
- **Métrica:** 0 cambios funcionales sin prueba; 0 pruebas flaky toleradas silenciosamente; 0 EF InMemory para afirmar comportamiento relacional

## Referencias

- `lex-test-pyramid`, `lex-test-isolation`, `codex-test-strategy`
- `.references/topicos/05-testes-e-qualidade.md`
