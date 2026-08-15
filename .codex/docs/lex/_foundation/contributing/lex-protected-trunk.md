# Lexis: Trunk Branches São Protegidos contra Escrita Direta

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Branches trunk (`main`, `master`, `release/*`) em todos os repositórios Guardia

## Lei

> **Trunk branches (`main`, `master`, `release/*`) DEVEM ser protegidas contra escrita direta. Todo desenvolvimento DEVE iniciar em uma branch criada conforme `lex-git-branches` (`{type}/{N}-{slug}`) e o código DEVE chegar ao trunk exclusivamente através de Pull Request mergeado, com a issue associada referenciada por `Closes #N` ou `Refs #N` (`lex-issue-first`) e todos os checks de CI obrigatórios aprovados. Push direto, commit direto na working copy do trunk, force-push, bypass de admin e edição via web UI no trunk são PROIBIDOS.**

## Exemplos

### Correto

```
# Issue #42 aberta com template e labels (lex-issue-quality)
git checkout main
git pull
git checkout -b feat/42-oauth2-authentication
# ... implementação, commits atômicos assinados (lex-small-commits, lex-signed-commits) ...
git push -u origin feat/42-oauth2-authentication
gh pr create --base main --head feat/42-oauth2-authentication --title "feat(auth): add OAuth2 authentication" --body "Closes #42"
# Revisão aprovada, CI verde, merge via UI/CLI; main avança apenas pelo merge commit do PR.
```

### Incorreto

```
# ❌ Commit direto na working copy de main
git checkout main
git commit -am "fix: small typo"
git push origin main
# Mesmo com issue associada, o trunk recebeu escrita fora de PR — VIOLA A LEI.

# ❌ Force push em main para "limpar histórico"
git push --force origin main

# ❌ Edição via web UI em arquivo do trunk sem abrir PR
# (GitHub permite quando a proteção está desabilitada — VIOLA A LEI)

# ❌ Admin bypass para mergear PR sem revisão obrigatória
gh pr merge 19 --admin
```

## Validação Automatizada

- **Ferramenta:**
  - GitHub Branch Protection Rules em `main`, `master`, `release/*`: `required_pull_request_reviews` (≥1 aprovação), `required_status_checks` (CI obrigatório), `allow_force_pushes: false`, `allow_deletions: false`, `enforce_admins: true`, `required_linear_history` opcional, `required_conversation_resolution: true`.
  - GitHub Actions workflow auditando o histórico: detecta commits no trunk cujo `parent count` ≠ 2 (não-merge) e cujo SHA não é tip de PR mergeado, falhando o pipeline e abrindo alerta.
  - `kata-quality-gate` (Phase 6 do Issue-Driven flow) verifica que a branch não é `main`/`master`/`release/*` antes de prosseguir.
- **Momento:** configuração no setup do repositório; auditoria contínua a cada push para o trunk; verificação no Gate 2.
- **Métrica:** 0 commits non-merge no trunk fora de PR aprovado; 100% dos repositórios Guardia com Branch Protection Rules configuradas conforme especificação; 0 incidentes de admin bypass não documentados em post-mortem.
