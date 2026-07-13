# Cry: Novo SDK Guardia em TypeScript/Node.js

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para escafoldar (ou enquadrar à conformidade) um SDK Guardia em TypeScript/Node.js conforme `lex-sdk-typescript` e `codex-sdk-typescript`

## Descrição

Este comando invoca `kata-sdk-typescript-scaffold` para produzir um SDK em TypeScript/Node.js que consome a API REST da Guardia e está em conformidade com `lex-sdk-typescript` desde o primeiro dia. O mesmo comando enquadra um SDK legado à conformidade quando a flag `--from` aponta para um diretório existente.

## Uso

```
/cry-new-sdk-typescript <nome-do-sdk> <bounded-context> [--target=npm-public|npm-internal|both] [--from=<caminho>]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `nome-do-sdk` | Sim | Nome do pacote seguindo a convenção canônica. | `@guardia/sdk-scheduled-payments` |
| `bounded-context` | Sim | Bounded context da Guardia atendido pelo SDK. Usado para localizar `docs/{context}/oas/openapi.yaml`. | `scheduled-payments` |
| `--target` | Não | Alvo de distribuição. Default: `npm-public`. | `--target=both` |
| `--from` | Não | Caminho de um SDK existente para enquadrar à conformidade em vez de escafoldar do zero. | `--from=sdks/legacy-billing` |

## O que o Comando Faz

1. Interpreta os inputs e valida o nome do SDK e o bounded context.
2. Executa `kata-sdk-typescript-scaffold` passo a passo, perguntando ao usuário qualquer input em falta.
3. Gera o esqueleto do projeto, transporte, modelo de erro, primeiro módulo de domínio e o fluxo de release via changesets.
4. Executa `pnpm validate` e produz o relatório de conformidade mapeando cada cláusula de `lex-sdk-typescript` ao artefato de verificação.
5. Expõe o relatório de conformidade e o checklist de próximos passos na descrição do PR.

## Prompt Template

```
Contexto:
- Nome do SDK: {{nome-do-sdk}}
- Bounded context: {{bounded-context}}
- Alvo de distribuição: {{target}}
- Caminho do SDK existente (quando for enquadrar à conformidade): {{from}}

Tarefa:
Execute `kata-sdk-typescript-scaffold` de ponta a ponta. Consulte
`lex-sdk-typescript` e `codex-sdk-typescript` para cada decisão. Faça
perguntas de esclarecimento antes de escafoldar quando o bounded context
não tiver OpenAPI em docs/{{bounded-context}}/oas/openapi.yaml ou quando
`--from` apontar para caminho inexistente. Após escafoldar, execute a
suíte de validação e produza o relatório de conformidade.

Saída:
- Esqueleto do SDK em sdks/{{bounded-context}}/ (monorepo) ou raiz do
  repositório (standalone), com src/, test/, tsconfig, tsup, biome,
  vitest, changesets, workflows de CI.
- Relatório de conformidade cobrindo as 10 cláusulas de `lex-sdk-typescript`.
- Changeset inicial documentando a superfície pública 0.1.0.
```

## Exemplo de Invocação

**Input:**

```
/cry-new-sdk-typescript @guardia/sdk-scheduled-payments scheduled-payments --target=both
```

**Output esperado:**

O Kata escafolda `sdks/scheduled-payments/`, gera tipos a partir de `docs/scheduled-payments/oas/openapi.yaml`, implementa o transporte com `Authorization`, `Idempotency-Key` e `X-Grd-Trace-Id`, entrega o primeiro módulo de domínio (`scheduled-transfers`), conecta changesets e o workflow de release para npm público e GitHub Packages, executa `pnpm validate` e anexa o relatório de conformidade ao PR resultante.

## Restrições

- Nunca publicar durante o scaffolding (sem `npm publish`); o Cry apenas prepara o pacote e o valida localmente.
- Nunca enfraquecer o baseline de `tsconfig.json` de `codex-sdk-typescript`.
- Quando o bounded context não tem especificação OpenAPI, pause e exponha o artefato em falta em vez de inventar endpoints.

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Atalho único com dois argumentos obrigatórios. | Procedimento de nove passos com validação e relatório. |
| **Complexidade** | Baixa (um comando). | Alta (scaffold, transporte, modelo de erro, testes, fluxo de release). |
| **Configura agente?** | Sim (assume o papel de autor do SDK e invoca o Kata). | Sim (define cada passo). |
| **Exemplo** | `/cry-new-sdk-typescript @guardia/sdk-x x` | Executar `kata-sdk-typescript-scaffold` com inputs explícitos. |

## Kata e Lexis Associados

- **kata-sdk-typescript-scaffold** — procedimento de scaffolding end-to-end.
- **lex-sdk-typescript** — leis inquebráveis para todo SDK TS/Node Guardia.
- **codex-sdk-typescript** — manual de referência.

## Referências

- `kata-sdk-typescript-scaffold`
- `lex-sdk-typescript`
- `codex-sdk-typescript`
- `lex-restful-headers`, `lex-idempotency`, `lex-error-handling` — contrato que o SDK aplica em cada chamada.
- `codex-semantic-version` — regras de versionamento consumidas pelo fluxo de release.
