# Cry: Diseño de API para Nueva Feature

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para diseñar la API REST de una nueva feature conforme a Lexis y Codex de Guardia

## Descripción

Este comando invoca al Warrior Daedalus (o al agente asumiendo su rol) para diseñar la API REST de una nueva feature: consultar Lexis y Codex RESTful y producir **especificación OpenAPI 3.x** (kata-api-design-oas) y **documento Markdown** estructurado de la API (kata-api-design-doc), ambos en **`docs/{context}/oas/`**.

## Uso

```
/cry-api-design <descripción de la feature> [base path]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `descripción de la feature` | Sí | Descripción del dominio, entidades, operaciones y reglas de negocio relevantes para la API | "Módulo de transferencias programadas: crear, listar, actualizar y cancelar; listado paginado y ordenable; mutaciones idempotentes" |
| `base path` | No | Prefijo de URL deseado (ej.: /v1/transactions). Si se omite, el agente propone uno basado en la feature | `/v1/scheduled-transfers` |

## Qué Hace el Comando

1. Interpreta la descripción de la feature y el base path (si se informó)
2. Asume el rol del Warrior Daedalus (especialista en diseño de API) o delega al agente que ejecuta kata-api-design-oas o kata-api-design-doc (según el formato solicitado)
3. El Warrior Daedalus (o el agente en su rol) consulta lex-directives y las Lexis/Codex RESTful, entidades, idempotencia, errores y auth
4. Identifica recursos, operaciones, paginación, ordenamiento y necesidad de Idempotency-Key
5. Produce especificación (OpenAPI o Markdown) con endpoints, métodos, status codes, headers, payloads y errores
6. Entrega el artefacto en el formato solicitado o inline

## Template de Prompt

```
Contexto:
- Descripción de la feature: {{descripción de la feature}}
- Base path (opcional): {{base path}}

Tarea:
Actúa como el Warrior Daedalus (Especialista en Diseño de API) y ejecuta de forma iterativa **kata-api-design-oas** y **kata-api-design-doc** (los Katas consultan las Lexis y Codex RESTful conforme su documentación). Basándote en la descripción de la feature, haz preguntas de clarificación cuando sea necesario y refina el diseño en base a las respuestas. Produce la especificación OpenAPI y el documento de la API en `docs/{context}/oas/`. Usa el base path informado o propone uno adecuado.

Formato de salida:
- Guardar en `docs/{context}/oas/` conforme a `lex-feature-design-docs`
- Crear el directorio si no existe en el proyecto
- Crear o actualizar la especificación OpenAPI y el documento Markdown de la API en ese path
- Lista o tabla de endpoints (path, método, resumen); para cada endpoint: parámetros, headers obligatorios (ej.: Idempotency-Key en mutaciones), status codes, estructura de request/response (data, pagination, errors conforme codex-restful-payload)
```

## Ejemplo de Invocación

**Input:**

```
/cry-api-design "Módulo de transferencias programadas: el usuario puede crear, listar, actualizar y cancelar; listado paginado y ordenable por fecha; crear/actualizar/cancelar idempotentes" /v1/scheduled-transfers
```

**Output esperado:**

Respuesta estructurada del Warrior Daedalus con:
- Recursos identificados (ej.: scheduled-transfers)
- Endpoints: POST (crear), GET (listar con paginación/ordenamiento), GET por id, PATCH (actualizar), DELETE (cancelar)
- Uso de Idempotency-Key en POST y PATCH; status 200/201/204/400/409/422 etc.; payload con data/pagination/errors conforme codex-restful-payload
- Especificación creada o actualizada en `docs/{context}/oas/` (directorio creado si no existía)

## Restricciones

- El Cry no implementa código; solo dispara el diseño de API
- La descripción de la feature debe ser suficiente para identificar recursos y operaciones; si está vaga, el agente puede pedir complemento
- Las excepciones a las Lexis deben documentarse en un ADR; el agente puede señalar cuándo una decisión requiere ADR

## Cry vs Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida con descripción de la feature y base path | Procedimiento completo en múltiples pasos |
| **Complejidad** | Baja (1 comando) | Alta (7 pasos: directivas, consulta Lexis/Codex, recursos, endpoints, errores, especificación, validación) |
| **¿Configura agente?** | Sí (asume el rol del Warrior Daedalus) | Sí (define todos los pasos del diseño) |
| **Ejemplo** | "/cry-api-design crear/listar/cancelar transferencias programadas" | Ejecutar kata-api-design-oas o kata-api-design-doc con inputs explícitos, según el formato deseado |

## Kata y Warrior Asociados

- **kata-api-design-oas** — Diseño de API y producción de especificación OpenAPI 3.x en `docs/{context}/oas/`
- **kata-api-design-doc** — Diseño de API y producción de documento Markdown estructurado en `docs/{context}/oas/`
- **warrior-daedalus** — Especialista en Diseño de API; ejecuta kata-api-design-oas y kata-api-design-doc (ambos en `docs/{context}/oas/`)

## Referencias

- `kata-api-design-oas`, `kata-api-design-doc` — Procedimientos ejecutados por el Warrior Daedalus (los Katas consultan las Lexis y Codex RESTful; ver documentación de los Katas)
