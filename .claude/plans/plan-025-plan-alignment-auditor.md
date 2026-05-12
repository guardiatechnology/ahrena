---
plan_id: "025"
title: "plan-alignment-auditor"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T23:50:00Z"
updated_at: "2026-05-07T23:50:00Z"
---

# Plano: Auditor de alinhamento Plano ↔ Implementação (pre-commit + pre-PR)

## Objetivo

Construir auditor automatizado que, dado um plano (`.claude/plans/plan-{NNN}-*.md` em `status: in-progress`), verifica em **pre-commit local** e **pre-PR no CI** que o diff respeita o `## Escopo` declarado: nenhum arquivo fora de escopo é tocado, nenhum item de `## Fora de escopo` é violado, e (best-effort) cada step `[x]` tem evidência no diff. Atual root-cause de retrabalho: `lex-agent-planning` codifica o plano mas não tem mecanismo de enforcement durante a execução, então scope creep e desvios passam despercebidos até a revisão final. Auditor fecha esse loop.

## Contexto

### Dor concreta (declarada pelo usuário)

> "Já tivemos casos recentes de desvios que geraram retrabalho massivo."

Sintomas típicos detectáveis:

| Sintoma | O que acontece | Custo |
|---|---|---|
| **Scope creep silencioso** | Dev modifica `frontend/...` numa PR cujo plano só declarou `backend/...` | Review mistura preocupações; aprovação atrasa |
| **Out-of-scope violado** | Plano declarou "Fora de escopo: refactor de logging"; commit toca lex-logging-decorator | Decisão revertida ou plano teve que ser refeito |
| **Step `[x]` sem evidência** | Plano marca step "atualizar warrior-apollo em es" como concluído mas o arquivo não está no diff | Falsa sensação de progresso; tradução fica esquecida |
| **Arquivos da Verificação ausentes** | Plano lista verificação "framework/platforms.yaml registra novo Lex"; commit não toca o yaml | PR aprovada com lint posterior falhando |
| **Plan stale** | Branch `feat/42-...` ativo; plan correspondente ainda em `status: pending` | Trabalho sem registro estruturado |
| **Múltiplas mudanças sem plano** | Commit em branch sem plan associado | Violação do `lex-agent-planning` |

### Como o auditor sabe qual plano auditar

Estratégia em cascata:

1. **Branch name match:** `feat/{N}-{slug}` → procura plano cujo `issue: "owner/repo#N"` bate
2. **Plan status:** se exatamente um plano está em `status: in-progress`, usa ele
3. **Env var explícita:** `AHRENA_ACTIVE_PLAN=plan-013` força a escolha
4. **Múltiplos válidos:** une os escopos (raro mas suportado)
5. **Nenhum válido:** auditor falha com mensagem clara orientando a criar o plan

### Arquitetura em duas camadas

```
┌──────────────────────────────────────────────────────────┐
│ Camada 1 — pre-commit local (rápido, < 2s)               │
│  - resolve plan ativo                                    │
│  - parsa ## Escopo do plan                               │
│  - lista files modificados via `git diff --cached`       │
│  - falha se file ∈ Fora-de-escopo                        │
│  - warn se file ∉ Escopo declarado                       │
│  - bloqueia commit se severidade error                   │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│ Camada 2 — pre-PR no CI (completo, ~10s)                 │
│  - tudo da Camada 1, contra `git diff main...HEAD`       │
│  - + verifica step `[x]` ↔ evidência no diff             │
│  - + verifica ## Verificação ↔ files presentes           │
│  - + verifica plan status: in-progress                   │
│  - + detecta plan stale (não atualizado em N dias)       │
│  - + bypass via PR label `waiver:plan-alignment`         │
│  - falha CI check se severidade error                    │
└──────────────────────────────────────────────────────────┘
```

### Como o auditor parsa o plano

`## Escopo` declara files com padrões previsíveis:

```markdown
## Escopo

### Artefatos a criar

| ... | Caminho | ... |
|---|---|---|
| Codex | `_foundation/quality/codex/codex-token-optimization.md` | ... |
| Lexis | `_foundation/quality/lexis/lex-token-budget.md` | ... |

### Atualizações em artefatos existentes

| Arquivo | Mudança |
|---|---|
| `templates/warrior-sample.md` | Adicionar campo `token_budget` ... |
| `framework/platforms.yaml` | Registrar codex e lex novos |
```

