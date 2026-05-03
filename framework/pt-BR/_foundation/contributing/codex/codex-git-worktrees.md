# Codex: Git Worktrees no Contexto Ahrena

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Convenções, ciclo de vida e comandos para uso de git worktrees por agentes AI no contexto Ahrena

## Visão Geral

Este Codex é o manual canônico para uso de git worktrees. Complementa `lex-git-worktrees` (a Lei) com explicações, convenções de nomenclatura, ciclo de vida completo, comandos e integração com o Claude Code SDK. Todo agente que cria ou gerencia worktrees DEVE consultar este Codex.

## Contexto

- **Domínio:** isolamento de ambiente de desenvolvimento por tarefa
- **Público-alvo:** todos os agentes (Claude, Cursor, warriors, katas) e revisores humanos
- **Atualização:** quando os comandos ou convenções mudarem

---

## 1. O que é um git worktree

Um git worktree é um diretório de trabalho adicional vinculado ao mesmo repositório git. Cada worktree tem seu próprio branch ativo, mas compartilha o histórico, objetos e configuração do repositório raiz.

```
repositório raiz (main)
├── .git/                         ← único objeto git compartilhado
├── src/
└── framework/

worktree (feat/42-payments-api)   ← diretório separado, branch próprio
├── .git                          ← arquivo de ponteiro, não diretório
├── src/
└── framework/
```

**Por que usar:** cada tarefa de feature roda em ambiente isolado — sem risco de misturar alterações, sem necessidade de `stash`, sem conflito de branch ativo entre tarefas paralelas.

---

## 2. Convenção de nomenclatura

### Branch

Segue `lex-git-branches` obrigatoriamente:

```
{type}/{issue-number}-{slug}
```

| Campo | Regra |
|---|---|
| `type` | Um de: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `issue-number` | Número inteiro da issue GitHub associada |
| `slug` | kebab-case, máximo 50 caracteres |

Exemplos válidos:
- `feat/42-scheduled-payments-api`
- `fix/87-null-pointer-transfer`
- `docs/101-update-contributing-guide`

### Diretório do worktree

```
.worktrees/{issue-number}-{slug}/
```

| Campo | Regra |
|---|---|
| `repo-name` | Nome do repositório (ex.: `ahrena`) |
| `issue-number` | Mesmo número da issue do branch |
| `slug` | Mesmo slug do branch |

Exemplos:
- `.worktrees/42-scheduled-payments-api/`
- `.worktrees/87-null-pointer-transfer/`

O prefixo `../{repo-name}-` coloca o worktree **fora** do diretório do repositório principal, evitando interferências com o `.git` raiz e mantendo a listagem de arquivos limpa.

---

## 3. Ciclo de vida

```
issue existe
    ↓
criar worktree  →  work inside  →  commit + push  →  PR aberto  →  PR merged
                                                                       ↓
                                                              remover worktree
                                                              deletar branch local
```

### 3.1 Criar o worktree

**Via Claude Code (recomendado):**

O Claude Code expõe o tool `EnterWorktree` que cria e entra no worktree automaticamente, com branch seguindo a convenção Ahrena.

**Via CLI:**

```powershell
# PowerShell (terminal: powershell conforme .ahrena/.directives)
$repo    = "ahrena"
$issue   = 42
$type    = "feat"
$slug    = "scheduled-payments-api"
$branch  = "$type/$issue-$slug"
$wtDir   = ".worktrees/$issue-$slug"

git worktree add $wtDir -b $branch
```

### 3.2 Trabalhar no worktree

```powershell
Set-Location $wtDir

# editar arquivos, commitar normalmente
git add .
git commit -m "feat(payments): add scheduled transfer entity"

# push do branch do worktree
git push -u origin $branch
```

### 3.3 Abrir PR

Abrir o PR referenciando a issue conforme `lex-issue-first`:

```powershell
gh pr create --title "feat(payments): add scheduled payments API" `
             --body "Closes #$issue" `
             --base main `
             --head $branch
```

### 3.4 Cleanup após merge

```powershell
# Sair do diretório do worktree (se dentro)
Set-Location ../..

# Remover o worktree
git worktree remove $wtDir --force

# Deletar branch local
git branch -d $branch

# Verificar
git worktree list
```

---

## 4. Integração com Claude Code

O Claude Code SDK expõe o tool `EnterWorktree` para criar e navegar worktrees de forma automatizada. O agente deve usá-lo preferencialmente ao CLI manual.

Parâmetros esperados pelo `EnterWorktree`:
- `branch`: nome do branch no formato `lex-git-branches`
- Cria automaticamente o diretório `../{repo}-{issue-number}-{slug}/`
- Retorna o caminho do worktree criado

Após a tarefa concluída e PR mergeado, o agente usa `ExitWorktree` para sair e depois executa o cleanup do CLI.

---

## 5. Worktrees em paralelo

Um repositório suporta múltiplos worktrees simultâneos — cada tarefa tem o seu:

```
git worktree list

/c/Workspace/guardia/public/ahrena                [main]
/c/Workspace/guardia/public/ahrena/.worktrees/42-payments    [feat/42-scheduled-payments-api]
/c/Workspace/guardia/public/ahrena/.worktrees/87-fix-null    [fix/87-null-pointer-transfer]
```

Restrições do git:
- O mesmo branch **não pode** estar ativo em dois worktrees ao mesmo tempo
- Operações como `git branch -d` falham se o branch estiver em uso em um worktree ativo — remover o worktree primeiro

---

## 6. Troubleshooting

| Problema | Causa provável | Solução |
|---|---|---|
| `fatal: '{dir}' already exists` | Diretório criado manualmente | Remover o diretório e recriar com `git worktree add` |
| `error: branch already checked out` | Branch ativo em outro worktree | Listar com `git worktree list`; remover o worktree obsoleto |
| `git branch -d` falha | Branch ainda referenciado por worktree ativo | `git worktree remove {dir} --force` primeiro |
| `git worktree list` mostra worktree sem diretório | Diretório deletado manualmente sem `remove` | `git worktree prune` para limpar referências obsoletas |

---

## 7. Boas práticas

1. **Nomear descritivamente.** O slug deve ser legível por humanos — quem faz `ls ..` deve entender o propósito do worktree sem abri-lo.
2. **Um worktree por issue.** Não reutilizar worktrees de issues diferentes — criar um novo a cada tarefa.
3. **Commitar antes de sair.** Antes de trocar de worktree, commitar ou stash as alterações no worktree atual.
4. **Cleanup imediato após merge.** Não acumular worktrees obsoletos — o cleanup deve ser parte do fluxo de finalização da tarefa.
5. **Não editar `.git` no worktree.** O arquivo `.git` no diretório do worktree é um ponteiro — não é um diretório `.git` completo; não modificar manualmente.

---

## Referências

- `lex-git-worktrees` — Lei correspondente
- `kata-git-worktree` — Procedimento passo a passo
- `lex-git-branches` — Convenção de nomenclatura de branches
- `lex-issue-first` — Issue obrigatória antes do branch
- `lex-agent-planning` — Planejamento da tarefa antes da execução
