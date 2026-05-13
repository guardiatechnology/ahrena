# Kata: Criar Stacked Pull Requests

> **Prefix:** `kata-` | **Type:** Skill Repetível | **Scope:** Decompor uma feature grande em uma cadeia de PRs reviewáveis em isolamento, usando `git` + `gh` (caminho vanilla)

## Objetivo

Esta Kata define o procedimento para transformar uma issue guarda-chuva em uma cadeia de Pull Requests encadeados (stack), aplicando primeiro a Decision Checklist canônica de `codex-stacked-prs` para validar que a stack faz sentido. Se a checklist reprova, redireciona para `kata-contributing-pr` (PR único). Se aprova, cria o worktree compartilhado, abre uma branch por camada, faz push, cria o PR de cada camada com `base` apontando para a anterior, e espelha labels/assignee/reviewers em cada PR.

## Quando Usar

- Quando o usuário pede para iniciar trabalho numa issue grande e o agente quer avaliar se vale stackar
- Quando o usuário invoca explicitamente `cry-new-stacked-pr`
- Quando uma issue guarda-chuva já tem ACs numerados e o escopo cruza ≥ 2 Pilares técnicos

## Entradas

| Entrada | Obrigatório | Descrição |
|---------|:-----------:|-----------|
| Issue guarda-chuva | Sim | Número da issue no formato `owner/repo#N`, atendendo `lex-issue-quality` (template, labels, Type, assignee, Why/What/How) |
| Escopo previsto | Sim | Descrição informal de componentes a tocar — usado pela Decision Checklist |
| ACs numerados | Sim | Acceptance Criteria do issue (`AC-1`, `AC-2`, ...) — base para mapeamento AC↔camada |
| Decomposição preferida | Não | Sugestão do usuário sobre como dividir; se omitida, agente propõe |

## Fluxo de Trabalho

```
Progresso:
- [ ] 0. Pre-flight: Decision Checklist
- [ ] 1. Validar issue guarda-chuva
- [ ] 2. Confirmar decomposição em camadas com o usuário
- [ ] 3. Criar worktree compartilhado
- [ ] 4. Para cada camada: branch + commits + push + PR
- [ ] 5. Espelhar labels/assignee/reviewers em cada PR
- [ ] 6. Verificação final
```

### Passo 0: Pre-flight — Decision Checklist

Aplicar a Decision Checklist canônica de [codex-stacked-prs](../codex/codex-stacked-prs.md), seção 2:

1. **Contar sinais altos** contra issue + escopo previsto:
   - Diff estimado > 500 linhas (1 ponto)
   - ≥ 4 ACs independentes (1 ponto)
   - ≥ 2 Pilares técnicos atravessados (1 ponto)
   - Camadas óbvias presentes (schema → API → UI; equivalente) (1 ponto)
   - Independência de review entre camadas (1 ponto)
   - Risco de rollback por camada (1 ponto)
2. **Verificar anti-sinais** (qualquer um veta):
   - Hotfix / resposta a incidente
   - Cross-fork PR
   - Refactor monolítico sem camadas naturais
3. **Decidir:**
   - **≥ 3 sinais altos AND 0 anti-sinais** → propor stack ao usuário
   - **Caso contrário** → parar e recomendar ao usuário invocar `kata-contributing-pr` (ou `cry-new-pr`) para um PR único

**Apresentar a proposta ao usuário** em formato concreto, ex.:

```
Esta issue parece candidata a stacked PR:
  Sinais altos: 4 (diff estimado ~800 linhas, 5 ACs, 2 Pilares, camadas óbvias)
  Anti-sinais: 0

Proposta de decomposição:
  Camada 1 (schema):  AC-1, AC-2 — migration + entity
  Camada 2 (api):     AC-3, AC-4 — repository + use case + router
  Camada 3 (ui):      AC-5      — frontend components

Confirmar e prosseguir? (s/n/ajustar)
```

Se o usuário rejeitar ou pedir PR único, encerrar este kata e recomendar ao usuário invocar `kata-contributing-pr` (ou `cry-new-pr`) — katas não encadeiam outros katas; orquestração entre katas é papel de Warriors.

### Passo 1: Validar issue guarda-chuva

