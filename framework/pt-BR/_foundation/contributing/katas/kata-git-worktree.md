# Kata: Criar e Gerenciar Git Worktree

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação, uso e remoção de git worktrees para tarefas baseadas em branch, conforme `lex-git-worktrees`

## Objetivo

Criar um git worktree isolado para uma tarefa, executar o trabalho dentro dele, abrir o PR e realizar o cleanup após o merge — garantindo que o checkout principal permaneça limpo e que cada tarefa tenha seu ambiente dedicado.

## Quando Usar

- No início de qualquer tarefa que exija um branch dedicado
- Antes de invocar warriors ou katas que produzem código ou artefatos em branches
- Quando o usuário pede "implemente X" e X requer um novo branch
- Ao retomar uma tarefa em andamento que já tem um worktree existente

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Número da issue | Sim | Issue GitHub existente que origina a tarefa (conforme `lex-issue-first`) |
| Tipo do branch | Sim | Um de: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| Slug | Sim | Descrição curta em kebab-case (máx. 50 chars) |
| Nome do repositório | Não | Padrão: nome do diretório raiz do repositório |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Verificar a issue
- [ ] 2. Compor nomes do branch e do diretório
- [ ] 3. Verificar worktrees existentes
- [ ] 4. Criar o worktree
- [ ] 5. Entrar no worktree e executar a tarefa
- [ ] 6. Commitar e abrir PR
- [ ] 7. Realizar cleanup após merge
```

### Passo 1: Verificar a issue

1. Confirmar que a issue GitHub existe e está aberta (conforme `lex-issue-first`)
2. Registrar o número da issue — será parte obrigatória do branch e do diretório
3. Se a issue não existir → parar e solicitar que o usuário crie a issue antes de prosseguir

### Passo 2: Compor nomes do branch e do diretório

Com base nos inputs:

```
branch  = {type}/{issue-number}-{slug}
wtDir   = ../{repo-name}-{issue-number}-{slug}
```

Exemplos:
- Issue #42, tipo `feat`, slug `scheduled-payments-api`
- Branch: `feat/42-scheduled-payments-api`
- Diretório: `../ahrena-42-scheduled-payments-api`

Apresentar ao usuário para confirmação antes de criar.

### Passo 3: Verificar worktrees existentes

```powershell
git worktree list
```

- Se o branch já estiver em uso em um worktree existente → perguntar ao usuário se quer retomar esse worktree (pular para o Passo 5) ou criar um novo
- Se o diretório alvo já existir mas não for um worktree → alertar o usuário e pedir confirmação antes de sobrescrever

### Passo 4: Criar o worktree

**Via Claude Code (preferencial):**

Usar o tool `EnterWorktree` com o branch composto no Passo 2.

**Via CLI (PowerShell):**

```powershell
git worktree add $wtDir -b $branch
```

Confirmar criação:
```powershell
git worktree list
```

### Passo 5: Entrar no worktree e executar a tarefa

```powershell
Set-Location $wtDir
```

Dentro do worktree:
- Executar toda a implementação dentro deste diretório
- Commitar com mensagens no formato Conventional Commits (conforme `lex-conventional-commits`)
- Fazer push do branch regularmente para o remote:
  ```powershell
  git push -u origin $branch
  ```

### Passo 6: Commitar e abrir PR

Quando a tarefa estiver concluída:

1. Garantir que todos os commits estejam feitos e o branch esteja atualizado no remote
2. Abrir o PR referenciando a issue:

```powershell
gh pr create --title "{type}({scope}): {description}" `
             --body "Closes #$issue" `
             --base main `
             --head $branch
```

3. Registrar a URL do PR e comunicar ao usuário

### Passo 7: Realizar cleanup após merge

Após confirmação de que o PR foi mergeado:

```powershell
# 1. Sair do worktree (se dentro dele)
Set-Location ../$repo

# 2. Remover o worktree
git worktree remove $wtDir --force

# 3. Deletar o branch local
git branch -d $branch

# 4. Verificar
git worktree list
```

Confirmar ao usuário: "Worktree `{wtDir}` removido. Branch `{branch}` deletado."

## Outputs

| Output | Descrição |
|--------|-----------|
| Worktree criado | Diretório `../{repo}-{issue-number}-{slug}/` com o branch ativo |
| Branch criado | `{type}/{issue-number}-{slug}` no repositório |
| PR aberto | URL do PR referenciando a issue |
| Cleanup | Worktree e branch removidos após merge |

## Exemplo de Execução

### Input

```
Issue: #42 "Add scheduled payments API"
Tipo: feat
Slug: scheduled-payments-api
Repositório: ahrena
```

### Passo 2 — Nomes compostos

```
Branch:    feat/42-scheduled-payments-api
Diretório: ../ahrena-42-scheduled-payments-api
```

### Passo 4 — Criação

```powershell
git worktree add ../ahrena-42-scheduled-payments-api -b feat/42-scheduled-payments-api
# Preparando worktree (novo branch 'feat/42-scheduled-payments-api')
# HEAD está agora em 4df8e43 Merge pull request #33...
```

### Passo 6 — PR

```powershell
gh pr create --title "feat(payments): add scheduled payments API" `
             --body "Closes #42" --base main --head feat/42-scheduled-payments-api
# https://github.com/guardiatechnology/ahrena/pull/43
```

### Passo 7 — Cleanup

```powershell
git worktree remove ../ahrena-42-scheduled-payments-api --force
git branch -d feat/42-scheduled-payments-api
# Deleted branch feat/42-scheduled-payments-api
```

## Restrições

- **Nunca criar worktree sem issue existente** — parar e informar o usuário se a issue não existir
- **Nunca reutilizar worktree de outra issue** — cada tarefa tem seu próprio worktree
- **Nunca fazer edições fora do worktree** durante a execução da tarefa
- **Nunca pular o cleanup** — worktrees obsoletos acumulam e confundem `git worktree list`
- **Nunca deletar o branch antes de remover o worktree** — o git rejeita a operação

## Referências

- `lex-git-worktrees` — Lei
- `codex-git-worktrees` — Manual com convenções, lifecycle e troubleshooting
- `lex-git-branches` — Convenção de nomenclatura de branches
- `lex-issue-first` — Issue obrigatória antes do branch
- `lex-conventional-commits` — Formato de commits
- `lex-agent-planning` — Planejamento da tarefa
