# Lexis: Escenarios BDD Redactados desde Fuentes de Negocio

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Redacción de escenarios BDD para cualquier feature, antes de la implementación

## Propósito

El Behavior-Driven Development en Guardia es una disciplina opcional e independiente, usada cuando la brecha entre los criterios de aceptación numerados y la intención de negocio subyacente es lo suficientemente amplia como para merecer una capa separada en lenguaje de negocio. Cuando se adopta BDD para una feature, la fuente de verdad para esa intención debe ser inequívoca — de lo contrario, los escenarios derivan hacia describir el contrato o el código, y dejan de describir el negocio.

Esta Lexis fija la fuente (issue + Notion), el lenguaje (solo dominio) y la persistencia (el cuerpo del propio issue), de modo que cada paso posterior (mapeo a pruebas, validación, revisiones) lea desde la misma superficie canónica.

## Ley

> **Los escenarios BDD DEBEN ser redactados antes de que comience la implementación, derivados exclusivamente del issue de GitHub y de Notion (las fuentes de verdad de negocio), nunca del código fuente existente, pruebas o diffs de implementación. Los escenarios DEBEN expresarse en Gherkin (Given/When/Then) usando lenguaje de negocio (actores de dominio, entidades de dominio, resultados de negocio observables), nunca lenguaje técnico (verbos HTTP, códigos de estado, formas de payload, selectores de UI). Cuando el issue ya contiene Gherkin orientado a API o UI (típico de las plantillas `user-story-for-api` o `user-story-for-frontend`), esos escenarios DEBEN ser duplicados y reescritos en forma de negocio, preservando los originales sin modificación. Los escenarios de negocio finales DEBEN ser persistidos de regreso en el cuerpo del issue de GitHub, dentro de una sección delimitada por los marcadores `<!-- bdd:scenarios:start -->` y `<!-- bdd:scenarios:end -->`.**

## Alcance

- **Aplica a:** cualquier feature, bugfix o cambio de comportamiento para el cual se haya adoptado BDD (típicamente invocado a través de `/cry-bdd-create-scenarios`).
- **Agentes vinculados:** cualquier agente que produzca escenarios BDD; principalmente `warrior-hera` y `kata-bdd-create-scenarios`.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Reglas

### 1. Fuente de verdad

Fuentes permitidas para redactar escenarios:

- El issue de GitHub (título, cuerpo, comentarios, labels, asignados).
- Páginas de Notion relacionadas (cuando `notion` esté en `mcp.servers`).

Fuentes prohibidas durante la redacción:

- Código fuente de la aplicación, pruebas, fixtures, ADRs, especificaciones OpenAPI derivadas de la implementación, líneas de log.
- Diffs de pull request.
- Recuerdo del ingeniero sobre "lo que el código hace hoy".

El propósito es describir lo que el negocio quiere, no lo que el sistema simplemente hace.

### 2. Solo lenguaje de negocio

Cada escenario describe comportamiento observable externamente en términos de dominio.

| Prohibido en `Given`, `When`, `Then` | Reemplazar por |
|---|---|
| Verbos HTTP (`POST`, `GET`, `PUT`, `PATCH`, `DELETE`) | una acción de dominio ("el cliente solicita un reembolso") |
| Rutas HTTP (`/v1/refunds`) | la operación de dominio ("una solicitud de reembolso") |
| Códigos de estado (`201`, `409`, `422`) | el resultado de negocio ("el reembolso queda registrado", "el reembolso es rechazado") |
| Tokens de forma de payload (`{ "data": ... }`) | el efecto observable ("existe una entrada de auditoría") |
| Selectores de UI (`.btn-submit`, `[data-testid=...]`) | la acción del usuario ("el operador aprueba la liberación") |
| Nombres de framework (`fastapi`, `react`) | omitir |

### 3. Duplicar, nunca reemplazar

Cuando el issue ya contiene Gherkin de `user-story-for-api` o `user-story-for-frontend`, esos escenarios se mantienen intactos (siguen siendo útiles para validación de contrato). El agente duplica cada uno en una forma de negocio dentro del bloque dedicado `bdd:scenarios`. Ambas representaciones conviven en el issue.

### 4. Persistido en el cuerpo del issue

Los escenarios finales viven dentro del cuerpo del issue, en un bloque delimitado:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...
  Given ...
  When ...
  Then ...
<!-- bdd:scenarios:end -->
```

El bloque es el registro canónico y mutable. El agente usa `update_issue` de GitHub MCP (o equivalente) para escribirlo o refrescarlo. Re-ejecutar la kata de redacción reemplaza solo este bloque, nunca ninguna otra parte del cuerpo.

### 5. Redactado antes de la implementación

La cry/kata se rehúsa a ejecutar si el working tree contiene cambios de implementación no triviales contra el issue objetivo, salvo que el usuario confirme explícitamente un backfill. La asunción por defecto es BDD-first.

### 6. Sin reglas inventadas

Si una regla no está presente en el issue o en Notion, no entra como `Scenario:`. Las reglas pendientes se listan bajo una sub-sección `## Pending Questions` dentro del mismo bloque `bdd:scenarios`, esperando al usuario.

## Ejemplos

### Correcto

(Cuerpo del issue, antes)

```gherkin
Scenario: Successful refund creation
  When I send POST /v1/refunds with body { "payment_id": "p_1", "amount": 1000 }
  Then the API returns 201 with { "id": ..., "status": "pending" }
```

(Cuerpo del issue, después de ejecutar `/cry-bdd-create-scenarios`)

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: Customer requests a refund for an eligible payment
  Given a captured payment of 1000 BRL made by the customer in the last 30 days
  When the customer requests a refund for that payment
  Then a refund is recorded against the payment in pending state
  And the audit trail records the refund attempt with the requesting customer
<!-- bdd:scenarios:end -->
```

El escenario original orientado a API queda intacto encima del bloque.

### Incorrecto

```gherkin
Scenario: Customer requests a refund
  When the customer sends POST /v1/refunds with payload { ... }
  Then the response is 201
  And the JSON contains "id" and "status"
```

El escenario usa verbos HTTP, códigos de estado y forma de payload (violación de la Regla 2).

```
(no <!-- bdd:scenarios:start --> block in the issue body)
```

El bloque está ausente (violación de la Regla 4).

```
(scenarios derived by reading service.py and test_refund.py)
```

Se usó código como fuente (violación de la Regla 1).

## Validación Automatizada

- **Herramienta:** `kata-bdd-create-scenarios` impone la restricción de fuente (solo lecturas vía GitHub MCP y Notion MCP), ejecuta una verificación de lenguaje por tokens prohibidos y escribe el bloque vía GitHub MCP solo tras confirmación explícita del usuario. `kata-bdd-validate-scenarios` confirma la presencia y la forma del bloque.
- **Momento:** durante la redacción de los escenarios (invocación de la cry); en la revisión del PR cuando los escenarios acompañan un cambio.
- **Métrica:** 100% de las features que usan BDD tienen un bloque `bdd:scenarios` en el issue; 0 escenarios que contengan tokens técnicos prohibidos.
