# Codex: SDK Guardia en TypeScript/Node.js

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Ingeniería — SDK: arquitectura, herramental, convenciones y flujo de release para toda biblioteca cliente en TypeScript/Node.js que consume la API REST de Guardia

## Visión General

Este Codex es la referencia canónica para el diseño y la implementación de SDKs en TypeScript/Node.js que consumen la API REST de Guardia. La Ley correspondiente es `lex-sdk-typescript`. Los agentes que escriben o revisan un SDK consultan este Codex para tomar decisiones sobre layout, herramental, transporte HTTP, mapeo de errores, telemetría, versionado y publicación.

## Contexto

- **Dominio:** ingeniería de SDK para clientes de la API REST de Guardia.
- **Audiencia:** `warrior-apollo` al entregar un SDK acompañando un contexto de API, `warrior-hephaestus` e `warrior-iris` al consumir, revisores de PR.
- **Actualización:** cuando un patrón nuevo se consolida (por ejemplo, adaptador de transporte, hook de telemetría) o cuando un SDK publicado introduce una convención que pasa a ser compartida.

## Contenido

### Principios

1. **Generado donde sea posible, escrito a mano donde importa.** Los tipos y operaciones de bajo nivel se generan a partir de `docs/{context}/oas/openapi.yaml` (`openapi-typescript` para tipos, `openapi-fetch` o un cliente propio para el runtime). La superficie pública (métodos ergonómicos, mapeo de errores, retry, telemetría) se escribe a mano y es estable.
2. **La superficie pública es contrato.** El mapa `exports` del paquete es el contrato. Todo lo que no esté declarado allí es interno y puede cambiar sin un major bump.
3. **Los errores viajan como valores.** Los métodos públicos retornan `Result<T, GuardiaError>` (o `Promise<Result<...>>`). Lanzar excepciones se reserva para errores del programador (forma inválida del argumento, estado inalcanzable).
4. **La idempotencia y la trazabilidad no son opcionales.** Toda llamada mutadora lleva `Idempotency-Key` y `X-Grd-Trace-Id`, generados por el SDK cuando el llamador no los provee.
5. **Cero dependencias de runtime como default.** Las nuevas dependencias de runtime requieren una entrada en `DEPENDENCIES.md` que justifique peso, licencia, mantenimiento y postura de seguridad.

### Estructura del Proyecto

```
sdk-{context}/
├── package.json
├── tsconfig.json
├── tsup.config.ts            # build (esm + cjs + d.ts)
├── biome.json                # lint + format (o eslint.config.js)
├── vitest.config.ts
├── src/
│   ├── index.ts              # superficie pública, declarada en `exports`
│   ├── client.ts             # clase GuardiaClient
│   ├── config.ts             # GuardiaClientConfig + defaults
│   ├── errors.ts             # GuardiaError + códigos canónicos
│   ├── result.ts             # helpers Result<T, E> (o re-export de @guardia/result)
│   ├── transport/
│   │   ├── http.ts           # wrapper de fetch: auth, retry, trace, idempotencia
│   │   ├── retry.ts          # política de backoff
│   │   └── telemetry.ts      # hooks de ciclo de vida (request, response, error)
│   ├── generated/            # salida de `openapi-typescript` — solo lectura
│   │   └── openapi.ts
│   └── domains/              # un archivo por recurso lógico
│       ├── scheduled-transfers.ts
│       └── refunds.ts
├── test/
│   ├── unit/
│   └── integration/          # grabaciones nock/MSW
├── DEPENDENCIES.md
├── CHANGELOG.md              # generado por changesets
├── README.md
└── .changeset/               # directorio de trabajo del changesets
```

### Herramental

| Aspecto | Elección | Nota |
|---------|----------|------|
| Build | `tsup` (respaldado por esbuild) | Emite ESM + CJS + `.d.ts` desde una sola configuración; tree-shakable. |
| Lint + format | `biome` (preferido) o `eslint` + `prettier` | Biome es preferido para los SDKs nuevos; los setups con eslint existentes pueden permanecer hasta un major. |
| Tipos | `tsc --noEmit` | Type-check separado del emit; el emit es del `tsup`. |
| Pruebas | `vitest` | ESM nativo, rápido, integra con MSW. |
| Mock HTTP | `msw` (preferido) o `nock` | MSW para pruebas basadas en fetch; nock para pruebas de transporte de bajo nivel. |
| Versionado | `changesets` | Intención por PR; el CI publica al merge a `main`. |
| Verificación del formato publicado | `arethetypeswrong` + `publint` | Ejecutar pre-publish; el CI bloquea merges. |

### Baseline de `tsconfig.json`

```jsonc
{
  "extends": "@guardia/tsconfig-sdk",   // cuando el perfil compartido exista
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "lib": ["ES2022"]
  },
  "include": ["src/**/*"]
}
```

### Convenciones de `package.json`

