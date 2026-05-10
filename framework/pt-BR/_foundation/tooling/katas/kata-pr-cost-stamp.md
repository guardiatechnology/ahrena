# Kata: Estampar custo de tokens e tempo de implementação (Claude Code) na PR

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Computar tokens, custo USD e tempo de implementação da assistência IA durante o desenvolvimento de uma PR e estampar o resultado no body via `gh pr edit`

## Objetivo

Calcular tokens, custo estimado em USD e tempo de implementação (ativo + calendário) das sessões Claude Code que originaram uma Pull Request e gravar um bloco markdown idempotente no body da PR. Apoia visibilidade financeira, ROI da automação e leitura de throughput por feature, bug ou refactor. É invocada pelo `kata-contributing-pr` quando `pr_cost_tracking.enabled: true` em `.ahrena/.directives` e pode rodar avulsa para atualizar PRs existentes.

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
- [ ] 3. Computar tokens e custo via ccusage (ou fallback)
- [ ] 4. Computar tempo de implementação (ativo + calendário)
- [ ] 5. Renderizar bloco markdown
- [ ] 6. Upsert no body da PR
- [ ] 7. Verificação final
```

### Passo 1: Verificar pré-condições e diretivas

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Ler `pr_cost_tracking.enabled`. Se `false` ou ausente → encerrar silenciosamente com mensagem `pr-cost-stamp: disabled in directives, skipping`.
3. Ler `pr_cost_tracking.idle_gap_minutes` (default `10`). Esse valor é o gap (em minutos) que separa janelas ativas dentro de uma sessão Claude Code para o cálculo de tempo ativo.
4. Verificar disponibilidade de `gh` (autenticado), `git` e `scripts/pr-cost-stamp.sh` (presente e executável; necessário para computar tempo). Qualquer ausência → encerrar com warning, sem propagar erro.
5. Tentar `npx ccusage@latest --version` (timeout 30s). Sucesso → `ccusage` é o backend de tokens/USD. Falha → `scripts/pr-cost-stamp.sh` cobre tokens também (sem custo). Em ambos os caminhos, o script é a fonte única de verdade dos tempos (ativo + calendário) — `ccusage` não expõe `timestamp` por turno em nenhum subcomando.

### Passo 2: Resolver contexto da PR

1. `OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)`.
2. `PR_NUMBER` do input ou de `gh pr view --json number --jq .number`.
3. `HEAD_REF=$(gh pr view $PR_NUMBER --json headRefName --jq .headRefName)`.
4. `BASE_REF=$(gh pr view $PR_NUMBER --json baseRefName --jq .baseRefName)`.
5. `SINCE_DATE` (formato `YYYYMMDD` para `--since`) e `BRANCH_FIRST_COMMIT_ISO` (ISO 8601 para `--calendar-start`). Se a branch ainda não tem commits sobre o base (branch nova ou erro de resolução), usar a data atual como fallback:
   ```bash
   SINCE_DATE=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cd --date=format:%Y%m%d | head -1)
   BRANCH_FIRST_COMMIT_ISO=$(git log --reverse $BASE_REF..$HEAD_REF --format=%cI | head -1)
   [ -z "$SINCE_DATE" ] && SINCE_DATE=$(date -u +%Y%m%d)
   [ -z "$BRANCH_FIRST_COMMIT_ISO" ] && BRANCH_FIRST_COMMIT_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   ```
6. `PR_END_ISO`: extremo superior da janela de calendário. Se a PR já foi mergeada, usar `mergedAt`; caso contrário, hora atual em UTC:
   ```bash
   MERGED_AT=$(gh pr view $PR_NUMBER --json mergedAt --jq .mergedAt)
   if [ -n "$MERGED_AT" ] && [ "$MERGED_AT" != "null" ]; then
     PR_END_ISO="$MERGED_AT"
   else
     PR_END_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   fi
   ```
7. Resolver o diretório raiz do repositório principal (não do worktree, quando aplicável):
   ```bash
   MAIN_DIR=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
   ```
   `git rev-parse --git-common-dir` aponta para o `.git/` do repositório principal mesmo em worktrees, garantindo que sessões registradas no main e em worktrees sejam agregadas.
8. `PROJECT_BASENAME=$(basename "$MAIN_DIR")` — usado pelo fallback e pelo cálculo de tempo (matching por basename do `cwd` no JSONL).
9. `PROJECT_ID=$(echo "$MAIN_DIR" | tr / -)` — id no formato Claude Code (path com `/` → `-`, prefixo `-`); usado pelo filtro `--project=<id>` do `ccusage`.

### Passo 3: Computar tokens e custo via ccusage (ou fallback)

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
- Saída JSON contém `daily` (entradas por data) e `totals` (agregado), com `modelBreakdowns` por entrada.

**Contagem de sessões únicas** (chamada complementar; o `daily` não a expõe):

```bash
SESSIONS=$(npx --yes ccusage@latest session \
  --since "$SINCE_DATE" \
  --json --offline 2>/dev/null \
  | jq --arg pid "$PROJECT_ID" '[.sessions[] | select(.sessionId | startswith($pid))] | length')
