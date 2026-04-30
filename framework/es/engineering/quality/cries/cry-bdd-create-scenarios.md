# Cry: Redactar Escenarios BDD de Negocio desde Issue + Notion

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Independiente — produce escenarios BDD orientados al negocio para un issue de GitHub y los escribe de regreso al cuerpo del issue

## Descripción

Atajo independiente para invocar `kata-bdd-create-scenarios`. Lee un issue de GitHub (y contexto de Notion cuando MCP esté configurado), produce escenarios Gherkin orientados al negocio y los persiste en el cuerpo del issue dentro de los marcadores `bdd:scenarios`. Nunca lee código fuente. Independiente de `/cry-implement-issue` — puede invocarse antes, después o totalmente fuera del flujo Issue-Driven.

## Uso

```
/cry-bdd-create-scenarios <issue-number> [<owner>/<repo>]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `issue-number` | Sí | Número del issue de GitHub | `42` |
| `<owner>/<repo>` | No | Por defecto: repo actual vía git remote | `guardiafinance/ahrena` |

## Prerrequisitos

- `github` listado en `mcp.servers` en `.ahrena/.directives`
- `notion` listado en `mcp.servers` (opcional, enriquece el contexto)
- Variables de entorno: `GITHUB_PAT` obligatoria; `NOTION_API_KEY` opcional
- Issue existente en GitHub

## Qué Hace el Comando

1. Invoca `kata-bdd-create-scenarios`.
2. La kata lee el issue y Notion (nunca código) y redacta escenarios orientados al negocio en Gherkin.
3. La kata duplica cualquier escenario API/UI ya presente en el issue, dejando los originales intactos.
4. La kata presenta al usuario el bloque `bdd:scenarios` propuesto para confirmación.
5. Tras la confirmación, la kata actualiza el cuerpo del issue vía GitHub MCP.

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Run kata-bdd-create-scenarios for issue #{{issue-number}}. Author business-focused BDD scenarios sourced exclusively from the GitHub issue body, comments, and related Notion pages. Do not read source code. Duplicate any existing API/UI Gherkin into a separate business-language form (preserve the originals). Wait for explicit user confirmation before updating the issue. Persist the final scenarios into the issue body inside the markers <!-- bdd:scenarios:start --> ... <!-- bdd:scenarios:end -->. Report scenario titles and slugs.

Strictly respect lex-bdd-scenarios (sources, language, persistence) and lex-mcp (no destructive write without explicit user confirmation).
```

## Ejemplo de Invocación

**Input:**

```
/cry-bdd-create-scenarios 42 guardiafinance/ahrena
```

**Salida esperada:**

- La kata obtiene el issue #42 (y Notion si está configurado).
- Detecta 2 escenarios orientados a API desde la plantilla user-story-for-api.
- Redacta 3 escenarios orientados al negocio.
- Presenta al usuario el bloque `bdd:scenarios` propuesto.
- Tras la confirmación, actualiza el cuerpo del issue. Los escenarios API originales permanecen sin cambios.
- Reporta los slugs de los escenarios:
  - `customer-requests-a-refund-for-an-eligible-payment`
  - `customer-cannot-refund-after-30-days`
  - `concurrent-refunds-deduplicate-by-idempotency-key`

## Restricciones

- **El código nunca es fuente.** Los archivos fuente y de prueba están fuera del alcance de este comando.
- **El issue debe existir.** Sin issue → el comando se rehúsa (sin auto-creación).
- **Confirmación obligatoria.** Sin escritura en el issue sin un "sí" explícito.
- **Independiente.** No entra en el flujo Issue-Driven, no bloquea ninguna fase ni gate.

## Cry vs Kata

| Aspecto | Cry | Kata |
|---|---|---|
| Naturaleza | Invocación rápida por número de issue | Procedimiento completo (leer, redactar, validar, confirmar, persistir) |
| Complejidad | Baja | Alta (9 pasos incluyendo MCP, validación de lenguaje, actualización idempotente del bloque) |

## Cries y Katas Asociados

- `kata-bdd-create-scenarios` — invocada por esta cry
- `cry-bdd-validate-scenarios` — verificación de cobertura tras la implementación
- `cry-implement-issue` — flujo ortogonal; esta cry puede ejecutarse junto a él sin acoplamiento

## Referencias

- `lex-bdd-scenarios`, `lex-bdd-coverage` — leyes
- `codex-bdd` — metodología
- `kata-bdd-create-scenarios`, `kata-bdd-validate-scenarios` — procedimientos
