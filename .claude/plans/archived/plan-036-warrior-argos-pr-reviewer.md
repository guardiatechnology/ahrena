---
plan_id: "036"
title: "warrior-argos-pr-reviewer"
status: done
agent: claude
issue: "guardiatechnology/ahrena#69"
pr: "guardiatechnology/ahrena#70"
created_at: "2026-05-09T00:00:00Z"
updated_at: "2026-05-10T22:00:00Z"
---

# Plano: warrior-argos — Revisor Multi-Eixo de Pull Requests

## Objetivo

Criar `warrior-argos`, primeiro warrior dedicado a revisão de Pull Request **pós-abertura, sob demanda do reviewer humano**, que orquestra os katas de review existentes (`kata-python-review`, `kata-frontend-review`, `kata-aws-review`, `kata-api-design-review`, `kata-security-review`, `kata-quality-gate`) + um novo `kata-events-review` (lacuna detectada — não há revisor para CloudEvents). Argos casa o diff da PR com a Issue/Plan referenciados e com o PRD + Capability Spec no Notion (via MCP), executa testes localmente em worktree isolado, detecta breaking changes em contratos públicos (OpenAPI, CloudEvents, migrations, símbolos exportados) e consolida tudo em um único review-comment idempotente no PR.

## Contexto

### Por que agora

- O fluxo Issue-Driven do `warrior-athena` cobre **Gate 2 pré-PR** (autor), mas não há equivalente **pós-PR pelo lado do reviewer** — PRs externas, hotfixes e contribuições manuais não passam por Gate 2.
- Existem 6 katas de review (`kata-python-review`, `kata-frontend-review`, `kata-aws-review`, `kata-api-design-review`, `kata-security-review`, `kata-quality-gate`) mas nenhum orquestrador único — humano dispara um por vez, perde visão de conjunto, não correlaciona com Issue/PRD.
- `kata-events-review` não existe — gap simétrico com `kata-api-design-review`. Mudanças em CloudEvents (`type` quebrado, payload com campo retirado, `idempotencykey` ausente, naming fora de snake_case) hoje só são revisadas por humano.
- Notion guarda PRD + Capability Spec aprovados — alinhar a implementação com o que foi prometido no produto exige consulta sistemática, não eventual.
- Retrocompatibilidade é cara para humano detectar: diff de OpenAPI, schema de eventos, ALTER em migrations, e símbolos públicos exportados são pontos cegos comuns.

### Decisões já alinhadas com o usuário

1. **Escopo**: sob demanda via `cry-review-pr <PR#>` — humano dispara explicitamente, não roda em toda PR aberta.
2. **Notion**: sempre verificar PRD + Capability Spec quando a Issue estiver linkada à PR.
3. **Testes**: execução local no worktree do reviewer (não confia só no CI).
4. **`kata-events-review`** está dentro deste plano (não vira plano separado).
5. **Sem Lexis nova nesta rodada** — Argos opera sob `lex-issue-driven`, `lex-pr-quality`, `lex-cloudevents`, `lex-restful-apis` e demais já existentes; o que falta é orquestração, não regra.

### Mapeamento de fluxo

```
cry-review-pr <PR#>
  └─→ warrior-argos
        ├─ Fase 0: Coleta
        │   ├─ kata-mcp-github-read   → PR (view, diff, checks), Issue linkada
        │   ├─ kata-mcp-notion-read   → PRD + Capability Spec referenciados
        │   ├─ leitura local           → docs/issues/issue-{N}/* se existir
        │   │                          → .claude/plans/plan-NNN-*.md se referenciado
        │   └─ detecção de stack       → analisa paths do diff
        │
        ├─ Fase 1: Worktree isolado
        │   └─ kata-git-worktree       → .worktrees/review-pr-<N>/
        │
        ├─ Fase 2: Revisão multi-eixo (paralela onde possível)
        │   ├─ A — Implementação técnica
        │   │   ├─ kata-python-review        (se *.py no diff)
        │   │   ├─ kata-frontend-review      (se *.ts/*.tsx/*.css/*.vue)
        │   │   ├─ kata-aws-review           (se *.tf/*.yaml IaC)
        │   │   ├─ kata-api-design-review    (se openapi*.yaml)
        │   │   └─ kata-events-review        (se events.md ou publishers/consumers tocados) ← NOVO
        │   │
        │   ├─ B — Alinhamento com specs
        │   │   ├─ AC da Issue ↔ código + testes
        │   │   ├─ PRD (Notion) ↔ funcionalidade entregue
        │   │   ├─ Capability Spec ↔ contratos públicos
        │   │   └─ Plan referenciado ↔ steps marcados
        │   │
        │   ├─ C — Testes locais
        │   │   ├─ pytest / vitest / cargo test (conforme stack)
        │   │   ├─ mypy --strict / tsc --noEmit
        │   │   └─ smoke endpoints públicos tocados
        │   │
        │   ├─ D — Retrocompatibilidade
        │   │   ├─ oasdiff old vs new openapi.yaml
        │   │   ├─ diff schema CloudEvents (campos retirados, type renomeado)
        │   │   ├─ squawk em migrations (lex-migrations-reversible)
        │   │   └─ comparação de símbolos públicos exportados
        │   │
        │   ├─ E — Segurança
        │   │   └─ kata-security-review
        │   │
        │   └─ F — Lexis/Codex compliance
        │       └─ scan do diff contra Lexis aplicáveis (lista codificada no warrior)
        │
        ├─ Fase 3: Consolidação
        │   ├─ findings agregados em 2 severidades (🔴 BLOCKER / 🟡 WARNING)
        │   ├─ cita arquivo:linha + Lexis/Codex violado
        │   ├─ marker idempotente <!-- argos-review-id:sha256(pr_number+commit_sha) --> (re-run híbrido)
        │   ├─ gh pr review --request-changes  se ≥1 BLOCKER ou ≥1 WARNING
        │   ├─ gh pr review --comment           se 0 findings
        │   └─ nunca --approve (humano decide aprovação)
        │
        └─ Fase 4: Cleanup
            └─ git worktree remove
```