```

O `sessionId` no `ccusage session --json` começa com o id do projeto (mesmo formato `--project=<id>`), o que permite filtrar via `startswith`. Sessão aqui é a sessão do Claude Code (uma conversa contínua), não commit individual: 6 commits dentro da mesma conversa contam como 1 sessão.

**Fallback — `scripts/pr-cost-stamp.sh`:**

```bash
RAW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE")
```

Saída JSON com schema equivalente ao do `ccusage` (chaves `totals`, `breakdown`, `meta`).

### Passo 4: Computar tempo de implementação (ativo + calendário)

Tempo é sempre derivado de `scripts/pr-cost-stamp.sh`, independentemente do backend de tokens, porque `ccusage` não expõe `timestamp` por turno em nenhum subcomando (validado em `docs/guide/json-output.md`).

```bash
TIME_RAW=$(scripts/pr-cost-stamp.sh \
  --project "$PROJECT_BASENAME" \
  --since "$SINCE_DATE" \
  --idle-gap-minutes "$IDLE_GAP_MINUTES" \
  --calendar-start "$BRANCH_FIRST_COMMIT_ISO" \
  --calendar-end   "$PR_END_ISO")

ACTIVE_MIN=$(echo "$TIME_RAW" | jq -r '.totals.active_minutes')
CALENDAR_MIN=$(echo "$TIME_RAW" | jq -r '.totals.calendar_minutes')
```

Quando o backend de tokens já é o próprio script (caminho fallback), uma única invocação cobre tudo — basta passar `--idle-gap-minutes`, `--calendar-start` e `--calendar-end` na chamada do Passo 3 e reaproveitar os campos de `totals.active_minutes` e `totals.calendar_minutes`.

Modelo de cálculo (cravado no script, não reimplementar no kata):

- **Tempo ativo:** soma, por `sessionId`, de janelas com gap ≤ `idle_gap_minutes` entre turnos consecutivos. Cada sessão com pelo menos um turno tem piso de 60 segundos para evitar que sessões curtas registrem zero. Janelas com gap maior contribuem zero (reflete tempo ocioso real).
- **Tempo de calendário:** `(calendar_end − calendar_start) / 60`, em minutos, com `floor`.

Ambos os campos saem em **minutos inteiros**; o renderizador (Passo 5) converte para `Xh Ymin`.

### Passo 5: Renderizar bloco markdown

A partir do JSON em `RAW` e dos minutos derivados em `TIME_RAW`, montar:

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
| Tempo ativo | <active_time_human> |
| Tempo de calendário | <calendar_time_human> (<since_date> → <pr_end_date>) |
| Modelos | <model_breakdown> |

_Computado por `kata-pr-cost-stamp` em <utc_now>. Janela: <since_date> → <pr_end_date>. Fonte: <tool_name> <tool_version>. Gap de inatividade: <idle_gap_minutes>min._
_Estimativas baseadas em pricing público da Anthropic; a fatura real vem do console._
<!-- ahrena:cost-stamp:end -->
```

Regras de formatação:

