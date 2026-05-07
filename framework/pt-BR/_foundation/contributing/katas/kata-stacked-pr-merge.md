# Kata: Merge Bottom-Up de Stacked PRs

> **Prefix:** `kata-` | **Type:** Skill Repetível | **Scope:** Mergear uma cadeia de Pull Requests encadeados na ordem correta (base → topo), atualizando explicitamente o `base` da próxima camada após cada merge, usando `gh` + `git` (caminho vanilla)

## Objetivo

Esta Kata define o procedimento para mergear uma stack inteira respeitando a política bottom-up: a camada inferior (`stack-1`) é mergeada primeiro em `main`; em seguida, o PR da camada 2 tem seu `base` atualizado de `stack-1` para `main` via `gh pr edit`, a branch é rebaseada onto `main` e force-pushed; o ciclo se repete até a última camada. Após o merge da última camada (que tem `Closes #N`), a issue guarda-chuva fecha automaticamente, e o agente faz cleanup do worktree compartilhado e das branches locais.

## Quando Usar

- Quando a camada base (`stack-1`) recebeu approval de review e está pronta para mergear
- Quando uma camada intermediária está aprovada e a anterior já foi mergeada
- Quando todas as camadas estão aprovadas e o usuário quer fechar a stack inteira em sequência

## Entradas

| Entrada | Obrigatório | Descrição |
|---------|:-----------:|-----------|
| Stack ativa | Sim | N PRs no GitHub criados por `kata-stacked-pr-create`, em ordem `stack-1` → `stack-N` |
| Approval de review | Sim | Pelo menos a camada base aprovada conforme `lex-pr-quality` (CODEOWNERS) |
| Estratégia de merge | Não | `--squash` (default recomendado), `--merge`, ou `--rebase` — herda da configuração do repo |
| Worktree compartilhado | Sim | `.worktrees/${N}-${SLUG}-stack/` ainda existente |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Verificar pré-requisitos (CI verde, approval, sem conflito)
- [ ] 2. Mergear camada inferior (1)
- [ ] 3. Para cada camada acima: atualizar base → rebase → force-push → mergear
- [ ] 4. Confirmar fechamento da issue guarda-chuva
- [ ] 5. Cleanup do worktree e branches locais
- [ ] 6. Verificação final
```

### Passo 1: Verificar pré-requisitos

Para a camada que será mergeada agora (`current_layer`):

```bash
PR_NUMBER=$(gh pr view "$LAYER_BRANCH" --json number --jq .number)

# CI verde?
gh pr checks "$PR_NUMBER" --repo "$OWNER/$REPO"

# Approval presente?
gh pr view "$PR_NUMBER" --json reviews \
  --jq '[.reviews[] | select(.state=="APPROVED")] | length'

# Sem conflito declarado pelo GitHub?
gh pr view "$PR_NUMBER" --json mergeable --jq .mergeable
```

Se algum critério falhar, parar e reportar ao usuário. Não tentar forçar.

### Passo 2: Mergear camada inferior (1)

A camada 1 tem `base: main`. Merge direto:

```bash
gh pr merge "$PR_NUMBER" \
  --repo "$OWNER/$REPO" \
  --squash \
  --delete-branch=false
```

| Flag | Razão |
|---|---|
| `--squash` | Default recomendado — produz histórico linear em `main` |
| `--delete-branch=false` | Importante: a branch `feat/${N}-stack-1-${SLUG}` ainda é base do PR da camada 2; deletá-la quebra a referência |

Após merge, atualizar `main` no worktree:

```bash
git fetch origin main
```

### Passo 3: Para cada camada acima — atualizar base → rebase → force-push → mergear

Loop para camadas `2..N`:

```bash
PREV_PR="$PR_NUMBER"   # PR já mergeado (camada i-1)
for i in $(seq 2 $N); do
  THIS_BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}"
  THIS_PR=$(gh pr view "$THIS_BRANCH" --json number --jq .number)

  # 3a. Atualizar base do PR para main (GitHub não migra automaticamente)
  gh pr edit "$THIS_PR" --repo "$OWNER/$REPO" --base main

  # 3b. Rebase local da branch onto main
  git checkout "$THIS_BRANCH"
  git rebase origin/main

  # se conflito, resolver per kata-stacked-pr-rebase passo 4

  # 3c. Force-push com lease
  git push --force-with-lease origin "$THIS_BRANCH"

  # 3d. Verificar pré-requisitos (CI verde após force-push, approval)
  gh pr checks "$THIS_PR"
  gh pr view "$THIS_PR" --json reviews \
    --jq '[.reviews[] | select(.state=="APPROVED")] | length'

  # 3e. Mergear (se última camada, deletar branch após)
  if [ "$i" -eq "$N" ]; then
    gh pr merge "$THIS_PR" --squash --delete-branch
  else
    gh pr merge "$THIS_PR" --squash --delete-branch=false
  fi

  PREV_PR="$THIS_PR"
  git fetch origin main
