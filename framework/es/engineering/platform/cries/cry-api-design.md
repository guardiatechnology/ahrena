# Cry: Diseño de API para Nueva Feature

> **Prefijo:** `cry-` | **Tipo:** Comando Recorrente | **Alcance:** Atajo para diseñar la API REST de una nueva feature conforme a Lexis y Codex de Guardia

## Descripción

Este comando invoca al Warrior Daedalus (o al agente asumiendo su rol) para diseñar la API REST de una nueva feature: consultar Lexis y Codex RESTful y producir **especificación OpenAPI 3.x** (kata-api-design-oas) y **documento Markdown** estructurado de la API (kata-api-design-doc), ambos en **paths.oas**.

## Uso

```
/cry-api-design <descripción de la feature> [base path]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `descripción de la feature` | Sí | Descripción del dominio, entidades, operaciones y reglas de negocio relevantes para la API | "Módulo de agendamiento de transferencias: crear, listar, actualizar y cancelar; listado paginado y ordenable; mutaciones idempotentes" |
| `base path` | No | Prefijo de URL deseado (ej.: /v1/transactions). Si se omite, el agente propone en función de la feature | `/v1/scheduled-transfers` |

## Qué Hace el Comando

1. Interpreta la descripción de la feature y el base path (si se informa)
2. Asume el rol del Warrior Daedalus (especialista en diseño de API) o delega al agente que ejecuta kata-api-design-oas o kata-api-design-doc (según formato solicitado)
3. Consulta lex-directives y las Lexis/Codex RESTful, entidades, idempotencia, errores y auth
4. Identifica recursos, operaciones, paginación, ordenación y necesidad de Idempotency-Key
5. Produce especificación (OpenAPI o Markdown) con endpoints, métodos, status, headers, payloads y errores
6. Entrega el artefacto en el formato solicitado o inline

## Prompt Template

```
Contexto:
- Descripción de la feature: {{descripción de la feature}}
- Base path (opcional): {{base path}}

Tarea:
Actúe como el Warrior Daedalus (Especialista en Diseño de API) y ejecute de forma iterativa el **kata-api-design-oas** y el **kata-api-design-doc**, produciendo ambos artefactos en paths.oas.
Con base en la descripción de la feature anterior, haga preguntas de clarificación cuando sea necesario (alcance, autenticación, paginación, ordenación, base path, criterios específicos) y refine el diseño con base en las respuestas. Consulte las Lexis y Codex RESTful de Guardia y produzca la especificación OpenAPI y el documento de la API en paths.oas.
Use el base path informado o proponga uno adecuado.

Formato de salida:
- Consultar **paths.oas** en `.ahrena/.directives` para el destino
- Crear el directorio (paths.oas) si no existe en el proyecto
- Crear o actualizar la especificación OpenAPI y el documento Markdown de la API en ese path
- Lista o tabla de endpoints (path, método, resumen); para cada endpoint: parámetros, headers obligatorios (ej.: Idempotency-Key en mutaciones), códigos de status, estructura de request/response (data, pagination, errors conforme codex-restful-payload)
```

## Ejemplo de Invocación

**Input:**

```
/cry-api-design "Módulo de agendamiento de transferencias: usuario puede crear, listar, actualizar y cancelar; listado paginado y ordenable por fecha; crear/actualizar/cancelar idempotentes" /v1/scheduled-transfers
```

**Output esperado:**

Respuesta estructurada del Warrior Daedalus con:
- Recursos identificados (ej.: scheduled-transfers)
- Endpoints: POST (crear), GET (listar con paginación/ordenación), GET por id, PATCH (actualizar), DELETE (cancelar)
- Uso de Idempotency-Key en POST y PATCH; status 200/201/204/400/409/422 etc.; payload con data/pagination/errors conforme codex-restful-payload
- Especificación creada o actualizada en el path **paths.oas** (`.ahrena/.directives`; directorio creado si no existía)

## Restricciones

- El Cry no implementa código; solo dispara el diseño de API
- La descripción de la feature debe ser suficiente para identificar recursos y operaciones; si es vaga, el agente puede pedir complemento
- Excepciones a las Lexis deben documentarse en ADR; el agente puede señalar cuando una decisión exija ADR

## Cry vs Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida con descripción de la feature y base path | Procedimiento completo en múltiples pasos |
| **Complejidad** | Baja (1 comando) | Alta (7 pasos: directivas, consulta Lexis/Codex, recursos, endpoints, errores, especificación, validación) |
| **¿Configura agente?** | Sí (asume rol del Warrior Daedalus) | Sí (define todos los pasos del diseño) |
| **Ejemplo** | "/cry-api-design crear/listar/cancelar transferencias agendadas" | Ejecutar kata-api-design-oas o kata-api-design-doc con inputs explícitos, según formato deseado |

## Kata y Warrior Asociados

- **kata-api-design-oas** — Diseño de API y producción de especificación OpenAPI 3.x en paths.oas
- **kata-api-design-doc** — Diseño de API y producción de documento Markdown estructurado en paths.oas
- **warrior-daedalus** — Especialista en Diseño de API; ejecuta kata-api-design-oas y kata-api-design-doc (ambos en paths.oas)

## Referencias

- lex-restful-apis, lex-entities, lex-idempotency, lex-error-handling, lex-auth
- codex-restful-apis, codex-restful-status-codes, codex-restful-payload, codex-restful-headers, codex-restful-pagination, codex-restful-sorting
