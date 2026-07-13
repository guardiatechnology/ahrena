# Kata: Escafoldar un SDK Guardia en TypeScript/Node.js

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — SDK: procedimiento end-to-end para escafoldar (o llevar a conformidad) un SDK en TypeScript/Node.js que consume la API REST de Guardia, según `lex-sdk-typescript` y `codex-sdk-typescript`

## Objetivo

Este Kata produce un esqueleto de SDK en TypeScript/Node.js que, en el primer día, está en conformidad con `lex-sdk-typescript`: tipos estrictos, `exports` declarado, transporte con auth + idempotencia + trace, mapeo de envelope de error, hooks de telemetría, pruebas y flujo de release vía changesets. El mismo procedimiento aplica para llevar un SDK existente a conformidad (los archivos existentes se comparan contra el esqueleto objetivo).

## Cuándo Usar

- Cuando un bounded context nuevo expone una API REST estable y se requiere un SDK público.
- Cuando un equipo interno necesita un cliente tipado contra un contexto de API existente de Guardia.
- Cuando se invoca `cry-new-sdk-typescript`.
- Cuando un SDK heredado falla en el Gate 2 y debe llevarse a conformidad con la Ley.

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Nombre del SDK | Sí | Nombre del paquete, p. ej. `@guardia/sdk-scheduled-payments` o `sdk-internal-billing`. |
| Bounded context | Sí | Bounded context de Guardia que atiende el SDK, p. ej. `scheduled-payments`. Se usa para localizar `docs/{context}/oas/openapi.yaml`. |
| Objetivo de distribución | Sí | `npm-public` (`@guardia/*`), `npm-internal` (GitHub Packages) o `both`. |
| Fuente OpenAPI | No | Ruta a `docs/{context}/oas/openapi.yaml`. Cuando esté ausente, el SDK se entrega sin tipos generados y el catálogo se escribe a mano. |
| Objetivo del repositorio | No | `monorepo` (default) o `standalone`. Afecta CI y la configuración del changesets. |
| Ruta del SDK existente | No | En el modo "llevar a conformidad", la ruta a la raíz del SDK existente. |

## Workflow

```
Progreso:
- [ ] 1. Aclarar inputs y resolver objetivo de distribución
- [ ] 2. Inicializar esqueleto del paquete
- [ ] 3. Configurar herramental (tsconfig, tsup, biome, vitest)
- [ ] 4. Generar tipos desde el OpenAPI (cuando esté disponible)
- [ ] 5. Implementar transporte (auth, retry, idempotencia, trace, telemetría)
- [ ] 6. Implementar modelo de error y helper Result
- [ ] 7. Implementar primer módulo de dominio + pruebas
- [ ] 8. Conectar changesets y flujo de release
- [ ] 9. Ejecutar suite de validación y producir reporte de conformidad
```

### Paso 1: Aclarar Inputs y Resolver Objetivo de Distribución

1. Confirmar que el nombre del SDK sigue la convención `@guardia/sdk-{context}` (público) o `@guardia-internal/sdk-{context}` (interno).
2. Confirmar que el bounded context existe bajo `docs/{context}/` y localizar `oas/openapi.yaml`. Cuando esté ausente, preguntar al usuario si proceder sin tipos generados o esperar a que se publique el OpenAPI.
3. Resolver la distribución:
   - `npm-public` → `publishConfig.access: "public"`, `provenance: true`, registry npmjs.
   - `npm-internal` → `publishConfig.registry: "https://npm.pkg.github.com"`.
   - `both` → matriz de publicación en CI; mismo artefacto.
4. Confirmar el objetivo del repositorio (monorepo vs standalone) — afecta la raíz del changesets y la ubicación del workflow de CI.

### Paso 2: Inicializar Esqueleto del Paquete

1. Crear el árbol de directorios según `codex-sdk-typescript` (`src/`, `test/`, `.changeset/`, archivos de configuración en el tope).
2. Escribir `package.json` con:
   - `name`, `version: "0.1.0"`, `type: "module"`, `engines.node: ">=20"`.
   - Mapa `exports` con al menos `"."` resolviendo a `dist/index.{js,cjs,d.ts}`.
   - `files: ["dist", "README.md", "DEPENDENCIES.md"]`.
   - `sideEffects: false`.
   - `publishConfig` según el objetivo de distribución.
3. Crear `DEPENDENCIES.md` listando cada dependencia de runtime con: nombre, propósito, licencia, fecha de la última auditoría.
4. Crear `README.md` con instalación, quickstart y enlace a `codex-sdk-typescript`.

