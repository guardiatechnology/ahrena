# Kata: Escafoldar um SDK Guardia em TypeScript/Node.js

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — SDK: procedimento end-to-end para escafoldar (ou enquadrar à conformidade) um SDK em TypeScript/Node.js que consome a API REST da Guardia, conforme `lex-sdk-typescript` e `codex-sdk-typescript`

## Objetivo

Este Kata produz um esqueleto de SDK em TypeScript/Node.js que, no primeiro dia, está em conformidade com `lex-sdk-typescript`: tipos estritos, `exports` declarado, transporte com auth + idempotência + trace, mapeamento de envelope de erro, hooks de telemetria, testes e fluxo de release via changesets. O mesmo procedimento se aplica ao trabalho de enquadrar um SDK existente à conformidade (os arquivos existentes são comparados ao esqueleto-alvo).

## Quando Usar

- Quando um novo bounded context expõe uma API REST estável e um SDK público é exigido.
- Quando um time interno precisa de um cliente tipado contra um contexto de API existente da Guardia.
- Quando `cry-new-sdk-typescript` for invocado.
- Quando um SDK legado falha no Gate 2 e precisa ser enquadrado à conformidade com a Lei.

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Nome do SDK | Sim | Nome do pacote, p. ex. `@guardia/sdk-scheduled-payments` ou `sdk-internal-billing`. |
| Bounded context | Sim | O bounded context da Guardia que o SDK atende, p. ex. `scheduled-payments`. Usado para localizar `docs/{context}/oas/openapi.yaml`. |
| Alvo de distribuição | Sim | `npm-public` (`@guardia/*`), `npm-internal` (GitHub Packages) ou `both`. |
| Fonte OpenAPI | Não | Caminho para `docs/{context}/oas/openapi.yaml`. Quando ausente, o SDK é entregue sem tipos gerados e o catálogo é escrito à mão. |
| Alvo do repositório | Não | `monorepo` (default) ou `standalone`. Afeta CI e configuração do changesets. |
| Caminho do SDK existente | Não | No modo "enquadrar à conformidade", o caminho da raiz do SDK existente. |

## Workflow

```
Progresso:
- [ ] 1. Esclarecer inputs e resolver alvo de distribuição
- [ ] 2. Inicializar esqueleto do pacote
- [ ] 3. Configurar ferramental (tsconfig, tsup, biome, vitest)
- [ ] 4. Gerar tipos a partir do OpenAPI (quando disponível)
- [ ] 5. Implementar transporte (auth, retry, idempotência, trace, telemetria)
- [ ] 6. Implementar modelo de erro e helper Result
- [ ] 7. Implementar primeiro módulo de domínio + testes
- [ ] 8. Conectar changesets e fluxo de release
- [ ] 9. Executar suíte de validação e produzir relatório de conformidade
```

### Passo 1: Esclarecer Inputs e Resolver Alvo de Distribuição

1. Confirme que o nome do SDK segue a convenção `@guardia/sdk-{context}` (público) ou `@guardia-internal/sdk-{context}` (interno).
2. Confirme que o bounded context existe em `docs/{context}/` e localize `oas/openapi.yaml`. Quando ausente, pergunte ao usuário se deve prosseguir sem tipos gerados ou aguardar a publicação do OpenAPI.
3. Resolva a distribuição:
   - `npm-public` → `publishConfig.access: "public"`, `provenance: true`, registry npmjs.
   - `npm-internal` → `publishConfig.registry: "https://npm.pkg.github.com"`.
   - `both` → matriz de publicação no CI; mesmo artefato.
4. Confirme o alvo do repositório (monorepo vs standalone) — afeta a raiz do changesets e a localização do workflow de CI.

### Passo 2: Inicializar Esqueleto do Pacote

1. Crie a árvore de diretórios conforme `codex-sdk-typescript` (`src/`, `test/`, `.changeset/`, arquivos de configuração no topo).
2. Escreva `package.json` com:
   - `name`, `version: "0.1.0"`, `type: "module"`, `engines.node: ">=20"`.
   - Mapa `exports` com no mínimo `"."` resolvendo para `dist/index.{js,cjs,d.ts}`.
   - `files: ["dist", "README.md", "DEPENDENCIES.md"]`.
   - `sideEffects: false`.
   - `publishConfig` conforme o alvo de distribuição.
