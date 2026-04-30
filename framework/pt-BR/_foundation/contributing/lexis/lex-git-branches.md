# Lexis: Convenção de Nomenclatura de Branches

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrantável | **Escopo:** Todos os branches git em repositórios Guardia

## Lei

> **Todo branch DEVE seguir o formato `{type}/{issue-number}-{kebab-slug}`, onde `type` DEVE ser um dos tipos do Conventional Commits (`feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test`), `{issue-number}` é o número da Issue do GitHub à qual o branch está vinculado, e `{kebab-slug}` é uma descrição breve, em letras minúsculas e separada por hífens. Criar ou enviar um branch sem uma Issue associada é PROIBIDO. Nomes de branch fora deste formato são PROIBIDOS.**

## Cobertura

- **Aplica-se a:** todos os branches de trabalho em todos os repositórios Guardia. As branches trunk (`main`, `master`, `release/*`) **não são branches de trabalho** — são alvos protegidos governados por `lex-protected-trunk` e recebem código apenas via PR mergeado a partir de uma branch nomeada conforme esta Lei.
- **Agentes vinculados:** desenvolvedores, agentes de IA que criam branches (warrior-athena, warrior-apollo, warrior-hephaestus).
- **Exceções:** Nenhuma. Branches fora do formato válido são rejeitados no push.

## Regras

### 1. Formato

```
{type}/{issue-number}-{slug}
```

| Parte | Regra |
|-------|-------|
| `type` | Um de: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `issue-number` | Inteiro positivo correspondente ao número da Issue do GitHub associada |
| `slug` | Letras minúsculas, kebab-case, máximo 50 caracteres; resume a mudança |

### 2. Issue antes do branch

Um branch NÃO DEVE ser criado antes de existir a Issue correspondente. Consulte `lex-issue-first`.

### 3. Trabalho nunca inicia em trunk

Antes de qualquer commit, o desenvolvedor (humano ou IA) **DEVE** verificar a branch ativa via `git rev-parse --abbrev-ref HEAD`. Se for `main`, `master` ou começar com `release/`, **DEVE** criar uma branch de trabalho conforme esta Lei (`git checkout -b {type}/{N}-{slug}`) antes de produzir qualquer mudança. Editar arquivos com a working copy posicionada em trunk é PROIBIDO. Detalhes do regime de proteção em `lex-protected-trunk`.

### 4. Um branch por Issue (padrão)

Cada Issue corresponde tipicamente a um branch. Exceções (múltiplos branches para uma única Issue complexa) exigem justificativa explícita nos comentários da Issue.

## Exemplos

### Corretos

```
feat/42-oauth2-authentication
fix/123-null-pointer-in-transaction
chore/89-update-rust-dependencies
docs/201-contributing-guide-revision
refactor/77-extract-payment-service
test/310-coverage-for-refund-module
ci/95-add-github-actions-lint
```

### Incorretos

```
seguim/wizardly-ptolemy-adb24b   # ❌ nome gerado, sem type, sem número de issue
my-feature                       # ❌ sem type, sem número de issue
wip/auth                         # ❌ wip não é um tipo válido do Conventional Commits
feat-42-oauth2                   # ❌ separador por barra obrigatório entre type e o restante
feat/oauth2-authentication       # ❌ número de issue ausente
```

## Validação Automatizada

- **Ferramenta:** hook pre-push com regex `^(feat|fix|docs|build|chore|ci|style|refactor|perf|test)\/[0-9]+-[a-z0-9][a-z0-9-]{0,49}$`; regras de proteção de branch no GitHub.
- **Quando:** no push do branch para o remoto; na criação do PR.
- **Métrica:** 0 branches no remoto fora do formato definido.
