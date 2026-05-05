---
plan_id: "002"
title: "lazy-load-domain-lexis"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#46"
created_at: "2026-05-05T16:00:00Z"
updated_at: "2026-05-05T16:15:00Z"
---

# Plano: Lazy-load de Lexis de domínio no Claude Code via `paths:`

## Objetivo

Reduzir o consumo de tokens do framework Ahrena no Claude Code declarando `paths:` (glob patterns) no frontmatter das Lexis de domínio em `framework/platforms.yaml`, para que sejam carregadas apenas quando o agente lê arquivos relevantes ao domínio. Hoje 64+ Lexis carregam sempre; meta é reduzir para ~30 carregadas eager (foundation/transversais), com o restante lazy.

## Contexto

A doc oficial do Claude Code (https://code.claude.com/docs/en/memory.md) confirma que `.claude/rules/*.md` suportam `paths:` no frontmatter como mecanismo nativo de lazy-load. Auditoria do `framework/platforms.yaml` + `scripts/install.py:transform_md_to_claude_rule` mostra que:

- O esquema `claude-code.rules.<key>.paths` já é aceito e injetado no frontmatter dos arquivos gerados
- Algumas Lexis já estão configuradas (frontend, brand visual, design-system)
- ~30 Lexis de domínio (Python, AWS, Mobile, Data, SRE, Platform, Frontend faltantes, Quality testing, Observability) ainda não declaram `paths:`

Portanto a mudança é puramente declarativa: editar `framework/platforms.yaml` adicionando `paths:` nos entries listados em "Steps". Não altera `scripts/`, não move arquivos, não muda pilar (Lexis continua Lexis — sem violar `lex-pilars`).

## Escopo

**Único arquivo a editar:**
- `framework/platforms.yaml` (seção `claude-code.rules`)

**Arquivos verificados pós-sync (não editados manualmente — gerados):**
- `.claude/rules/engineering/backend/lex-python-*.md`
- `.claude/rules/engineering/devops/lex-aws-*.md`
- `.claude/rules/engineering/mobile/lex-mobile-*.md`
- `.claude/rules/engineering/data/lex-*.md`
- `.claude/rules/engineering/platform/lex-*.md`
- `.claude/rules/engineering/quality/lex-test-*.md`
- `.claude/rules/engineering/sre/lex-*.md`
- `.claude/rules/engineering/frontend/lex-frontend-{security,testing}.md`
- `.claude/rules/_foundation/quality/lex-{observability-required,logging-decorator}.md`

**Fora de escopo:**
- Cursor (`globs:` em `cursor.rules`) — já configurado, não tocar
- Codex em `.claude/docs/` — já lazy via listagem em CLAUDE.md sem `@import`
- `codex-feature-design-docs` em local errado — fix separado (issue própria)
- Restruturação de warriors — desnecessário (já lazy via Agent tool)

## Steps

- [ ] 1. Criar issue no repo `guardiatechnology/ahrena` seguindo `lex-issue-quality` (template `simple-task`, label `enhancement 🔝`, type `Task`, assignee `@me`); responder Why/What/How
- [ ] 2. Atualizar este plan com o número da issue no front-matter
- [ ] 3. Criar branch `chore/{N}-lazy-load-domain-lexis` (worktree per `lex-git-worktrees`)
- [ ] 4. Ler `framework/platforms.yaml` linhas ~447–560 e mapear quais dos 30 entries abaixo já têm `paths:` (skip) vs faltam (editar)
- [ ] 5. Adicionar `paths:` no `framework/platforms.yaml` para os entries faltantes:
  - **Backend Python (7):** todos `paths: ["**/*.py"]`
    - `engineering/backend/lexis/lex-python-typing`
    - `engineering/backend/lexis/lex-python-security`
    - `engineering/backend/lexis/lex-python-immutability`
    - `engineering/backend/lexis/lex-python-testing`
    - `engineering/backend/lexis/lex-python-error-handling`
    - `engineering/backend/lexis/lex-python-error-object`
    - `engineering/backend/lexis/lex-python-result-type`
  - **DevOps/AWS (3):** `paths: ["**/*.tf", "**/*.hcl", "**/*.cdk.ts", "**/cdk/**", "**/cloudformation/**", "**/cf-*.yaml"]`
    - `engineering/devops/lexis/lex-aws-iac`
    - `engineering/devops/lexis/lex-aws-security`
    - `engineering/devops/lexis/lex-aws-cost`
  - **Mobile (2):** `paths: ["**/*.swift", "**/*.kt", "**/*.java", "**/*.dart", "**/ios/**", "**/android/**"]`
    - `engineering/mobile/lexis/lex-mobile-offline-first`
    - `engineering/mobile/lexis/lex-mobile-platform-parity`
  - **Data (2):**
    - `engineering/data/lexis/lex-migrations-reversible`: `paths: ["**/migrations/**", "**/alembic/**", "**/*migration*", "**/*.sql"]`
    - `engineering/data/lexis/lex-data-retention`: `paths: ["**/migrations/**", "**/models/**", "docs/data-retention.yaml"]`
  - **Platform Guardia (8):**
    - `engineering/platform/lexis/lex-auth`: `paths: ["**/auth/**", "**/*auth*.py", "**/*auth*.ts"]`
    - `engineering/platform/lexis/lex-cloudevents`: `paths: ["**/events/**", "**/*event*.py", "**/*event*.ts"]`
    - `engineering/platform/lexis/lex-entities`: `paths: ["**/entities/**", "**/*entity*.py", "docs/**/entities/**"]`
    - `engineering/platform/lexis/lex-entity-naming`: `paths: ["**/entities/**", "**/*entity*", "docs/**/entities/**"]`
    - `engineering/platform/lexis/lex-error-handling`: `paths: ["**/*.py", "**/*.ts"]`
    - `engineering/platform/lexis/lex-idempotency`: `paths: ["**/api/**", "**/*api*.py", "**/*router*.py", "**/events/**"]`
    - `engineering/platform/lexis/lex-restful-apis`: `paths: ["**/api/**", "**/*api*.py", "**/*router*.py", "**/openapi*.yaml", "docs/**/oas/**"]`
    - `engineering/platform/lexis/lex-feature-design-docs`: `paths: ["docs/**"]`
  - **Quality/Testing (2):** `paths: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts"]`
    - `engineering/quality/lexis/lex-test-pyramid`
    - `engineering/quality/lexis/lex-test-isolation`
    - `engineering/quality/lexis/lex-dry`: **deixar SEM paths** (transversal, qualquer linguagem)
  - **SRE (2):**
    - `engineering/sre/lexis/lex-slo-required`: `paths: ["docs/slo/**", "**/slo/**", "**/*.slo.yaml"]`
    - `engineering/sre/lexis/lex-runbook-for-every-alert`: `paths: ["docs/runbooks/**", "**/runbooks/**", "**/alerts/**", "**/*.alerts.yaml"]`
  - **Frontend faltantes (2):**
    - `engineering/frontend/lexis/lex-frontend-security`: `paths: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.vue", "**/*.svelte"]`
    - `engineering/frontend/lexis/lex-frontend-testing`: `paths: ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx", "**/__tests__/**"]`
  - **Observability (2):**
    - `_foundation/quality/lexis/lex-observability-required`: `paths: ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.go", "**/api/**", "**/handlers/**", "**/jobs/**", "**/consumers/**"]`
    - `_foundation/quality/lexis/lex-logging-decorator`: `paths: ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.go"]`
- [ ] 6. Rodar sync: `python scripts/install.py --sync-claude-code` (confirmar comando via `--help`)
- [ ] 7. Validar 3 arquivos amostra:
  - `head -5 .claude/rules/engineering/backend/lex-python-typing.md` → deve mostrar frontmatter `paths: ["**/*.py"]`
  - `head -5 .claude/rules/engineering/devops/lex-aws-iac.md` → deve mostrar frontmatter `paths:` com lista AWS
  - `head -5 .claude/rules/engineering/quality/lex-dry.md` → deve **não** ter frontmatter `paths:` (controle: continua eager)
- [ ] 8. Contar total: `grep -L "^paths:" .claude/rules/**/lex-*.md | wc -l` deve cair de ~64 para ~30
- [ ] 9. Commit atômico (per `lex-conventional-commits` + `lex-commit-language`): `chore(framework): add paths to domain lexis for claude-code lazy-load`
- [ ] 10. Abrir PR seguindo `lex-pr-quality` (mirror labels da issue, size label, assignee, reviewers via CODEOWNERS)
- [ ] 11. Atualizar status deste plan para `in-progress` no início e `done` ao final; mover para archive após merge

## Lexis que continuam eager (sem `paths:`) — intencional

Foundation transversal (toda sessão precisa):
- `_foundation/process/lex-{directives, checkpoint, agent-planning, naming, platforms-rules}`
- `_foundation/tooling/lex-{mcp, terminal-type}`
- `_foundation/quality/lex-{tone, template-usage, hard-gate-pattern}`
- `_foundation/i18n/lex-framework-language`
- `_foundation/authoring/lex-pilars`
- `_foundation/contributing/*` (todos os 11 — git, issue, commit, PR transversais)
- `documentation/i18n/lex-language*` (4 — i18n obrigatório toda criação)
- `design/brand/lex-brand-voice` (toda comunicação Guardia)
- `engineering/quality/lex-dry` (transversal multi-linguagem)
- `engineering/workflow/lex-issue-driven` (toda issue)

## Funções reusadas (não reimplementar)

- `transform_md_to_claude_rule(content, pilar, rule_config)` — `scripts/install.py:650-674`
- `load_platforms_config()` — `scripts/install.py:216-249`
- `_process_lang_dir_to_claude_code()` — `scripts/install.py:1093`

## Verificação end-to-end

1. **Baseline pré-mudança:** `grep -L "^paths:" .claude/rules/**/lex-*.md | wc -l` (esperado: ~64 sem paths)
2. **Geração correta pós-sync:** `head -5` em 3 arquivos amostra (1 com paths, 1 com paths multi-glob, 1 controle sem paths)
3. **Comportamento real:** abrir 2 sessões Claude Code em diretórios distintos:
   - **Sessão A** (diretório só com `.md` e `.yaml`): `lex-python-*` não deve aparecer no contexto
   - **Sessão B** (diretório Python): `Read foo.py` → `lex-python-typing` deve aparecer
4. **Métrica:** contagem de Lexis carregadas em sessão sem código: meta ≤ 30 (de ~64)

## Dependências

- Issue criada no repo (`lex-issue-first`)
- Branch criado em worktree (`lex-git-worktrees`)
- `scripts/install.py` no estado atual (`transform_md_to_claude_rule` já implementa `paths:`)

## Riscos

- **Glob muito restrito** → Lexis não dispara onde deveria. Mitigação: começar generoso (`**/*.py` em vez de `src/**/*.py`); medir e ajustar.
- **Glob muito amplo** → Lexis carrega quase sempre, perde benefício. Mitigação: revisar pós-deploy via métrica.
- **Paths controversos** (`lex-auth`, `lex-idempotency`, `lex-restful-apis`) — globs heurísticos. Mitigação: review humano por warriors da plataforma (Daedalus, Apollo) no PR.
- **`lex-feature-design-docs` com `paths: ["docs/**"]`** pode disparar em qualquer sessão de doc, não só design feature. Aceitável — escopo dela é exatamente `docs/{context}/`.
