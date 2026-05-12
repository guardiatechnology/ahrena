---
plan_id: "024"
title: "examples-as-codex-companion"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T23:30:00Z"
updated_at: "2026-05-07T23:30:00Z"
---

# Plano: Exemplos como codex companion — extrair `## Examples` de Lexis para arquivos lazy-loaded

## Objetivo

Reduzir o footprint de Lexis carregadas eagerly extraindo a seção `## Examples` (correto + incorreto) para um arquivo codex companion `codex-examples-{lex-name}.md` carregado lazily. Lex original mantém pointer curto: "Para exemplos canônicos, veja `codex-examples-{name}`". Em uma Lex típica de ~100 linhas onde Examples ocupa 30-50 linhas, essa extração corta 30-50% da Lex carregada toda vez. Para humano lendo o site MkDocs, exemplos continuam acessíveis via link; para agente que já internalizou o pattern, exemplos não consomem tokens em todo carregamento.

## Contexto

### Diagnóstico (medido nos artefatos atuais)

Amostra de 5 Lexis representativas:

| Lex | Linhas total | Linhas em `## Examples` | % | Reduzível |
|---|--:|--:|--:|---|
| `lex-logging-decorator` | 75 | 38 (correto) + 26 (incorreto) = 64 | 85% | Sim — Examples dominam |
| `lex-python-result-type` | 56 | 18 + 14 = 32 | 57% | Sim |
| `lex-frontend-accessibility` | 90 | 0 explícito (rules tem exemplos inline) | 0% | Não — diferente padrão |
| `lex-conventional-commits` | 75 | 13 + 12 = 25 | 33% | Sim |
| `lex-protected-trunk` | 90 | 22 + 17 = 39 | 43% | Sim |

**Conclusão:** Lexis com seção `## Examples` clara (90% do framework) ganham 30-85% de redução. Lexis com exemplos inline em rules são minoria — codex documenta como caso especial.

### Por que codex companion (não inline trim, não excluir exemplos)

| Alternativa | Pro | Contra |
|---|---|---|
| **Codex companion** ✅ | Lex curta eagerly; exemplos lazy via `paths:`; humano segue link no site; agente carrega sob demanda | Split em 2 arquivos para mesma "unit" mental |
| Excluir exemplos da Lex | Maior redução | Perde valor pedagógico; humanos perdidos sem exemplos |
| Trim parcial (deixar 1-2 exemplos) | Compromisso | Decidir quais ficar é arbitrário; manutenção dupla |
| Mover para wiki externo | Simples | Sai do framework versionado; quebra single source |

Codex companion preserva todos os exemplos (zero perda), só muda o **carregamento**.

### Como o lazy-load funciona aqui

```yaml
# framework/platforms.yaml
cursor:
  rules:
    _foundation/quality/lexis/lex-logging-decorator:
      description: "..."
      alwaysApply: false
      # Lex carrega quando description matches OR quando glob abaixo bate

  docs:  # codex companions vão para `docs` (lazy section)
    _foundation/quality/codex/codex-examples-lex-logging-decorator:
      description: "Canonical correct/incorrect examples for lex-logging-decorator"
      paths: ["**/*.py", "**/*.ts", "**/*.go"]  # carrega quando code é tocado
```

Resultado: Lex carrega quando agente precisa entender a regra. Exemplos carregam quando agente está realmente escrevendo código (paths que disparam).

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Onde mora o companion | Mesmo subclade da Lex, em `codex/` | E.g., `_foundation/quality/lexis/lex-logging-decorator.md` → `_foundation/quality/codex/codex-examples-lex-logging-decorator.md` |
| Naming pattern | `codex-examples-{full-lex-name}` (preserva prefix `lex-`) | Resolve direto para a Lex de origem; sem ambiguidade |
| Frontmatter | Mínimo (só `description`) — companion é puro conteúdo de exemplo | Reduz ruído |
| Conteúdo do companion | Apenas seções `## Correct` (ou `### Correct`) e `## Incorrect`; sem prose adicional, sem repetição da Law | Exemplos são auto-explicativos referenciando a Lex |
| Pointer na Lex | `## Examples` substituída por: "Para exemplos canônicos correto/incorreto, ver `codex-examples-{name}`" | 2 linhas em vez de 30-50 |
| Migration de Lexis existentes | Onda 2 — não obriga refactor imediato | Plan-024 entrega ferramentas; backfill em sub-PRs separados (provavelmente automatizáveis via script) |
| Aplicação a Lexis novas | A partir de plan-024 mergeado, novas Lexis criadas via `kata-create-lexis` MUST criar par Lex + companion quando há seção Examples | Forcing function via kata |
| Validador (plan-019) | Novo módulo: para cada Lex com regra prescritiva (heurística), checa se existe companion correspondente; warning-only inicial | Detecta drift |
| `kata-artifact-self-review` | Estendida: ao revisar Lex, também revisa companion se existir | Coerência |
| Idiomas | 3 (companion segue mesmo padrão de tradução da Lex pai) | `lex-framework-language` |
| MCP integration | Tool `ahrena_query_examples(lex_name, lang)` retorna o companion | Sinérgico com plan-021 |

