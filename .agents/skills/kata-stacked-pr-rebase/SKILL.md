---
name: kata-stacked-pr-rebase
description: "Cascade Rebase em Stacked PRs. Propagar mudanças feitas em uma camada inferior da stack para todas as camadas superiores, usando git rebase + git push --force-with-lease (caminho vanilla)"
---

# Kata: Cascade Rebase em Stacked PRs

> **Prefix:** `kata-` | **Type:** Skill Repetível | **Scope:** Propagar mudanças feitas em uma camada inferior da stack para todas as camadas superiores, usando `git rebase` + `git push --force-with-lease` (caminho vanilla)

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

## Variant: git-spice

Aplicável quando `.ahrena/.directives` declara `stacked_prs.tool: gs`. A grande vantagem do caminho gs neste kata é o **auto-restack**: alterar uma camada inferior (commit novo, amend, ou rebase contra trunk) reaplica automaticamente os commits das camadas superiores em cima da nova base. O agente quase nunca precisa de loop manual; em conflito, `gs rebase continue` substitui `git rebase --continue`. Consultar `codex-git-spice` para mapeamento completo.

### Caso 1: amend ou commit novo numa camada já submetida

Estando dentro do worktree compartilhado e na camada modificada:

```bash
git-spice branch checkout "feat/${ISSUE_NUMBER}-stack-${MODIFIED_LAYER}-${LAYER_SLUG}"

# (a) Commit adicional na mesma camada
git add <arquivos>
git-spice commit create -m "fix(scope): ajuste pedido em review"
# → gs reaplica camadas i+1..N em cima do novo commit

# (b) Amend no último commit da camada
git add <arquivos>
git-spice commit amend --no-edit
# → idem; auto-restack acontece após o amend

# Submeter o stack para refletir nos PRs (idempotente)
git-spice stack submit
# ou apenas as camadas afetadas:
git-spice upstack submit
```

`gs commit create` e `gs commit amend` chamam `git commit` por baixo (assinatura GPG preservada quando `commit.gpgsign=true` global) e em seguida disparam `gs upstack restack` para todas as camadas acima.

### Caso 2: trunk (`main`) avançou e a camada base precisa rebase

```bash
# Estando em qualquer camada do worktree compartilhado
git-spice repo sync --restack
# Pull do trunk + apaga branches já mergeadas localmente +
# rebaseia o stack atual contra o trunk atualizado
```

Equivalente ao loop vanilla `git fetch && git rebase origin/main && cascade rebase manual`, em um único comando.

### Caso 3: squash merge upstream criou divergência

Se a camada anterior foi mergeada com squash (no trunk) e o histórico unsquashed sumiu:

```bash
git-spice repo sync --restack
# Cobre a maioria dos casos: gs detecta o squash e ajusta a base.
```

Se ainda restar inconsistência (raro):

```bash
# Move a camada superior para diretamente sobre main
git-spice upstack onto main
# ou para outra base explícita
git-spice upstack onto "feat/${ISSUE_NUMBER}-stack-3-${LAYER_SLUG}"
```

### Caso 4: conflito durante auto-restack

`gs` para com mensagem semelhante a `git rebase` em conflito. Resolução:

```bash
git status
# resolver marcadores <<<<<<< / >>>>>>> manualmente
git add <arquivos-resolvidos>
git-spice rebase continue
# ou para abortar:
git-spice rebase abort
```

`gs rebase continue` retoma o auto-restack do ponto onde parou — incluindo camadas acima ainda não tocadas. Não use `git rebase --continue` direto; pode dessincronizar a metadata do gs em casos de cascata multi-camada.

### Caso 5: push após mudanças

`gs` aplica `--force-with-lease` automaticamente em `branch submit` e `stack submit`:

```bash
git-spice stack submit             # default seguro: --force-with-lease
git-spice stack submit --force     # bypassa lease (NÃO usar sem motivo)
git-spice stack submit --no-verify # pula pre-push hooks (autorização explícita)
```

### Notas operacionais (gs)

- **Ordem importa, e o gs cuida dela:** comece sempre pela camada modificada — `gs` propaga para cima sozinho.
- **Não pulei o `gs commit create`?** Se você fez `git commit` direto, a camada acima não foi auto-restacked. Use `gs upstack restack` manualmente.
- **Hooks lentos:** o auto-restack repete `pre-commit` por camada acima; otimizar ou usar `--no-verify` com autorização (mesma disciplina do vanilla).
- **GPG signing:** preservado nos commits resultantes do auto-restack se `commit.gpgsign=true` global; verificar com `git log --show-signature`.
