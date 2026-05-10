---
plan_id: "026"
title: "commit-readiness-observer"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-08T00:00:00Z"
updated_at: "2026-05-08T00:00:00Z"
---

# Plano: Observer de prontidão para commit (sinais que identificam o momento adequado)

## Objetivo

Construir mecanismo que identifica **quando o working tree está em estado "atomic commit-ready"** e quando não está. Observer não é daemon — é função idempotente invocada em pontos discretos (após batch de edits, após test run, após step `[x]` do plan ser marcado, ou sob demanda via `cry-commit-readiness`). Avalia 10 sinais (testes passando, type-check, lint, escopo Conventional Commits coerente, sem TODOs novos, alinhamento com plano, etc.), produz score `ready | unclear | not-ready` + diagnóstico com próximos passos. Quando `ready`, sugere subject Conventional Commits e oferece commit. Resolve dor concreta: dev/agente acumula 5 mudanças não-correlatas em um commit gigante, ou divide um change atômico em commits parciais que não compilam.

## Contexto

### Por que isso é problema real

`lex-small-commits` obriga commits atômicos ("um logical change por commit, código compila e tests passam após cada commit"). `lex-conventional-commits` exige tipo único por commit. Mas:

- **Humano não tem feedback** sobre se o estado atual atende esses critérios — descobre no review
- **Agente** (Apollo, Hephaestus) decide commit hora por hora baseado em "feeling" — sem sinal objetivo
- **Resultado real:** commits que misturam `feat` + `refactor` + `docs`; ou commits parciais que falham CI; ou commits enormes que misturam cleanup + feature

### Sinais que indicam "agora é hora de commitar"

| # | Sinal | Por que importa | Como medir |
|---|---|---|---|
| 1 | **Tests for affected paths pass** | `lex-small-commits` rule 2: estado funcional após commit | `pytest --testpath` em paths tocados; ou cache `pytest-watch`; ou heurística (file `foo.py` modificado → `foo.test.py` ou `tests/test_foo.py` rodou e passou) |
| 2 | **Type check passes** | Mesmo motivo | `mypy --strict` em arquivos modificados; `tsc --noEmit` |
| 3 | **Linter limpo** | Mesmo motivo | `ruff check`, `eslint`, `golangci-lint` |
| 4 | **Diff cabe em 1 Conventional Commits type** | `lex-conventional-commits`: 1 type por commit | Heurística de paths: `tests/**` only → `test:`; `docs/**` → `docs:`; `framework/**/lexis/**` → varia; **mistura** de paths que sugerem types diferentes → ambíguo |
| 5 | **Sem TODOs novos no diff** | Sinal de trabalho incompleto | grep `TODO:`/`XXX:`/`FIXME:` em added lines |
| 6 | **Alinhamento com plan ativo** (plan-025) | Diff respeita `## Escopo` | Reusa `plan_alignment.py` |
| 7 | **Step `[x]` recém-marcado** | Sinal positivo: completou unidade | Diff em `.claude/plans/plan-*.md` mostra `[x]` adicionado |
| 8 | **Diff size dentro budget atomic** | Commits > 500 linhas são red flag | `git diff --stat` |
| 9 | **Sem partial refactor** | Sinal: signature mudou em 1 lugar, callers não atualizados | Heurística: grep símbolos modificados em files não tocados — match fraco mas útil |
| 10 | **Commit message draftable** | Score de coesão | LLM ou heurística: tenta gerar subject < 70 chars; se diff é incoerente, draft fica vago |

### Inferir scope da sessão por `git diff` + mtime + cache nativo de tooling