## Escopo

### Artefatos a criar (todos em pt-BR + es + en por `lex-framework-language`)

| # | Tipo    | Nome                  | Path                                                                              |
|---|---------|-----------------------|-----------------------------------------------------------------------------------|
| 1 | Kata    | `kata-events-review`  | `framework/{lang}/engineering/platform/katas/kata-events-review.md`               |
| 2 | Warrior | `warrior-argos`       | `framework/{lang}/engineering/quality/warriors/warrior-argos.md`                  |
| 3 | Cry     | `cry-review-pr`       | `framework/{lang}/engineering/quality/cries/cry-review-pr.md`                     |

> Subclade `engineering/quality` para Argos e Cry porque revisão é atributo de qualidade, não plataforma; `engineering/platform` para `kata-events-review` (par com `kata-api-design-review` que está em `engineering/platform/katas/`).

### Artefatos a atualizar (cross-references)

| # | Tipo  | Nome                       | Mudança                                                                                       |
|---|-------|----------------------------|-----------------------------------------------------------------------------------------------|
| 4 | Kata  | `kata-api-design-review`   | Adicionar referência a `kata-events-review` na seção *Referências* (irmão simétrico)          |
| 5 | Kata  | `kata-events-doc`          | Adicionar referência a `kata-events-review` (par autoria/revisão)                              |
| 6 | Lexis | `lex-cloudevents`          | Em *Validação Automatizada*, citar `kata-events-review` como ferramenta de PR review          |

### Sem novas Lexis nesta rodada

Argos não cria regra nova — orquestra enforcement de regras existentes. Se evoluirmos para "toda PR sem fluxo Athena exige Argos antes do merge", aí sim entraria `lex-pr-review-required` em plano futuro.

### Sem entradas em `framework/platforms.yaml`

`lex-platforms-rules` exige entrada apenas para Lexis e Codex. Katas/Warriors/Cries são propagados pelo sync `python scripts/install.py --self --target . --platform claude-code` e Make.

## Decisões (fechadas com o usuário)

### D1+D2 — Verdict policy e severidades

Argos publica review via `gh pr review` com regra:

| Findings | Ação no `gh` |
|----------|--------------|
| 0 BLOCKER e 0 WARNING | `--comment` (review informativo) |
| ≥1 BLOCKER **ou** ≥1 WARNING | `--request-changes` |
| qualquer cenário | **nunca** `--approve` (aprovação é exclusivamente humana) |

**Duas severidades** (não três):

- 🔴 **BLOCKER** — MUST ser corrigido **neste** PR antes do merge. Exemplo: violação de Lexis com HARD-GATE, AC não coberto, breaking change não documentado, ausência de Issue (`lex-issue-first`).
- 🟡 **WARNING** — pode ser contestado pelo autor e diferido para um **follow-up PR** (com Issue própria). Exemplo: símbolo público alterado sem `__all__` declarado, `oasdiff` não instalado, cobertura de teste abaixo do threshold mas com justificativa.

Tags `INFO` / `MINOR` ficam fora do template — Argos só reporta o que tem ação.

### D3 — Ausência de Issue é HARD-GATE

PR sem Issue linkada (`Closes #N` / `Refs #N` no body) gera finding 🔴 BLOCKER citando `lex-issue-first`. O eixo B (alinhamento com specs) imediatamente para — sem Issue, não há AC, não há PRD a consultar.

