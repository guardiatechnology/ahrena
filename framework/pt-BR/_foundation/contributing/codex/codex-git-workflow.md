# Codex: Fluxo de Trabalho Git

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Fluxo completo de contribuição git — Issue → Branch → Commits → PR → Merge

## Propósito

Este Codex descreve o fluxo de trabalho git canônico para todos os repositórios Guardia. Ele conecta as Lexis individuais em uma referência única de ponta a ponta, para que desenvolvedores e agentes possam seguir o ciclo completo de contribuição sem consultar cada artefato separadamente.

## Visão Geral do Fluxo

```
Issue → Branch → Commits → PR → Revisão → Merge
```

Cada etapa é regida por pelo menos uma Lexis. Pular uma etapa viola o fluxo.

## Etapa 1 — Issue (`lex-issue-first`)

**Regra:** Nenhum branch sem uma Issue.

1. Verifique se já existe uma Issue para o trabalho planejado.
2. Se não existir: abra uma usando `kata-contributing-issue` (ou o cry correspondente: `cry-new-feature-request`, `cry-new-epic`, etc.).
3. A Issue DEVE descrever: **o quê** (objetivo), **por quê** (motivação e impacto), **resultado esperado** (critérios de aceitação).
4. Anote o número da Issue — ele é obrigatório para o nome do branch.

**Templates disponíveis (`.ahrena/contributing_templates/`):**

| Tipo | Template |
|------|----------|
| Feature request | `feature-request.md` |
| Epic | `epic.md` |
| User story (API) | `user-story-for-api.md` |
| User story (frontend) | `user-story-for-frontend.md` |

## Etapa 2 — Branch (`lex-git-branches`)

**Formato:** `{type}/{issue-number}-{slug}`

```bash
git checkout main
git pull origin main
git checkout -b feat/42-oauth2-authentication
```

**Tipos válidos:** `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test`

| Exemplo | Tipo |
|---------|------|
| `feat/42-oauth2-authentication` | Nova funcionalidade |
| `fix/123-null-pointer-in-transaction` | Correção de bug |
| `chore/89-update-rust-dependencies` | Manutenção |
| `docs/201-contributing-guide-revision` | Documentação |
| `refactor/77-extract-payment-service` | Refatoração |

## Etapa 3 — Commits

Quatro Lexis regem cada commit:

| Lexis | Regra |
|-------|-------|
| `lex-conventional-commits` | Formato: `{type}[scope]: {description}` |
| `lex-signed-commits` | Todo commit DEVE ser assinado com GPG (`-S` ou `commit.gpgsign true`) |
| `lex-small-commits` | Uma mudança lógica por commit (atômico) |
| `lex-commit-language` | Subject em inglês; body PODE usar tag `[lang]` |

### Formato do commit

```
{type}[scope opcional]: {descrição em inglês}

[body opcional — use tag [lang] para idioma local]

[footer opcional: Closes #N, BREAKING CHANGE: ...]
```

### Exemplos

```bash
# ✅ Correto: atômico, assinado, convencional, subject em inglês
git commit -S -m "feat(auth): add OAuth2 client configuration"
git commit -S -m "test(auth): add unit tests for OAuth2 flow"

# ❌ Incorreto: mudanças mistas, sem assinatura
git commit -m "add OAuth2, fix header bug, update README"
```

### Configuração de assinatura automática

Consulte `kata-setup-gpg-signing` para configurar a assinatura GPG automática. Após configurado:

```bash
# git assina automaticamente — sem necessidade do -S
git commit -m "feat(auth): implement token refresh"
```

## Etapa 4 — Pull Request (`lex-issue-first`)

1. Envie o branch:
   ```bash
   git push -u origin feat/42-oauth2-authentication
   ```
2. Abra o PR usando `kata-contributing-pr` ou `gh pr create`.
3. Título do PR: formato Conventional Commits em inglês.
4. Corpo do PR DEVE incluir `Closes #N` ou `Refs #N`.

### Estrutura do corpo do PR

```markdown
## Description
{resumo da mudança}

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Related Issues
Closes #42

## How Has This Been Tested?
{descreva testes locais ou verificações automatizadas}

## Checklist
- [ ] Commits são assinados (GPG Verified)
- [ ] Testes existentes passam
- [ ] Novos testes adicionados para novos comportamentos
- [ ] Sem mudanças fora do escopo
```

## Etapa 5 — Revisão e Merge

Requisitos para merge:

- Mínimo 1 aprovação de um mantenedor (conforme CODEOWNERS).
- Todos os checks de CI passam.
- Todos os commits mostram **Verified** (assinados com GPG).
- Sem conflitos de merge com `main`.
- PR referencia uma Issue.

Após o merge: `main` é atualizado; o branch é excluído.

## Releases (`lex-semantic-version`)

Releases seguem o Versionamento Semântico (`MAJOR.MINOR.PATCH`). As tags DEVEM ser assinadas:

```bash
git tag -s v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

Breaking changes incrementam `MAJOR`. Novas features incrementam `MINOR`. Correções incrementam `PATCH`.

## Referências

| Artefato | Propósito |
|----------|-----------|
| `lex-issue-first` | Toda mudança deve originar-se de uma Issue |
| `lex-git-branches` | Nomenclatura de branch: `{type}/{issue-number}-{slug}` |
| `lex-conventional-commits` | Formato de mensagem de commit |
| `lex-signed-commits` | Requisito de assinatura GPG |
| `lex-small-commits` | Commits atômicos |
| `lex-commit-language` | Subject em inglês |
| `lex-semantic-version` | Tagging de releases |
| `kata-setup-gpg-signing` | Configurar assinatura GPG |
| `kata-contributing-issue` | Abrir uma Issue no GitHub |
| `kata-contributing-pr` | Abrir um Pull Request |
| `codex-contributing` | Visão geral do processo de contribuição |
