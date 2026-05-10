# Codex: Custo de tokens e tempo de implementação em Pull Requests (Claude Code)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Computação e estampagem de custo de assistência IA (Claude Code) em Pull Requests — tokens, USD e tempo de implementação

## Visão Geral

Este Codex é a referência para computar tokens consumidos, custo estimado em USD e tempo de implementação (ativo + calendário) durante o desenvolvimento que originou um Pull Request, e estampar esses números no body da PR. Tokens e custo vêm dos logs JSONL persistidos pelo Claude Code em `~/.claude/projects/<project-hash>/`, agregados pela ferramenta open-source [`ccusage`](https://github.com/ryoppippi/ccusage). Tempo vem dos mesmos JSONL (parseados por `scripts/pr-cost-stamp.sh`) — `ccusage` não expõe `timestamp` por turno em nenhum subcomando, então o script é fonte única para os agregados de tempo. O bloco resultante é inserido no body da PR delimitado por marcadores HTML que garantem idempotência. É consultado por `kata-pr-cost-stamp` (que computa e atualiza a PR) e por `kata-contributing-pr` (que invoca o stamp como step opcional).

## Contexto

- **Domínio:** observabilidade financeira de assistência IA em Pull Requests do framework Ahrena e dos projetos consumidores.
- **Público-alvo:** agentes de IA que executam `kata-pr-cost-stamp`; mantenedores que revisam custos por PR; tech leads avaliando ROI da automação.
- **Atualização:** quando o formato de saída do `ccusage` mudar de major; quando a tabela de preços do Anthropic for revisada; quando novas dimensões (ex.: por usuário, por epic) forem adicionadas ao bloco.

## Conteúdo

### Princípios

1. **Opt-in por projeto.** A funcionalidade é desativada por padrão. O projeto declara `pr_cost_tracking.enabled: true` em `.ahrena/.directives` para ativar. Não há Lexis impondo o uso — custo é dado interno e cada time decide expor.
2. **Fonte única de preço.** A tabela de USD por modelo é a do `ccusage`, que reflete o pricing público da Anthropic. O kata nunca hardcoda valores; auditoria trimestral confirma se o `ccusage` continua atualizado.
3. **Idempotência por marcadores HTML.** O bloco é delimitado por `<!-- ahrena:cost-stamp:start -->` e `<!-- ahrena:cost-stamp:end -->`. Re-executar o kata sobre a mesma PR substitui o conteúdo entre os marcadores; nunca duplica.
4. **Não-bloqueante.** Falha do stamp (rede, ferramenta indisponível, parsing) não impede a PR. O kata loga o erro e continua.
5. **Estimativa, não fatura.** O número exibido é estimativa baseada em pricing público; a fatura real vem do console Anthropic. O bloco declara isso explicitamente.

### Fonte de dados

| Item | Detalhe |
|------|---------|
| Local dos logs | `~/.claude/projects/<project-hash>/*.jsonl` |
| Granularidade | uma linha JSONL por turno; cada turno traz `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `model`, `cwd`, `sessionId`, `timestamp` |
| Hash do projeto | derivado pelo Claude Code a partir do path absoluto do projeto; o `ccusage` traduz o hash de volta para o nome do projeto via `--project` ou `--instances` |
| Janela temporal de tokens | `[branch_creation_date, now]` por padrão (filtro `--since` no `ccusage`/script) |
| Janela temporal de calendário | `[branch_creation_date, mergedAt ou agora]` — usa `mergedAt` quando a PR já foi mergeada, hora atual UTC quando ainda aberta |
| Gap de inatividade | `pr_cost_tracking.idle_gap_minutes` (default `10`); separa janelas ativas dentro de uma sessão para o cálculo de tempo ativo |

### Ferramentas suportadas

| Ferramenta | Quando usar | Comando base |
|------------|-------------|--------------|
| `ccusage` (preferida) | Sempre que `npx`/`node` estiverem disponíveis | `npx ccusage@latest daily --project=<project-id> --since <YYYYMMDD> --json` |
| `scripts/pr-cost-stamp.sh` (fallback) | Ambientes sem Node (ex.: runners minimalistas) | parsing direto dos JSONL com `jq` |

O kata tenta `ccusage` primeiro. Falha de execução (não falha de dados) cai para o fallback. Falha do fallback emite warning e segue sem stamp.

### Filtro por projeto

Os subcomandos `daily`, `weekly`, `monthly` e `blocks` do `ccusage` aceitam `--project <id>` e `--instances` (breakdown por projeto). O `<id>` é o identificador derivado do caminho absoluto do projeto, com `/` substituído por `-` e prefixo `-` (ex.: `/Users/foo/repo` → `-Users-foo-repo`). Use a forma `--project=<id>` para preservar o prefixo `-` na linha de comando.

O subcomando `session` não aceita `--project` e por isso não é usado por este Codex.

O kata usa `--project=<id>` como filtro primário; o filtro por `cwd` na linha JSONL permanece como complemento documentado, útil quando o usuário trabalha em múltiplos clones do mesmo repositório com nomes idênticos.

### Tempo de implementação

O bloco apresenta **duas métricas de tempo**, sempre juntas quando `pr_cost_tracking.enabled: true`:

| Métrica | Definição | Fonte de dados |
|---------|-----------|----------------|
| **Tempo ativo** | Soma, por `sessionId`, de janelas com gap ≤ `idle_gap_minutes` entre turnos consecutivos. Cada sessão com pelo menos um turno tem piso de 60s. Aproxima horas de trabalho engajado com a IA. | `timestamp` por turno nos JSONL; agregado por `scripts/pr-cost-stamp.sh` |
| **Tempo de calendário** | `(branch_creation_time, mergedAt ou agora)` em minutos. Aproxima lead time / throughput. | `git log --reverse <base>..<head> --format=%cI`; `gh pr view --json mergedAt` |

#### Por que dois números?

- **Tempo ativo** responde "quanto custou em horas de trabalho engajado". É a métrica de custo em horas, complementar ao USD.
- **Tempo de calendário** responde "quanto a feature ficou em curso no relógio". É métrica de fluxo (lead time), não de custo.

Os dois juntos diferenciam *concentração* (alto ativo, baixo calendário — sprint focado) de *diluição* (baixo ativo, alto calendário — feature parou esperando review, dependência, decisão).

#### Cálculo do tempo ativo

Modelo canônico: para cada `sessionId`, ordenar turnos por `timestamp`; somar `delta` apenas quando `delta ≤ idle_gap_minutes × 60`; janelas com gap maior contribuem zero (refletem ociosidade real). Sessões com um único turno recebem piso de 60s para evitar "zero work".

Exemplo: sessão com turnos em `t=0s, t=30s, t=65s, t=9000s, t=9020s` e `idle_gap_minutes=10` (= 600s):
- 30s ≤ 600 → soma 30s
- 35s ≤ 600 → soma 35s
- 8935s > 600 → soma 0 (intervalo ocioso)
- 20s ≤ 600 → soma 20s
- Total: 85s = 1min (após piso aplicado pelo script).

Caso single-turn: uma sessão com apenas um turno produz soma vazia de deltas (o intervalo de 1 a 1 não tem elementos), e o piso eleva o resultado ao mínimo documentado de 60 segundos.

#### Cálculo do tempo de calendário

`floor((calendar_end − calendar_start) / 60)` em minutos. `calendar_start` = primeiro commit da branch (`git log --reverse <base>..<head> --format=%cI | head -1`); `calendar_end` = `mergedAt` da PR ou hora atual em UTC quando ainda aberta.

#### Backend único

`ccusage` agrega no nível diário (`daily`), em janelas de billing de 5h (`blocks`) ou em sessão (`session` com `lastActivity`), mas **não expõe `timestamp` por turno** em nenhum subcomando (validado em `docs/guide/json-output.md`). Por isso, o tempo é sempre calculado pelo `scripts/pr-cost-stamp.sh`, mesmo quando `ccusage` é o backend de tokens/USD.

### Formato do bloco

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Métrica | Valor |
|---|---|
| Sessões | 3 |
| Tokens de input | 245.892 |
| Tokens de output | 18.432 |
| Cache reads | 1.245.888 |
| Cache writes | 89.234 |
| Custo estimado | $4.32 USD |
| Tempo ativo | 2h 47min |
| Tempo de calendário | 1d 4h (2026-05-04 → 2026-05-05) |
| Modelos | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

_Computado por `kata-pr-cost-stamp` em 2026-05-09T01:30:00Z. Janela: 2026-05-07 → 2026-05-09. Fonte: ccusage 1.x. Gap de inatividade: 10min._
_Estimativas baseadas em pricing público da Anthropic; a fatura real vem do console._
<!-- ahrena:cost-stamp:end -->
```

Regras do bloco:

- Marcadores HTML em linhas próprias, sem indentação; o regex de upsert depende disso.
- Cabeçalho fixo `## AI Assistance Cost (Claude Code)` para discoverabilidade.
- Tabela com colunas idênticas em todas as línguas; rótulos traduzidos.
- Linhas "Tempo ativo" e "Tempo de calendário" sempre presentes quando `enabled: true`.
- Linha de procedência (timestamp UTC, janela, versão da ferramenta, gap de inatividade) sempre presente.
- Disclaimer de estimativa sempre presente.
- Tempo formatado a partir de minutos inteiros: `< 60min` → `<n>min`; `< 24h` → `<h>h <m>min` (omite `<m>min` quando zero); `≥ 24h` → `<d>d <h>h` (omite `<h>h` quando zero); `0` → `0min`.

### Idempotência

O kata aplica upsert por meio dos marcadores HTML:

1. Lê o body atual da PR via `gh pr view --json body`.
2. Procura o intervalo `<!-- ahrena:cost-stamp:start --> ... <!-- ahrena:cost-stamp:end -->`.
3. Se existe → substitui o intervalo pelo bloco recém-gerado.
4. Se não existe → anexa o bloco ao final do body, separado por linha em branco.
5. Atualiza a PR via `gh pr edit --body`.

Re-executar o kata 2x consecutivas produz exatamente o mesmo body se nenhuma sessão nova ocorreu no intervalo.

### Privacidade

- **Repositórios públicos:** o body da PR é público assim que a PR é aberta. Custo absoluto em USD pode ser sensível; cada time decide se expõe. O kata respeita o opt-in do `.directives`; nada é estampado por padrão.
- **Mascaramento opcional:** `pr_cost_tracking.mask_absolute_cost: true` substitui o valor absoluto por uma faixa qualitativa (`< $1`, `$1–$10`, `$10–$50`, `> $50`). Configuração ainda não implementada nesta primeira iteração — declarada para iteração futura.
- **Sem PII:** nenhum conteúdo da sessão (mensagens, prompts, código) é estampado. Apenas agregados numéricos.

### Limitações conhecidas

| Limitação | Mitigação |
|-----------|-----------|
| Sessões cross-machine não capturadas (apenas a máquina onde roda o kata conta) | Codex documenta; agregação cross-machine é fora de escopo desta iteração |
| Janela heurística `[branch_creation_date, now]` inclui sessões off-topic no mesmo projeto | Filtro por `--project` reduz; `cwd` complementa; futura iteração pode usar `sessionId` rastreado por hooks |
| Stacked PRs com camadas sobrepostas — soma de tempo ativo das camadas > tempo ativo real | Cada camada usa sua janela `[branch_checkout_time, mergedAt ou agora]`; aceitar imprecisão; codex documenta |
| Variação de pricing entre versões do `ccusage` | Smoke test de regressão em CI; pinning de versão mínima testada via `ccusage@<min-version>` |
| `idle_gap_minutes` mal calibrado distorce tempo ativo | Default 10min cobre maioria dos fluxos; configurável por projeto; valor efetivo é exibido na linha de procedência do bloco |
| Tempo ativo ≠ tempo de leitura/edição manual | Métrica reflete cadência de turnos com a IA, não trabalho 100% humano antes/depois; documentar como "horas de assistência IA", não "horas totais de feature" |
| `BRANCH_FIRST_COMMIT_ISO` cai para `date -u` quando a branch ainda não tem commits sobre o base | Fallback intencional do kata (Passo 2) para não passar string vazia ao script. Resultado: tempo de calendário aparece como uma janela mínima recém-aberta, sem sinalização de que o limite foi sintético. Aceitar até a branch acumular commits e o stamp ser re-executado |

### Decisões vigentes

| Aspecto | Decisão |
|---------|---------|
| Backend de tokens/USD | `ccusage` via `npx ccusage@latest` (com fallback para `scripts/pr-cost-stamp.sh`) |
| Backend de tempo (ativo + calendário) | `scripts/pr-cost-stamp.sh` sempre — `ccusage` não expõe `timestamp` por turno |
| Filtro de projeto | flag nativa `--project=<id>` no `ccusage`; basename do `cwd` no fallback |
| Adoção | opt-in via `pr_cost_tracking.enabled` no `.directives` |
| `idle_gap_minutes` | sub-flag em `.directives`; default `10` |
| Trigger | step opcional em `kata-contributing-pr` |
| Idempotência | marcadores HTML `ahrena:cost-stamp:start/end` |
| Privacidade | sem mascaramento na primeira iteração; flag prevista para depois |

## Glossário

| Termo | Definição |
|-------|-----------|
| Stamp | bloco markdown delimitado por marcadores HTML, inserido no body da PR pelo `kata-pr-cost-stamp` |
| Janela de stamp | intervalo `[branch_creation_date, mergedAt ou agora]` no qual sessões Claude Code são consideradas para o cálculo |
| Tempo ativo | soma de janelas com gap ≤ `idle_gap_minutes` entre turnos consecutivos por `sessionId`; aproxima horas de trabalho engajado com a IA |
| Tempo de calendário | duração corrida `[branch_creation_date, mergedAt ou agora]`; aproxima lead time / throughput |
| `idle_gap_minutes` | gap (em minutos) que separa janelas ativas dentro de uma mesma sessão; default 10, configurável em `.directives` |
| Cache reads / cache writes | tokens lidos do cache / gravados no cache prompt da Anthropic; pricing distinto dos tokens regulares |
| ccusage | CLI open-source que parseia os logs JSONL do Claude Code e calcula custo agregado |
| Upsert | operação que insere o bloco caso não exista ou substitui o existente entre os marcadores |

## Referências

- `lex-directives` — leitura obrigatória do `.ahrena/.directives` antes de qualquer execução
- `kata-pr-cost-stamp` — procedimento que aplica este Codex
- `kata-contributing-pr` — step opcional que invoca o stamp
- `ccusage` — https://github.com/ryoppippi/ccusage
- Anthropic pricing — https://www.anthropic.com/pricing
