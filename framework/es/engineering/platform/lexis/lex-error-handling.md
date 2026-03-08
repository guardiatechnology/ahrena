# Lexis: Estructura Estandarizada de Errores en las Respuestas

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma Guardia — tratamiento de errores

## Propósito

Garantizar consistencia, claridad y rastreabilidad en la comunicación de fallos entre servicios, consumidores de API e interfaces. Los errores estandarizados permiten tratamiento programático y diagnóstico; los errores de autenticación que indiquen existencia de usuario comprometen la seguridad.

## Ley

> **Los errores retornados por la plataforma Guardia DEBEN seguir la estructura estandarizada (array errors con propiedades code, reason y message); los códigos DEBEN tener el prefijo ERR y el código HTTP (ej.: ERR400_); reason DEBEN estar listados en Errores Conocidos; retentativa y circuit breaker conforme a la especificación; los errores de autenticación NUNCA DEBEN indicar si un usuario existe.**

## Alcance

- **Se aplica a:** APIs REST públicas e internas, comunicación entre microservicios, integraciones y UIs que consuman APIs de la plataforma Guardia.
- **Agentes vinculados:** todos los implementadores de APIs y clientes que traten respuestas de error.
- **Excepciones:** Ninguna para la estructura de error; los nuevos reason deben estar justificados y registrados en Errores Conocidos.

## Consecuencias de Violación

1. **Inconsistencia:** los clientes no pueden tratar errores de forma uniforme.
2. **Seguridad:** mensajes de autenticación que revelen existencia de usuario facilitan enumeración.
3. **Remediación:** estandarizar payload de error y revisar mensajes sensibles.

## Ejemplos

### Correcto

Payload con `errors: [{ "code": "ERR402_INSUFFICIENT_FUNDS", "reason": "PAYMENT_IS_REQUIRED", "message": "..." }]`; reason en Errores Conocidos; 401 sin indicar si el usuario existe.

### Incorrecto

Error sin array errors; code sin prefijo ERR + HTTP; reason no catalogado sin justificación; mensaje de login diferenciando "usuario no encontrado" y "contraseña incorrecta".

## Validación Automatizada

- **Herramienta:** revisión de contrato (OpenAPI) y código; pruebas de error.
- **Momento:** revisión de PR y pruebas de integración.
- **Métrica:** 0 respuestas de error fuera de la estructura; 0 mensajes de autenticación que indiquen existencia de usuario.

## Referencias

- [Especificación de Tratamiento de Errores — Hub Guardia](https://hub.guardia.finance/docs/specifications/error-handling/)
- codex-error-handling (engineering/platform)
