# Codex: SDK Guardia em TypeScript/Node.js

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Engenharia — SDK: arquitetura, ferramental, convenções e fluxo de release para toda biblioteca cliente em TypeScript/Node.js que consome a API REST da Guardia

## Visão Geral

Este Codex é a referência canônica para o desenho e a implementação de SDKs em TypeScript/Node.js que consomem a API REST da Guardia. A Lei correspondente é `lex-sdk-typescript`. Agentes que escrevem ou revisam um SDK consultam este Codex para decisões sobre layout, ferramental, transporte HTTP, mapeamento de erros, telemetria, versionamento e publicação.

## Contexto

- **Domínio:** engenharia de SDK para clientes da API REST da Guardia.
- **Público-alvo:** `warrior-apollo` ao entregar um SDK acompanhando um contexto de API, `warrior-hephaestus` e `warrior-iris` ao consumir, revisores de PR.
- **Atualização:** quando um novo padrão se consolida (por exemplo, adaptador de transporte, hook de telemetria) ou quando um SDK publicado introduz convenção que passa a ser compartilhada.

## Conteúdo

### Princípios

1. **Gerado onde for possível, escrito à mão onde importa.** Tipos e operações de baixo nível são gerados a partir de `docs/{context}/oas/openapi.yaml` (`openapi-typescript` para tipos, `openapi-fetch` ou cliente próprio para o runtime). A superfície pública (métodos ergonômicos, mapeamento de erro, retry, telemetria) é escrita à mão e estável.
2. **Superfície pública é contrato.** O mapa `exports` do pacote é o contrato. Tudo que não estiver declarado ali é interno e pode mudar sem major bump.
3. **Erros trafegam como valores.** Métodos públicos retornam `Result<T, GuardiaError>` (ou `Promise<Result<...>>`). Lançar exceção é reservado a erros de programador (forma inválida de argumento, estado inalcançável).
4. **Idempotência e rastreabilidade não são opcionais.** Toda chamada mutadora carrega `Idempotency-Key` e `X-Grd-Trace-Id`, gerados pelo SDK quando não fornecidos pelo chamador.
5. **Zero dependência de runtime como padrão.** Novas dependências de runtime exigem entrada em `DEPENDENCIES.md` justificando peso, licença, manutenção e postura de segurança.

### Estrutura do Projeto

```
sdk-{context}/
├── package.json
├── tsconfig.json
├── tsup.config.ts            # build (esm + cjs + d.ts)
├── biome.json                # lint + format (ou eslint.config.js)
├── vitest.config.ts
├── src/
│   ├── index.ts              # superfície pública, declarada em `exports`
│   ├── client.ts             # classe GuardiaClient
│   ├── config.ts             # GuardiaClientConfig + defaults
│   ├── errors.ts             # GuardiaError + códigos canônicos
│   ├── result.ts             # helpers Result<T, E> (ou re-export de @guardia/result)
│   ├── transport/
│   │   ├── http.ts           # wrapper de fetch: auth, retry, trace, idempotência
│   │   ├── retry.ts          # política de backoff
│   │   └── telemetry.ts      # hooks de ciclo de vida (request, response, error)
│   ├── generated/            # saída de `openapi-typescript` — somente leitura
│   │   └── openapi.ts
│   └── domains/              # um arquivo por recurso lógico
│       ├── scheduled-transfers.ts
│       └── refunds.ts
├── test/
│   ├── unit/
│   └── integration/          # gravações nock/MSW
├── DEPENDENCIES.md
├── CHANGELOG.md              # gerado por changesets
├── README.md
└── .changeset/               # diretório de trabalho do changesets
```

### Ferramental

| Aspecto | Escolha | Observação |
|---------|---------|-----------|
| Build | `tsup` (apoiado por esbuild) | Emite ESM + CJS + `.d.ts` a partir de uma única configuração; tree-shakable. |
| Lint + format | `biome` (preferido) ou `eslint` + `prettier` | Biome é preferido para novos SDKs; setups com eslint existentes podem permanecer até um major. |
| Tipos | `tsc --noEmit` | Type-check separado do emit; o emit é do `tsup`. |
| Testes | `vitest` | ESM nativo, rápido, integra com MSW. |
| Mock de HTTP | `msw` (preferido) ou `nock` | MSW para testes baseados em fetch; nock para testes de transporte de baixo nível. |
| Versionamento | `changesets` | Intenção por PR; CI publica no merge para `main`. |
| Verificação do formato publicado | `arethetypeswrong` + `publint` | Executar pre-publish; CI bloqueia merges. |

### Baseline de `tsconfig.json`

