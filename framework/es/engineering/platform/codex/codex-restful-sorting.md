# Codex: Ordenación en APIs RESTful

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — APIs REST — ordenación

## Visión General

Reglas para ordenación de listados en APIs de la plataforma Guardia: propiedades permitidas, índices, ordenación estable y particionamiento. Se usa junto con la paginación.

## Contexto

- **Dominio:** ordenación de recursos en listados paginados de la plataforma Guardia.
- **Público objetivo:** implementadores y consumidores de APIs.
- **Actualización:** cuando la especificación de ordenación en el Hub sea alterada.

## Contenido

- Ordenación limitada a propiedades temporales: **created_at**, **updated_at**, **reference_at** (otros campos solo si documentados en el contrato y con índice).
- Uso de índices para evitar full scan; ordenación **estable** (criterio secundario ej.: entity_id) para que la paginación no duplique ni omita ítems.
- Parámetros: **order_by** (default created_at), **sort** (default asc). Ausencia → created_at asc.
- Valores no permitidos en order_by o sort → 400 Bad Request (ERR400_INVALID_PARAMETER, ORDER_BY_INVALID, SORT_INVALID).
- En escenarios con **particionamiento** (ej.: por tenant), la ordenación DEBE respetar el alcance de la partición.
- Excepción: ordenación fija por regla de negocio puede omitir order_by si justificada y registrada en PDR (Registro de Decisión de Producto).

## Referencias

- OAS
- [codex-restful-apis](codex-restful-apis.md) (índice); [codex-restful-pagination](codex-restful-pagination.md)