Auditor extrai paths via regex sobre as células de tabela. Glob patterns aceitos (`**/*.py`). Files mencionados em `## Steps` também contam (heurística secundária).

`## Fora de escopo` lista padrões que **não podem** ser tocados — auditor extrai (geralmente texto + caminhos) e gera deny-list.

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Implementação | Módulo Python em `scripts/_validate/plan_alignment.py` (estende plan-019) | Reusa infra do validator existente |
| Pre-commit local | Hook em `.github/githooks/pre-commit` invoca `python3 scripts/validate.py --mode=plan-alignment --staged` | Mesmo modelo dos hooks de signature/branch-naming já existentes |
| Pre-PR CI | Job `plan-alignment` em `validate-pr.yml` (workflow unificado com plan-028) rodando em `pull_request` | Block via Branch Protection |
| Severity inicial | `warning-only` — auditor reporta mas não bloqueia | Adoção gradual; promove para `error` após 2-3 sprints de uso |
| Bypass commit-level | Trailer `Plan-bypass: <reason>` no commit message | Para hotfix legítimo ou retoque trivial |
| Bypass PR-level | Label `waiver:plan-alignment` + comment justificando (>20 chars), mirror do plan-020 | Para casos onde plano evoluiu mas auditor ainda lê versão antiga |
| Auto-detect commits sem plano | Sim — emite warning, sugere abrir plano | `lex-agent-planning` exige plano para tasks multi-step |
| Exemption list por projeto | `plan_alignment.exempt_paths` em `.directives` (e.g., `.cursor/**`, `.claude/**` que são derivados gerados pelo install.py) | Evita false positive em arquivos sintetizados |
| Step `[x]` ↔ diff matching | Heurística: para cada step com `[x]`, procura keywords no diff (paths citados, nomes de arquivos, palavras-chave do step text) | Best-effort, não 100% — emite info quando incerto |
| Múltiplos planos in-progress | União dos escopos | Suportado mas raro; sinaliza no log |
| Plan stale | `updated_at` > 14 dias atrás → warning | Plano abandonado mas não arquivado é red flag |
| HARD-GATE em `lex-agent-planning` | Sim, novo critério: "agente que executa task multi-step sem plano em status `in-progress` e sem `Plan-bypass:` no trailer viola a Lex" | Forcing function para abertura de plano |
| Idiomas | 3 (pt-BR canonical + es + en) — codex e cry novos | `lex-framework-language` |

### Harmonização com plan-028 (doc-coherence)

`plan-028` introduz auditor de coerência "código ↔ doc" com mecanismos similares (CI workflow, waiver, estrutura `scripts/_validate/`). Três decisões de harmonização acordadas:

1. **Convenção de waiver unificada via labels namespaced.**
   - `waiver:plan-alignment` (este plan)
   - `waiver:doc-coherence` (plan-028)
   - Comment estruturado no PR carrega o detalhe (motivo, expiração)
2. **Infraestrutura compartilhada `scripts/_validate/`** sob `scripts/validate.py` (plan-019). Mesmo formato de finding.
3. **Workflow de PR unificado** `.github/workflows/validate-pr.yml` com **jobs paralelos** (`plan-alignment`, `doc-coherence`, futuros), em vez de um workflow por validador.

### Onde encaixa nos artefatos existentes

| Artefato | Papel |
|---|---|
| `lex-agent-planning` (existente) | Adiciona criterion explícito sobre alinhamento e bypass |
| `kata-quality-gate` (existente) | Check 1 (AC↔test traceability) ganha sub-check de plan alignment |
| `kata-plan-task` (existente) | Atualiza para mencionar o auditor como ferramenta companion |
| `scripts/validate.py` (plan-019) | Recebe novo módulo |
| `.github/githooks/` | Recebe novo hook |
| `.github/workflows/` | Recebe novo workflow |
| `framework/.directives.sample` | Bloco `plan_alignment.exempt_paths` |

## Escopo

### Artefatos a criar