Após o reposicionamento de `.checkpoint` (issue #73, plan-040), o schema canônico do checkpoint é enxuto (Session focus, Active plans, Open threads, Notes) e **NÃO** contém mais `Artifacts produced`. O observer precisa inferir o scope da sessão de outra forma — sem depender de campo que não existe mais e sem inventar persistência custom.

**Fonte da "referência do que foi implementado":** `git diff --name-only --diff-filter=AM` cruzado com mtime dos arquivos. O set `S` de paths da sessão é determinado por: arquivos modificados ou adicionados no working tree cujo mtime é mais recente que o último commit da branch. Isso aproxima "o que foi tocado nesta janela de trabalho" sem precisar de log explícito em `.checkpoint`.

**Fonte da "evidência de validação":** caches nativos de tooling — `.pytest_cache/lastfailed`, `.pytest_cache/v/cache/lastfailed`, `.mypy_cache/`, `.ruff_cache/`. Essas pastas já registram o que passou/falhou na última execução, com invalidação automática por mtime/hash de conteúdo. Reinventar isso violaria DRY (`lex-dry`) e o propósito de `lex-checkpoint` (sessão, não validação).

**Contrato do observer:**

1. Calcula `S` = `git diff --name-only --diff-filter=AM HEAD` interseccionado com paths cujo mtime > timestamp do último commit da branch.
2. (Opcional, hint) Lê `.checkpoint > Active plans` se presente — usa para sinal #6 (plan alignment) cruzando com plano(s) listado(s). Se `.checkpoint` ausente ou sem Active plans, sinal #6 cai para heurística padrão (qualquer plano com status `in-progress` em `.claude/plans/`).
3. Para cada path `p ∈ S`:
   - **Sinal #1 (tests):** consulta `.pytest_cache/lastfailed`. Se `p` (ou seu test-file derivado) **não** aparece em `lastfailed` **E** mtime de `.pytest_cache/v/` > mtime de `p` → green via cache. Caso contrário, re-executa pytest restrito a `p` + tests derivados.
   - **Sinal #2 (typecheck):** consulta `.mypy_cache/3.X/{module}.meta.json`; se hash do source nele bate com hash atual de `p` → green via cache. Senão re-executa `mypy --strict p`.
   - **Sinal #3 (linter):** consulta `.ruff_cache/`; análoga ao mypy.
4. Para paths `p ∉ S` (modificados fora da sessão atual): observer roda os sinais sem cache — não confia em estado do qual a sessão não tem evidência.
5. Sinais leves (TODOs novos, diff size, step `[x]` recém-marcado, plan alignment, message draftable) **sempre** rodam — são O(diff), não O(código).

**Por que isso resolve o problema sem depender hard de `.checkpoint`:**

- `git diff --name-only` + mtime já é o registro canônico de "o que foi tocado" — nada novo a inventar; sem dependência de campo opcional do checkpoint.
- `.pytest_cache`, `.mypy_cache`, `.ruff_cache` já são caches válidos, com invalidação correta por hash de conteúdo, mantidos pelas próprias ferramentas.
- `.checkpoint > Active plans` continua sendo **dica útil mas opcional** para o sinal #6 (plan alignment); ausência não quebra o observer — apenas perde uma otimização menor.
- Observer **não escreve** em `.checkpoint` (preserva schema reposicionado de `lex-checkpoint`).
- Quando nada mudou em `p` desde a última validação, sinal é green em < 50ms (leitura de cache nativo) em vez de re-executar pytest/mypy/ruff.

**Quando os caches nativos não existem** (projeto novo, primeira execução, cache limpo): observer roda full validation, popula os caches via execução normal, e na próxima invocação já tem cache hit. Não há fallback "custom" a manter.

### Counter-signals (motivos para NÃO commitar agora)

- Tests falhando em paths tocados → bloqueia
- Linter erro (não warning) → bloqueia
- TypeError → bloqueia
- 2+ Conventional Commits types misturados → sugere split
- Plan-alignment violation (plan-025) → sugere bypass ou correção
- File modificado com `assert` ou `print` debug não removido → sugere cleanup

### Arquitetura: 3 modos de invocação

```
┌─────────────────────────────────────────────────────────────────┐
│ Modo 1 — Sob demanda (humano)                                   │
│  $ cry-commit-readiness                                         │
│  → score + diagnóstico no terminal                              │
│  → se ready: oferece executar `git commit` com message draftado │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Modo 2 — Embed em kata-commit (agente ou humano)                │
│  /cry-commit                                                    │
│  → kata-commit Phase 0: readiness check                         │
│  → se ready, prossegue com formatação + assinatura + commit     │
│  → se not-ready, retorna diagnóstico antes de criar commit ruim │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Modo 3 — Hook agentic (Claude Code / Cursor session)            │
│  Após cada batch de Edit/Write tool calls                       │
│  → agent auto-invoca kata-commit-readiness-check                │
│  → se ready: notifica usuário "ready to commit, want to?"       │
│  → se not-ready: silencia (avoid noise)                         │
│  → integração com VSCode extension scaffold (PR #39)            │
└─────────────────────────────────────────────────────────────────┘
```

Modo 3 é opcional/experimental no roll-out inicial — codex documenta como pattern; implementação depende da extension VSCode evoluir.

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Não-daemon | Função invocada em pontos discretos | Daemon FS watcher = consumo + complexidade desnecessários |
| Implementação | Módulo Python `scripts/_validate/commit_readiness.py` (estende plan-019) | Reusa infra |
| Score model | `ready` (todos sinais green ou neutral) / `unclear` (ambíguo, e.g., type não inferível) / `not-ready` (≥1 bloqueante red) | 3 estados são suficientes |
| Output formato | (a) JSON estruturado para CI/agentes; (b) human-readable colorido; (c) markdown summary | Compatível com plan-019 output framework |
| Commit message draft | Heurística first (paths → type, summary curta); LLM provider opcional (Anthropic) para casos ambíguos via `commit_readiness.draft_provider` em `.directives` | Heurística cobre 80%; LLM é fallback |
| Bilingual subject | Per `lex-commit-language`: subject sempre EN; body opcional `[en]` + `[pt-BR]` | Conformidade automática |
| Allow incremental commit | Sim — usuário pode forçar commit com `--no-readiness-check` | Não vira camisa-de-força |
| Severity rollout | `ready=info, unclear=warning, not-ready=error` no kata-commit; **suggestion-only** no Mode 1 (cry standalone) | Bloqueio só onde já há gate explícito |
| Cache de validação | Lê caches nativos (`.pytest_cache/lastfailed`, `.mypy_cache/`, `.ruff_cache/`); **não inventa cache custom** | DRY (`lex-dry`); tooling nativo já tem invalidação correta por hash de conteúdo |
| Scope da sessão | Observer infere via `git diff --name-only --diff-filter=AM` ∩ paths com mtime > timestamp do último commit; **não depende** de `.checkpoint > Artifacts produced` (campo removido por plan-040) | Sem dependência hard de `.checkpoint`; degradação graciosa quando ausente |
| Hint opcional via `.checkpoint > Active plans` | Sinal #6 (plan alignment) usa quando presente; senão cai para heurística padrão (planos `in-progress` em `.claude/plans/`) | `.checkpoint` reposicionado é otimização, não dependência |
| Invalidação | Delegada aos caches nativos (mtime/hash); observer só consulta | Sem código novo de invalidação a manter |
| Test runner | Configurável (pytest, jest, go test, vitest) por linguagem detectada via files mexidos | Heterogeneidade |
| Integração com plan-025 | Sim — sinal #6 chama `plan_alignment.check()`; resultado é input do score | Compõe |
| Idiomas dos artefatos | 3 (pt-BR canonical + es + en) | `lex-framework-language` |

## Escopo

### Artefatos a criar

| Pilar / tipo | Caminho | Conteúdo |
|---|---|---|
| Codex | `_foundation/contributing/codex/codex-commit-readiness.md` (3 idiomas) | Conceito de readiness; 10 sinais; 3 modos de invocação; output formato; troubleshooting; integração com IDEs (placeholder VSCode) |
| Kata | `_foundation/contributing/katas/kata-commit-readiness-check.md` (3 idiomas) | Procedimento: invoca módulo; coleta resultado de cada sinal; produz score + diagnóstico + drafted commit message; pode ser invocado isoladamente ou como Phase 0 de `kata-commit` |
| Cry | `_foundation/contributing/cries/cry-commit-readiness.md` (3 idiomas) | Atalho usuário → invoca `kata-commit-readiness-check`; print colorido; opcionalmente prompt "commit now? (y/n)" se ready |
| Validator module | `scripts/_validate/commit_readiness.py` | Implementa os 10 sinais; chamável como `validate.py --mode=commit-readiness [--against HEAD] [--format=json|human|md]` |
| Tests | `tests/validate/test_commit_readiness.py` + fixtures | Casos por sinal + casos compostos (ready, not-ready, unclear) |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `_foundation/contributing/katas/kata-commit.md` | Adicionar Phase 0: "Readiness check via kata-commit-readiness-check; se score=not-ready, abort com diagnóstico antes de prosseguir; se score=unclear, prompt confirmação humana; se score=ready, prossegue" |
| `_foundation/contributing/lexis/lex-small-commits.md` Validation | Acrescentar: "Auditoria automatizada via `scripts/validate.py --mode=commit-readiness`; ferramenta canônica para validar atomicidade antes do commit" |
| `_foundation/contributing/lexis/lex-conventional-commits.md` Validation | Idem — readiness checa coerência de type |
| `engineering/workflow/warriors/warrior-athena.md` (e outros que invocam `kata-commit`) | Acrescentar nota: "agent SHOULD invocar `cry-commit-readiness` antes de chamar `cry-commit` em pontos de transição naturais (após step `[x]`, após test run verde)" |
| `_foundation/quality/codex/codex-token-optimization.md` (criado em plan-022) | Acrescentar técnica #8: "Atomicity-first commits — observer detects commit-ready moments" |
| `framework/.directives.sample` | Adicionar bloco:<br>`# commit_readiness:`<br>`#   draft_provider: heuristic   # heuristic | anthropic`<br>`#   test_runner_python: pytest`<br>`#   test_runner_node: jest`<br>`#   max_atomic_lines: 500`<br>`#   block_on_todos: true`<br>`#   integrate_plan_alignment: true` |
| `framework/platforms.yaml` | Registrar codex, kata, cry novos |
| `scripts/validate.py` | Adicionar mode `commit-readiness` |

## Fora de escopo

- **Daemon FS watcher** rodando continuamente — fora; codex documenta como pattern para iteração futura via VSCode extension (PR #39)
- **Auto-commit sem confirmação humana** — fora; observer só sugere; commit final é decisão explícita
- **Auto-split de commits** quando multi-type detectado — fora; observer sugere split (lista files por type detectado); split é manual
- **Detecção avançada de partial refactor** (AST analysis) — fora; primeiro versão é heurística (grep); AST fica em iteração futura
- **Integração nativa com IDEs além de Claude Code/Cursor** — fora; codex menciona como possível extensão
- **Notificação push** (Slack, email, OS notification) — fora; output é terminal/IDE first
- **Histórico de readiness scores** ao longo do tempo — fora; cada invocação é stateless

## Steps

- [ ] 1. **Confirmar plan-019 mergeado** — `validate.py` é base (bloqueante)
- [ ] 2. **Confirmar plan-025 mergeado ou em paralelo** — sinal #6 (plan alignment) reusa o módulo do auditor (sinérgico mas não strict-blocker; sem ele, sinal #6 é skipped)
- [ ] 3. Abrir issue com template `feature-request`, Issue Type `Feature`, label `evolvability ♻️` + `enhancement 🔝`
- [ ] 4. Criar branch `feat/{N}-commit-readiness-observer` e worktree
- [ ] 5. Atualizar status deste plan para `in-progress`
- [ ] 6. Implementar `scripts/_validate/commit_readiness.py`:
  - Function por sinal: `signal_tests_pass()`, `signal_typecheck()`, `signal_linter()`, `signal_conventional_type()`, `signal_no_todos()`, `signal_plan_alignment()`, `signal_step_marked()`, `signal_diff_size()`, `signal_no_partial_refactor()`, `signal_message_draftable()`
  - Aggregator: combina sinais → score `ready|unclear|not-ready`; lista findings
  - Drafter: dado diff, retorna subject Conventional Commits + body (heurística first; LLM se configurado)
  - **Cache via tooling nativo + scope via git diff:** `session_scope()` infere `S` via `git diff --name-only --diff-filter=AM` ∩ paths com mtime > último commit da branch (sem depender de `.checkpoint`); `cache_pytest()`, `cache_mypy()`, `cache_ruff()` consultam pastas `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` para evidência de validação verde; sinais pesados aceitam cache hit somente para paths em `S`; opcionalmente lê `.checkpoint > Active plans` (read-only, sem escrita) como hint para sinal #6 (plan alignment) — fallback para heurística padrão quando ausente
- [ ] 7. Adicionar tests em `tests/validate/test_commit_readiness.py` cobrindo cada sinal isoladamente e cenários combinados
- [ ] 8. Atualizar `scripts/validate.py` para expor `--mode=commit-readiness`
- [ ] 9. Redigir `kata-commit-readiness-check.md` em pt-BR
- [ ] 10. Redigir `cry-commit-readiness.md` em pt-BR
- [ ] 11. Redigir `codex-commit-readiness.md` em pt-BR
- [ ] 12. Atualizar `kata-commit.md` em pt-BR (Phase 0)
- [ ] 13. Atualizar `lex-small-commits.md` e `lex-conventional-commits.md` em pt-BR (Validation tooling)
- [ ] 14. Atualizar `warrior-athena.md` em pt-BR (nota sobre auto-invocação)
- [ ] 15. Atualizar `codex-token-optimization.md` (se plan-022 mergeado) com técnica #8
- [ ] 16. Atualizar `framework/.directives.sample` com bloco `commit_readiness`
- [ ] 17. Atualizar `framework/platforms.yaml`
- [ ] 18. Traduzir 3 artefatos novos + 4 atualizações para `es` e `en`
- [ ] 19. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 20. **Smoke test 1 (ready clean state)**: branch sandbox; modificar 1 file `foo.py`; tests `test_foo.py` passam; mypy passa; ruff passa; rodar `cry-commit-readiness` → score `ready`; subject draftado começa com tipo apropriado
- [ ] 21. **Smoke test 2 (test failing)**: introduzir falha em `test_foo.py`; readiness retorna `not-ready` com finding sinal #1
- [ ] 22. **Smoke test 3 (linter failing)**: deixar `print('debug')` no código; readiness retorna `not-ready` com finding sinal #3
- [ ] 23. **Smoke test 4 (multi-type)**: 1 commit candidato com `foo.py` (feat) + `tests/test_foo.py` (test) + `docs/foo.md` (docs); readiness retorna `unclear` (ou `not-ready` se config strict) sugerindo split; lista files por type
- [ ] 24. **Smoke test 5 (TODO novo)**: adicionar `TODO: implement later` em código; readiness retorna `not-ready` sinal #5
- [ ] 25. **Smoke test 6 (plan alignment OK)**: branch com plano ativo cujo escopo bate; sinal #6 verde; resto verde → `ready`
- [ ] 26. **Smoke test 7 (plan alignment violado)**: file fora de escopo; sinal #6 vermelho; readiness `not-ready`
- [ ] 27. **Smoke test 8 (step `[x]` recém-marcado)**: diff inclui `- [ ] step` → `- [x] step` no plan; sinal #7 verde positivo
- [ ] 28. **Smoke test 9 (diff > 500 linhas)**: stub commit com 600 linhas; sinal #8 emite warning; score `unclear`
- [ ] 29. **Smoke test 10 (kata-commit Phase 0)**: invocar `kata-commit` em estado not-ready; verificar que aborta antes de criar commit; mensagem orienta usar `cry-commit-readiness` para ver detalhes
- [ ] 30. **Smoke test 11 (override)**: rodar `kata-commit --no-readiness-check`; cria commit ignorando readiness — registra warning no body do commit
- [ ] 31. **Smoke test 12 (commit message draft)**: ready state; verificar que subject draftado segue Conventional Commits + `lex-commit-language` (EN); body bilíngue com `[en]` + `[pt-BR]` se config solicitar
- [ ] 31a. **Smoke test 13 (scope via `git diff` + mtime)**: branch com `app/foo.py` modificado depois do último commit e `app/bar.py` modificado antes; observer infere `S = {app/foo.py}`; cache de tooling reusado apenas para `app/foo.py`; `app/bar.py` força re-execução completa dos sinais
- [ ] 31b. **Smoke test 14 (cache hit nativo)**: rodar `pytest`, `mypy`, `ruff` verde em `app/foo.py`; segunda invocação do observer sem mudanças no arquivo; verificar cache hit em `.pytest_cache`/`.mypy_cache`/`.ruff_cache` em < 50ms (sem re-executar tooling)
- [ ] 31c. **Smoke test 15 (cache miss por mtime)**: estado igual ao 31b; tocar `app/foo.py` (mtime > cache); verificar que tooling nativo invalida e observer re-executa
- [ ] 31d. **Smoke test 16 (`.checkpoint` ausente)**: workspace sem `.checkpoint`; observer roda full validation em todos os paths modificados (sem scope hint do `Active plans`); não falha — apenas usa heurística padrão para sinal #6
- [ ] 31e. **Smoke test 17 (`.checkpoint > Active plans` opcional)**: `.checkpoint` no schema novo com `Active plans` listando `plan-026`; observer consome como hint para sinal #6 (plan alignment); resultado igual ao smoke test 25 (plan alignment OK), mas com confirmação explícita de qual plano foi usado
- [ ] 32. Rodar `kata-artifact-self-review` em codex, kata, cry novos
- [ ] 33. Commits atômicos por componente — **dogfooding:** cada commit deste PR passa pelo readiness do próprio plano
- [ ] 34. Push e abrir PR via `kata-contributing-pr`
- [ ] 35. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-019 mergeado** — `scripts/validate.py` é base (bloqueante)
- **Plan-025 mergeado ou paralelo** — sinérgico para sinal #6; sem ele, sinal vira no-op (sem regressão)
- `lex-small-commits`, `lex-conventional-commits`, `lex-commit-language`, `kata-commit` mergeados (já estão)
- `pytest` / `mypy` / `ruff` instaláveis no projeto-cliente; runners equivalentes para outras stacks
- **Independente** de plans 011-018, 020-024, 026

## Riscos

- **False positive bloqueando trabalho** (test cache stale, linter false alarm). Mitigação: severity gradual; override via `--no-readiness-check`; cache invalidation explícita
- **Sinais ruidosos confundem score.** Mitigação: cada sinal isolado em test fixture; combiner é deterministic; codex documenta cada sinal e como debug
- **Heurística de Conventional Commits type erra** quando paths não são óbvios (e.g., refactor que toca docs incidentalmente). Mitigação: prefer `unclear` em vez de `not-ready` quando ambíguo; humano decide
- **Test runner detection erra** em mono-repo poliglota. Mitigação: configurável via `.directives` per linguagem; auto-detect via file extensions tocados
- **LLM provider opcional gera custo extra.** Mitigação: heurística first (default `draft_provider: heuristic`); LLM só se config explícito
- **Performance ruim** se runs `pytest` toda vez. Mitigação: cache check (`.pytest_cache/lastfailed`, `.pytest_cache/cachedir`); marker file de "last successful run"; runner nunca é forçado pelo readiness — usa cache se < 5min
- **Conflito com VSCode extension PR #39** se ele evoluir paralelamente. Mitigação: codex documenta API esperada (function call signature); extension consome quando madura
- **Mode 3 (auto-invoke após cada edit)** vira spam de notificações. Mitigação: throttle (max 1× por minuto); só notifica quando score muda de `not-ready` para `ready` (transição); silêncio em estados não-positive
- **Score `unclear` vira lixeira** que esconde problemas. Mitigação: cada finding sob `unclear` tem ação sugerida explícita; user vê o "porquê" do unclear; codex documenta resolution path
- **Override `--no-readiness-check` vira hábito.** Mitigação: marker no commit message body documenta uso; relatório agregado mensal lista uso (audit trail similar ao plan-025)
- **`git diff` + mtime sub-estima scope** se sessão fez vários commits intermediários. Mitigação: observer usa último commit da branch como ponto de referência; em branches longas, considera todos os commits depois do merge-base com `main`; ainda assim `S` representa "trabalho da branch", o que é mais preciso que "trabalho da sessão" para fins de cache
- **Cache nativo de tooling indisponível** (pasta deletada, projeto recém-clonado) → cache miss para todos paths. Mitigação: comportamento esperado e correto; primeira execução popula caches; sem regressão de correctness
- **`.checkpoint` ausente** em projetos que não adotaram `lex-checkpoint` reposicionado. Mitigação: observer degrada graciosamente — sinal #6 cai para heurística padrão (planos `in-progress` em `.claude/plans/`); codex documenta que `.checkpoint > Active plans` é hint, não dependência

## Verificação

1. `codex-commit-readiness` × 3 idiomas + `kata-commit-readiness-check` × 3 idiomas + `cry-commit-readiness` × 3 idiomas = 9 arquivos novos
2. `scripts/_validate/commit_readiness.py` + tests com cobertura ≥80% e tests por cada um dos 10 sinais
3. `validate.py` expõe `--mode=commit-readiness`
4. `kata-commit` × 3 idiomas com Phase 0 documentada
5. `lex-small-commits`, `lex-conventional-commits` × 3 idiomas com nota de validation tooling
6. `warrior-athena` × 3 idiomas com nota sobre auto-invocação
7. `framework/.directives.sample` tem bloco `commit_readiness`
8. `framework/platforms.yaml` lista os 3 novos artefatos
9. **12 smoke tests passam** (steps 20-31)
10. **Dogfooding:** cada commit do PR deste plan-026 foi precedido por readiness check verde (registrado no body do commit ou em audit log)
11. Performance: invocação completa < 3s em projeto médio; cache miss < 3s; **cache hit via `.checkpoint` < 50ms** para sinais pesados (tests, typecheck, linter)
12. **Integração não-invasiva:** observer infere scope via `git diff` + mtime; consulta caches nativos (`.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`); opcionalmente lê `.checkpoint > Active plans` como hint para sinal #6 (plan alignment); **não modifica** `.checkpoint` (preserva schema reposicionado de `lex-checkpoint`); ausência de `.checkpoint` ou de caches nativos não quebra o observer — apenas desliga o atalho de cache hit (caches) ou cai para heurística padrão (Active plans)
13. **Sem nova Lex** criada; **sem regressão** em commit/PR flow para projetos com `commit_readiness.draft_provider: heuristic` e severity warning
14. PR final passa HARD-GATE de `lex-pr-quality`; passa o próprio readiness; carrega stamp de custo se plan-007 mergeado