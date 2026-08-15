# Lexis: Código Intencional y Verificable

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Código de aplicación, pruebas y automatizaciones mantenidos en el repositorio

## Propósito

Impedir que el ruido, el código muerto y la complejidad sin control oculten el comportamiento real. Esta Lexis cubre criterios objetivos; las decisiones contextuales pertenecen a `codex-code-design`.

## Ley

> **Todo código versionado DEBE expresar comportamiento activo con nombres del dominio, sin código muerto o comentado, sin comentarios que repitan la implementación y dentro de los límites de complejidad configurados por el proyecto.**

## Alcance

- **Se aplica a:** código de producción, pruebas, scripts y ejemplos ejecutables
- **Agentes vinculados:** todos los agentes que implementan, refactorizan o revisan código
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Reglas Verificables

1. Los comentarios explican una decisión, restricción, riesgo o comportamiento no evidente; no narran la línea siguiente.
2. No se puede versionar código comentado ni imports, parámetros, variables o miembros privados sin uso.
3. Los nombres deben ser buscables y reflejar el lenguaje del bounded context; se prohíben abreviaturas locales no documentadas.
4. Los límites de complejidad, tamaño de función, parámetros y nesting deben declararse en la configuración del analizador. Sin configuración, CI adopta el baseline de la stack e impide regresiones.
5. Una alerta de complejidad exige investigación y refactorización protegida o decisión registrada; no autoriza extracción mecánica que reduzca cohesión.

<HARD-GATE>
Subject: cambio de código antes de commit o entrega
Action: bloquear la entrega cuando exista código comentado, símbolo muerto, comentario que solo repita el código o regresión de los límites configurados
Preconditions: analizadores de la stack ejecutados sobre los archivos cambiados; diff revisado en nombres y comentarios
Scope: código de aplicación, pruebas y scripts versionados
Counter-pretexts: plazo corto, código generado manualmente, compatibilidad temporal, lint desactivado localmente
Exceptions: ninguna
</HARD-GATE>

## Consecuencias de Incumplimiento

1. **Bloqueo:** el cambio no pasa el quality gate.
2. **Diagnóstico:** la salida identifica archivo, regla y límite excedido.
3. **Remediación:** eliminar el ruido, simplificar con una prueba de protección o registrar la decisión técnica si debe cambiar el límite.

## Ejemplos

### Correcto

```csharp
// El proveedor puede confirmar después del timeout; la clave preserva la deduplicación en la reconciliación.
await gateway.AuthorizeAsync(request, idempotencyKey, cancellationToken);
```

### Incorrecto

```csharp
// Autoriza el pago.
await gateway.AuthorizeAsync(request, key, CancellationToken.None);
// await legacyGateway.AuthorizeAsync(request);
```

## Validación Automatizada

- **Herramienta:** analizadores de la stack (por ejemplo Roslyn/.NET analyzers, Ruff, ESLint), detector de código muerto y `kata-quality-gate`
- **Momento:** pre-commit y CI del pull request
- **Métrica:** 0 código comentado o muerto; 0 regresiones; 0 comentarios puramente narrativos en el diff

## Referencias

- `lex-dry`, `lex-no-silent-tech-debt`, `codex-code-design`
