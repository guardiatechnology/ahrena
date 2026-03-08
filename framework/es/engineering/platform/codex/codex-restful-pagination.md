# Codex: Paginación en APIs RESTful

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — APIs REST — paginación

## Visión General

Parámetros, estructura de respuesta y comportamientos para listados paginados en la plataforma Guardia. Tokens opacos, ordenación estable y errores estandarizados.

## Contexto

- **Dominio:** paginación de recursos en APIs HTTP de la plataforma Guardia.
- **Público objetivo:** implementadores y consumidores de APIs.
- **Actualización:** cuando la especificación de paginación en el Hub sea alterada.

## Contenido

### Petición

| Parámetro | Tipo | Default | Máximo | Regla |
|-----------|------|---------|--------|-------|
| page_size | uint32 | 20 | 100 | Rechazar por encima del límite con 400 ERR400_INVALID_PARAMETER (PAGE_SIZE_TOO_LARGE, etc.) |
| page_token | string | — | — | Token opaco; retornado en llamadas anteriores |
| order_by | string | created_at | — | created_at, updated_at, reference_at; otro valor → 400 ORDER_BY_INVALID |
| sort | string | asc | — | asc, desc (case insensitive); otro → 400 SORT_INVALID |

### Respuesta

- `data`: array de la página actual.
- `pagination`: page_size, total_count, first_page_token, previous_page_token, next_page_token, last_page_token (todos presentes; nulos cuando no aplique). **total_count** PUEDE omitirse cuando el coste de cálculo sea prohibitivo (ej.: conteo exacto en bases muy grandes); cuando se omita, documentar en el contrato.
- Headers: Cache-Control (ej.: max-age=900), Link con rel first, previous, next, last.
- **Compliance by Design:** tokens opacos y expiración limitada; logs de acceso con X-Grd-Trace-Id; sin filtración de datos entre tenants; parámetros validados y rechazados con code/reason estandarizados.

### Comportamientos

- Primera página: sin page_token, page_size=20.
- Soporte a paginación reversa (previous_page_token, first_page_token).
- Ordenación estable y determinística.
- Tokens opacos (criptografiados/firmados); expiración (ej.: 10 min); log con X-Grd-Trace-Id.
- Sin resultados: 200 OK, lista vacía, total_count=0.

### Errores conocidos

| Escenario | HTTP | code | reason |
|-----------|------|------|--------|
| page_token inválido/expirado | 400 | ERR400_INVALID_PARAMETER | PAGE_TOKEN_INVALID, PAGE_TOKEN_EXPIRED |
| page_size inválido/por encima del límite | 400 | ERR400_INVALID_PARAMETER | PAGE_SIZE_INVALID, PAGE_SIZE_TOO_LARGE |
| order_by/sort inválido | 400 | ERR400_INVALID_PARAMETER | ORDER_BY_INVALID, SORT_INVALID |

Ejemplo de respuesta de error (page_token inválido):

```json
{
  "errors": [
    {
      "code": "ERR400_INVALID_PARAMETER",
      "reason": "PAGE_TOKEN_INVALID",
      "message": "El token de paginación informado es inválido o ha expirado."
    }
  ]
}
```

## Referencias

- HATEOAS
- [codex-restful-apis](codex-restful-apis.md) (índice); [codex-restful-sorting](codex-restful-sorting.md)
