# Cry: Nuevo SDK Guardia en TypeScript/Node.js

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para escafoldar (o llevar a conformidad) un SDK Guardia en TypeScript/Node.js según `lex-sdk-typescript` y `codex-sdk-typescript`

## Descripción

Este comando invoca `kata-sdk-typescript-scaffold` para producir un SDK en TypeScript/Node.js que consume la API REST de Guardia y está en conformidad con `lex-sdk-typescript` desde el primer día. El mismo comando lleva un SDK heredado a conformidad cuando la flag `--from` apunta a un directorio existente.

## Uso

```
/cry-new-sdk-typescript <nombre-del-sdk> <bounded-context> [--target=npm-public|npm-internal|both] [--from=<ruta>]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `nombre-del-sdk` | Sí | Nombre del paquete siguiendo la convención canónica. | `@guardia/sdk-scheduled-payments` |
| `bounded-context` | Sí | Bounded context de Guardia atendido por el SDK. Se usa para localizar `docs/{context}/oas/openapi.yaml`. | `scheduled-payments` |
| `--target` | No | Objetivo de distribución. Default: `npm-public`. | `--target=both` |
| `--from` | No | Ruta a un SDK existente para llevar a conformidad en vez de escafoldar desde cero. | `--from=sdks/legacy-billing` |

## Qué Hace el Comando

1. Interpreta los inputs y valida el nombre del SDK y el bounded context.
2. Ejecuta `kata-sdk-typescript-scaffold` paso a paso, preguntando al usuario por cualquier input faltante.
3. Genera el esqueleto del proyecto, transporte, modelo de error, primer módulo de dominio y el flujo de release vía changesets.
4. Ejecuta `pnpm validate` y produce el reporte de conformidad mapeando cada cláusula de `lex-sdk-typescript` a su artefacto de verificación.
5. Expone el reporte de conformidad y el checklist de próximos pasos en la descripción del PR.

## Prompt Template

```
Contexto:
- Nombre del SDK: {{nombre-del-sdk}}
- Bounded context: {{bounded-context}}
- Objetivo de distribución: {{target}}
- Ruta del SDK existente (cuando se vaya a llevar a conformidad): {{from}}

Tarea:
Ejecutar `kata-sdk-typescript-scaffold` de punta a punta. Consultar
`lex-sdk-typescript` y `codex-sdk-typescript` para cada decisión. Hacer
preguntas de aclaración antes de escafoldar cuando el bounded context no
tenga OpenAPI en docs/{{bounded-context}}/oas/openapi.yaml o cuando
`--from` apunte a una ruta inexistente. Tras escafoldar, ejecutar la
suite de validación y producir el reporte de conformidad.

Salida:
- Esqueleto del SDK en sdks/{{bounded-context}}/ (monorepo) o raíz del
  repositorio (standalone), con src/, test/, tsconfig, tsup, biome,
  vitest, changesets, workflows de CI.
- Reporte de conformidad cubriendo las 10 cláusulas de `lex-sdk-typescript`.
- Changeset inicial documentando la superficie pública 0.1.0.
```

## Ejemplo de Invocación

**Input:**

```
/cry-new-sdk-typescript @guardia/sdk-scheduled-payments scheduled-payments --target=both
```

**Salida esperada:**

El Kata escafolda `sdks/scheduled-payments/`, genera tipos desde `docs/scheduled-payments/oas/openapi.yaml`, implementa el transporte con `Authorization`, `Idempotency-Key` y `X-Grd-Trace-Id`, entrega el primer módulo de dominio (`scheduled-transfers`), conecta changesets y el workflow de release para npm público y GitHub Packages, ejecuta `pnpm validate` y anexa el reporte de conformidad al PR resultante.

## Restricciones

- Nunca publicar durante el scaffolding (sin `npm publish`); el Cry solo prepara el paquete y lo valida localmente.
- Nunca debilitar el baseline de `tsconfig.json` de `codex-sdk-typescript`.
- Cuando el bounded context no tiene especificación OpenAPI, pausar y exponer el artefacto faltante en lugar de inventar endpoints.

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Atajo único con dos argumentos obligatorios. | Procedimiento de nueve pasos con validación y reporte. |
| **Complejidad** | Baja (un comando). | Alta (scaffold, transporte, modelo de error, pruebas, flujo de release). |
| **¿Configura agente?** | Sí (asume el rol de autor del SDK e invoca el Kata). | Sí (define cada paso). |
| **Ejemplo** | `/cry-new-sdk-typescript @guardia/sdk-x x` | Ejecutar `kata-sdk-typescript-scaffold` con inputs explícitos. |

## Kata y Lexis Asociados

- **kata-sdk-typescript-scaffold** — procedimiento de scaffolding end-to-end.
- **lex-sdk-typescript** — leyes inquebrantables para todo SDK TS/Node Guardia.
- **codex-sdk-typescript** — manual de referencia.

## Referencias

- `kata-sdk-typescript-scaffold`
- `lex-sdk-typescript`
- `codex-sdk-typescript`
- `lex-restful-headers`, `lex-idempotency`, `lex-error-handling` — contrato que el SDK aplica en cada llamada.
- `codex-semantic-version` — reglas de versionado consumidas por el flujo de release.
