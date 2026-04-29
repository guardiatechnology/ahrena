# Kata: Validação BDD da Implementação

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Qualidade. Segunda metade da Fase 8 do fluxo Issue-Driven. Mapeia cada cenário Gherkin de `07-bdd-scenarios.md` aos testes existentes no repositório e reporta gaps.

## Objetivo

Produzir `docs/issues/issue-{n}/08-bdd-validation-report.md` com o mapeamento `SCN-{N}` ↔ testes existentes, detectar lacunas de cobertura, verificar a ausência de step-runner BDD nos manifestos e emitir decisão `go | no-go` para o Gate 3 (`kata-quality-gate` Check 8). **Este Kata pode ler código** — esta é exatamente sua função; a restrição "cego para código" aplica-se apenas ao desenho de cenários (Fase 8.1).

## Quando Usar

- Fase 8.2 do fluxo orquestrado por `warrior-athena`/`warrior-themis`, **após** `kata-bdd-scenarios-design` concluir.
- Sob demanda para auditoria de cobertura BDD em features já implementadas.

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `issue_number` | Sim | Número da issue (ex.: `42`) |
| `repo` | Sim | `owner/repo` |
| `07-bdd-scenarios.md` | Sim | Artefato da Fase 8.1; falha se ausente ou mal-formado |
| Manifestos do projeto | Sim (no repositório) | `pyproject.toml`, `package.json`, `go.mod`, etc. |
| Suite de testes | Sim (no repositório) | `tests/`, `__tests__/`, `spec/`, equivalente da stack |

## Workflow

```
Progresso:
- [ ] 1. Verificar pré-condições (Fase 8.1 concluída e sem ACs bloqueadas)
- [ ] 2. Parsear 07-bdd-scenarios.md
- [ ] 3. Indexar testes do repositório (somente leitura)
- [ ] 4. Classificar cada cenário (covered | partial | missing)
- [ ] 5. Verificar acoplamento a framework BDD
- [ ] 6. Compor 08-bdd-validation-report.md
- [ ] 7. Emitir decisão go | no-go
- [ ] 8. Atualizar checkpoint
- [ ] 9. Validação final
```

### Passo 1: Verificar pré-condições

1. Confirmar `docs/issues/issue-{n}/07-bdd-scenarios.md` presente.
2. Confirmar frontmatter bem-formado: `sources`, `ac_coverage`, `generated_by: warrior-themis`.
3. Verificar que nenhuma AC está com `status: BLOCKED` no `ac_coverage`. Se houver bloqueio, parar e devolver à Fase 8.1 (a Issue precisa ser complementada antes que o Gate 3 possa passar).
4. Verificar que `sources` declara apenas caminhos permitidos (sem `src/`, `tests/`, etc.). Se viola, falhar e exigir regeneração da Fase 8.1.

### Passo 2: Parsear 07-bdd-scenarios.md

1. Extrair lista de cenários: para cada cenário, registrar `id (SCN-{N})`, tags AC (`@AC-{N}`), tag de tipo (`@happy-path` etc.), título.
2. Construir mapa `SCN → AC[]` e mapa inverso `AC → SCN[]`.
3. Validar unicidade do `SCN-{N}` no arquivo. Conflito = falha de pré-condição (regenerar Fase 8.1).

### Passo 3: Indexar testes do repositório

Esta etapa **pode** abrir arquivos sob `tests/`, `__tests__/`, `spec/`, etc. Sem executar testes — apenas descoberta estática.

1. Determinar diretórios de teste convencionais da stack:
   - Python: `tests/`, `tests/unit/`, `tests/integration/`, `tests/e2e/`
   - JS/TS: `__tests__/`, `tests/`, `e2e/`, `cypress/`, `playwright/`
   - Go: arquivos `*_test.go`
   - Java: `src/test/java/`
2. Para cada arquivo de teste, varrer:
   - Nomes de funções/`it`/`describe` em busca de `SCN-{N}` (regex `SCN[-_ ]?\d+`).
   - Docstrings/JSDoc/comentários imediatamente antes da função em busca da mesma referência.
3. Construir mapa `SCN → [test_path:line, ...]`.
4. Para cada caminho de teste descoberto, registrar nível inferido pelo diretório (unit | integration | e2e).

### Passo 4: Classificar cada cenário

Para cada `SCN-{N}` da Fase 8.1:

| Classificação | Critério |
|---|---|
| **covered** | ≥ 1 teste referencia `SCN-{N}` **e** o nível é compatível com a tag de tipo |
| **partial** | Teste referencia `SCN-{N}` **mas** o nível é insuficiente para o tipo do cenário (ver tabela abaixo), ou apenas parte do `Then` é asserida |
| **missing** | Nenhum teste referencia `SCN-{N}` |

**Compatibilidade nível ↔ tipo:**

| Tag de tipo | Nível compatível |
|---|---|
| `@happy-path` | unit OR integration OR e2e (qualquer um, conforme `lex-test-pyramid`) |
| `@alternative` | unit OR integration |
| `@edge` | unit OR integration |
| `@error` | unit OR integration |
| `@nfr` (latência, idempotência, disponibilidade) | integration OR e2e (unit puro não observa NFR real) |

Se cenário `@nfr` cobre apenas teste unit → `partial` com recomendação de subir nível.

### Passo 5: Verificar acoplamento a framework BDD

1. Varrer manifestos contra a lista proibida de `lex-bdd-no-framework-coupling` Regra 4:
   - Python: `pyproject.toml`, `requirements*.txt`, `Pipfile`, `setup.py` → procurar `behave`, `pytest-bdd`, `lettuce`, `radish-bdd`.
   - JS/TS: `package.json` (deps + devDeps) → procurar `cucumber`, `cucumber-js`, `@cucumber/cucumber`, `jest-cucumber`, `cypress-cucumber-preprocessor`.
   - Go: `go.mod` → procurar `godog`.
   - Java: `pom.xml`, `build.gradle` → procurar `cucumber-jvm`.
   - .NET: `*.csproj` → procurar `specflow`, `reqnroll`.
2. Varrer estrutura de diretórios:
   - Existência de `features/` ou `tests/features/` consumida por runner.
   - Existência de `step_definitions/`, `steps/`, `support/world.js` ligados a cenários.
   - Decoradores/anotações `@given`/`@when`/`@then`/`@step` em arquivos de teste.
3. Registrar resultado: `clean` (nenhuma violação) ou `violations: [...]` (lista das ocorrências).

Adicionalmente, se um teste valida um cenário sem referência `SCN-{N}` (mesmo que o teste seja correto), registrar como **violação de rastreabilidade** — não impede go, mas vai como nota na seção de gaps.

### Passo 6: Compor 08-bdd-validation-report.md

Estrutura:

```yaml
---
issue: {n}
repo: {owner/repo}
generated_at: "{ISO-8601}"
generated_by: warrior-themis
scenarios_total: 12
covered_count: 9
partial_count: 2
missing_count: 1
framework_coupling: clean   # ou: violations
gate_3_decision: go | no-go
---
```

Conteúdo:

```markdown
# Relatório de Validação BDD — Issue #{n}

## Resumo

- Total de cenários: 12
- Cobertos: 9
- Parciais: 2
- Faltantes: 1
- Acoplamento a framework BDD: limpo

## Mapeamento Cenário ↔ Teste

| SCN | AC | Tipo | Status | Testes |
|---|---|---|---|---|
| SCN-1 | AC-1 | @happy-path | covered | tests/integration/test_transfer_scheduling.py:23 |
| SCN-2 | AC-2 | @alternative | covered | tests/integration/test_transfer_scheduling.py:48 |
| SCN-3 | AC-3 | @error | covered | tests/integration/test_transfer_scheduling.py:71 |
| SCN-4 | AC-3 | @edge | partial | tests/unit/test_transfer_rules.py:15 (apenas borda inferior) |
| SCN-5 | AC-4 | @nfr | partial | tests/unit/test_balance_query.py:8 (cobre só lógica, não latência observável) |
| SCN-6 | AC-5 | @nfr | missing | — |

## Gaps (itens no-go)

### SCN-4 — partial (cobertura parcial)
- **AC:** AC-3
- **O que cobre hoje:** borda inferior (saldo igual ao valor)
- **O que falta:** borda superior (saldo igual ao valor + taxa)
- **Nível recomendado:** integration
- **Responsável sugerido:** warrior-apollo

### SCN-5 — partial (nível insuficiente)
- **AC:** AC-4 (@nfr — latência)
- **O que cobre hoje:** lógica unitária da query
- **O que falta:** assert observável de latência
- **Nível recomendado:** integration com medição
- **Responsável sugerido:** warrior-apollo

### SCN-6 — missing
- **AC:** AC-5 (@nfr — idempotência)
- **Nível recomendado:** integration
- **Responsável sugerido:** warrior-apollo

## Verificação de Acoplamento a Framework

- pyproject.toml: ✓ sem step-runner
- package.json: ✓ sem step-runner
- features/: ✓ ausente
- step_definitions/: ✓ ausente

## Decisão para o Gate 3

**no-go**

Razão: 1 cenário faltante (SCN-6) + 2 parciais (SCN-4, SCN-5).

## Próximas Ações

| Gap | Ação | Responsável | Nível | Iteração |
|---|---|---|---|---|
| SCN-6 | Criar teste integration validando idempotência da operação | warrior-apollo | integration | next |
| SCN-5 | Adicionar teste integration medindo latência observável | warrior-apollo | integration | next |
| SCN-4 | Estender teste existente para cobrir borda superior | warrior-apollo | integration | next |
```