PR sem PRD / sem `docs/issues/issue-{N}/` mas **com** Issue linkada: cada eixo reporta `not applicable: missing prerequisite` na sub-checagem afetada e prossegue. Isso vira 🟡 WARNING (não BLOCKER) — Issue mínima é suficiente para começar; PRD/Capability Spec elevam a qualidade da review.

### D4 — Bootstrap de deps automático

Argos detecta e tenta nesta ordem:

1. `make bootstrap` (se `Makefile` tem o target)
2. `poetry install` (se `pyproject.toml` com `[tool.poetry]`)
3. `pip install -e .` (se `pyproject.toml` PEP 621)
4. `npm ci` ou `yarn install` ou `pnpm install` (conforme lockfile)
5. `cargo build` (se `Cargo.toml`)
6. `bundle install` (se `Gemfile`)

Se nenhum aplica ou todos falham: eixo C reporta `tests skipped: bootstrap failed: <stderr-da-última-tentativa>` como 🟡 WARNING e a review prossegue com os outros eixos.

### D5 — Re-run híbrido (marker por commit SHA)

Marker no review-comment: `<!-- argos-review-id:sha256(pr_number+commit_sha) -->`.

| Cenário | Comportamento |
|---------|---------------|
| Re-run com mesmo `commit_sha` (PR head não mudou) | **Edita** o comment existente — review único, sempre refletindo estado atual. |
| Re-run após autor pushar novo commit (`commit_sha` mudou) | **Cria** comment novo. Comments anteriores ficam como audit trail (review do commit X, review do commit Y). |

Antes de criar/editar, Argos lista comments do PR via `gh api repos/{owner}/{repo}/issues/{pr}/comments`, busca por marker que case com `pr_number+commit_sha` atual.

## Steps