- Números com separador de milhares por locale (`pt-BR` usa ponto). Para `es` e `en` aplicar separador apropriado.
- `cost_usd` com 2 decimais.
- `model_breakdown`: lista de `<model_id> (<percent>%)` ordenada por participação decrescente, separados por vírgula.
- `<utc_now>`, `<since_date>` e `<pr_end_date>` em ISO 8601 com sufixo `Z` (ou data simples para `since_date`/`pr_end_date` quando hora não agrega contexto).
- **Tempo humanizado** a partir de minutos inteiros:
  - `< 60min` → `"<n>min"` (ex.: `47min`)
  - `< 24h`  → `"<h>h <m>min"` (ex.: `2h 47min`); omitir `<m>min` quando zero (`3h`)
  - `≥ 24h` → `"<d>d <h>h"` (ex.: `1d 4h`); omitir `<h>h` quando zero (`2d`)
- Se `active_minutes` ou `calendar_minutes` for `0`, renderizar `0min`.

### Passo 6: Upsert no body da PR

1. Obter body atual:
   ```bash
   CURRENT_BODY=$(gh pr view $PR_NUMBER --json body --jq .body)
   ```
2. Aplicar upsert por marcadores via Python — substituição literal segura, sem interpolação de backreferences (`$1`, `\1`, `\n`, etc.) dentro do bloco renderizado:
   ```bash
   echo "$CURRENT_BODY" > /tmp/pr-body.in
   echo "$RENDERED_BLOCK" > /tmp/pr-body.block

   python3 - <<'PY'
   import re, pathlib
   body = pathlib.Path("/tmp/pr-body.in").read_text()
   block = pathlib.Path("/tmp/pr-body.block").read_text().rstrip("\n")
   pattern = re.compile(
       r"<!-- ahrena:cost-stamp:start -->.*?<!-- ahrena:cost-stamp:end -->",
       re.DOTALL,
   )
   if pattern.search(body):
       # substituir bloco existente; lambda força replacement literal
       new_body = pattern.sub(lambda _: block, body)
   else:
       # anexar ao final do body separado por linha em branco
       new_body = body.rstrip("\n") + "\n\n" + block + "\n"
   pathlib.Path("/tmp/pr-body.in").write_text(new_body)
   PY

   NEW_BODY=$(cat /tmp/pr-body.in)
   ```

   Por que Python e não `awk`/`perl`/`sed`: o `awk` BWK do macOS não passa variáveis multi-linha; o `s///` do `perl` (sem `e`) interpreta sequências como `\n` no replacement; `sed` exige escaping pesado de caracteres especiais. Python com `lambda _: block` em `re.sub` substitui o bloco literalmente, sem reinterpretar backreferences. Python 3 está presente por padrão em macOS, Linux e na maioria dos runners de CI.
3. Atualizar a PR:
   ```bash
   gh pr edit $PR_NUMBER --body "$NEW_BODY"
   ```

### Passo 7: Verificação final

- [ ] `pr_cost_tracking.enabled: true` confirmado em `.directives`
- [ ] Backend de tokens identificado (`ccusage` ou fallback) e versão registrada no bloco
- [ ] `scripts/pr-cost-stamp.sh` invocado para tempo, com `--idle-gap-minutes`, `--calendar-start` e `--calendar-end` preenchidos
- [ ] JSON de tokens e JSON de tempo obtidos sem erro
- [ ] Linhas "Tempo ativo" e "Tempo de calendário" presentes no bloco renderizado
- [ ] Bloco contém marcadores `start`/`end` em linhas próprias
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
pr-cost-stamp: time backend=pr-cost-stamp.sh 1.1.0 idle_gap=10min
pr-cost-stamp: active 167min (2h 47min), calendar 1680min (1d 4h)
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
- **Tempo ativo é heurística:** depende do `idle_gap_minutes` para separar trabalho engajado de pausa; cross-machine não captura sessões em outras máquinas; em stacked PRs as janelas das camadas se sobrepõem. Limitações documentadas em `codex-pr-cost-tracking`.

## Referências

- `codex-pr-cost-tracking` — Manual de referência (fonte de dados, formato, idempotência, privacidade)
- `lex-directives` — Leitura obrigatória do `.ahrena/.directives`
- `kata-contributing-pr` — Step opcional que invoca este kata
- `scripts/pr-cost-stamp.sh` — Fallback Bash quando `ccusage` indisponível
- `ccusage` — https://github.com/ryoppippi/ccusage
