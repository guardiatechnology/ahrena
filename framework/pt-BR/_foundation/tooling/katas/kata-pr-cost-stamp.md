# Kata: Estampar custo de tokens (Claude Code) na PR

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Computar tokens consumidos e custo USD da assistência IA durante o desenvolvimento de uma PR e estampar o resultado no body via `gh pr edit`

## Objetivo

Calcular tokens e custo estimado em USD das sessões Claude Code que originaram uma Pull Request e gravar um bloco markdown idempotente no body da PR. Apoia visibilidade financeira e baseline de ROI da automação por feature, bug ou refactor. É invocada pelo `kata-contributing-pr` quando `pr_cost_tracking.enabled: true` em `.ahrena/.directives` e pode rodar avulsa para atualizar PRs existentes.

## Quando Usar

- Logo após criar ou atualizar uma PR via `kata-contributing-pr` em projeto que ativou `pr_cost_tracking.enabled: true`.
- Manualmente em uma PR existente para atualizar o stamp com sessões adicionais (ex.: depois de novos commits).
- Em CI ou hook pós-merge para auditoria histórica (uso futuro).

## Entradas

| Entrada | Obrigatório | Descrição |
|---------|:-----------:|-----------|
| Número da PR | Sim | `$PR_NUMBER` no repositório atual |
| Repositório | Não | `owner/repo`; default: `gh repo view --json nameWithOwner` |
| Branch | Não | nome da branch da PR; default: `gh pr view <PR> --json headRefName` |
| Janela inicial | Não | data ISO; default: data do primeiro commit da branch (`git log --reverse <base>..<head> --format=%cI \| head -1`) |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Verificar pré-condições e diretivas
- [ ] 2. Resolver contexto da PR
- [ ] 3. Computar uso via ccusage (ou fallback)
- [ ] 4. Renderizar bloco markdown
- [ ] 5. Upsert no body da PR
- [ ] 6. Verificação final
```

### Passo 1: Verificar pré-condições e diretivas

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Ler `pr_cost_tracking.enabled`. Se `false` ou ausente → encerrar silenciosamente com mensagem `pr-cost-stamp: disabled in directives, skipping`.
3. Verificar disponibilidade de `gh` (autenticado) e `git`. Faltando → encerrar com warning, sem propagar erro.
4. Tentar `npx ccusage@latest --version` (timeout 30s). Sucesso → `ccusage` é o backend. Falha → tentar `scripts/pr-cost-stamp.sh --version`. Falha → encerrar com warning `pr-cost-stamp: no backend available, skipping`.

### Passo 2: Resolver contexto da PR

1. `OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)`.
2. `PR_NUMBER` do input ou de `gh pr view --json number --jq .number`.
3. `HEAD_REF=$(gh pr view $PR_NUMBER --json headRefName --jq .headRefName)`.
4. `BASE_REF=$(gh pr view $PR_NUMBER --json baseRefName --jq .baseRefName)`.
5. `SINCE_DATE`: data do primeiro commit da branch em `YYYYMMDD`.
   ```bash
   SINCE_DATE=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cd --date=format:%Y%m%d | head -1)
   ```
6. Resolver o diretório raiz do repositório principal (não do worktree, quando aplicável):
   ```bash
   MAIN_DIR=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
   ```
   `git rev-parse --git-common-dir` aponta para o `.git/` do repositório principal mesmo em worktrees, garantindo que sessões registradas no main e em worktrees sejam agregadas.
7. `PROJECT_BASENAME=$(basename "$MAIN_DIR")` — usado pelo fallback (matching por basename do `cwd` no JSONL).
8. `PROJECT_ID=$(echo "$MAIN_DIR" | tr / -)` — id no formato Claude Code (path com `/` → `-`, prefixo `-`); usado pelo filtro `--project=<id>` do `ccusage`.

### Passo 3: Computar uso via ccusage (ou fallback)

**Preferencial — `ccusage`:**

```bash
RAW=$(npx --yes ccusage@latest daily \
  --project="$PROJECT_ID" \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null)
