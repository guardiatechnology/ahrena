# Lexis: Uso Obrigatório de Git Worktrees

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Toda tarefa baseada em branch executada por agentes AI no contexto Ahrena

## Lei

> **Todo agente que precisar criar um branch para implementar uma tarefa DEVE fazê-lo dentro de um git worktree dedicado, criado a partir do repositório principal. O branch do worktree DEVE seguir `lex-git-branches` (`{type}/{issue-number}-{slug}`) e uma issue GitHub DEVE existir antes da criação (conforme `lex-issue-first`). O diretório do worktree DEVE usar o slug do branch como nome legível. Trabalhar diretamente no checkout principal com alterações pertencentes a um branch de tarefa é PROIBIDO. O worktree DEVE ser removido após o merge do PR correspondente.**

## Abrangência

- **Aplica-se a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, qualquer agente AI que crie branches para implementar tarefas
- **Agentes vinculados:** todos os warriors e katas que produzem código ou artefatos em branches dedicados (`warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`)
- **Exceções permitidas:**
  - Commits diretos em `main` para correções triviais de tipografia ou formatação (conforme `lex-issue-first`)
  - Operações de leitura/consulta sem produção de branch
  - **Stacked Pull Requests** — uma stack inteira ocupa um único worktree compartilhado em vez de um worktree por branch. Regra detalhada na seção 5 abaixo

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

O diretório do worktree DEVE seguir o path definido em `paths.worktrees` em `.ahrena/.directives` (padrão: `.worktrees/`) e usar `{issue-number}-{slug}` como nome:

```
.worktrees/{issue-number}-{slug}/
```

Exemplo: branch `feat/42-scheduled-payments-api` → diretório `.worktrees/42-scheduled-payments-api/`

O path `.worktrees/` está dentro do repositório e é ignorado pelo git via `.gitignore`.

### 3. Worktree como ambiente isolado

O agente DEVE usar o worktree como ambiente exclusivo para a tarefa:

- Todas as edições de arquivo ocorrem **dentro** do worktree
- Commits são feitos no contexto do worktree
- O checkout principal permanece limpo — sem alterações não relacionadas ao seu próprio branch

### 4. Cleanup obrigatório após merge

Após o merge do PR correspondente:

1. Sair do diretório do worktree (se dentro dele)
2. Remover o worktree: `git worktree remove .worktrees/{issue-number}-{slug} --force`
3. Deletar o branch local: `git branch -d {branch}`
4. Confirmar: `git worktree list` não deve exibir o worktree removido

### 5. Worktree compartilhado para Stacked Pull Requests

Quando uma feature é decomposta em N camadas encadeadas (conforme `codex-stacked-prs`), a regra de "um worktree por branch" das seções 2-4 NÃO se aplica. Uma stack inteira opera dentro de um **único** worktree compartilhado.

**Justificativa:** o cascade rebase (`kata-stacked-pr-rebase`) opera lendo e re-escrevendo as branches da stack em sequência, e exige working dir único. Worktree por branch quebra esse pressuposto.

#### 5.1 Nomenclatura do diretório

```
.worktrees/{issue-number}-{slug}-stack/
```

| Campo | Regra |
|---|---|
| `issue-number` | Número da issue guarda-chuva (1 issue → N camadas) |
| `slug` | Slug descritivo da feature, **sem** o segmento `stack-{layer}` |
| Sufixo `-stack` | Literal e obrigatório — sinal canônico de que o diretório hospeda uma stack |

Exemplo: para a issue #42 ("Scheduled Payments"), o worktree é `.worktrees/42-scheduled-payments-stack/`. Dentro dele coexistem as branches `feat/42-stack-1-schema`, `feat/42-stack-2-api`, `feat/42-stack-3-ui`.

#### 5.2 Branches dentro do worktree compartilhado

Cada camada tem branch própria, seguindo o pattern de `lex-git-branches`:

```
{type}/{issue-number}-stack-{layer}-{slug}
```

A camada base (`layer = 1`) é criada junto com o worktree partindo de `main`. Camadas superiores (`layer ≥ 2`) são criadas a partir da camada anterior:

```bash
git worktree add .worktrees/${N}-${SLUG}-stack -b feat/${N}-stack-1-${SLUG} main
cd .worktrees/${N}-${SLUG}-stack
# trabalho na camada 1, commit, push
git checkout -b feat/${N}-stack-2-${SLUG} feat/${N}-stack-1-${SLUG}
# trabalho na camada 2, commit, push
```

#### 5.3 Troca de camada

O agente alterna entre camadas com `git checkout` dentro do mesmo diretório — **nunca** criando worktrees adicionais para a mesma stack:

```bash
git checkout feat/${N}-stack-1-${SLUG}    # voltar para camada base
git checkout feat/${N}-stack-3-${SLUG}    # ir para o topo
```

#### 5.4 Cleanup após merge da stack

Quando a última camada da stack mergear (a que tem `Closes #N`), a issue fecha e o cleanup é único:

```bash
cd ../..
git worktree remove .worktrees/${N}-${SLUG}-stack --force
# deletar TODAS as branches locais da stack
for i in $(seq 1 $N); do
  git branch -D feat/${N}-stack-${i}-${SLUG_i} 2>/dev/null || true
done
```

Veja `kata-stacked-pr-merge` (Passo 5) para o procedimento completo.

#### 5.5 Restrições específicas

- **Nunca** criar mais de um worktree para a mesma stack — todas as camadas vivem no diretório `-stack/`
- **Nunca** misturar branches de stacks diferentes no mesmo worktree
- **Nunca** trabalhar numa branch da stack a partir do checkout principal — a stack inteira é tarefa do worktree dedicado
- O sufixo `-stack` no nome do diretório é **literal** — não substituir por convenção interna

## Exemplos

### Correto

```
Issue #42 existe: "Add scheduled payments API"
Branch: feat/42-scheduled-payments-api
Worktree: .worktrees/42-scheduled-payments-api/

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
- `codex-stacked-prs` — exceção declarada: uma stack ocupa um único worktree compartilhado
