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

## Identidade de autor: humano vs bot

Projetos Ahrena escolhem como commits e PRs conduzidos por warriors são atribuídos: como o ser humano contribuinte (padrão) ou como a identidade do GitHub App `ahrena-bot[bot]` (opt-in).

### Modo padrão — autor humano

Quando `bot_author.enabled` é `false` (ou a seção está ausente do `.ahrena/.directives`), os warriors fazem commit usando a identidade git e a chave GPG do desenvolvedor, exatamente como se um ser humano tivesse digitado os comandos. `git log --pretty='%an <%ae>'` mostra o desenvolvedor; os PRs aparecem sob o login do GitHub do desenvolvedor. Este é o comportamento histórico; atualizar o framework não altera nada.

| Aspecto | Padrão (autor humano) |
|---------|-----------------------|
| Autor do commit | `user.name` / `user.email` do desenvolvedor |
| Assinatura do commit | Chave GPG do desenvolvedor (por `lex-signed-commits`) |
| Autor do PR no GitHub | Login GitHub do desenvolvedor |
| `gh pr view` | `Author: <login-do-desenvolvedor>` |
| Trilha de auditoria | Cada contribuinte aparece individualmente nos commits e PRs |

### Modo opt-in — autor bot

Quando `bot_author.enabled` é `true`, os warriors listados em `bot_author.apply_to` invocam `scripts/ahrena-auth.sh` antes de cada `git commit` / `gh pr create`. O script troca as credenciais do GitHub App Ahrena por um token de instalação de curta duração e exporta a identidade do bot para o shell que invocou:

```
GH_TOKEN_AHRENA_BOT=<installation-token>
GIT_AUTHOR_NAME=ahrena-bot[bot]
GIT_AUTHOR_EMAIL=<numeric-user-id>+ahrena-bot[bot]@users.noreply.github.com
GIT_COMMITTER_NAME=ahrena-bot[bot]
GIT_COMMITTER_EMAIL=<igual ao autor>
```

Commits produzidos sob esta identidade são assinados no servidor pelo token de instalação do App (não é necessária chave GPG na máquina do desenvolvedor para a identidade do bot). Quando `bot_author.commit_co_author` é `human`, o body do commit carrega `Co-authored-by: <nome humano> <email humano>` para que a pessoa que conduziu o trabalho permaneça rastreável.

| Aspecto | Opt-in (autor bot) |
|---------|--------------------|
| Autor do commit | `ahrena-bot[bot]` |
| Assinatura do commit | Assinada no servidor pelo token de instalação do GitHub App |
| Autor do PR no GitHub | `ahrena-bot[bot]` |
| `gh pr view` | `Author: ahrena-bot[bot]` |
| Trailer de coautor | `Co-authored-by: <humano>` (quando `commit_co_author=human`) |
| Trilha de auditoria | Bot vs humano é respondido pela UI do GitHub sem precisar parsear trailers |

### Trade-offs

- **Autor bot** — separação mais clara entre contribuições conduzidas por humanos e por agentes, trilha de auditoria mais simples na camada de identidade, sem GPG na máquina do desenvolvedor para os commits do bot e sinal limpo para ferramentas de cost tracking e revisão de PR que já reconhecem identidades de bot. Requer registrar o GitHub App `ahrena-bot` e provisionar as credenciais.
- **Autor humano** — preserva o reconhecimento por contribuinte no `git log`, mantém o fluxo GPG existente e remove uma peça móvel para desenvolvedores solo ou projetos em que o ser humano é o único remetente. Não requer registro adicional de GitHub App.

### Opt-out por warrior

`bot_author.apply_to` é uma lista de nomes de warriors. Apenas os warriors nessa lista chamam o resolver de auth; warriors omitidos da lista mantêm o comportamento de autor humano mesmo quando a chave mestra está ativada. Isso permite adoção parcial (por exemplo, autor bot para `apollo` e `hephaestus` enquanto `iris` mantém a identidade do desenvolvedor).

### Commits fora de banda

Um commit digitado diretamente pelo ser humano (sem envolvimento de warrior) mantém a identidade do desenvolvedor independentemente da diretiva — o resolver de auth só dispara quando um warrior encapsula o commit. A diretiva governa a atribuição via warrior, não invocações diretas de `git commit`.

### Armazenamento de credenciais

As credenciais do GitHub App seguem a mesma convenção de armazenamento de `scripts/argos/auth.sh`:

| Fonte | Usado quando |
|-------|--------------|
| Variáveis de ambiente (`AHRENA_BOT_APP_ID`, `AHRENA_BOT_INSTALLATION_ID`, `AHRENA_BOT_PRIVATE_KEY_PATH`) | Ambientes de CI / não-interativos |
| Keychain do macOS (entrada `security` `ahrena.bot.github-app`) | Desenvolvimento local em macOS |
| `.env.local` na raiz do repositório | Desenvolvimento local em Linux/Windows |

Credenciais NUNCA são enviadas ao repositório em um commit; o resolver de auth materializa as credenciais apenas no ambiente do shell que invocou, nunca no stdout ou em logs.

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
