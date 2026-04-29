# Kata: Desenho de Cenários BDD

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Qualidade. Primeira metade da Fase 8 do fluxo Issue-Driven. Produz o conjunto de cenários Gherkin de uma issue, **cego para o código de implementação**.

## Objetivo

Produzir `docs/issues/issue-{n}/07-bdd-scenarios.md` derivando cenários Gherkin **exclusivamente** das fontes de especificação (Issue do GitHub, páginas Notion vinculadas e artefatos das Fases 1-3 do fluxo). O artefato é validação black-box do comportamento esperado e serve de contrato para a etapa seguinte (`kata-bdd-validate-implementation`).

## Quando Usar

- Fase 8.1 do fluxo orquestrado por `warrior-athena`, **após** Gate 2 passar.
- Sempre que uma feature ou bugfix precisar de um conjunto de cenários BDD atualizado (ex.: ACs aditados via Gate 1 nova iteração).
- Sob demanda quando o time pede uma validação BDD independente de uma feature já implementada.

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `issue_number` | Sim | Número da issue no GitHub (ex.: `42`) |
| `repo` | Sim | `owner/repo` (ex.: `guardiafinance/ahrena`) |
| Artefatos de fluxo | Sim | `01-brief.md`, `02-requirements.md`, `03-architecture.md` em `docs/issues/issue-{n}/` |
| Páginas Notion | Não | Referenciadas pela Issue ou pelos artefatos; coletadas via `kata-mcp-notion-read` |
| ADRs vinculados | Não | Em `docs/adr/` quando referenciados pela arquitetura |

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições e directives
- [ ] 2. Declarar guarda de leitura (cego para código)
- [ ] 3. Ler fontes de especificação permitidas
- [ ] 4. Construir inventário de ACs
- [ ] 5. Derivar cenários por AC (taxonomia)
- [ ] 6. Redigir Gherkin declarativo
- [ ] 7. Auto-lint (regex do codex-gherkin)
- [ ] 8. Compor 07-bdd-scenarios.md (frontmatter + Gherkin)
- [ ] 9. Tratar ambiguidades (comentário na Issue)
- [ ] 10. Persistir e atualizar checkpoint
- [ ] 11. Validação final
```

### Passo 1: Verificar pré-condições e directives

1. Ler `.ahrena/.directives` per `lex-directives`.
2. Confirmar que `github` e `notion` estão em `mcp.servers` per `lex-mcp`. Se `notion` não estiver, prosseguir só com Issue + artefatos (registrar no frontmatter).
3. Confirmar variáveis `GITHUB_PAT` e `NOTION_API_KEY` (quando aplicável).
4. Confirmar a presença de `docs/issues/issue-{n}/01-brief.md`, `02-requirements.md`, `03-architecture.md`. Se algum faltar, parar e reportar — Fase 8 exige Fases 1-3 completas.

### Passo 2: Declarar guarda de leitura (cego para código)

Antes de qualquer leitura, registrar internamente o conjunto de fontes proibidas (per `lex-bdd-spec-only-sources` Regra 2). O agente **NÃO** pode abrir arquivos em:

```
src/, app/, lib/, pkg/, internal/, tests/, spec/, __tests__/,
cypress/, e2e/, playwright/, *.feature consumidos por runner,
qualquer extensão de código (.py, .ts, .tsx, .js, .jsx, .java, .go, .rs)
```

Se uma fonte permitida (ex.: `03-architecture.md`) cita um arquivo de implementação, **o caminho citado é apenas referência textual** — o agente não abre o arquivo.

### Passo 3: Ler fontes de especificação permitidas

Em ordem (per `codex-bdd` Seção 2):

1. `docs/issues/issue-{n}/02-requirements.md` — ACs numerados.
2. `docs/issues/issue-{n}/01-brief.md` — contexto.
3. GitHub Issue via `kata-mcp-github-read` — título, body, comentários relevantes.
4. Páginas Notion referenciadas via `kata-mcp-notion-read` em modo `page` profundidade `full`.
5. `docs/issues/issue-{n}/03-architecture.md` — restrições e contratos visíveis ao usuário.
6. ADRs em `docs/adr/` quando referenciados pelo `03-architecture.md`.

Para cada fonte aberta, registrar internamente o caminho/URL (será listada no frontmatter do output).

### Passo 4: Construir inventário de ACs

1. Extrair de `02-requirements.md` cada critério numerado `AC-{N}`.
2. Para cada AC, identificar:
   - Tipo de exigência (positiva, negativa, com fronteira numérica, com NFR).
   - Termos de domínio que aparecem (para preservar linguagem ubíqua per `codex-bdd` Seção 6).
   - Dependências entre ACs (quando aplicável).
3. Manter o inventário como tabela mental ou rascunho (não persiste).

### Passo 5: Derivar cenários por AC (taxonomia)

Aplicar a regra de cobertura mínima de `codex-bdd` Seção 4:

| Para cada AC | Pelo menos |
|---|---|
| Sempre | 1 `@happy-path` |
| Tem requisito negativo explícito ("recusa quando", "rejeita se") | 1 `@error` |
| Tem fronteira numérica/temporal (limites, ranges, datas) | 1 `@edge` |
| Tem caminho alternativo de sucesso | 1 `@alternative` |
| Tem NFR observável (latência, idempotência) | 1 `@nfr` |

Atribuir id `SCN-{N}` único, contínuo dentro do arquivo (regenerar a numeração se cenários forem removidos em revisão).

### Passo 6: Redigir Gherkin declarativo

Para cada cenário:

1. Aplicar a estrutura de `codex-gherkin` Seção 1 (subset adotado).
2. Usar `Background` apenas para pré-condição de negócio compartilhada (per `lex-bdd-gherkin-format` Regra 6).
3. Steps em terceira pessoa, voz ativa, presente — em linguagem de domínio (per `codex-bdd` Seção 6).
4. `Then` sempre com resultado **observável** (não "a operação acontece").
5. Para variações ≥ 3 do mesmo trio, usar `Scenario Outline` + `Examples`.
6. Aplicar tags: ≥ 1 `@AC-{N}` + exatamente 1 tag de tipo (per `lex-bdd-gherkin-format` Regra 4).

### Passo 7: Auto-lint (regex do codex-gherkin)

Antes de salvar, varrer o conteúdo dos passos contra o conjunto de regex em `codex-gherkin` Seção 12:

```
Proibido em qualquer step:
- métodos HTTP + path
- status codes (numéricos ou nomeados)
- nomes de função/método com parênteses
- SQL (SELECT, INSERT INTO, UPDATE)
- caminhos de implementação (src/, app/, etc.)
- seletores CSS/XPath
- extensões de arquivo de código

