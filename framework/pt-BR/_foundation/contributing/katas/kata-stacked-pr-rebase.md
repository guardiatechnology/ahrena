# Kata: Cascade Rebase em Stacked PRs

> **Prefix:** `kata-` | **Type:** Skill Repetível | **Scope:** Propagar mudanças feitas em uma camada inferior da stack para todas as camadas superiores, usando `git rebase` + `git push --force-with-lease` (caminho vanilla)

## Objetivo

Esta Kata define o procedimento manual para resolver a situação em que uma camada da stack recebe nova mudança (commit adicional, amend, ou squash via review) e as camadas acima dela precisam ser rebaseadas para incorporar essa mudança. O agente trabalha de baixo para cima dentro do worktree compartilhado, sempre com `--force-with-lease` para evitar sobrescrever commits de outros revisores.

## Quando Usar

- Quando review pediu ajuste em uma camada já submetida (ex.: amend na camada 1)
- Quando `main` avançou e a camada 1 precisa ser rebaseada (`git rebase main`)
- Quando uma camada superior precisa absorver mudanças de uma camada inferior antes de virar mergeável
- Quando squash merge de PR upstream criou divergência (precisa `git rebase --onto`)

## Entradas

| Entrada | Obrigatório | Descrição |
|---------|:-----------:|-----------|
| Worktree da stack ativo | Sim | `.worktrees/${N}-${SLUG}-stack/` existente, criado por `kata-stacked-pr-create` |
| Camada modificada | Sim | Identificador da camada onde a mudança aconteceu (ex.: `stack-1-schema`) |
| Camadas superiores | Sim | Lista das branches que precisam rebase (`stack-2-...`, `stack-3-...`) |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Identificar camada modificada e cadeia acima
- [ ] 2. Push da camada modificada com --force-with-lease
- [ ] 3. Para cada camada superior: rebase + push
- [ ] 4. Resolver conflitos quando ocorrerem
- [ ] 5. Verificação final
```

### Passo 1: Identificar camada modificada e cadeia acima

1. Entrar no worktree compartilhado:
   ```bash
   cd .worktrees/${ISSUE_NUMBER}-${SLUG}-stack
   ```
2. Listar todas as branches da stack na ordem (base → topo):
   ```bash
   git branch --list "feat/${ISSUE_NUMBER}-stack-*-${SLUG}" | sort
   ```
3. Identificar a camada modificada e as camadas acima dela. Ex.: se a camada 2 mudou, camadas 3..N precisam rebase.

### Passo 2: Push da camada modificada com `--force-with-lease`

A camada modificada já está commitada localmente (amend, novo commit, ou rebase contra `main`). Push com lease:

```bash
git checkout "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"
git push --force-with-lease origin "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"
```

**Nunca usar `--force` cego.** O `--force-with-lease` recusa o push se outro revisor tiver commitado em cima desde o último fetch — protege contra sobrescrever trabalho alheio.

### Passo 3: Para cada camada superior — rebase + push

Loop ascendente, da camada `MODIFIED_LAYER + 1` até `N`:

```bash
for i in $(seq $((MODIFIED_LAYER + 1)) $N); do
  PREV="feat/${ISSUE_NUMBER}-stack-$((i-1))-${PREV_SLUG}"
  THIS="feat/${ISSUE_NUMBER}-stack-${i}-${THIS_SLUG}"

  git checkout "$THIS"
  git rebase "$PREV"

  # se houver conflito, ver Passo 4 antes de continuar

  git push --force-with-lease origin "$THIS"
done
```

Cada iteração:
1. Checkout da camada superior
2. `git rebase {camada anterior}` — replay dos commits únicos da camada superior em cima da camada anterior atualizada
3. `git push --force-with-lease`

### Passo 4: Resolver conflitos

Quando `git rebase` para com conflito:

1. **Identificar arquivos em conflito:**
   ```bash
   git status
   ```
2. **Resolver manualmente** os marcadores `<<<<<<<` / `=======` / `>>>>>>>`. A escolha de resolução depende do contexto — se incerteza, parar e consultar o usuário.
3. **Marcar resolvido e continuar:**
   ```bash
   git add <arquivos-resolvidos>
   git rebase --continue
   ```
4. **Abortar quando irrecuperável** (raro):
   ```bash
   git rebase --abort
   ```
   Volta ao estado pré-rebase. Investigar e tentar de novo, possivelmente com decomposição diferente.

**Caso especial — squash merge upstream criou divergência:**

Se a camada anterior foi mergeada com squash em `main`, os commits originais sumiram e o rebase comum gera "artificial conflicts". Usar `--onto`:

```bash
# Em vez de:
# git rebase feat/${N}-stack-1-${SLUG}
# Faça:
git rebase --onto main "feat/${N}-stack-1-${SLUG}" "feat/${N}-stack-2-${SLUG}"
```

`--onto` reaplica apenas os commits únicos da camada 2 (excluindo os da camada 1 já squashed) em cima de `main`.

### Passo 5: Verificação final

- [ ] A camada modificada foi pushada com `--force-with-lease` (e não `--force`)
- [ ] Todas as camadas superiores foram rebaseadas em ordem ascendente
- [ ] Todos os pushes succederam (nenhum recusado por divergência inesperada)
- [ ] `git log --oneline {topo} ^main` mostra a história linear esperada
- [ ] Conflitos resolvidos preservaram intenção das duas camadas (não descartar mudanças por engano)
- [ ] Comentar nos PRs do GitHub se a mudança é significativa para revisores recontextualizarem

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Branches superiores rebaseadas | Histórico git linear | Repositório remoto |
| PRs atualizados | GitHub PRs | Auto-atualizados via push (mesmo `head` ref) |

## Restrições

- **Nunca** usar `--force` cego — sempre `--force-with-lease`
- **Nunca** rebasear `main` no fluxo de cascade — só rebaseamos branches da stack
- **Não** rebasear na ordem errada (de cima para baixo) — pode reintroduzir mudanças já obsoletas
- Se conflito for grande ou ambíguo, **parar** e consultar o usuário em vez de adivinhar
- Se a stack ficar inconsistente (rebase falhou no meio), **não esconder o estado** — listar branches restantes para o usuário e propor `git rebase --abort` ou continuação manual
- Hooks pre-push pesados (linters, testes) podem deixar a cascade muito lenta; em casos extremos, considerar `--no-verify` **com autorização explícita do usuário** e justificativa registrada

## Referências

- `codex-stacked-prs` — modelo conceitual e ciclo de vida
- `kata-stacked-pr-create` — criação inicial da stack
- `kata-stacked-pr-merge` — merge bottom-up (etapa seguinte na vida da stack)
- `lex-protected-trunk` — trunk nunca recebe force-push
- `lex-signed-commits` — assinatura GPG preservada em rebase quando `commit.gpgsign=true`
- `lex-conventional-commits` — disciplina de commit mantida