## Escopo

### Artefatos a criar (3 idiomas)

| Pilar | Caminho relativo | Conteúdo principal |
|---|---|---|
| Codex | `_foundation/quality/codex/codex-examples-pattern.md` (3 idiomas) | Conceito de companion; convenção de naming; estrutura mínima do companion (frontmatter + ## Correct + ## Incorrect); quando usar inline (Lexis curtas com exemplo único) vs companion (Lexis com múltiplos exemplos); referência a `codex-token-optimization` (plan-022) como técnica #7 |
| Codex companion piloto | `_foundation/quality/codex/codex-examples-lex-logging-decorator.md` (3 idiomas) | Extração dos exemplos atuais de `lex-logging-decorator` para servir de **prova de conceito** e modelo |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `lex-logging-decorator.md` (3 idiomas) | Substituir seção `## Examples` por pointer (2 linhas); validar que comportamento eager/lazy continua coerente |
| `templates/lex-sample.md` (3 idiomas) | Acrescentar opção: seção `## Examples` pode (a) ser inline para Lexis curtas, ou (b) ser substituída por pointer para `codex-examples-{name}` quando volumosa. Documentar cada opção |
| `templates/codex-sample.md` (3 idiomas) | Acrescentar variante específica para `codex-examples-{lex-name}` (frontmatter mínimo, 2 seções) |
| `kata-create-lexis.md` (3 idiomas) | Adicionar step "Decidir Examples inline vs companion"; quando companion, criar par |
| `kata-artifact-self-review.md` (3 idiomas) | Acrescentar item: ao revisar Lex com pointer, revisar também o companion |
| `_foundation/quality/codex/codex-token-optimization.md` (criado em plan-022) | Adicionar técnica #7: "Examples as codex companion" |
| `scripts/_validate/examples_companion.py` (novo) | Heurística: Lex com regra prescritiva (HARD-GATE ou MUST/MUST NOT no Law) e comprimento > 80 linhas DEVERIA ter companion; warning |
| `scripts/validate.py` | Importar |
| `framework/platforms.yaml` | Registrar codex pattern + codex piloto + futura entry para cada companion criado em backfills |

### Migração de Lexis existentes (out of scope, mas documentada)

Companion criado para `lex-logging-decorator` neste plan serve de **modelo**. Backfill de outras Lexis fica em sub-PRs separados (não bloqueante). Codex `codex-examples-pattern` documenta o procedimento:

1. Identificar Lex com `## Examples` > 20 linhas
2. Criar `codex-examples-{lex-name}` extraindo as 2 subseções
3. Substituir seção na Lex por pointer
4. Atualizar `platforms.yaml`
5. Rodar `kata-artifact-self-review` em ambos
6. Sub-PR dedicado por Lex ou batch por subclade

Sub-PRs de backfill referenciam plan-024 como origem do pattern.

## Fora de escopo

- **Backfill em massa de Lexis existentes** — entrega só o piloto + ferramentas; backfill é onda 2 em sub-PRs
- **Examples em Codex existentes** — Codex já é lazy; sem ganho
- **Examples em Kata** — exemplos em Kata são parte do step (procedural); não extraíveis
- **Examples em Warrior (`Interaction Example`)** — parte da identity/persona; não extraíveis sem perder semântica
- **Examples em Cry** — tipicamente curtos; não vale companion
- **Geração automática de companion via script** — manual no piloto; tooling futuro pode automatizar
- **Companion compartilhado entre múltiplas Lexis** — 1:1 sempre; reuso fica como decisão de codex normal
- **Versionamento independente do companion** — companion segue a Lex pai; mudanças sincronizadas

## Steps

- [ ] 1. **Confirmar plan-022 mergeado** — companion é técnica adicional codificada lá; ordem importa para cross-reference
- [ ] 2. **Confirmar plan-019 mergeado** — `validate.py` para receber novo módulo
- [ ] 3. Abrir issue com template `feature-request`, Issue Type `Feature`, label `evolvability ♻️`, título "feat(framework): examples as codex companion (lazy-loaded examples for shorter Lexis)"
- [ ] 4. Criar branch `feat/{N}-examples-as-codex-companion` e worktree
- [ ] 5. Atualizar status deste plan para `in-progress`
- [ ] 6. Redigir `codex-examples-pattern.md` em pt-BR — explica conceito, naming, estrutura, decisão inline vs companion
- [ ] 7. **Criar companion piloto:** redigir `codex-examples-lex-logging-decorator.md` em pt-BR extraindo as duas subseções da Lex existente
- [ ] 8. **Refactor da Lex piloto:** substituir seção `## Examples` em `lex-logging-decorator.md` (pt-BR) por pointer de 2 linhas
- [ ] 9. Atualizar `templates/lex-sample.md` em pt-BR com a variante do pointer
- [ ] 10. Atualizar `templates/codex-sample.md` em pt-BR com variante `codex-examples-*`
- [ ] 11. Atualizar `kata-create-lexis.md` em pt-BR com step de decisão inline vs companion
- [ ] 12. Atualizar `kata-artifact-self-review.md` em pt-BR
- [ ] 13. Atualizar `codex-token-optimization.md` em pt-BR (adicionar técnica #7); se plan-022 ainda não mergeado, abrir TODO comment para inclusão futura
- [ ] 14. Implementar `scripts/_validate/examples_companion.py` + tests
- [ ] 15. Atualizar `scripts/validate.py` para importar o novo módulo
- [ ] 16. Atualizar `framework/platforms.yaml` (codex-examples-pattern + codex-examples-lex-logging-decorator + atualização da Lex piloto se entry mudou)
- [ ] 17. Traduzir codex pattern + codex piloto + Lex piloto modificada + 4 atualizações de templates/katas/codex para `es` e `en`
- [ ] 18. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 19. **Smoke test 1 (carregamento)**: em sandbox Claude Code, abrir arquivo `.py`; verificar que `lex-logging-decorator` carrega; abrir DevTools/inspector para confirmar que `codex-examples-lex-logging-decorator` carrega quando código é editado (matching `paths:`)
- [ ] 20. **Smoke test 2 (regressão)**: rodar lint configurado per `lex-logging-decorator` em código sandbox; deve continuar detectando violações; valida que pointer não quebrou enforcement
- [ ] 21. **Smoke test 3 (validator)**: `validate.py` com novo módulo emite warning para outras Lexis longas (`lex-python-result-type`, etc.) que ainda não têm companion — confirma detection works
- [ ] 22. **Smoke test 4 (MCP integration)**: se plan-021 mergeado, chamar `ahrena_query_examples(lex_name="lex-logging-decorator", lang="pt-BR")`; verificar que retorna o companion
- [ ] 23. **Smoke test 5 (kata-artifact-self-review)**: rodar review na Lex piloto pós-refactor; verificar que checa também o companion
- [ ] 24. Medir: tamanho de `lex-logging-decorator.md` antes (75 linhas) vs depois (alvo: ~25 linhas); registrar no codex `codex-token-optimization` técnica #7
- [ ] 25. Commits atômicos; push; abrir PR via `kata-contributing-pr`
- [ ] 26. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-022 mergeado** — `codex-token-optimization` recebe técnica #7 (bloqueante para cross-reference; soft-bloqueante se aceitar TODO)
- **Plan-019 mergeado** — `scripts/validate.py` (bloqueante)
- `templates/*-sample.md` presentes
- `kata-create-lexis`, `kata-artifact-self-review` mergeados
- **Independente** de plans 011-018, 020, 023
- **Sinérgico** com plan-021 (MCP) — tool `ahrena_query_examples` é extensão natural

## Riscos

- **Split em 2 arquivos confunde leitor humano.** Mitigação: pointer é claríssimo (link direto para companion); MkDocs renderiza navegação coerente; humano clica no link
- **Lex perde valor pedagógico** sem exemplos inline. Mitigação: Lex pode reter 1 exemplo curto inline + pointer para companion com a coleção completa; codex `codex-examples-pattern` documenta esse híbrido como opção válida
- **Companion fica órfão** quando Lex é deletada/renomeada. Mitigação: `kata-artifact-self-review` checa coerência; `validate.py` warns sobre companions sem Lex pai
- **Migration backfill nunca acontece** após plan-024 mergear. Mitigação: aceito — backfill é "nice to have"; ferramenta pronta; pressure orgânica via warnings do validator
- **Cursor/Claude Code não respeitam `paths:` para companions** (já carregam sempre). Mitigação: codex documenta o comportamento real; `paths:` é optimization-hint, fallback é eager-load (sem regressão funcional, só sem ganho)
- **Naming `codex-examples-lex-X` é verboso.** Mitigação: clareza importa mais; codex documenta racionale; alternativas curtas (`codex-ex-X`) descartadas por ambiguidade
- **Plan-022 e plan-024 conflitam** ao tocar `codex-token-optimization`. Mitigação: plan-022 mergeia primeiro (cria o codex); plan-024 só estende com técnica #7 — diff cirúrgico

## Verificação

1. `codex-examples-pattern` × 3 idiomas + `codex-examples-lex-logging-decorator` × 3 idiomas = 6 arquivos novos
2. `lex-logging-decorator` × 3 idiomas com pointer; tamanho reduzido (medido em step 24)
3. 4 atualizações × 3 idiomas (templates lex/codex, kata-create-lexis, kata-artifact-self-review)
4. `codex-token-optimization` × 3 idiomas com técnica #7
5. `scripts/_validate/examples_companion.py` + tests
6. `framework/platforms.yaml` atualizado
7. 5 smoke tests passam
8. Lex piloto reduzida em pelo menos 30 linhas (de 75 para ~25)
9. **Sem alteração** em Lexis que não são piloto (backfill é onda 2)
10. PR final passa HARD-GATE de `lex-pr-quality`; carrega stamp de custo se plan-007 mergeado