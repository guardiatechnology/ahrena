# Lexis: Uso Obrigatório de Git Worktrees

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Toda tarefa baseada em branch executada por agentes AI no contexto Ahrena

## Lei

> **Todo agente que precisar criar um branch para implementar uma tarefa DEVE fazê-lo dentro de um git worktree dedicado, criado a partir do repositório principal. O branch do worktree DEVE seguir `lex-git-branches` (`{type}/{issue-number}-{slug}`) e uma issue GitHub DEVE existir antes da criação (conforme `lex-issue-first`). O diretório do worktree DEVE usar o slug do branch como nome legível. Trabalhar diretamente no checkout principal com alterações pertencentes a um branch de tarefa é PROIBIDO. O worktree DEVE ser removido após o merge do PR correspondente.**

## Abrangência

- **Aplica-se a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, qualquer agente AI que crie branches para implementar tarefas
- **Agentes vinculados:** todos os warriors e katas que produzem código ou artefatos em branches dedicados (`warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`)
- **Exceções permitidas:** commits diretos em `main` para correções triviais de tipografia ou formatação (conforme `lex-issue-first`); operações de leitura/consulta sem produção de branch

## Regras

### 1. Issue antes do worktree

Antes de criar o worktree, o agente DEVE:

1. Verificar que uma issue GitHub existe para a tarefa (conforme `lex-issue-first`)
2. Anotar o número da issue — é parte obrigatória do nome do branch e do diretório do worktree

### 2. Nomenclatura do branch e do diretório

O branch DEVE seguir o formato de `lex-git-branches`:

```
{type}/{issue-number}-{slug}
```

O diretório do worktree DEVE usar o mesmo slug `{issue-number}-{slug}` como nome, prefixado com o nome do repositório para legibilidade:

```
../{repo-name}-{issue-number}-{slug}/
```

Exemplo: branch `feat/42-scheduled-payments-api` → diretório `../ahrena-42-scheduled-payments-api/`

### 3. Worktree como ambiente isolado

O agente DEVE usar o worktree como ambiente exclusivo para a tarefa:

- Todas as edições de arquivo ocorrem **dentro** do worktree
- Commits são feitos no contexto do worktree
- O checkout principal permanece limpo — sem alterações não relacionadas ao seu próprio branch

### 4. Cleanup obrigatório após merge

Após o merge do PR correspondente:

1. Sair do diretório do worktree (se dentro dele)
2. Remover o worktree: `git worktree remove ../{repo}-{issue-number}-{slug} --force`
3. Deletar o branch local: `git branch -d {branch}`
4. Confirmar: `git worktree list` não deve exibir o worktree removido

## Exemplos

### Correto

```
Issue #42 existe: "Add scheduled payments API"
Branch: feat/42-scheduled-payments-api
Worktree: ../ahrena-42-scheduled-payments-api/

→ Agente entra no worktree via EnterWorktree ou git worktree add
→ Todas as edições feitas dentro do worktree
→ Checkout principal permanece em main, limpo
→ Após merge do PR: worktree removido, branch deletado
```

### Incorreto

```
# Agente edita arquivos no checkout principal para implementar feature
# ❌ checkout principal acumula alterações misturadas

# Branch criado sem issue associada
# ❌ Viola lex-issue-first e lex-git-branches

# Worktree não removido após merge — acúmulo de diretórios obsoletos
# ❌ git worktree list exibe worktrees mortos
```

## Validação Automatizada

- **Ferramenta:** `git worktree list` para verificar worktrees ativos; Claude Code `EnterWorktree` para criação e navegação; `kata-git-worktree` como ponto de entrada canônico
- **Momento:** antes de iniciar qualquer tarefa que produza um branch; após merge do PR (cleanup)
- **Métrica:** 0 tarefas de feature executadas fora de um worktree dedicado; 0 worktrees criados sem issue GitHub correspondente; checkout principal sempre limpo durante execuções de feature

## Referências

- `codex-git-worktrees` — manual com convenções, ciclo de vida e comandos
- `kata-git-worktree` — procedimento passo a passo
- `lex-git-branches` — convenção de nomenclatura de branches
- `lex-issue-first` — issue obrigatória antes do branch
