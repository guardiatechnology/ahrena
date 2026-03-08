# Codex: Tratamiento de Errores en la Plataforma Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — tratamiento de errores

## Visión General

Este Codex describe el estándar para representación, categorización y manipulación de errores en la plataforma Guardia. Objetiva consistencia, claridad y rastreabilidad en la comunicación de fallos entre servicios, consumidores de API e interfaces.

## Contexto

- **Dominio:** estructura del payload de error, códigos, retentativa y seguridad.
- **Público objetivo:** implementadores de APIs y desarrolladores que tratan errores.
- **Actualización:** cuando la especificación de Tratamiento de Errores en el Hub sea alterada o cuando se registren nuevos errores.

## Contenido

### Estructura del payload de error

Todos los errores DEBEN encapsularse en el campo `errors`, que DEBE ser un array de objetos (incluso con un solo error). Cada objeto DEBE contener:

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| code | string | Código semántico en UPPER_SNAKE_CASE, único en el dominio; prefijo ERR + código HTTP (ej.: ERR400_, ERR409_). |
| reason | string | Categoría semántica para tratamiento programático; DEBE estar en Errores Conocidos en el Hub. |
| message | string | Descripción orientada al desarrollador; NUNCA exponer datos sensibles ni stack trace. |

### Ejemplo de payload

```json
{
  "errors": [
    {
      "code": "ERR402_INSUFFICIENT_FUNDS",
      "reason": "PAYMENT_IS_REQUIRED",
      "message": "Saldo insuficiente para la operación solicitada."
    }
  ]
}
```

### Reglas generales

- **code:** único, UPPER_SNAKE_CASE, coherente con el status HTTP.
- **reason:** indica causa específica; puede haber varios reason para un mismo code; NO contener datos sensibles.
- **message:** informativa para el desarrollador; puede ser internacionalizable vía Accept-Language; NUNCA exponer información interna sensible.
- **Documentación:** para cada operación, documentar los pares code/reason posibles en el contrato (OpenAPI) y en el catálogo de Errores Conocidos del proyecto.

### Retentativa

- Las condiciones para retry DEBEN documentarse en Errores Conocidos.
- Cuando aplique, incluir header `Retry-After` con tiempo recomendado.
- Los clientes DEBEN aplicar backoff exponencial base 2 cuando el tiempo no se informe, hasta un máximo de 4 intentos.
- Tras el 4º intento, adoptar patrón de circuit breaker; estado half-open puede probarse cada 60 segundos.
- Número de intentos e intervalos configurables por el cliente, respetando límites de la plataforma.

### Creación de nuevos errores

- DEBEN seguir la estructura estandarizada (code, reason, message).
- DEBEN registrarse en el catálogo de Errores Conocidos del proyecto.
- Nuevos grupos de reason DEBEN justificarse por contextos de negocio inéditos.
- **Consideraciones de seguridad:** evitar mensajes que permitan enumeración (ej.: usuario existe/no existe); no incluir datos internos ni stack trace.
- **Monitorización:** garantizar que los nuevos errores se incluyan en métricas y alertas conforme a la política de la plataforma.

### Seguridad

- Los errores de autenticación NUNCA DEBEN indicar si un usuario existe.
- Ningún mensaje DEBE contener stack trace ni identificadores internos sensibles.

### Monitorización

- TODOS los errores DEBEN registrarse para auditoría.
- Errores 4xx y 5xx DEBEN monitorizarse continuamente.
- Errores 5xx DEBEN disparar alertas.

### Cuándo usar

Esta especificación DEBE aplicarse en: APIs REST públicas e internas; comunicación entre microservicios; integraciones con socios; UIs que consuman APIs de la plataforma.

## Referencias

- codex-restful-payload (estructura de errors); OpenAPI (catálogo de errores)
