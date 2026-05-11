---
plan_id: "003"
title: "lazy-load-planning-lexis"
status: done
agent: claude
issue: "guardiatechnology/ahrena#46"
pr: "guardiatechnology/ahrena#47"
created_at: "2026-05-05T17:00:00Z"
updated_at: "2026-05-11T22:28:15Z"
---

# Plano: Lazy-load de Lexis de planejamento/contributing no Claude Code

## Objetivo

Estender a PR #47 (issue #46) com Fase 2: declarar `paths:` para Lexis do contexto de planejamento/contributing que ainda carregam eager. Reduzir mais ~7–8k tokens em sessões fora desses contextos. Mesma branch `chore/46-lazy-load-domain-lexis`.

## Contexto

A Fase 1 (commits anteriores nesta branch) cobriu Lexis de domínio (Python, AWS, Mobile, Data, SRE, Platform, Frontend testing/security, Observability). Restam ~13 Lexis de foundation/contributing que carregam eager mas têm triggers ambientais claros (templates de issue/PR, COMMIT_EDITMSG, .checkpoint, plans existentes, docs/issues/). Declarar `paths:` para essas Lexis preserva enforcement quando o agente está no contexto certo, e libera contexto fora dele.

Lexis verdadeiramente always-on (lex-directives, lex-tone, lex-mcp, lex-terminal-type, lex-pilars, lex-naming, lex-template-usage, lex-framework-language, lex-platforms-rules, lex-brand-voice, lex-language*, lex-dry) **continuam eager** — agente decide se aplicam antes de ler qualquer arquivo.

## Escopo

**Editar:**
- `framework/platforms.yaml` (seção `claude-code.rules`) — adicionar/atualizar entries

**Lexis a receber `paths:`:**

### Process
- `_foundation/process/lexis/lex-agent-planning` — `[".claude/plans/**", "**/plan-*.md"]`
- `_foundation/process/lexis/lex-checkpoint` — `["**/.checkpoint"]`

### Issue/PR templates
- `_foundation/contributing/lexis/lex-issue-quality` — `[".github/ISSUE_TEMPLATE/**"]`
- `_foundation/contributing/lexis/lex-issue-first` — `[".github/ISSUE_TEMPLATE/**", ".github/PULL_REQUEST_TEMPLATE*.md"]`
- `_foundation/contributing/lexis/lex-pr-quality` — `[".github/PULL_REQUEST_TEMPLATE*.md", ".github/CODEOWNERS"]`

### Branch / worktree / trunk
- `_foundation/contributing/lexis/lex-git-branches` — `[".github/CODEOWNERS", ".github/workflows/**.yml"]`
- `_foundation/contributing/lexis/lex-git-worktrees` — `[".github/CODEOWNERS", ".gitignore"]`
- `_foundation/contributing/lexis/lex-protected-trunk` — `[".github/CODEOWNERS", ".github/workflows/**.yml"]`

### Commits
- `_foundation/contributing/lexis/lex-conventional-commits` — `["**/COMMIT_EDITMSG", ".commitlintrc*", ".github/workflows/**commit**.yml"]`
- `_foundation/contributing/lexis/lex-commit-language` — mesmo
- `_foundation/contributing/lexis/lex-small-commits` — mesmo
- `_foundation/contributing/lexis/lex-signed-commits` — mesmo

### Versioning
- `_foundation/contributing/lexis/lex-semantic-version` — `["package.json", "**/__version__.py", "CHANGELOG*", ".bumpversion*"]`

### Issue-driven flow
- `engineering/workflow/lexis/lex-issue-driven` — `["docs/issues/**", ".ahrena/workflow/**"]`

**Total: 13 Lexis recebem `paths:`.**

**Fora de escopo:**
- Cursor (já configurado)
- Lexis always-on (foundation transversais que não têm trigger ambiental)
- Hooks/CI guard-rails para enforcement complementar (issue própria, fora desta PR)

## Steps

- [x] 1. Criar plan-003 com status `in-progress`
- [ ] 2. Mapear quais entries já existem em `claude-code.rules` (vs precisam ser criados)
- [ ] 3. Editar `framework/platforms.yaml` adicionando `paths:` (atualizar existentes + criar novos)
- [ ] 4. Rodar `python3 scripts/install.py --self --platform claude-code --local`
- [ ] 5. Validar 100% dos arquivos com paths como YAML válido
- [ ] 6. Commit atômico na branch atual
- [ ] 7. Push (vai para PR #47 existente)
- [ ] 8. Atualizar body do PR #47 com escopo expandido

## Riscos

- **Trigger ambiental fraco** — se agente vai criar issue do zero (sem ler template), `lex-issue-quality` não dispara. Mitigação: cobrir via Skills (`kata-contributing-issue`) em fase futura ou via guard-rails CI/hooks.
- **Lex-checkpoint com glob `**/.checkpoint`** — depende do `.checkpoint` já existir; em sessão zero não dispara. Aceitável (no flow normal o arquivo existe quando há checkpoint a recuperar).
- **Globs de commits (COMMIT_EDITMSG)** — só disparam durante operação de commit interativa; em commit não-interativo (ex: `gh` ou hook) o agente pode não ler. Mitigação: enforcement via commitlint (já existe) é o guard-rail real.

## Dependências

- PR #47 ainda aberta (não merge antes desta extensão)
- Branch `chore/46-lazy-load-domain-lexis` ativa
- `scripts/install.py` já corrigido (commit 15325ce)

## Verificação

1. Antes: contar Lexis eager restantes → meta ≤ 18
2. Depois do sync: cada uma das 13 Lexis acima tem frontmatter `paths:` válido em `.claude/rules/`
3. Controle: `lex-tone`, `lex-mcp`, `lex-directives` continuam SEM paths