### Passo 7: Emitir decisão go | no-go

- **go**: `missing_count == 0`, `partial_count == 0`, `framework_coupling == clean`.
- **no-go**: qualquer outra combinação. Listar próximas ações com responsável (warrior) e nível (per `codex-test-strategy`).

### Passo 8: Atualizar checkpoint

Atualizar `.ahrena/workflow/issue-{n}/checkpoint.md` com:

```yaml
phase_completed: 8.2
phase_next: 6.b   # se go: voltar ao Quality Gate (Check 8)
                  # se no-go: aguardando warrior-apollo/hephaestus/iris implementar gaps
artifacts:
  bdd_validation_report: docs/issues/issue-{n}/08-bdd-validation-report.md
gate_3:
  status: go | no-go
  last_run_at: "{ISO-8601}"
updated_at: "{ISO-8601}"
```

### Passo 9: Validação Final

Antes de devolver controle:

- [ ] Todos os `SCN-{N}` da Fase 8.1 aparecem no mapeamento.
- [ ] Cada cenário `partial` ou `missing` tem ação recomendada com responsável e nível.
- [ ] Verificação de acoplamento a framework está completa (todos os manifestos varridos).
- [ ] Decisão `go | no-go` é coerente com o conteúdo do relatório.
- [ ] Checkpoint atualizado.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Relatório de validação | Markdown YAML + tabelas | `docs/issues/issue-{n}/08-bdd-validation-report.md` |
| Decisão Gate 3 | `go` ou `no-go` | Resposta ao orquestrador + checkpoint |
| Lista de próximas ações | Tabela | Seção do relatório |
| Checkpoint atualizado | Markdown YAML | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrições

- **PODE ler código:** descoberta estática de testes faz parte do objetivo deste Kata. A restrição "cego para código" aplica-se apenas a `kata-bdd-scenarios-design` (Fase 8.1).
- **NÃO PODE executar testes:** descoberta é estática (parsing de nomes/docstrings); validação de execução fica para o `kata-quality-gate` Check 1.
- **NÃO PODE modificar testes:** quando há gap, o Kata reporta. A implementação dos testes faltantes fica para `warrior-apollo`/`warrior-hephaestus`/`warrior-iris` em iteração subsequente.
- **NÃO PODE inferir cobertura sem referência `SCN-{N}`:** se um teste valida o comportamento sem referenciar o cenário, é violação de `lex-bdd-no-framework-coupling` Regra 3 — registra-se como nota, mas não conta como cobertura.
- **DEVE bloquear o gate** quando manifesto declara step-runner BDD ou diretório `features/` consumido por runner é encontrado.

## Referências

- `lex-bdd-no-framework-coupling` — proibições de framework e regras de rastreabilidade
- `lex-bdd-gherkin-format` — formato dos cenários parseados
- `codex-bdd` — princípios e taxonomia
- `codex-gherkin` — sintaxe esperada
- `codex-test-strategy` — escolha de níveis para gaps
- `lex-test-pyramid` — distribuição de níveis
- `kata-bdd-scenarios-design` — etapa anterior (Fase 8.1)
- `kata-quality-gate` — Check 8 consome o `gate_3_decision` deste relatório
- `lex-issue-driven` — fluxo Issue-Driven (Fase 8 e Gate 3)
- `warrior-themis` — agente que invoca este Kata
