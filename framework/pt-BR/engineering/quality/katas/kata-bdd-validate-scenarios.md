# Kata: Validar Cobertura BDD na Suite de Testes

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Independente — confirma que cada cenário BDD de negócio em uma issue do GitHub é coberto por pelo menos um teste, via marcador canônico ou fallback

## Objetivo

Ler o bloco `bdd:scenarios` de uma issue do GitHub, escanear a suite de testes em busca de marcadores BDD canônicos e padrões de fallback, e produzir um relatório bidirecional de cobertura (cenários → testes, testes → cenários) classificado como `complete`, `gaps`, `drift` ou `gaps+drift`. A kata não executa testes; ela inspeciona mapeamentos.

## Quando Usar

- Após o início da implementação, para confirmar que cenários estão sendo cobertos conforme os testes chegam.
- Na revisão de PR, para confirmar que uma mudança casa com a intenção BDD registrada na issue.
- Invocada através de `/cry-bdd-validate-scenarios <issue>`.
- Independente — independente de `kata-quality-gate`. Ambas podem rodar na mesma mudança sem acoplamento.

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Número da issue | Sim | Issue do GitHub contendo o bloco `bdd:scenarios` |
| Repositório | Sim | `owner/repo` (padrão: detectado via git remote) |
| Raiz dos testes | Não | Caminho(s) a escanear; padrão: raízes comuns por stack |
| Stack | Não | Detectado a partir das extensões de arquivo na working tree |

## Workflow

```
Progresso:
- [ ] 1. Verificar MCP e diretivas
- [ ] 2. Ler a issue e extrair o bloco bdd:scenarios
- [ ] 3. Parsear cenários em pares (título, slug)
- [ ] 4. Detectar stack(s) e escanear testes
- [ ] 5. Construir mapa cenário → teste
- [ ] 6. Construir mapa teste → cenário
- [ ] 7. Classificar gaps e drift
- [ ] 8. Emitir relatório de cobertura
```

### Passo 1: Verificar MCP e diretivas

Igual ao Passo 1 de `kata-bdd-create-scenarios`. O MCP `github` é obrigatório; o Notion não é usado aqui.

### Passo 2: Ler a issue

Usar `kata-mcp-github-read` para buscar o corpo da issue. Localizar o bloco `<!-- bdd:scenarios:start -->` ... `<!-- bdd:scenarios:end -->`. Se ausente, reportar "no BDD scenarios authored in this issue" e parar. A kata é um no-op quando não há nada a validar; ela nunca inventa a ausência de bloco como achado.

### Passo 3: Parsear cenários

Para cada linha `Scenario: <título>` no bloco:

1. Extrair o título (verbatim, com trim).
2. Computar o slug: lowercase, substituir runs de não-alfanuméricos por `-`, colapsar `-` repetidos, remover `-` no início e no fim.

Produzir uma lista `[(title, slug)]`.

### Passo 4: Detectar stack e escanear testes

Detectar stacks a partir da working tree:

- `*.py` → Python
- `*.ts|*.tsx|*.js|*.jsx` → JS/TS
- `*.go` → Go

Raízes de teste padrão quando não especificadas:

- Python: `tests/`, `**/test_*.py`, `**/*_test.py`
- JS/TS: `tests/`, `__tests__/`, `**/*.test.{ts,tsx,js,jsx}`, `**/*.spec.{ts,tsx,js,jsx}`
- Go: `**/*_test.go`

Para cada teste, coletar:

- `markers`: lista de slugs reivindicados via marcador canônico
  - Python: decorador `@bdd_scenario("...")` acima da função de teste (regex; tolerar tanto o helper bare quanto `@pytest.mark.bdd_scenario("...")` quando o helper encapsula um pytest mark)
  - JS/TS: tag JSDoc `// @bdd_scenario <slug>` imediatamente acima do teste, ou chamada `bddScenario("<slug>", ...)` envolvendo o teste
  - Go: comentário `// bdd_scenario: <slug>` imediatamente acima de `func TestXxx`
- `fallbacks`: lista de slugs/títulos encontrados via nome do teste ou docstring que casa com `BDD:\s*<título-ou-slug>`

Um único teste PODE mapear para múltiplos cenários.

### Passo 5: mapa cenário → teste

Para cada cenário `(title, slug)`:

1. Listar testes com marcador canônico que casa com `slug`.
2. Listar testes com fallback que casa com `title` ou `slug` (case-insensitive no título; exato no slug).
3. Status: `covered` se ≥1 teste em qualquer um dos grupos; `gap` caso contrário.

### Passo 6: mapa teste → cenário

Para cada teste que tenha pelo menos um marcador BDD ou fallback:

1. Resolver o slug para um cenário na lista parseada.
2. Se nenhum cenário correspondente existir na issue → `drift` (marcador órfão).

### Passo 7: Classificar

- **`complete`**: todo cenário coberto, sem marcadores órfãos.
- **`gaps`**: ao menos um cenário sem cobertura.
- **`drift`**: ao menos um teste reivindica um cenário ausente da issue.
- Uma execução pode ser ambos (`gaps+drift`).

### Passo 8: Emitir relatório de cobertura

Tabela em Markdown apresentada ao usuário:

```markdown
# BDD Coverage — Issue #{n}

- **Result:** {complete | gaps | drift | gaps+drift}
- **Scenarios in issue:** {count}
- **Covered:** {count}  | **Uncovered:** {count}  | **Orphan markers:** {count}

## Scenario → Test

| Scenario | Slug | Tests | Status |
|---|---|---|:-:|
| Customer requests a refund for an eligible payment | customer-requests-a-refund-for-an-eligible-payment | tests/refunds/test_create.py::test_pending_refund | ✅ |
| Concurrent refunds deduplicate by idempotency key | concurrent-refunds-deduplicate-by-idempotency-key | — | ❌ |

## Drift (markers without scenarios)

- tests/legacy/test_old.py::test_a — claims `legacy-scenario-removed`
```

Quando `result != complete`, recomendar correções explícitas por achado:

- **Gaps:** adicionar um teste de cobertura (qualquer nível) marcado com o slug do cenário ou com `BDD: <título>` na docstring; alternativamente, remover o cenário da issue se a regra não estiver mais no escopo.
- **Drift:** remover o marcador, renomeá-lo para um slug válido, ou restaurar o cenário na issue.

Se o usuário pedir explicitamente, salvar o relatório em `docs/bdd-coverage/{issue-n}.md`. Caso contrário, emitir apenas inline.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Relatório de cobertura | Resposta em Markdown | Visível ao usuário |
| Relatório opcional salvo | Arquivo Markdown | `docs/bdd-coverage/{issue-n}.md` (apenas quando o usuário pedir) |

## Restrições

- **Read-only.** Não modifica a issue, os testes nem qualquer outro arquivo.
- **Não executa testes.** A cobertura aqui é estrutural (mapeamento), não comportamental.
- **Não infere cenários a partir dos testes.** Um teste sem marcador não é cobertura.
- **Sem aprovações silenciosas.** Quando a issue não tem bloco `bdd:scenarios`, a kata diz isso explicitamente.

## Referências

- `lex-bdd-coverage` — lei de cobertura
- `codex-bdd` — metodologia e convenções de marcadores
- `kata-bdd-create-scenarios` — procedimento predecessor
- `lex-test-pyramid`, `codex-test-strategy` — decisões de nível para os testes de cobertura
