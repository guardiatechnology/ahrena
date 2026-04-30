# Cry: Redigir Cenários BDD de Negócio a partir da Issue + Notion

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Independente — produz cenários BDD focados em negócio para uma issue do GitHub e os escreve de volta no corpo da issue

## Descrição

Atalho independente para invocar `kata-bdd-create-scenarios`. Lê uma issue do GitHub (e contexto do Notion quando o MCP estiver configurado), produz cenários Gherkin focados em negócio e os persiste no corpo da issue dentro dos marcadores `bdd:scenarios`. Nunca lê código-fonte. Independente de `/cry-implement-issue` — pode ser invocado antes, depois ou totalmente fora do fluxo Issue-Driven.

## Uso

```
/cry-bdd-create-scenarios <issue-number> [<owner>/<repo>]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `issue-number` | Sim | Número da issue no GitHub | `42` |
| `<owner>/<repo>` | Não | Padrão: repositório atual via git remote | `guardiafinance/ahrena` |

## Pré-requisitos

- `github` listado em `mcp.servers` em `.ahrena/.directives`
- `notion` listado em `mcp.servers` (opcional, enriquece o contexto)
- Env: `GITHUB_PAT` obrigatória; `NOTION_API_KEY` opcional
- Issue existente no GitHub

## O Que o Comando Faz

1. Invoca `kata-bdd-create-scenarios`.
2. A kata lê a issue e o Notion (nunca código) e redige cenários focados em negócio em Gherkin.
3. A kata duplica quaisquer cenários API/UI já presentes na issue, deixando os originais intocados.
4. A kata apresenta o bloco `bdd:scenarios` proposto ao usuário para confirmação.
5. Sob confirmação, a kata atualiza o corpo da issue via GitHub MCP.

## Prompt Template

```
Context:
- Issue: #{{issue-number}}
- Repository: {{<owner>/<repo>}} (or detected via git remote)

Task:
Run kata-bdd-create-scenarios for issue #{{issue-number}}. Author business-focused BDD scenarios sourced exclusively from the GitHub issue body, comments, and related Notion pages. Do not read source code. Duplicate any existing API/UI Gherkin into a separate business-language form (preserve the originals). Wait for explicit user confirmation before updating the issue. Persist the final scenarios into the issue body inside the markers <!-- bdd:scenarios:start --> ... <!-- bdd:scenarios:end -->. Report scenario titles and slugs.

Strictly respect lex-bdd-scenarios (sources, language, persistence) and lex-mcp (no destructive write without explicit user confirmation).
```

## Exemplo de Invocação

**Entrada:**

```
/cry-bdd-create-scenarios 42 guardiafinance/ahrena
```

**Saída esperada:**

- A kata busca a issue #42 (e o Notion, se configurado).
- Detecta 2 cenários focados em API a partir do template user-story-for-api.
- Redige 3 cenários focados em negócio.
- Apresenta ao usuário o bloco `bdd:scenarios` proposto.
- Sob confirmação, atualiza o corpo da issue. Cenários API originais permanecem inalterados.
- Reporta os slugs dos cenários:
  - `customer-requests-a-refund-for-an-eligible-payment`
  - `customer-cannot-refund-after-30-days`
  - `concurrent-refunds-deduplicate-by-idempotency-key`

## Restrições

- **Código nunca é fonte.** Arquivos-fonte e testes estão fora de escopo para este comando.
- **A issue deve existir.** Sem issue → o comando recusa (sem auto-criação).
- **Confirmação obrigatória.** Sem escrita na issue sem um "sim" explícito.
- **Independente.** Não entra no fluxo Issue-Driven, não bloqueia nenhuma fase ou gate.

## Cry vs Kata

| Aspecto | Cry | Kata |
|---|---|---|
| Natureza | Invocação rápida pelo número da issue | Procedimento completo (ler, redigir, validar, confirmar, persistir) |
| Complexidade | Baixa | Alta (9 passos incluindo MCP, validação de linguagem, atualização idempotente do bloco) |

## Cries e Katas Associados

- `kata-bdd-create-scenarios` — invocada por esta cry
- `cry-bdd-validate-scenarios` — checagem de cobertura após a implementação
- `cry-implement-issue` — fluxo ortogonal; esta cry pode rodar ao lado dele sem acoplamento

## Referências

- `lex-bdd-scenarios`, `lex-bdd-coverage` — leis
- `codex-bdd` — metodologia
- `kata-bdd-create-scenarios`, `kata-bdd-validate-scenarios` — procedimentos