done
```

**Pontos críticos:**

- O `gh pr edit --base main` precisa rodar **antes** do rebase + push. Se a base do PR ainda é `feat/${N}-stack-1-...` (que acaba de mergear), GitHub fica confuso; trocar primeiro evita surpresa.
- O `--delete-branch=false` em camadas intermediárias preserva a referência usada pelas próximas camadas (mesmo que já tenham seu base trocado, manter consistência).
- O `--delete-branch` na **última camada** dispara cleanup automático no GitHub.

### Passo 4: Confirmar fechamento da issue guarda-chuva

A última camada tem `Closes #N` no body. Após seu merge, GitHub fecha a issue.

```bash
gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" --json state --jq .state
# esperado: CLOSED
```

Se ainda estiver `OPEN`, verificar se a última camada tinha `Closes #N` no body — se faltou, fechar manualmente com referência no comentário:

```bash
gh issue close "$ISSUE_NUMBER" --comment "Fechada por #${LAST_PR_NUMBER} (última camada da stack)."
```

### Passo 5: Cleanup do worktree e branches locais

Após todas as camadas mergeadas:

```bash
# Sair do worktree
cd ../..  # voltar ao repo raiz

# Remover o worktree compartilhado
git worktree remove ".worktrees/${ISSUE_NUMBER}-${SLUG}-stack" --force

# Deletar branches locais (todas as camadas)
for i in $(seq 1 $N); do
  git branch -D "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" 2>/dev/null || true
done

# Verificar
git worktree list
git branch --list "feat/${ISSUE_NUMBER}-stack-*"
```

`git worktree list` não deve mais mostrar o worktree da stack. `git branch --list` não deve retornar nada.

### Passo 6: Verificação final

- [ ] N PRs mergeados em `main`, na ordem `stack-1` → `stack-N`
- [ ] Para cada PR intermediário (`stack-2` a `stack-N`), o `base` foi explicitamente atualizado para `main` antes do merge
- [ ] Cada camada superior foi rebaseada onto `main` antes do merge (histórico linear preservado)
- [ ] Issue guarda-chuva está `CLOSED` (auto-fechada pelo último `Closes #N` ou manualmente)
- [ ] Worktree compartilhado removido
- [ ] Todas as branches locais da stack deletadas
- [ ] Plan correspondente (`plan-NNN-...`) movido para `archived/` se houver

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Stack mergeada | N commits squash em `main` | `main` do repositório |
| Issue fechada | GitHub Issue state CLOSED | Repositório |
| Worktree limpo | Diretório removido | Local filesystem |
| Branches deletadas | Branches locais e remotas removidas | Local + remoto |

## Restrições

- **Nunca** mergear fora da ordem (camada 3 antes da camada 2) — quebra a base do PR seguinte e força reconstrução manual
- **Nunca** deletar a branch da camada `i-1` antes de mergear a camada `i` (referência usada pelo PR seguinte)
- **Não** trocar a estratégia de merge entre camadas — manter `--squash` (ou o que o repo padroniza) consistente
- **Não** mergear via UI do GitHub durante a sequência — usar exclusivamente `gh pr merge` via CLI para coordenar com os passos de rebase
- Se um conflito aparecer no rebase de uma camada superior, **parar** e invocar `kata-stacked-pr-rebase` (passo 4) — não tentar resolver dentro deste kata
- Se a issue guarda-chuva não fechar automaticamente, **investigar antes de fechar manualmente** — pode indicar que `Closes #N` está faltando no PR errado

## Referências

- `codex-stacked-prs` — modelo conceitual; ciclo de vida; política bottom-up
- `kata-stacked-pr-create` — criação inicial da stack
- `kata-stacked-pr-rebase` — cascade rebase quando há conflito
- `lex-pr-quality` — HARD-GATE de 8 critérios atendido por cada PR antes do merge
- `lex-protected-trunk` — `main` recebe código apenas via merge de PR aprovado
- `lex-issue-first` — `Closes #N` na última camada fecha a issue
- `lex-git-worktrees` — exceção stack=worktree compartilhado