Obrigatório por cenário:
- @AC-\d+ (≥ 1)
- @(happy-path|alternative|edge|error|nfr) (exatamente 1)
- SCN-\d+ único no arquivo
```

Violação → reescrever o passo em linguagem de negócio antes de prosseguir. Não salvar arquivo com violação.

### Passo 8: Compor 07-bdd-scenarios.md

Estrutura final do arquivo:

```yaml
---
issue: {n}
repo: {owner/repo}
generated_at: "{ISO-8601}"
generated_by: warrior-themis
sources:
  github_issue: "{owner/repo}#{n}"
  notion_pages:
    - "{URL página 1}"
  flow_artifacts:
    - docs/issues/issue-{n}/01-brief.md
    - docs/issues/issue-{n}/02-requirements.md
    - docs/issues/issue-{n}/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2, SCN-3]
---
```

Bloco Gherkin abaixo, com `# language: <lang>` quando o idioma não for `en`.

Quando há > 3 Features ou > 30 cenários, dividir per `codex-gherkin` Seção 2 em `scenarios/*.feature` e manter `07-bdd-scenarios.md` apenas como índice + frontmatter.

### Passo 9: Tratar ambiguidades

Se uma AC não permite escrever cenário a partir das fontes:

1. **NÃO** consultar código (per `lex-bdd-spec-only-sources` Regra 4).
2. Listar a ambiguidade em comentário na Issue (via `kata-mcp-github-write` se disponível, senão pedir que o orquestrador o faça).
3. Marcar a AC no frontmatter como bloqueada:

