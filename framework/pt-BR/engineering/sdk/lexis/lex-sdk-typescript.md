# Lexis: SDK Guardia em TypeScript/Node.js

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Engenharia — SDK: toda biblioteca cliente em TypeScript/Node.js que consome a API REST da Guardia, independentemente de distribuição (`@guardia/*` no npm ou interna)

## Lei

> **Todo SDK em TypeScript/Node.js que consome a API REST da Guardia DEVE: (1) compilar sob `strict: true` com `noUncheckedIndexedAccess: true` e ter como alvo ES2022 ou superior; (2) declarar cada símbolo público no campo `exports` do `package.json` — re-exports implícitos via barril fora de `exports` são PROIBIDOS; (3) versionar segundo Semantic Versioning 2.0.0, onde qualquer alteração visível na superfície pública (tipos, assinaturas de função, códigos de erro exportados, comportamento de runtime de contratos documentados) constitui major ou minor bump conforme `codex-semantic-version`; (4) propagar os headers canônicos da Guardia em toda chamada HTTP — `Authorization: Bearer <token>`, `Idempotency-Key` para verbos mutadores e `X-Grd-Trace-Id` — conforme `lex-restful-headers` e `lex-idempotency`; (5) traduzir respostas de erro para o envelope padronizado definido em `lex-error-handling`, preservando `code`, `reason` e `message`, sem vazar formatos de transporte; (6) entregar declarações de tipo (`.d.ts`) geradas a partir do código-fonte — `any` NÃO PODE aparecer na superfície pública, e `unknown` é permitido apenas em fronteiras de parsing (decodificação de resposta) com caminho de estreitamento tipado; (7) declarar cada dependência de runtime em `dependencies` com entrada justificada no `DEPENDENCIES.md` do SDK — adicionar dependência de runtime sem justificativa é PROIBIDO; (8) fornecer testes unitários para cada função pública e testes de integração contra um transporte HTTP gravado (nock/MSW ou equivalente) com ≥ 80% de cobertura de linhas em CI; (9) expor hooks de telemetria (ciclo de vida da requisição, erro, retry) que consumidores PODEM conectar ao OpenTelemetry — chamadas internas a `console.*` são PROIBIDAS; (10) declarar `engines.node` com a versão LTS mínima suportada do Node.js (atualmente `>=20`) e NÃO PODE usar APIs introduzidas após esse piso sem proteção de runtime.**

## Abrangência

- **Aplica-se a:** todo SDK em TypeScript ou JavaScript autorado pela Guardia cujo propósito é consumir a API REST da Guardia, independentemente do canal de distribuição (`@guardia/*` no npm, GitHub Packages privado, pacote interno de monorepo, fork vendoreado).
- **Fora de escopo:** código de aplicação que embute um SDK (consumidores), código gerado por `openapi-typescript`/`openapi-fetch` a partir de `docs/{context}/oas/openapi.yaml` (o SDK encapsula e re-expõe o código gerado por meio de sua própria superfície pública, a qual está em escopo).
- **Agentes vinculados:** `warrior-apollo` (ao autorar um SDK em nome de um contexto de API), `warrior-hephaestus` (ao integrar um SDK em um frontend), `warrior-iris` (consumidores mobile de SDKs compatíveis com Node), `warrior-athena` (Gate 2 do fluxo Issue-Driven).
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Bloqueio automático:** o Gate 2 (`kata-quality-gate`) rejeita o PR quando qualquer cláusula da Lei for violada e não remediada.
2. **Quebra de superfície pública:** qualquer desvio das cláusulas (2), (3) ou (6) é tratado como incidente de contrato publicado e dispara um ciclo coordenado de depreciação conforme `codex-semantic-version`.
3. **Escalada de segurança:** vazamento de header de autenticação, ausência de `Idempotency-Key` em verbos mutadores ou retornos `any` não tipados na superfície pública são escalados ao platform owner do contexto de API consumido.
4. **Remediação:** o SDK DEVE ser ajustado à conformidade antes do próximo release; releases intermediários com violações conhecidas carregam entrada documentada em `KNOWN_ISSUES.md` e versão-alvo para a correção.

## Exemplos

### Correto

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
// package.json — exports explícitos, engines, sem barril implícito
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

### Incorreto

```typescript
// ❌ Superfície pública sem tipos
export async function createTransfer(input: any): Promise<any> {
  const res = await fetch("/v1/transfers", { method: "POST", body: JSON.stringify(input) });
  return res.json(); // sem Idempotency-Key, sem Authorization, sem envelope de erro, retorna any
}
```

```json
// ❌ Barril implícito, sem engines, sem mapa exports
{
  "name": "guardia-sdk",
  "main": "src/index.ts",
  "dependencies": { "axios": "*", "lodash": "*", "moment": "*" }
}
```

## Validação Automatizada

- **Ferramenta:**
  - **TS estrito:** `tsc --noEmit` com o `tsconfig.json` do SDK estendendo `@guardia/tsconfig-sdk` (que fornece `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`).
  - **Drift de superfície pública:** `api-extractor` (ou `arethetypeswrong`/`publint`) verificando mapa `exports`, consistência de dual-emit e cobertura de `.d.ts`.
  - **Conformidade semver:** `changesets` com `--commit-mode=intent`; CI bloqueia merges que alterem versão sem changeset correspondente.
  - **Contrato HTTP:** suíte de integração gravando requisições contra `nock` ou MSW com asserções sobre `Authorization`, `Idempotency-Key`, `X-Grd-Trace-Id`.
  - **Auditoria de dependências:** `npm audit --omit=dev` + `depcheck`; presença de `DEPENDENCIES.md` exigida no Gate 2.
  - **Linter:** `eslint-plugin-no-restricted-imports` bloqueando `console.*` em `src/`; `@typescript-eslint/no-explicit-any` em `error` para arquivos publicáveis.
- **Momento:** pre-commit (lint, tipos), CI em cada PR (suíte completa, cobertura, publint), pré-publish (validação por `npm publish --dry-run`), Gate 2 do fluxo Issue-Driven.
- **Métrica:** 0 PRs com `any` na superfície pública; 100% dos endpoints mutadores com asserção de `Idempotency-Key` em testes de integração; 100% dos releases com changeset correspondente; cobertura de linhas não decrescente em `main`.
