# Kata: Gate de Qualidade (Gate 2)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 6 do fluxo Issue-Driven — validação final com 7 checks que incluem rastreabilidade AC↔teste, scope creep, best practices, testes, cobertura, tipos e performance budget

## Objetivo

Executar o Gate 2 do fluxo Issue-Driven: 7 verificações stack-aware sobre a implementação concluída na Fase 4 (e revisada pela Fase 5). Produz relatório `go`/`no-go`/`unverifiable` em `.ahrena/issues/{n}/06-quality-report.md`. Qualquer falha retorna à Fase 4 com contexto detalhado; apenas `go` permite avançar à Fase 7. Checks individuais que não podem ser executados no ambiente atual (ferramenta ausente, sem arquivos aplicáveis) reportam `unverifiable` e aparecem ao humano em vez de passar silenciosamente.

Esta kata é a **guardiã da qualidade** do fluxo — garante que a implementação cobre todos os ACs, não ultrapassou o escopo, aplicou as best practices definidas nas Lexis, e não regrediu performance além dos budgets declarados.

## Quando Usar

- Fase 6 do fluxo orquestrado por `warrior-athena`, após `kata-security-review` resultar em `approved`
- Quando é necessário validar rigorosamente uma implementação antes de abrir PR

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Requisitos Fase 2 | Sim | `.ahrena/issues/{n}/02-requirements.md` (ACs numerados) |
| Arquitetura Fase 3 | Sim | `.ahrena/issues/{n}/03-architecture.md` (tabela de componentes — escopo) |
| Implementação Fase 4 | Sim | Código + testes no working tree |
| Revisão Fase 5 | Sim | `.ahrena/issues/{n}/05-security-review.md` (deve estar `approved`) |
| Coverage threshold | Não | `quality.coverage_threshold` em `.directives` (padrão: 80) |
| Stack | Sim | Linguagem do código implementado (detectado via arquivos tocados) |

## Workflow

```
Progresso:
- [ ] 1. Coletar contexto (ACs, escopo, diff, stack)
- [ ] 2. Check 1 — Rastreabilidade AC ↔ teste (bidirecional)
- [ ] 3. Check 2 — Scope creep
- [ ] 4. Check 3 — Best practices (Lexis aplicáveis por stack)
- [ ] 5. Check 4 — Testes executados
- [ ] 6. Check 5 — Cobertura
- [ ] 7. Check 6 — Tipos
- [ ] 8. Check 7 — Performance budget
- [ ] 9. Consolidar resultado go/no-go/unverifiable
- [ ] 10. Persistir em .ahrena/issues/{n}/06-quality-report.md
- [ ] 11. Atualizar checkpoint
```

### Passo 1: Coletar contexto