```yaml
ac_coverage:
  - ac: AC-3
    scenarios: []
    status: BLOCKED
    blockers:
      - "Falta definir o que acontece quando o cliente já tem um agendamento ativo para a mesma data"
```

4. Não inventar o cenário. A Issue precisa ser complementada antes do Gate 3 passar.

### Passo 10: Persistir e atualizar checkpoint

1. Criar `docs/issues/issue-{n}/` se não existir.
2. Salvar `07-bdd-scenarios.md` (e arquivos `scenarios/*.feature` quando aplicável).
3. Atualizar `.ahrena/workflow/issue-{n}/checkpoint.md` com YAML front-matter (per `lex-issue-driven` Regra 7):
   - `phase_completed: 8.1`
   - `phase_next: 8.2`
   - artefato sob `artifacts.bdd_scenarios`
   - timestamp em `updated_at`

### Passo 11: Validação Final

Antes de devolver o controle ao orquestrador, conferir:

- [ ] Frontmatter declara apenas fontes permitidas (sem caminhos sob `src/`, `tests/`, etc.).
- [ ] `ac_coverage` lista todas as ACs do `02-requirements.md` (com `scenarios` ou `status: BLOCKED`).
- [ ] Cada cenário tem id `SCN-{N}` único.
- [ ] Cada cenário tem ≥ 1 `@AC-{N}` e exatamente 1 tag de tipo.
- [ ] Auto-lint passa em todos os cenários.
- [ ] Cenários com requisito negativo têm `@error`; cenários com fronteira têm `@edge`.
- [ ] Idioma do bloco Gherkin é consistente em todo o arquivo.
- [ ] Checkpoint atualizado.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Cenários consolidados | Markdown + Gherkin | `docs/issues/issue-{n}/07-bdd-scenarios.md` |
| Cenários por Feature (split opcional) | `.feature` | `docs/issues/issue-{n}/scenarios/*.feature` |
| Comentário na Issue (quando há ambiguidade) | GitHub comment | Issue `{repo}#{n}` |
| Checkpoint atualizado | Markdown YAML | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Resumo ao orquestrador | Texto estruturado | Resposta ao `warrior-themis` / `warrior-athena` |

## Restrições

- **Cego para código:** nunca abrir arquivos sob `src/`, `app/`, `lib/`, `pkg/`, `internal/`, `tests/`, `spec/`, `cypress/`, `e2e/`, etc., nem executar `grep`/`find` sobre eles (per `lex-bdd-spec-only-sources`).
- **Sem step-runner:** o output é documentação; não criar arquivos `step_definitions/`, `behave.ini`, etc. (per `lex-bdd-no-framework-coupling`).
- **Sem cenário imperativo:** nada de seletores de UI, status codes, nomes de função/tabela (per `lex-bdd-gherkin-format`).
- **Sem invenção:** se a Issue não permite escrever o cenário, o agente bloqueia a AC e devolve à origem; não consulta código nem deduz comportamento.
- **Linguagem ubíqua:** quando o cenário toca domínio core (transferência, conciliação, lançamento contábil), usar os termos do modelo de domínio (`warrior-theseus`, Event Storm).

## Referências

- `lex-bdd-spec-only-sources` — fontes permitidas
- `lex-bdd-gherkin-format` — formato declarativo
- `lex-bdd-no-framework-coupling` — sem step-runner
- `codex-bdd` — princípios e taxonomia
- `codex-gherkin` — sintaxe e padrões
- `lex-issue-driven` — fluxo Issue-Driven (Fase 8)
- `kata-bdd-validate-implementation` — etapa seguinte (Fase 8.2)
- `kata-mcp-github-read`, `kata-mcp-notion-read` — leitura via MCP
- `warrior-themis` — agente que invoca este Kata