| Pilar / tipo | Caminho relativo | Conteúdo |
|---|---|---|
| Codex | `_foundation/process/codex/codex-plan-alignment.md` (3 idiomas) | Conceito; arquitetura 2-camadas; como auditor parsa o plano; bypass mechanisms; exemption patterns; troubleshooting (plan não detectado, false positives) |
| Cry | `_foundation/process/cries/cry-plan-check.md` (3 idiomas) | Atalho local: `python3 scripts/validate.py --mode=plan-alignment --against main`; útil antes de push manual |
| Validator module | `scripts/_validate/plan_alignment.py` | Lógica do auditor; chamado pelo `validate.py --mode=plan-alignment` ou pelo modo default em CI |
| Tests | `tests/validate/test_plan_alignment.py` + fixtures | Casos: scope respected; scope creep; out-of-scope violated; step sem evidência; plan stale; bypass via trailer; bypass via label; múltiplos planos |
| Pre-commit hook | `.github/githooks/pre-commit-plan-alignment.sh` | Invoca `validate.py --mode=plan-alignment --staged --severity=error-only` (mode rápido) |
| CI workflow | `.github/workflows/validate-pr.yml` (job `plan-alignment`) | Workflow unificado com plan-028. Job roda em `pull_request`; chama `validate.py --mode=plan-alignment --against ${{ github.base_ref }}`; falha se severity `error`. Plan-028 adiciona job `doc-coherence` no mesmo arquivo. |

### Atualizações em artefatos existentes (3 idiomas onde aplicável)

| Arquivo | Mudança |
|---|---|
| `_foundation/process/lexis/lex-agent-planning.md` | Acrescentar HARD-GATE com critérios: (a) plan in-progress existe; (b) diff respeita `## Escopo`; (c) `## Fora de escopo` não violado. Bypass via trailer ou label declarado |
| `_foundation/process/katas/kata-plan-task.md` | Acrescentar referência ao auditor; documentar fluxo "rodar `cry-plan-check` antes do push" |
| `engineering/workflow/katas/kata-quality-gate.md` | Estender Check 1 com sub-check: "Plan-alignment auditor passou?" — incorpora resultado |
| `engineering/workflow/lexis/lex-issue-driven.md` Gate 2 | Adicionar item: "Plan alignment ✅ (warning-only ainda) ou label `waiver:plan-alignment` com justificativa" |
| `framework/.directives.sample` | Bloco comentado:<br>`# plan_alignment:`<br>`#   exempt_paths: [".cursor/**", ".claude/**", "site/**"]`<br>`#   stale_threshold_days: 14`<br>`#   severity: warning   # warning | error` |
| `framework/platforms.yaml` | Registrar codex e cry novos |
| `_foundation/quality/codex/codex-token-optimization.md` (criado em plan-022) | Acrescentar nota: "Plan alignment auditor é mecanismo de enforcement do `lex-agent-planning`" |
| `scripts/validate.py` | Importar `plan_alignment` module; adicionar flag `--mode=plan-alignment` |

## Fora de escopo