- [x] **1.** Abrir Issue de feature-request (`lex-issue-first`, `lex-issue-quality`) com template apropriado, labels (`feature request ➕`, `quality`), Issue Type `Feature`, assignee, e Why/What/How preenchidos. Atualizar front-matter deste plano com `issue: "guardiatechnology/ahrena#<N>"`.
- [ ] **2.** Criar worktree e branch `feat/<N>-warrior-argos-pr-reviewer` (`lex-git-worktrees`, `lex-git-branches`) em `.worktrees/<N>-warrior-argos-pr-reviewer/`.
- [ ] **3.** Pre-flight: confirmar que `gh`, `git`, `python3`, `oasdiff`, `squawk` estão disponíveis no PATH; se faltar algum, documentar a degradação esperada (ex: sem `oasdiff` → eixo D pula breaking-change check de OpenAPI). Decisões 1–5 já fechadas neste plano (seção *Decisões*).
- [ ] **4.** Criar `framework/{pt-BR,es,en}/engineering/platform/katas/kata-events-review.md` — template de revisão de CloudEvents: checa `type` (regex `event.guardia.{module}.{entity_type}.{event_name}`), `idempotencykey` presente, payload `data` versus catálogo `entities/`, snake_case (`lex-entity-naming`), tamanho < 12KB, breaking change detection (campo retirado, type renomeado, schema estreitado). Espelha estrutura de `kata-api-design-review`.
- [ ] **5.** Criar `framework/{pt-BR,es,en}/engineering/quality/warriors/warrior-argos.md` — orquestrador das 6 fases. Inclui:
  - Lista de Lexis aplicáveis para o eixo F (compliance scan) — `lex-python-typing`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object`, `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-restful-apis`, `lex-cloudevents`, `lex-entity-naming`, `lex-idempotency`, `lex-error-handling`, `lex-auth`, `lex-aws-iac`, `lex-aws-security`, `lex-aws-cost`, `lex-migrations-reversible`, `lex-data-retention`, `lex-observability-required`, `lex-logging-decorator`, `lex-dry`.
  - Heurística de detecção de stack (paths → katas a invocar).
  - Output template do review-comment.
  - Política de marker idempotente.
- [ ] **6.** Criar `framework/{pt-BR,es,en}/engineering/quality/cries/cry-review-pr.md` — entrypoint humano: `cry-review-pr <PR#> [--repo owner/name]`. Invoca `warrior-argos` com o número da PR.
- [ ] **7.** Atualizar `kata-api-design-review` (3 línguas): adicionar referência cruzada a `kata-events-review` na seção *Referências*.
- [ ] **8.** Atualizar `kata-events-doc` (3 línguas): adicionar referência cruzada a `kata-events-review` na seção *Referências* (par autoria/revisão).
- [ ] **9.** Atualizar `lex-cloudevents` (3 línguas): em *Validação Automatizada*, mencionar `kata-events-review` como ferramenta de revisão pós-PR.
- [ ] **10.** Sync local: `python3 scripts/install.py --self --target . --platform claude-code` e `python3 scripts/install.py --self --target . --platform cursor` (regenera `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `.cursor/`).
- [ ] **11.** Smoke test manual: rodar `cry-review-pr` em uma PR aberta e verificar (a) coleta de contexto, (b) detecção de stack, (c) execução dos katas certos, (d) consolidação no review-comment, (e) idempotência em re-run.
- [ ] **12.** Auto-revisão dos artefatos com `kata-artifact-self-review` antes do PR.
- [ ] **13.** Commit em commits atômicos (`lex-small-commits`, `lex-conventional-commits`, `lex-commit-language`, `lex-signed-commits`):
  - `feat(quality): add kata-events-review for CloudEvents PR review`
  - `feat(quality): add warrior-argos and cry-review-pr for multi-axis PR review`
  - `docs(quality): cross-reference kata-events-review in api-design-review, events-doc, lex-cloudevents`
  - `chore(claude): regenerate .claude/ and .cursor/ via install.py --self`
- [ ] **14.** Abrir PR (`kata-contributing-pr`, `lex-pr-quality`): mirror labels da Issue, size label, assignee `@me`, reviewer via `.github/CODEOWNERS`, body com `Closes #<N>`.
- [ ] **15.** Após merge: marcar plano `status: done`, mover para `archived/` e remover worktree (`git worktree remove`).

## Dependencies

- Nenhum plano anterior bloqueante.
- `kata-events-review` (Step 4) é dependência interna de `warrior-argos` (Step 5) — Steps 4 → 5 são sequenciais.
- Steps 7–9 (cross-references) podem rodar em paralelo após Steps 4–6.

## Risks

| Risco | Mitigação |
|-------|-----------|
| Sobreposição com Athena Gate 2 gera ruído (mesma checagem rodando 2x) | Argos é pós-PR sob demanda; Athena é pré-PR no fluxo Issue-Driven. Documentação clara no warrior + cry separa explicitamente os dois momentos. |
| Notion MCP indisponível no momento da review | `lex-mcp` Rule 4 (fallback graceful): retry once, depois eixo B reporta `not applicable: notion mcp unavailable` sem bloquear o resto da review. |
| Bootstrap de deps falha em projeto com setup complexo (Docker exigido, monorepo) | Eixo C reporta `tests skipped: bootstrap failed` com stderr; review prossegue com os outros eixos. Não bloquear. |
| Detecção de breaking change em símbolos exportados é heurística (Python sem schema público formal) | Limitar a (a) `__all__` quando declarado, (b) símbolos importados em `tests/` como proxy de "API pública usada". Reportar como 🟡 major (não 🔴 blocker) — sinaliza, não bloqueia. |
| `oasdiff` / `squawk` não instalados no ambiente do reviewer | Detectar e degradar — eixo D reporta `oasdiff not installed: install via brew/cargo` em vez de falhar. |
| Re-run em PR muito ativa (rebase frequente) gera comments duplicados | Marker idempotente baseado em `pr_number + commit_sha` (decisão 5). Mesmo commit → update; commit novo → comment novo (histórico preservado). |
| Argos tenta `gh pr review --approve` indevidamente | Política codificada (D1+D2): apenas `--comment` ou `--request-changes`. Approve fica exclusivamente humano — verificação no kata-events-review e no warrior. |
| Falsa-positividade alta gera fadiga (autor recebe `--request-changes` em demasia) | 2 severidades estritas. Findings duvidosos viram 🟡 WARNING (contestável + diferível para follow-up PR). Após 30 dias de uso real, revisar precisão por amostragem antes de promover findings borderline para BLOCKER. |

## Critérios de aceitação

- [ ] AC-1: `cry-review-pr <PR#>` em uma PR Python típica produz review-comment estruturado com pelo menos os eixos A, C, F preenchidos.
- [ ] AC-2: PR que altera `events.md` ou publisher/consumer de CloudEvents dispara `kata-events-review` e detecta `type` fora do regex como 🔴 blocker.
- [ ] AC-3: PR sem Issue linkada gera finding 🔴 citando `lex-issue-first` no eixo B.
- [ ] AC-4: Re-run de `cry-review-pr` no mesmo commit atualiza o review-comment existente (mesmo marker), não cria duplicata.
- [ ] AC-5: Notion MCP indisponível → eixo B reporta `not applicable: notion mcp unavailable`, demais eixos prosseguem.
- [ ] AC-6: PR com `openapi.yaml` que remove um campo público é detectada por `oasdiff` no eixo D e reportada como 🔴 breaking change.
- [ ] AC-7: Artefatos existem em pt-BR, es, en com equivalência estrutural (`lex-framework-language`).
- [ ] AC-8: `kata-events-review` é referenciado em `kata-api-design-review`, `kata-events-doc` e `lex-cloudevents` (cross-refs).