```jsonc
{
  "name": "@guardia/sdk-{context}",
  "version": "0.1.0",
  "description": "SDK Guardia para el bounded context {context}.",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
    // una entrada por subruta pública; sin barriles implícitos.
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "files": ["dist", "README.md", "DEPENDENCIES.md"],
  "engines": { "node": ">=20" },
  "scripts": {
    "build": "tsup",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "biome check src test",
    "typecheck": "tsc --noEmit",
    "validate": "pnpm typecheck && pnpm lint && pnpm test && publint && attw --pack .",
    "release": "changeset publish"
  },
  "publishConfig": { "access": "public", "provenance": true },
  "sideEffects": false
}
```

`provenance: true` habilita la atestación de procedencia firmada de npm cuando se publica desde GitHub Actions; obligatorio para paquetes `@guardia/*`.

### Patrón de Transporte HTTP

La capa de transporte es un wrapper delgado sobre `fetch`:

1. **Auth.** Lee `config.token` (string o `() => Promise<string>` para refresh de token) y define `Authorization: Bearer <token>`. Los errores de obtención de token se traducen a `GuardiaError` con código `ERR401_UNAUTHORIZED`/`AUTH_TOKEN_UNAVAILABLE`.
2. **Idempotencia.** Los verbos mutadores (`POST`, `PUT`, `PATCH`, `DELETE`) reciben `Idempotency-Key` desde el llamador o, en su ausencia, generado por el SDK como UUID v7. La clave se registra vía telemetría, nunca en `console`.
3. **Propagación de trace.** El transporte lee el trace id actual del tracer configurado (default no-op) y define `X-Grd-Trace-Id`. Cuando la respuesta incluye trace id, se expone en el resultado para correlación de logs.
4. **Política de retry.** Backoff exponencial con jitter en `429`, `502`, `503`, `504` y errores de red a nivel de transporte. Defaults: 3 reintentos, base 100 ms, tope 2 s. Configurable por llamada vía `RequestOptions.retry`.
5. **Timeout.** Timeout por llamada (default 30 s) usando `AbortController`. Aparece como `GuardiaError` con código `ERR408_TIMEOUT`.
6. **Decodificación de error.** Las respuestas no-2xx se decodifican contra el envelope canónico (`{ errors: [{ code, reason, message }] }`, según `lex-error-handling`). Los formatos incompatibles caen a un `GuardiaError` sintético con código `ERR502_BAD_GATEWAY` y el payload bruto preservado en `cause`.
7. **Decodificación de respuesta.** Las respuestas 2xx pasan por un decoder tipado (Zod, Valibot o un decoder generado desde el OpenAPI). Las fallas de decodificación se traducen a `GuardiaError` con código `ERR502_BAD_GATEWAY`/`RESPONSE_DECODE_ERROR`.

### Modelo de Error

```typescript
// errors.ts
export type GuardiaErrorCode =
  | "ERR400_INVALID_PARAMETER"
  | "ERR401_UNAUTHORIZED"
  | "ERR403_FORBIDDEN"
  | "ERR404_NOT_FOUND"
  | "ERR408_TIMEOUT"
  | "ERR409_CONFLICT"
  | "ERR429_TOO_MANY_REQUESTS"
  | "ERR500_INTERNAL"
  | "ERR502_BAD_GATEWAY"
  | "ERR503_SERVICE_UNAVAILABLE";

export class GuardiaError extends Error {
  readonly code: GuardiaErrorCode;
  readonly reason: string;
  readonly traceId?: string;
  readonly cause?: unknown;
  // ...
}
```

El catálogo completo de códigos de error refleja `lex-error-handling` y `codex-known-errors`. Los códigos específicos del SDK (transporte, decoder) se prefijan con `ERR502_` o `ERR500_` y se documentan en el README del SDK.

### Hooks de Telemetría

El SDK expone hooks de ciclo de vida que los consumidores conectan a OpenTelemetry o a cualquier logger:

```typescript
type TelemetryHook = {
  onRequest?: (event: RequestEvent) => void;
  onResponse?: (event: ResponseEvent) => void;
  onError?: (event: ErrorEvent) => void;
  onRetry?: (event: RetryEvent) => void;
};
```

La implementación default es no-op. Internamente, el SDK no llama a `console.*`.

### Código Generado a Partir del OpenAPI

Cuando `docs/{context}/oas/openapi.yaml` existe, se ejecuta `openapi-typescript` para producir `src/generated/openapi.ts`:

```
pnpm dlx openapi-typescript docs/{context}/oas/openapi.yaml -o src/generated/openapi.ts
```

`src/generated/` es salida de solo lectura (gitignored o commitada según la política del SDK — ambas son aceptables; commitar simplifica la instalación del consumidor, gitignorar mantiene el diff liviano). Los archivos escritos a mano en `src/domains/*` importan tipos de `generated/` y exponen métodos ergonómicos.

### Política de Versionado

- **Major (X.0.0):** remoción de símbolo público, cambio en firma de función, cambio en código de error exportado, cambio en comportamiento observable en runtime de un contrato documentado.
- **Minor (0.X.0):** adición de símbolo público, adición de parámetro opcional, adición de código de error sin ruptura.
- **Patch (0.0.X):** corrección interna sin cambio en la superficie pública.
- **Pre-1.0.0:** la superficie pública es inestable; los minor bumps pueden traer rupturas, pero `BREAKING CHANGES.md` DEBE listar cada ruptura.