1. Ler ACs de `02-requirements.md` (extrair `AC-1`, `AC-2`, ...).
2. Ler tabela de componentes de `03-architecture.md` (extrair lista de arquivos previstos).
3. Executar `git diff --name-only {base}...HEAD` para lista de arquivos modificados.
4. Detectar stack (`*.py` → Python; `*.ts` → Node/TS; etc.).
5. Ler `quality.coverage_threshold` de `.ahrena/.directives` (padrão: `80`).
6. **Detectar modo de execução** lendo o front-matter de `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - Se `stack.approved: true` está presente, modo é **por camada** (ver seção dedicada abaixo); identificar a camada corrente (`stack.decomposition[i].status: in-progress`) e filtrar `covers_acs` + `components`.
   - Caso contrário, modo é **PR único** (comportamento padrão; passos 2-8 rodam sobre o conjunto completo de ACs e componentes).

### Modo por camada (Stacked PRs)

Quando o checkpoint contém `stack.approved: true`, esta kata é invocada **uma vez por camada** antes da camada submeter seu PR. Cada execução opera sobre subsets, não sobre o conjunto completo:

| Check | Escopo no modo por camada |
|---|---|
| Check 1 — AC ↔ teste | Filtrar pelo subset `stack.decomposition[i].covers_acs`. ACs fora da camada **não** são avaliados nesta execução; aparecerão em camada posterior |
| Check 2 — Scope creep | Comparar arquivos modificados desde a camada anterior contra `stack.decomposition[i].components` (não contra a tabela completa da Fase 3) |
| Check 3 — Best practices | Aplicar Lexis sobre arquivos modificados na camada corrente (mesmas regras; escopo menor) |
| Check 4 — Testes | Executar suíte completa (testes não são particionáveis por camada com segurança) |
| Check 5 — Cobertura | Avaliar contra threshold sobre o conjunto completo do diff até a camada corrente (acumulado base→camada N) |
| Check 6 — Tipos | Mesma regra; escopo = arquivos da camada |
| Check 7 — Performance budget | Mesma regra; aplicar quando a camada toca código sensível a performance |

**Transição de status:**
- A camada começa em `pending` e Athena promove para `in-progress` ao iniciar Fase 4 daquela camada.
- Quando os 7 checks retornam ✅ para a camada, esta kata atualiza `stack.decomposition[i].status: submitted` no checkpoint.
- Após o PR da camada ser mergeado, Athena (ou `kata-stacked-pr-merge`) atualiza para `merged`.

**Validação agregada final:** disparada automaticamente ao **final da execução da última camada** — ou seja, na mesma invocação de `kata-quality-gate` que promove a última camada `pending` para `submitted`. Depois que os 7 checks com escopo da camada retornam ✅, a kata roda uma passada agregada adicional que confirma:
1. Toda AC numerada na Fase 2 foi coberta por **alguma** camada (sem AC órfão).
2. Todo componente declarado na Fase 3 foi tocado por **alguma** camada (sem componente órfão).

Se a validação agregada falhar, o resultado geral da camada é rebaixado para `no-go` e o relatório aponta os elementos órfãos. Em fluxo PR único (sem `stack`), a validação agregada é trivialmente equivalente ao Check 1 do conjunto completo e não gera passada extra.

### Passo 2: Check 1 — Rastreabilidade AC ↔ teste (bidirecional)

**AC → Teste:**
1. Para cada AC identificado no Passo 1, buscar em arquivos de teste (via regex) por:
   - Nome contendo `AC_{N}` ou `AC-{N}`
   - Docstring contendo `AC-{N}`
   - Marker `@pytest.mark.ac("AC-{N}")` ou equivalente
2. Cada AC deve ter pelo menos 1 teste correspondente.
3. ACs sem teste → ❌ `Check 1 — AC→Test`.

**Teste → AC:**
1. Para cada teste novo/modificado no diff, verificar se referencia pelo menos um AC.
2. Testes sem AC referenciado → ❌ `Check 1 — Test→AC` (indica scope creep).

Resultado do Check 1: ✅ se ambas as direções estão completas; ❌ caso contrário.

### Passo 3: Check 2 — Scope creep

1. Comparar lista de arquivos modificados (Passo 1) com tabela de componentes da Fase 3.
2. Arquivos fora da tabela → candidatos a scope creep.
3. **Exceções legítimas** (não flagar):
   - Arquivos de teste correspondentes a componentes declarados (ex.: se `service.py` está na tabela, `test_service.py` é implícito).
   - Arquivos de configuração automática (ex.: `requirements.lock`, `yarn.lock`).
   - Documentação gerada pelo próprio fluxo (ex.: `.ahrena/issues/{n}/*`).
4. Funções/classes públicas novas em arquivos tocados que não mapeiam a nenhum AC → flagar.

Resultado do Check 2: ✅ se só arquivos declarados + exceções foram modificados; ❌ se há scope creep não justificado.

Se ❌: **opções apresentadas ao usuário**:
- (a) Ampliar ACs (retornar a Fase 2/3 e reexecutar Gate 1).
- (b) Reverter código fora de escopo e abrir nova issue para ele.

### Passo 4: Check 3 — Best practices (Lexis aplicáveis)

Selecionar Lexis aplicáveis ao stack e executar a verificação de cada:

**Python (`*.py` no diff):**

| Lexis | Verificação | Comando / Heurística |
|---|---|---|
| `lex-python-typing` | Sem erros de tipo | `mypy --strict {arquivos-tocados}` |
| `lex-python-testing` | Funções públicas testadas | Para cada função pública nova/modificada, procurar teste que a chama |
| `lex-python-security` | Sem credenciais hardcoded | Regex por padrões de credencial |
| `lex-python-immutability` | Sem mutação em estruturas compartilhadas | Análise estática (ast): mutação em parâmetros ou globais |
| `lex-python-error-handling` | Sem `except: pass` ou swallowing | Regex por `except` sem re-raise e sem log |
| `lex-conventional-commits` | Commits no formato correto | `git log {base}..HEAD --format=%s` + regex `^(feat\|fix\|chore\|docs\|refactor\|test\|build\|ci)(\(.+\))?: .+` |

Registrar violações com arquivo/linha. Qualquer violação → ❌ `Check 3 — {lex-name}`.

### Passo 5: Check 4 — Testes executados

1. Executar comando de teste detectado pelo stack:
   - Python: `pytest`
   - Node/TS: `yarn test` (ou `npm test` conforme `.directives`)
2. Capturar exit code e output.
3. Qualquer falha → ❌ `Check 4 — Tests`.

### Passo 6: Check 5 — Cobertura

1. Executar teste com coverage:
   - Python: `pytest --cov={pacote} --cov-report=term-missing`
2. Extrair percentual de cobertura total.
3. Comparar com `quality.coverage_threshold` (padrão: 80).
4. `% < threshold` → ❌ `Check 5 — Coverage ({%}% < {threshold}%)`.

### Passo 7: Check 6 — Tipos

1. Executar verificador de tipos específico do stack:
   - Python: `mypy --strict` sobre pacotes modificados
   - TS: `tsc --noEmit`
2. Capturar erros.
3. Erros novos (em arquivos modificados neste PR) → ❌ `Check 6 — Types`.
4. Erros pré-existentes em arquivos não modificados → não bloquear (registrar como nota).

### Passo 8: Consolidar resultado go/no-go

1. Se todos os 6 checks ✅ → resultado `go`.
2. Se qualquer check ❌ → resultado `no-go`.

Para cada ❌, registrar:
- Qual check falhou
- Detalhes (arquivos, linhas, comandos, output)
- Recomendação de correção

### Passo 9: Persistir em `.ahrena/issues/{n}/06-quality-report.md`

Estrutura:

```markdown
# Quality Gate — Issue #{n}: {título}

- **Referências:** [Requisitos](./02-requirements.md) · [Arquitetura](./03-architecture.md) · [Segurança](./05-security-review.md)
- **Data:** {YYYY-MM-DD}
- **Resultado:** {✅ go | ❌ no-go}

## Matriz de Rastreabilidade AC ↔ Teste

| AC | Descrição | Testes que cobrem | Status |
|---|---|---|:-:|
| AC-1 | ... | `test_foo_AC_1`, `test_bar_AC_1` | ✅ |
| AC-2 | ... | `test_baz_AC_2` | ✅ |
| AC-3 | ... | — | ❌ |

### Testes sem AC referenciado (candidatos a scope creep)

- `test_helper_utility` em `tests/test_utils.py:42` — {recomendação}

## Resultado por Check

| # | Check | Status | Detalhes |
|:-:|---|:-:|---|
| 1 | Rastreabilidade AC ↔ Teste | {✅/❌} | {resumo} |
| 2 | Scope Creep | {✅/❌} | {resumo} |
| 3 | Best Practices | {✅/❌} | {resumo} |
| 4 | Testes Executados | {✅/❌} | {resumo} |
| 5 | Cobertura | {✅/❌} | {atual}% / {threshold}% |
| 6 | Tipos | {✅/❌} | {resumo} |

## Detalhes das Falhas

### Check {n}: {nome}

{descrição detalhada, arquivos, linhas, output do comando}

**Recomendação:** {como corrigir}

## Conclusão

- Se `go`: seguir para Fase 7 (`kata-pr-prepare`).
- Se `no-go`: retornar à Fase 4 com as correções acima.
```

### Passo 10: Atualizar checkpoint

1. Atualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase concluída: 6
   - resultado: `go` ou `no-go`
   - Se `go`: próxima fase = 7
   - Se `no-go`: próxima fase = 4 (retornar para correções)
   - **Modo por camada:** atualizar adicionalmente `stack.decomposition[i].status` da camada corrente — `submitted` quando `go`; manter `in-progress` quando `no-go`. A `phase_next` permanece em 4 enquanto houver camada pendente.
2. Informar ao `warrior-athena`:
   - Se `go` (PR único): avançar para `kata-contributing-pr` (conforme Regra 12 de `lex-issue-driven`).
   - Se `go` (modo por camada): liberar a camada para submissão via `kata-stacked-pr-create`; se ainda houver camada pendente, retornar à Fase 4 para a próxima.
   - Se `no-go`: apresentar relatório ao humano e aguardar direção (corrigir ou ampliar ACs).

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Relatório do Gate | Markdown com 6 checks + matriz de rastreabilidade | `.ahrena/issues/{n}/06-quality-report.md` |
| Resultado | `go` / `no-go` | Retorno ao orquestrador |
| Checkpoint atualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrições

- **Checks são executados, não simulados:** `pytest`, `mypy`, coverage e scans são comandos reais; a kata não pode "marcar como passado" sem execução efetiva.
- **Ordem dos checks é mandatória:** checks 1-3 (análise estática) antes de 4-6 (execução); se análise falha, ainda executar os demais para reportar panorama completo.
- **Threshold configurável mas não opcional:** `quality.coverage_threshold` pode ser ajustado em `.directives`, mas Check 5 é sempre executado.
- **Sem override para `no-go`:** a única saída legítima de `no-go` é corrigir a implementação ou renegociar os ACs (via Gate 1). Nenhum humano ou agente pode marcar como `go` manualmente.
- **Destino fixo:** `.ahrena/issues/{n}/06-quality-report.md` (conforme `lex-issue-driven`). No modo por camada, o relatório acumula uma seção por camada e uma seção final agregada.
- **Subset por camada não relaxa critérios:** o filtro de ACs/componentes apenas reduz o escopo da execução; thresholds (cobertura, performance) e estritude dos checks permanecem idênticos.

## Referências

- `lex-issue-driven` — leis do fluxo, em particular as regras de rastreabilidade, scope creep e a Regra 11 (Gate 2 por camada quando há stack aprovada)
- `codex-issue-workflow` — detalhamento completo dos 7 checks
- `codex-stacked-prs` — modelo conceitual e Decision Checklist para stacked PRs
- `kata-stacked-pr-create` — invocado pela Fase 7 quando há stack aprovada
- `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-immutability`, `lex-python-error-handling`, `lex-conventional-commits` — Lexis verificadas no Check 3