```

Notas:
- O subcomando é `daily`. O `session` não aceita `--project`. A forma `--project=<id>` (com `=`) preserva o prefixo `-` do id.
- `--offline` usa a tabela de pricing embutida no `ccusage`; remova para forçar fetch online quando online estiver disponível e atualizado.
- Saída JSON contém `daily` (entradas por data) e `totals` (agregado), com `modelBreakdowns` por entrada. Para contagem de sessões únicas, fazer uma chamada complementar `ccusage session --since "$SINCE_DATE" --json` e filtrar por `cwd` na linha JSONL.

**Fallback — `scripts/pr-cost-stamp.sh`:**

```bash
RAW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE")
```

Saída JSON com schema equivalente ao do `ccusage` (chaves `totals`, `breakdown`, `meta`).

### Passo 4: Renderizar bloco markdown

A partir do JSON em `RAW`, montar:

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Métrica | Valor |
|---|---|
| Sessões | <sessions> |
| Tokens de input | <input_tokens> |
| Tokens de output | <output_tokens> |
| Cache reads | <cache_read_tokens> |
| Cache writes | <cache_create_tokens> |
| Custo estimado | $<cost_usd> USD |
| Modelos | <model_breakdown> |

_Computado por `kata-pr-cost-stamp` em <utc_now>. Janela: <since_date> → agora. Fonte: <tool_name> <tool_version>._
_Estimativa baseada em pricing público da Anthropic; a fatura real vem do console._
<!-- ahrena:cost-stamp:end -->
```

Regras de formatação:

- Números com separador de milhares por locale (`pt-BR` usa ponto). Para `es` e `en` aplicar separador apropriado.
- `cost_usd` com 2 decimais.
- `model_breakdown`: lista de `<model_id> (<percent>%)` ordenada por participação decrescente, separados por vírgula.
- `<utc_now>` em ISO 8601 com sufixo `Z`.

### Passo 5: Upsert no body da PR

1. Obter body atual:
   ```bash
   CURRENT_BODY=$(gh pr view $PR_NUMBER --json body --jq .body)
   ```
2. Aplicar upsert por marcadores:
   ```bash
   START='<!-- ahrena:cost-stamp:start -->'
   END='<!-- ahrena:cost-stamp:end -->'

   if grep -q "$START" <<< "$CURRENT_BODY"; then
     # substituir bloco existente
     NEW_BODY=$(awk -v start="$START" -v end="$END" -v block="$RENDERED_BLOCK" '
       BEGIN{p=1}
       $0 ~ start {print block; p=0}
       p {print}
       $0 ~ end {p=1; next}
     ' <<< "$CURRENT_BODY")
   else
     # anexar ao final do body
     NEW_BODY="${CURRENT_BODY}"$'\n\n'"${RENDERED_BLOCK}"
   fi
   ```
3. Atualizar a PR:
   ```bash
   gh pr edit $PR_NUMBER --body "$NEW_BODY"
   ```

### Passo 6: Verificação final

- [ ] `pr_cost_tracking.enabled: true` confirmado em `.directives`
- [ ] Backend identificado (`ccusage` ou fallback) e versão registrada no bloco
- [ ] JSON de uso obtido sem erro
- [ ] Bloco renderizado contém marcadores `start`/`end` em linhas próprias
- [ ] Body atualizado contém exatamente uma ocorrência dos marcadores
- [ ] `gh pr view $PR_NUMBER --json body` mostra o bloco visível e formatado

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Bloco de custo | Markdown delimitado por marcadores HTML | Body da PR |
| Mensagem de status | Texto | Stdout do agente |

## Exemplo de Execução

### Input

```bash
PR_NUMBER=67
# diretivas: pr_cost_tracking.enabled: true
```

### Saída esperada (stdout)

```
pr-cost-stamp: backend=ccusage version=1.x project=ahrena since=20260507
pr-cost-stamp: 3 sessions, 245892 input, 18432 output, $4.32 USD
pr-cost-stamp: PR #67 body updated (block upserted)
```

### Bloco resultante (no body da PR)

Ver `codex-pr-cost-tracking` → seção "Formato do bloco".

## Restrições

- **Não-bloqueante:** qualquer falha (rede, parsing, ferramenta) emite warning e encerra com exit 0. O kata nunca aborta `kata-contributing-pr`.
- **Sem hardcode de pricing:** o kata jamais recalcula custo a partir de tabela própria; usa exclusivamente o resultado do `ccusage` ou do fallback.
- **Sem PII no body:** nenhum conteúdo de sessão (mensagens, código, prompts) é estampado; apenas agregados.
- **Idempotência obrigatória:** re-execução sem novas sessões produz o mesmo body.
- **Respeitar diretiva:** `pr_cost_tracking.enabled: false` ou ausente → kata é no-op.

## Referências

- `codex-pr-cost-tracking` — Manual de referência (fonte de dados, formato, idempotência, privacidade)
- `lex-directives` — Leitura obrigatória do `.ahrena/.directives`
- `kata-contributing-pr` — Step opcional que invoca este kata
- `scripts/pr-cost-stamp.sh` — Fallback Bash quando `ccusage` indisponível
- `ccusage` — https://github.com/ryoppippi/ccusage