3. Crie `DEPENDENCIES.md` listando cada dependência de runtime com: nome, propósito, licença, data da última auditoria.
4. Crie `README.md` com instalação, quickstart e link para `codex-sdk-typescript`.

### Passo 3: Configurar Ferramental

1. **`tsconfig.json`** — estenda `@guardia/tsconfig-sdk` quando existir; caso contrário, inline o baseline de `codex-sdk-typescript`. Confirme `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, target `ES2022`, module `ESNext`.
2. **`tsup.config.ts`** — entry `src/index.ts`, formatos `["esm", "cjs"]`, `dts: true`, `clean: true`, `treeshake: true`, `splitting: false`. Acrescente entries para cada subcaminho declarado em `exports`.
3. **`biome.json`** (ou `eslint.config.js`) — habilite `noExplicitAny` como erro em arquivos publicáveis, proíba `console.*` em `src/`, proíba imports relativos atravessando `src/generated/` a partir de fora da camada de transporte.
4. **`vitest.config.ts`** — limiares de cobertura em 80/80/80/80; ambiente `node` para testes de transporte, `happy-dom` apenas quando polyfills de DOM forem necessários.

### Passo 4: Gerar Tipos a Partir do OpenAPI

1. Quando `docs/{context}/oas/openapi.yaml` existe:
   ```
   pnpm dlx openapi-typescript docs/{context}/oas/openapi.yaml -o src/generated/openapi.ts
   ```
2. Adicione um script npm `"types:generate": "openapi-typescript ..."` para manter o comando descobrível.
3. Decida entre commit ou gitignore para `src/generated/`. Default: commit, para simplificar a instalação pelo consumidor. Documente a escolha no `README.md`.
4. Quando o OpenAPI estiver ausente, escreva à mão tipos mínimos em `src/types/` e registre no `README.md` que o SDK será regenerado quando o spec for publicado.

### Passo 5: Implementar Transporte

1. Crie `src/transport/http.ts` com a classe `HttpTransport`:
   - Lê `config.baseUrl`, `config.token` (string ou resolver assíncrono), `config.fetch` (default `globalThis.fetch`).
   - Monta `Authorization: Bearer <token>`.
   - Para `POST`/`PUT`/`PATCH`/`DELETE`, define `Idempotency-Key` recebido do chamador ou gera UUID v7.
   - Lê o trace id de `config.tracer` (default no-op) e define `X-Grd-Trace-Id`.
   - Envolve `fetch` com `AbortController` para timeout.
2. Crie `src/transport/retry.ts`:
   - Backoff exponencial com jitter em `429`, `502`, `503`, `504`, erros de rede.
   - Defaults: 3 tentativas, base 100 ms, teto 2 s.
   - Honra `Retry-After` quando presente.
3. Crie `src/transport/telemetry.ts`:
   - Interface `TelemetryHook` (`onRequest`, `onResponse`, `onError`, `onRetry`).
   - Default no-op.

### Passo 6: Implementar Modelo de Erro e Helper Result

1. Crie `src/errors.ts` com a classe `GuardiaError` e a união canônica `GuardiaErrorCode` (espelhando `codex-known-errors`).
2. Crie `src/result.ts` com `Result<T, E>` = `Ok<T> | Err<E>` mais helpers `ok`, `err`, `isOk`, `isErr`, `map`, `mapErr`.
3. O transporte traduz toda resposta não-2xx e toda falha em nível de transporte para `Err(GuardiaError)`. Métodos públicos retornam `Promise<Result<T, GuardiaError>>`.
4. Exponha códigos de erro pelo subcaminho `./errors` em `exports` para que consumidores possam fazer pattern-matching.

### Passo 7: Implementar Primeiro Módulo de Domínio + Testes

1. Escolha um recurso do OpenAPI (p. ex. `scheduled-transfers`) e implemente `src/domains/scheduled-transfers.ts` expondo os métodos CRUD canônicos (`create`, `list`, `get`, `update`, `delete`) conforme `codex-restful-payload`.
2. Conecte os métodos ao `HttpTransport`; mapeie formas de request/response por decoders.
3. Escreva **testes unitários** para cada método usando MSW para asserir:
   - URL, método, body e headers da requisição (`Authorization`, `Idempotency-Key` em verbos mutadores, `X-Grd-Trace-Id`).
   - Decodificação da resposta de sucesso.
   - Mapeamento do envelope de erro para `400`, `401`, `404`, `409`, `429`, `500`, `503`.
   - Retry em `503` com backoff (use fake timers).
4. Escreva **testes de integração** que exercitam o transporte contra um servidor gravado (servidor HTTP do MSW) e asseram a superfície pública end-to-end.

### Passo 8: Conectar Changesets e Fluxo de Release

1. Execute `pnpm dlx @changesets/cli init`.
2. Configure `.changeset/config.json` com `access: "public"` (para `@guardia/*`) ou `restricted` (interno), `baseBranch: "main"`, `commit: false`.
3. Adicione o GitHub Action do changesets em `.github/workflows/release.yml`:
   - No push para `main`, execute `pnpm validate`, depois `changeset version` (abre um PR) ou `changeset publish` (quando o PR de versão for merged).
   - Em pacotes `@guardia/*`, habilite `--provenance` e exija permissão `id-token: write`.
4. Adicione um `.github/workflows/ci.yml` que roda em cada PR: `pnpm install`, `pnpm validate`, upload de cobertura.

### Passo 9: Validação e Relatório de Conformidade

1. Execute `pnpm validate` localmente:
   - `tsc --noEmit` sem erros.
   - `biome check` sem erros.
   - `vitest run` com cobertura ≥ 80%.
   - `publint` sem erros.
   - `attw --pack .` sem erros (sem CJS falso, sem ESM falso).
2. Produza o relatório de conformidade mapeando cada cláusula de `lex-sdk-typescript` ao artefato de verificação:

| Cláusula | Verificação |
|----------|-------------|
| 1. TS estrito | Saída de `tsc --noEmit` |
| 2. Mapa `exports` | Saída de `publint`/`attw` |
| 3. Semver | Diretório `.changeset/` + workflow de CI |
| 4. Headers canônicos | Asserções em testes de integração |
| 5. Envelope de erro | Testes unitários para `400`/`401`/`409`/`500` |
| 6. `.d.ts` pública | `attw --pack .` |
| 7. Dependências justificadas | `DEPENDENCIES.md` |
| 8. Testes + cobertura | Relatório de cobertura do Vitest |
| 9. Hooks de telemetria | `src/transport/telemetry.ts` + testes |
| 10. `engines.node` | `package.json` |

3. Entregue o relatório ao revisor do PR e ao `warrior-athena` para o Gate 2.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Esqueleto do SDK | Projeto TypeScript | `sdk-{context}/` (monorepo) ou raiz do repositório (standalone) |
| Relatório de conformidade | Markdown | Corpo do PR ou `docs/sdks/{context}/conformance.md` |
| Changeset inicial | Markdown | `.changeset/initial.md` descrevendo a superfície 0.1.0 |

## Exemplo de Execução

### Input de Exemplo

```
Nome do SDK: @guardia/sdk-scheduled-payments
Bounded context: scheduled-payments
Distribuição: npm-public
OpenAPI: docs/scheduled-payments/oas/openapi.yaml
Repositório: monorepo
```

### Output de Exemplo

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
│   ├── generated/openapi.ts        (de openapi-typescript)
│   └── domains/scheduled-transfers.ts
├── test/{unit,integration}/...
├── DEPENDENCIES.md
├── README.md
└── .changeset/initial.md
```

Validação: `pnpm validate` passa, cobertura 87% de linhas, `publint` e `attw` sem erros, relatório de conformidade anexado ao PR.

## Restrições

- Nunca enfraquecer o `tsconfig.json` em relação ao baseline (sem opt-out de `strict`, `noUncheckedIndexedAccess` ou `exactOptionalPropertyTypes`).
- Nunca publicar um release `0.x.y` que introduza mudança na superfície pública sem entrada em `BREAKING CHANGES.md`.
- Nunca adicionar dependência de runtime sem entrada em `DEPENDENCIES.md` justificando.
- Nunca escrever em `console.*` a partir de `src/`; roteie todo sinal pelo hook de telemetria.
- Quando `docs/{context}/oas/openapi.yaml` estiver ausente, não invente endpoints — pause e solicite o OAS ou escreva à mão um stub mínimo em `src/types/` com aprovação explícita do usuário.