1. Ler a issue: `gh issue view $N --repo $OWNER/$REPO --json number,title,labels,assignees,body`
2. Confirmar que atende `lex-issue-quality`:
   - Template usado (feature-request / user-story-* / epic / tech-task)
   - Labels mínimas presentes
   - Issue Type definido (Feature / Task / Epic)
   - Pelo menos um assignee
   - Body responde Why / What / How
3. Se algum critério faltar, alertar o usuário e parar — issue precisa ser corrigida antes da branch (`lex-issue-first`).

### Passo 2: Confirmar decomposição em camadas

Após confirmação do usuário no Passo 0, formalizar a decomposição:

1. Para cada camada, registrar:
   - Slug curto (kebab-case): `schema`, `api`, `ui`, `tests`, etc.
   - ACs cobertos: subset dos ACs da issue guarda-chuva
   - Componentes tocados: lista informal de módulos/diretórios
2. Apresentar ao usuário a decomposição final como tabela (ex.: ver Passo 0).
3. Salvar mentalmente — vai ser usado no body de cada PR.

### Passo 3: Criar worktree compartilhado

Naming canônico (`codex-stacked-prs` seção 4):

```bash
ISSUE_NUMBER=42
SLUG="scheduled-payments"   # sem o segmento stack-{layer}
WORKTREE_DIR=".worktrees/${ISSUE_NUMBER}-${SLUG}-stack"
BASE_BRANCH="feat/${ISSUE_NUMBER}-stack-1-${SLUG}"

git worktree add "$WORKTREE_DIR" -b "$BASE_BRANCH" main
cd "$WORKTREE_DIR"
```

A branch da camada 1 já é criada junto com o worktree, partindo de `main`. Diferente do fluxo padrão (`lex-git-worktrees`), uma stack inteira ocupa **um único** worktree compartilhado — exceção declarada na Lexis.

### Passo 4: Para cada camada — branch + commits + push + PR

**Camada 1 (já em `feat/${N}-stack-1-${SLUG}`):**

1. Implementar o escopo da camada
2. Commits atômicos assinados (seguir `lex-conventional-commits`, `lex-small-commits`, `lex-signed-commits`)
3. Push:
   ```bash
   git push -u origin "feat/${ISSUE_NUMBER}-stack-1-${SLUG}"
   ```
4. Criar PR com base em `main`:
   ```bash
   gh pr create \
     --base main \
     --head "feat/${ISSUE_NUMBER}-stack-1-${SLUG}" \
     --title "feat(scope): camada 1 — schema (1/N)" \
     --body "Refs #${ISSUE_NUMBER} (1/N — schema)
   
   Cobre: AC-1, AC-2.
   Próxima camada: feat/${ISSUE_NUMBER}-stack-2-${SLUG}." \
     --assignee "@me"
   ```
5. Capturar o número do PR retornado.

**Camadas 2..N:**

Para cada camada `i` de `2..N`, partindo da branch da camada anterior:

```bash
PREV_BRANCH="feat/${ISSUE_NUMBER}-stack-$((i-1))-${SLUG}"
THIS_BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG}"

git checkout -b "$THIS_BRANCH" "$PREV_BRANCH"
# implementar
# commitar
git push -u origin "$THIS_BRANCH"

gh pr create \
  --base "$PREV_BRANCH" \
  --head "$THIS_BRANCH" \
  --title "feat(scope): camada ${i} — ${LAYER_NAME} (${i}/N)" \
  --body "Refs #${ISSUE_NUMBER} (${i}/N — ${LAYER_NAME})

Cobre: AC-X, AC-Y.
Base: ${PREV_BRANCH} (PR #PREV_PR_NUMBER).
$( [ "$i" -eq "$N" ] && echo "Última camada — fechará a issue ao mergear." )" \
  --assignee "@me"
```

**Camada N (última):** trocar `Refs #${ISSUE_NUMBER}` por `Closes #${ISSUE_NUMBER}` no body do PR.

### Passo 5: Espelhar labels/assignee/reviewers em cada PR

Labels de tamanho (`size/*`) são auto-aplicadas pelo GitHub Actions — não aplicar manualmente.

Para cada PR criado no Passo 4:

```bash
# Pegar labels do issue guarda-chuva
LABELS=$(gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" \
  --json labels --jq '[.labels[].name] | join(",")')

# Espelhar no PR
gh pr edit "$PR_NUMBER" --repo "$OWNER/$REPO" --add-label "$LABELS"

# Verificar reviewers via CODEOWNERS (auto-request quando configurado)
gh pr view "$PR_NUMBER" --json reviewRequests \
  --jq '[.reviewRequests[].login]'

# Se vazio, adicionar manualmente per .github/CODEOWNERS:
gh pr edit "$PR_NUMBER" --add-reviewer "org/team"
```

Aplicar labels específicos de PR quando aplicável (ver `codex-labels`):
- `breaking change 💥` — algum commit quebra contrato
- `security 🛡️` — resolve vulnerabilidade

### Passo 6: Verificação final

- [ ] Decision Checklist documentada (sinais contados, anti-sinais zerados)
- [ ] Issue guarda-chuva atende `lex-issue-quality`
- [ ] Worktree compartilhado criado em `.worktrees/${N}-${SLUG}-stack/`
- [ ] N branches criadas seguindo `feat/${N}-stack-{i}-{slug}`
- [ ] N PRs abertos com `base` correto (camada 1 → main; camadas 2..N → camada anterior)
- [ ] Body de cada PR referencia issue: `Refs #N` (intermediárias) ou `Closes #N` (última)
- [ ] Body de cada PR informa cobertura de ACs e relação com camadas adjacentes
- [ ] Labels do issue espelhadas em **cada** PR
- [ ] Reviewers via CODEOWNERS solicitados em cada PR
- [ ] Cada PR auto-atribuído (`@me`)
- [ ] Commits de cada camada assinados (verificação GPG)
- [ ] Cada PR atende `lex-pr-quality` HARD-GATE individualmente

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Stack de PRs encadeados | N PRs no GitHub | Repositório de origem |
| Worktree compartilhado | Diretório local | `.worktrees/${N}-${SLUG}-stack/` |
| URLs dos PRs | Lista | Apresentadas ao usuário em ordem (camada 1 → N) |

## Restrições

- **Nunca** prosseguir sem confirmação explícita do usuário no Passo 0 — agente propõe, usuário decide
- **Nunca** criar branches da stack sem worktree compartilhado correspondente
- **Nunca** mergear PRs no GitHub via UI durante a fase de criação — o merge bottom-up tem kata próprio (`kata-stacked-pr-merge`)
- **Não** aplicar labels `size/*` manualmente — GitHub Actions aplica
- Se a Decision Checklist reprovar, **não tentar argumentar** — redirecionar imediatamente para `kata-contributing-pr`
- Cada commit em qualquer camada deve seguir as 4 Lexis de commit (`lex-conventional-commits`, `lex-commit-language`, `lex-small-commits`, `lex-signed-commits`)

## Variant: git-spice

Aplicável quando `.ahrena/.directives` declara `stacked_prs.tool: gs`. Pré-requisito: `git-spice` instalado (`brew install git-spice`) e `gs auth login` realizado uma vez. Toda a estratégia (Passo 0 — Decision Checklist, validação da issue, decomposição em camadas) permanece **idêntica** ao caminho vanilla; apenas os passos operacionais 3, 4 e 5 trocam de comandos. Consultar `codex-git-spice` para mapeamento completo.

### Passo 3 (gs): Inicializar gs e criar worktree compartilhado

```bash
ISSUE_NUMBER=42
SLUG="scheduled-payments"
WORKTREE_DIR=".worktrees/${ISSUE_NUMBER}-${SLUG}-stack"

# Worktree continua sendo um único compartilhado (codex-stacked-prs §4)
git worktree add "$WORKTREE_DIR" main
cd "$WORKTREE_DIR"

# Idempotente: roda só na primeira vez que o repositório encontra gs.
# Verifique antes com `cat .git/spice/store/info` e pule se já inicializado.
git-spice repo init --trunk main --remote origin
```

### Passo 4 (gs): Criar e submeter cada camada

**Camada 1** (a partir do trunk):

```bash
# Implementar arquivos da camada 1, depois:
git add <arquivos-da-camada-1>
git-spice branch create "feat/${ISSUE_NUMBER}-stack-1-${SLUG}" \
  -m "feat(scope): camada 1 — schema (1/N)"
# `gs branch create` commita o stage automaticamente.
```