### Paso 3: Configurar Herramental

1. **`tsconfig.json`** — extender `@guardia/tsconfig-sdk` cuando exista; en caso contrario, inline el baseline de `codex-sdk-typescript`. Confirmar `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, target `ES2022`, module `ESNext`.
2. **`tsup.config.ts`** — entry `src/index.ts`, formatos `["esm", "cjs"]`, `dts: true`, `clean: true`, `treeshake: true`, `splitting: false`. Agregar entries por cada subruta declarada en `exports`.
3. **`biome.json`** (o `eslint.config.js`) — habilitar `noExplicitAny` como error en archivos publicables, prohibir `console.*` en `src/`, prohibir imports relativos que crucen `src/generated/` desde fuera de la capa de transporte.
4. **`vitest.config.ts`** — umbrales de cobertura en 80/80/80/80; ambiente `node` para pruebas de transporte, `happy-dom` solo cuando se necesiten polyfills del DOM.

### Paso 4: Generar Tipos desde el OpenAPI

1. Cuando `docs/{context}/oas/openapi.yaml` exista:
   ```
   pnpm dlx openapi-typescript docs/{context}/oas/openapi.yaml -o src/generated/openapi.ts
   ```
2. Agregar un script npm `"types:generate": "openapi-typescript ..."` para mantener el comando descubrible.
3. Decidir entre commit o gitignore para `src/generated/`. Default: commit, para simplificar la instalación del consumidor. Documentar la elección en `README.md`.
4. Cuando el OpenAPI esté ausente, escribir a mano tipos mínimos en `src/types/` y registrar en `README.md` que el SDK será regenerado cuando el spec aterrice.

### Paso 5: Implementar Transporte

1. Crear `src/transport/http.ts` con la clase `HttpTransport`:
   - Lee `config.baseUrl`, `config.token` (string o resolver asíncrono), `config.fetch` (default `globalThis.fetch`).
   - Arma `Authorization: Bearer <token>`.
   - Para `POST`/`PUT`/`PATCH`/`DELETE`, define `Idempotency-Key` desde el llamador o genera UUID v7.
   - Lee el trace id de `config.tracer` (default no-op) y define `X-Grd-Trace-Id`.
   - Envuelve `fetch` con `AbortController` para timeout.
2. Crear `src/transport/retry.ts`:
   - Backoff exponencial con jitter en `429`, `502`, `503`, `504`, errores de red.
   - Defaults: 3 reintentos, base 100 ms, tope 2 s.
   - Honra `Retry-After` cuando esté presente.
3. Crear `src/transport/telemetry.ts`:
   - Interface `TelemetryHook` (`onRequest`, `onResponse`, `onError`, `onRetry`).
   - Default no-op.

### Paso 6: Implementar Modelo de Error y Helper Result

1. Crear `src/errors.ts` con la clase `GuardiaError` y la unión canónica `GuardiaErrorCode` (espejando `codex-known-errors`).
2. Crear `src/result.ts` con `Result<T, E>` = `Ok<T> | Err<E>` más helpers `ok`, `err`, `isOk`, `isErr`, `map`, `mapErr`.
3. El transporte traduce toda respuesta no-2xx y toda falla a nivel de transporte a `Err(GuardiaError)`. Los métodos públicos retornan `Promise<Result<T, GuardiaError>>`.
4. Exponer los códigos de error por la subruta `./errors` en `exports` para que los consumidores puedan hacer pattern-matching.

### Paso 7: Implementar Primer Módulo de Dominio + Pruebas

1. Elegir un recurso del OpenAPI (p. ej. `scheduled-transfers`) e implementar `src/domains/scheduled-transfers.ts` exponiendo los métodos CRUD canónicos (`create`, `list`, `get`, `update`, `delete`) según `codex-restful-payload`.
2. Conectar los métodos al `HttpTransport`; mapear formas de request/response a través de decoders.
3. Escribir **pruebas unitarias** para cada método usando MSW para aserir:
   - URL, método, body y headers de la solicitud (`Authorization`, `Idempotency-Key` en verbos mutadores, `X-Grd-Trace-Id`).
   - Decodificación de la respuesta exitosa.
   - Mapeo del envelope de error para `400`, `401`, `404`, `409`, `429`, `500`, `503`.
   - Retry en `503` con backoff (usar fake timers).
4. Escribir **pruebas de integración** que ejerciten el transporte contra un servidor grabado (servidor HTTP de MSW) y aseren la superficie pública end-to-end.

### Paso 8: Conectar Changesets y Flujo de Release

1. Ejecutar `pnpm dlx @changesets/cli init`.
2. Configurar `.changeset/config.json` con `access: "public"` (para `@guardia/*`) o `restricted` (interno), `baseBranch: "main"`, `commit: false`.
3. Agregar el GitHub Action de changesets en `.github/workflows/release.yml`:
   - En push a `main`, ejecutar `pnpm validate`, luego `changeset version` (abre un PR) o `changeset publish` (cuando el PR de versión se mergea).
   - En paquetes `@guardia/*`, habilitar `--provenance` y exigir el permiso `id-token: write`.
4. Agregar un `.github/workflows/ci.yml` que corre en cada PR: `pnpm install`, `pnpm validate`, upload de cobertura.

### Paso 9: Validación y Reporte de Conformidad

1. Ejecutar `pnpm validate` localmente:
   - `tsc --noEmit` sin errores.
   - `biome check` sin errores.
   - `vitest run` con cobertura ≥ 80%.
   - `publint` sin errores.
   - `attw --pack .` sin errores (sin CJS falso, sin ESM falso).
2. Producir el reporte de conformidad mapeando cada cláusula de `lex-sdk-typescript` a su artefacto de verificación:

| Cláusula | Verificación |
|----------|--------------|
| 1. TS estricto | Salida de `tsc --noEmit` |
| 2. Mapa `exports` | Salida de `publint`/`attw` |
| 3. Semver | Directorio `.changeset/` + workflow de CI |
| 4. Headers canónicos | Aserciones en pruebas de integración |
| 5. Envelope de error | Pruebas unitarias para `400`/`401`/`409`/`500` |
| 6. `.d.ts` pública | `attw --pack .` |
| 7. Dependencias justificadas | `DEPENDENCIES.md` |
| 8. Pruebas + cobertura | Reporte de cobertura de Vitest |
| 9. Hooks de telemetría | `src/transport/telemetry.ts` + pruebas |
| 10. `engines.node` | `package.json` |

3. Entregar el reporte al revisor del PR y a `warrior-athena` para el Gate 2.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Esqueleto del SDK | Proyecto TypeScript | `sdk-{context}/` (monorepo) o raíz del repositorio (standalone) |
| Reporte de conformidad | Markdown | Cuerpo del PR o `docs/sdks/{context}/conformance.md` |
| Changeset inicial | Markdown | `.changeset/initial.md` describiendo la superficie 0.1.0 |

## Ejemplo de Ejecución

### Input de Ejemplo

```
Nombre del SDK: @guardia/sdk-scheduled-payments
Bounded context: scheduled-payments
Distribución: npm-public
OpenAPI: docs/scheduled-payments/oas/openapi.yaml
Repositorio: monorepo
```

### Output de Ejemplo

```
sdks/scheduled-payments/
├── package.json          (@guardia/sdk-scheduled-payments@0.1.0, mapa exports, engines, provenance)
├── tsconfig.json         (strict + noUncheckedIndexedAccess)
├── tsup.config.ts        (esm + cjs + dts)
├── biome.json
├── vitest.config.ts
├── src/
│   ├── index.ts
│   ├── client.ts
│   ├── config.ts
│   ├── errors.ts
│   ├── result.ts
│   ├── transport/{http,retry,telemetry}.ts
│   ├── generated/openapi.ts        (desde openapi-typescript)
│   └── domains/scheduled-transfers.ts
├── test/{unit,integration}/...
├── DEPENDENCIES.md
├── README.md
└── .changeset/initial.md
```

Validación: `pnpm validate` pasa, cobertura 87% de líneas, `publint` y `attw` sin errores, reporte de conformidad anexado al PR.

## Restricciones

- Nunca debilitar el `tsconfig.json` respecto al baseline (sin opt-out de `strict`, `noUncheckedIndexedAccess` ni `exactOptionalPropertyTypes`).
- Nunca publicar un release `0.x.y` que introduzca un cambio en la superficie pública sin una entrada en `BREAKING CHANGES.md`.
- Nunca agregar una dependencia de runtime sin una entrada en `DEPENDENCIES.md` que la justifique.
- Nunca escribir en `console.*` desde `src/`; toda señal se enruta por el hook de telemetría.
- Cuando `docs/{context}/oas/openapi.yaml` esté ausente, no inventar endpoints — pausar y exponer el artefacto faltante o escribir a mano un stub mínimo en `src/types/` con aprobación explícita del usuario.