```jsonc
{
  "extends": "@guardia/tsconfig-sdk",   // quando o perfil compartilhado existir
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

### Convenções de `package.json`

```jsonc
{
  "name": "@guardia/sdk-{context}",
  "version": "0.1.0",
  "description": "SDK Guardia para o bounded context {context}.",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
    // uma entrada por subcaminho público; sem barris implícitos.
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

`provenance: true` habilita a atestação de proveniência assinada pelo npm quando publicado a partir do GitHub Actions; obrigatório para pacotes `@guardia/*`.

### Padrão de Transporte HTTP

A camada de transporte é um wrapper enxuto sobre `fetch`:

1. **Auth.** Lê `config.token` (string ou `() => Promise<string>` para refresh de token) e define `Authorization: Bearer <token>`. Erros de obtenção de token traduzem-se para `GuardiaError` com código `ERR401_UNAUTHORIZED`/`AUTH_TOKEN_UNAVAILABLE`.
2. **Idempotência.** Verbos mutadores (`POST`, `PUT`, `PATCH`, `DELETE`) recebem `Idempotency-Key` do chamador ou, na ausência, gerada pelo SDK como UUID v7. A chave é registrada via telemetria, nunca em `console`.
3. **Propagação de trace.** O transporte lê o trace id atual do tracer configurado (default no-op) e define `X-Grd-Trace-Id`. Quando a resposta inclui trace id, ele é exposto no resultado para correlação de logs.
4. **Política de retry.** Backoff exponencial com jitter em `429`, `502`, `503`, `504` e erros de rede em nível de transporte. Default: 3 tentativas, base 100 ms, teto 2 s. Configurável por chamada via `RequestOptions.retry`.
5. **Timeout.** Timeout por chamada (default 30 s) usando `AbortController`. Surge como `GuardiaError` com código `ERR408_TIMEOUT`.
6. **Decodificação de erro.** Respostas não-2xx são decodificadas contra o envelope canônico (`{ errors: [{ code, reason, message }] }`, conforme `lex-error-handling`). Formatos incompatíveis recaem para um `GuardiaError` sintético com código `ERR502_BAD_GATEWAY` e payload bruto preservado em `cause`.
7. **Decodificação de resposta.** Respostas 2xx passam por decoder tipado (Zod, Valibot ou decoder gerado do OpenAPI). Falhas de decodificação traduzem-se para `GuardiaError` com código `ERR502_BAD_GATEWAY`/`RESPONSE_DECODE_ERROR`.

### Modelo de Erro

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

O catálogo completo de códigos de erro espelha `lex-error-handling` e `codex-known-errors`. Códigos específicos do SDK (transporte, decoder) são prefixados por `ERR502_` ou `ERR500_` e documentados no README do SDK.

### Hooks de Telemetria

O SDK expõe hooks de ciclo de vida que consumidores conectam a OpenTelemetry ou a qualquer logger:

```typescript
type TelemetryHook = {
  onRequest?: (event: RequestEvent) => void;
  onResponse?: (event: ResponseEvent) => void;
  onError?: (event: ErrorEvent) => void;
  onRetry?: (event: RetryEvent) => void;
};
```

A implementação default é no-op. Internamente, o SDK não chama `console.*`.

### Código Gerado a Partir do OpenAPI

Quando `docs/{context}/oas/openapi.yaml` existe, execute `openapi-typescript` para produzir `src/generated/openapi.ts`:

```
pnpm dlx openapi-typescript docs/{context}/oas/openapi.yaml -o src/generated/openapi.ts
```

`src/generated/` é saída somente leitura (gitignored ou commitado conforme a política do SDK — ambos são aceitáveis; commitar simplifica a instalação pelo consumidor, gitignorar mantém o diff enxuto). Os arquivos escritos à mão em `src/domains/*` importam tipos de `generated/` e expõem métodos ergonômicos.

### Política de Versionamento

- **Major (X.0.0):** remoção de símbolo público, mudança em assinatura de função, mudança em código de erro exportado, mudança em comportamento de runtime observável de contrato documentado.
- **Minor (0.X.0):** adição de símbolo público, adição de parâmetro opcional, adição de código de erro sem quebra.
- **Patch (0.0.X):** correção interna sem mudança na superfície pública.
- **Pré-1.0.0:** a superfície pública é instável; minor bumps podem carregar quebras, mas `BREAKING CHANGES.md` DEVE listar cada quebra.

### Fluxo de Release

1. O autor do PR adiciona um `.changeset/*.md` descrevendo a intenção (major/minor/patch) conforme a convenção do changesets.
2. O CI em `main` consome changesets pendentes, calcula a próxima versão, regenera `CHANGELOG.md` e abre um PR `Version Packages`.
3. O merge do PR `Version Packages` dispara `changeset publish`, que:
   - Constrói (`pnpm build`).
   - Valida (`pnpm validate` — typecheck, lint, test, publint, attw).
   - Publica no npm com `--provenance` (para `@guardia/*`).
   - Cria um GitHub Release com o trecho do changelog.

### Alvos de Distribuição

Ambos os alvos são suportados sem código condicional:

- **npm público (`@guardia/*`).** `publishConfig.access: "public"`, `provenance: true`, registry `https://registry.npmjs.org`.
- **Interno.** Mesmo pacote, registrado no registry interno do GitHub Packages; `publishConfig.registry: "https://npm.pkg.github.com"`. Consumidores usam `.npmrc` no nível do projeto. O artefato de build é idêntico.

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Classe pública | `Guardia{Context}Client` ou `GuardiaClient` para SDKs de contexto único | `GuardiaScheduledPaymentsClient` |
| Nomenclatura de método | verbo + recurso | `createScheduledTransfer`, `listRefunds` |
| Paginação | baseada em cursor conforme `codex-restful-pagination` | `client.listRefunds({ pageSize: 50 })` retorna `{ data, pageToken }` |
| Casing de arquivo | kebab-case | `scheduled-transfers.ts` |
| Tipos públicos | exportados de `index.ts` apenas quando estáveis | `ScheduledTransferInput`, `ScheduledTransfer` |

### Decisões Vigentes

| ADR | Decisão | Status |
|-----|---------|--------|
| ADR-{NN} | tsup como ferramenta de build para SDKs Guardia | Ativa |
| ADR-{NN} | changesets como ferramenta de versionamento | Ativa |
| ADR-{NN} | Biome como ferramenta de lint/format para novos SDKs | Ativa |

(Substitua os placeholders por números reais de ADR conforme forem escritos.)

### Restrições Técnicas

- Node.js mínimo: `>=20` (LTS no momento da autoria).
- O formato `Result<T, E>` espelha a semântica de `lex-python-result-type` quando aplicável; SDKs PODEM re-exportar de `@guardia/result` assim que esse pacote existir.
- Nenhuma API exclusiva de `node:` em caminhos de código consumidos por SDKs `@guardia/*` voltados a edge runtimes; quando uma variante para edge for necessária, exponha um subcaminho `exports` separado (`./edge`) condicionado por `worker`.

## Diagrama de Referência

```
┌──────────────────────────────────────────────────────────────┐
│                       Aplicação Consumidora                  │
└──────────────────────────────┬───────────────────────────────┘
                               │ import { GuardiaClient }
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  src/index.ts (superfície pública — declarada em `exports`)  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ src/domains/{resource}.ts   (métodos ergonômicos)      │  │
│  └─────────────────────────┬──────────────────────────────┘  │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ src/transport/http.ts                                  │  │
│  │   auth · retry · idempotência · trace · timeout · decode│ │
│  └─────────────────────────┬──────────────────────────────┘  │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ src/generated/openapi.ts  (tipos de openapi-typescript)│  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
                       API REST da Guardia
```

## Glossário

| Termo | Definição |
|-------|-----------|
| Superfície pública | Conjunto de símbolos alcançáveis a partir do mapa `exports` do pacote; contrato de estabilidade do SDK. |
| Código gerado | Saída de `openapi-typescript` (e similares) em `src/generated/`; tratado como somente leitura. |
| Transporte | Wrapper de `fetch` que centraliza auth, idempotência, retry, propagação de trace e decodificação. |
| Decoder | Função que converte payload desconhecido em valor tipado (schema Zod, decoder gerado, escrito à mão). |
| Hook de telemetria | Callback fornecido pelo consumidor que o SDK invoca nas fronteiras de request/response/error/retry. |

## Referências

- `lex-sdk-typescript` — Lei correspondente.
- `kata-sdk-typescript-scaffold` — procedimento para escafoldar um novo SDK.
- `cry-new-sdk-typescript` — atalho que invoca o Kata.
- `lex-restful-headers`, `codex-restful-headers` — headers canônicos da Guardia.
- `lex-idempotency`, `codex-idempotency` — política de idempotência.
- `lex-error-handling`, `codex-known-errors` — envelope e catálogo de códigos de erro.
- `codex-semantic-version` — regras de versionamento.
- `lex-observability-required` — expectativas de telemetria.
- `codex-oas-structure`, `lex-feature-design-docs` — especificação OpenAPI de origem.