**Camadas 2..N** (cada uma sobre a anterior):

```bash
git add <arquivos-da-camada-i>
git-spice branch create "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}" \
  -m "feat(scope): camada ${i} — ${LAYER_NAME} (${i}/N)"
# Estando checked out na camada i-1, gs usa-a como base automaticamente.
```

> **Auto-restack:** quando você commita na camada `i` via `gs commit create` ou `gs commit amend`, `gs` reaplica os commits das camadas `i+1..N` em cima da nova base. Por isso: **sempre** comece pela camada inferior; **nunca** misture mudanças de duas camadas no mesmo `commit create`.

**Submeter todos os PRs de uma só vez:**

```bash
git-spice stack submit --draft --fill
# --draft   → todos os PRs como rascunho
# --fill    → preenche título/body do commit message
```

`gs stack submit` aceita `--label`, `--reviewer`, `--assign` mas aplica os mesmos a **todos** os PRs da stack. Para mirror exato do issue (e variações por camada), prefira aplicar via `gh pr edit` no Passo 5 (gs).

**Body customizado por camada** (opcional, quando `--fill` não basta):

```bash
git-spice branch checkout "feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}"
git-spice branch submit \
  --title "feat(scope): camada ${i} — ${LAYER_NAME} (${i}/N)" \
  --body "Refs #${ISSUE_NUMBER} (${i}/N — ${LAYER_NAME})

Cobre: AC-X, AC-Y."
```

Para a **última camada**, troque `Refs #${ISSUE_NUMBER}` por `Closes #${ISSUE_NUMBER}` no body.

### Passo 5 (gs): Espelhar labels/assignee/reviewers em cada PR

Idêntico ao caminho vanilla — `gs` não diferencia por camada quando se trata de mirror do issue. Reutilize o loop com `gh pr edit`:

```bash
# Popular PR_NUMBERS a partir das branches da stack (gs stack submit
# imprime as URLs, mas para o loop precisamos dos números):
PR_NUMBERS=()
for i in $(seq 1 "$N"); do
  BRANCH="feat/${ISSUE_NUMBER}-stack-${i}-${LAYER_SLUG_i}"
  PR_NUMBERS+=("$(gh pr view "$BRANCH" --json number --jq .number)")
done

LABELS=$(gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" \
  --json labels --jq '[.labels[].name] | join(",")')

for PR in "${PR_NUMBERS[@]}"; do
  gh pr edit "$PR" --repo "$OWNER/$REPO" \
    --add-label "$LABELS" \
    --add-assignee "@me"
  # Reviewers via CODEOWNERS: auto-request quando configurado;
  # senão, adicionar manualmente:
  gh pr edit "$PR" --add-reviewer "org/team"
done
```

### Notas operacionais (gs)

- **Force-push seguro por default:** `gs branch submit` e `gs stack submit` já usam `--force-with-lease`; nunca passe `--force` sem motivo registrado.
- **Hooks pesados:** auto-restack repete o ciclo de hooks por camada acima; otimizar pre-commit ou usar `--no-verify` com autorização do usuário (mesma disciplina do vanilla).
- **GPG signing:** preservado se `commit.gpgsign=true` global; `gs` não tem flag específica.
- **Confusão de nome:** o binário se chama `git-spice`. Use `git-spice` em scripts; `gs` apenas em shell interativo (alias).

## Referências

- `codex-stacked-prs` — Decision Checklist canônica, naming, ciclo de vida
- `codex-git-spice` — instalação, catálogo de comandos `gs`, mapeamento vanilla→gs
- `kata-stacked-pr-rebase` — cascade rebase quando uma camada inferior muda
- `kata-stacked-pr-merge` — merge bottom-up após review aprovada
- `kata-contributing-pr` — fallback para PR único quando Decision Checklist reprova
- `lex-issue-first`, `lex-issue-quality` — pré-condições da issue guarda-chuva
- `lex-git-branches` — naming `{type}/{N}-stack-{layer}-{slug}`
- `lex-git-worktrees` — exceção declarada para worktree compartilhado de stack
- `lex-pr-quality` — HARD-GATE aplicado por PR da stack
- `cry-new-stacked-pr` — atalho que invoca esta Kata
