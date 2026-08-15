# Lexis: Fronteras Seguras en .NET

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Entradas, autorización, secretos e integraciones de aplicaciones .NET

## Propósito

Impedir que confianza del cliente, datos sensibles o valores externos crucen fronteras sin validación y política explícitas.

## Ley

> **Toda frontera .NET DEBE validar entrada y autorización en el servidor, obtener secretos de proveedores seguros, parametrizar acceso a datos e impedir que logs, errores o telemetría expongan información sensible.**

## Alcance

- **Se aplica a:** endpoints, consumers, jobs, persistence, HTTP clients y configuración
- **Agentes vinculados:** Apollo-.NET y revisores de backend
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Reglas Verificables

1. Authentication prueba identidad; authorization valida acción y recurso en cada operación protegida.
2. Datos del cliente, claims y headers no reemplazan consulta o política server-side de ownership.
3. SQL usa parámetros o LINQ traducible; se prohíbe concatenar entrada en comandos.
4. URLs externas controlables por usuario requieren allowlist y mitigación de SSRF.
5. Secretos no aparecen en código, `appsettings*.json` versionado, errores, snapshots o logs.
6. Logs usan campos estructurados y masking; no emiten tokens, PAN, CVV, contraseñas o PII innecesaria.

## Consecuencias de Incumplimiento

1. **Bloqueo:** el cambio no puede entregarse.
2. **Respuesta:** detener propagación, rotar el secreto cuando corresponda y activar gestión de incidente.
3. **Remediación:** validar en la frontera, mover secretos al provider, parametrizar consultas y agregar prueba negativa.

## Ejemplos

### Correcto

```csharp
var card = await db.Cards.SingleOrDefaultAsync(
    item => item.Id == cardId && item.AccountId == subject.AccountId,
    cancellationToken);
```

### Incorrecto

```csharp
logger.LogInformation("Authorization {Token} for card {Pan}", token, pan);
```

## Validación Automatizada

- **Herramienta:** secret scanning, SAST, NuGet vulnerability audit, analyzers y pruebas de autorización
- **Momento:** pre-commit, CI y revisión de dependencias
- **Métrica:** 0 secretos o datos sensibles; 0 SQL concatenado; cada operación protegida cambiada tiene prueba de denegación

## Referencias

- `lex-auth`, `lex-error-handling`
- `.references/topicos/09-seguranca-privacidade-e-supply-chain.md`