### Flujo de Release

1. El autor del PR agrega un `.changeset/*.md` describiendo la intención (major/minor/patch) según la convención de changesets.
2. El CI en `main` consume los changesets pendientes, calcula la próxima versión, regenera `CHANGELOG.md` y abre un PR `Version Packages`.
3. El merge del PR `Version Packages` dispara `changeset publish`, que:
   - Construye (`pnpm build`).
   - Valida (`pnpm validate` — typecheck, lint, test, publint, attw).
   - Publica en npm con `--provenance` (para `@guardia/*`).
   - Crea un GitHub Release con el extracto del changelog.

### Objetivos de Distribución

Ambos objetivos se soportan sin código condicional:

- **npm público (`@guardia/*`).** `publishConfig.access: "public"`, `provenance: true`, registry `https://registry.npmjs.org`.
- **Interno.** Mismo paquete, registrado en el registry interno de GitHub Packages; `publishConfig.registry: "https://npm.pkg.github.com"`. Los consumidores usan un `.npmrc` a nivel de proyecto. El artefacto de build es idéntico.

### Patrones y Convenciones

| Aspecto | Patrón | Ejemplo |
|---------|--------|---------|
| Clase pública | `Guardia{Context}Client` o `GuardiaClient` para SDKs de contexto único | `GuardiaScheduledPaymentsClient` |
| Nomenclatura de método | verbo + recurso | `createScheduledTransfer`, `listRefunds` |
| Paginación | basada en cursor según `codex-restful-pagination` | `client.listRefunds({ pageSize: 50 })` retorna `{ data, pageToken }` |
| Casing de archivo | kebab-case | `scheduled-transfers.ts` |
| Tipos públicos | exportados desde `index.ts` solo cuando son estables | `ScheduledTransferInput`, `ScheduledTransfer` |

### Decisiones Vigentes

| ADR | Decisión | Estado |
|-----|----------|--------|
| ADR-{NN} | tsup como herramienta de build para los SDKs Guardia | Activa |
| ADR-{NN} | changesets como herramienta de versionado | Activa |
| ADR-{NN} | Biome como herramienta de lint/format para los SDKs nuevos | Activa |

(Reemplazar los placeholders por números concretos de ADR a medida que se escriban.)

### Restricciones Técnicas

- Node.js mínimo: `>=20` (LTS al momento de la autoría).
- La forma `Result<T, E>` refleja la semántica de `lex-python-result-type` cuando aplica; los SDKs PUEDEN re-exportar de `@guardia/result` cuando ese paquete exista.
- Ninguna API exclusiva de `node:` en rutas de código consumidas por SDKs `@guardia/*` orientados a edge runtimes; cuando se requiera una variante para edge, exponer una subruta `exports` separada (`./edge`) condicionada por `worker`.

## Diagrama de Referencia

```
┌──────────────────────────────────────────────────────────────┐
│                       Aplicación Consumidora                 │
└──────────────────────────────┬───────────────────────────────┘
                               │ import { GuardiaClient }
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  src/index.ts (superficie pública — declarada en `exports`)  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ src/domains/{resource}.ts   (métodos ergonómicos)      │  │
│  └─────────────────────────┬──────────────────────────────┘  │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ src/transport/http.ts                                  │  │
│  │   auth · retry · idempotencia · trace · timeout · decode│ │
│  └─────────────────────────┬──────────────────────────────┘  │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ src/generated/openapi.ts  (tipos de openapi-typescript)│  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
                       API REST de Guardia
```

## Glosario

| Término | Definición |
|---------|------------|
| Superficie pública | Conjunto de símbolos alcanzables desde el mapa `exports` del paquete; contrato de estabilidad del SDK. |
| Código generado | Salida de `openapi-typescript` (y similares) en `src/generated/`; tratado como solo lectura. |
| Transporte | Wrapper de `fetch` que centraliza auth, idempotencia, retry, propagación de trace y decodificación. |
| Decoder | Función que convierte un payload desconocido en valor tipado (schema Zod, decoder generado, escrito a mano). |
| Hook de telemetría | Callback provisto por el consumidor que el SDK invoca en las fronteras de request/response/error/retry. |

## Referencias

- `lex-sdk-typescript` — Ley correspondiente.
- `kata-sdk-typescript-scaffold` — procedimiento para escafoldar un SDK nuevo.
- `cry-new-sdk-typescript` — atajo que invoca el Kata.
- `lex-restful-headers`, `codex-restful-headers` — headers canónicos de Guardia.
- `lex-idempotency`, `codex-idempotency` — política de idempotencia.
- `lex-error-handling`, `codex-known-errors` — envelope y catálogo de códigos de error.
- `codex-semantic-version` — reglas de versionado.
- `lex-observability-required` — expectativas de telemetría.
- `codex-oas-structure`, `lex-feature-design-docs` — especificación OpenAPI de origen.