- **Auto-update do plan** baseado no diff (LLM ajusta ## Steps `[x]` ou expande ## Escopo) — fora; humano atualiza, auditor verifica
- **Geração de plan a partir de issue** (LLM cria plan-NNN a partir do issue body) — fora; `kata-plan-task` é o caminho
- **Cross-plan dependency check** (auditor verifica se plan-013 espera plan-012 mergeado antes de iniciar) — fora; `## Dependências` é texto, validação é manual
- **Pre-commit globalmente em projetos clientes** — entrega o hook em `.github/githooks/`; cliente roda `git config core.hooksPath .github/githooks` para ativar (já é o pattern do `bounded-context-template`)
- **Auditor de outros agentes** (Cursor session, Strands run) — escopo é git-driven; sessões de IDE são fora
- **Notificação por Slack/email** quando bypass usado — fora; relatório agregado mensal possível em iteração futura
- **UI/dashboard** para histórico de bypasses — fora

## Steps

- [ ] 1. **Confirmar plan-019 mergeado** — `scripts/validate.py` é prerequisite (bloqueante)
- [ ] 2. Abrir issue com template `feature-request`, Issue Type `Feature`, label `ci 🏗️` + `evolvability ♻️`, título "feat(framework): plan alignment auditor — pre-commit + pre-PR enforcement of plan ↔ implementation"
- [ ] 3. Criar branch `feat/{N}-plan-alignment-auditor` e worktree
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. **Spike de parsing**: protótipo Python que lê `.claude/plans/plan-013-*.md`; extrai paths declarados em `## Escopo`; valida que regex pega ≥90% dos paths reais (incluindo backticks em tabela, code fences, glob patterns)
- [ ] 6. Implementar `scripts/_validate/plan_alignment.py`:
   - **Resolver plan ativo:** branch name → issue # → match em `.claude/plans/*.md`; fallback to `status: in-progress` único; fallback to env var
   - **Parser do plan:** extrai `## Escopo` (paths), `## Fora de escopo` (deny patterns), `## Steps` (checkboxes), `## Verificação` (expected files)
   - **Diff analyzer:** lê `git diff --cached` (staged) ou `git diff main...HEAD` (PR mode); produz lista de files
   - **Matcher:** classifica cada file modificado como `in-scope | out-of-scope | undeclared | exempt`
   - **Step verifier:** para cada step `[x]`, busca keywords/paths no diff; emite `info` quando não encontrado (não é falha, só sinal)
   - **Bypass detector:** lê trailer `Plan-bypass:` no commit message; lê PR label `waiver:plan-alignment` via `gh api`
   - **Output:** lista de findings em formato compatível com plan-019 (severity, file, message)
- [ ] 7. Adicionar tests em `tests/validate/test_plan_alignment.py` cobrindo todos os 8+ cenários listados em "Decisões fechadas"
- [ ] 8. Atualizar `scripts/validate.py` para importar e expor `--mode=plan-alignment`
- [ ] 9. Criar `.github/githooks/pre-commit-plan-alignment.sh`:
   - Invoca `validate.py --mode=plan-alignment --staged --severity=error-only`
   - Sai com 0 se OK ou warning; 1 se error
   - Mensagem clara orientando bypass via trailer
- [ ] 10. Criar `.github/workflows/validate-pr.yml` com job `plan-alignment` (workflow unificado com plan-028):
   - Trigger: `pull_request`
   - Estrutura com jobs paralelos: `plan-alignment` (este plan), `doc-coherence` (plan-028 quando executar)
   - Job `plan-alignment` steps: checkout (with full history), setup Python, run `validate.py --mode=plan-alignment --against ${{ github.base_ref }}`
   - Falha em severity `error` (warning-only no rollout inicial)
   - Se plan-028 mergear primeiro, plan-025 adiciona o job ao arquivo existente em vez de criar
- [ ] 11. Redigir `codex-plan-alignment.md` em pt-BR (canonical)
- [ ] 12. Redigir `cry-plan-check.md` em pt-BR
- [ ] 13. Atualizar `lex-agent-planning.md` em pt-BR com HARD-GATE
- [ ] 14. Atualizar `kata-plan-task.md` em pt-BR
- [ ] 15. Atualizar `kata-quality-gate.md` Check 1 em pt-BR
- [ ] 16. Atualizar `lex-issue-driven.md` Gate 2 em pt-BR
- [ ] 17. Atualizar `framework/.directives.sample` com bloco `plan_alignment`
- [ ] 18. Atualizar `framework/platforms.yaml`
- [ ] 19. Atualizar `codex-token-optimization` (se plan-022 mergeado) com nota
- [ ] 20. Traduzir codex novo + cry novo + 4 atualizações Lex/Kata para `es` e `en`
- [ ] 21. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 22. **Smoke test 1 (scope respected)**: branch sandbox `feat/99-test`; plan-099 com `## Escopo` listando `foo.py`; commit toca apenas `foo.py`; `cry-plan-check` retorna OK
- [ ] 23. **Smoke test 2 (scope creep)**: mesma branch; commit também toca `bar.py` não declarado; auditor warns
- [ ] 24. **Smoke test 3 (out-of-scope violated)**: commit toca arquivo listado em `## Fora de escopo`; auditor falha com error
- [ ] 25. **Smoke test 4 (step sem evidência)**: plan tem step `[x] atualizar baz.py em es` mas commit não toca `baz.es.md`; auditor emite info
- [ ] 26. **Smoke test 5 (bypass trailer)**: commit com trailer `Plan-bypass: hot-fix typo` — auditor passa silenciosamente; bypass logado em audit trail (file `.ahrena/bypass-log.jsonl`)
- [ ] 27. **Smoke test 6 (PR label)**: PR sandbox com label `waiver:plan-alignment` + comment `[plan-waived]: scope evolved, plan to be re-Gate-1ed`; CI passa
- [ ] 28. **Smoke test 7 (plan stale)**: plan com `updated_at` > 14 dias; auditor emite warning
- [ ] 29. **Smoke test 8 (no plan, multi-step)**: branch sem plano correspondente; commit com 5 file changes; auditor warns "violação de lex-agent-planning"
- [ ] 30. **Smoke test 9 (exempt paths)**: commit toca apenas `.cursor/rules/...` (gerados pelo install.py); auditor passa silenciosamente porque `.cursor/**` está em `exempt_paths`
- [ ] 31. **Smoke test 10 (regressão pre-commit)**: hook bloqueia commit local quando severity error; mensagem orienta uso de `Plan-bypass:` se intencional
- [ ] 32. Rodar `kata-artifact-self-review` em codex e cry novos
- [ ] 33. Commits atômicos por componente (`plan_alignment.py` + tests = 1 commit; hook + workflow = 1; artefatos framework = 1; traduções = 1 ou stacked)
- [ ] 34. Push e abrir PR via `kata-contributing-pr` — **dogfooding**: este próprio PR é auditado pelo auditor sendo entregue
- [ ] 35. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-019 mergeado** — `scripts/validate.py` é base (bloqueante)
- `lex-agent-planning` mergeada (já está) — Lex base estendida
- `kata-quality-gate`, `lex-issue-driven` mergeados (já estão) — integração
- `gh` CLI autenticado para leitura de PR labels
- **Independente** de plans 011-018, 020-024
- **Sinérgico** com plan-020 (ADR automation) — mesmo modelo de label+waiver; pode reusar partes de código
- **Sinérgico** com plan-022 (token-optimization-codification) — auditor codifica enforcement do budget também (técnica adicional)

## Riscos

- **False positives bloqueando commits legítimos.** Mitigação: severity `warning-only` no rollout inicial; exemption list configurável; bypass trailer rápido; promove para `error` só após 2-3 sprints de tuning
- **Parser frágil contra variação de formato em `## Escopo`.** Mitigação: spike step 5 valida regex contra plans reais (013-024); template `templates/plan-sample.md` futuro pode codificar formato esperado; warnings explicam quando parser não conseguiu ler
- **Plans imprecisos forçam auditor a ser lenient.** Mitigação: aceito — qualidade do auditor depende da qualidade do plan; gera pressure orgânica para plans mais precisos
- **Bypass trailer vira escape hatch.** Mitigação: bypass logado em `.ahrena/bypass-log.jsonl`; relatório mensal lista todos; auditoria trimestral; codex documenta uso aceitável vs abuso
- **Múltiplos planos in-progress geram confusão.** Mitigação: warning quando >1 plano detectado; humano resolve declarando `AHRENA_ACTIVE_PLAN`; codex documenta como caso especial
- **Hook pre-commit lento** > 2s. Mitigação: budget step 9; usa apenas staged files (não full diff); plan parsing cacheado in-memory; smoke test mede
- **Auditor falha quando plan não tem `## Escopo` formal** (planos legados). Mitigação: detecta ausência → warning informativo, não error; auditor é skip-friendly
- **Convivência com `decision:waived` (plan-020)** e `waiver:doc-coherence` (plan-028). Mitigação: namespace `waiver:*` é o padrão deste plan e do plan-028 — labels distintos por dimensão (`waiver:plan-alignment`, `waiver:doc-coherence`); plan-020 mantém seu prefixo `decision:` por se tratar de outro tipo de exceção (decisão arquitetural sem ADR vs. dispensa de gate). Codex documenta os três propósitos.
- **Step `[x]` matching gera muito ruído** (false-info). Mitigação: severity `info`, não warning; humano vê na lista mas não bloqueia; iteração futura pode melhorar heurística com LLM-assisted matching

## Verificação

1. `codex-plan-alignment` × 3 idiomas + `cry-plan-check` × 3 idiomas = 6 arquivos novos
2. `scripts/_validate/plan_alignment.py` + tests com cobertura ≥80%
3. `.github/githooks/pre-commit-plan-alignment.sh` executável
4. `.github/workflows/validate-pr.yml` com job `plan-alignment` rodando em PRs
5. `lex-agent-planning` × 3 idiomas com HARD-GATE novo
6. `kata-plan-task`, `kata-quality-gate`, `lex-issue-driven` × 3 idiomas atualizados
7. `framework/.directives.sample` tem bloco `plan_alignment`
8. `framework/platforms.yaml` lista codex e cry novos
9. **10 smoke tests passam** (steps 22-31)
10. **Dogfooding:** o próprio PR deste plan-025 passa o auditor que ele entrega
11. Performance: hook < 2s; CI < 10s
12. **Sem alteração** em demais Lexis/Codex; **sem nova Lex** além da extensão de `lex-agent-planning`
13. PR final passa HARD-GATE de `lex-pr-quality`; carrega stamp de custo se plan-007 mergeado