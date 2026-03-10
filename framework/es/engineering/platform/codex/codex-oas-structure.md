# Codex: Orden de Operaciones en Paths OpenAPI

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Plataforma Guardia — estructura de paths en especificaciones OpenAPI 3.x

## Visión General

Este Codex define el orden en que los métodos HTTP deben aparecer en cada path en la especificación OpenAPI (OAS 3.x), para consistencia y legibilidad. Todo artefato que genera o edita especificaciones OAS en la plataforma Guardia debe respetar este orden al documentar las operaciones de un path.

## Contexto

- **Dominio:** Estructura de paths y operaciones en especificaciones OpenAPI 3.x.
- **Público objetivo:** Agentes y procedimientos que producen o mantienen specs OAS (kata-api-design-oas, Warrior Daedalus).
- **Actualización:** Cuando se modifique la convención de la plataforma para el orden de métodos.

## Contenido

### Orden obligatoria de las operaciones

En cada entrada de `paths` en la especificación OpenAPI (YAML o JSON), las operaciones (métodos HTTP) **DEBEN** listarse en el siguiente orden:

| Orden | Método HTTP | Uso típico |
|:-----:|-------------|------------|
| 1 | POST | Creación de recurso |
| 2 | GET | Lectura (uno o lista) |
| 3 | PUT | Sustitución completa |
| 4 | PATCH | Actualización parcial |
| 5 | DELETE | Exclusión (lógica o física) |

Al documentar un path (ej.: `/v1/transactions`), incluya solo las operaciones que expone el endpoint, **manteniendo esta secuencia**. Ejemplo: si el path tiene solo POST, GET y PATCH, deben aparecer en ese orden en el YAML/JSON.

### Restricciones técnicas

- Al generar o editar una especificación OpenAPI, el agente **DEBE** ordenar las operaciones de cada path conforme a la tabla anterior.
- Los métodos no utilizados en el path pueden omitirse; los que se documenten **DEBEN** seguir la secuencia POST → GET → PUT → PATCH → DELETE.
- El orden aplica al documento OAS (claves `post`, `get`, `put`, `patch`, `delete` en cada path), no al orden de definición de los paths en sí.

## Glosario

| Término | Definición |
|---------|------------|
| path | Ruta de URL en la spec OAS (ej.: `/v1/transactions`, `/v1/transactions/{entity_id}`) |
| operación | Método HTTP (post, get, put, patch, delete) documentado bajo un path |

## Referencias

- codex-restful-apis — Índice de las APIs RESTful de Guardia
- [OpenAPI Specification 3.x](https://spec.openapis.org/oas/v3.0.3)
