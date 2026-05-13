# Lexis: SDK Guardia en TypeScript/Node.js

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ingeniería — SDK: toda biblioteca cliente en TypeScript/Node.js que consume la API REST de Guardia, sin importar la distribución (`@guardia/*` en npm o interna)

## Ley

> **Todo SDK en TypeScript/Node.js que consume la API REST de Guardia DEBE: (1) compilar bajo `strict: true` con `noUncheckedIndexedAccess: true` y tener como objetivo ES2022 o superior; (2) declarar cada símbolo público en el campo `exports` del `package.json` — re-exports implícitos vía barril fuera de `exports` están PROHIBIDOS; (3) versionar según Semantic Versioning 2.0.0, donde cualquier cambio visible en la superficie pública (tipos, firmas de función, códigos de error exportados, comportamiento en runtime de contratos documentados) constituye un major o minor bump según `codex-semantic-version`; (4) propagar los headers canónicos de Guardia en toda llamada HTTP — `Authorization: Bearer <token>`, `Idempotency-Key` para verbos mutadores y `X-Grd-Trace-Id` — según `lex-restful-headers` y `lex-idempotency`; (5) traducir las respuestas de error al envelope estandarizado definido en `lex-error-handling`, preservando `code`, `reason` y `message`, sin filtrar formatos del transporte; (6) entregar declaraciones de tipo (`.d.ts`) generadas a partir del código fuente — `any` NO PUEDE aparecer en la superficie pública, y `unknown` solo se admite en fronteras de parseo (decodificación de respuesta) con un camino de estrechamiento tipado; (7) declarar cada dependencia de runtime en `dependencies` con una entrada justificada en el `DEPENDENCIES.md` del SDK — añadir una dependencia de runtime sin justificación está PROHIBIDO; (8) proveer pruebas unitarias para cada función pública y pruebas de integración contra un transporte HTTP grabado (nock/MSW o equivalente) con ≥ 80% de cobertura de líneas en CI; (9) exponer hooks de telemetría (ciclo de vida de la solicitud, error, retry) que los consumidores PUEDEN conectar a OpenTelemetry — las llamadas internas a `console.*` están PROHIBIDAS; (10) declarar `engines.node` con la versión LTS mínima soportada de Node.js (actualmente `>=20`) y NO PUEDE usar APIs introducidas después de ese piso sin protección en runtime.**

## Alcance

- **Se aplica a:** todo SDK en TypeScript o JavaScript autorizado por Guardia cuyo propósito sea consumir la API REST de Guardia, sin importar el canal de distribución (`@guardia/*` en npm, GitHub Packages privado, paquete interno de monorepo, fork vendorizado).
- **Fuera de alcance:** el código de aplicación que incrusta un SDK (consumidores), el código generado por `openapi-typescript`/`openapi-fetch` a partir de `docs/{context}/oas/openapi.yaml` (el SDK envuelve y reexpone el código generado a través de su propia superficie pública, que sí está en alcance).
- **Agentes vinculados:** `warrior-apollo` (al autorizar un SDK en nombre de un contexto de API), `warrior-hephaestus` (al integrar un SDK en un frontend), `warrior-iris` (consumidores mobile de SDKs compatibles con Node), `warrior-athena` (Gate 2 del flujo Issue-Driven).
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de la Violación

1. **Bloqueo automático:** el Gate 2 (`kata-quality-gate`) rechaza el PR cuando cualquier cláusula de la Ley sea violada y no remediada.
2. **Ruptura de la superficie pública:** cualquier desviación de las cláusulas (2), (3) o (6) se trata como un incidente de contrato publicado y dispara un ciclo coordinado de deprecación según `codex-semantic-version`.
3. **Escalamiento de seguridad:** filtraciones del header de autenticación, ausencia de `Idempotency-Key` en verbos mutadores o retornos `any` no tipados en la superficie pública se escalan al platform owner del contexto de API consumido.
4. **Remediación:** el SDK DEBE ajustarse a la conformidad antes del próximo release; los releases intermedios con violaciones conocidas llevan una entrada documentada en `KNOWN_ISSUES.md` y la versión objetivo para la corrección.

## Ejemplos

### Correcto

```typescript
// src/client.ts — API pública
import type { paths } from "./generated/openapi";

export class GuardiaClient {
  constructor(private readonly config: GuardiaClientConfig) {}

  async createScheduledTransfer(
    input: CreateScheduledTransferInput,
    options: RequestOptions = {},
  ): Promise<Result<ScheduledTransfer, GuardiaError>> {
    return this.transport.request({
      method: "POST",
      path: "/v1/scheduled-transfers",
      body: input,
      headers: {
        "Idempotency-Key": options.idempotencyKey ?? randomUuidV7(),
        "X-Grd-Trace-Id": this.tracer.currentTraceId(),
      },
      decoder: ScheduledTransferDecoder,
    });
  }
}
```

```json
// package.json — exports explícitos, engines, sin barril implícito
{
  "name": "@guardia/sdk-scheduled-payments",
  "version": "1.4.0",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    },
    "./errors": {
      "types": "./dist/errors.d.ts",
      "import": "./dist/errors.js",
      "require": "./dist/errors.cjs"
    }
  },
  "engines": { "node": ">=20" },
  "files": ["dist", "README.md", "DEPENDENCIES.md"]
}
```

### Incorrecto

```typescript
// ❌ Superficie pública sin tipos
export async function createTransfer(input: any): Promise<any> {
  const res = await fetch("/v1/transfers", { method: "POST", body: JSON.stringify(input) });
  return res.json(); // sin Idempotency-Key, sin Authorization, sin envelope de error, retorna any
}
```

```json
// ❌ Barril implícito, sin engines, sin mapa exports
{
  "name": "guardia-sdk",
  "main": "src/index.ts",
  "dependencies": { "axios": "*", "lodash": "*", "moment": "*" }
}
```

## Validación Automatizada

- **Herramientas:**
  - **TS estricto:** `tsc --noEmit` con el `tsconfig.json` del SDK extendiendo `@guardia/tsconfig-sdk` (que provee `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`).
  - **Drift de la superficie pública:** `api-extractor` (o `arethetypeswrong`/`publint`) verificando el mapa `exports`, la consistencia del dual-emit y la cobertura de `.d.ts`.
  - **Cumplimiento semver:** `changesets` con `--commit-mode=intent`; el CI bloquea merges que cambien la versión sin el changeset correspondiente.
  - **Contrato HTTP:** suite de integración que graba solicitudes contra `nock` o MSW con aserciones sobre `Authorization`, `Idempotency-Key`, `X-Grd-Trace-Id`.
  - **Auditoría de dependencias:** `npm audit --omit=dev` + `depcheck`; la presencia de `DEPENDENCIES.md` es exigida por el Gate 2.
  - **Linter:** `eslint-plugin-no-restricted-imports` bloqueando `console.*` en `src/`; `@typescript-eslint/no-explicit-any` en `error` para archivos publicables.
- **Momento:** pre-commit (lint, tipos), CI en cada PR (suite completa, cobertura, publint), pre-publish (validación con `npm publish --dry-run`), Gate 2 del flujo Issue-Driven.
- **Métrica:** 0 PRs con `any` en la superficie pública; 100% de los endpoints mutadores con aserción de `Idempotency-Key` en pruebas de integración; 100% de los releases con changeset correspondiente; cobertura de líneas no decreciente en `main`.
